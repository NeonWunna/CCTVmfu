<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';
import logoUrl from '../assets/mfu-logo.png';
import Toast from '../components/ui/Toast.vue';
import ConfirmModal from '../components/ui/ConfirmModal.vue';
import api from '../services/api';
import LoadingSpinner from '../components/ui/LoadingSpinner.vue';

const router = useRouter();

const userName = ref("Admin User");
const userRole = ref("Security Administrator");
const showDropdown = ref(false);
const searchQuery = ref("");
const showAddModal = ref(false);
const isEditMode = ref(false);
const editingCameraId = ref(null);
const isRefreshing = ref(false);

// Filter state
const showFilterDropdown = ref(false);
const selectedFilter = ref("all"); // "all", "online", "offline"

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

// Form validation errors
const validationErrors = ref({});

const newCamera = ref({
  name: "",
  location: "",
  ipAddress: "",
  rtspUrl: "",
  latitude: "",
  longitude: "",
  brand: "",
  version: "",
  status: "offline"
});

const cameras = ref([]);

const fetchCameras = async () => {
  try {
    const response = await api.getCameras();
    if (Array.isArray(response.data)) {
      cameras.value = response.data.map(camera => {
        // Map backend status to frontend status
        let mappedStatus = 'online'; // Default
        if (camera.status === 'offline') {
          mappedStatus = 'offline';
        } else if (camera.status === 'no_signal') {
          mappedStatus = 'no_signal';
        } else if (camera.status === 'no_rtsp') {
          mappedStatus = 'no_rtsp';
        } else if (camera.status === 'online' && camera.image_status === 'blur') {
          mappedStatus = 'blurry';
        } else {
          mappedStatus = camera.status;
        }
        
        return {
          ...camera,
          ipAddress: camera.ip_address,
          rtspUrl: camera.rtsp_url,
          lastUpdate: camera.last_update,
          status: mappedStatus,
          originalStatus: camera.status // Keep original for editing if needed
        };
      });
    } else {
      console.warn('API returned non-array data:', response.data);
      cameras.value = [];
    }
  } catch (error) {
    console.error('Error fetching cameras:', error);
    showToast('Failed to load cameras', 'error');
  }
};

const refreshStatus = async () => {
  isRefreshing.value = true;
  try {
    await api.checkAllCamerasStatus();
    await fetchCameras();
    showToast('Camera statuses updated', 'success');
  } catch (error) {
    console.error('Error refreshing status:', error);
    showToast('Failed to refresh status', 'error');
  } finally {
    isRefreshing.value = false;
  }
};

let pollInterval = null;

onMounted(() => {
  document.addEventListener('keydown', handleKeyDown);
  document.addEventListener('click', handleClickOutside);
  fetchCameras();
  pollInterval = setInterval(fetchCameras, 10000);
});

onUnmounted(() => {
  document.removeEventListener('keydown', handleKeyDown);
  document.removeEventListener('click', handleClickOutside);
  if (pollInterval) clearInterval(pollInterval);
});

const userInitials = computed(() =>
  userName.value
    .split(' ')
    .map(n => n[0])
    .join('')
    .toUpperCase()
    .slice(0, 2)
);

const onlineCount = computed(() => cameras.value.filter(c => c.status === "online" || c.status === "blurry").length);
const offlineCount = computed(() => cameras.value.filter(c => c.status === "offline").length);
const noSignalCount = computed(() => cameras.value.filter(c => c.status === "no_signal").length);
const noRtspCount = computed(() => cameras.value.filter(c => c.status === "no_rtsp").length);
const totalCount = computed(() => cameras.value.length);

const filteredCameras = computed(() => {
  let filtered = cameras.value;

  // Apply search filter
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase();
    filtered = filtered.filter(camera =>
      camera.name.toLowerCase().includes(query) ||
      camera.location.toLowerCase().includes(query) ||
      camera.ipAddress.toLowerCase().includes(query)
    );
  }

  // Apply status filter
  if (selectedFilter.value === "online") {
    filtered = filtered.filter(c => c.status === "online" || c.status === "blurry");
  } else if (selectedFilter.value === "offline") {
    filtered = filtered.filter(c => c.status === "offline");
  } else if (selectedFilter.value === "no_signal") {
    filtered = filtered.filter(c => c.status === "no_signal");
  } else if (selectedFilter.value === "no_rtsp") {
    filtered = filtered.filter(c => c.status === "no_rtsp");
  }

  return filtered.sort((a, b) => {
    // Sort offline to bottom typically, or grouping
    if (a.status === 'online' && b.status === 'offline') return -1;
    if (a.status === 'offline' && b.status === 'online') return 1;
    return 0;
  });
});

const filterOptions = [
  { value: "all", label: "All Cameras", icon: "all" },
  { value: "online", label: "Online Only", icon: "online" },
  { value: "no_signal", label: "No Signal", icon: "no_signal" },
  { value: "no_rtsp", label: "No RTSP", icon: "no_rtsp" },
  { value: "offline", label: "Offline Only", icon: "offline" }
];

const currentFilterLabel = computed(() => {
  const option = filterOptions.find(opt => opt.value === selectedFilter.value);
  return option ? option.label : "All Cameras";
});

const showToast = (message, type = 'info') => {
  toast.value = { show: true, message, type };
};

const closeToast = () => {
  toast.value = { show: false, message: '', type: 'info' };
};

const validateIPAddress = (ip) => {
  const pattern = /^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/;
  return pattern.test(ip);
};

