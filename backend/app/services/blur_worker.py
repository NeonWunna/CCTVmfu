
import cv2
import logging
import asyncio
import requests
import numpy as np
import urllib.parse
from datetime import datetime
from app import models
from app.db.session import SessionLocal
from app.services.camera import THAILAND_TZ

logger = logging.getLogger(__name__)

# go2rtc API base URL (container name on same docker network)
GO2RTC_API_URL = "http://cctv_go2rtc:1984"

# Max concurrent blur checks — prevents CPU starvation on low-core containers
BLUR_SEMAPHORE = asyncio.Semaphore(3)

# Per-camera hard timeout (seconds) — prevents any single camera from hanging
BLUR_TIMEOUT = 30


class BlurWorker:
    def __init__(self, check_interval: int = 300, threshold: float = 50.0):
        self.check_interval = check_interval
        self.threshold = threshold
        self.running = False
        self._shutdown = False

    def _fetch_frame_from_go2rtc(self, rtsp_url: str) -> np.ndarray | None:
        """
        Fetch a JPEG frame from go2rtc snapshot API.
        Returns decoded frame (numpy array) or None if failed.
        Uses a short timeout to avoid blocking the thread executor.
        """
        try:
            encoded_url = urllib.parse.quote(rtsp_url, safe='')
            snapshot_url = f"{GO2RTC_API_URL}/api/frame.jpeg?src={encoded_url}"

            response = requests.get(snapshot_url, timeout=10)
            if response.status_code == 200 and response.content:
                nparr = np.frombuffer(response.content, np.uint8)
                frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                return frame
            else:
                logger.warning(f"go2rtc snapshot failed: status={response.status_code}")
                return None
        except Exception as e:
            logger.warning(f"go2rtc snapshot error for {rtsp_url}: {e}")
            return None

    def check_sharpness(self, rtsp_url: str) -> float:
        """
        Fetch a frame via go2rtc snapshot API and calculate Laplacian variance.
        Direct RTSP (cv2.VideoCapture) is intentionally NOT used as fallback
        because it has no timeout and can hang indefinitely, blocking CPU.
        Returns variance (float). Returns 0.0 if failed.
        """
        if not rtsp_url:
            return 0.0

        frame = self._fetch_frame_from_go2rtc(rtsp_url)

        if frame is None:
            logger.warning(f"Could not fetch frame via go2rtc for: {rtsp_url}")
            return 0.0

        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            laplacian = cv2.Laplacian(gray, cv2.CV_64F)
            variance = laplacian.var()
            return variance
        except Exception as e:
            logger.error(f"Error calculating blur for {rtsp_url}: {e}")
            return 0.0

    async def _check_camera_safe(self, cam) -> tuple:
        """
        Check a single camera with concurrency limit + hard timeout.
        Returns (cam, variance) or (cam, None) on failure/timeout.
        """
        async with BLUR_SEMAPHORE:
            try:
                async with asyncio.timeout(BLUR_TIMEOUT):
                    variance = await asyncio.to_thread(self.check_sharpness, cam.rtsp_url)
                    return cam, variance
            except asyncio.TimeoutError:
                logger.warning(f"Blur check timed out ({BLUR_TIMEOUT}s) for camera {cam.id} ({cam.ip_address})")
                return cam, None
            except Exception as e:
                logger.error(f"Blur check error for camera {cam.id}: {e}")
                return cam, None

    async def run_once(self):
        """
        Run blur check for all ONLINE cameras concurrently (capped by semaphore).
        """
        logger.info("Starting background blur check...")
        start_time = datetime.now()

        db = SessionLocal()
        try:
            cameras = db.query(models.Camera).filter(
                models.Camera.status == "online",
                models.Camera.rtsp_url != None,
                models.Camera.rtsp_url != ""
            ).all()

            if not cameras:
                logger.info("No online cameras with RTSP to check.")
                return

            # Run all checks concurrently (semaphore limits to BLUR_SEMAPHORE at a time)
            tasks = [self._check_camera_safe(cam) for cam in cameras]
            results = await asyncio.gather(*tasks)

            updates_count = 0
            for cam, variance in results:
                if self._shutdown:
                    break
                if variance is None:
                    # Timeout or error — skip update, don't change status
                    continue

                new_image_status = "blur" if variance < self.threshold else "normal"

                needs_update = False
                if new_image_status == "blur" and cam.status != "blurry":
                    logger.info(f"Camera {cam.id} changed to blurry! (Score: {variance:.2f})")
                    cam.status = "blurry"
                    needs_update = True

                if cam.image_status != new_image_status:
                    logger.info(f"Camera {cam.id} image_status: {cam.image_status} → {new_image_status} (Score: {variance:.2f})")
                    cam.image_status = new_image_status
                    needs_update = True

                cam.sharpness_value = float(variance)
                cam.last_image_check = datetime.now(THAILAND_TZ).strftime("%Y-%m-%d %H:%M:%S")
                updates_count += 1

            db.commit()
            elapsed = (datetime.now() - start_time).total_seconds()
            logger.info(f"Blur check done in {elapsed:.2f}s. Scanned {len(cameras)}, updated {updates_count} cameras.")

        except Exception as e:
            logger.error(f"Error in blur worker run: {e}")
        finally:
            db.close()

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
