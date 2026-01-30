import json
import os
import sys

# Add parent directory to path to allow importing app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import SessionLocal, engine
from app.db.base import Base
from app.models.camera import Camera

def import_cctv_data():
    # Ensure tables exist
    Base.metadata.create_all(bind=engine)

    json_file_path = os.path.join(os.path.dirname(__file__), 'cctvinfo.json')
    
    if not os.path.exists(json_file_path):
        print(f"Error: File not found at {json_file_path}")
        return

    print(f"Reading data from {json_file_path}...")
    with open(json_file_path, 'r', encoding='utf-8') as f:
        content = f.read().strip()
        
    # Fix format: if it's a sequence of objects separated by commas but not in an array
    if content.startswith('{') and content.endswith('}'):
        # Check if it looks like multiple objects like {}, {}
        # We can try wrapping it in []
        content = f"[{content}]"
        
    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        # If that failed, maybe it has a trailing comma?
        if content.strip().endswith(',]'):
             content = content.replace(',]', ']')
             data = json.loads(content)
        else:
             raise


    db = SessionLocal()
    try:
        count_new = 0
        count_updated = 0
        
        for item in data:
            ip_address = item.get('ip_address')
            if not ip_address:
                continue

            # Extract NO for RTSP URL generation
            no = item.get('NO')
            rtsp_url = None
            if no:
               rtsp_url = f"rtsp://mfustream:mediamfu2025@172.30.36.13:554/LiveMedia/ch{no}/Media1/trackID={no}"

            # Map JSON fields to model fields
            camera_data = {
                'ip_address': ip_address,
                'name': str(item.get('name')) if item.get('name') is not None else None,
                'location': str(item.get('location')) if item.get('location') is not None else None,
                'coordinates': f"{item.get('latitude')}, {item.get('longitude')}",
                'status': 'down', # Default status, will be updated by background service
                'rtsp_url': rtsp_url
            }

            # Check if camera exists
            existing_camera = db.query(Camera).filter(Camera.ip_address == ip_address).first()

            if existing_camera:
                # Update existing camera
                changed = False
                for key, value in camera_data.items():
                    # converting coordinates to proper string format for comparison might be tricky so we just update
                    # simpler to just update fields
                    if getattr(existing_camera, key) != value:
                        setattr(existing_camera, key, value)
                        changed = True
                
                if changed:
                    count_updated += 1
            else:
                # Create new camera
                new_camera = Camera(**camera_data)
                db.add(new_camera)
                count_new += 1

        db.commit()
        print(f"Import completed successfully.")
        print(f"New cameras added: {count_new}")
        print(f"Cameras updated: {count_updated}")

    except Exception as e:
        print(f"An error occurred: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    import_cctv_data()
