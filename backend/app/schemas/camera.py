"""
Camera Schemas
Pydantic models for camera data validation.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator


class CameraBase(BaseModel):
    """Base camera schema with common fields."""
    
    name: str = Field(..., min_length=1, max_length=255, description="Camera name")
    location: str = Field(..., min_length=1, max_length=255, description="Camera location")
    ip_address: str = Field(..., max_length=45, description="Camera IP address")
    coordinates: Optional[str] = Field(None, max_length=100, description="GPS coordinates")
    brand: Optional[str] = Field(None, max_length=100, description="Camera brand/manufacturer")
    status: Optional[str] = Field("up", max_length=20, description="Camera status (up/down)")
    version: Optional[str] = Field(None, max_length=50, description="Firmware version")
    rtsp_url: Optional[str] = Field(None, max_length=500, description="RTSP Stream URL")
    last_update: Optional[str] = Field(None, description="Last update timestamp")

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        """Validate status is one of allowed values."""
        allowed = ["up", "down", "maintenance", "unknown"]
        if v and v.lower() not in allowed:
            raise ValueError(f"Status must be one of: {', '.join(allowed)}")
        return v.lower() if v else "up"


class CameraCreate(BaseModel):
    """Schema for creating a new camera."""
    name: str = Field(..., min_length=1, max_length=255, description="Camera name")
    location: str = Field(..., min_length=1, max_length=255, description="Camera location")
    ip_address: str = Field(..., max_length=45, description="Camera IP address")
    latitude: float = Field(..., description="GPS Latitude")
    longitude: float = Field(..., description="GPS Longitude")
    brand: Optional[str] = Field(None, max_length=100)
    status: Optional[str] = Field("up", max_length=20)
    version: Optional[str] = Field(None, max_length=50)
    rtsp_url: Optional[str] = Field(None, max_length=500)

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        """Validate status is one of allowed values."""
        allowed = ["up", "down", "maintenance", "unknown"]
        if v and v.lower() not in allowed:
            raise ValueError(f"Status must be one of: {', '.join(allowed)}")
        return v.lower() if v else "up"


class CameraUpdate(BaseModel):
    """Schema for updating a camera."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    location: Optional[str] = Field(None, min_length=1, max_length=255)
    ip_address: Optional[str] = Field(None, max_length=45)
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    brand: Optional[str] = Field(None, max_length=100)
    status: Optional[str] = Field(None, max_length=20)
    version: Optional[str] = Field(None, max_length=50)
    rtsp_url: Optional[str] = Field(None, max_length=500)
    last_update: Optional[str] = None

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        allowed = ["up", "down", "maintenance", "unknown"]
        if v.lower() not in allowed:
            raise ValueError(f"Status must be one of: {', '.join(allowed)}")
        return v.lower()


class Camera(CameraBase):
    """Schema for camera response (includes ID and timestamps)."""
    
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        """Pydantic configuration."""
        from_attributes = True
