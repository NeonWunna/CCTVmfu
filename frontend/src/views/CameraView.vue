<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import logoUrl from '../assets/mfu-logo.png';
import Toast from '../components/ui/Toast.vue';
import ConfirmModal from '../components/ui/ConfirmModal.vue';
import api from '../services/api';

const router = useRouter();
const route = useRoute();
const cameraId = route.params.id;

// ===== STATE =====
const userName = ref("Admin User");
const userRole = ref("Security Administrator");
const showDropdown = ref(false);
const isFullscreen = ref(false);

const toast = ref({
  show: false,
  message: '',
  type: 'info'
});

const confirmModal = ref({
  show: false,
  title: '',
  message: '',
  onConfirm: null,
  loading: false
});

const cameraData = ref({
  id: cameraId,
  name: '',
  location: '',
  ipAddress: '',
  status: 'online',
  imageStatus: 'normal',
  coordinates: '',
  brand: '',
  version: '',
  lastUpdate: '',
  rtspUrl: ''
});

// ===== COMPUTED =====
const userInitials = computed(() =>
  userName.value
    .split(' ')
    .map(n => n[0])
    .join('')
    .toUpperCase()
    .slice(0, 2)
);

// ===== API =====
const fetchCameraDetails = async () => {
  if (!cameraId) return;

  try {
    const { data } = await api.getCamera(cameraId);
      // Map backend status to frontend status
      let mappedStatus = 'online'; // Default
      if (data.status === 'offline') {
        mappedStatus = 'offline';
      } else if (data.status === 'no_signal' || data.status === 'no_rtsp') {
        mappedStatus = 'no_signal';
      } else if (data.status === 'online' && data.image_status === 'blur') {
        mappedStatus = 'blurry';
      } else {
        mappedStatus = data.status;
      }

      cameraData.value = {
        id:          data.id,
        name:        data.name,
        location:    data.location,
        ipAddress:   data.ip_address,
        status:      mappedStatus,
      imageStatus: data.image_status,
      coordinates: data.coordinates,
      brand:       data.brand,
      version:     data.version,
      lastUpdate:  data.last_update,
      rtspUrl:     data.rtsp_url
    };
  } catch (error) {
    console.error('Error fetching camera details:', error);
    showToast('Failed to load camera details', 'error');
  }
};

// ===== TOAST =====
const showToast = (message, type = 'info') => {
  toast.value = { show: true, message, type };
};

const closeToast = () => {
  toast.value = { show: false, message: '', type: 'info' };
};

// ===== PROFILE / NAV =====
const toggleProfileMenu = () => {
  showDropdown.value = !showDropdown.value;
};

const closeDropdown = () => {
  showDropdown.value = false;
};

