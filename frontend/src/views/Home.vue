<script setup>
import { ref, computed, onMounted, onUnmounted, shallowRef, useTemplateRef } from 'vue';
import { useRouter } from 'vue-router';
import L from 'leaflet';
import logoUrl from '../assets/mfu-logo.png';
import Toast from '../components/ui/Toast.vue';
import ConfirmModal from '../components/ui/ConfirmModal.vue';
import api from '../services/api';

const router = useRouter();

const userName = ref("Admin User");
const userRole = ref("Security Administrator");
const showDropdown = ref(false);

// Toast state
const toast = ref({
  show: false,
  message: '',
  type: 'info'
});

// Confirm modal state
const confirmModal = ref({
  show: false,
  title: '',
  message: '',
  onConfirm: null,
  loading: false
});

const cctvs = ref([]);

const parseCoordinates = (coordString) => {
  if (!coordString) return { lat: 0, lng: 0 };
  try {
    // Expected format: "20.0451° N, 99.8825° E" or similar
    const parts = coordString.split(',');
    if (parts.length !== 2) return { lat: 0, lng: 0 };
    
    const latStr = parts[0].replace(/[^\d.]/g, '');
    const lngStr = parts[1].replace(/[^\d.]/g, '');
    
    const lat = parseFloat(latStr);
    const lng = parseFloat(lngStr);
    
    return {
      lat: isNaN(lat) ? 0 : lat,
      lng: isNaN(lng) ? 0 : lng
    };
  } catch (e) {
    console.warn("Failed to parse coordinates:", coordString);
    return { lat: 0, lng: 0 };
  }
};

const fetchCameras = async () => {
  try {
    const response = await api.getCameras();
    cctvs.value = response.data.map(camera => {
      const coords = parseCoordinates(camera.coordinates);
      return {
        ...camera,
        lat: coords.lat,
        lng: coords.lng,
        // Ensure status matches visual logic if needed
      };
    });
    
    // Update map markers after data is loaded
    if (map.value) {
      renderMapMarkers();
    }
  } catch (error) {
    console.error('Error fetching cameras:', error);
    showToast('Failed to load camera data', 'error');
  }
};

// Use shallowRef for Leaflet map instance to avoid deep reactivity performance cost
const map = shallowRef(null);
const mapContainer = useTemplateRef('mapContainer');
const pulseIntervals = [];
const markersLayer = shallowRef(null); // Layer group for markers

const onlineCount = computed(() => cctvs.value.filter(c => c.status === "up").length);
const offlineCount = computed(() => cctvs.value.filter(c => c.status === "down").length);
const totalCount = computed(() => cctvs.value.length);
const userInitials = computed(() => {
  return userName.value
    .split(' ')
    .map(n => n[0])
    .join('')
    .toUpperCase()
    .slice(0, 2);
});

// Helper function to show toast
const showToast = (message, type = 'info') => {
  toast.value = {
    show: true,
    message,
    type
  };
};

// Helper function to close toast
const closeToast = () => {
  toast.value.show = false;
};

const toggleProfileMenu = () => {
  showDropdown.value = !showDropdown.value;
};

const closeDropdown = () => {
  showDropdown.value = false;
};

const goToCameraSettings = () => {
  closeDropdown();
  router.push('/camera-settings');
};

const logout = () => {
  confirmModal.value = {
    show: true,
    title: 'Confirm Logout',
    message: 'Are you sure you want to logout?',
    onConfirm: () => {
      localStorage.removeItem('isAuthenticated');
      confirmModal.value.show = false;
      closeDropdown();
      router.push('/login');
      showToast('Logged out successfully', 'info');
    }
  };
};

const handleLogoError = (event) => {
  event.target.style.display = 'none';
};

const viewCamera = (cctvName) => {
  showToast(`Opening camera view for: ${cctvName}`, 'info');
  // You can replace this with actual navigation to camera view page
  // router.push(`/camera/${cctvName}`);
};

