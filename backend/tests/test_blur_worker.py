
import pytest
import cv2
import numpy as np
import asyncio
from unittest.mock import MagicMock, patch, AsyncMock
from app.services.blur_worker import BlurWorker
from app import models

def create_dummy_image(variance=100):
    # greater variance = sharper
    # lesser variance = blurrier
    img = np.zeros((100, 100, 3), dtype=np.uint8)
    if variance > 500:
        cv2.randn(img, 128, 50) # Noise creates high variance/edges
        cv2.putText(img, "SHARP", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    else:
        cv2.randn(img, 128, 5) # Low contrast noise
        img = cv2.GaussianBlur(img, (21, 21), 0) # Blur it
        
    return img

@pytest.mark.asyncio
async def test_check_sharpness_logic():
    worker = BlurWorker(threshold=100.0)
    
    # Mock cv2.VideoCapture
    with patch('cv2.VideoCapture') as mock_cap_cls:
        mock_cap = MagicMock()
        mock_cap_cls.return_value = mock_cap
        mock_cap.isOpened.return_value = True
        
        # Test Case 1: Sharp Image
        sharp_img = create_dummy_image(variance=1000)
        mock_cap.read.return_value = (True, sharp_img)
        
        variance = worker.check_sharpness("rtsp://sharp")
        assert variance > 100.0
        
        # Test Case 2: Blur Image
        blur_img = create_dummy_image(variance=10)
        mock_cap.read.return_value = (True, blur_img)
        
        variance = worker.check_sharpness("rtsp://blur")
        assert variance < 100.0
        
        # Test Case 3: Capture Fail
        mock_cap.read.return_value = (False, None)
        variance = worker.check_sharpness("rtsp://fail")
        assert variance == 0.0

@pytest.mark.asyncio
async def test_blur_worker_run_once():
    # Helper to create dummy cameras
    cameras = [
        models.Camera(id=1, status="up", rtsp_url="rtsp://c1", image_status="normal"),
        models.Camera(id=2, status="up", rtsp_url="rtsp://c2", image_status="normal"),
        models.Camera(id=3, status="down", rtsp_url="rtsp://c3", image_status="normal") # Should be skipped
    ]
    
    with patch('app.services.blur_worker.SessionLocal') as mock_session_cls:
        mock_db = MagicMock()
        mock_session_cls.return_value = mock_db
        
        # Setup query return only UP cameras
        mock_db.query.return_value.filter.return_value.all.return_value = [cameras[0], cameras[1]]
        
        worker = BlurWorker(threshold=100.0)
        
        # Mock check_sharpness to avoid OpenCV calls in this test and just return variances
        # Cam1: 50 (Blur), Cam2: 200 (Sharp)
        with patch.object(worker, 'check_sharpness', side_effect=[50.0, 200.0]):
            await worker.run_once()
            
            # Verify Cam1 became blur
            assert cameras[0].image_status == "blur"
            assert cameras[0].sharpness_value == 50.0
            
            # Verify Cam2 stayed normal (or updated if logic sets it)
            # if camera was normal and is still normal, needs_update might be false 
            # but we update usage timestamp anyway if we implemented it that way.
            # In my code:
            # cam.sharpness_value = variance
            # cam.last_image_check = ...
            # db.commit() is called.
            
            assert cameras[1].image_status == "normal"
            assert cameras[1].sharpness_value == 200.0
            
            # Cam3 should not be touched
            assert cameras[2].image_status == "normal" 

if __name__ == "__main__":
    print("Run with pytest tests/test_blur_worker.py")
