"""
Camera Service
Business logic for camera operations.
"""
from typing import List, Optional
from datetime import datetime
from zoneinfo import ZoneInfo
from sqlalchemy.orm import Session

from app import models, schemas
import logging

logger = logging.getLogger(__name__)

# Thailand timezone
THAILAND_TZ = ZoneInfo("Asia/Bangkok")


class CameraService:
    """Service class for camera-related business logic."""
    
    def __init__(self, db: Session):
        """
        Initialize camera service.
        
        Args:
            db: SQLAlchemy database session
        """
        self.db = db

    def get_cameras(self, skip: int = 0, limit: int = 100) -> List[models.Camera]:
        """
        Retrieve all cameras with pagination.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
        
        Returns:
            List of camera models
        """
        return self.db.query(models.Camera).offset(skip).limit(limit).all()

    def get_camera(self, camera_id: int) -> Optional[models.Camera]:
        """
        Retrieve a specific camera by ID.
        
        Args:
            camera_id: ID of the camera to retrieve
        
        Returns:
            Camera model if found, None otherwise
        """
        return self.db.query(models.Camera).filter(
            models.Camera.id == camera_id
        ).first()

    def create_camera(self, camera: schemas.CameraCreate) -> models.Camera:
        """
        Create a new camera.
        """
        # Convert Pydantic model to dict, excluding lat/long which aren't in DB model
        camera_data = camera.model_dump(exclude={'latitude', 'longitude'})
        
        # Create coordinates string
        camera_data['coordinates'] = f"{camera.latitude}, {camera.longitude}"
        
        # Set initial last_update to now (Thailand timezone)
        if not camera_data.get('last_update'):
            camera_data['last_update'] = datetime.now(THAILAND_TZ).strftime("%Y-%m-%d %H:%M:%S")

        db_camera = models.Camera(**camera_data)
        self.db.add(db_camera)
        self.db.commit()
        self.db.refresh(db_camera)
        return db_camera

    def update_camera(
        self, 
        camera_id: int, 
        camera: schemas.CameraUpdate
    ) -> Optional[models.Camera]:
        """
        Update an existing camera.
        """
        db_camera = self.get_camera(camera_id)
        if db_camera:
            update_data = camera.model_dump(exclude_unset=True, exclude={'latitude', 'longitude'})
            
            # Handle coordinates update if lat or long provided
            if camera.latitude is not None or camera.longitude is not None:
                current_lat = 0.0
                current_long = 0.0
                
                # Safely parse existing coordinates
                if db_camera.coordinates and ',' in db_camera.coordinates:
                    try:
                        parts = db_camera.coordinates.split(',')
                        current_lat = float(parts[0].strip()) if len(parts) > 0 and parts[0].strip() else 0.0
                        current_long = float(parts[1].strip()) if len(parts) > 1 and parts[1].strip() else 0.0
                    except (ValueError, IndexError):
                        current_lat = 0.0
                        current_long = 0.0
                
                new_lat = camera.latitude if camera.latitude is not None else current_lat
                new_long = camera.longitude if camera.longitude is not None else current_long
                
                update_data['coordinates'] = f"{new_lat}, {new_long}"

            # Always update last_update timestamp (Thailand timezone)
            update_data['last_update'] = datetime.now(THAILAND_TZ).strftime("%Y-%m-%d %H:%M:%S")

            # Prevent manual status update (system controlled via ping)
            if 'status' in update_data:
                del update_data['status']

            for key, value in update_data.items():
                setattr(db_camera, key, value)
            self.db.commit()
            self.db.refresh(db_camera)
        return db_camera

    def delete_camera(self, camera_id: int) -> Optional[models.Camera]:
        """
        Delete a camera.
        
        Args:
            camera_id: ID of the camera to delete
        
        Returns:
            Deleted camera model if found, None otherwise
        """
        db_camera = self.get_camera(camera_id)
        if db_camera:
            self.db.delete(db_camera)
            self.db.commit()
        return db_camera

    def get_camera_by_ip(self, ip_address: str) -> Optional[models.Camera]:
        """
        Find a camera by IP address.
        
        Args:
            ip_address: IP address to search for
        
        Returns:
            Camera model if found, None otherwise
        """
        return self.db.query(models.Camera).filter(
            models.Camera.ip_address == ip_address
        ).first()

    def count_cameras(self) -> int:
        """
        Count total number of cameras.
        
        Returns:
            Total camera count
        """
        return self.db.query(models.Camera).count()

    def check_camera_blur(self, camera_id: int, threshold: float = 50.0) -> Optional[models.Camera]:
        """
        Run a blur check on a single camera and update its image/status fields.
        - Uses the same Laplacian-variance logic as BlurWorker.
        - If the camera was blurry and is now clear, remove the blurry status.
        """
        db_camera = self.get_camera(camera_id)
        if not db_camera:
            return None

        if not db_camera.rtsp_url:
            logger.warning(f"Camera {camera_id} has no RTSP URL; skipping blur check")
            return db_camera

        try:
            # Local import to avoid circular refs and heavy imports when unused
            from app.services.blur_worker import BlurWorker

            worker = BlurWorker(threshold=threshold)
            variance = worker.check_sharpness(db_camera.rtsp_url)

            new_image_status = "blur" if variance < threshold else "normal"
            status_changed = False

            # Update main status based on blur outcome
            if new_image_status == "blur" and db_camera.status != "blurry":
                db_camera.status = "blurry"
                status_changed = True
            elif new_image_status == "normal" and db_camera.status == "blurry":
                # Camera regained clarity; restore to online (or keep existing if not blurry-driven)
                db_camera.status = "online"
                status_changed = True

            if db_camera.image_status != new_image_status:
                db_camera.image_status = new_image_status
                status_changed = True

            db_camera.sharpness_value = float(variance)
            db_camera.last_image_check = datetime.now(THAILAND_TZ).strftime("%Y-%m-%d %H:%M:%S")

            if status_changed:
                db_camera.last_update = datetime.now(THAILAND_TZ).strftime("%Y-%m-%d %H:%M:%S")

            self.db.commit()
            self.db.refresh(db_camera)
        except Exception as e:
            logger.error(f"Error running blur check for camera {camera_id}: {e}")

        return db_camera

    def check_camera_status(self, camera_id: int) -> Optional[models.Camera]:
        """
        Check camera status by pinging its IP and checking services (80/554).
        """
        db_camera = self.get_camera(camera_id)
        if db_camera and db_camera.ip_address:
            from app.utils.network import check_port, ping_ip
            
            # 1. ICMP Ping
            is_pingable = ping_ip(db_camera.ip_address, timeout=1)
            
            # 2. Port Checks
            is_web_up = check_port(db_camera.ip_address, 80, timeout=1)
            is_rtsp_up = check_port(db_camera.ip_address, 554, timeout=1)
                
            # Logic similar to MCPService but synchronous
            if is_web_up and is_rtsp_up:
                new_status = "online"
            elif is_web_up or is_rtsp_up:
                new_status = "no_signal"
            elif is_pingable:
                new_status = "reachable"
            else:
                new_status = "offline"
            
            # Update if status changed
            if db_camera.status != new_status:
                logger.info(f"Camera {camera_id} ({db_camera.name}) status changed: {db_camera.status} -> {new_status}")
                db_camera.status = new_status
                db_camera.last_update = datetime.now(THAILAND_TZ).strftime("%Y-%m-%d %H:%M:%S")
                self.db.commit()
                self.db.refresh(db_camera)
            
        return db_camera

    # check_all_cameras_status removed in favor of PingWorker