const addMarker = (cctv) => {
  if (!map.value) return;
  
  const color = cctv.status === "up" ? "#10b981" : "#ef4444";
  const statusText = cctv.status === "up" ? "Online" : "Offline";

  // Create custom marker
  const marker = L.circleMarker([cctv.lat, cctv.lng], {
    radius: 10,
    color: color,
    fillColor: color,
    fillOpacity: 0.8,
    weight: 3
  });
  
  if (markersLayer.value) {
    markersLayer.value.addLayer(marker);
  } else if (map.value) {
    marker.addTo(map.value);
  }

  // Create custom popup content
  const popupContent = `
    <div class="popup-header">${cctv.name}</div>
    <div class="popup-body">
      <div class="popup-status">
        <span class="status-badge ${cctv.status}" style="display: inline-flex; align-items: center; gap: 6px; padding: 4px 12px; border-radius: 20px; font-size: 13px; font-weight: 600; background-color: ${cctv.status === 'up' ? '#d1fae5' : '#fee2e2'}; color: ${cctv.status === 'up' ? '#065f46' : '#991b1b'};">
          <span class="legend-dot ${cctv.status}" style="width: 12px; height: 12px; border-radius: 50%; display: inline-block; background-color: ${cctv.status === 'up' ? '#10b981' : '#ef4444'}; box-shadow: 0 0 0 3px ${cctv.status === 'up' ? 'rgba(16, 185, 129, 0.2)' : 'rgba(239, 68, 68, 0.2)'};"></span>
          ${statusText}
        </span>
      </div>
      <div class="popup-info" style="font-size: 13px; color: #6b7280; line-height: 1.6;">
        <div class="popup-info-item" style="display: flex; justify-content: space-between; padding: 4px 0;">
          <span class="popup-info-label" style="font-weight: 500; color: #374151;">Location:</span>
          <span>${cctv.location}</span>
        </div>
        <div class="popup-info-item" style="display: flex; justify-content: space-between; padding: 4px 0;">
          <span class="popup-info-label" style="font-weight: 500; color: #374151;">Last Update:</span>
          <span>${cctv.lastUpdate}</span>
        </div>
        <div class="popup-info-item" style="display: flex; justify-content: space-between; padding: 4px 0;">
          <span class="popup-info-label" style="font-weight: 500; color: #374151;">Coordinates:</span>
          <span>${cctv.lat.toFixed(4)}, ${cctv.lng.toFixed(4)}</span>
        </div>
      </div>
      <div class="popup-actions" style="margin-top: 12px; padding-top: 12px; border-top: 1px solid #e5e7eb;">
        <button 
          onclick="window.viewCameraFromPopup('${cctv.name}')"
          style="width: 100%; padding: 8px 16px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border: none; border-radius: 8px; font-size: 14px; font-weight: 600; cursor: pointer; display: flex; align-items: center; justify-content: center; gap: 8px; transition: all 0.2s ease;"
          onmouseover="this.style.opacity='0.9'; this.style.transform='translateY(-1px)'"
          onmouseout="this.style.opacity='1'; this.style.transform='translateY(0)'"
        >
          <svg style="width: 18px; height: 18px;" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"></path>
          </svg>
          View Camera
        </button>
      </div>
    </div>
  `;

  marker.bindPopup(popupContent, {
    maxWidth: 300,
    className: 'custom-popup'
  });

  // Add pulsing animation for offline cameras
  if (cctv.status === "down") {
    const intervalId = setInterval(() => {
      if (map.value && map.value.hasLayer(marker)) {
         marker.setStyle({ fillOpacity: marker.options.fillOpacity === 0.8 ? 0.3 : 0.8 });
      }
    }, 1000);
    pulseIntervals.push(intervalId);
  }
};

const initMap = () => {
  if (!mapContainer.value) return;

  // Initialize map with better styling
  const mapInstance = L.map(mapContainer.value, {
    zoomControl: true,
    attributionControl: true
  }).setView([20.0443, 99.8937], 16);
  
  map.value = mapInstance;

  // Use a more professional map tile
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors',
    maxZoom: 19
  }).addTo(mapInstance);

  // Create markers layer group
  markersLayer.value = L.layerGroup().addTo(mapInstance);
};

