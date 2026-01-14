<template>
  <div class="cctv-app">
    <div class="header">
      <div class="logo-container">
        <img :src="logoSrc" alt="MFU Logo" class="logo" @error="handleLogoError">
        <div class="header-text">
          <h1>CCTV Monitoring System</h1>
          <p>Mae Fah Luang University - Real-time Surveillance</p>
        </div>
      </div>

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
    </div>

    <div class="dropdown-overlay" :class="{ show: showDropdown }" @click="closeDropdown"></div>

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

    <div class="map-container">
      <div id="map" ref="mapContainer"></div>
    </div>
  </div>
</template>

<script>
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import mfuLogo from '../assets/mfu-logo.png';

export default {
  name: 'CctvMonitoring',
  data() {
    return {
      userName: 'Admin User',
      userRole: 'Security Administrator',
      showDropdown: false,
      cctvs: [
        {
          name: 'Main Gate CCTV',
          lat: 20.045,
          lng: 99.8925,
          status: 'up',
          location: 'Main Entrance',
          lastUpdate: '2 min ago',
        },
        {
          name: 'Library CCTV',
          lat: 20.0442,
          lng: 99.8945,
          status: 'up',
          location: 'Central Library',
          lastUpdate: '1 min ago',
        },
        {
          name: 'Dormitory CCTV',
          lat: 20.0435,
          lng: 99.8952,
          status: 'down',
          location: 'Student Housing',
          lastUpdate: '15 min ago',
        },
        {
          name: 'Parking Lot CCTV',
          lat: 20.0455,
          lng: 99.8935,
          status: 'up',
          location: 'Parking Area A',
          lastUpdate: 'Just now',
        },
        {
          name: 'Sports Complex CCTV',
          lat: 20.0438,
          lng: 99.892,
          status: 'up',
          location: 'Athletic Center',
          lastUpdate: '3 min ago',
        },
      ],
      map: null,
      logoSrc: mfuLogo,
    };
  },
  computed: {
    onlineCount() {
      return this.cctvs.filter((c) => c.status === 'up').length;
    },
    offlineCount() {
      return this.cctvs.filter((c) => c.status === 'down').length;
    },
    totalCount() {
      return this.cctvs.length;
    },
    userInitials() {
      return this.userName
        .split(' ')
        .map((n) => n[0])
        .join('')
        .toUpperCase()
        .slice(0, 2);
    },
  },
  methods: {
    toggleProfileMenu() {
      this.showDropdown = !this.showDropdown;
    },
    closeDropdown() {
      this.showDropdown = false;
    },
    goToProfile() {
      alert('Navigate to Profile page');
      this.closeDropdown();
    },
    goToSettings() {
      alert('Navigate to Settings page');
      this.closeDropdown();
    },
    viewActivity() {
      alert('View Activity Log');
      this.closeDropdown();
    },
    logout() {
      if (confirm('Are you sure you want to logout?')) {
        alert('Logging out...');
        this.closeDropdown();
      }
    },
    handleLogoError(event) {
      event.target.style.display = 'none';
    },
    initMap() {
      this.map = L.map(this.$refs.mapContainer, {
        zoomControl: true,
        attributionControl: true,
      }).setView([20.0443, 99.8937], 16);

      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors',
        maxZoom: 19,
      }).addTo(this.map);

      this.cctvs.forEach((cctv) => {
        this.addMarker(cctv);
      });
    },
    addMarker(cctv) {
      const color = cctv.status === 'up' ? '#10b981' : '#ef4444';
      const statusText = cctv.status === 'up' ? 'Online' : 'Offline';

      const marker = L.circleMarker([cctv.lat, cctv.lng], {
        radius: 10,
        color,
        fillColor: color,
        fillOpacity: 0.8,
        weight: 3,
      }).addTo(this.map);

      const popupContent = `
        <div class="popup-header">${cctv.name}</div>
        <div class="popup-body">
            <div class="popup-status">
                <span class="status-badge ${cctv.status}">
                    <span class="legend-dot ${cctv.status}"></span>
                    ${statusText}
                </span>
            </div>
            <div class="popup-info">
                <div class="popup-info-item">
                    <span class="popup-info-label">Location:</span>
                    <span>${cctv.location}</span>
                </div>
                <div class="popup-info-item">
                    <span class="popup-info-label">Last Update:</span>
                    <span>${cctv.lastUpdate}</span>
                </div>
                <div class="popup-info-item">
                    <span class="popup-info-label">Coordinates:</span>
                    <span>${cctv.lat.toFixed(4)}, ${cctv.lng.toFixed(4)}</span>
                </div>
            </div>
        </div>
      `;

      marker.bindPopup(popupContent, {
        maxWidth: 300,
        className: 'custom-popup',
      });

      if (cctv.status === 'down') {
        setInterval(() => {
          marker.setStyle({ fillOpacity: marker.options.fillOpacity === 0.8 ? 0.3 : 0.8 });
        }, 1000);
      }
    },
  },
  mounted() {
    this.initMap();
  },
};
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

.cctv-app {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  background-color: #f8f9fa;
  color: #2c3e50;
  display: flex;
  flex-direction: column;
  height: 100vh;
}

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
}

.header-text p {
  font-size: 14px;
  opacity: 0.9;
  font-weight: 400;
}

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
  z-index: 1000;
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

.map-container {
  flex: 1;
  position: relative;
  overflow: hidden;
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
:global(.leaflet-popup-content-wrapper) {
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  padding: 0;
  overflow: hidden;
}

:global(.leaflet-popup-content) {
  margin: 0;
  min-width: 200px;
}

:global(.popup-header) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 12px 15px;
  font-weight: 600;
  font-size: 15px;
}

:global(.popup-body) {
  padding: 15px;
}

:global(.popup-status) {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 10px;
}

:global(.status-badge) {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 600;
}

:global(.status-badge.up) {
  background-color: #d1fae5;
  color: #065f46;
}

:global(.status-badge.down) {
  background-color: #fee2e2;
  color: #991b1b;
}

:global(.popup-info) {
  font-size: 13px;
  color: #6b7280;
  line-height: 1.6;
}

:global(.popup-info-item) {
  display: flex;
  justify-content: space-between;
  padding: 4px 0;
}

:global(.popup-info-label) {
  font-weight: 500;
  color: #374151;
}
</style>

