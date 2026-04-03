
import cv2
import logging
import asyncio
import requests
import numpy as np
import urllib.parse
import gc
from datetime import datetime
from app import models
from app.db.session import SessionLocal
from app.services.camera import THAILAND_TZ

logger = logging.getLogger(__name__)

# go2rtc API base URL (container name on same docker network)
GO2RTC_API_URL = "http://cctv_go2rtc:1984"

# ── Tuning constants ──────────────────────────────────────────────────
# Concurrent snapshot fetches. This is I/O-bound (waiting for go2rtc),
# so we can safely go higher than 3. Kept at 5 to limit RAM on 512 MiB container.
BLUR_CONCURRENCY = 5

# Per-camera hard timeout (seconds) — prevents any single camera from hanging
BLUR_TIMEOUT = 15

# Max width (px) to downscale frames before Laplacian — saves RAM & CPU.
# Blur detection is scale-invariant; 480 px is more than enough.
PROCESSING_WIDTH = 480

# How many cameras to process before committing & freeing ORM objects.
BATCH_SIZE = 50
# ──────────────────────────────────────────────────────────────────────


class BlurWorker:
    def __init__(self, check_interval: int = 300, threshold: float = 50.0):
        self.check_interval = check_interval
        self.threshold = threshold
        self.running = False
        self._shutdown = False

    def _fetch_frame_from_go2rtc(self, rtsp_url: str) -> np.ndarray | None:
        """
        Fetch a JPEG frame from go2rtc snapshot API.
        Retries once after 2s if go2rtc returns 500 (stream not yet connected).
        Returns decoded grayscale frame (numpy array) or None if failed.
        """
        import time

        encoded_url = urllib.parse.quote(rtsp_url, safe='')
        snapshot_url = f"{GO2RTC_API_URL}/api/frame.jpeg?src={encoded_url}"

        MAX_RETRIES = 2
        RETRY_DELAY = 2  # seconds — give go2rtc time to establish RTSP connection

        for attempt in range(MAX_RETRIES):
            try:
                response = requests.get(snapshot_url, timeout=10)
                if response.status_code == 200 and response.content:
                    nparr = np.frombuffer(response.content, np.uint8)
                    frame = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
                    return frame

                if response.status_code == 500 and attempt < MAX_RETRIES - 1:
                    # go2rtc hasn't connected to this stream yet — wait and retry
                    logger.debug(f"go2rtc returned 500, retrying in {RETRY_DELAY}s... ({rtsp_url})")
                    time.sleep(RETRY_DELAY)
                    continue

                logger.debug(f"go2rtc snapshot failed: status={response.status_code} for {rtsp_url}")
                return None
            except Exception as e:
                logger.debug(f"go2rtc snapshot error for {rtsp_url}: {e}")
                return None

        return None

    def check_sharpness(self, rtsp_url: str) -> float:
        """
        Fetch a frame via go2rtc and calculate Laplacian variance.
        Memory-optimised: decodes as grayscale, downscales, uses CV_32F.
        Returns variance (float). Returns 0.0 if failed.
        """
        if not rtsp_url:
            return 0.0

        gray = self._fetch_frame_from_go2rtc(rtsp_url)  # already grayscale

        if gray is None:
            logger.warning(f"Could not fetch frame via go2rtc for: {rtsp_url}")
            return 0.0

        try:
            # Downscale to PROCESSING_WIDTH if wider — saves RAM & CPU
            h, w = gray.shape[:2]
            if w > PROCESSING_WIDTH:
                scale = PROCESSING_WIDTH / w
                new_w = PROCESSING_WIDTH
                new_h = int(h * scale)
                gray = cv2.resize(gray, (new_w, new_h), interpolation=cv2.INTER_AREA)

            # Laplacian with CV_32F (4 bytes/pixel instead of 8)
            laplacian = cv2.Laplacian(gray, cv2.CV_32F)
            variance = float(laplacian.var())

            # Explicit cleanup
            del laplacian
            del gray

            return variance
        except Exception as e:
            logger.error(f"Error calculating blur for {rtsp_url}: {e}")
            return 0.0

    async def _check_camera_safe(self, cam_id: int, rtsp_url: str, semaphore: asyncio.Semaphore) -> tuple:
        """
        Check a single camera with concurrency limit + hard timeout.
        Only receives primitives (id, url) to avoid holding ORM objects across threads.
        Returns (cam_id, variance) or (cam_id, None) on failure/timeout.
        """
        async with semaphore:
            try:
                variance = await asyncio.wait_for(
                    asyncio.to_thread(self.check_sharpness, rtsp_url),
                    timeout=BLUR_TIMEOUT
                )
                return cam_id, variance
            except asyncio.TimeoutError:
                logger.warning(f"Blur check timed out ({BLUR_TIMEOUT}s) for camera {cam_id}")
                return cam_id, None
            except Exception as e:
                logger.error(f"Blur check error for camera {cam_id}: {e}")
                return cam_id, None

    async def run_once(self):
        """
        Run blur check for all ONLINE cameras in batches.
        Processes BATCH_SIZE cameras at a time, commits, then moves on.
        """
        logger.info("Starting background blur check...")
        start_time = datetime.now()

        db = SessionLocal()
        semaphore = asyncio.Semaphore(BLUR_CONCURRENCY)

        try:
            # Fetch only the columns we need — avoids loading full ORM objects
            camera_rows = db.query(
                models.Camera.id,
                models.Camera.rtsp_url,
                models.Camera.status,
                models.Camera.image_status,
            ).filter(
                models.Camera.status.in_(["online", "blurry"]),
                models.Camera.rtsp_url != None,
                models.Camera.rtsp_url != ""
            ).all()

            if not camera_rows:
                logger.info("No online cameras with RTSP to check.")
                return

            total_cameras = len(camera_rows)
            total_updated = 0

            # Process in batches
            for batch_start in range(0, total_cameras, BATCH_SIZE):
                if self._shutdown:
                    break

                batch = camera_rows[batch_start:batch_start + BATCH_SIZE]
                batch_num = (batch_start // BATCH_SIZE) + 1

                # Create async tasks for this batch only
                tasks = [
                    self._check_camera_safe(row.id, row.rtsp_url, semaphore)
                    for row in batch
                ]
                results = await asyncio.gather(*tasks)

                # Apply results to DB
                now_str = datetime.now(THAILAND_TZ).strftime("%Y-%m-%d %H:%M:%S")
                batch_updates = 0

                for cam_id, variance in results:
                    if variance is None:
                        continue

                    new_image_status = "blur" if variance < self.threshold else "normal"

                    # Find the original row data for comparison
                    original = next((r for r in batch if r.id == cam_id), None)
                    if original is None:
                        continue

                    needs_status_change = False
                    update_dict = {
                        "sharpness_value": float(variance),
                        "last_image_check": now_str,
                    }

                    if new_image_status == "blur" and original.status != "blurry":
                        logger.info(f"Camera {cam_id} changed to blurry! (Score: {variance:.2f})")
                        update_dict["status"] = "blurry"
                        needs_status_change = True
                    elif new_image_status == "normal" and original.status == "blurry":
                        logger.info(f"Camera {cam_id} recovered from blurry → online (Score: {variance:.2f})")
                        update_dict["status"] = "online"
                        needs_status_change = True

                    if original.image_status != new_image_status:
                        logger.info(f"Camera {cam_id} image_status: {original.image_status} → {new_image_status} (Score: {variance:.2f})")
                        update_dict["image_status"] = new_image_status
                        needs_status_change = True

                    if needs_status_change:
                        update_dict["last_update"] = now_str

                    # Use direct UPDATE query — avoids loading full ORM objects
                    db.query(models.Camera).filter(
                        models.Camera.id == cam_id
                    ).update(update_dict)
                    batch_updates += 1

                # Commit after each batch
                db.commit()
                total_updated += batch_updates
                logger.debug(f"Batch {batch_num}: checked {len(batch)}, updated {batch_updates}")

                # Force garbage collection between batches
                gc.collect()

            elapsed = (datetime.now() - start_time).total_seconds()
            logger.info(f"Blur check done in {elapsed:.2f}s. Scanned {total_cameras}, updated {total_updated} cameras.")

        except Exception as e:
            logger.error(f"Error in blur worker run: {e}")
            db.rollback()
        finally:
            db.close()
            gc.collect()

    async def start_loop(self):
        self.running = True
        logger.info(f"Blur Worker Loop Started (Interval: {self.check_interval}s)")
        while self.running:
            try:
                await self.run_once()
            except Exception as e:
                logger.error(f"Critical error in blur loop: {e}")

            for _ in range(self.check_interval):
                if not self.running:
                    break
                await asyncio.sleep(1)

    def stop(self):
        self.running = False
        self._shutdown = True
