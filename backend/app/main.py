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

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Start unified Status Worker
    # Replaces separate Ping and Blur workers
    from app.services.status_worker import StatusWorker
    
    # Check every minute (60s)
    status_worker = StatusWorker(concurrent_limit=20, loop_interval=60)
    status_worker_task = asyncio.create_task(status_worker.start_loop())
    
    # Store worker references in app state
    app.state.status_worker = status_worker
    
    yield
    
    # Shutdown: Stop workers
    status_worker.stop()
    status_worker_task.cancel()
    
    try:
        await status_worker_task
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
