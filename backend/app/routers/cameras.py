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
    Check status of all cameras by pinging their IPs.
    """
    service = CameraService(db)
    service.check_all_cameras_status()
    return schemas.MessageResponse(message="All cameras status check initiated")


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


def generate_frames(rtsp_url: str):
    """
    Generator function to read frames from RTSP stream and yield them as MJPEG.
    WARNING: This simple implementation is blocking and may consume significant resources.
    For production, consider using a dedicated streaming server or async-compatible library.
    """
    cap = cv2.VideoCapture(rtsp_url)
    
    # Try to open the stream
    if not cap.isOpened():
        # Fallback to a placeholder or error frame? 
        # For now, just stop.
        return

    try:
        while True:
            success, frame = cap.read()
            if not success:
                break
            
            # Encode frame as JPEG
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            
            # Yield frame in MJPEG format
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    finally:
        cap.release()


@router.get("/{camera_id}/stream")
def stream_camera(
    camera_id: int,
    db: Session = Depends(get_db)
):
    """
    Stream camera video as MJPEG.
    """
    service = CameraService(db)
    camera = service.get_camera(camera_id)
    
    if not camera or not camera.rtsp_url:
        return Response(status_code=404, content="Camera or RTSP URL not found")

    return StreamingResponse(
        generate_frames(camera.rtsp_url), 
        media_type="multipart/x-mixed-replace; boundary=frame"
    )
