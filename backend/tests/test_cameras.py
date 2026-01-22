"""
Camera API Tests
Test cases for camera CRUD endpoints.
"""
import pytest


class TestHealthEndpoints:
    """Test health check endpoints."""
    
    def test_root_endpoint(self, client):
        """Test root endpoint returns welcome message."""
        response = client.get("/api/")
        assert response.status_code == 200
        assert "message" in response.json()
    
    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/api/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
    
    def test_status_endpoint(self, client):
        """Test status endpoint."""
        response = client.get("/api/status")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "cameras" in data


class TestCameraEndpoints:
    """Test camera CRUD endpoints."""
    
    def test_list_cameras_empty(self, client):
        """Test listing cameras when database is empty."""
        response = client.get("/api/cameras/")
        assert response.status_code == 200
        assert response.json() == []
    
    def test_create_camera(self, client):
        """Test creating a new camera."""
        camera_data = {
            "name": "Test Camera",
            "location": "Building A",
            "ip_address": "192.168.1.100",
            "coordinates": "18.123,98.456",
            "brand": "Hikvision",
            "status": "up",
            "version": "1.0.0"
        }
        response = client.post("/api/cameras/", json=camera_data)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == camera_data["name"]
        assert data["ip_address"] == camera_data["ip_address"]
        assert "id" in data
    
    def test_get_camera(self, client):
        """Test getting a specific camera."""
        # First create a camera
        camera_data = {
            "name": "Test Camera",
            "location": "Building A",
            "ip_address": "192.168.1.100"
        }
        create_response = client.post("/api/cameras/", json=camera_data)
        camera_id = create_response.json()["id"]
        
        # Then get it
        response = client.get(f"/api/cameras/{camera_id}")
        assert response.status_code == 200
        assert response.json()["id"] == camera_id
    
    def test_get_camera_not_found(self, client):
        """Test getting a non-existent camera."""
        response = client.get("/api/cameras/9999")
        assert response.status_code == 404
    
    def test_update_camera(self, client):
        """Test updating a camera."""
        # Create a camera
        camera_data = {
            "name": "Test Camera",
            "location": "Building A",
            "ip_address": "192.168.1.100"
        }
        create_response = client.post("/api/cameras/", json=camera_data)
        camera_id = create_response.json()["id"]
        
        # Update it
        update_data = {
            "name": "Updated Camera",
            "location": "Building B",
            "ip_address": "192.168.1.101"
        }
        response = client.put(f"/api/cameras/{camera_id}", json=update_data)
        assert response.status_code == 200
        assert response.json()["name"] == "Updated Camera"
    
    def test_delete_camera(self, client):
        """Test deleting a camera."""
        # Create a camera
        camera_data = {
            "name": "Test Camera",
            "location": "Building A",
            "ip_address": "192.168.1.100"
        }
        create_response = client.post("/api/cameras/", json=camera_data)
        camera_id = create_response.json()["id"]
        
        # Delete it
        response = client.delete(f"/api/cameras/{camera_id}")
        assert response.status_code == 200
        
        # Verify it's gone
        get_response = client.get(f"/api/cameras/{camera_id}")
        assert get_response.status_code == 404