const validateForm = () => {
  const errors = {};

  if (!newCamera.value.name.trim()) {
    errors.name = 'Camera name is required';
  }
  if (!newCamera.value.location.trim()) {
    errors.location = 'Location is required';
  }
  if (!newCamera.value.ipAddress.trim()) {
    errors.ipAddress = 'IP address is required';
  } else if (!validateIPAddress(newCamera.value.ipAddress)) {
    errors.ipAddress = 'Invalid IP address format';
  }
  if (newCamera.value.latitude && isNaN(parseFloat(newCamera.value.latitude))) {
    errors.latitude = 'Latitude must be a number';
  }
  if (newCamera.value.longitude && isNaN(parseFloat(newCamera.value.longitude))) {
    errors.longitude = 'Longitude must be a number';
  }

  validationErrors.value = errors;
  return Object.keys(errors).length === 0;
};

const toggleProfileMenu = () => {
  showDropdown.value = !showDropdown.value;
  showFilterDropdown.value = false;
};

const toggleFilterDropdown = () => {
  showFilterDropdown.value = !showFilterDropdown.value;
  showDropdown.value = false;
};

const closeDropdown = () => {
  showDropdown.value = false;
};

const closeFilterDropdown = () => {
  showFilterDropdown.value = false;
};

const handleClickOutside = (event) => {
  const filterButton = document.querySelector('.filter-button-container');
  const filterDropdown = document.querySelector('.filter-dropdown');
  
  if (showFilterDropdown.value && 
      filterButton && 
      !filterButton.contains(event.target) &&
      filterDropdown &&
      !filterDropdown.contains(event.target)) {
    showFilterDropdown.value = false;
  }
};

const selectFilter = (value) => {
  selectedFilter.value = value;
  showFilterDropdown.value = false;
  handleSearch();
};

