<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../stores/auth';
import logoUrl from '../assets/mfu-logo.png';
import Toast from '../components/ui/Toast.vue';
import ConfirmModal from '../components/ui/ConfirmModal.vue';
import LoadingSpinner from '../components/ui/LoadingSpinner.vue';
import AppHeader from '../components/dashboard/AppHeader.vue';
import StatsCards from '../components/dashboard/StatsCards.vue';
import api from '../services/api';

const router = useRouter();
const authStore = useAuthStore();

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
      authStore.logout();
      confirmModal.value.show = false;
      router.push('/login');
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

            <button class="btn btn-ghost refresh-btn" :disabled="isRefreshing" @click="refreshStatus">
              <svg v-if="!isRefreshing" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              <LoadingSpinner v-else size="sm" />
              <span>Check Status</span>
            </button>

            <button class="btn btn-primary" @click="addNewCamera">
              <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
              </svg>
              Add Camera
            </button>
          </div>
        </header>

        <div v-if="filteredCameras.length === 0" class="empty-state">
          <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
          <h3>No cameras found</h3>
          <p>Try adjusting your search or filter criteria.</p>
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
                    {{ camera.status === 'offline' ? 'Offline' : (camera.status === 'blurry' ? 'Blurry' : (camera.status === 'no_signal' ? 'No Signal' : 'Online')) }}
                  </span>
                </td>
                <td data-label="Camera Name">
                  <div class="camera-name-cell">
                    <div class="camera-icon-small">
                      <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                      </svg>
                    </div>
                    <span class="camera-name-text">{{ camera.name }}</span>
                  </div>
                </td>
                <td data-label="Location">{{ camera.location }}</td>
                <td data-label="IP Address"><span class="ip-address">{{ camera.ipAddress }}</span></td>
                <td data-label="RTSP URL">
                  <span class="rtsp-url" :title="camera.rtspUrl">{{ camera.rtspUrl ? (camera.rtspUrl.length > 30 ? `${camera.rtspUrl.substring(0, 30)}...` : camera.rtspUrl) : '-' }}</span>
                </td>
                <td data-label="Coordinates">{{ camera.coordinates || '-' }}</td>
                <td data-label="Brand">{{ camera.brand || '-' }}</td>
                <td data-label="Version">{{ camera.version || '-' }}</td>
                <td data-label="Last Update">{{ camera.lastUpdate || '-' }}</td>
                <td data-label="Actions">
                  <div class="table-actions">
                    <button class="action-button-small edit" aria-label="Edit camera" @click="editCamera(camera)">
                      <svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" /></svg>
                    </button>
                    <button class="action-button-small delete" aria-label="Delete camera" @click="removeCamera(camera)">
                      <svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" /></svg>
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>
    </section>

    <transition name="modal">
      <div v-if="showAddModal" class="modal-overlay" @click.self="closeModal">
        <div class="modal-container">
          <div class="modal-header">
            <h3>{{ isEditMode ? 'Edit Camera' : 'Add New Camera' }}</h3>
            <button class="close-button" aria-label="Close modal" @click="closeModal">
              <svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" /></svg>
            </button>
          </div>

          <form class="modal-body" @submit.prevent="saveCamera">
            <div class="form-group">
              <label for="camera-name">Camera Name <span class="required">*</span></label>
              <input id="camera-name" v-model="newCamera.name" type="text" placeholder="e.g., Main Gate CCTV" :class="{ error: validationErrors.name }">
              <span v-if="validationErrors.name" class="error-message">{{ validationErrors.name }}</span>
            </div>

            <div class="form-group">
              <label for="camera-location">Location <span class="required">*</span></label>
              <input id="camera-location" v-model="newCamera.location" type="text" placeholder="e.g., Main Entrance" :class="{ error: validationErrors.location }">
              <span v-if="validationErrors.location" class="error-message">{{ validationErrors.location }}</span>
            </div>

            <div class="form-group">
              <label for="camera-ip">IP Address <span class="required">*</span></label>
              <input id="camera-ip" v-model="newCamera.ipAddress" type="text" placeholder="e.g., 192.168.1.10" :class="{ error: validationErrors.ipAddress }">
              <span v-if="validationErrors.ipAddress" class="error-message">{{ validationErrors.ipAddress }}</span>
            </div>

            <div class="form-group">
              <label for="camera-rtsp">RTSP URL</label>
              <input id="camera-rtsp" v-model="newCamera.rtspUrl" type="text" placeholder="e.g., rtsp://user:pass@192.168.1.10:554/stream">
            </div>

            <div class="form-row">
              <div class="form-group">
                <label for="camera-latitude">Latitude</label>
                <input id="camera-latitude" v-model="newCamera.latitude" type="number" step="any" placeholder="e.g., 20.0451" :class="{ error: validationErrors.latitude }">
                <span v-if="validationErrors.latitude" class="error-message">{{ validationErrors.latitude }}</span>
              </div>

              <div class="form-group">
                <label for="camera-longitude">Longitude</label>
                <input id="camera-longitude" v-model="newCamera.longitude" type="number" step="any" placeholder="e.g., 99.8825" :class="{ error: validationErrors.longitude }">
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
              <input id="camera-version" v-model="newCamera.version" type="text" placeholder="e.g., V5.7.3">
            </div>

            <div class="modal-footer">
              <button type="button" class="button-secondary" @click="closeModal">Cancel</button>
              <button type="submit" class="button-primary">{{ isEditMode ? 'Update Camera' : 'Add Camera' }}</button>
            </div>
          </form>
        </div>
      </div>
    </transition>
  </div>
