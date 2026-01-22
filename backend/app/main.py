from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db.base import Base
from app.db.session import engine
from app.routers import cameras, health

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="CCTV MFU API",
    description="Backend API for CCTV Management System - Mae Fah Luang University",
    version="1.0.0",
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