const goToDashboard = () => {
  router.push('/');
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

const editCamera = (camera) => {
  isEditMode.value = true;
  editingCameraId.value = camera.id;

  let lat = "";
  let long = "";

  if (camera.coordinates) {
    const parts = camera.coordinates.split(',').map(s => s.trim());
    if (parts.length >= 2) {
      lat = parts[0];
      long = parts[1];
    }
  }

  newCamera.value = {
    name: camera.name,
    location: camera.location,
    ipAddress: camera.ipAddress,
    rtspUrl: camera.rtspUrl || "",
    latitude: lat,
    longitude: long,
    brand: camera.brand,
    version: camera.version || "",
    status: camera.status
  };
  validationErrors.value = {};
  showAddModal.value = true;
};

const removeCamera = (camera) => {
  confirmModal.value = {
    show: true,
    title: 'Delete Camera',
    message: `Are you sure you want to delete ${camera.name}? This action cannot be undone.`,
    type: 'danger',
    loading: false,
    onConfirm: async () => {
      confirmModal.value.loading = true;
      try {
        await api.deleteCamera(camera.id);
        await fetchCameras();
        showToast('Camera deleted successfully', 'success');
        confirmModal.value.show = false;
      } catch (error) {
        console.error('Error deleting camera:', error);
        showToast('Failed to delete camera', 'error');
      } finally {
        confirmModal.value.loading = false;
      }
    }
  };
};

const EMPTY_CAMERA = {
  name: "",
  location: "",
  ipAddress: "",
  rtspUrl: "",
  latitude: "",
  longitude: "",
  brand: "",
  version: "",
  status: "offline"
};

const resetForm = () => {
  isEditMode.value = false;
  editingCameraId.value = null;
  newCamera.value = { ...EMPTY_CAMERA };
  validationErrors.value = {};
};

const addNewCamera = () => {
  resetForm();
  showAddModal.value = true;
};

const closeModal = () => {
  const hasChanges = Object.keys(EMPTY_CAMERA).some(
    key => newCamera.value[key] !== EMPTY_CAMERA[key]
  );

  if (hasChanges && !isEditMode.value) {
    confirmModal.value = {
      show: true,
      title: 'Discard Changes?',
      message: 'You have unsaved changes. Are you sure you want to close without saving?',
      onConfirm: () => {
        showAddModal.value = false;
        confirmModal.value.show = false;
        resetForm();
      }
    };
  } else {
    showAddModal.value = false;
    resetForm();
  }
};

const saveCamera = async () => {
  if (!validateForm()) {
    showToast('Please fill in the required information!', 'error');
    return;
  }

  confirmModal.value.loading = true;

  const payload = {
    name: newCamera.value.name,
    location: newCamera.value.location,
    ip_address: newCamera.value.ipAddress,
    rtsp_url: newCamera.value.rtspUrl,
    latitude: newCamera.value.latitude ? parseFloat(newCamera.value.latitude) : 0,
    longitude: newCamera.value.longitude ? parseFloat(newCamera.value.longitude) : 0,
    brand: newCamera.value.brand,
    version: newCamera.value.version || "",
    status: newCamera.value.status
  };

  try {
    if (isEditMode.value) {
      await api.updateCamera(editingCameraId.value, payload);
      await fetchCameras();
      showToast('Camera updated successfully', 'success');
    } else {
      const response = await api.createCamera(payload);
      cameras.value.unshift({
        ...response.data,
        ipAddress: response.data.ip_address,
        rtspUrl: response.data.rtsp_url,
        lastUpdate: response.data.last_update
      });
      showToast('Camera added successfully', 'success');
    }
    showAddModal.value = false;
    resetForm();
  } catch (error) {
    console.error('Error saving camera:', error);
    showToast('IP address already exists!', 'error');
  } finally {
    confirmModal.value.loading = false;
  }
};

const handleConfirmCancel = () => {
  confirmModal.value.show = false;
  confirmModal.value.loading = false;
};

const handleKeyDown = (e) => {
  if (e.key === 'Escape' && showAddModal.value) {
    closeModal();
  }
  if (e.key === 'Escape' && showFilterDropdown.value) {
    showFilterDropdown.value = false;
  }
};

const handleSearch = () => {
  setTimeout(() => {
    const firstRow = document.querySelector('.camera-table tbody tr:first-child');
    if (firstRow) {
      firstRow.scrollIntoView({ behavior: 'smooth', block: 'start', inline: 'nearest' });
      const mainArea = document.querySelector('.main-area');
      if (mainArea) {
        mainArea.scrollTop = mainArea.scrollTop - 170;
      }
    }
  }, 0);
};
</script>

<template>
  <div class="page-container">
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
      @cancel="handleConfirmCancel"
      @close="handleConfirmCancel"
    />

    <!-- Header -->
    <header class="header">
      <div class="header-content">
        <div class="header-left">
          <img :src="logoUrl" alt="MFU Logo" class="logo" @error="handleLogoError">
          <div class="header-text">
            <h1>Camera Management</h1>
            <p>Mae Fah Luang University - Security System</p>
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
                <button class="dropdown-item">
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
        <aside class="sidebar">
          <button class="back-button" @click="goToDashboard">
            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"></path>
            </svg>
            Dashboard
          </button>

          <div class="stats-container">
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

            <div class="stat-card stat-no_signal" style="border-bottom: 2px solid #3b82f6;">
              <div class="stat-icon" style="background: rgba(59, 130, 246, 0.15); color: #3b82f6;">
                <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636"></path>
                </svg>
              </div>
              <div class="stat-info">
                <div class="stat-label">NO SIGNAL</div>
                <div class="stat-value">{{ noSignalCount }}</div>
              </div>
            </div>

            <div class="stat-card stat-no_rtsp" style="border-bottom: 2px solid #06b6d4;">
              <div class="stat-icon" style="background: rgba(6, 182, 212, 0.15); color: #06b6d4;">
                 <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"></path>
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 6l12 12"></path>
                 </svg>
              </div>
              <div class="stat-info">
                <div class="stat-label">NO RTSP</div>
                <div class="stat-value">{{ noRtspCount }}</div>
              </div>
            </div>
          </div>
        </aside>

        <!-- Main Area -->
        <section class="main-area">
          <div class="inventory-header">
            <div class="inventory-title">
              <h2>Camera Inventory</h2>
              <p>Manage and monitor all CCTV cameras across campus</p>
            </div>

            <div class="inventory-controls">
              <div class="search-filter-group">
                <div class="search-box">
                  <svg class="search-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
                  </svg>
                  <input
                    v-model="searchQuery"
                    @input="handleSearch"
                    type="text"
                    placeholder="Search by name, location, or IP address..."
                    class="search-input"
                    aria-label="Search cameras"
                  >
                </div>

                <div class="filter-button-container">
                  <button class="filter-button" @click="toggleFilterDropdown" :class="{ active: selectedFilter !== 'all' }">
                    <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z"></path>
                    </svg>
                    <span class="filter-text">{{ currentFilterLabel }}</span>
                    <svg class="filter-arrow" :class="{ open: showFilterDropdown }" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
                    </svg>
                  </button>

                  <transition name="dropdown">
                    <div v-show="showFilterDropdown" class="filter-dropdown">
                      <button 
                        v-for="option in filterOptions" 
                        :key="option.value"
                        class="filter-option"
                        :class="{ active: selectedFilter === option.value }"
                        @click="selectFilter(option.value)"
                      >
                        <svg v-if="option.icon === 'all'" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"></path>
                        </svg>
                        <svg v-else-if="option.icon === 'online'" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                        </svg>
                        <svg v-else-if="option.icon === 'offline'" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                        </svg>
                        <svg v-else-if="option.icon === 'no_signal'" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636"></path>
                        </svg>
                        <svg v-else-if="option.icon === 'no_rtsp'" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                           <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"></path>
                           <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 6l12 12"></path>
                        </svg>
                        <span>{{ option.label }}</span>
                        <svg v-if="selectedFilter === option.value" class="check-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                        </svg>
                      </button>
                    </div>
                  </transition>
                </div>
              </div>

              <button class="btn btn-secondary refresh-btn" @click="refreshStatus" :disabled="isRefreshing">
                <svg v-if="!isRefreshing" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
                </svg>
                <LoadingSpinner v-else size="sm" />
                <span style="margin-left: 0.5rem">Check Status</span>
              </button>

              <button class="btn btn-primary" @click="addNewCamera">
                <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path>
                </svg>
                Add Camera
              </button>
            </div>
          </div>

          <!-- Camera Table -->
          <div v-if="filteredCameras.length === 0" class="empty-state">
            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
            </svg>
            <h3>No cameras found</h3>
            <p>Try adjusting your search or filter criteria</p>
          </div>

          <div v-else class="table-container">
            <table class="camera-table">
              <thead>
                <tr>
                  <th>Status</th>
                  <th>Camera Name</th>
                  <th>Location</th>
                  <th>IP Address</th>
                  <th>RTSP URL</th>
                  <th>Coordinates</th>
                  <th>Brand</th>
                  <th>Version</th>
                  <th>Last Update</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="camera in filteredCameras" :key="camera.id" class="camera-row">
                  <td data-label="Status">
                    <span class="status-badge" :class="camera.status">
                      <span class="status-dot"></span>
                      {{ 
                        camera.status === 'offline' ? 'Offline' : 
                        (camera.status === 'blurry' ? 'Blurry' : 
                        (camera.status === 'no_signal' ? 'No Signal' : 
                        (camera.status === 'no_rtsp' ? 'No RTSP' : 'Online'))) 
                      }}
                    </span>
                  </td>
                  <td data-label="Camera Name">
                    <div class="camera-name-cell">
                      <div class="camera-icon-small">
                        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"></path>
                        </svg>
                      </div>
                      <span class="camera-name-text">{{ camera.name }}</span>
                    </div>
                  </td>
                  <td data-label="Location">{{ camera.location }}</td>
                  <td data-label="IP Address"><span class="ip-address">{{ camera.ipAddress }}</span></td>
                  <td data-label="RTSP URL">
                    <span class="rtsp-url" :title="camera.rtspUrl">{{ camera.rtspUrl ? (camera.rtspUrl.length > 20 ? camera.rtspUrl.substring(0, 20) + '...' : camera.rtspUrl) : '-' }}</span>
                  </td>
                  <td data-label="Coordinates">{{ camera.coordinates || '-' }}</td>
                  <td data-label="Brand">{{ camera.brand || '-' }}</td>
                  <td data-label="Version">{{ camera.version || '-' }}</td>
                  <td data-label="Last Update">{{ camera.lastUpdate || '-' }}</td>
                  <td data-label="Actions">
                    <div class="table-actions">
                      <button class="action-button-small edit" @click="editCamera(camera)" aria-label="Edit camera">
                        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
                        </svg>
                      </button>
                      <button class="action-button-small delete" @click="removeCamera(camera)" aria-label="Delete camera">
                        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
                        </svg>
                      </button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>
      </div>
    </main>

    <!-- Add/Edit Camera Modal -->
    <transition name="modal">
      <div v-if="showAddModal" class="modal-overlay" @click.self="closeModal">
        <div class="modal-container">
          <div class="modal-header">
            <h3>{{ isEditMode ? 'Edit Camera' : 'Add New Camera' }}</h3>
            <button class="close-button" @click="closeModal" aria-label="Close modal">
              <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
              </svg>
            </button>
          </div>

          <form class="modal-body" @submit.prevent="saveCamera">
            <div class="form-group">
              <label for="camera-name">Camera Name <span class="required">*</span></label>
              <input
                id="camera-name"
                v-model="newCamera.name"
                type="text"
                placeholder="e.g., Main Gate CCTV"
                :class="{ 'error': validationErrors.name }"
              >
              <span v-if="validationErrors.name" class="error-message">{{ validationErrors.name }}</span>
            </div>

            <div class="form-group">
              <label for="camera-location">Location <span class="required">*</span></label>
              <input
                id="camera-location"
                v-model="newCamera.location"
                type="text"
                placeholder="e.g., Main Entrance"
                :class="{ 'error': validationErrors.location }"
              >
              <span v-if="validationErrors.location" class="error-message">{{ validationErrors.location }}</span>
            </div>

            <div class="form-group">
              <label for="camera-ip">IP Address <span class="required">*</span></label>
              <input
                id="camera-ip"
                v-model="newCamera.ipAddress"
                type="text"
                placeholder="e.g., 192.168.1.10"
                :class="{ 'error': validationErrors.ipAddress }"
              >
              <span v-if="validationErrors.ipAddress" class="error-message">{{ validationErrors.ipAddress }}</span>
            </div>

            <div class="form-group">
              <label for="camera-rtsp">RTSP URL</label>
              <input
                id="camera-rtsp"
                v-model="newCamera.rtspUrl"
                type="text"
                placeholder="e.g., rtsp://user:pass@192.168.1.10:554/stream"
              >
            </div>

            <div class="form-row">
              <div class="form-group half">
                <label for="camera-latitude">Latitude</label>
                <input
                  id="camera-latitude"
                  v-model="newCamera.latitude"
                  type="number"
                  step="any"
                  placeholder="e.g., 20.0451"
                  :class="{ 'error': validationErrors.latitude }"
                >
                <span v-if="validationErrors.latitude" class="error-message">{{ validationErrors.latitude }}</span>
              </div>
              <div class="form-group half">
                <label for="camera-longitude">Longitude</label>
                <input
                  id="camera-longitude"
                  v-model="newCamera.longitude"
                  type="number"
                  step="any"
                  placeholder="e.g., 99.8825"
                  :class="{ 'error': validationErrors.longitude }"
                >
                <span v-if="validationErrors.longitude" class="error-message">{{ validationErrors.longitude }}</span>
              </div>
            </div>

            <div class="form-group">
              <label for="camera-brand">Brand</label>
              <select id="camera-brand" v-model="newCamera.brand">
                <option value="">Select Brand</option>
                <option value="Hikvision">Hikvision</option>
                <option value="Dahua">Dahua</option>
                <option value="Axis">Axis</option>
                <option value="Uniview">Uniview</option>
                <option value="Other">Other</option>
              </select>
            </div>

            <div class="form-group">
              <label for="camera-version">Firmware Version</label>
              <input
                id="camera-version"
                v-model="newCamera.version"
                type="text"
                placeholder="e.g., V5.7.3"
              >
            </div>

            <div class="modal-footer">
              <button type="button" class="button-secondary" @click="closeModal">Cancel</button>
              <button type="submit" class="button-primary">
                {{ isEditMode ? 'Update Camera' : 'Add Camera' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </transition>
  </div>
</template>

<style scoped>
/* ===== RESET ===== */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
  scrollbar-width: thin;
  scrollbar-color: rgba(102, 126, 234, 0.7) rgba(0, 0, 0, 0.2);
}

::-webkit-scrollbar {
  width: 10px;
  height: 10px;
}
::-webkit-scrollbar-track {
  background: rgba(0, 0, 0, 0.2);
  border-radius: 10px;
}
::-webkit-scrollbar-thumb {
  background: linear-gradient(180deg, rgba(102, 126, 234, 0.7) 0%, rgba(118, 75, 162, 0.7) 100%);
  border-radius: 10px;
  border: 2px solid rgba(26, 32, 44, 0.4);
}
::-webkit-scrollbar-thumb:hover {
  background: linear-gradient(180deg, rgba(102, 126, 234, 0.9) 0%, rgba(118, 75, 162, 0.9) 100%);
  box-shadow: 0 0 10px rgba(102, 126, 234, 0.5);
}
::-webkit-scrollbar-thumb:active {
  background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
  box-shadow: 0 0 15px rgba(102, 126, 234, 0.7);
}

/* ===== PAGE ===== */
.page-container {
  min-height: 100vh;
  background: linear-gradient(135deg, rgba(26, 32, 44, 0.95) 0%, rgba(45, 55, 72, 0.98) 100%);
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  position: relative;
  overflow-x: hidden;
  width: 100%;
}
.page-container::before {
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

/* ===== LAYOUT ===== */
.main-content {
  max-width: 100%;
  margin: 0 auto;
  padding: 2rem;
  position: relative;
  z-index: 1;
}
.content-wrapper {
  display: grid;
  grid-template-columns: 280px 1fr;
  gap: 2rem;
  min-height: calc(100vh - 200px);
}

/* ===== SIDEBAR ===== */
.sidebar {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  position: sticky;
  top: 0;
  height: fit-content;
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

/* ===== STATS ===== */
.stats-container {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}
.stat-card {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px);
  border: 2px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 1.25rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
  transition: all 0.3s ease;
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
}
.stat-value {
  font-size: 1.75rem;
  font-weight: 700;
  color: white;
  margin-top: 0.25rem;
  text-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
}

/* ===== MAIN AREA ===== */
.main-area {
  background: rgba(26, 32, 44, 0.9);
  backdrop-filter: blur(20px);
  border: 2px solid rgba(102, 126, 234, 0.2);
  border-radius: 16px;
  padding: 0;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
  overflow: auto;
  max-height: calc(100vh - 200px);
  display: flex;
  flex-direction: column;
  position: relative;
}

/* ===== INVENTORY HEADER ===== */
.inventory-header {
  position: sticky;
  top: 0;
  z-index: 10;
  background: rgba(26, 32, 44, 1);
  backdrop-filter: blur(20px) saturate(180%);
  margin: 0;
  padding: 1.5rem 2rem;
  border-bottom: 2px solid rgba(102, 126, 234, 0.3);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
  flex-shrink: 0;
  border-radius: 16px 16px 0 0;
}
.inventory-title h2 {
  font-size: 1.75rem;
  color: white;
  font-weight: 700;
  margin-bottom: 0.5rem;
  text-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
}
.inventory-title p {
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.875rem;
}
.inventory-controls {
  display: flex;
  gap: 1rem;
  margin-top: 1.5rem;
  flex-wrap: wrap;
}

/* ===== SEARCH & FILTER GROUP ===== */
.search-filter-group {
  display: flex;
  gap: 0.5rem;
  flex: 1;
  min-width: 300px;
}

.search-box {
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
  color: rgba(255, 255, 255, 0.4);
}
.search-input {
  width: 100%;
  padding: 0.75rem 1rem 0.75rem 3rem;
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

/* ===== FILTER BUTTON ===== */
.filter-button-container {
  position: relative;
}

.filter-button {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px);
  border: 2px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  color: rgba(255, 255, 255, 0.8);
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  white-space: nowrap;
}

.filter-button:hover {
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(102, 126, 234, 0.4);
  color: white;
}

.filter-button.active {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.2) 0%, rgba(118, 75, 162, 0.2) 100%);
  border-color: rgba(102, 126, 234, 0.5);
  color: #667eea;
}

.filter-button svg {
  width: 18px;
  height: 18px;
  flex-shrink: 0;
}

.filter-text {
  display: inline-block;
}

.filter-arrow {
  width: 16px;
  height: 16px;
  transition: transform 0.3s ease;
}

.filter-arrow.open {
  transform: rotate(180deg);
}

/* ===== FILTER DROPDOWN ===== */
.filter-dropdown {
  position: absolute;
  top: calc(100% + 0.5rem);
  right: 0;
  background: rgba(26, 32, 44, 0.98);
  backdrop-filter: blur(20px);
  border: 2px solid rgba(102, 126, 234, 0.3);
  border-radius: 12px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5);
  min-width: 220px;
  overflow: hidden;
  z-index: 1000;
  padding: 0.5rem;
}

