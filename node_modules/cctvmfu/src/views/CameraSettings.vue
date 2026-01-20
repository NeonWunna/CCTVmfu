<script setup>
import { ref, computed } from 'vue';
import { useRouter } from 'vue-router';
import logoUrl from '../assets/mfu-logo.png';

const router = useRouter();

const userName = ref("Admin User");
const userRole = ref("Security Administrator");
const showDropdown = ref(false);
const searchQuery = ref("");

const cameras = ref([
  { 
    id: 1,
    name: "Main Gate CCTV", 
    status: "up",
    location: "Main Entrance",
    ipAddress: "192.168.1.10",
    lastUpdate: "2 min ago"
  },
  { 
    id: 2,
    name: "Library CCTV", 
    status: "up",
    location: "Central Library",
    ipAddress: "192.168.1.11",
    lastUpdate: "1 min ago"
  },
  { 
    id: 3,
    name: "Dormitory CCTV", 
    status: "down",
    location: "Student Housing",
    ipAddress: "192.168.1.12",
    lastUpdate: "15 min ago"
  },
  { 
    id: 4,
    name: "Parking Lot CCTV", 
    status: "up",
    location: "Parking Area A",
    ipAddress: "192.168.1.13",
    lastUpdate: "Just now"
  },
  { 
    id: 5,
    name: "Sports Complex CCTV", 
    status: "up",
    location: "Athletic Center",
    ipAddress: "192.168.1.14",
    lastUpdate: "3 min ago"
  },
  { 
    id: 6,
    name: "Cafeteria CCTV", 
    status: "up",
    location: "Student Cafeteria",
    ipAddress: "192.168.1.15",
    lastUpdate: "1 min ago"
  },
  { 
    id: 7,
    name: "Admin Building CCTV", 
    status: "up",
    location: "Administration Office",
    ipAddress: "192.168.1.16",
    lastUpdate: "4 min ago"
  },
  { 
    id: 8,
    name: "Science Building CCTV", 
    status: "up",
    location: "Science Faculty",
    ipAddress: "192.168.1.17",
    lastUpdate: "2 min ago"
  },
  { 
    id: 9,
    name: "Engineering Hall CCTV", 
    status: "down",
    location: "Engineering Building",
    ipAddress: "192.168.1.18",
    lastUpdate: "20 min ago"
  },
  { 
    id: 10,
    name: "East Gate CCTV", 
    status: "up",
    location: "East Entrance",
    ipAddress: "192.168.1.19",
    lastUpdate: "Just now"
  },
  { 
    id: 11,
    name: "West Gate CCTV", 
    status: "up",
    location: "West Entrance",
    ipAddress: "192.168.1.20",
    lastUpdate: "3 min ago"
  },
  { 
    id: 12,
    name: "Parking Area B CCTV", 
    status: "up",
    location: "Parking Lot B",
    ipAddress: "192.168.1.21",
    lastUpdate: "5 min ago"
  },
  { 
    id: 13,
    name: "Student Center CCTV", 
    status: "up",
    location: "Student Activities Center",
    ipAddress: "192.168.1.22",
    lastUpdate: "2 min ago"
  },
  { 
    id: 14,
    name: "Basketball Court CCTV", 
    status: "up",
    location: "Outdoor Courts",
    ipAddress: "192.168.1.23",
    lastUpdate: "6 min ago"
  },
  { 
    id: 15,
    name: "Medical Center CCTV", 
    status: "up",
    location: "Health Services",
    ipAddress: "192.168.1.24",
    lastUpdate: "1 min ago"
  }
]);

const userInitials = computed(() => {
  return userName.value
    .split(' ')
    .map(n => n[0])
    .join('')
    .toUpperCase()
    .slice(0, 2);
});

const onlineCount = computed(() => cameras.value.filter(c => c.status === "up").length);
const offlineCount = computed(() => cameras.value.filter(c => c.status === "down").length);
const totalCount = computed(() => cameras.value.length);

