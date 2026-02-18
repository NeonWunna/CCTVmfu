
import asyncio
import logging
import cv2
import numpy as np
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app import models
from app.db.session import SessionLocal
from app.services.camera import THAILAND_TZ

logger = logging.getLogger(__name__)

class BlurWorker:
    def __init__(self, concurrent_limit: int = 50, loop_interval: int = 300):
        # Limit concurrency for image processing as it's CPU intensive
        self.concurrent_limit = concurrent_limit
        self.semaphore = asyncio.Semaphore(concurrent_limit)
        self.loop_interval = loop_interval
        self.running = False
        self.blur_threshold = 100.0

    def calculate_sharpness(self, image):
        """
        Calculate the variance of the Laplacian of the image.
        Returns the variance (float).
        """
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        return cv2.Laplacian(gray, cv2.CV_64F).var()

    async def check_camera_image(self, camera_id: str, rtsp_url: str):
        """
        Check a single camera's image quality.
        Returns (camera_id, variance, is_error)
        """
        async with self.semaphore:
            if not rtsp_url:
                return camera_id, None, True
            
            # Run OpenCV in a separate thread to avoid blocking the event loop
            loop = asyncio.get_event_loop()
            try:
                variance = await loop.run_in_executor(None, self._process_stream, rtsp_url)
                return camera_id, variance, False
            except Exception as e:
                # logger.error(f"Error processing camera {camera_id}: {e}")
                return camera_id, None, True

    def _process_stream(self, rtsp_url: str):
        """
        Synchronous function to capture frame and calculate sharpness.
        """
        try:
            cap = cv2.VideoCapture(rtsp_url)
            if not cap.isOpened():
                return None
            
            # Read one frame
            ret, frame = cap.read()
            cap.release()
            
            if not ret or frame is None:
                return None
            
            return self.calculate_sharpness(frame)
        except Exception:
            return None

    async def run_once(self):
        """
        Run one full sweep of image quality checks.
        """
        logger.info("Starting background blur detection sweep...")
        start_time = datetime.now()
        
        db = SessionLocal()
        try:
            # Only check cameras that are known to be UP
            cameras = db.query(models.Camera).filter(models.Camera.status == "up").all()
            
            if not cameras:
                logger.info("No online cameras to check.")
                return

            tasks = []
            camera_map = {c.id: c for c in cameras}
            
            for cam in cameras:
                if cam.rtsp_url:
                    tasks.append(self.check_camera_image(cam.id, cam.rtsp_url))
            
            if not tasks:
                logger.info("No cameras with RTSP URLs found.")
                return

            # Run all checks
            results = await asyncio.gather(*tasks)
            
            updates_count = 0
            
            for cam_id, variance, is_error in results:
                camera = camera_map.get(cam_id)
                if not camera:
                    continue

                # Update timestamp
                camera.last_image_check = datetime.now(THAILAND_TZ)
                
                if is_error or variance is None:
                    # Could not read stream, but ping said it's up.
                    # Maybe mark as unknown or just ignore image status update?
                    # For now, let's leave it as is, or maybe 'unknown' image status?
                    # Requirement says: Online but blur -> Orange.
                    # If we can't get image, effectively we don't know if it's blur.
                    continue

                camera.sharpness_value = variance
                
                # Logic for status transition
                is_blurry = variance < self.blur_threshold
                
                if is_blurry:
                    camera.blur_consistency_count += 1
                    camera.normal_consistency_count = 0
                    
                    if camera.blur_consistency_count >= 1:
                        if camera.image_status != "blur":
                            camera.image_status = "blur"
                            updates_count += 1
                else:
                    camera.normal_consistency_count += 1
                    camera.blur_consistency_count = 0
                    
                    if camera.normal_consistency_count >= 2:
                        if camera.image_status != "normal":
                            camera.image_status = "normal"
                            updates_count += 1
            
            if updates_count > 0:
                db.commit()
                logger.info(f"Updated image status for {updates_count} cameras.")
            
            elapsed = (datetime.now() - start_time).total_seconds()
            logger.info(f"Blur detection sweep completed in {elapsed:.2f}s. Checked {len(tasks)} cameras.")
            
        except Exception as e:
            logger.error(f"Error in blur worker run: {e}")
        finally:
            db.close()

    async def start_loop(self):
        """
        Start the infinite loop, running once every day at midnight (TH Time).
        """
        self.running = True
        logger.info("Blur Worker Loop Started (Scheduled for Midnight).")
        
        while self.running:
            try:
                now = datetime.now(THAILAND_TZ)
                # Find next midnight
                next_run = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
                wait_seconds = (next_run - now).total_seconds()
                
                logger.info(f"Waiting {wait_seconds:.2f}s until next midnight check...")
                await asyncio.sleep(wait_seconds)
                
                if not self.running:
                    break
                    
                await self.run_once()
            except Exception as e:
                logger.error(f"Critical error in blur loop: {e}")
                # Prevent tight loop on error, wait a minute before retrying calculation
                await asyncio.sleep(60)

    def stop(self):
        self.running = False
