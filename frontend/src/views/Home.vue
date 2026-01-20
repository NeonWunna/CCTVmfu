<script setup>
import { ref, computed, onMounted, onUnmounted, shallowRef, useTemplateRef } from 'vue';
import { useRouter } from 'vue-router';
import L from 'leaflet';
import logoUrl from '../assets/mfu-logo.png';

const router = useRouter();

const userName = ref("Admin User");
const userRole = ref("Security Administrator");
const showDropdown = ref(false);
const cctvs = ref([
  { 
    name: "Main Gate CCTV", 
    lat: 20.0450, 
    lng: 99.8925, 
    status: "up",
    location: "Main Entrance",
    lastUpdate: "2 min ago"
  },
  { 
    name: "Library CCTV", 
    lat: 20.0442, 
    lng: 99.8945, 
    status: "up",
    location: "Central Library",
    lastUpdate: "1 min ago"
  },
  { 
    name: "Dormitory CCTV", 
    lat: 20.0435, 
    lng: 99.8952, 
    status: "down",
    location: "Student Housing",
    lastUpdate: "15 min ago"
  },
  { 
    name: "Parking Lot CCTV", 
    lat: 20.0455, 
    lng: 99.8935, 
    status: "up",
    location: "Parking Area A",
    lastUpdate: "Just now"
  },
  { 
    name: "Sports Complex CCTV", 
    lat: 20.0438, 
    lng: 99.8920, 
    status: "up",
    location: "Athletic Center",
    lastUpdate: "3 min ago"
  },
  { 
    name: "Cafeteria CCTV", 
    lat: 20.0448, 
    lng: 99.8940, 
    status: "up",
    location: "Student Cafeteria",
    lastUpdate: "1 min ago"
  },
  { 
    name: "Admin Building CCTV", 
    lat: 20.0446, 
    lng: 99.8930, 
    status: "up",
    location: "Administration Office",
    lastUpdate: "4 min ago"
  },
  { 
    name: "Science Building CCTV", 
    lat: 20.0440, 
    lng: 99.8938, 
    status: "up",
    location: "Science Faculty",
    lastUpdate: "2 min ago"
  },
  { 
    name: "Engineering Hall CCTV", 
    lat: 20.0452, 
    lng: 99.8948, 
    status: "down",
    location: "Engineering Building",
    lastUpdate: "20 min ago"
  },
  { 
    name: "East Gate CCTV", 
    lat: 20.0458, 
    lng: 99.8955, 
    status: "up",
    location: "East Entrance",
    lastUpdate: "Just now"
  },
  { 
    name: "West Gate CCTV", 
    lat: 20.0445, 
    lng: 99.8915, 
    status: "up",
    location: "West Entrance",
    lastUpdate: "3 min ago"
  },
  { 
    name: "Parking Area B CCTV", 
    lat: 20.0433, 
    lng: 99.8928, 
    status: "up",
    location: "Parking Lot B",
    lastUpdate: "5 min ago"
  },
  { 
    name: "Student Center CCTV", 
    lat: 20.0447, 
    lng: 99.8942, 
    status: "up",
    location: "Student Activities Center",
    lastUpdate: "2 min ago"
  },
  { 
    name: "Basketball Court CCTV", 
    lat: 20.0436, 
    lng: 99.8918, 
    status: "up",
    location: "Outdoor Courts",
    lastUpdate: "6 min ago"
  },
  { 
    name: "Medical Center CCTV", 
    lat: 20.0443, 
    lng: 99.8933, 
    status: "up",
    location: "Health Services",
    lastUpdate: "1 min ago"
  }
]);

// Use shallowRef for Leaflet map instance to avoid deep reactivity performance cost
const map = shallowRef(null);
const mapContainer = useTemplateRef('mapContainer');
const pulseIntervals = [];

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

const toggleProfileMenu = () => {
  showDropdown.value = !showDropdown.value;
};

const closeDropdown = () => {
  showDropdown.value = false;
};

const goToCameraSettings = () => {
  path: '/camera-settings',
  name: 'CameraSettings',
  component: () => import('@/views/CameraSettings.vue'),
  meta: { requiresAuth: true }
  closeDropdown();
};

