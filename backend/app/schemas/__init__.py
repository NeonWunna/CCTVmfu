"""Schemas package - Pydantic models for request/response validation."""
from .camera import Camera, CameraCreate, CameraUpdate, CameraBase
from .common import PaginationParams, PaginatedResponse, MessageResponse, StatusResponse

__all__ = [
    "Camera",
    "CameraCreate", 
    "CameraUpdate",
    "CameraBase",
    "PaginationParams",
    "PaginatedResponse",
    "MessageResponse",
    "StatusResponse",
]
