"""
Camera Model
SQLAlchemy model for camera entity.
"""
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func

from app.db.base import Base


class Camera(Base):
    """Camera database model."""
    
    __tablename__ = "cameras"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), index=True, nullable=False)
    location = Column(String(255), nullable=False)
    ip_address = Column(String(45), unique=True, nullable=False)  # IPv6 max length
    coordinates = Column(String(100), nullable=True)
    brand = Column(String(100), nullable=True)
    status = Column(String(20), default="up", nullable=False)
    version = Column(String(50), nullable=True)
    last_update = Column(String(50), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self) -> str:
        """String representation of camera."""
        return f"<Camera(id={self.id}, name='{self.name}', ip='{self.ip_address}')>"
