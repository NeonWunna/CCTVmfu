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
    # Prefer FFmpeg backend for RTSP handling when available.
    cap = cv2.VideoCapture(rtsp_url, cv2.CAP_FFMPEG)

    # Fallback to default backend if FFmpeg backend is unavailable on this build.
    if not cap.isOpened():
        cap.release()
        cap = cv2.VideoCapture(rtsp_url)

    # Reduce decoder queue to keep frames as fresh as possible.
    # Not all backends honor this; it's safe to attempt.
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    
    # Try to open the stream
    if not cap.isOpened():
        # Fallback to a placeholder or error frame? 
        # For now, just stop.
        return

    try:
        while True:
            # Grab first available frame packet.
            if not cap.grab():
                break

            # Drop a few queued packets so we retrieve a newer frame.
            # This trades frame continuity for lower latency.
            for _ in range(2):
                if not cap.grab():
                    break

            success, frame = cap.retrieve()
            if not success or frame is None:
                continue
            
            # Encode frame as JPEG
            ret, buffer = cv2.imencode('.jpg', frame)
            if not ret:
                continue
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