.filter-option {
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
  position: relative;
}

.filter-option:hover {
  background: rgba(102, 126, 234, 0.2);
  color: white;
}

.filter-option.active {
  background: rgba(102, 126, 234, 0.3);
  color: white;
}

.filter-option svg {
  width: 18px;
  height: 18px;
  flex-shrink: 0;
}

.filter-option .check-icon {
  margin-left: auto;
  color: #10b981;
}

/* ===== BUTTONS ===== */
.btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  white-space: nowrap;
}
.btn svg {
  width: 20px;
  height: 20px;
  flex-shrink: 0;
}
.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
.btn:disabled:hover {
  transform: none;
  box-shadow: none;
}
.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
}
.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
}
.btn-secondary {
  background: linear-gradient(135deg, #4a5568 0%, #2d3748 100%);
  color: white;
  box-shadow: 0 4px 15px rgba(74, 85, 104, 0.4);
}
.btn-secondary:hover:not(:disabled) {
  background: linear-gradient(135deg, #2d3748 0%, #1a202c 100%);
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(74, 85, 104, 0.5);
}

/* ===== EMPTY STATE ===== */
.empty-state {
  text-align: center;
  padding: 4rem 2rem;
  margin: 0 2rem 2rem;
  color: rgba(255, 255, 255, 0.4);
}
.empty-state svg {
  width: 64px;
  height: 64px;
  margin: 0 auto 1rem;
}
.empty-state h3 {
  font-size: 1.5rem;
  color: rgba(255, 255, 255, 0.7);
  margin-bottom: 0.5rem;
}
.empty-state p {
  color: rgba(255, 255, 255, 0.5);
}

/* ===== TABLE ===== */
.table-container {
  padding: 0 2rem 2rem;
  overflow-x: auto;
  flex-shrink: 0;
  width: 100%;
}

.camera-table {
  width: 100%;
  min-width: 1400px;
  border-collapse: separate;
  border-spacing: 0;
}
.camera-table thead {
  background: rgba(26, 32, 44, 1);
  position: sticky;
  top: 0;
  z-index: 9;
}
.camera-table thead th {
  padding: 1rem 0.75rem;
  text-align: left;
  font-weight: 700;
  font-size: 0.875rem;
  color: white;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  border-bottom: 2px solid rgba(102, 126, 234, 0.3);
  white-space: nowrap;
}
.camera-table tbody tr {
  background: rgba(255, 255, 255, 0.03);
  transition: all 0.3s ease;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}
.camera-table tbody tr:hover {
  background: rgba(255, 255, 255, 0.08);
  transform: scale(1.005);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}
.camera-table tbody td {
  padding: 1rem 0.75rem;
  color: rgba(255, 255, 255, 0.8);
  font-size: 0.875rem;
  vertical-align: middle;
}
/* ===== TABLE CELL CONTENT ===== */
.camera-name-cell {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}
.camera-icon-small {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.camera-icon-small svg {
  width: 20px;
  height: 20px;
  color: white;
}
.camera-name-text {
  font-weight: 600;
  color: white;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.ip-address {
  font-family: 'Courier New', monospace;
  color: rgba(102, 126, 234, 0.9);
  font-weight: 500;
}
.rtsp-url {
  font-family: 'Courier New', monospace;
  font-size: 0.8rem;
  color: rgba(255, 255, 255, 0.7);
}

/* ===== STATUS BADGE ===== */
.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 600;
  border: 1px solid;
  white-space: nowrap;
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
.status-badge.no_signal {
  background: rgba(59, 130, 246, 0.15);
  color: #3b82f6;
  border-color: rgba(59, 130, 246, 0.3);
}
.status-badge.no_rtsp {
  background: rgba(6, 182, 212, 0.15);
  color: #06b6d4;
  border-color: rgba(6, 182, 212, 0.3);
}
.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}
.status-badge.online .status-dot {
  background: #10b981;
  box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.2);
  animation: pulse-dot 2s ease-in-out infinite;
}
.status-badge.offline .status-dot {
  background: #ef4444;
  box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.2);
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
.status-badge.no_rtsp .status-dot {
  background: #06b6d4;
  box-shadow: 0 0 0 3px rgba(6, 182, 212, 0.2);
}

@keyframes pulse-blue {
  0%, 100% {
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.2);
  }
  50% {
    box-shadow: 0 0 0 6px rgba(59, 130, 246, 0.1);
  }
}
@keyframes pulse-dot {
  0%, 100% { opacity: 1; transform: scale(1); }
  50%      { opacity: 0.7; transform: scale(1.1); }
}

/* ===== TABLE ACTIONS ===== */
.table-actions {
  display: flex;
  gap: 0.5rem;
  justify-content: flex-start;
}
.action-button-small {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2px solid;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s ease;
  background: rgba(255, 255, 255, 0.03);
  flex-shrink: 0;
}
.action-button-small svg {
  width: 18px;
  height: 18px;
}
.action-button-small.edit {
  border-color: rgba(102, 126, 234, 0.5);
  color: #667eea;
}
.action-button-small.edit:hover {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-color: transparent;
  color: white;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
}
.action-button-small.delete {
  border-color: rgba(239, 68, 68, 0.5);
  color: #ef4444;
}
.action-button-small.delete:hover {
  background: #ef4444;
  border-color: transparent;
  color: white;
  box-shadow: 0 4px 15px rgba(239, 68, 68, 0.4);
}

/* ===== MODAL ===== */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.8);
  backdrop-filter: blur(10px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1050;
  padding: 1rem;
}
.modal-container {
  background: rgba(26, 32, 44, 0.98);
  backdrop-filter: blur(20px);
  border: 2px solid rgba(102, 126, 234, 0.3);
  border-radius: 16px;
  max-width: 600px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
  position: relative;
  z-index: 1051;
}
.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem 2rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}
.modal-header h3 {
  font-size: 1.5rem;
  color: white;
  font-weight: 700;
  text-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
}
.close-button {
  width: 40px;
  height: 40px;
  border: none;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}