const renderMapMarkers = () => {
  if (!markersLayer.value) return;
  
  // Clear existing markers
  markersLayer.value.clearLayers();
  
  // Clear existing intervals
  pulseIntervals.forEach(id => clearInterval(id));
  pulseIntervals.length = 0;

  // Add CCTV markers
  cctvs.value.forEach(cctv => {
    // Only add if has valid coordinates
    if (cctv.lat && cctv.lng) {
      addMarker(cctv);
    }
  });
};

onMounted(() => {
  initMap();
  // Make viewCamera available globally for popup buttons
  window.viewCameraFromPopup = viewCamera;
  
  // Fetch initial data
  fetchCameras();
  
  // Set up auto-refresh every 30 seconds
  const refreshInterval = setInterval(fetchCameras, 30000);
  
  onUnmounted(() => {
    clearInterval(refreshInterval);
  });
});

onUnmounted(() => {
  // Clean up global function
  delete window.viewCameraFromPopup;
  
  // Clear all pulsing intervals
  pulseIntervals.forEach(id => clearInterval(id));
  pulseIntervals.length = 0;

  // Destroy map instance to prevent memory leaks
  if (map.value) {
    try {
      map.value.remove();
    } catch (e) {
      console.warn('Map cleanup error:', e);
    }
    map.value = null;
  }
});
</script>

<template>
  <div class="dashboard-container">
    <!-- Toast Notification -->
    <Toast 
      :show="toast.show"
      :message="toast.message"
      :type="toast.type"
      @close="closeToast"
    />

    <!-- Confirm Modal -->
    <ConfirmModal
      :show="confirmModal.show"
      :title="confirmModal.title"
      :message="confirmModal.message"
      :loading="confirmModal.loading"
      confirm-text="Confirm"
      cancel-text="Cancel"
      type="danger"
      @confirm="confirmModal.onConfirm"
      @cancel="() => confirmModal.show = false"
      @close="() => confirmModal.show = false"
    />

    <!-- Header -->
    <header class="header">
      <div class="header-content">
        <div class="header-left">
          <img :src="logoUrl" alt="MFU Logo" class="logo" @error="handleLogoError">
          <div class="header-text">
            <h1>CCTV Monitoring System</h1>
            <p>Mae Fah Luang University - Real-time Surveillance</p>
          </div>
        </div>

        <!-- Profile Section -->
        <div class="header-right">
          <div class="profile-section" @click="toggleProfileMenu">
            <div class="profile-avatar">{{ userInitials }}</div>
            <div class="profile-info">
              <div class="profile-name">{{ userName }}</div>
              <div class="profile-role">{{ userRole }}</div>
            </div>
            <svg class="dropdown-arrow" :class="{ open: showDropdown }" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
            </svg>
          </div>

          <!-- Dropdown Menu -->
          <transition name="dropdown">
            <div v-show="showDropdown" class="profile-dropdown">
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
          </transition>

          <div v-show="showDropdown" class="dropdown-overlay" @click="closeDropdown"></div>
        </div>
      </div>
    </header>

    <!-- Status Panel -->
    <div class="status-panel">
      <div class="panel-left">
        <div class="panel-title">
          <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
          </svg>
          <h2>System Status</h2>
        </div>
        <div class="legend">
          <div class="legend-item">
            <span class="legend-dot up"></span>
            <span>Online</span>
          </div>
          <div class="legend-item">
            <span class="legend-dot down"></span>
            <span>Offline</span>
          </div>
        </div>
      </div>

      <div class="stats">
        <div class="stat-card stat-total">
          <div class="stat-icon">
            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"></path>
            </svg>
          </div>
          <div class="stat-info">
            <div class="stat-label">TOTAL CAMERAS</div>
            <div class="stat-value">{{ totalCount }}</div>
          </div>
        </div>

        <div class="stat-card stat-online">
          <div class="stat-icon">
            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
            </svg>
          </div>
          <div class="stat-info">
            <div class="stat-label">ONLINE</div>
            <div class="stat-value">{{ onlineCount }}</div>
          </div>
        </div>

        <div class="stat-card stat-offline">
          <div class="stat-icon">
            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
            </svg>
          </div>
          <div class="stat-info">
            <div class="stat-label">OFFLINE</div>
            <div class="stat-value">{{ offlineCount }}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Map -->
    <main class="map-container">
      <div ref="mapContainer" id="map"></div>
    </main>
  </div>
