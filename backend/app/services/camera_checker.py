import cv2
import numpy as np
import requests
import logging

# Configure logging
logger = logging.getLogger(__name__)

def check_camera_status(camera_ip: str, rtsp_url: str = None) -> str:
    """
    Check camera status based on a 4-step process:
    1. Ping/HTTP Health Check -> 'offline'
    2. RTSP Stream Connection -> 'no_signal'
    3. Frame Capture (Black/Empty) -> 'no_signal'
    4. Blur Detection -> 'blurry' or 'online'
    """
    
    # STEP 1: Health check (HTTP/Ping)
    # Using simple requests.get on port 80 as a proxy for 'ping' since raw ping requires privileges/subprocess
    camera_url = f"http://{camera_ip}"
    
    is_reachable = False
    try:
        # Short timeout for health check
        res = requests.get(camera_url, timeout=2)
        # Any response code implies reachable
        is_reachable = True
    except requests.exceptions.RequestException:
        # Try port 8080 or just assume unreachable on HTTP
        pass
    
    if not is_reachable:
        # Strict: if not reachable on HTTP, it is OFFLINE per prompt requirement.
        return "offline"

    # STEP 2: RTSP Stream Check
    if not rtsp_url:
        # If reachable but no RTSP to check, assume ONLINE (or could be NO_SIGNAL if stream expected)
        # Defaulting to ONLINE as reachability is confirmed.
        return "online"

    # STEP 3: Frame Capture
    cap = cv2.VideoCapture(rtsp_url)
    
    if not cap.isOpened():
        return "no_signal"  # -> Contactable but stream not opening
    
    try:
        ret, frame = cap.read()
    finally:
        cap.release()
    
    if not ret or frame is None:
        return "no_signal"  # -> Stream opened but no frame
    
    # Check if frame is black (mean pixel value < 5)
    if frame.mean() < 5:
        return "no_signal"  # -> Black image = no signal
    
    # STEP 4: Blur detection
    try:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        
        BLUR_THRESHOLD = 100.0
        if laplacian_var < BLUR_THRESHOLD:
            return "blurry"
    except Exception as e:
        logger.error(f"Error in blur detection: {e}")
        return "online"
    
    return "online"
