
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
    def __init__(self, check_interval: int = 300, threshold: float = 100.0, progress_callback=None):
        self.check_interval = check_interval # 5 minutes
        self.threshold = threshold
        self.progress_callback = progress_callback
        self.running = False
        self._shutdown = False

    # ... check_sharpness remains same ...

    async def run_once(self):
        """
        Run blur check for all UP cameras.
        Sequential execution is acceptable here as confirmed in design.
        """
        logger.info("Starting background blur check...")
        start_time = datetime.now()
        
        db = SessionLocal()
        try:
            # Filter for cameras that are ONLINE (formerly UP)
            cameras = db.query(models.Camera).filter(models.Camera.status == "online").all()
            total_cameras = len(cameras)
            
            # Report Initial Progress (0 / Total)
            if self.progress_callback:
                await self.progress_callback(0, total_cameras)
            
            updates_count = 0
            
            for index, cam in enumerate(cameras):
                if self._shutdown:
                    break
                    
                # Report Progress
                if self.progress_callback:
                    await self.progress_callback(index + 1, total_cameras)

                # Check blur
                variance = await asyncio.to_thread(self.check_sharpness, cam.rtsp_url)
                
                # Determine status
                new_image_status = "blur" if variance < self.threshold else "normal"
                
                # Update DB
                # Always update last_image_check
                needs_update = False
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
            
            # Final progress update
            if self.progress_callback:
                await self.progress_callback(total_cameras, total_cameras)
                # Optional: Send a "done" signal or simply let it finish
            
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
