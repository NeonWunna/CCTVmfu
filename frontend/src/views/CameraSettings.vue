<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';
import logoUrl from '../assets/mfu-logo.png';
import Toast from '../components/ui/Toast.vue';
import ConfirmModal from '../components/ui/ConfirmModal.vue';
import LoadingSpinner from '../components/ui/LoadingSpinner.vue';
import AppHeader from '../components/dashboard/AppHeader.vue';
import StatsCards from '../components/dashboard/StatsCards.vue';
import api from '../services/api';

const router = useRouter();

const userName = ref('Admin User');
const userRole = ref('Security Administrator');
const searchQuery = ref('');
const showAddModal = ref(false);
const isEditMode = ref(false);
const editingCameraId = ref(null);
const isRefreshing = ref(false);
const showFilterDropdown = ref(false);
const selectedFilter = ref('all');

const toast = ref({ show: false, message: '', type: 'info' });
const confirmModal = ref({ show: false, title: '', message: '', onConfirm: null, loading: false });
const validationErrors = ref({});

const newCamera = ref({
  name: '',
  location: '',
  ipAddress: '',
  rtspUrl: '',
  latitude: '',
  longitude: '',
  brand: '',
  version: '',
  status: 'offline'
});

const cameras = ref([]);

const fetchCameras = async () => {
  try {
    const response = await api.getCameras();
    if (Array.isArray(response.data)) {
      cameras.value = response.data.map((camera) => {
        let mappedStatus = 'online';
        if (camera.status === 'offline') {
          mappedStatus = 'offline';
        } else if (camera.status === 'no_signal' || camera.status === 'no_rtsp') {
          mappedStatus = 'no_signal';
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
          originalStatus: camera.status
        };
      });
    } else {
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

const onlineCount = computed(() => cameras.value.filter((camera) => camera.status === 'online').length);
const offlineCount = computed(() => cameras.value.filter((camera) => camera.status === 'offline').length);
const noSignalCount = computed(() => cameras.value.filter((camera) => camera.status === 'no_signal').length);
const blurryCount = computed(() => cameras.value.filter((camera) => camera.status === 'blurry').length);
const totalCount = computed(() => cameras.value.length);

const filteredCameras = computed(() => {
  const query = searchQuery.value.trim().toLowerCase();
  let filtered = cameras.value;

  if (query) {
    filtered = filtered.filter((camera) =>
      (camera.name || '').toLowerCase().includes(query) ||
      (camera.location || '').toLowerCase().includes(query) ||
      (camera.ipAddress || '').toLowerCase().includes(query)
    );
  }

  if (selectedFilter.value === 'online') {
    filtered = filtered.filter((camera) => camera.status === 'online');
  } else if (selectedFilter.value === 'offline') {
    filtered = filtered.filter((camera) => camera.status === 'offline');
  } else if (selectedFilter.value === 'no_signal') {
    filtered = filtered.filter((camera) => camera.status === 'no_signal');
  } else if (selectedFilter.value === 'blurry') {
    filtered = filtered.filter((camera) => camera.status === 'blurry');
  }

  return [...filtered].sort((a, b) => (a.name || '').localeCompare(b.name || ''));
});

const filterOptions = [
  { value: 'all', label: 'All Cameras', icon: 'all' },
  { value: 'online', label: 'Online', icon: 'online' },
  { value: 'offline', label: 'Offline', icon: 'offline' },
  { value: 'no_signal', label: 'No Signal', icon: 'no_signal' },
  { value: 'blurry', label: 'Blurry', icon: 'blurry' }
];

const currentFilterLabel = computed(() => {
  const option = filterOptions.find((opt) => opt.value === selectedFilter.value);
  return option ? option.label : 'All Cameras';
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

  if (!newCamera.value.name.trim()) errors.name = 'Camera name is required';
  if (!newCamera.value.location.trim()) errors.location = 'Location is required';

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

const toggleFilterDropdown = () => {
  showFilterDropdown.value = !showFilterDropdown.value;
};

const handleClickOutside = (event) => {
  const filterButton = document.querySelector('.filter-button-container');
  const filterDropdown = document.querySelector('.filter-dropdown');

  if (
    showFilterDropdown.value &&
    filterButton &&
    !filterButton.contains(event.target) &&
    filterDropdown &&
    !filterDropdown.contains(event.target)
  ) {
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

const goToCameraSettings = () => {
  router.push('/camera-settings');
};

const logout = () => {
  confirmModal.value = {
    show: true,
    title: 'Confirm Logout',
    message: 'Are you sure you want to logout?',
    loading: false,
    onConfirm: () => {
      localStorage.removeItem('isAuthenticated');
      confirmModal.value.show = false;
      router.push('/login');
      showToast('Logged out successfully', 'info');
    }
  };
};

const editCamera = (camera) => {
  isEditMode.value = true;
  editingCameraId.value = camera.id;

  let lat = '';
  let long = '';

  if (camera.coordinates) {
    const parts = camera.coordinates.split(',').map((s) => s.trim());
    if (parts.length >= 2) {
      lat = parts[0];
      long = parts[1];
    }
  }

  newCamera.value = {
    name: camera.name,
    location: camera.location,
    ipAddress: camera.ipAddress,
    rtspUrl: camera.rtspUrl || '',
    latitude: lat,
    longitude: long,
    brand: camera.brand,
    version: camera.version || '',
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
  name: '',
  location: '',
  ipAddress: '',
  rtspUrl: '',
  latitude: '',
  longitude: '',
  brand: '',
  version: '',
  status: 'offline'
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
    (key) => newCamera.value[key] !== EMPTY_CAMERA[key]
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
    version: newCamera.value.version || '',
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

const handleKeyDown = (event) => {
  if (event.key === 'Escape' && showAddModal.value) closeModal();
  if (event.key === 'Escape' && showFilterDropdown.value) showFilterDropdown.value = false;
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
  <div class="dashboard-page">
    <Toast :show="toast.show" :message="toast.message" :type="toast.type" @close="closeToast" />

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

    <AppHeader
      :logo-url="logoUrl"
      :user-name="userName"
      :user-role="userRole"
      :show-mobile-filters-button="false"
      @camera-settings="goToCameraSettings"
      @logout="logout"
    />

    <section class="stats-strip">
      <StatsCards
        :total="totalCount"
        :online="onlineCount"
        :offline="offlineCount"
        :no-signal="noSignalCount"
        :blurry="blurryCount"
        :selected-filter="selectedFilter"
        :loading="false"
        @select-filter="selectFilter"
      />
    </section>

    <section class="workspace">
      <section class="main-area">
        <header class="inventory-header">
          <div class="inventory-title">
            <h2>Camera Inventory</h2>
            <p>Manage and monitor all CCTV cameras across campus.</p>
          </div>

          <div class="inventory-controls">
            <button class="btn btn-ghost back-btn" @click="goToDashboard">
              <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
              </svg>
              Dashboard
            </button>

            <div class="search-filter-group">
              <div class="search-box">
                <svg class="search-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
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
                <button class="filter-button" :class="{ active: selectedFilter !== 'all' }" @click="toggleFilterDropdown">
                  <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
                  </svg>
                  <span>{{ currentFilterLabel }}</span>
                  <svg class="filter-arrow" :class="{ open: showFilterDropdown }" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
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
                      <svg v-if="option.icon === 'all'" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" /></svg>
                      <svg v-else-if="option.icon === 'online'" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                      <svg v-else-if="option.icon === 'offline'" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                      <svg v-else-if="option.icon === 'no_signal'" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636" /></svg>
                      <svg v-else-if="option.icon === 'blurry'" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" /></svg>
                      <span>{{ option.label }}</span>
                    </button>
                  </div>
                </transition>
              </div>
            </div>
