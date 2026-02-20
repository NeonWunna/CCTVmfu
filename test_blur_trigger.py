
import requests
import time

def test_blur_trigger():
    print("Testing Blur Check Trigger...")
    try:
        # Assuming backend is running on default port 8000
        # We need to use valid camera info if we want to confirm it works
        # But here we just test if the endpoint accepts the request
        response = requests.post("http://localhost:8000/api/cameras/check-blur")
        
        if response.status_code == 200:
            print("SUCCESS: Endpoint returned 200")
            print(f"Response: {response.json()}")
        else:
            print(f"FAILED: Endpoint returned {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"ERROR: Could not connect to API. Is the server running? {e}")

if __name__ == "__main__":
    test_blur_trigger()