.close-button:hover {
  background: rgba(255, 255, 255, 0.1);
}
.close-button svg {
  width: 20px;
  height: 20px;
  color: rgba(255, 255, 255, 0.8);
}
.modal-body {
  padding: 2rem;
}

/* ===== FORM ===== */
.form-group {
  margin-bottom: 1.5rem;
}
.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}
.form-group.half {
  margin-bottom: 0;
}
.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  color: white;
  font-weight: 600;
  font-size: 0.875rem;
}
.required {
  color: #ef4444;
}
.form-group input,
.form-group select {
  width: 100%;
  padding: 0.75rem 1rem;
  border: 2px solid rgba(255, 255, 255, 0.1);
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px);
  border-radius: 8px;
  font-size: 0.875rem;
  color: white;
  transition: all 0.3s ease;
}
.form-group select option {
  background: rgba(26, 32, 44, 0.98);
  color: white;
  padding: 0.5rem;
}
.form-group input::placeholder {
  color: rgba(255, 255, 255, 0.4);
}
.form-group input:focus,
.form-group select:focus {
  outline: none;
  border-color: #667eea;
  background: rgba(255, 255, 255, 0.08);
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.2);
}
.form-group input.error {
  border-color: #ef4444;
}
.error-message {
  display: block;
  margin-top: 0.5rem;
  color: #ef4444;
  font-size: 0.75rem;
}

