
import cv2
import logging
import time
import asyncio
import requests
import numpy as np
import urllib.parse
from datetime import datetime, timedelta
from app import models
from app.db.session import SessionLocal
from app.services.camera import THAILAND_TZ

logger = logging.getLogger(__name__)

# go2rtc API base URL (container name on same docker network)
GO2RTC_API_URL = "http://cctv_go2rtc:1984"


class BlurWorker:
    def __init__(self, check_interval: int = 300, threshold: float = 50.0):
        self.check_interval = check_interval # 5 minutes
        self.threshold = threshold
        self.running = False
        self._shutdown = False

    def _fetch_frame_from_go2rtc(self, rtsp_url: str) -> np.ndarray | None:
        """
        Fetch a JPEG frame from go2rtc snapshot API.
        Returns decoded frame (numpy array) or None if failed.
        """
        try:
            encoded_url = urllib.parse.quote(rtsp_url, safe='')
            snapshot_url = f"{GO2RTC_API_URL}/api/frame.jpeg?src={encoded_url}"
            
            response = requests.get(snapshot_url, timeout=10)
            if response.status_code == 200 and response.content:
                # Decode JPEG to numpy array
                nparr = np.frombuffer(response.content, np.uint8)
                frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                return frame
            else:
                logger.warning(f"go2rtc snapshot failed: status={response.status_code}")
                return None
        except Exception as e:
            logger.warning(f"go2rtc snapshot error for {rtsp_url}: {e}")
            return None

    def _fetch_frame_direct(self, rtsp_url: str) -> np.ndarray | None:
        """
        Fetch frame directly via OpenCV RTSP (fallback).
        """
        try:
            cap = cv2.VideoCapture(rtsp_url)
            if not cap.isOpened():
                return None
            
            ret, frame = cap.read()
            cap.release()
            
            if not ret or frame is None:
                return None
            return frame
        except Exception as e:
            logger.warning(f"Direct RTSP error for {rtsp_url}: {e}")
            return None

    def check_sharpness(self, rtsp_url: str) -> float:
        """
        Capture a frame and calculate Laplacian variance.
        Tries go2rtc snapshot API first, falls back to direct RTSP.
        Returns variance (float). Returns 0.0 if failed.
        """
        if not rtsp_url:
            return 0.0

        # Try go2rtc snapshot API first (works even with auth issues)
        frame = self._fetch_frame_from_go2rtc(rtsp_url)
        
        # Fallback to direct RTSP if go2rtc failed
        if frame is None:
            logger.info(f"Falling back to direct RTSP for blur check")
            frame = self._fetch_frame_direct(rtsp_url)

        if frame is None:
            logger.error(f"Could not fetch frame for blur check: {rtsp_url}")
            return 0.0

        try:
            # Convert to grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Calculate Laplacian variance
            laplacian = cv2.Laplacian(gray, cv2.CV_64F)
            variance = laplacian.var()
            
            return variance
        except Exception as e:
            logger.error(f"Error calculating blur for {rtsp_url}: {e}")
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
                cam.sharpness_value = float(variance)
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
