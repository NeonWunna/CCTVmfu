import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add the parent directory to sys.path to resolve 'app' module
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.db.session import SessionLocal
from app.models.camera import Camera

def toggle_blur(ip_address, status):
    db = SessionLocal()
    try:
        camera = db.query(Camera).filter(Camera.ip_address == ip_address).first()
        if not camera:
            print(f"Camera with IP {ip_address} not found.")
            return

        camera.image_status = status
        # Reset consistency counts to avoid immediate override by worker if running
        if status == 'blur':
            camera.blur_consistency_count = 3
            camera.normal_consistency_count = 0
            camera.sharpness_value = 50.0
        else:
            camera.blur_consistency_count = 0
            camera.normal_consistency_count = 2
            camera.sharpness_value = 500.0
            
        db.commit()
        print(f"Updated camera {camera.name} ({ip_address}) image_status to '{status}'")
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python toggle_blur.py <ip_address> <status: normal|blur>")
        sys.exit(1)
    
    ip = sys.argv[1]
    status = sys.argv[2]
    
    if status not in ['normal', 'blur']:
        print("Status must be 'normal' or 'blur'")
        sys.exit(1)
        
    toggle_blur(ip, status)