const hideIframeControls = (event) => {
  try {
    const iframeDoc = event.target.contentDocument || event.target.contentWindow.document;
    if (!iframeDoc) return;
    
    const style = iframeDoc.createElement('style');
    style.innerHTML = `
      video::-webkit-media-controls { display: none !important; }
      video { pointer-events: none; }
      .info { display: none !important; }
    `;
    iframeDoc.head.appendChild(style);

    const removeControls = () => {
      iframeDoc.querySelectorAll('video').forEach(v => {
        v.removeAttribute('controls');
        v.controls = false;
      });
    };
    
    removeControls();
    
    const observer = new MutationObserver(removeControls);
    if (iframeDoc.body) {
      observer.observe(iframeDoc.body, { childList: true, subtree: true });
    }
  } catch (e) {
    console.warn("Could not hide iframe controls:", e);
  }
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

// ===== FULLSCREEN =====
const enterFullscreen = (el) =>
  (el.requestFullscreen ?? el.webkitRequestFullscreen)?.call(el);

const exitFullscreen = () =>
  (document.exitFullscreen ?? document.webkitExitFullscreen)?.call(document);

const FULLSCREEN_EVENTS = ['fullscreenchange', 'webkitfullscreenchange'];

const handleFullscreenChange = () => {
  isFullscreen.value = !!document.fullscreenElement;
};

const toggleFullscreen = () => {
  document.fullscreenElement
    ? exitFullscreen()
    : enterFullscreen(document.querySelector('.video-container'));
};

// ===== LIFECYCLE =====
onMounted(() => {
  fetchCameraDetails();
  FULLSCREEN_EVENTS.forEach(ev => document.addEventListener(ev, handleFullscreenChange));
});

onBeforeUnmount(() => {
  FULLSCREEN_EVENTS.forEach(ev => document.removeEventListener(ev, handleFullscreenChange));
});
</script>

<template>
  <div class="camera-view-container">
    <Toast
      :show="toast.show"
      :message="toast.message"
      :type="toast.type"
      @close="closeToast"
    />

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
        <!-- Sidebar -->
        <aside class="sidebar">
          <button class="back-button" @click="goBack">
            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"></path>
            </svg>
            Back to Dashboard
          </button>

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
                {{ 
                  cameraData.status === 'offline' ? 'Offline' : 
                  (cameraData.status === 'blurry' ? 'Blurry' : 
                  (cameraData.status === 'no_signal' ? 'No Signal' : 'Online')) 
                }}
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
            </div>
          </div>
        </aside>

        <!-- Video -->
        <section class="video-section">
          <div class="video-container">
            <div v-if="!cameraData.rtspUrl" class="video-placeholder">
              <div class="placeholder-content">
                <div class="camera-icon-large">
                  <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"></path>
                  </svg>
                  <div class="scan-line-large"></div>
                </div>
                <h3>Video Stream Unavailable</h3>
                <p class="connect-target">Connect to: {{ cameraData.ipAddress }}</p>
                <p class="no-rtsp">No RTSP URL available for this camera.</p>
              </div>
              <div class="scan-overlay"></div>
            </div>

            <iframe
              v-else
              :src="`/stream/stream.html?src=${encodeURIComponent(cameraData.rtspUrl)}`"
              class="video-stream"
              title="Live Camera Feed"
              frameborder="0"
              allowfullscreen
              scrolling="no"
              @error="e => e.target.style.display = 'none'"
              @load="hideIframeControls"
            ></iframe>

            <button class="fullscreen-btn" @click="toggleFullscreen" :title="isFullscreen ? 'Exit Fullscreen' : 'Enter Fullscreen'">
              <svg v-if="!isFullscreen" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4"></path>
              </svg>
              <svg v-else fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 9l6 6m0-6l-6 6m12-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
              </svg>
            </button>
          </div>
        </section>
      </div>
    </main>
  </div>
</template>

<style scoped>
/* ===== RESET ===== */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

/* ===== PAGE ===== */
.camera-view-container {
  min-height: 100vh;
  background: linear-gradient(135deg, rgba(26, 32, 44, 0.95) 0%, rgba(45, 55, 72, 0.98) 100%);
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  position: relative;
}
.camera-view-container::before {
  content: '';
  position: absolute;
  inset: 0;
  background:
    radial-gradient(circle at 20% 30%, rgba(102, 126, 234, 0.1) 0%, transparent 50%),
    radial-gradient(circle at 80% 70%, rgba(118, 75, 162, 0.1) 0%, transparent 50%);
  pointer-events: none;
}

/* ===== HEADER ===== */
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

/* ===== PROFILE ===== */
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

/* ===== DROPDOWN ===== */
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
  inset: 0;
  z-index: 999;
}

/* ===== TRANSITIONS ===== */
.dropdown-enter-active,
.dropdown-leave-active {
  transition: all 0.3s ease;
}
.dropdown-enter-from,
.dropdown-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

/* ===== LAYOUT ===== */
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

/* ===== SIDEBAR ===== */
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

/* ===== INFO CARD ===== */
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
.info-header h3 {
  color: white;
  font-size: 1.25rem;
  font-weight: 700;
  margin-bottom: 0.75rem;
  text-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
}

