"""
Common Schemas
Shared Pydantic models for common data structures.
"""
from typing import Generic, List, Optional, TypeVar
from pydantic import BaseModel

T = TypeVar("T")


class PaginationParams(BaseModel):
    """Pagination parameters for list endpoints."""
    skip: int = 0
    limit: int = 100


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response wrapper."""
    items: List[T]
    total: int
    skip: int
    limit: int
    
    class Config:
        from_attributes = True


class MessageResponse(BaseModel):
    """Standard message response."""
    message: str
    detail: Optional[str] = None


class StatusResponse(BaseModel):
    """System status response."""
    status: str
    version: str
    cameras: int
