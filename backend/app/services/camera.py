"""
Camera Service
Business logic for camera operations.
"""
from typing import List, Optional
from datetime import datetime
from zoneinfo import ZoneInfo
from sqlalchemy.orm import Session

from app import models, schemas
from app.utils.network import ping_ip
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
                current_coords = db_camera.coordinates.split(',') if db_camera.coordinates else ["0", "0"]
                current_lat = float(current_coords[0].strip()) if len(current_coords) > 0 else 0.0
                current_long = float(current_coords[1].strip()) if len(current_coords) > 1 else 0.0
                
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

    def check_camera_status(self, camera_id: int) -> Optional[models.Camera]:
        """
        Check camera status by pinging its IP and update DB.
        
        Args:
            camera_id: ID of the camera to check
            
        Returns:
            Updated camera model
        """
        db_camera = self.get_camera(camera_id)
        if db_camera and db_camera.ip_address:
            # Ping the camera
            is_reachable = ping_ip(db_camera.ip_address)
            new_status = "up" if is_reachable else "down"
            
            # Update if status changed
            # We also update active timestamp if it's reachable or status changes
            if db_camera.status != new_status:
                logger.info(f"Camera {camera_id} ({db_camera.name}) status changed: {db_camera.status} -> {new_status}")
                db_camera.status = new_status
                db_camera.last_update = datetime.now(THAILAND_TZ).strftime("%Y-%m-%d %H:%M:%S")
                self.db.commit()
                self.db.refresh(db_camera)
            
        return db_camera

    def check_all_cameras_status(self) -> None:
        """
        Check status of all cameras.
        This could be slow if there are many cameras.
        """
        cameras = self.get_cameras(limit=10000) # Get all
        for camera in cameras:
            self.check_camera_status(camera.id)
