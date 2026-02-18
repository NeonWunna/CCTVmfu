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

    files_to_import = ['cctvinfo2.json', 'oldcctvinfo.json']
    
    db = SessionLocal()
    counters = {'new': 0, 'updated': 0}

    try:
        for filename in files_to_import:
            process_file(filename, db, counters)
        
        db.commit()
        print(f"Import completed successfully.")
        print(f"New cameras added: {counters['new']}")
        print(f"Cameras updated: {counters['updated']}")

    except Exception as e:
        print(f"An error occurred during import: {e}")
        db.rollback()
    finally:
        db.close()

def process_file(filename, db, counters):
    json_file_path = os.path.join(os.path.dirname(__file__), filename)
    
    if not os.path.exists(json_file_path):
        print(f"Warning: File not found at {json_file_path}")
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
             print(f"Error decoding JSON in {filename}")
             raise

    print(f"Processing {len(data)} items from {filename}...")

    for item in data:
        ip_address = item.get('IP ADDRESS')
        if not ip_address:
            continue

        # Extract generated RTSP or use specific field
        rtsp_url = item.get('ANPR&PTZ RTSP')
        
        # If the specific field is empty, generate the default format
        if not rtsp_url and ip_address:
           rtsp_url = f"rtsp://{ip_address}:554/LiveMedia/ch1/Media1/trackID=1"

        # Map JSON fields to model fields
        camera_data = {
            'ip_address': ip_address,
            'name': str(item.get('CAMERA NAME_NEW')) if item.get('CAMERA NAME_NEW') is not None else None,
            'location': str(item.get('Location')) if item.get('Location') is not None else None,
            'coordinates': f"{item.get('Latitude')}, {item.get('Longtitude')}",
            'status': 'down', # Default status, will be updated by background service
            'rtsp_url': rtsp_url
        }

        # Check if camera exists
        existing_camera = db.query(Camera).filter(Camera.ip_address == ip_address).first()

        if existing_camera:
            # Update existing camera
            changed = False
            for key, value in camera_data.items():
                if getattr(existing_camera, key) != value:
                    setattr(existing_camera, key, value)
                    changed = True
            
            if changed:
                counters['updated'] += 1
        else:
            # Create new camera
            new_camera = Camera(**camera_data)
            db.add(new_camera)
            counters['new'] += 1

if __name__ == "__main__":
    import_cctv_data()
