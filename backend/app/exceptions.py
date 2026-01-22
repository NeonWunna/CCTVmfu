"""
Custom Exceptions
Centralized exception handling for the application.
"""
from fastapi import HTTPException, status


class CameraNotFoundException(HTTPException):
    """Exception raised when a camera is not found."""
    
    def __init__(self, camera_id: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Camera with id {camera_id} not found"
        )


class CameraAlreadyExistsException(HTTPException):
    """Exception raised when trying to create a camera that already exists."""
    
    def __init__(self, ip_address: str):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Camera with IP address {ip_address} already exists"
        )


class DatabaseConnectionException(HTTPException):
    """Exception raised when database connection fails."""
    
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection failed"
        )


class ValidationException(HTTPException):
    """Exception raised for validation errors."""
    
    def __init__(self, message: str):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=message
        )
