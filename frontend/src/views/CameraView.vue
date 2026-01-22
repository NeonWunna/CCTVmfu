<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import logoUrl from '../assets/mfu-logo.png';
import Toast from '../components/ui/Toast.vue';
import ConfirmModal from '../components/ui/ConfirmModal.vue';

const router = useRouter();
const route = useRoute();

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

// Camera data (you can pass this via route params or fetch from API)
const cameraData = ref({
  id: route.params.id || '1',
  name: route.query.name || 'Main Gate CCTV',
  location: route.query.location || 'Main Entrance',
  ipAddress: route.query.ip || '192.168.1.100',
  status: route.query.status || 'up',
  coordinates: route.query.coordinates || '20.0451, 99.8825',
  brand: route.query.brand || 'Hikvision',
  lastUpdate: route.query.lastUpdate || new Date().toLocaleString()
});

const isRecording = ref(true);
const isFullscreen = ref(false);
const videoQuality = ref('HD');

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

const goBack = () => {
  router.push('/');
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

const toggleRecording = () => {
  isRecording.value = !isRecording.value;
  showToast(isRecording.value ? 'Recording started' : 'Recording stopped', 'success');
};

const takeSnapshot = () => {
  showToast('Snapshot captured successfully', 'success');
  // Backend integration: Capture frame from video stream
};

const toggleFullscreen = () => {
  const videoContainer = document.querySelector('.video-container');
  if (!document.fullscreenElement) {
    videoContainer.requestFullscreen();
    isFullscreen.value = true;
  } else {
    document.exitFullscreen();
    isFullscreen.value = false;
  }
};

const changeQuality = (quality) => {
  videoQuality.value = quality;
  showToast(`Video quality changed to ${quality}`, 'info');
  // Backend integration: Change video stream quality
};

onMounted(() => {
  // Backend integration: Initialize video stream here
  console.log('Camera View mounted. Ready for video stream integration.');
  console.log('Camera IP:', cameraData.value.ipAddress);
  
  // Listen for fullscreen changes
  document.addEventListener('fullscreenchange', () => {
    isFullscreen.value = !!document.fullscreenElement;
  });
});
</script>

<template>
  <div class="camera-view-container">
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
            <h1>Live Camera View</h1>
            <p>Mae Fah Luang University - Real-time Surveillance Feed</p>
          </div>
        </div>

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

    <!-- Main Content -->
    <main class="main-content">
      <div class="content-wrapper">
        <!-- Sidebar - Camera Info -->
        <aside class="sidebar">
          <button class="back-button" @click="goBack">
            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"></path>
            </svg>
            Back to Dashboard
          </button>

          <!-- Camera Info Card -->
          <div class="info-card">
            <div class="info-header">
              <div class="camera-icon">
                <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"></path>
                </svg>
                <div class="scan-line"></div>
              </div>
              <h3>{{ cameraData.name }}</h3>
              <span class="status-badge" :class="cameraData.status">
                <span class="status-dot"></span>
                {{ cameraData.status === 'up' ? 'Online' : 'Offline' }}
              </span>
            </div>

            <div class="info-body">
              <div class="info-item">
                <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"></path>
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"></path>
                </svg>
                <div>
                  <div class="info-label">Location</div>
                  <div class="info-value">{{ cameraData.location }}</div>
                </div>
              </div>

              <div class="info-item">
                <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9"></path>
                </svg>
                <div>
                  <div class="info-label">IP Address</div>
                  <div class="info-value ip-address">{{ cameraData.ipAddress }}</div>
                </div>
              </div>

              <div class="info-item">
                <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z"></path>
                </svg>
                <div>
                  <div class="info-label">Brand</div>
                  <div class="info-value">{{ cameraData.brand }}</div>
                </div>
              </div>

              <div class="info-item">
                <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
                <div>
                  <div class="info-label">Last Update</div>
                  <div class="info-value">{{ cameraData.lastUpdate }}</div>
                </div>
              </div>
            </div>
          </div>

          <!-- Recording Status -->
          <div class="recording-card">
            <div class="recording-indicator" :class="{ active: isRecording }">
              <span class="rec-dot"></span>
              <span class="rec-text">{{ isRecording ? 'RECORDING' : 'NOT RECORDING' }}</span>
            </div>
          </div>
        </aside>

        <!-- Video Section -->
        <section class="video-section">
          <!-- Video Controls Bar -->
          <div class="controls-bar">
            <div class="controls-left">
              <h2>Live Feed</h2>
              <span class="quality-badge">{{ videoQuality }}</span>
            </div>
            <div class="controls-right">
              <button class="control-btn" @click="changeQuality('SD')" :class="{ active: videoQuality === 'SD' }">
                <span>SD</span>
              </button>
              <button class="control-btn" @click="changeQuality('HD')" :class="{ active: videoQuality === 'HD' }">
                <span>HD</span>
              </button>
              <button class="control-btn" @click="changeQuality('FHD')" :class="{ active: videoQuality === 'FHD' }">
                <span>FHD</span>
              </button>
              <div class="divider"></div>
              <button class="control-btn" @click="takeSnapshot" title="Take Snapshot">
                <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z"></path>
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 13a3 3 0 11-6 0 3 3 0 016 0z"></path>
                </svg>
              </button>
              <button class="control-btn" @click="toggleRecording" :class="{ active: isRecording }" title="Toggle Recording">
                <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"></path>
                </svg>
              </button>
              <button class="control-btn" @click="toggleFullscreen" title="Fullscreen">
                <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4"></path>
                </svg>
              </button>
            </div>
          </div>

          <!-- Video Container -->
          <div class="video-container">
            <!-- Placeholder for video stream -->
            <!-- Backend integration: Replace this div with actual video element -->
            <div class="video-placeholder">
              <div class="placeholder-content">
                <div class="camera-icon-large">
                  <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"></path>
                  </svg>
                  <div class="scan-line-large"></div>
                </div>
                <h3>Video Stream Ready</h3>
                <p>Connect to: {{ cameraData.ipAddress }}</p>
                <div class="integration-note">
                  <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                  </svg>
                  <span>Backend Integration Point: Insert video stream element here</span>
                </div>
              </div>
              
              <!-- Scanning overlay effect -->
              <div class="scan-overlay"></div>
            </div>

            <!-- Example of where backend developer will add video element:
            <video 
              id="cameraStream" 
              autoplay 
              playsinline
              class="video-stream"
            ></video>
            -->

            <!-- Live indicator -->
            <div class="live-indicator">
              <span class="live-dot"></span>
              <span>LIVE</span>
            </div>

            <!-- Timestamp overlay -->
            <div class="timestamp-overlay">
              {{ new Date().toLocaleString() }}
            </div>
          </div>
        </section>
      </div>
    </main>
  </div>
</template>

<style scoped>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

.camera-view-container {
  min-height: 100vh;
  background: linear-gradient(135deg, rgba(26, 32, 44, 0.95) 0%, rgba(45, 55, 72, 0.98) 100%);
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  position: relative;
}

.camera-view-container::before {
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
}

/* Header - Dark Theme */
.header {
  background: rgba(26, 32, 44, 0.95);
  backdrop-filter: blur(20px);
  box-shadow: 0 2px 20px rgba(0, 0, 0, 0.3), 0 0 0 1px rgba(102, 126, 234, 0.2);
  position: sticky;
  top: 0;
  z-index: 100;
  border-bottom: 2px solid rgba(102, 126, 234, 0.2);
}

.header-content {
  max-width: 1600px;
  margin: 0 auto;
  padding: 20px 30px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 1rem;
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
  text-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
}

.header-text p {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.7);
  margin-top: 0.25rem;
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

/* Dropdown Menu */
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
  z-index: 1000;
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
  z-index: 999;
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

/* Main Content */
.main-content {
  max-width: 1600px;
  margin: 0 auto;
  padding: 2rem;
  position: relative;
  z-index: 1;
}

.content-wrapper {
  display: grid;
  grid-template-columns: 320px 1fr;
  gap: 2rem;
  min-height: calc(100vh - 200px);
}

/* Sidebar */
.sidebar {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.back-button {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px);
  border: 2px solid rgba(102, 126, 234, 0.3);
  border-radius: 12px;
  color: white;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.back-button:hover {
  transform: translateX(-4px);
  background: rgba(102, 126, 234, 0.2);
  border-color: rgba(102, 126, 234, 0.5);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.back-button svg {
  width: 20px;
  height: 20px;
}

/* Info Card */
.info-card {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px);
  border: 2px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  padding: 1.5rem;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
}

.info-header {
  text-align: center;
  margin-bottom: 1.5rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.camera-icon {
  width: 64px;
  height: 64px;
  margin: 0 auto 1rem;
  border-radius: 16px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
}

.camera-icon svg {
  width: 32px;
  height: 32px;
  color: white;
  position: relative;
  z-index: 2;
}

.scan-line {
  position: absolute;
  top: -100%;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.8), transparent);
  animation: scan 3s ease-in-out infinite;
}

@keyframes scan {
  0%, 100% {
    top: -100%;
    opacity: 0;
  }
  10% {
    opacity: 1;
  }
  90% {
    opacity: 1;
  }
  100% {
    top: 200%;
    opacity: 0;
  }
}

.info-header h3 {
  color: white;
  font-size: 1.25rem;
  font-weight: 700;
  margin-bottom: 0.75rem;
  text-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
}

.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 600;
  border: 1px solid;
}