const filteredCameras = computed(() => {
  if (!searchQuery.value) return cameras.value;
  
  const query = searchQuery.value.toLowerCase();
  return cameras.value.filter(camera => 
    camera.name.toLowerCase().includes(query) ||
    camera.location.toLowerCase().includes(query) ||
    camera.ipAddress.toLowerCase().includes(query)
  );
});

const toggleProfileMenu = () => {
  showDropdown.value = !showDropdown.value;
};

const closeDropdown = () => {
  showDropdown.value = false;
};

const goToCameraSettings = () => {
  closeDropdown();
};

const goToDashboard = () => {
  router.push('/');
};

const logout = () => {
  if (confirm('Are you sure you want to logout?')) {
    localStorage.removeItem('isAuthenticated');
    closeDropdown();
    router.push('/login');
  }
};

const handleLogoError = (event) => {
  event.target.style.display = 'none';
};

const editCamera = (camera) => {
  alert(`Edit camera: ${camera.name}\nIP: ${camera.ipAddress}\nLocation: ${camera.location}`);
  // Implement edit functionality here
};

const removeCamera = (camera) => {
  if (confirm(`Are you sure you want to remove "${camera.name}"?`)) {
    cameras.value = cameras.value.filter(c => c.id !== camera.id);
  }
};

const addNewCamera = () => {
  alert('Add new camera functionality will be implemented here');
  // Implement add new camera functionality
};
</script>

<template>
  <div class="settings-container">
    <!-- Header -->
    <div class="header">
      <div class="logo-container">
        <img :src="logoUrl" alt="MFU Logo" class="logo" @error="handleLogoError">
        <div class="header-text">
          <h1>Camera Settings</h1>
          <p>Manage CCTV Cameras - Mae Fah Luang University</p>
        </div>
      </div>

      <!-- Profile Section -->
      <div class="profile-section" @click="toggleProfileMenu">
        <div class="profile-avatar">{{ userInitials }}</div>
        <div class="profile-info">
          <div class="profile-name">{{ userName }}</div>
          <div class="profile-role">{{ userRole }}</div>
        </div>
        <svg class="profile-dropdown-icon" :class="{ open: showDropdown }" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
        </svg>
      </div>

      <!-- Dropdown Menu -->
      <div class="profile-dropdown" :class="{ show: showDropdown }">
        <div class="dropdown-header">
          <div class="dropdown-avatar">{{ userInitials }}</div>
          <div class="dropdown-name">{{ userName }}</div>
          <div class="dropdown-role">{{ userRole }}</div>
        </div>
        <div class="dropdown-menu">
          <button class="dropdown-item" @click="goToCameraSettings">
            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"></path>
            </svg>
            Camera Settings
          </button>
          <div class="dropdown-divider"></div>
          <button class="dropdown-item logout" @click="logout">
            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"></path>
            </svg>
            Logout
          </button>
        </div>
      </div>

      <!-- Dropdown Overlay -->
      <div class="dropdown-overlay" :class="{ show: showDropdown }" @click="closeDropdown"></div>
    </div>

    <!-- Main Content -->
    <div class="main-content">
      <!-- Back Button and Stats -->
      <div class="top-bar">
        <button class="back-button" @click="goToDashboard">
          <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"></path>
          </svg>
          Back to Dashboard
        </button>

        <div class="stats-mini">
          <div class="stat-mini">
            <span class="stat-mini-value up">{{ onlineCount }}</span>
            <span class="stat-mini-label">Online</span>
          </div>
          <div class="stat-mini">
            <span class="stat-mini-value down">{{ offlineCount }}</span>
            <span class="stat-mini-label">Offline</span>
          </div>
          <div class="stat-mini">
            <span class="stat-mini-value">{{ totalCount }}</span>
            <span class="stat-mini-label">Total</span>
          </div>
        </div>
      </div>

      <!-- Search and Add Button -->
      <div class="controls-bar">
        <div class="search-box">
          <svg class="search-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
          </svg>
          <input 
            v-model="searchQuery"
            type="text" 
            placeholder="Search cameras by name, location, or IP address..."
            class="search-input"
          >
        </div>
        <button class="add-camera-btn" @click="addNewCamera">
          <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path>
          </svg>
          Add Camera
        </button>
      </div>

      <!-- Camera List -->
      <div class="camera-list">
        <div v-if="filteredCameras.length === 0" class="no-results">
          <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
          </svg>
          <p>No cameras found matching your search</p>
        </div>

        <div v-for="camera in filteredCameras" :key="camera.id" class="camera-card">
          <div class="camera-info">
            <div class="camera-icon">
              <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"></path>
              </svg>
            </div>
            <div class="camera-details">
              <div class="camera-name-row">
                <h3 class="camera-name">{{ camera.name }}</h3>
                <span class="status-badge" :class="camera.status">
                  <span class="status-dot" :class="camera.status"></span>
                  {{ camera.status === 'up' ? 'Online' : 'Offline' }}
                </span>
              </div>
              <div class="camera-meta">
                <span class="meta-item">
                  <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"></path>
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"></path>
                  </svg>
                  {{ camera.location }}
                </span>
                <span class="meta-item">
                  <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z"></path>
                  </svg>
                  {{ camera.ipAddress }}
                </span>
                <span class="meta-item">
                  <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                  </svg>
                  {{ camera.lastUpdate }}
                </span>
              </div>
            </div>
          </div>
          <div class="camera-actions">
            <button class="action-btn edit-btn" @click="editCamera(camera)">
              <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
              </svg>
              Edit
            </button>
            <button class="action-btn remove-btn" @click="removeCamera(camera)">
              <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
              </svg>
              Remove
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Container */
.settings-container {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background-color: #f8f9fa;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

/* Header Styles */
.header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 20px 30px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  gap: 20px;
  flex-shrink: 0;
  position: relative;
  z-index: 1001;
}

