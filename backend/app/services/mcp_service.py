
import logging
import asyncio
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import or_, String, cast

from app.models.camera import Camera
from app.utils.network import check_port_async, async_ping_ip

logger = logging.getLogger(__name__)

class MCPService:
    def __init__(self, db: Session):
        self.db = db

    async def _check_single_camera_status(self, camera: Camera) -> Dict[str, Any]:
        """
        Checks real-time status of a camera using ICMP Ping and Port Checks (80/554).
        """
        # 1. Try ICMP Ping (fastest)
        is_pingable = await async_ping_ip(camera.ip_address, timeout=1)
        
        # 2. Check Ports
        is_web_up = await check_port_async(camera.ip_address, 80, timeout=1.0)
        is_rtsp_up = await check_port_async(camera.ip_address, 554, timeout=1.0)

        # Logic for status
        if is_web_up and is_rtsp_up:
            status = "online"
        elif is_web_up or is_rtsp_up:
            status = "no_signal" # Alive but potentially misconfigured or only partially accessible
        elif is_pingable:
            status = "reachable" # Responds to ping but services are down
        else:
            status = "offline"

        return {
            "id": camera.id,
            "name": camera.name,
            "location": camera.location,
            "ip_address": camera.ip_address,
            "status": status,
            "details": {
                "ping": is_pingable,
                "web_port_80": is_web_up,
                "rtsp_port_554": is_rtsp_up
            }
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
        
        # Check status concurrently
        tasks = [self._check_single_camera_status(cam) for cam in cameras]
        results = await asyncio.gather(*tasks)
        
        return list(results)

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
                "status": cam.status # Return stored status
            }
            for cam in cameras
        ]