/* ===== MODAL FOOTER ===== */
.modal-footer {
  display: flex;
  gap: 1rem;
  padding-top: 1.5rem;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}
.modal-footer .button-secondary,
.modal-footer .button-primary {
  flex: 1;
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}
.modal-footer .button-secondary {
  background: rgba(255, 255, 255, 0.05);
  color: rgba(255, 255, 255, 0.8);
  border: 2px solid rgba(255, 255, 255, 0.1);
}
.modal-footer .button-secondary:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.2);
}
.modal-footer .button-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
}
.modal-footer .button-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
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
.modal-enter-active,
.modal-leave-active {
  transition: all 0.3s ease;
}
.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}
.modal-enter-from .modal-container,
.modal-leave-to .modal-container {
  transform: scale(0.9);
}

/* ===== RESPONSIVE: LARGE TABLETS & SMALL LAPTOPS (1200px - 1024px) ===== */
@media (max-width: 1200px) {
  .content-wrapper {
    grid-template-columns: 240px 1fr;
    gap: 1.5rem;
  }
  
  .camera-table {
    min-width: 1200px;
  }
  
  .inventory-controls {
    gap: 0.75rem;
  }
}

/* ===== RESPONSIVE: TABLET LANDSCAPE (1024px - 768px) ===== */
@media (max-width: 1024px) {
  .content-wrapper {
    grid-template-columns: 1fr;
    gap: 1.5rem;
    min-height: auto;
  }
  
  .sidebar {
    position: static;
    flex-direction: row;
    flex-wrap: wrap;
    gap: 1rem;
  }
  
  .back-button {
    width: auto;
  }
  
  .stats-container {
    flex-direction: row;
    flex: 1;
    gap: 1rem;
  }
  
  .stat-card {
    flex: 1;
    min-width: 150px;
  }
  
  .main-area {
    max-height: none;
  }
  
  .camera-table {
    min-width: 1000px;
  }
}

