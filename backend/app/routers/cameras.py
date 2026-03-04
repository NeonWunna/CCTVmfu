"""
Camera Router
API endpoints for camera CRUD operations.
"""
from fastapi import APIRouter, Depends, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List
import cv2
import threading

from app import schemas
from app.db.session import get_db
from app.services import CameraService
from app.exceptions import CameraNotFoundException

router = APIRouter(prefix="/cameras")


@router.get("", response_model=List[schemas.Camera])
def list_cameras(
    skip: int = 0, 
    limit: int = 1000, 
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


@router.post("", response_model=schemas.Camera)
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


@router.api_route("/events", methods=["GET", "POST"])
def get_camera_events():
    """
    Placeholder for camera-related events (SSE or similar).
    Added to prevent route conflict with /{camera_id}.
    """
    return {"events": []}


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


@router.post("/check-status", response_model=schemas.MessageResponse)
def check_all_cameras_status(
    db: Session = Depends(get_db)
):
    """
    Check status of all cameras.
    This is now handled by the background worker.
    """
    # We could trigger the worker here if we wanted to force a check,
    # but for now we just confirm the background process is running.
    return schemas.MessageResponse(message="Background check is active. Status updates will appear shortly.")


@router.post("/{camera_id}/check", response_model=schemas.Camera)
def check_camera_status(
    camera_id: int, 
    db: Session = Depends(get_db)
):
    """
    Check status of a specific camera by pinging its IP.
    """
    service = CameraService(db)
    db_camera = service.check_camera_status(camera_id)
    if db_camera is None:
        raise CameraNotFoundException(camera_id)
    return db_camera


@router.post("/{camera_id}/check-blur", response_model=schemas.Camera)
def check_camera_blur(
    camera_id: int,
    db: Session = Depends(get_db)
):
    """
    Run a one-off blur detection for a specific camera and update image/status fields.
    """
    service = CameraService(db)
    db_camera = service.check_camera_blur(camera_id)
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


from fastapi.responses import RedirectResponse

@router.get("/{camera_id}/stream")
def stream_camera(
    camera_id: int,
    db: Session = Depends(get_db)
):
    """
    Redirect to go2rtc WebRTC stream.
    """
    service = CameraService(db)
    camera = service.get_camera(camera_id)
    
    if not camera or not camera.rtsp_url:
        return Response(status_code=404, content="Camera or RTSP URL not found")

    import urllib.parse
    encoded_url = urllib.parse.quote(camera.rtsp_url)
    # Redirect to Nginx reverse proxy routing to go2rtc
    return RedirectResponse(url=f"/stream/webrtc.html?src={encoded_url}")
