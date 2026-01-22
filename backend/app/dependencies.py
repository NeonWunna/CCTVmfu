"""
Shared Dependencies
FastAPI dependency injection for reusable components.
"""
from typing import Generator
from sqlalchemy.orm import Session

from app.db.session import SessionLocal


def get_db() -> Generator[Session, None, None]:
    """
    Database session dependency.
    Provides a database session for each request and ensures proper cleanup.
    
    Yields:
        Session: SQLAlchemy database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Future dependencies can be added here:
# - get_current_user
# - get_current_active_user
# - verify_api_key
# - rate_limiter