.logo-container {
  display: flex;
  align-items: center;
  gap: 15px;
}

.logo {
  height: 60px;
  width: auto;
}

.header-text {
  flex: 1;
}

.header-text h1 {
  font-size: 24px;
  font-weight: 700;
  margin-bottom: 4px;
  letter-spacing: -0.5px;
  color: white;
}

.header-text p {
  font-size: 14px;
  opacity: 0.9;
  font-weight: 400;
  color: white;
}

/* Profile Section */
.profile-section {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-left: auto;
  background: rgba(255, 255, 255, 0.15);
  padding: 8px 16px;
  border-radius: 50px;
  backdrop-filter: blur(10px);
  cursor: pointer;
  transition: all 0.3s ease;
}

.profile-section:hover {
  background: rgba(255, 255, 255, 0.25);
  transform: translateY(-1px);
}

.profile-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 16px;
  color: white;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.profile-info {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}

.profile-name {
  font-size: 14px;
  font-weight: 600;
  line-height: 1.2;
}

.profile-role {
  font-size: 12px;
  opacity: 0.85;
  line-height: 1.2;
}

.profile-dropdown-icon {
  width: 20px;
  height: 20px;
  opacity: 0.8;
  transition: transform 0.3s ease;
}

.profile-dropdown-icon.open {
  transform: rotate(180deg);
}

/* Profile Dropdown */
.profile-dropdown {
  position: absolute;
  top: 100%;
  right: 30px;
  margin-top: 10px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.15);
  min-width: 220px;
  overflow: hidden;
  z-index: 1002;
  opacity: 0;
  transform: translateY(-10px);
  pointer-events: none;
  transition: all 0.3s ease;
}

.profile-dropdown.show {
  opacity: 1;
  transform: translateY(0);
  pointer-events: all;
}

