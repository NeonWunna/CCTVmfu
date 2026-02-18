
import asyncio
import logging
from datetime import datetime
from sqlalchemy.orm import Session
from app import models
from app.db.session import SessionLocal
from app.utils.network import check_port_async
from app.services.camera import THAILAND_TZ

logger = logging.getLogger(__name__)

class PingWorker:
    def __init__(self, concurrent_limit: int = 200, default_port: int = 80):
        self.concurrent_limit = concurrent_limit
        self.default_port = default_port
        self.semaphore = asyncio.Semaphore(concurrent_limit)
        self.running = False

    async def check_camera(self, camera_id: str, ip_address: str, current_status: str, rtsp_url: str = None):
        """
        Check a single camera and return validation result.
        Returns (camera_id, is_up)
        """
        async with self.semaphore:
            # Determine port: 554 if RTSP is present, else default (80)
            port = self.default_port
            if rtsp_url:
                # Naive check for port in URL
                # rtsp://user:pass@ip:port/path
                try:
                    # Very basic parsing, can be improved
                    if ":554" in rtsp_url:
                        port = 554
                except:
                    pass
            
            # Prioritize 554 for CCTV if we suspect it's a stream
            # But the requirement said 554 or 80.
            # Let's try 554 first if rtsp, else 80.
            # Actually, let's keep it simple: try 80, if fail try 554? 
            # Or just strictly 80 for web interface availability?
            # The prompt said "Check port: 554 (RTSP) OR 80". 
            # Let's try 80 first (management), then 554 (stream). 
            # If either is open, it's UP.
            
            is_up = await check_port_async(ip_address, 80, timeout=1.0)
            if not is_up:
                is_up = await check_port_async(ip_address, 554, timeout=1.0)
                
            return camera_id, is_up

    async def run_once(self):
        """
        Run one full sweep of checks.
        """
        logger.info("Starting background camera ping sweep...")
        start_time = datetime.now()
        
        # Create a new DB session for reading cameras using the factory
        # We use a context manager to ensure it closes
        db = SessionLocal()
        try:
            cameras = db.query(models.Camera).all()
            
            tasks = []
            for cam in cameras:
                tasks.append(self.check_camera(cam.id, cam.ip_address, cam.status, cam.rtsp_url))
            
            # Run all checks
            results = await asyncio.gather(*tasks)
            
            # Process results and update DB
            updates_count = 0
            
            # We need to re-fetch cameras or keep them attached? 
            # Better to batch update or update one by one. 
            # Since we have the ID, let's fetch only those that need update or update in bulk?
            # Updating one by one in a single transaction might be safer for concurrency 
            # or just simple enough.
            
            for cam_id, is_up in results:
                new_status = "up" if is_up else "down"
                
                # Find the camera object in our current session list
                # optimization: map id to camera object
                camera = next((c for c in cameras if c.id == cam_id), None)
                
                if camera and camera.status != new_status:
                    camera.status = new_status
                    camera.last_update = datetime.now(THAILAND_TZ).strftime("%Y-%m-%d %H:%M:%S")
                    updates_count += 1
            
            if updates_count > 0:
                db.commit()
                logger.info(f"Updated status for {updates_count} cameras.")
            
            elapsed = (datetime.now() - start_time).total_seconds()
            logger.info(f"Ping sweep completed in {elapsed:.2f}s. Scanned {len(cameras)} cameras.")
            
        except Exception as e:
            logger.error(f"Error in ping worker run: {e}")
        finally:
            db.close()

    async def start_loop(self):
        """
        Start the infinite loop.
        """
        self.running = True
        logger.info("Ping Worker Loop Started.")
        while self.running:
            try:
                await self.run_once()
            except Exception as e:
                logger.error(f"Critical error in ping loop: {e}")
            
            # Wait for 30 seconds
            await asyncio.sleep(30)

    def stop(self):
        self.running = False
