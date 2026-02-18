
import pytest
import asyncio
from unittest.mock import MagicMock, patch, AsyncMock
from app.services.ping_worker import PingWorker
from app import models

# Mocking the network call
@pytest.mark.asyncio
async def test_check_port_async():
    from app.utils.network import check_port_async
    
    # Test True
    with patch('asyncio.open_connection', new_callable=AsyncMock) as mock_conn:
        mock_conn.return_value = (AsyncMock(), AsyncMock())
        result = await check_port_async('127.0.0.1', 80)
        assert result is True

    # Test False (Exception)
    with patch('asyncio.open_connection', side_effect=OSError("Unreachable")):
        result = await check_port_async('127.0.0.1', 80)
        assert result is False

@pytest.mark.asyncio
async def test_ping_worker_run_once():
    # Helper to create dummy cameras
    cameras = [
        models.Camera(id=1, name="Cam1", ip_address="192.168.1.1", status="down"),
        models.Camera(id=2, name="Cam2", ip_address="192.168.1.2", status="up"),
    ]
    
    # Mock Session
    mock_db = MagicMock()
    mock_db.query.return_value.all.return_value = cameras
    
    # Mock SessionLocal to return our mock_db
    with patch('app.services.ping_worker.SessionLocal', return_value=mock_db):
        # Mock check_port_async to return True for Cam1, False for Cam2
        # This should flip their statuses
        with patch('app.services.ping_worker.check_port_async', side_effect=[True, False]):
            worker = PingWorker()
            
            # Run one sweep
            await worker.run_once()
            
            # Verify status updates
            assert cameras[0].status == "up"  # Was down, now up
            assert cameras[1].status == "down" # Was up, now down
            
            # Verify commit was called
            assert mock_db.commit.called

if __name__ == "__main__":
    # fast way to run without installing pytest if needed, 
    # but we should use pytest
    print("Please run with: pytest tests/test_ping_worker.py")
