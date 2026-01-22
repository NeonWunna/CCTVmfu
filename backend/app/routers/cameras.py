"""
Camera Router
API endpoints for camera CRUD operations.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app import schemas
from app.db.session import get_db
from app.services import CameraService
from app.exceptions import CameraNotFoundException

router = APIRouter(prefix="/cameras")


@router.get("/", response_model=List[schemas.Camera])
def list_cameras(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    """
    Retrieve all cameras with pagination.
    
    Args:
        skip: Number of records to skip (offset)
        limit: Maximum number of records to return
        db: Database session (injected)
    
    Returns:
        List of camera objects
    """
    service = CameraService(db)
    return service.get_cameras(skip=skip, limit=limit)


@router.post("/", response_model=schemas.Camera)
def create_camera(
    camera: schemas.CameraCreate, 
    db: Session = Depends(get_db)
):
    """
    Create a new camera.
    
    Args:
        camera: Camera data for creation
        db: Database session (injected)
    
    Returns:
        Created camera object
    """
    service = CameraService(db)
    return service.create_camera(camera=camera)


@router.get("/{camera_id}", response_model=schemas.Camera)
def get_camera(
    camera_id: int, 
    db: Session = Depends(get_db)
):
    """
    Retrieve a specific camera by ID.
    
    Args:
        camera_id: ID of the camera to retrieve
        db: Database session (injected)
    
    Returns:
        Camera object
    
    Raises:
        CameraNotFoundException: If camera with given ID doesn't exist
    """
    service = CameraService(db)
    db_camera = service.get_camera(camera_id=camera_id)
    if db_camera is None:
        raise CameraNotFoundException(camera_id)
    return db_camera


@router.put("/{camera_id}", response_model=schemas.Camera)
def update_camera(
    camera_id: int, 
    camera: schemas.CameraUpdate, 
    db: Session = Depends(get_db)
):
    """
    Update an existing camera.
    
    Args:
        camera_id: ID of the camera to update
        camera: Updated camera data
        db: Database session (injected)
    
    Returns:
        Updated camera object
    
    Raises:
        CameraNotFoundException: If camera with given ID doesn't exist
    """
    service = CameraService(db)
    db_camera = service.update_camera(camera_id=camera_id, camera=camera)
    if db_camera is None:
        raise CameraNotFoundException(camera_id)
    return db_camera


@router.delete("/{camera_id}", response_model=schemas.MessageResponse)
def delete_camera(
    camera_id: int, 
    db: Session = Depends(get_db)
):
    """
    Delete a camera.
    
    Args:
        camera_id: ID of the camera to delete
        db: Database session (injected)
    
    Returns:
        Confirmation message
    
    Raises:
        CameraNotFoundException: If camera with given ID doesn't exist
    """
    service = CameraService(db)
    db_camera = service.delete_camera(camera_id=camera_id)
    if db_camera is None:
        raise CameraNotFoundException(camera_id)
    return schemas.MessageResponse(message="Camera deleted successfully")