</template>

<style scoped>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

/* Dashboard Container */
.dashboard-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  width: 100vw;
  background-color: #f7fafc;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

/* Header Styles - Matching CameraSettings */
.header {
  background: rgba(255, 255, 255, 0.98);
  box-shadow: 0 2px 20px rgba(0, 0, 0, 0.1);
  position: sticky;
  top: 0;
  z-index: 1001;
}

.header-content {
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px 30px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 15px;
}

.logo {
  height: 60px;
  width: auto;
}

.header-text h1 {
  font-size: 24px;
  color: #2d3748;
  font-weight: 700;
  margin-bottom: 4px;
  letter-spacing: -0.5px;
}

.header-text p {
  font-size: 14px;
  color: #718096;
  font-weight: 400;
}

.header-right {
  position: relative;
}

/* Profile Section */
.profile-section {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.5rem 1rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 50px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.profile-section:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.profile-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: white;
  color: #667eea;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 0.875rem;
}

.profile-info {
  display: flex;
  flex-direction: column;
}

.profile-name {
  color: white;
  font-weight: 600;
  font-size: 0.875rem;
}

.profile-role {
  color: rgba(255, 255, 255, 0.9);
  font-size: 0.75rem;
}

.dropdown-arrow {
  width: 20px;
  height: 20px;
  color: white;
  transition: transform 0.3s ease;
}

.dropdown-arrow.open {
  transform: rotate(180deg);
}

/* Dropdown Menu */
.profile-dropdown {
  position: absolute;
  top: calc(100% + 0.5rem);
  right: 0;
  background: white;
  border-radius: 12px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.15);
  min-width: 280px;
  overflow: hidden;
  z-index: 1002;
}

.dropdown-header {
  padding: 1.5rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  text-align: center;
}

.dropdown-avatar {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: white;
  color: #667eea;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 1.25rem;
  margin: 0 auto 0.75rem;
}

.dropdown-name {
  color: white;
  font-weight: 600;
  font-size: 1rem;
  margin-bottom: 0.25rem;
}

.dropdown-role {
  color: rgba(255, 255, 255, 0.9);
  font-size: 0.875rem;
}

.dropdown-menu {
  padding: 0.5rem;
}

.dropdown-item {
  width: 100%;
  padding: 0.75rem 1rem;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  background: none;
  border: none;
  cursor: pointer;
  color: #4a5568;
  font-size: 0.875rem;
  border-radius: 8px;
  transition: all 0.2s ease;
}

.dropdown-item:hover {
  background: #f7fafc;
  color: #667eea;
}

.dropdown-item.logout:hover {
  background: #fff5f5;
  color: #e53e3e;
}

.dropdown-item svg {
  width: 20px;
  height: 20px;
}

.dropdown-divider {
  height: 1px;
  background: #e2e8f0;
  margin: 0.5rem 0;
}

.dropdown-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 1000;
}

/* Transitions */
.dropdown-enter-active,
.dropdown-leave-active {
  transition: all 0.3s ease;
}

.dropdown-enter-from,
.dropdown-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

/* Status Panel - Enhanced */
.status-panel {
  background: white;
  padding: 20px 30px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 30px;
  flex-wrap: wrap;
  flex-shrink: 0;
  z-index: 1000;
  position: relative;
  border-bottom: 1px solid #e2e8f0;
}

.panel-left {
  display: flex;
  align-items: center;
  gap: 30px;
}

.panel-title {
  display: flex;
  align-items: center;
  gap: 12px;
}

.panel-title svg {
  width: 24px;
  height: 24px;
  color: #667eea;
}

.panel-title h2 {
  font-size: 1.25rem;
  color: #2d3748;
  font-weight: 700;
}

