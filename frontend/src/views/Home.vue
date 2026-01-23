<script setup>
import { ref, computed, onMounted, onUnmounted, shallowRef, useTemplateRef, watch } from 'vue';
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
const searchQuery = ref("");

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
    // Expected format: "20.0451, 99.8825" or "-99.0, 79.2313"
    const parts = coordString.split(',');
    if (parts.length !== 2) return { lat: 0, lng: 0 };
    
    // Keep minus sign, digits, and dots only
    const latStr = parts[0].replace(/[^\d.-]/g, '');
    const lngStr = parts[1].replace(/[^\d.-]/g, '');
    
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
        // Map backend snake_case to frontend camelCase
        ipAddress: camera.ip_address,
        lastUpdate: camera.last_update
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

const filteredCameras = computed(() => {
  if (!searchQuery.value.trim()) {
    return cctvs.value;
  }
  
  const query = searchQuery.value.toLowerCase().trim();
  return cctvs.value.filter(camera => 
    camera.name.toLowerCase().includes(query) ||
    (camera.ipAddress && camera.ipAddress.toLowerCase().includes(query))
  );
});

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
  // Find the camera data
  const camera = cctvs.value.find(c => c.name === cctvName);
  if (camera) {
    // Navigate to camera view with data
    router.push({
      name: 'CameraView',
      params: { id: camera.id },
      query: {
        name: camera.name,
        location: camera.location,
        ip: camera.ipAddress,
        status: camera.status,
        coordinates: `${camera.lat}, ${camera.lng}`,
        brand: camera.brand || 'N/A',
        lastUpdate: camera.lastUpdate || new Date().toLocaleString()
      }
    });
  }
};

const focusOnCamera = (camera) => {
  if (!map.value || !camera.lat || !camera.lng) return;
  
  // Zoom and pan to camera location
  map.value.setView([camera.lat, camera.lng], 18, {
    animate: true,
    duration: 1
  });
  
  // Find and open the popup for this camera
  setTimeout(() => {
    markersLayer.value.eachLayer((layer) => {
      if (layer.getLatLng().lat === camera.lat && layer.getLatLng().lng === camera.lng) {
        layer.openPopup();
      }
    });
  }, 500);
  
  showToast(`Focused on: ${camera.name}`, 'info');
};