.status-badge.up {
  background: rgba(16, 185, 129, 0.15);
  color: #10b981;
  border-color: rgba(16, 185, 129, 0.3);
}

.status-badge.down {
  background: rgba(239, 68, 68, 0.15);
  color: #ef4444;
  border-color: rgba(239, 68, 68, 0.3);
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.status-badge.up .status-dot {
  background: #10b981;
  box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.2);
  animation: pulse-dot 2s ease-in-out infinite;
}

.status-badge.down .status-dot {
  background: #ef4444;
}

@keyframes pulse-dot {
  0%, 100% {
    box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.2);
  }
  50% {
    box-shadow: 0 0 0 6px rgba(16, 185, 129, 0.1);
  }
}

.info-body {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.info-item {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  padding: 0.75rem;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 8px;
  transition: all 0.2s ease;
}

.info-item:hover {
  background: rgba(255, 255, 255, 0.05);
}

.info-item svg {
  width: 20px;
  height: 20px;
  color: rgba(102, 126, 234, 0.8);
  flex-shrink: 0;
  margin-top: 2px;
}

.info-label {
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.6);
  margin-bottom: 0.25rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.info-value {
  font-size: 0.9375rem;
  color: white;
  font-weight: 500;
}

.ip-address {
  font-family: 'Courier New', monospace;
  color: rgba(102, 126, 234, 0.9);
}

/* Recording Card */
.recording-card {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px);
  border: 2px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 1.25rem;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
}

