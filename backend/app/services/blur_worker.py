
import cv2
import logging
import time
import asyncio
from datetime import datetime, timedelta
from app import models
from app.db.session import SessionLocal
from app.services.camera import THAILAND_TZ

logger = logging.getLogger(__name__)

class BlurWorker:
    def __init__(self, check_interval: int = 300, threshold: float = 100.0):
        self.check_interval = check_interval # 5 minutes
        self.threshold = threshold
        self.running = False
        self._shutdown = False

    def check_sharpness(self, rtsp_url: str) -> float:
        """
        Capture a frame and calculate Laplacian variance.
        Returns variance (float). Returns 0.0 if failed.
        """
        if not rtsp_url:
            return 0.0
            
        try:
            # Open stream
            cap = cv2.VideoCapture(rtsp_url)
            if not cap.isOpened():
                return 0.0
            
            # Read one frame
            ret, frame = cap.read()
            cap.release()
            
            if not ret or frame is None:
                return 0.0
                
            # Convert to grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Calculate Laplacian variance
            laplacian = cv2.Laplacian(gray, cv2.CV_64F)
            variance = laplacian.var()
            
            return variance
        except Exception as e:
            logger.error(f"Error checking blur for {rtsp_url}: {e}")
            return 0.0

    async def run_once(self):
        """
        Run blur check for all UP cameras.
        Sequential execution is acceptable here as confirmed in design.
        """
        logger.info("Starting background blur check...")
        start_time = datetime.now()
        
        db = SessionLocal()
        try:
            # Filter for cameras that are ONLINE and have a non-empty rtsp_url
            cameras = db.query(models.Camera).filter(
                models.Camera.status == "online",
                models.Camera.rtsp_url != None,
                models.Camera.rtsp_url != ""
            ).all()
            
            updates_count = 0
            
            for cam in cameras:
                if self._shutdown:
                    break
                    
                # We can perform the check in a thread to strictly avoid blocking the loop 
                # (although run_once is called in a task, blocking here blocks this task, not the whole app if other tasks are concurrent)
                # But CV2 is CPU bound mostly.
                
                # Check blur
                variance = await asyncio.to_thread(self.check_sharpness, cam.rtsp_url)
                
                # Determine status
                new_image_status = "blur" if variance < self.threshold else "normal"
                
                # Update DB
                # Always update last_image_check
                needs_update = False
                
                # Check if we need to update the main status to 'blurry'
                if new_image_status == "blur" and cam.status != "blurry":
                    logger.info(f"Camera {cam.id} status changed to blurry! (Score: {variance:.2f})")
                    cam.status = "blurry"
                    needs_update = True
                    
                if cam.image_status != new_image_status:
                    logger.info(f"Camera {cam.id} image status changed: {cam.image_status} -> {new_image_status} (Score: {variance:.2f})")
                    cam.image_status = new_image_status
                    needs_update = True
                
                # Update score and timestamp
                cam.sharpness_value = variance
                cam.last_image_check = datetime.now(THAILAND_TZ).strftime("%Y-%m-%d %H:%M:%S")
                
                # Commit periodically or per camera? Per camera is safer for long running loop
                # optimization: commit every 10?
                db.commit() 
                db.refresh(cam)
                updates_count += 1
                
                # Small sleep to be nice to CPU?
                await asyncio.sleep(0.1)

            elapsed = (datetime.now() - start_time).total_seconds()
            logger.info(f"Blur check completed in {elapsed:.2f}s. Scanned {len(cameras)} cameras.")
            
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
            
            # sleep for interval
            for _ in range(self.check_interval):
                if not self.running:
                    break
                await asyncio.sleep(1)

    def stop(self):
        self.running = False
        self._shutdown = True