const clearSearch = () => {
  searchQuery.value = "";
  if (map.value && cctvs.value.length > 0) {
    // Reset to default view showing all cameras
    map.value.setView([20.0443, 99.8937], 16);
  }
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

  // Create custom popup content with IP and Last Update - Dark Theme
  const popupContent = `
    <div class="popup-header">${cctv.name}</div>
    <div class="popup-body">
      <div class="popup-status">
        <span class="status-badge ${cctv.status}" style="display: inline-flex; align-items: center; gap: 6px; padding: 6px 14px; border-radius: 20px; font-size: 13px; font-weight: 600; background-color: ${cctv.status === 'up' ? 'rgba(16, 185, 129, 0.15)' : 'rgba(239, 68, 68, 0.15)'}; color: ${cctv.status === 'up' ? '#10b981' : '#ef4444'}; border: 1px solid ${cctv.status === 'up' ? 'rgba(16, 185, 129, 0.3)' : 'rgba(239, 68, 68, 0.3)'};">
          <span class="legend-dot ${cctv.status}" style="width: 10px; height: 10px; border-radius: 50%; display: inline-block; background-color: ${cctv.status === 'up' ? '#10b981' : '#ef4444'}; box-shadow: 0 0 0 3px ${cctv.status === 'up' ? 'rgba(16, 185, 129, 0.2)' : 'rgba(239, 68, 68, 0.2)'};"></span>
          ${statusText}
        </span>
      </div>
      <div class="popup-info" style="font-size: 13px; color: rgba(255, 255, 255, 0.7); line-height: 1.8;">
        <div class="popup-info-item" style="display: flex; justify-content: space-between; padding: 6px 0;">
          <span class="popup-info-label" style="font-weight: 500; color: rgba(255, 255, 255, 0.9);">IP Address:</span>
          <span style="font-family: 'Courier New', monospace; color: rgba(102, 126, 234, 0.9);">${cctv.ipAddress || 'N/A'}</span>
        </div>
        <div class="popup-info-item" style="display: flex; justify-content: space-between; padding: 6px 0;">
          <span class="popup-info-label" style="font-weight: 500; color: rgba(255, 255, 255, 0.9);">Location:</span>
          <span>${cctv.location}</span>
        </div>
        <div class="popup-info-item" style="display: flex; justify-content: space-between; padding: 6px 0;">
          <span class="popup-info-label" style="font-weight: 500; color: rgba(255, 255, 255, 0.9);">Last Update:</span>
          <span>${cctv.lastUpdate || 'N/A'}</span>
        </div>
        <div class="popup-info-item" style="display: flex; justify-content: space-between; padding: 6px 0;">
          <span class="popup-info-label" style="font-weight: 500; color: rgba(255, 255, 255, 0.9);">Coordinates:</span>
          <span>${cctv.lat.toFixed(4)}, ${cctv.lng.toFixed(4)}</span>
        </div>
      </div>
      <div class="popup-actions" style="margin-top: 14px; padding-top: 14px; border-top: 1px solid rgba(255, 255, 255, 0.1);">
        <button 
          onclick="window.viewCameraFromPopup('${cctv.name}')"
          style="width: 100%; padding: 10px 18px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border: none; border-radius: 10px; font-size: 14px; font-weight: 600; cursor: pointer; display: flex; align-items: center; justify-content: center; gap: 8px; transition: all 0.2s ease; box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);"
          onmouseover="this.style.opacity='0.9'; this.style.transform='translateY(-1px)'; this.style.boxShadow='0 6px 16px rgba(102, 126, 234, 0.4)'"
          onmouseout="this.style.opacity='1'; this.style.transform='translateY(0)'; this.style.boxShadow='0 4px 12px rgba(102, 126, 234, 0.3)'"
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

  // Determine which cameras to display based on search
  const camerasToDisplay = searchQuery.value.trim() ? filteredCameras.value : cctvs.value;

  // Add CCTV markers
  camerasToDisplay.forEach(cctv => {
    // Only add if has valid coordinates
    if (cctv.lat && cctv.lng) {
      addMarker(cctv);
    }
  });

  // If searching and have results, adjust map view to show all filtered cameras
  if (searchQuery.value.trim() && camerasToDisplay.length > 0) {
    const bounds = L.latLngBounds(
      camerasToDisplay
        .filter(c => c.lat && c.lng)
        .map(c => [c.lat, c.lng])
    );
    
    if (bounds.isValid()) {
      map.value.fitBounds(bounds, { padding: [50, 50], maxZoom: 17 });
    }
  }
};

onMounted(() => {
  initMap();
  // Make viewCamera available globally for popup buttons
  window.viewCameraFromPopup = viewCamera;
  
  // Fetch initial data
  fetchCameras();
  
  // Set up auto-refresh every 30 seconds
  const refreshInterval = setInterval(fetchCameras, 30000);
  
  // Watch search query changes and update markers
  watch(searchQuery, () => {
    if (map.value) {
      renderMapMarkers();
    }
  });
  
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

      <div class="panel-center">
        <div class="search-wrapper">
          <svg class="search-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
          </svg>
          <input 
            v-model="searchQuery"
            type="text" 
            placeholder="Search cameras by name or IP..."
            class="search-input"
            aria-label="Search cameras"
          >
          <button 
            v-if="searchQuery" 
            @click="clearSearch" 
            class="clear-button"
            aria-label="Clear search"
          >
            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
            </svg>
          </button>
        </div>
        <div v-if="searchQuery" class="search-results-info">
          <span class="results-count">
            {{ filteredCameras.length }} camera{{ filteredCameras.length !== 1 ? 's' : '' }} found
          </span>
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

    <!-- Search Results Panel (only show when searching) -->
    <transition name="slide-down">
      <div v-if="searchQuery && filteredCameras.length > 0" class="search-results-panel">
        <div class="results-header">
          <h3>Search Results</h3>
          <button @click="clearSearch" class="close-results">
            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
            </svg>
          </button>
        </div>
        <div class="results-list">
          <div 
            v-for="camera in filteredCameras" 
            :key="camera.id" 
            class="result-item"
            @click="focusOnCamera(camera)"
          >
            <div class="result-icon">
              <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"></path>
              </svg>
            </div>
            <div class="result-info">
              <div class="result-name">{{ camera.name }}</div>
              <div class="result-details">
                <span class="result-ip">{{ camera.ipAddress }}</span>
                <span class="result-separator">•</span>
                <span class="result-location">{{ camera.location }}</span>
              </div>
            </div>
            <span class="status-indicator" :class="camera.status"></span>
          </div>
        </div>
      </div>
    </transition>

    <!-- No Results Message -->
    <transition name="fade">
      <div v-if="searchQuery && filteredCameras.length === 0" class="no-results">
        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
        </svg>
        <h3>No cameras found</h3>
        <p>Try searching with a different name or IP address</p>
        <button @click="clearSearch" class="clear-search-button">Clear Search</button>
      </div>
    </transition>

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

/* Dashboard Container - Dark Theme */
.dashboard-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  width: 100vw;
  background: linear-gradient(135deg, rgba(26, 32, 44, 0.95) 0%, rgba(45, 55, 72, 0.98) 100%);
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  position: relative;
}

.dashboard-container::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: 
    radial-gradient(circle at 20% 30%, rgba(102, 126, 234, 0.1) 0%, transparent 50%),
    radial-gradient(circle at 80% 70%, rgba(118, 75, 162, 0.1) 0%, transparent 50%);
  pointer-events: none;
  z-index: 0;
}

/* Header Styles - Dark Theme */
.header {
  background: rgba(26, 32, 44, 0.95);
  backdrop-filter: blur(20px);
  box-shadow: 0 2px 20px rgba(0, 0, 0, 0.3), 0 0 0 1px rgba(102, 126, 234, 0.2);
  position: sticky;
  top: 0;
  z-index: 1001;
  border-bottom: 2px solid rgba(102, 126, 234, 0.2);
  position: relative;
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
  filter: drop-shadow(0 2px 8px rgba(0, 0, 0, 0.3));
}

.header-text h1 {
  font-size: 24px;
  color: white;
  font-weight: 700;
  margin-bottom: 4px;
  letter-spacing: -0.5px;
  text-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
}

.header-text p {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.7);
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
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
}

.profile-section:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.5);
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

/* Dropdown Menu - Dark Theme */
.profile-dropdown {
  position: absolute;
  top: calc(100% + 0.5rem);
  right: 0;
  background: rgba(26, 32, 44, 0.98);
  backdrop-filter: blur(20px);
  border: 2px solid rgba(102, 126, 234, 0.3);
  border-radius: 12px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5);
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
  color: rgba(255, 255, 255, 0.8);
  font-size: 0.875rem;
  border-radius: 8px;
  transition: all 0.2s ease;
}

.dropdown-item:hover {
  background: rgba(102, 126, 234, 0.2);
  color: white;
}

.dropdown-item.logout:hover {
  background: rgba(239, 68, 68, 0.2);
  color: #ef4444;
}

.dropdown-item svg {
  width: 20px;
  height: 20px;
}

.dropdown-divider {
  height: 1px;
  background: rgba(255, 255, 255, 0.1);
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

/* Status Panel - Dark Theme */
.status-panel {
  background: rgba(26, 32, 44, 0.9);
  backdrop-filter: blur(20px);
  padding: 20px 30px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 30px;
  flex-wrap: wrap;
  flex-shrink: 0;
  z-index: 1000;
  position: relative;
  border-bottom: 2px solid rgba(102, 126, 234, 0.2);
}

.panel-left {
  display: flex;
  align-items: center;
  gap: 30px;
  min-width: 250px;
}

.panel-center {
  flex: 1;
  max-width: 500px;
  min-width: 280px;
}

.panel-title {
  display: flex;
  align-items: center;
  gap: 12px;
}

.panel-title svg {
  width: 24px;
  height: 24px;
  color: rgba(102, 126, 234, 0.8);
}

.panel-title h2 {
  font-size: 1.25rem;
  color: white;
  font-weight: 700;
  text-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
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
  color: rgba(255, 255, 255, 0.8);
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

/* Stats Cards - Dark Theme */
.stats {
  display: flex;
  gap: 15px;
  flex-wrap: wrap;
}

.stat-card {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px);
  border: 2px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 16px 20px;
  display: flex;
  align-items: center;
  gap: 14px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
  transition: all 0.3s ease;
  min-width: 180px;
}

.stat-card:hover {
  transform: translateY(-2px);
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(102, 126, 234, 0.4);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3);
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
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
}

.stat-online .stat-icon {
  background: linear-gradient(135deg, #48bb78 0%, #38a169 100%);
  box-shadow: 0 4px 15px rgba(72, 187, 120, 0.4);
}

.stat-offline .stat-icon {
  background: linear-gradient(135deg, #f56565 0%, #e53e3e 100%);
  box-shadow: 0 4px 15px rgba(245, 101, 101, 0.4);
}

.stat-info {
  flex: 1;
}

.stat-label {
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.6);
  font-weight: 600;
  letter-spacing: 0.5px;
  margin-bottom: 4px;
}

.stat-value {
  font-size: 1.875rem;
  font-weight: 700;
  color: white;
  line-height: 1;
  text-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
}

/* Search in Status Panel - Dark Theme */
.search-wrapper {
  position: relative;
  width: 100%;
}

.search-icon {
  position: absolute;
  left: 1rem;
  top: 50%;
  transform: translateY(-50%);
  width: 20px;
  height: 20px;
  color: rgba(255, 255, 255, 0.4);
  pointer-events: none;
}

.search-input {
  width: 100%;
  padding: 0.75rem 3rem 0.75rem 3rem;
  border: 2px solid rgba(255, 255, 255, 0.1);
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  font-size: 0.875rem;
  color: white;
  transition: all 0.3s ease;
}

.search-input::placeholder {
  color: rgba(255, 255, 255, 0.4);
}

.search-input:focus {
  outline: none;
  border-color: #667eea;
  background: rgba(255, 255, 255, 0.08);
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.2);
}

.clear-button {
  position: absolute;
  right: 0.5rem;
  top: 50%;
  transform: translateY(-50%);
  width: 32px;
  height: 32px;
  border: none;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.clear-button:hover {
  background: rgba(255, 255, 255, 0.15);
}

.clear-button svg {
  width: 16px;
  height: 16px;
  color: rgba(255, 255, 255, 0.8);
}

.search-results-info {
  text-align: center;
  margin-top: 8px;
}

.results-count {
  display: inline-block;
  padding: 4px 12px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 600;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
}

/* Search Results Panel - Dark Theme */
.search-results-panel {
  background: rgba(26, 32, 44, 0.95);
  backdrop-filter: blur(20px);
  border-bottom: 2px solid rgba(102, 126, 234, 0.2);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
  max-height: 185px;
  overflow-y: auto;
  z-index: 998;
  position: relative;
}

/* Custom Scrollbar for Search Results Panel */
.search-results-panel::-webkit-scrollbar {
  width: 8px;
}

.search-results-panel::-webkit-scrollbar-track {
  background: rgba(0, 0, 0, 0.2);
  border-radius: 10px;
  margin: 4px 0;
}

.search-results-panel::-webkit-scrollbar-thumb {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 10px;
  box-shadow: 0 0 6px rgba(102, 126, 234, 0.5);
}

.search-results-panel::-webkit-scrollbar-thumb:hover {
  background: linear-gradient(135deg, #7c8ef7 0%, #8b5cb5 100%);
  box-shadow: 0 0 8px rgba(102, 126, 234, 0.8);
}

/* Firefox scrollbar */
.search-results-panel {
  scrollbar-width: thin;
  scrollbar-color: rgba(102, 126, 234, 0.8) rgba(0, 0, 0, 0.2);
}

.results-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 30px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  background: rgba(255, 255, 255, 0.03);
  position: sticky;
  top: 0;
  z-index: 1;
}

.results-header h3 {
  font-size: 1rem;
  color: white;
  font-weight: 600;
  text-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
}

.close-results {
  width: 32px;
  height: 32px;
  border: none;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.close-results:hover {
  background: rgba(255, 255, 255, 0.1);
}

.close-results svg {
  width: 18px;
  height: 18px;
  color: rgba(255, 255, 255, 0.8);
}

.results-list {
  padding: 8px 0;
}

.result-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 30px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.result-item:hover {
  background: rgba(255, 255, 255, 0.05);
}

.result-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.result-icon svg {
  width: 20px;
  height: 20px;
  color: white;
}

.result-info {
  flex: 1;
}

.result-name {
  font-weight: 600;
  color: white;
  font-size: 0.9375rem;
  margin-bottom: 4px;
  text-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
}

.result-details {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.8125rem;
  color: rgba(255, 255, 255, 0.6);
}

.result-ip {
  font-family: 'Courier New', monospace;
  font-weight: 500;
  color: rgba(102, 126, 234, 0.9);
}

.result-separator {
  color: rgba(255, 255, 255, 0.3);
}

.status-indicator {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  flex-shrink: 0;
}

.status-indicator.up {
  background: #10b981;
  box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.2);
  animation: pulse-green 2s ease-in-out infinite;
}

.status-indicator.down {
  background: #ef4444;
  box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.2);
}

/* No Results - Dark Theme */
.no-results {
  background: rgba(26, 32, 44, 0.95);
  backdrop-filter: blur(20px);
  padding: 3rem 2rem;
  text-align: center;
  border-bottom: 2px solid rgba(102, 126, 234, 0.2);
}

.no-results svg {
  width: 64px;
  height: 64px;
  color: rgba(102, 126, 234, 0.4);
  margin: 0 auto 1rem;
}

.no-results h3 {
  font-size: 1.25rem;
  color: white;
  margin-bottom: 0.5rem;
  text-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
}

.no-results p {
  color: rgba(255, 255, 255, 0.6);
  margin-bottom: 1.5rem;
}

.clear-search-button {
  padding: 0.75rem 1.5rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
}

.clear-search-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
}

/* Transitions */
.slide-down-enter-active,
.slide-down-leave-active {
  transition: all 0.3s ease;
}

.slide-down-enter-from {
  opacity: 0;
  transform: translateY(-20px);
}

.slide-down-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* Map Container */
.map-container {
  flex: 1;
  position: relative;
  overflow: hidden;
  z-index: 1;
  border-top: 2px solid rgba(102, 126, 234, 0.2);
}

#map {
  height: 100%;
  width: 100%;
}

/* Responsive Design */
@media (max-width: 1200px) {
  .status-panel {
    flex-wrap: wrap;
  }

  .panel-left {
    flex: 1 1 100%;
    justify-content: space-between;
  }

  .panel-center {
    flex: 1 1 100%;
    max-width: 100%;
    order: 3;
  }

  .stats {
    flex: 1 1 100%;
    justify-content: center;
  }
}

@media (max-width: 1024px) {
  .status-panel {
    flex-direction: column;
    flex-wrap: nowrap;
    align-items: stretch;
    gap: 16px;
    height: auto;
  }

  .panel-left {
    width: 100%;
    flex: 0 0 auto;
    flex-wrap: wrap;
    justify-content: space-between;
  }

  .panel-center {
    width: 100%;
    flex: 0 0 auto;
    max-width: none;
    order: 0 !important;
  }

  .stats {
    width: 100%;
    flex-wrap: nowrap;
    overflow-x: auto;
    justify-content: flex-start;
    gap: 12px;
    padding-bottom: 4px;
    -webkit-overflow-scrolling: touch;
  }
  
  .stat-card {
    min-width: 160px;
    flex: 0 0 auto;
  }

  .search-results-panel {
    max-height: 165px;
  }

  .results-header,
  .result-item {
    padding-left: 20px;
    padding-right: 20px;
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

  .panel-left {
    gap: 15px;
  }

  .legend {
    flex-wrap: wrap;
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
    flex-shrink: 0;
  }

  .stat-icon svg {
    width: 20px;
    height: 20px;
  }

  .stat-value {
    font-size: 1.5rem;
  }

  .search-input {
    font-size: 0.875rem;
    padding: 0.75rem 2.75rem 0.75rem 2.75rem;
  }

  .result-name {
    font-size: 0.875rem;
  }

  .result-details {
    font-size: 0.75rem;
  }
}

@media (max-width: 480px) {
  .panel-title svg {
    width: 20px;
    height: 20px;
  }

  .panel-title h2 {
    font-size: 0.9rem;
  }

  .legend {
    gap: 10px;
  }

  .legend-item {
    font-size: 12px;
  }

  .search-results-panel {
    max-height: 150px;
  }

  .result-item {
    padding: 10px 15px;
  }

  .result-icon {
    width: 36px;
    height: 36px;
  }

  .result-details {
    flex-direction: column;
    align-items: flex-start;
    gap: 2px;
  }

  .result-separator {
    display: none;
  }

  .results-count {
    font-size: 0.7rem;
    padding: 3px 10px;
  }
}
</style>

<style>
/* Global styles for Leaflet popup - Dark Theme */
.leaflet-popup-content-wrapper {
  background: rgba(26, 32, 44, 0.98);
  backdrop-filter: blur(20px);
  border: 2px solid rgba(102, 126, 234, 0.3);
  border-radius: 12px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5);
  padding: 0;
  overflow: hidden;
}

.leaflet-popup-content {
  margin: 0;
  min-width: 250px;
}

.leaflet-popup-tip {
  background: rgba(26, 32, 44, 0.98);
  box-shadow: 0 3px 14px rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(102, 126, 234, 0.3);
}

.popup-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 14px 16px;
  font-weight: 600;
  font-size: 15px;
  text-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
}

.popup-body {
  padding: 16px;
  background: rgba(26, 32, 44, 0.98);
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