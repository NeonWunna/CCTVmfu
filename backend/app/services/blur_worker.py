
import cv2
import numpy as np
import logging
import time
from datetime import datetime
from threading import Thread, Event

class BlurWorker:
    def __init__(self, check_interval: int = 300, blur_threshold: float = 100.0):
        """
        Args:
            check_interval: Interval between checks in seconds (default 300s = 5mins)
            blur_threshold: Threshold for Laplacian variance (default 100.0)
        """
        self.check_interval = check_interval
        self.blur_threshold = blur_threshold
        self.stop_event = Event()
        self.thread = None

    def get_frame(self, rtsp_url: str):
        """
        Capture a single frame from RTSP stream.
        """
        try:
            # Open with generic options to speed up connection or fail faster?
            # For now default is fine.
            cap = cv2.VideoCapture(rtsp_url)
            if not cap.isOpened():
                return None
            
            # Read one frame
            ret, frame = cap.read()
            cap.release()
            
            if ret:
                return frame
            return None
        except Exception as e:
            logger.error(f"Error capturing frame from {rtsp_url}: {e}")
            return None

    def calculate_sharpness(self, frame) -> float:
        """
        Calculate sharpness using Laplacian Variance.
        """
        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            laplacian = cv2.Laplacian(gray, cv2.CV_64F)
            variance = laplacian.var()
            return variance
        except Exception as e:
            logger.error(f"Error calculating sharpness: {e}")
            return 0.0

    def check_all_cameras(self):
        """
        Iterate through all UP cameras and check for blur.
        This runs sequentially to avoid overloading the CPU.
        """
        logger.info("Starting Blur Detection Sweep...")
        start_time = datetime.now()
        
        # We need to manage session carefully. 
        # Iterating over query result keeps session active?
        # Ideally fetch IDs then process one by one with short-lived sessions
        # to avoid long transaction.
        
        db = SessionLocal()
        try:
            # 1. Get List of Candidate Cameras
            cameras = db.query(models.Camera).filter(
                models.Camera.status == 'up',
                models.Camera.rtsp_url != None
            ).all()
            # Detach objects so we can close session? 
            # Or just keep session open. 700 cams processing might take time.
            # Let's keep it simple: Keep session open but maybe commit frequently.
            
        except Exception as e:
            logger.error(f"Error fetching cameras: {e}")
            db.close()
            return

        checked_count = 0
        blurry_count = 0
        
        for camera in cameras:
            if self.stop_event.is_set():
                break
                
            try:
                frame = self.get_frame(camera.rtsp_url)
                if frame is not None:
                    score = self.calculate_sharpness(frame)
                    is_blurry = score < self.blur_threshold
                    
                    new_image_status = "blur" if is_blurry else "normal"
                    
                    # Update fields
                    camera.blur_score = score
                    camera.image_status = new_image_status
                    camera.last_blur_check = datetime.now(THAILAND_TZ).strftime("%Y-%m-%d %H:%M:%S")
                    
                    if is_blurry:
                        blurry_count += 1
                        
                    # Commit every update to be safe
                    db.commit() 
                    checked_count += 1
                    
            except Exception as e:
                logger.error(f"Error processing camera {camera.id}: {e}")
                continue
        
        db.close()
        elapsed = (datetime.now() - start_time).total_seconds()
        logger.info(f"Blur Sweep Completed: Checked {checked_count} cameras, Found {blurry_count} blurry. Time: {elapsed:.2f}s")

    def run_loop(self):
        """
        Main loop for the worker thread.
        """
        logger.info(f"Blur Worker Started (Interval: {self.check_interval}s)")
        
        # Run immediately on start? Or wait first? 
        # Usually run immediately.
        while not self.stop_event.is_set():
            try:
                self.check_all_cameras()
            except Exception as e:
                logger.error(f"Critical Error in Blur Worker: {e}")
            
            # Wait for interval or stop event
            if self.stop_event.wait(self.check_interval):
                break

    def start(self):
        if self.thread is None or not self.thread.is_alive():
            self.stop_event.clear()
            self.thread = Thread(target=self.run_loop, daemon=True)
            self.thread.start()

    def stop(self):
        if self.thread and self.thread.is_alive():
            self.stop_event.set()
            self.thread.join(timeout=5)
            logger.info("Blur Worker Stopped")