.recording-indicator {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  padding: 0.75rem;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.03);
}

.recording-indicator.active {
  background: rgba(239, 68, 68, 0.15);
  border: 1px solid rgba(239, 68, 68, 0.3);
}

.rec-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: #6b7280;
}

.recording-indicator.active .rec-dot {
  background: #ef4444;
  box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.2);
  animation: pulse-rec 1.5s ease-in-out infinite;
}

@keyframes pulse-rec {
  0%, 100% {
    box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.2);
  }
  50% {
    box-shadow: 0 0 0 6px rgba(239, 68, 68, 0.1);
  }
}

.rec-text {
  font-size: 0.875rem;
  font-weight: 700;
  letter-spacing: 1px;
  color: rgba(255, 255, 255, 0.6);
}

.recording-indicator.active .rec-text {
  color: #ef4444;
}

/* Video Section */
.video-section {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.controls-bar {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px);
  border: 2px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 1rem 1.5rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
}

.controls-left {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.controls-left h2 {
  color: white;
  font-size: 1.25rem;
  font-weight: 700;
  text-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
}

.quality-badge {
  padding: 0.375rem 0.75rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 6px;
  font-size: 0.75rem;
  font-weight: 700;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
}

.controls-right {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.control-btn {
  padding: 0.625rem 1rem;
  background: rgba(255, 255, 255, 0.05);
  border: 2px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  color: rgba(255, 255, 255, 0.8);
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  font-weight: 600;
}

.control-btn:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(102, 126, 234, 0.4);
  color: white;
}

.control-btn.active {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-color: transparent;
  color: white;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.4);
}

.control-btn svg {
  width: 18px;
  height: 18px;
}

.divider {
  width: 1px;
  height: 24px;
  background: rgba(255, 255, 255, 0.1);
  margin: 0 0.25rem;
}

/* Video Container */
.video-container {
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(10px);
  border: 2px solid rgba(102, 126, 234, 0.3);
  border-radius: 16px;
  overflow: hidden;
  position: relative;
  aspect-ratio: 16/9;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
}