.legend {
  display: flex;
  align-items: center;
  gap: 20px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 500;
  color: #4a5568;
}

.legend-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  display: inline-block;
}

.legend-dot.up {
  background-color: #10b981;
  box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.2);
  animation: pulse-green 2s ease-in-out infinite;
}

.legend-dot.down {
  background-color: #ef4444;
  box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.2);
  animation: pulse-red 2s ease-in-out infinite;
}

@keyframes pulse-green {
  0%, 100% {
    box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.2);
  }
  50% {
    box-shadow: 0 0 0 6px rgba(16, 185, 129, 0.1);
  }
}

@keyframes pulse-red {
  0%, 100% {
    box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.2);
  }
  50% {
    box-shadow: 0 0 0 6px rgba(239, 68, 68, 0.1);
  }
}

/* Stats Cards - Enhanced to match CameraSettings */
.stats {
  display: flex;
  gap: 15px;
}

.stat-card {
  background: white;
  border-radius: 12px;
  padding: 16px 20px;
  display: flex;
  align-items: center;
  gap: 14px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border: 2px solid #e2e8f0;
  transition: all 0.3s ease;
  min-width: 180px;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.stat-icon svg {
  width: 24px;
  height: 24px;
  color: white;
}

.stat-total .stat-icon {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.stat-online .stat-icon {
  background: linear-gradient(135deg, #48bb78 0%, #38a169 100%);
}

.stat-offline .stat-icon {
  background: linear-gradient(135deg, #f56565 0%, #e53e3e 100%);
}

.stat-info {
  flex: 1;
}

.stat-label {
  font-size: 0.75rem;
  color: #718096;
  font-weight: 600;
  letter-spacing: 0.5px;
  margin-bottom: 4px;
}

.stat-value {
  font-size: 1.875rem;
  font-weight: 700;
  color: #2d3748;
  line-height: 1;
}

/* Map Container */
.map-container {
  flex: 1;
  position: relative;
  overflow: hidden;
  z-index: 1;
}

#map {
  height: 100%;
  width: 100%;
}

/* Responsive Design */
@media (max-width: 1024px) {
  .status-panel {
    flex-direction: column;
    align-items: flex-start;
  }

  .panel-left {
    width: 100%;
    flex-wrap: wrap;
  }

  .stats {
    width: 100%;
    overflow-x: auto;
  }
}

@media (max-width: 768px) {
  .header-content {
    padding: 15px 20px;
  }

  .header-text h1 {
    font-size: 18px;
  }

  .header-text p {
    font-size: 12px;
  }

  .logo {
    height: 45px;
  }

  .profile-info {
    display: none;
  }

  .status-panel {
    padding: 15px 20px;
  }

  .panel-title h2 {
    font-size: 1rem;
  }

  .stats {
    gap: 10px;
  }

  .stat-card {
    min-width: 150px;
    padding: 12px 16px;
  }

  .stat-icon {
    width: 40px;
    height: 40px;
  }

  .stat-icon svg {
    width: 20px;
    height: 20px;
  }

  .stat-value {
    font-size: 1.5rem;
  }
}

@media (max-width: 480px) {
  .panel-title svg {
    width: 20px;
    height: 20px;
  }

  .legend {
    gap: 15px;
  }

  .legend-item {
    font-size: 12px;
  }
}
</style>

<style>
/* Global styles for Leaflet popup */
.leaflet-popup-content-wrapper {
  border-radius: 12px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
  padding: 0;
  overflow: hidden;
}

.leaflet-popup-content {
  margin: 0;
  min-width: 250px;
}

.leaflet-popup-tip {
  box-shadow: 0 3px 14px rgba(0, 0, 0, 0.2);
}

.popup-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 14px 16px;
  font-weight: 600;
  font-size: 15px;
}

.popup-body {
  padding: 16px;
}

.custom-popup .leaflet-popup-close-button {
  color: white;
  font-size: 24px;
  padding: 8px 12px;
}

.custom-popup .leaflet-popup-close-button:hover {
  color: rgba(255, 255, 255, 0.8);
}
</style>