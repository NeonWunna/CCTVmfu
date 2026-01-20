<script setup>
import { ref, computed } from 'vue';
import { useRouter } from 'vue-router';
import logoUrl from '../assets/mfu-logo.png';

const router = useRouter();

const userName = ref("Admin User");
const userRole = ref("Security Administrator");
const showDropdown = ref(false);
const searchQuery = ref("");
const viewMode = ref("grid"); // 'grid' or 'list'

const cameras = ref([
  { 
    id: 1,
    name: "Main Gate CCTV", 
    status: "up",
    location: "Main Entrance",
    ipAddress: "192.168.1.10",
    lastUpdate: "2 min ago",
    category: "entrance"
  },
  { 
    id: 2,
    name: "Library CCTV", 
    status: "up",
    location: "Central Library",
    ipAddress: "192.168.1.11",
    lastUpdate: "1 min ago",
    category: "academic"
  },
  { 
    id: 3,
    name: "Dormitory CCTV", 
    status: "down",
    location: "Student Housing",
    ipAddress: "192.168.1.12",
    lastUpdate: "15 min ago",
    category: "residential"
  },
  { 
    id: 4,
    name: "Parking Lot CCTV", 
    status: "up",
    location: "Parking Area A",
    ipAddress: "192.168.1.13",
    lastUpdate: "Just now",
    category: "parking"
  },
  { 
    id: 5,
    name: "Sports Complex CCTV", 
    status: "up",
    location: "Athletic Center",
    ipAddress: "192.168.1.14",
    lastUpdate: "3 min ago",
    category: "sports"
  },
  { 
    id: 6,
    name: "Cafeteria CCTV", 
    status: "up",
    location: "Student Cafeteria",
    ipAddress: "192.168.1.15",
    lastUpdate: "1 min ago",
    category: "facilities"
  },
  { 
    id: 7,
    name: "Admin Building CCTV", 
    status: "up",
    location: "Administration Office",
    ipAddress: "192.168.1.16",
    lastUpdate: "4 min ago",
    category: "administrative"
  },
  { 
    id: 8,
    name: "Science Building CCTV", 
    status: "up",
    location: "Science Faculty",
    ipAddress: "192.168.1.17",
    lastUpdate: "2 min ago",
    category: "academic"
  },
  { 
    id: 9,
    name: "Engineering Hall CCTV", 
    status: "down",
    location: "Engineering Building",
    ipAddress: "192.168.1.18",
    lastUpdate: "20 min ago",
    category: "academic"
  },
  { 
    id: 10,
    name: "East Gate CCTV", 
    status: "up",
    location: "East Entrance",
    ipAddress: "192.168.1.19",
    lastUpdate: "Just now",
    category: "entrance"
  },
  { 
    id: 11,
    name: "West Gate CCTV", 
    status: "up",
    location: "West Entrance",
    ipAddress: "192.168.1.20",
    lastUpdate: "3 min ago",
    category: "entrance"
  },
  { 
    id: 12,
    name: "Parking Area B CCTV", 
    status: "up",
    location: "Parking Lot B",
    ipAddress: "192.168.1.21",
    lastUpdate: "5 min ago",
    category: "parking"
  },
  { 
    id: 13,
    name: "Student Center CCTV", 
    status: "up",
    location: "Student Activities Center",
    ipAddress: "192.168.1.22",
    lastUpdate: "2 min ago",
    category: "facilities"
  },
  { 
    id: 14,
    name: "Basketball Court CCTV", 
    status: "up",
    location: "Outdoor Courts",
    ipAddress: "192.168.1.23",
    lastUpdate: "6 min ago",
    category: "sports"
  },
  { 
    id: 15,
    name: "Medical Center CCTV", 
    status: "up",
    location: "Health Services",
    ipAddress: "192.168.1.24",
    lastUpdate: "1 min ago",
    category: "facilities"
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
};

const removeCamera = (camera) => {
  if (confirm(`Are you sure you want to remove "${camera.name}"?`)) {
    cameras.value = cameras.value.filter(c => c.id !== camera.id);
  }
};

const addNewCamera = () => {
  alert('Add new camera functionality will be implemented here');
};

const toggleViewMode = () => {
  viewMode.value = viewMode.value === 'grid' ? 'list' : 'grid';
};
</script>

<template>
  <div class="settings-container">
    <!-- Header -->
    <header class="header">
      <div class="header-left">
        <div class="logo-container">
          <img :src="logoUrl" alt="MFU Logo" class="logo" @error="handleLogoError">
        </div>
        <div class="header-text">
          <h1>Camera Management</h1>
          <p>Mae Fah Luang University Security System</p>
        </div>
      </div>

      <div class="header-right">
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

      <div class="dropdown-overlay" :class="{ show: showDropdown }" @click="closeDropdown"></div>
    </header>

    <!-- Main Content -->
    <main class="main-content">
      <!-- Navigation -->
      <div class="navigation-bar">
        <button class="back-button" @click="goToDashboard">
          <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"></path>
          </svg>
          Dashboard
        </button>
      </div>

      <!-- Stats Overview -->
      <div class="stats-section">
        <div class="stat-card stat-total">
          <div class="stat-icon">
            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"></path>
            </svg>
          </div>
          <div class="stat-content">
            <div class="stat-label">Total Cameras</div>
            <div class="stat-value">{{ totalCount }}</div>
          </div>
        </div>

        <div class="stat-card stat-online">
          <div class="stat-icon">
            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
            </svg>
          </div>
          <div class="stat-content">
            <div class="stat-label">Online</div>
            <div class="stat-value">{{ onlineCount }}</div>
          </div>
        </div>

        <div class="stat-card stat-offline">
          <div class="stat-icon">
            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
            </svg>
          </div>
          <div class="stat-content">
            <div class="stat-label">Offline</div>
            <div class="stat-value">{{ offlineCount }}</div>
          </div>
        </div>

        <div class="stat-card stat-uptime">
          <div class="stat-icon">
            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"></path>
            </svg>
          </div>
          <div class="stat-content">
            <div class="stat-label">System Uptime</div>
            <div class="stat-value">{{ Math.round((onlineCount / totalCount) * 100) }}%</div>
          </div>
        </div>
      </div>

      <!-- Controls Section -->
      <div class="controls-section">
        <div class="section-header">
          <h2>Camera Inventory</h2>
          <p>Manage and monitor all CCTV cameras across campus</p>
        </div>

        <div class="controls-bar">
          <div class="search-container">
            <svg class="search-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
            </svg>
            <input 
              v-model="searchQuery"
              type="text" 
              placeholder="Search by name, location, or IP address..."
              class="search-input"
            >
          </div>

          <div class="action-buttons">
            <button class="view-toggle-btn" @click="toggleViewMode" :title="viewMode === 'grid' ? 'Switch to List View' : 'Switch to Grid View'">
              <svg v-if="viewMode === 'grid'" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"></path>
              </svg>
              <svg v-else fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z"></path>
              </svg>
            </button>
            
            <button class="add-camera-btn" @click="addNewCamera">
              <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path>
              </svg>
              Add Camera
            </button>
          </div>
        </div>
      </div>

      <!-- Camera List -->
      <div class="camera-section">
        <div v-if="filteredCameras.length === 0" class="no-results">
          <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
          </svg>
          <h3>No cameras found</h3>
          <p>Try adjusting your search criteria</p>
        </div>

        <div v-else class="camera-grid" :class="{ 'list-view': viewMode === 'list' }">
          <div v-for="camera in filteredCameras" :key="camera.id" class="camera-card">
            <div class="camera-header">
              <div class="camera-icon-wrapper">
                <svg class="camera-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"></path>
                </svg>
              </div>
              <span class="status-indicator" :class="camera.status">
                <span class="status-dot"></span>
                {{ camera.status === 'up' ? 'Online' : 'Offline' }}
              </span>
            </div>

            <div class="camera-body">
              <h3 class="camera-name">{{ camera.name }}</h3>
              
              <div class="camera-details">
                <div class="detail-row">
                  <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"></path>
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"></path>
                  </svg>
                  <span>{{ camera.location }}</span>
                </div>

                <div class="detail-row">
                  <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9"></path>
                  </svg>
                  <span class="ip-address">{{ camera.ipAddress }}</span>
                </div>

                <div class="detail-row">
                  <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                  </svg>
                  <span class="last-update">{{ camera.lastUpdate }}</span>
                </div>
              </div>
            </div>

            <div class="camera-footer">
              <button class="card-action-btn edit" @click="editCamera(camera)">
                <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
                </svg>
                Edit
              </button>
              <button class="card-action-btn delete" @click="removeCamera(camera)">
                <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
                </svg>
                Remove
              </button>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<style scoped>
* {
  box-sizing: border-box;
}

/* Container */
.settings-container {
  min-height: 100vh;
  background: linear-gradient(to bottom, #f8fafc 0%, #e2e8f0 100%);
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

/* Header */
.header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 1.25rem 2rem;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  justify-content: space-between;
  position: sticky;
  top: 0;
  z-index: 1000;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 1.25rem;
}

.logo-container {
  display: flex;
  align-items: center;
}

.logo {
  height: 50px;
  width: auto;
}

.header-text h1 {
  font-size: 1.5rem;
  font-weight: 700;
  margin: 0 0 0.25rem 0;
  letter-spacing: -0.025em;
}

.header-text p {
  font-size: 0.875rem;
  margin: 0;
  opacity: 0.95;
  font-weight: 400;
}

/* Profile Section */
.header-right {
  display: flex;
  align-items: center;
}

.profile-section {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  background: rgba(255, 255, 255, 0.15);
  padding: 0.5rem 1rem;
  border-radius: 50px;
  cursor: pointer;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
}

.profile-section:hover {
  background: rgba(255, 255, 255, 0.25);
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
  font-size: 0.875rem;
  color: white;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.profile-info {
  display: flex;
  flex-direction: column;
}

.profile-name {
  font-size: 0.875rem;
  font-weight: 600;
  line-height: 1.2;
}

.profile-role {
  font-size: 0.75rem;
  opacity: 0.9;
  line-height: 1.2;
}

.profile-dropdown-icon {
  width: 18px;
  height: 18px;
  transition: transform 0.3s ease;
  opacity: 0.9;
}

.profile-dropdown-icon.open {
  transform: rotate(180deg);
}

/* Dropdown */
.profile-dropdown {
  position: absolute;
  top: 100%;
  right: 2rem;
  margin-top: 0.75rem;
  background: white;
  border-radius: 12px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.15);
  min-width: 240px;
  overflow: hidden;
  z-index: 1001;
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
  padding: 1.5rem;
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
  font-size: 1.5rem;
  margin: 0 auto 0.75rem;
  border: 3px solid rgba(255, 255, 255, 0.3);
}

.dropdown-name {
  font-size: 1rem;
  font-weight: 600;
  margin-bottom: 0.25rem;
}

.dropdown-role {
  font-size: 0.8125rem;
  opacity: 0.95;
}

.dropdown-menu {
  padding: 0.5rem 0;
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1.25rem;
  color: #374151;
  border: none;
  background: none;
  width: 100%;
  text-align: left;
  font-size: 0.875rem;
  cursor: pointer;
  transition: background 0.2s ease;
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
  margin: 0.5rem 0;
}

.dropdown-item.logout {
  color: #ef4444;
}

.dropdown-item.logout svg {
  color: #ef4444;
}

.dropdown-overlay {
  position: fixed;
  inset: 0;
  z-index: 999;
  display: none;
}

.dropdown-overlay.show {
  display: block;
}

/* Main Content */
.main-content {
  max-width: 1400px;
  margin: 0 auto;
  padding: 2rem;
}

/* Navigation Bar */
.navigation-bar {
  margin-bottom: 2rem;
}

.back-button {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.625rem 1.25rem;
  background: white;
  border: 2px solid #e5e7eb;
  border-radius: 10px;
  color: #374151;
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.back-button:hover {
  border-color: #667eea;
  color: #667eea;
  transform: translateX(-2px);
}

.back-button svg {
  width: 18px;
  height: 18px;
}

/* Stats Section */
.stats-section {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.25rem;
  margin-bottom: 2.5rem;
}

.stat-card {
  background: white;
  border-radius: 16px;
  padding: 1.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  border: 2px solid #f3f4f6;
  display: flex;
  align-items: center;
  gap: 1.25rem;
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.stat-icon svg {
  width: 32px;
  height: 32px;
  color: white;
}

.stat-total .stat-icon {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.stat-online .stat-icon {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
}

.stat-offline .stat-icon {
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
}

.stat-uptime .stat-icon {
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
}

.stat-content {
  flex: 1;
}

.stat-label {
  font-size: 0.875rem;
  color: #6b7280;
  font-weight: 500;
  margin-bottom: 0.375rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.stat-value {
  font-size: 2rem;
  font-weight: 700;
  color: #1f2937;
  line-height: 1;
}

/* Controls Section */
.controls-section {
  background: white;
  border-radius: 16px;
  padding: 1.75rem;
  margin-bottom: 2rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  border: 2px solid #f3f4f6;
}

.section-header {
  margin-bottom: 1.5rem;
}

.section-header h2 {
  font-size: 1.5rem;
  font-weight: 700;
  color: #1f2937;
  margin: 0 0 0.375rem 0;
}

.section-header p {
  font-size: 0.875rem;
  color: #6b7280;
  margin: 0;
}

.controls-bar {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.search-container {
  flex: 1;
  position: relative;
}

.search-icon {
  position: absolute;
  left: 1rem;
  top: 50%;
  transform: translateY(-50%);
  width: 20px;
  height: 20px;
  color: #9ca3af;
  pointer-events: none;
}

.search-input {
  width: 100%;
  padding: 0.875rem 1rem 0.875rem 3rem;
  border: 2px solid #e5e7eb;
  border-radius: 10px;
  font-size: 0.875rem;
  transition: all 0.2s ease;
  background: #f9fafb;
}

.search-input:focus {
  outline: none;
  border-color: #667eea;
  background: white;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.action-buttons {
  display: flex;
  gap: 0.75rem;
}

.view-toggle-btn {
  padding: 0.875rem;
  background: #f3f4f6;
  border: 2px solid #e5e7eb;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.view-toggle-btn:hover {
  background: #e5e7eb;
  border-color: #667eea;
}

.view-toggle-btn svg {
  width: 20px;
  height: 20px;
  color: #374151;
}

.add-camera-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.875rem 1.5rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 10px;
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
}

.add-camera-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(102, 126, 234, 0.3);
}

.add-camera-btn svg {
  width: 20px;
  height: 20px;
}

/* Camera Section */
.camera-section {
  min-height: 400px;
}

.no-results {
  text-align: center;
  padding: 4rem 2rem;
  color: #9ca3af;
}

.no-results svg {
  width: 80px;
  height: 80px;
  margin-bottom: 1.5rem;
  opacity: 0.5;
}

.no-results h3 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #6b7280;
  margin: 0 0 0.5rem 0;
}

.no-results p {
  font-size: 0.875rem;
  margin: 0;
}

/* Camera Grid */
.camera-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 1.5rem;
}

.camera-grid.list-view {
  grid-template-columns: 1fr;
}

/* Camera Card */
.camera-card {
  background: white;
  border-radius: 16px;
  padding: 1.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  border: 2px solid #f3f4f6;
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.camera-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
  border-color: #667eea;
}

.camera-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.camera-icon-wrapper {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
}

.camera-icon {
  width: 28px;
  height: 28px;
  color: white;
}

.status-indicator {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.375rem 0.875rem;
  border-radius: 20px;
  font-size: 0.8125rem;
  font-weight: 600;
}

.status-indicator.up {
  background: #d1fae5;
  color: #065f46;
}

.status-indicator.down {
  background: #fee2e2;
  color: #991b1b;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: currentColor;
}

.camera-body {
  flex: 1;
}

.camera-name {
  font-size: 1.125rem;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 1rem 0;
}

.camera-details {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.detail-row {
  display: flex;
  align-items: center;
  gap: 0.625rem;
  font-size: 0.875rem;
  color: #6b7280;
}

.detail-row svg {
  width: 18px;
  height: 18px;
  color: #9ca3af;
  flex-shrink: 0;
}

.ip-address {
  font-family: 'Monaco', 'Courier New', monospace;
  font-size: 0.8125rem;
}

.camera-footer {
  display: flex;
  gap: 0.75rem;
  padding-top: 0.75rem;
  border-top: 1px solid #f3f4f6;
}

.card-action-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.625rem 1rem;
  border-radius: 8px;
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  border: 2px solid;
}

.card-action-btn svg {
  width: 16px;
  height: 16px;
}

.card-action-btn.edit {
  background: white;
  color: #667eea;
  border-color: #667eea;
}

.card-action-btn.edit:hover {
  background: #667eea;
  color: white;
}

.card-action-btn.delete {
  background: white;
  color: #ef4444;
  border-color: #ef4444;
}

.card-action-btn.delete:hover {
  background: #ef4444;
  color: white;
}

/* Responsive Design */
@media (max-width: 1024px) {
  .camera-grid {
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  }
}

@media (max-width: 768px) {
  .header {
    padding: 1rem 1.25rem;
    flex-wrap: wrap;
  }

  .header-left {
    gap: 0.875rem;
  }

  .logo {
    height: 40px;
  }

  .header-text h1 {
    font-size: 1.25rem;
  }

  .header-text p {
    font-size: 0.75rem;
  }

  .main-content {
    padding: 1.25rem;
  }

  .stats-section {
    grid-template-columns: 1fr;
  }

  .controls-bar {
    flex-direction: column;
    align-items: stretch;
  }

  .action-buttons {
    width: 100%;
  }

  .view-toggle-btn,
  .add-camera-btn {
    flex: 1;
  }

  .camera-grid {
    grid-template-columns: 1fr;
  }

  .profile-dropdown {
    right: 1rem;
    left: 1rem;
    margin-top: 0.5rem;
  }
}

@media (max-width: 480px) {
  .stat-card {
    padding: 1.25rem;
  }

  .stat-icon {
    width: 50px;
    height: 50px;
  }

  .stat-icon svg {
    width: 26px;
    height: 26px;
  }

  .stat-value {
    font-size: 1.5rem;
  }

  .camera-footer {
    flex-direction: column;
  }
}
</style>