import asyncio
import logging
from datetime import datetime
from sqlalchemy.orm import Session
from app import models
from app.db.session import SessionLocal
from app.services.camera import THAILAND_TZ
from app.services.camera_checker import check_camera_status

logger = logging.getLogger(__name__)

class StatusWorker:
    def __init__(self, concurrent_limit: int = 50, loop_interval: int = 60):
        # Limit concurrency for image processing as it's CPU intensive
        self.concurrent_limit = concurrent_limit
        self.semaphore = asyncio.Semaphore(concurrent_limit)
        self.loop_interval = loop_interval
        self.running = False

    async def process_camera(self, camera_id: int, ip_address: str, rtsp_url: str):
        """
        Run check_camera_status in a thread pool.
        Returns (camera_id, status)
        """
        async with self.semaphore:
            loop = asyncio.get_event_loop()
            try:
                # Run the synchronous check_camera_status in executor
                status = await loop.run_in_executor(
                    None, 
                    check_camera_status, 
                    ip_address, 
                    rtsp_url
                )
                return camera_id, status
            except Exception as e:
                logger.error(f"Error checking camera {camera_id}: {e}")
                return camera_id, "offline" # Fallback on error

    async def run_once(self):
        """
        Run one full sweep of status checks.
        """
        logger.info("Starting background camera status check...")
        start_time = datetime.now()
        
        db = SessionLocal()
        try:
            cameras = db.query(models.Camera).all()
            
            if not cameras:
                logger.info("No cameras to check.")
                return

            tasks = []
            camera_map = {c.id: c for c in cameras}
            
            for cam in cameras:
                tasks.append(self.process_camera(cam.id, cam.ip_address, cam.rtsp_url))
            
            # Run all checks
            results = await asyncio.gather(*tasks)
            
            updates_count = 0
            
            for cam_id, new_status in results:
                camera = camera_map.get(cam_id)
                if not camera:
                    continue

                if camera.status != new_status:
                    camera.status = new_status
                    # Also update image_status based on status for backward compatibility if needed?
                    # The prompt implies status dictates color.
                    # We might want to keep image_status in sync or deprecated.
                    # For now just set status.
                    camera.last_update = datetime.now(THAILAND_TZ).strftime("%Y-%m-%d %H:%M:%S")
                    updates_count += 1
                
                # Update last check time regardless of change
                # camera.last_image_check = datetime.now(THAILAND_TZ) # Field might be used for 'last seen'

            if updates_count > 0:
                db.commit()
                logger.info(f"Updated status for {updates_count} cameras.")
            
            elapsed = (datetime.now() - start_time).total_seconds()
            logger.info(f"Status check completed in {elapsed:.2f}s. Checked {len(tasks)} cameras.")
            
        except Exception as e:
            logger.error(f"Error in status worker run: {e}")
        finally:
            db.close()

    async def start_loop(self):
        self.running = True
        logger.info(f"Status Worker Loop Started (Interval: {self.loop_interval}s).")
        
        while self.running:
            try:
                await self.run_once()
            except Exception as e:
                logger.error(f"Critical error in status loop: {e}")
                
            # Wait for interval
            if self.running:
                 await asyncio.sleep(self.loop_interval)

    def stop(self):
        self.running = False