.video-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, rgba(26, 32, 44, 0.9) 0%, rgba(45, 55, 72, 0.9) 100%);
  position: relative;
}

.placeholder-content {
  text-align: center;
  z-index: 2;
  position: relative;
}

.camera-icon-large {
  width: 120px;
  height: 120px;
  margin: 0 auto 1.5rem;
  border-radius: 24px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
  box-shadow: 0 8px 32px rgba(102, 126, 234, 0.4);
}

.camera-icon-large svg {
  width: 60px;
  height: 60px;
  color: white;
  position: relative;
  z-index: 2;
}

.scan-line-large {
  position: absolute;
  top: -100%;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.9), transparent);
  animation: scan 2.5s ease-in-out infinite;
}

.placeholder-content h3 {
  color: white;
  font-size: 1.75rem;
  font-weight: 700;
  margin-bottom: 0.75rem;
  text-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
}

.placeholder-content p {
  color: rgba(102, 126, 234, 0.9);
  font-size: 1.125rem;
  font-family: 'Courier New', monospace;
  margin-bottom: 2rem;
}

.integration-note {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.25rem;
  background: rgba(102, 126, 234, 0.15);
  border: 1px solid rgba(102, 126, 234, 0.3);
  border-radius: 8px;
  color: rgba(255, 255, 255, 0.8);
  font-size: 0.875rem;
}

.integration-note svg {
  width: 18px;
  height: 18px;
  color: rgba(102, 126, 234, 0.8);
}

.scan-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(90deg, transparent, rgba(102, 126, 234, 0.8), transparent);
  animation: scan-horizontal 4s linear infinite;
  z-index: 1;
}

@keyframes scan-horizontal {
  0% {
    transform: translateY(0);
  }
  100% {
    transform: translateY(calc(100vh - 200px));
  }
}

/* Live Indicator */
.live-indicator {
  position: absolute;
  top: 1.5rem;
  left: 1.5rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: rgba(239, 68, 68, 0.9);
  backdrop-filter: blur(10px);
  border-radius: 6px;
  color: white;
  font-size: 0.875rem;
  font-weight: 700;
  letter-spacing: 1px;
  box-shadow: 0 4px 12px rgba(239, 68, 68, 0.4);
  z-index: 10;
}

.live-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: white;
  animation: pulse-live 1s ease-in-out infinite;
}

@keyframes pulse-live {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.4;
  }
}

/* Timestamp Overlay */
.timestamp-overlay {
  position: absolute;
  bottom: 1.5rem;
  right: 1.5rem;
  padding: 0.5rem 1rem;
  background: rgba(0, 0, 0, 0.8);
  backdrop-filter: blur(10px);
  border-radius: 6px;
  color: white;
  font-size: 0.875rem;
  font-family: 'Courier New', monospace;
  border: 1px solid rgba(255, 255, 255, 0.1);
  z-index: 10;
}

/* Video Stream (for backend integration) */
.video-stream {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

/* Responsive Design */
@media (max-width: 1200px) {
  .content-wrapper {
    grid-template-columns: 280px 1fr;
  }
}

@media (max-width: 1024px) {
  .content-wrapper {
    grid-template-columns: 1fr;
  }

  .sidebar {
    flex-direction: row;
    flex-wrap: wrap;
  }

  .info-card,
  .recording-card {
    flex: 1;
    min-width: 250px;
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

  .main-content {
    padding: 1rem;
  }

  .controls-bar {
    flex-direction: column;
    gap: 1rem;
  }

  .controls-left,
  .controls-right {
    width: 100%;
    justify-content: center;
  }

  .controls-right {
    flex-wrap: wrap;
  }

  .camera-icon-large {
    width: 80px;
    height: 80px;
  }

  .camera-icon-large svg {
    width: 40px;
    height: 40px;
  }

  .placeholder-content h3 {
    font-size: 1.25rem;
  }

  .placeholder-content p {
    font-size: 0.9375rem;
  }
}

@media (max-width: 480px) {
  .sidebar {
    flex-direction: column;
  }

  .info-card,
  .recording-card {
    width: 100%;
  }

  .control-btn span {
    display: none;
  }

  .control-btn {
    padding: 0.625rem;
  }
}
</style>