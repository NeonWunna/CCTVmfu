"""
Camera Service
Business logic for camera operations.
"""
from typing import List, Optional
from sqlalchemy.orm import Session

from app import models, schemas


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
        
        Args:
            camera: Camera creation schema
        
        Returns:
            Created camera model
        """
        db_camera = models.Camera(**camera.model_dump())
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
        
        Args:
            camera_id: ID of the camera to update
            camera: Camera update schema with new data
        
        Returns:
            Updated camera model if found, None otherwise
        """
        db_camera = self.get_camera(camera_id)
        if db_camera:
            update_data = camera.model_dump(exclude_unset=True)
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
