from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import asyncio
import logging
from contextlib import asynccontextmanager

from app.db.base import Base
from app.db.session import engine, SessionLocal
from app.routers import cameras, health
from app.services import CameraService
from app.services.ping_worker import PingWorker
from app.services.blur_worker import BlurWorker

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create database tables
Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Start background ping worker
    ping_worker = PingWorker(concurrent_limit=200)
    ping_worker_task = asyncio.create_task(ping_worker.start_loop())

    # Startup: Start background blur worker
    # Check every 5 mins (300s)
    blur_worker = BlurWorker(concurrent_limit=50, loop_interval=300)
    blur_worker_task = asyncio.create_task(blur_worker.start_loop())
    
    # Store worker references in app state
    app.state.ping_worker = ping_worker
    app.state.blur_worker = blur_worker
    
    yield
    
    # Shutdown: Stop workers
    ping_worker.stop()
    ping_worker_task.cancel()
    
    blur_worker.stop()
    blur_worker_task.cancel()
    
    try:
        await ping_worker_task
        await blur_worker_task
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
