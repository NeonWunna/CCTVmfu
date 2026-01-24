// Mock API that simulates backend responses
const delay = (ms) => new Promise(resolve => setTimeout(resolve, ms));

let mockCameras = [
  { 
    id: 1,
    name: "Main Gate CCTV", 
    status: "up",
    location: "Main Entrance",
    ipAddress: "192.168.1.10",
    coordinates: "20.0451° N, 99.8825° E",
    lat: 20.0450,
    lng: 99.8925,
    brand: "Hikvision",
    version: "V5.7.3",
    lastUpdate: "2 min ago"
  },
  { 
    id: 2,
    name: "Library CCTV", 
    status: "up",
    location: "Central Library",
    ipAddress: "192.168.1.11",
    coordinates: "20.0456° N, 99.8831° E",
    lat: 20.0442,
    lng: 99.8945,
    brand: "Dahua",
    version: "V2.840.0000000.28.R",
    lastUpdate: "1 min ago"
  },
  { 
    id: 3,
    name: "Dormitory CCTV", 
    status: "down",
    location: "Student Housing",
    ipAddress: "192.168.1.12",
    coordinates: "20.0448° N, 99.8819° E",
    lat: 20.0435,
    lng: 99.8952,
    brand: "Axis",
    version: "10.12.85",
    lastUpdate: "15 min ago"
  },
];

export const mockCameraAPI = {
  async getAll() {
    console.log('🎭 Mock API: Getting all cameras');
    await delay(500);
    return {
      data: {
        cameras: [...mockCameras]
      }
    };
  },

  async create(data) {
    console.log('🎭 Mock API: Creating camera', data);
    await delay(800);
    const newCamera = {
      id: mockCameras.length + 1,
      ...data,
      lastUpdate: "Just now"
    };
    mockCameras.push(newCamera);
    return { data: newCamera };
  },

  async update(id, data) {
    console.log('🎭 Mock API: Updating camera', id, data);
    await delay(800);
    const index = mockCameras.findIndex(c => c.id === id);
    if (index !== -1) {
      mockCameras[index] = { ...mockCameras[index], ...data, lastUpdate: "Just now" };
      return { data: mockCameras[index] };
    }
    throw new Error('Camera not found');
  },

  async delete(id) {
    console.log('🎭 Mock API: Deleting camera', id);
    await delay(600);
    const index = mockCameras.findIndex(c => c.id === id);
    if (index !== -1) {
      mockCameras.splice(index, 1);
    }
    return { data: { message: 'Deleted' } };
  }
};

export const mockAuthAPI = {
  async loginWithGoogle(token) {
    console.log('🎭 Mock API: Google login', token);
    await delay(1000);
    return {
      data: {
        token: 'mock-jwt-token-google-' + Date.now(),
        user: {
          name: 'Admin User',
          email: 'admin@mfu.ac.th',
          role: 'Security Administrator'
        }
      }
    };
  },

  async loginWithSSO(token) {
    console.log('🎭 Mock API: SSO login', token);
    await delay(1000);
    return {
      data: {
        token: 'mock-jwt-token-sso-' + Date.now(),
        user: {
          name: 'Admin User',
          email: 'admin@mfu.ac.th',
          role: 'Security Administrator'
        }
      }
    };
  }
};