const logout = () => {
  if (confirm('Are you sure you want to logout?')) {
    localStorage.removeItem('isAuthenticated');
    closeDropdown();
    router.push('/login');
  }
};

const handleLogoError = (event) => {
  // Fallback if logo image doesn't exist
  event.target.style.display = 'none';
};

const viewCamera = (cctvName) => {
  alert(`Opening camera view for: ${cctvName}`);
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
  }).addTo(map.value);

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
      // Check if map and marker still exist to avoid errors on component unmount
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

  // Add CCTV markers
  cctvs.value.forEach(cctv => {
    addMarker(cctv);
  });
};

onMounted(() => {
  initMap();
});

onUnmounted(() => {
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
    <!-- Header -->
    <div class="header">
      <div class="logo-container">
        <img :src="logoUrl" alt="MFU Logo" class="logo" @error="handleLogoError">
        <div class="header-text">
          <h1>CCTV Monitoring System</h1>
          <p>Mae Fah Luang University - Real-time Surveillance</p>
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

    <!-- Status Panel -->
    <div class="status-panel">
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

      <div class="stats">
        <div class="stat-card">
          <div>
            <div class="stat-value up">{{ onlineCount }}</div>
            <div class="stat-label">Online</div>
          </div>
        </div>
        <div class="stat-card">
          <div>
            <div class="stat-value down">{{ offlineCount }}</div>
            <div class="stat-label">Offline</div>
          </div>
        </div>
        <div class="stat-card">
          <div>
            <div class="stat-value" style="color: #667eea;">{{ totalCount }}</div>
            <div class="stat-label">Total</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Map -->
    <div class="map-container">
      <div ref="mapContainer" id="map"></div>
    </div>
  </div>
</template>

<style scoped>
/* Dashboard Container */
.dashboard-container {
    display: flex;
    flex-direction: column;
    height: 100vh;
    width: 100vw;
    background-color: #f8f9fa;
    color: #2c3e50;
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
    z-index: 1001; /* Ensure header is above map */
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

/* Profile Dropdown Menu */
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

/* Overlay */
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

/* Status Panel */
.status-panel {
    background: white;
    padding: 15px 30px;
    border-bottom: 1px solid #e5e7eb;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 20px;
    flex-wrap: wrap;
    flex-shrink: 0;
    z-index: 1000;
    position: relative;
}

.legend {
    display: flex;
    align-items: center;
    gap: 25px;
}

.legend-item {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 14px;
    font-weight: 500;
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
}

.legend-dot.down {
    background-color: #ef4444;
    box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.2);
}

/* Stats Cards */
.stats {
    display: flex;
    gap: 15px;
}

.stat-card {
    background: #f8f9fa;
    padding: 10px 20px;
    border-radius: 8px;
    display: flex;
    align-items: center;
    gap: 10px;
    border: 1px solid #e5e7eb;
}

.stat-value {
    font-size: 24px;
    font-weight: 700;
    line-height: 1;
}

.stat-value.up {
    color: #10b981;
}

.stat-value.down {
    color: #ef4444;
}

.stat-label {
    font-size: 12px;
    color: #6b7280;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.5px;
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

@media (max-width: 768px) {
    .header {
        padding: 15px 20px;
        flex-wrap: wrap;
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

    .profile-section {
        width: 100%;
        margin-left: 0;
        margin-top: 10px;
        justify-content: center;
    }

    .profile-dropdown {
        right: 20px;
        left: 20px;
        min-width: auto;
    }

    .status-panel {
        padding: 12px 20px;
        flex-direction: column;
        align-items: flex-start;
    }

    .stats {
        width: 100%;
        justify-content: space-between;
    }

    .stat-card {
        flex: 1;
        justify-content: center;
    }
}
</style>

<style>
/* Global styles for Leaflet popup that can't be scoped easily */
.leaflet-popup-content-wrapper {
    border-radius: 12px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
    padding: 0;
    overflow: hidden;
}

.leaflet-popup-content {
    margin: 0;
    min-width: 200px;
}

.popup-header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 12px 15px;
    font-weight: 600;
    font-size: 15px;
}

.popup-body {
    padding: 15px;
}
</style>