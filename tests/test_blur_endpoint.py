
import asyncio
from unittest.mock import MagicMock
from fastapi import Request, BackgroundTasks
from app.routers.cameras import check_blur_status

def test_blur_endpoint_logic():
    print("Testing check_blur_status logic...")

    # Mock Request and App State
    mock_request = MagicMock(spec=Request)
    mock_worker = MagicMock()
    
    # Setup app.state.blur_worker
    mock_request.app.state.blur_worker = mock_worker
    
    # Mock BackgroundTasks
    mock_background_tasks = MagicMock(spec=BackgroundTasks)
    
    # Call the endpoint function directly
    response = check_blur_status(mock_request, mock_background_tasks)
    
    # Verification
    print(f"Response: {response}")
    
    # Check if run_once was added to background tasks
    # BackgroundTasks.add_task(func, *args, **kwargs)
    mock_background_tasks.add_task.assert_called_once_with(mock_worker.run_once)
    
    if mock_background_tasks.add_task.called:
        print("SUCCESS: Worker.run_once was added to background tasks.")
    else:
        print("FAILED: Worker was not triggered.")

if __name__ == "__main__":
    test_blur_endpoint_logic()