/* Camera icon + scan */
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
  0%, 100% { top: -100%; opacity: 0; }
  10%      { opacity: 1; }
  90%      { opacity: 1; }
  100%     { top: 200%; opacity: 0; }
}

/* Status badge */
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

@keyframes pulse-dot {
  0%, 100% { box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.2); }
  50%      { box-shadow: 0 0 0 6px rgba(16, 185, 129, 0.1); }
}

@keyframes pulse-blue {
  0%, 100% {
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.2);
  }
  50% {
    box-shadow: 0 0 0 6px rgba(59, 130, 246, 0.1);
  }
}

.status-badge.online {
  background: rgba(16, 185, 129, 0.15);
  color: #10b981;
  border-color: rgba(16, 185, 129, 0.3);
}
.status-badge.offline {
  background: rgba(239, 68, 68, 0.15);
  color: #ef4444;
  border-color: rgba(239, 68, 68, 0.3);
}
.status-badge.blurry {
  background: rgba(249, 115, 22, 0.15);
  color: #f97316;
  border-color: rgba(249, 115, 22, 0.3);
}

.status-badge.online .status-dot {
  background: #10b981;
  box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.2);
  animation: pulse-dot 2s ease-in-out infinite;
}
.status-badge.offline .status-dot {
  background: #ef4444;
}
.status-badge.blurry .status-dot {
  background: #f97316;
  box-shadow: 0 0 0 3px rgba(249, 115, 22, 0.2);
  animation: pulse-dot 2s ease-in-out infinite;
}
.status-badge.no_signal .status-dot {
  background: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.2);
  animation: pulse-blue 2s ease-in-out infinite;
}

/* Info rows */
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
  transition: background 0.2s ease;
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
.info-value.ip-address {
  font-family: 'Courier New', monospace;
  color: rgba(102, 126, 234, 0.9);
}

/* ===== VIDEO SECTION ===== */
.video-section {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}
.video-container {
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(10px);
  border: 2px solid rgba(102, 126, 234, 0.3);
  border-radius: 16px;
  overflow: hidden;
  position: relative;
  aspect-ratio: 16 / 9;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
}

/* Placeholder (no RTSP) */
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
  position: relative;
  z-index: 2;
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
.placeholder-content .connect-target {
  color: rgba(102, 126, 234, 0.9);
  font-size: 1.125rem;
  font-family: 'Courier New', monospace;
  margin-bottom: 0.5rem;
}
.placeholder-content .no-rtsp {
  color: rgba(255, 255, 255, 0.5);
  font-size: 0.9375rem;
}

/* Horizontal scan overlay — uses a pseudo-element so translateY
   stays relative to .video-container, not the viewport */
.scan-overlay {
  position: absolute;
  inset: 0;
  pointer-events: none;
  z-index: 1;
  overflow: hidden;
}
.scan-overlay::after {
  content: '';
  position: absolute;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(90deg, transparent, rgba(102, 126, 234, 0.8), transparent);
  animation: scan-vertical 4s linear infinite;
}
@keyframes scan-vertical {
  0%   { top: 0%; }
  100% { top: 100%; }
}

/* Live stream */
.video-stream {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

/* ===== FULLSCREEN BUTTON ===== */
.fullscreen-btn {
  position: absolute;
  bottom: 1.5rem;
  right: 1.5rem;
  padding: 0.75rem;
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(10px);
  border: 2px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  color: white;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10;
}
.fullscreen-btn:hover {
  background: rgba(102, 126, 234, 0.8);
  border-color: rgba(102, 126, 234, 0.5);
  transform: scale(1.1);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}
.fullscreen-btn svg {
  width: 24px;
  height: 24px;
}

/* ===== RESPONSIVE: TABLET ===== */
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
  .info-card {
    flex: 1;
    min-width: 250px;
  }
}

/* ===== RESPONSIVE: MOBILE ===== */
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
  .placeholder-content .connect-target {
    font-size: 0.9375rem;
  }
}
@media (max-width: 480px) {
  .sidebar {
    flex-direction: column;
  }
  .info-card {
    width: 100%;
  }
}
</style>