import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import SessionLocal
from app.models.camera import Camera

def verify_import():
    db = SessionLocal()
    try:
        count = db.query(Camera).count()
        print(f"Total cameras in DB: {count}")
        
        # Check a specific camera
        camera = db.query(Camera).filter(Camera.ip_address == "172.30.36.11").first()
        if camera:
            print(f"Found camera: {camera.name}")
            print(f"IP: {camera.ip_address}")
            print(f"Status: {camera.status}")
            print(f"Coordinates: {camera.coordinates}")
        else:
            print("Camera 172.30.36.11 not found")
            
    finally:
        db.close()

if __name__ == "__main__":
    verify_import()
