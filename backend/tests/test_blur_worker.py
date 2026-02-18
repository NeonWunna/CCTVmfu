import sys
import os
import unittest
from unittest.mock import MagicMock, patch, AsyncMock
import asyncio
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.blur_worker import BlurWorker
from app.models.camera import Camera

class TestBlurWorker(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.worker = BlurWorker(concurrent_limit=1, loop_interval=1)
        self.worker.blur_threshold = 100.0

    @patch('app.services.blur_worker.SessionLocal')
    @patch('app.services.blur_worker.cv2.VideoCapture')
    async def test_detect_blur_transition(self, mock_capture, mock_session_cls):
        # Mock DB Session
        mock_db = MagicMock()
        mock_session_cls.return_value = mock_db
        
        # Mock Camera
        camera = Camera(
            id=1, 
            name="Test Cam", 
            ip_address="1.2.3.4", 
            status="up", 
            rtsp_url="rtsp://test",
            image_status="normal",
            blur_consistency_count=0,
            normal_consistency_count=0
        )
        mock_db.query.return_value.filter.return_value.all.return_value = [camera]
        
        # Mock OpenCV to return a BLURRY frame (low variance)
        mock_cap_instance = MagicMock()
        mock_capture.return_value = mock_cap_instance
        mock_cap_instance.isOpened.return_value = True
        
        # Create a blank image (low variance)
        import numpy as np
        blank_image = np.zeros((100, 100, 3), dtype=np.uint8)
        mock_cap_instance.read.return_value = (True, blank_image)
        
        # Run 3 times to trigger state change (count >= 3)
        for _ in range(3):
            await self.worker.run_once()
            
        # Verify status is now 'blur'
        self.assertEqual(camera.image_status, "blur")
        self.assertEqual(camera.blur_consistency_count, 3)
        print("Test 1 (Blur Transition): PASSED")

    @patch('app.services.blur_worker.SessionLocal')
    @patch('app.services.blur_worker.cv2.VideoCapture')
    async def test_detect_normal_transition(self, mock_capture, mock_session_cls):
        # Mock DB Session
        mock_db = MagicMock()
        mock_session_cls.return_value = mock_db
        
        # Mock Camera starting as BLUR
        camera = Camera(
            id=1, 
            name="Test Cam", 
            ip_address="1.2.3.4", 
            status="up", 
            rtsp_url="rtsp://test",
            image_status="blur",
            blur_consistency_count=3,
            normal_consistency_count=0
        )
        mock_db.query.return_value.filter.return_value.all.return_value = [camera]
        
        # Mock OpenCV to return a SHARP frame (high variance)
        mock_cap_instance = MagicMock()
        mock_capture.return_value = mock_cap_instance
        mock_cap_instance.isOpened.return_value = True
        
        # Create a noise image (high variance)
        import numpy as np
        noise_image = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)
        mock_cap_instance.read.return_value = (True, noise_image)
        
        # Run 2 times to trigger state change (count >= 2)
        for _ in range(2):
            await self.worker.run_once()
            
        # Verify status is now 'normal'
        self.assertEqual(camera.image_status, "normal")
        self.assertEqual(camera.normal_consistency_count, 2)
        print("Test 2 (Normal Transition): PASSED")

if __name__ == '__main__':
    unittest.main()
