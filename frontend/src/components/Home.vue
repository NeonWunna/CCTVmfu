<script setup>
import { ref, computed, onMounted, onUnmounted, shallowRef, useTemplateRef } from 'vue';
import L from 'leaflet';
import logoUrl from '../assets/mfu-logo.png';
import '../assets/home.css';

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

const goToProfile = () => {
  alert('Navigate to Profile page');
  closeDropdown();
};

const goToSettings = () => {
  alert('Navigate to Settings page');
  closeDropdown();
};

const viewActivity = () => {
  alert('View Activity Log');
  closeDropdown();
};

const logout = () => {
  if (confirm('Are you sure you want to logout?')) {
    alert('Logging out...');
    closeDropdown();
    // Add your logout logic here
  }
};

const handleLogoError = (event) => {
  // Fallback if logo image doesn't exist
  event.target.style.display = 'none';
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
  map.value = L.map(mapContainer.value, {
    zoomControl: true,
    attributionControl: true
  }).setView([20.0443, 99.8937], 16);

  // Use a more professional map tile
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors',
    maxZoom: 19
  }).addTo(map.value);

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
    map.value.remove();
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
          <button class="dropdown-item" @click="goToProfile">
            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path>
            </svg>
            My Profile
          </button>
          <button class="dropdown-item" @click="goToSettings">
            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"></path>
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
            </svg>
            Settings
          </button>
          <button class="dropdown-item" @click="viewActivity">
            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
            </svg>
            Activity Log
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
