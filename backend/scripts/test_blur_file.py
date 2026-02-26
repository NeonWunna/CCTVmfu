import cv2
import sys
import os

def check_blur(image_path: str, threshold: float = 50.0):
    print(f"📸 Testing image: {image_path}")
    
    if not os.path.exists(image_path):
        print("❌ Error: File not found. Please check the path.")
        return
        
    image = cv2.imread(image_path)
    if image is None:
        print("❌ Error: Could not load image. It might not be a valid image file.")
        return
        
    # แปลงเป็นภาพขาวดำ
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # คำนวณความเบลอด้วย Laplacian variance (แบบเดียวกับที่ใช้ในระบบ)
    variance = cv2.Laplacian(gray, cv2.CV_64F).var()
    
    status = "BLUR" if variance < threshold else "NORMAL"
    
    print("-" * 30)
    print(f"Score (Variance)  : {variance:.2f}")
    print(f"Threshold         : {threshold}")
    print(f"Result            : {status}")
    print("-" * 30)
    
    if variance >= threshold:
        print("⚠️ หมายเหตุ: ภาพนี้ได้คะแนนเกินเกณฑ์ (Normal)")
        print("หากดูด้วยตาแล้วเบลอ อาจเกิดจากระบบจับ 'ความคมกริบของตัวหนังสือ' (Timestamp) ในภาพแทนครับ")
    
if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python test_blur_file.py <path_to_image_file>")
    else:
        check_blur(sys.argv[1])
