"""
Health Check Router
Provides endpoints for system health monitoring and status checks.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import Camera

router = APIRouter()





@router.get("/health")
def health_check():
    """Health check endpoint for container orchestration."""
    return {"status": "healthy"}


@router.get("/status")
def get_status(db: Session = Depends(get_db)):
    """Get system status including camera count."""
    camera_count = db.query(Camera).count()
    return {
        "status": "running",
        "cameras": camera_count,
        "version": "1.0.0"
    }