/* ===== RESPONSIVE: TABLET PORTRAIT (768px - 640px) ===== */
@media (max-width: 768px) {
  .header-content {
    padding: 15px 20px;
  }
  
  .header-text h1 {
    font-size: 18px;
  }
  
  .header-text p {
    display: none;
  }
  
  .profile-info {
    display: none;
  }
  
  .logo {
    height: 45px;
  }
  
  .main-content {
    padding: 1rem;
  }
  
  .stats-container {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 0.75rem;
  }
  
  .stat-card {
    flex-direction: column;
    padding: 1rem;
    text-align: center;
    gap: 0.5rem;
  }
  
  .stat-icon {
    width: 40px;
    height: 40px;
    margin: 0 auto;
  }
  
  .stat-icon svg {
    width: 20px;
    height: 20px;
  }
  
  .stat-label {
    font-size: 0.65rem;
  }
  
  .stat-value {
    font-size: 1.5rem;
  }
  
  .inventory-header {
    padding: 1.25rem 1rem;
  }
  
  .inventory-title h2 {
    font-size: 1.25rem;
  }
  
  .inventory-title p {
    font-size: 0.75rem;
  }
  
  .inventory-controls {
    flex-direction: column;
    gap: 0.75rem;
  }
  
  .search-filter-group {
    flex-direction: column;
    min-width: 0;
    width: 100%;
  }
  
  .search-box {
    min-width: 0;
    width: 100%;
  }
  
  .filter-button-container {
    width: 100%;
  }
  
  .filter-button {
    width: 100%;
    justify-content: space-between;
  }
  
  .filter-dropdown {
    left: 0;
    right: 0;
    width: 100%;
  }
  
  .btn {
    width: 100%;
    justify-content: center;
  }
  
  /* Card-style table for mobile */
  .table-container {
    padding: 0 1rem 1rem;
  }
  
  .camera-table {
    min-width: 0;
  }
  
  .camera-table thead {
    display: none;
  }
  
  .camera-table,
  .camera-table tbody,
  .camera-table tr,
  .camera-table td {
    display: block;
    width: 100%;
  }
  
  .spacer-row {
    display: none;
  }
  
  .camera-table tbody tr {
    margin-bottom: 1rem;
    border-radius: 12px;
    border: 2px solid rgba(255, 255, 255, 0.1);
    padding: 1rem;
    background: rgba(255, 255, 255, 0.05);
  }
  
  .camera-table tbody tr:hover {
    transform: none;
  }
  
  .camera-table tbody td {
    padding: 0.75rem 0;
    border: none;
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 0.875rem;
  }
  
  .camera-table tbody td::before {
    content: attr(data-label);
    font-weight: 700;
    color: rgba(255, 255, 255, 0.6);
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    min-width: 100px;
    flex-shrink: 0;
  }
  
  .camera-table tbody td:first-child {
    padding-top: 0;
  }
  
  .camera-table tbody td:last-child {
    padding-bottom: 0;
    justify-content: flex-end;
  }
  
  .camera-table tbody td:last-child::before {
    display: none;
  }
  
  .camera-name-cell {
    justify-content: flex-end;
  }
  
  .table-actions {
    justify-content: flex-end;
  }
  
  .modal-container {
    margin: 0.5rem;
    width: calc(100% - 1rem);
  }
  
  .modal-header {
    padding: 1rem 1.25rem;
  }
  
  .modal-header h3 {
    font-size: 1.25rem;
  }
  
  .modal-body {
    padding: 1rem 1.25rem;
  }
  
  .form-row {
    grid-template-columns: 1fr;
  }
}

