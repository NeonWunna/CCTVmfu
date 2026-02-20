
import asyncio
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from unittest.mock import MagicMock, AsyncMock
from app.services.mcp_service import MCPService
from app.models.camera import Camera

async def test_mcp_blur_status():
    print("Testing MCP Service Blur Status...")
    
    # Mock DB Session
    mock_db = MagicMock()
    
    # Mock Camera Object
    mock_camera = Camera(
        id=1,
        name="Test Camera",
        location="Building A",
        ip_address="192.168.1.100",
        status="online",
        image_status="blurry",
        sharpness_value=50.5,
        last_image_check="2023-10-27 10:00:00"
    )
    
    # Mock Query
    mock_query = MagicMock()
    mock_query.filter.return_value = mock_query
    mock_query.all.return_value = [mock_camera]
    mock_db.query.return_value = mock_query
    
    # Initialize Service
    service = MCPService(mock_db)
    
    # Mock check_port_async to avoid actual network calls
    # We need to mock app.utils.network.check_port_async
    # Since it's imported in mcp_service.py, we should patch it where it is used.
    # But since we are importing MCPService class, we can just patch check_port_async inside the service module if we could,
    # or just trust the logic since we aren't testing network here.
    # Actually, let's just use unittest.mock.patch
    
    from unittest.mock import patch
    
    with patch('app.services.mcp_service.check_port_async', new_callable=AsyncMock) as mock_check:
        mock_check.return_value = True # Simulate Online
        
        # Test check_camera_status
        print("1. Testing check_camera_status...")
        results = await service.check_camera_status("Test")
        
        if not results:
            print("FAILED: No results returned")
            return
            
        cam = results[0]
        print(f"Result: {cam}")
        
        if "image_status" not in cam or cam["image_status"] != "blurry":
            print(f"FAILED: image_status missing or incorrect with {cam.get('image_status')}")
        elif "sharpness_value" not in cam or cam["sharpness_value"] != 50.5:
             print("FAILED: sharpness_value missing or incorrect")
        else:
            print("PASSED: check_camera_status includes blur fields")
            
        # Test find_cameras_by_location
        print("\n2. Testing find_cameras_by_location...")
        results_loc = service.find_cameras_by_location("Building")
        cam_loc = results_loc[0]
        print(f"Result: {cam_loc}")
        
        if "image_status" not in cam_loc or cam_loc["image_status"] != "blurry":
             print("FAILED: image_status missing or incorrect in find_cameras_by_location")
        else:
             print("PASSED: find_cameras_by_location includes blur fields")

if __name__ == "__main__":
    asyncio.run(test_mcp_blur_status())