</template>

<style scoped>
.dashboard-page {
  --space-2: 16px;
  --space-3: 24px;
  height: 100vh;
  height: 100dvh;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background:
    radial-gradient(circle at 12% 8%, rgba(14, 165, 233, 0.14), transparent 36%),
    radial-gradient(circle at 86% 0%, rgba(20, 184, 166, 0.12), transparent 38%),
    #020617;
  color: #e2e8f0;
  font-family: 'Trebuchet MS', 'Segoe UI', sans-serif;
}

.stats-strip {
  padding: 12px var(--space-3);
}

.workspace {
  flex: 1;
  min-height: 0;
  padding: 0 var(--space-3) var(--space-3);
  overflow: hidden;
}

.main-area {
  height: 100%;
  min-height: 0;
  border: 1px solid rgba(148, 163, 184, 0.24);
  border-radius: 16px;
  background: rgba(15, 23, 42, 0.74);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.inventory-header {
  padding: 14px 16px;
  border-bottom: 1px solid rgba(148, 163, 184, 0.24);
  background: rgba(15, 23, 42, 0.9);
  display: flex;
  flex-direction: column;
  gap: 14px;
  flex-shrink: 0;
}

.inventory-title h2 {
  margin: 0;
  color: #f8fafc;
  font-size: 1.35rem;
}

.inventory-title p {
  margin: 4px 0 0;
  color: #94a3b8;
  font-size: 0.84rem;
}

.inventory-controls {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
}

.search-filter-group {
  display: flex;
  gap: 8px;
  flex: 1;
  min-width: 320px;
}

.search-box {
  flex: 1;
  min-width: 0;
  position: relative;
}

.search-icon {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  width: 18px;
  height: 18px;
  color: #64748b;
}

.search-input {
  width: 100%;
  height: 40px;
  border: 1px solid rgba(148, 163, 184, 0.28);
  border-radius: 10px;
  background: rgba(2, 6, 23, 0.55);
  color: #e2e8f0;
  padding: 0 12px 0 38px;
  font-size: 0.86rem;
}

.search-input::placeholder {
  color: #64748b;
}

.search-input:focus,
.filter-button:focus-visible,
.btn:focus-visible,
.action-button-small:focus-visible,
.close-button:focus-visible,
.button-secondary:focus-visible,
.button-primary:focus-visible {
  outline: 2px solid #38bdf8;
  outline-offset: 2px;
}

.filter-button-container {
  position: relative;
  flex-shrink: 0;
}

.filter-button {
  height: 40px;
  border: 1px solid rgba(148, 163, 184, 0.28);
  border-radius: 10px;
  background: rgba(15, 23, 42, 0.78);
  color: #e2e8f0;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 0 12px;
  font-size: 0.84rem;
  font-weight: 600;
  cursor: pointer;
}

.filter-button.active {
  border-color: rgba(56, 189, 248, 0.55);
  color: #bfdbfe;
}

.filter-button svg {
  width: 16px;
  height: 16px;
  flex-shrink: 0;
}

.filter-arrow {
  transition: transform 0.18s ease;
}

.filter-arrow.open {
  transform: rotate(180deg);
}

.filter-dropdown {
  position: absolute;
  top: calc(100% + 6px);
  right: 0;
  min-width: 190px;
  border: 1px solid rgba(148, 163, 184, 0.24);
  border-radius: 12px;
  background: rgba(15, 23, 42, 0.96);
  box-shadow: 0 14px 28px rgba(2, 6, 23, 0.45);
  padding: 6px;
  z-index: 20;
}

.filter-option {
  width: 100%;
  border: 0;
  background: transparent;
  color: #cbd5e1;
  border-radius: 8px;
  padding: 8px 10px;
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  font-size: 0.84rem;
}

.filter-option:hover,
.filter-option.active {
  background: rgba(51, 65, 85, 0.52);
}

.filter-option svg {
  width: 15px;
  height: 15px;
  flex-shrink: 0;
}

.btn {
  height: 40px;
  border-radius: 10px;
  border: 1px solid rgba(148, 163, 184, 0.28);
  padding: 0 12px;
  font-size: 0.84rem;
  font-weight: 600;
  color: #e2e8f0;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.btn svg {
  width: 16px;
  height: 16px;
}

.btn:disabled {
  opacity: 0.65;
  cursor: not-allowed;
}

.btn-ghost {
  background: rgba(15, 23, 42, 0.78);
}

.btn-primary {
  border-color: transparent;
  background: linear-gradient(135deg, #0284c7 0%, #0d9488 100%);
  color: #f8fafc;
}

.table-container {
  flex: 1;
  min-height: 0;
  overflow: auto;
  padding: 0 16px 16px;
}

.camera-table {
  width: 100%;
  min-width: 1250px;
  border-collapse: separate;
  border-spacing: 0;
}

.camera-table thead th {
  position: sticky;
  top: 0;
  z-index: 5;
  background: rgba(15, 23, 42, 0.98);
  color: #e2e8f0;
  font-size: 0.78rem;
  font-weight: 700;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  text-align: left;
  padding: 12px 10px;
  border-bottom: 1px solid rgba(148, 163, 184, 0.24);
}

.camera-table tbody td {
  padding: 12px 10px;
  border-bottom: 1px solid rgba(148, 163, 184, 0.15);
  font-size: 0.84rem;
  color: #cbd5e1;
  vertical-align: middle;
}

.camera-table tbody tr:hover {
  background: rgba(30, 41, 59, 0.45);
}

.camera-name-cell {
  display: flex;
  align-items: center;
  gap: 10px;
  min-width: 0;
}

.camera-icon-small {
  width: 30px;
  height: 30px;
  border-radius: 8px;
  background: linear-gradient(135deg, #0ea5e9 0%, #6366f1 100%);
  color: #f8fafc;
  display: grid;
  place-items: center;
  flex-shrink: 0;
}

.camera-icon-small svg {
  width: 14px;
  height: 14px;
}

.camera-name-text {
  color: #f8fafc;
  font-weight: 600;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.ip-address,
.rtsp-url {
  color: #93c5fd;
  font-family: 'Consolas', monospace;
}

.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  border: 1px solid transparent;
  border-radius: 999px;
  padding: 4px 10px;
  font-size: 0.74rem;
  font-weight: 700;
}

.status-dot {
  width: 7px;
  height: 7px;
  border-radius: 999px;
}

.status-badge.online { background: rgba(22, 163, 74, 0.16); border-color: rgba(22, 163, 74, 0.36); color: #86efac; }
.status-badge.online .status-dot { background: #22c55e; }
.status-badge.offline { background: rgba(220, 38, 38, 0.15); border-color: rgba(220, 38, 38, 0.34); color: #fca5a5; }
.status-badge.offline .status-dot { background: #ef4444; }
.status-badge.no_signal { background: rgba(59, 130, 246, 0.16); border-color: rgba(59, 130, 246, 0.36); color: #bfdbfe; }
.status-badge.no_signal .status-dot { background: #3b82f6; }
.status-badge.blurry { background: rgba(249, 115, 22, 0.16); border-color: rgba(249, 115, 22, 0.36); color: #fdba74; }
.status-badge.blurry .status-dot { background: #f97316; }

.table-actions {
  display: flex;
  gap: 8px;
}

.action-button-small {
  width: 34px;
  height: 34px;
  border-radius: 8px;
  border: 1px solid rgba(148, 163, 184, 0.3);
  background: rgba(15, 23, 42, 0.78);
  display: grid;
  place-items: center;
  cursor: pointer;
  color: #cbd5e1;
}

.action-button-small svg {
  width: 16px;
  height: 16px;
}

.action-button-small.edit { border-color: rgba(59, 130, 246, 0.5); color: #93c5fd; }
.action-button-small.delete { border-color: rgba(239, 68, 68, 0.5); color: #fca5a5; }

.empty-state {
  margin: 16px;
  border: 1px dashed rgba(148, 163, 184, 0.3);
  border-radius: 14px;
  padding: 38px 16px;
  text-align: center;
  color: #94a3b8;
}

.empty-state svg {
  width: 40px;
  height: 40px;
  margin-bottom: 8px;
}

.empty-state h3 {
  margin: 0;
  color: #f8fafc;
  font-size: 1rem;
}

.empty-state p {
  margin: 6px 0 0;
  font-size: 0.84rem;
}

.modal-overlay {
  position: fixed;
  inset: 0;
  z-index: 1200;
  background: rgba(2, 6, 23, 0.78);
  backdrop-filter: blur(5px);
  display: grid;
  place-items: center;
  padding: 16px;
}

.modal-container {
  width: min(640px, 100%);
  max-height: 90vh;
  overflow-y: auto;
  border: 1px solid rgba(148, 163, 184, 0.24);
  border-radius: 14px;
  background: rgba(15, 23, 42, 0.96);
  box-sizing: border-box;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 14px 16px;
  border-bottom: 1px solid rgba(148, 163, 184, 0.2);
}

.modal-header h3 { margin: 0; color: #f8fafc; font-size: 1.15rem; }

.close-button {
  width: 34px;
  height: 34px;
  border: 1px solid rgba(148, 163, 184, 0.3);
  border-radius: 10px;
  background: rgba(15, 23, 42, 0.76);
  color: #cbd5e1;
  display: grid;
  place-items: center;
  cursor: pointer;
}

.close-button svg { width: 16px; height: 16px; }

.modal-body { padding: 16px; box-sizing: border-box; overflow: hidden; }
.form-group { margin-bottom: 14px; }
.form-row { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 10px; }
.form-group label { display: block; margin-bottom: 6px; color: #e2e8f0; font-size: 0.82rem; font-weight: 600; }
.required { color: #f87171; }

.form-group input,
.form-group select {
  width: 100%;
  height: 40px;
  border: 1px solid rgba(148, 163, 184, 0.3);
  border-radius: 10px;
  background: rgba(2, 6, 23, 0.56);
  color: #e2e8f0;
  padding: 0 10px;
  font-size: 0.84rem;
  box-sizing: border-box;
}

.form-group input::placeholder { color: #64748b; }
.form-group input.error { border-color: rgba(248, 113, 113, 0.7); }
.error-message { display: block; margin-top: 5px; color: #fca5a5; font-size: 0.75rem; }

.modal-footer {
  margin-top: 18px;
  padding-top: 14px;
  border-top: 1px solid rgba(148, 163, 184, 0.18);
  display: flex;
  gap: 10px;
}

.button-secondary,
.button-primary {
  flex: 1;
  height: 40px;
  border-radius: 10px;
  font-size: 0.84rem;
  font-weight: 600;
  cursor: pointer;
}

.button-secondary { border: 1px solid rgba(148, 163, 184, 0.28); background: rgba(15, 23, 42, 0.76); color: #cbd5e1; }
.button-primary { border: 0; background: linear-gradient(135deg, #0284c7 0%, #0d9488 100%); color: #f8fafc; }

.dropdown-enter-active,
.dropdown-leave-active { transition: opacity 0.16s ease, transform 0.16s ease; }
.dropdown-enter-from,
.dropdown-leave-to { opacity: 0; transform: translateY(-4px); }
.modal-enter-active,
.modal-leave-active { transition: opacity 0.18s ease; }
.modal-enter-from,
.modal-leave-to { opacity: 0; }

@media (max-width: 1199px) {
  .stats-strip { padding: 12px var(--space-2); }
  .workspace { padding: 0 var(--space-2) var(--space-2); }
  .search-filter-group { min-width: 260px; }
  .camera-table { min-width: 1120px; }
}

@media (max-width: 767px) {
  .dashboard-page { height: auto; min-height: 100vh; min-height: 100dvh; overflow: auto; }
  .stats-strip { padding: 10px 12px; }
  .workspace { display: block; padding: 0 12px 12px; overflow: visible; }
  .main-area { height: auto; overflow: visible; }
  .inventory-header { padding: 12px; }
  .inventory-title h2 { font-size: 1.1rem; }
  .inventory-title p { font-size: 0.78rem; }
  .inventory-controls { flex-direction: column; align-items: stretch; }
  .search-filter-group { width: 100%; min-width: 0; flex-direction: column; }
  .filter-button-container { width: 100%; }
  .filter-button { width: 100%; justify-content: space-between; }
  .filter-dropdown { left: 0; right: 0; width: 100%; }
  .btn { width: 100%; justify-content: center; }
  .table-container { overflow: visible; padding: 0 12px 12px; }
  .camera-table { min-width: 0; }
  .camera-table thead { display: none; }
  .camera-table, .camera-table tbody, .camera-table tr, .camera-table td { display: block; width: 100%; }
  .camera-table tbody tr { border: 1px solid rgba(148, 163, 184, 0.24); border-radius: 12px; background: rgba(15, 23, 42, 0.62); margin-bottom: 10px; padding: 8px; }
  .camera-table tbody td { border: 0; display: flex; justify-content: space-between; align-items: flex-start; gap: 10px; padding: 8px 2px; }
  .camera-table tbody td::before { content: attr(data-label); flex-shrink: 0; color: #94a3b8; font-size: 0.68rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.04em; min-width: 92px; }
  .camera-table tbody td:last-child::before { display: none; }
  .camera-name-cell { justify-content: flex-end; text-align: right; }
  .camera-name-text { white-space: normal; overflow: visible; }
  .table-actions { justify-content: flex-end; }
  .form-row { grid-template-columns: 1fr; }
  .modal-footer { flex-direction: column; }
  .modal-overlay { padding: 10px; }
  .modal-container { width: 100%; max-height: 85vh; border-radius: 12px; }
  .modal-header { padding: 12px 14px; }
  .modal-header h3 { font-size: 1.05rem; }
  .modal-body { padding: 12px 14px; }
  .form-group { margin-bottom: 10px; }
  .form-group label { font-size: 0.78rem; margin-bottom: 4px; }
  .form-group input,
  .form-group select { height: 38px; font-size: 0.82rem; padding: 0 8px; border-radius: 8px; }
  .modal-footer { margin-top: 14px; padding-top: 12px; gap: 8px; }
  .button-secondary,
  .button-primary { height: 38px; font-size: 0.82rem; border-radius: 8px; }
}
</style>
