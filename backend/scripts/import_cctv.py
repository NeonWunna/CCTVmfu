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

    json_files = ['cctvinfo2.json', 'oldcctvinfo2.json']
    
    db = SessionLocal()
    current_ip = None # Initialize current_ip
    try:
        count_new = 0
        count_updated = 0

        for json_filename in json_files:
            json_file_path = os.path.join(os.path.dirname(__file__), json_filename)
            
            if not os.path.exists(json_file_path):
                print(f"Error: File not found at {json_file_path}")
                continue

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
                     print(f"Failed to parse JSON from {json_filename}")
                     continue

            for item in data:
                raw_ip = item.get('IP ADDRESS')
                if not raw_ip:
                    continue
                
                ip_address = str(raw_ip).strip()
                current_ip = ip_address # Update current_ip for error tracking
                # print(f"Processing IP: {ip_address}") # Debug output

                # Extract RTSP URL — try 'enable rtsp' first (used by oldcctvinfo2.json),
                # then fall back to 'ANPR&PTZ RTSP'.
                def get_rtsp(item):
                    for field in ('enable rtsp', 'ANPR&PTZ RTSP'):
                        val = str(item.get(field, '') or '').strip()
                        if val.lower().startswith('rtsp://'):
                            return val
                    return ''
                rtsp_url = get_rtsp(item)

                # Map JSON fields to model fields
                camera_data = {
                    'ip_address': ip_address,
                    'name': str(item.get('CAMERA NAME_NEW')) if item.get('CAMERA NAME_NEW') is not None else None,
                    'location': str(item.get('Location')) if item.get('Location') is not None else None,
                    'coordinates': f"{item.get('Latitude')}, {item.get('Longtitude')}",
                    'rtsp_url': rtsp_url
                }

                # Check if camera exists
                existing_camera = db.query(Camera).filter(Camera.ip_address == ip_address).first()

                if existing_camera:
                    # Update existing camera — do NOT overwrite status (preserves online/offline from ping_worker)
                    skip_fields = {'status'}
                    changed = False
                    for key, value in camera_data.items():
                        if key in skip_fields:
                            continue
                        if getattr(existing_camera, key) != value:
                            setattr(existing_camera, key, value)
                            changed = True
                    
                    if changed:
                        count_updated += 1
                else:
                    # Create new camera — set initial status 'down'
                    new_camera = Camera(**camera_data, status='down')
                    db.add(new_camera)
                    db.flush() # Ensure it's visible to subsequent queries in same transaction
                    count_new += 1
            
            # Commit after each file to ensure subsequent files can see the changes
            db.commit()

        print(f"Import completed successfully.")
        print(f"New cameras added: {count_new}")
        print(f"Cameras updated: {count_updated}")

    except Exception as e:
        print(f"An error occurred processing IP {current_ip}: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    import_cctv_data()