/* ===== RESPONSIVE: MOBILE (below 640px) ===== */
@media (max-width: 640px) {
  .header-content {
    padding: 12px 15px;
  }
  
  .header-text h1 {
    font-size: 16px;
  }
  
  .logo {
    height: 40px;
  }
  
  .profile-section {
    padding: 0.4rem 0.8rem;
  }
  
  .profile-avatar {
    width: 36px;
    height: 36px;
    font-size: 0.8rem;
  }
  
  .main-content {
    padding: 0.75rem;
  }
  
  .stats-container {
    gap: 0.5rem;
  }
  
  .stat-card {
    padding: 0.75rem 0.5rem;
    min-height: 90px;
  }
  
  .stat-icon {
    width: 36px;
    height: 36px;
  }
  
  .stat-icon svg {
    width: 18px;
    height: 18px;
  }
  
  .stat-label {
    font-size: 0.6rem;
  }
  
  .stat-value {
    font-size: 1.25rem;
  }
  
  .inventory-header {
    padding: 1rem 0.75rem;
  }
  
  .inventory-title h2 {
    font-size: 1.1rem;
  }
  
  .inventory-title p {
    font-size: 0.7rem;
  }
  
  .btn {
    padding: 0.65rem 1rem;
    font-size: 0.875rem;
  }
  
  .btn svg {
    width: 18px;
    height: 18px;
  }
  
  .camera-table tbody td {
    font-size: 0.8rem;
    padding: 0.6rem 0;
  }
  
  .camera-table tbody td::before {
    font-size: 0.65rem;
    min-width: 85px;
  }
  
  .camera-icon-small {
    width: 32px;
    height: 32px;
  }
  
  .camera-icon-small svg {
    width: 16px;
    height: 16px;
  }
  
  .status-badge {
    font-size: 0.7rem;
    padding: 0.4rem 0.8rem;
  }
  
  .action-button-small {
    width: 32px;
    height: 32px;
  }
  
  .action-button-small svg {
    width: 16px;
    height: 16px;
  }
}

/* ===== RESPONSIVE: VERY SMALL MOBILE (below 480px) ===== */
@media (max-width: 480px) {
  .header-left {
    gap: 0.5rem;
  }
  
  .logo {
    height: 35px;
  }
  
  .header-text h1 {
    font-size: 14px;
  }
  
  .profile-avatar {
    width: 32px;
    height: 32px;
    font-size: 0.75rem;
  }
  
  .stat-card {
    padding: 0.6rem 0.4rem;
    min-height: 85px;
  }
  
  .stat-icon {
    width: 32px;
    height: 32px;
  }
  
  .stat-icon svg {
    width: 16px;
    height: 16px;
  }
  
  .stat-label {
    font-size: 0.55rem;
  }
  
  .stat-value {
    font-size: 1.1rem;
  }
  
  .camera-table tbody tr {
    padding: 0.75rem;
  }
  
  .camera-table tbody td {
    font-size: 0.75rem;
  }
  
  .camera-table tbody td::before {
    font-size: 0.6rem;
    min-width: 75px;
  }
  
  .modal-container {
    border-radius: 12px;
  }
  
  .modal-header,
  .modal-body {
    padding: 0.875rem 1rem;
  }
  
  .modal-header h3 {
    font-size: 1.1rem;
  }
  
  .form-group {
    margin-bottom: 1.25rem;
  }
}
</style>