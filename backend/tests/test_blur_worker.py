
import pytest
import cv2
import numpy as np
import os
from unittest.mock import MagicMock, patch
from app.services.blur_worker import BlurWorker
from app import models

# Helper to create a dummy image
def create_dummy_image(blurry=False):
    # Create a 100x100 gray image
    img = np.zeros((100, 100), dtype=np.uint8)
    
    if not blurry:
        # Add noise/edges to make it sharp
        cv2.randn(img, 128, 50)
    else:
        # Plain gray image (variance near 0)
        img[:] = 128
        
    # Convert to BGR as cv2.imread would return
    return cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)

def test_calculate_sharpness():
    worker = BlurWorker()
    
    # Sharp Image
    sharp_img = create_dummy_image(blurry=False)
    score_sharp = worker.calculate_sharpness(sharp_img)
    # Random noise usually has high variance
    assert score_sharp > 100 

    # Blurry Image
    blurry_img = create_dummy_image(blurry=True)
    score_blur = worker.calculate_sharpness(blurry_img)
    assert score_blur < 10

@patch('app.services.blur_worker.SessionLocal')
def test_check_all_cameras(mock_session_cls):
    # Setup Mock DB
    mock_db = MagicMock()
    mock_session_cls.return_value = mock_db
    
    # Setup Camera
    camera = models.Camera(id=1, name="Cam1", ip_address="1.2.3.4", status="up", rtsp_url="rtsp://test")
    # Query must return list of cameras
    mock_db.query.return_value.filter.return_value.all.return_value = [camera]
    
    # Setup Worker with mocked get_frame
    worker = BlurWorker(blur_threshold=50)
    
    # Create a blurry frame
    blurry_frame = create_dummy_image(blurry=True)
    
    # Mock get_frame to return our blurry frame
    with patch.object(worker, 'get_frame', return_value=blurry_frame):
        worker.check_all_cameras()
    
    # Assert
    assert camera.image_status == "blur"
    assert camera.blur_score < 50
    # Commit should be called at least once
    assert mock_db.commit.called

if __name__ == "__main__":
    print("Run with: pytest tests/test_blur_worker.py")