.dropdown-header {
  padding: 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  text-align: center;
}

.dropdown-avatar {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 24px;
  margin: 0 auto 10px;
  border: 3px solid rgba(255, 255, 255, 0.3);
}

.dropdown-name {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 4px;
}

.dropdown-role {
  font-size: 13px;
  opacity: 0.9;
}

.dropdown-menu {
  padding: 8px 0;
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 20px;
  color: #374151;
  text-decoration: none;
  transition: all 0.2s ease;
  cursor: pointer;
  border: none;
  background: none;
  width: 100%;
  text-align: left;
  font-size: 14px;
}

.dropdown-item:hover {
  background: #f3f4f6;
}

.dropdown-item svg {
  width: 20px;
  height: 20px;
  color: #6b7280;
}

.dropdown-divider {
  height: 1px;
  background: #e5e7eb;
  margin: 8px 0;
}

.dropdown-item.logout {
  color: #ef4444;
}

.dropdown-item.logout svg {
  color: #ef4444;
}

.dropdown-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 999;
  display: none;
}

.dropdown-overlay.show {
  display: block;
}

/* Main Content */
.main-content {
  flex: 1;
  padding: 30px;
  max-width: 1400px;
  margin: 0 auto;
  width: 100%;
}

/* Top Bar */
.top-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  flex-wrap: wrap;
  gap: 20px;
}

.back-button {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  color: #374151;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.back-button:hover {
  background: #f9fafb;
  border-color: #667eea;
  color: #667eea;
}

.back-button svg {
  width: 20px;
  height: 20px;
}

.stats-mini {
  display: flex;
  gap: 20px;
}

.stat-mini {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 10px 20px;
  background: white;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
}

.stat-mini-value {
  font-size: 24px;
  font-weight: 700;
  color: #667eea;
}

.stat-mini-value.up {
  color: #10b981;
}

.stat-mini-value.down {
  color: #ef4444;
}

.stat-mini-label {
  font-size: 12px;
  color: #6b7280;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-top: 4px;
}

/* Controls Bar */
.controls-bar {
  display: flex;
  gap: 15px;
  margin-bottom: 25px;
  flex-wrap: wrap;
}

.search-box {
  flex: 1;
  position: relative;
  min-width: 300px;
}

.search-icon {
  position: absolute;
  left: 15px;
  top: 50%;
  transform: translateY(-50%);
  width: 20px;
  height: 20px;
  color: #9ca3af;
}

.search-input {
  width: 100%;
  padding: 12px 15px 12px 45px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  font-size: 14px;
  transition: all 0.2s ease;
}

.search-input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.add-camera-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
}

.add-camera-btn:hover {
  opacity: 0.9;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.add-camera-btn svg {
  width: 20px;
  height: 20px;
}

/* Camera List */
.camera-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.no-results {
  text-align: center;
  padding: 60px 20px;
  color: #9ca3af;
}

.no-results svg {
  width: 64px;
  height: 64px;
  margin-bottom: 16px;
}

.no-results p {
  font-size: 16px;
}

.camera-card {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  transition: all 0.2s ease;
  gap: 20px;
}

.camera-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  border-color: #667eea;
}

.camera-info {
  display: flex;
  gap: 15px;
  align-items: flex-start;
  flex: 1;
}

.camera-icon {
  width: 50px;
  height: 50px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.camera-icon svg {
  width: 28px;
  height: 28px;
  color: white;
}

.camera-details {
  flex: 1;
}

.camera-name-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
  flex-wrap: wrap;
}

.camera-name {
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
  margin: 0;
}

.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 600;
}

.status-badge.up {
  background-color: #d1fae5;
  color: #065f46;
}

.status-badge.down {
  background-color: #fee2e2;
  color: #991b1b;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.status-dot.up {
  background-color: #10b981;
}

.status-dot.down {
  background-color: #ef4444;
}

.camera-meta {
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #6b7280
}