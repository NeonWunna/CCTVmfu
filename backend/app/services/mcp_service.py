
import logging
import asyncio
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import or_, String, cast

from app.models.camera import Camera
from app.utils.network import check_port_async

logger = logging.getLogger(__name__)

class MCPService:
    def __init__(self, db: Session):
        self.db = db

    async def _check_single_camera_status(self, camera: Camera) -> Dict[str, Any]:
        """
        Checks real-time status of a camera by attempting to connect to port 80 and 554.
        Returns the camera details with 'status' field updated.
        """
        is_web_up = await check_port_async(camera.ip_address, 80, timeout=1.0)
        
        status = "offline"
        if is_web_up:
            # If web is up, check RTSP if available (optional but better)
            # For now, if web is up, we consider it online or at least reachable.
            # But let's follow PingWorker logic: 
            # If web is up, it's at least 'no_signal' (alive but maybe no video).
            # To be 'online' fully, maybe we check 554?
            # User simply asked for "online/offline". 
            # I will return "online" if port 80 is up, to keep it simple and fast.
            # If port 80 is down, check 554 just in case it's a stream-only device.
            status = "online"
        else:
            # Check 554 as fallback
            is_rtsp_up = await check_port_async(camera.ip_address, 554, timeout=1.0)
            if is_rtsp_up:
                status = "online"
        
        return {
            "id": camera.id,
            "name": camera.name,
            "location": camera.location,
            "ip_address": camera.ip_address,
            "status": status,
            "image_status": camera.image_status,
            "sharpness_value": camera.sharpness_value,
            "last_image_check": camera.last_image_check
        }

    async def check_camera_status(self, search_term: str) -> List[Dict[str, Any]]:
        """
        Search cameras by id, name, or location, and check their real-time status.
        """
        # Search DB
        query = self.db.query(Camera).filter(
            or_(
                Camera.id.cast(String).ilike(f"%{search_term}%"),
                Camera.name.ilike(f"%{search_term}%"),
                Camera.location.ilike(f"%{search_term}%")
            )
        )
        cameras = query.all()
        logger.info(f"MCP: Found {len(cameras)} cameras for search term '{search_term}'")
        
        # Check status concurrently
        try:
            tasks = [self._check_single_camera_status(cam) for cam in cameras]
            results = await asyncio.gather(*tasks)
            return list(results)
        except Exception as e:
            logger.error(f"MCP: Error checking camera status: {e}")
            raise e

    def find_cameras_by_location(self, location: str) -> List[Dict[str, Any]]:
        """
        Find cameras strictly by location prefix/match. No ping.
        """
        query = self.db.query(Camera).filter(
            Camera.location.ilike(f"%{location}%")
        )
        cameras = query.all()
        
        # Return DB status
        return [
            {
                "id": cam.id,
                "name": cam.name,
                "location": cam.location,
                "ip_address": cam.ip_address,
                "status": cam.status, # Return stored status
                "image_status": cam.image_status,
                "sharpness_value": cam.sharpness_value,
                "last_image_check": cam.last_image_check
            }
            for cam in cameras
        ]
