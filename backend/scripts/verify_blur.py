
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import cv2
import numpy as np
from app.services.blur_worker import BlurWorker

def create_dummy_image(blurry=False):
    img = np.zeros((100, 100), dtype=np.uint8)
    if not blurry:
        cv2.randn(img, 128, 50)
    else:
        img[:] = 128
    return cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)

def main():
    print("Starting Manual Verification for Blur Detection...")
    
    worker = BlurWorker()
    
    # 1. Test Calculation Logic
    sharp = create_dummy_image(blurry=False)
    blur = create_dummy_image(blurry=True)
    
    score_sharp = worker.calculate_sharpness(sharp)
    score_blur = worker.calculate_sharpness(blur)
    
    print(f"Sharp Image Score: {score_sharp}")
    print(f"Blur Image Score: {score_blur}")
    
    if score_sharp > 100 and score_blur < 10:
        print("✅ Logic Verification PASSED")
    else:
        print("❌ Logic Verification FAILED")

    print("\nNote: Database verification requires running app against real DB.")
    print("This script verifies the core detection logic only.")

if __name__ == "__main__":
    main()
