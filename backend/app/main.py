from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import asyncio
import logging
from contextlib import asynccontextmanager

from app.db.base import Base
from app.db.session import engine, SessionLocal
from app.routers import cameras, health
from app.services import CameraService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create database tables
Base.metadata.create_all(bind=engine)

def background_check_cameras():
    """Sync function to run in thread pool"""
    db = SessionLocal()
    try:
        service = CameraService(db)
        service.check_all_cameras_status()
        logger.info("Background camera status check completed")
    except Exception as e:
        logger.error(f"Background check error: {e}")
    finally:
        db.close()

async def periodic_status_check():
    """Periodically run status check"""
    while True:
        try:
            await asyncio.to_thread(background_check_cameras)
        except Exception as e:
            logger.error(f"Error in periodic check loop: {e}")
        # Wait for 60 seconds before next check
        await asyncio.sleep(60)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Start background task
    task = asyncio.create_task(periodic_status_check())
    yield
    # Shutdown: Cancel task (optional cleanup)
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass

app = FastAPI(
    title="CCTV MFU API",
    description="Backend API for CCTV Management System - Mae Fah Luang University",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Middleware Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Configure specific origins for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(cameras.router, prefix="/api", tags=["cameras"])
