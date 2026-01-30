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
const viewMode = ref("grid");
const showAddModal = ref(false);
const isEditMode = ref(false);
const editingCameraId = ref(null);
const isSubmitting = ref(false);
const isRefreshing = ref(false);
const tableContainer = ref(null); 

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
  status: "up"
});

const cameras = ref([]);

const fetchCameras = async () => {
  try {
    const response = await api.getCameras();
    // Validate if response.data is an array
    if (Array.isArray(response.data)) {
        // Map backend snake_case to frontend camelCase
        cameras.value = response.data.map(camera => ({
          ...camera,
          ipAddress: camera.ip_address,
          rtspUrl: camera.rtsp_url,
          lastUpdate: camera.last_update
        }));
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
  fetchCameras();
  
  // Auto-refresh camera data every 10 seconds to reflect background checks
  pollInterval = setInterval(fetchCameras, 10000);
});

onUnmounted(() => {
  document.removeEventListener('keydown', handleKeyDown);
  if (pollInterval) clearInterval(pollInterval);
});

const userInitials = computed(() => {
  return userName.value
    .split(' ')
    .map(n => n[0])
    .join('')
    .toUpperCase()
    .slice(0, 2);
});

const onlineCount = computed(() => cameras.value.filter(c => c.status === "up").length);
const offlineCount = computed(() => cameras.value.filter(c => c.status === "down").length);
const totalCount = computed(() => cameras.value.length);

const filteredCameras = computed(() => {
  let filtered = cameras.value;
  
  // Apply search filter if there's a query
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase();
    filtered = cameras.value.filter(camera => 
      camera.name.toLowerCase().includes(query) ||
      camera.location.toLowerCase().includes(query) ||
      camera.ipAddress.toLowerCase().includes(query)
    );
  }
  
  // Sort by status: online (up) first, then offline (down)
  return filtered.sort((a, b) => {
    if (a.status === 'up' && b.status === 'down') return -1;
    if (a.status === 'down' && b.status === 'up') return 1;
    return 0; // Keep original order if both have same status
  });
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
  toast.value = false;
};

// Validate IP address
const validateIPAddress = (ip) => {
  const pattern = /^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/;
  return pattern.test(ip);
};

// Validate form
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
};

const closeDropdown = () => {
  showDropdown.value = false;
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
  
  // Parse coordinates
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

const addNewCamera = () => {
  isEditMode.value = false;
  editingCameraId.value = null;
  newCamera.value = {
    name: "",
    location: "",
    ipAddress: "",
    rtspUrl: "",
    latitude: "",
    longitude: "",
    brand: "",
    version: "",
    status: "up"
  };
  validationErrors.value = {};
  showAddModal.value = true;
};

const closeModal = () => {
  // Check if form has unsaved changes
  const hasChanges = newCamera.value.name || 
                     newCamera.value.location || 
                     newCamera.value.ipAddress || 
                     newCamera.value.rtspUrl || 
                     newCamera.value.latitude || 
                     newCamera.value.longitude || 
                     newCamera.value.brand ||
                     newCamera.value.version;
  
  if (hasChanges && !isEditMode.value) {
    // Keep the add modal open, just show confirm dialog on top
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

const resetForm = () => {
  isEditMode.value = false;
  editingCameraId.value = null;
  newCamera.value = {
    name: "",
    location: "",
    ipAddress: "",
    rtspUrl: "",
    latitude: "",
    longitude: "",
    brand: "",
    version: "",
    status: "up"
  };
  validationErrors.value = {};
};

const saveCamera = async () => {
  if (!validateForm()) {
    showToast('Please fill in the required information!', 'error');
    return;
  }

  // Show loading state
  confirmModal.value.loading = true;
  isSubmitting.value = true;
  
  // Prepare payload
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
      // Update existing
      try {
        await api.updateCamera(editingCameraId.value, payload);
        await fetchCameras();
        showToast('Camera updated successfully', 'success');
        showAddModal.value = false;
        resetForm();
      } catch (error) {
        console.error('Error updating camera:', error);
        showToast('Ipaddress already exist!', 'error');
      }
    } else {
      // Create new
      try {
        const response = await api.createCamera(payload);
        // Map the response data from snake_case to camelCase before adding to cameras array
        const newCameraData = {
          ...response.data,
          ipAddress: response.data.ip_address,
          rtspUrl: response.data.rtsp_url,
          lastUpdate: response.data.last_update
        };
        // Add new camera to TOP of list
        cameras.value.unshift(newCameraData);
        showToast('Camera added successfully', 'success');
        // Manually close modal to avoid "discard changes" check
        showAddModal.value = false;
        resetForm();
      } catch (error) {
        console.error('Error adding camera:', error);
        showToast('Ipaddress already exist!', 'error');
      }
    }
  } catch (error) {
    console.error('Error saving camera:', error);
    showToast('An error occurred', 'error');
  } finally {
    confirmModal.value.loading = false;
    isSubmitting.value = false;
  }
};

const toggleViewMode = () => {
  viewMode.value = viewMode.value === 'grid' ? 'list' : 'grid';
};

const handleConfirmCancel = () => {
  confirmModal.value.show = false;
  confirmModal.value.loading = false;
};

// Handle ESC key for modal
const handleKeyDown = (e) => {
  if (e.key === 'Escape' && showAddModal.value) {
    closeModal();
  }
};

const handleSearch = () => {
  setTimeout(() => {
    const firstRow = document.querySelector('.camera-table tbody tr:first-child');
    
    if (firstRow) {
      // Scroll the first row into view
      firstRow.scrollIntoView({ 
        behavior: 'smooth', 
        block: 'start',
        inline: 'nearest'
      });
      
      // Then adjust by scrolling up a bit to account for sticky headers
      const mainArea = document.querySelector('.main-area');
      if (mainArea) {
        // Scroll up by the height of inventory header (~170px)
        mainArea.scrollTop = mainArea.scrollTop - 170;
      }
    }
  }, 0);
};

// Add event listener for ESC key - Logic moved to combined onUnmounted above

</script>

<template>
  <div class="page-container">
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

          <!-- Dropdown Menu -->
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
        <!-- Sidebar -->
        <aside class="sidebar">
          <button class="back-button" @click="goToDashboard">
            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"></path>
            </svg>
            Dashboard
          </button>

          <!-- Stats Cards -->
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
          </div>
        </aside>

        <!-- Main Area -->
        <section class="main-area">
          <!-- Inventory Header -->
          <div class="inventory-header">
            <div class="inventory-title">
              <h2>Camera Inventory</h2>
              <p>Manage and monitor all CCTV cameras across campus</p>
            </div>
            
            <div class="inventory-controls">
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

              <button class="add-button refresh-btn" @click="refreshStatus" :disabled="isRefreshing">
                <svg v-if="!isRefreshing" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
                </svg>
                <LoadingSpinner v-else size="sm" />
                <span style="margin-left: 0.5rem">Check Status</span>
              </button>

              <button class="add-button" @click="addNewCamera">
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
  <p>Try adjusting your search criteria</p>
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
    <tr class="spacer-row">
    <td colspan="10"></td>
  </tr>
  <tr v-for="camera in filteredCameras" :key="camera.id" class="camera-row">
    <td data-label="Status">
      <span class="status-badge" :class="camera.status">
        <span class="status-dot"></span>
        {{ camera.status === 'up' ? 'Online' : 'Offline' }}
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
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

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
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: 
    radial-gradient(circle at 20% 30%, rgba(102, 126, 234, 0.1) 0%, transparent 50%),
    radial-gradient(circle at 80% 70%, rgba(118, 75, 162, 0.1) 0%, transparent 50%);
  pointer-events: none;
}

/* Header Styles - Dark Theme */
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

/* Main Content */
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
  height: calc(100vh - 200px);
  overflow: hidden;
}

/* Sidebar - Dark Theme */
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

/* Main Area - Dark Theme */
.main-area {
  background: rgba(26, 32, 44, 0.9);
  backdrop-filter: blur(20px);
  border: 2px solid rgba(102, 126, 234, 0.2);
  border-radius: 16px;
  padding: 0;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
  overflow-y: auto;
  overflow-x: hidden; /* ADD THIS */
  height: 100%;
  display: flex;
  flex-direction: column;
  position: relative;
}

.inventory-header {
  position: sticky;
  top: 0;
  z-index: 10; /* Higher than table header */
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

.search-box {
  flex: 1;
  min-width: 300px;
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

.view-toggle {
  padding: 0.75rem 1rem;
  background: rgba(255, 255, 255, 0.05);
  border: 2px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.view-toggle:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(102, 126, 234, 0.4);
}

.view-toggle svg {
  width: 20px;
  height: 20px;
  color: rgba(255, 255, 255, 0.8);
}

.add-button {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
}

.add-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
}

.add-button svg {
  width: 20px;
  height: 20px;
}

.refresh-btn {
  background: linear-gradient(135deg, #4a5568 0%, #2d3748 100%) !important;
}

.refresh-btn:hover {
  background: linear-gradient(135deg, #2d3748 0%, #1a202c 100%) !important;
}

.refresh-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.refresh-btn:disabled:hover {
  transform: none;
}

/* Empty State */
.empty-state {
  text-align: center;
  padding: 4rem 2rem;
  margin: 0 2rem 2rem 2rem;  /* Add this line */
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

/* Camera Table Styles */
.table-container {
  padding: 0 2rem 2rem 2rem;
  overflow-x: hidden;
}

.camera-table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
}

.camera-table thead {
  background: rgba(26, 32, 44, 1); /* Solid background - same as inventory header */
  position: sticky;
  top: 0.1px;
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
  transform: scale(1.01);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.camera-table tbody td {
  padding: 1rem 0.75rem;
  color: rgba(255, 255, 255, 0.8);
  font-size: 0.875rem;
  vertical-align: middle;
}

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

.table-actions {
  display: flex;
  gap: 0.5rem;
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

/* Keep status badge and IP address styles */
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
  box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.2);
}

.ip-address {
  font-family: 'Courier New', monospace;
  color: rgba(102, 126, 234, 0.9);
  font-weight: 500;
}

/* Modal Styles - Dark Theme */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
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

.modal-container::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, #667eea 0%, #764ba2 50%, #667eea 100%);
  background-size: 200% 100%;
  animation: shimmer 3s linear infinite;
}

@keyframes pulse-dot {
  0%, 100% {
    opacity: 1;
    transform: scale(1);
  }
  50% {
    opacity: 0.7;
    transform: scale(1.1);
  }
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

.form-group {
  margin-bottom: 1.5rem;
}

.form-row {
  display: flex;
  gap: 1rem;
}

.form-group.half {
  flex: 1;
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

.modal-footer {
  display: flex;
  gap: 1rem;
  padding-top: 1.5rem;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.button-secondary,
.button-primary {
  flex: 1;
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.button-secondary {
  background: rgba(255, 255, 255, 0.05);
  color: rgba(255, 255, 255, 0.8);
  border: 2px solid rgba(255, 255, 255, 0.1);
}

.button-secondary:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.2);
}

.button-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
}

.button-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
}

/* ===== PROFESSIONAL CUSTOM SCROLLBAR STYLES ===== */

/* Global Scrollbar (Webkit: Chrome, Safari, Edge) */
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
  transition: all 0.3s ease;
}

::-webkit-scrollbar-thumb:hover {
  background: linear-gradient(180deg, rgba(102, 126, 234, 0.9) 0%, rgba(118, 75, 162, 0.9) 100%);
  border-color: rgba(26, 32, 44, 0.2);
  box-shadow: 0 0 10px rgba(102, 126, 234, 0.5);
}

::-webkit-scrollbar-thumb:active {
  background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
  box-shadow: 0 0 15px rgba(102, 126, 234, 0.7);
}

/* Firefox Scrollbar */
* {
  scrollbar-width: thin;
  scrollbar-color: rgba(102, 126, 234, 0.7) rgba(0, 0, 0, 0.2);
}

/* Main Area Scrollbar (Enhanced) */
.main-area {
  scrollbar-width: thin;
  scrollbar-color: rgba(102, 126, 234, 0.7) rgba(0, 0, 0, 0.2);
}

.main-area::-webkit-scrollbar {
  width: 12px;
}

.main-area::-webkit-scrollbar-track {
  background: rgba(0, 0, 0, 0.25);
  border-radius: 10px;
  margin: 10px 0;
  box-shadow: inset 0 0 5px rgba(0, 0, 0, 0.3);
}

.main-area::-webkit-scrollbar-thumb {
  background: linear-gradient(180deg, rgba(102, 126, 234, 0.8) 0%, rgba(118, 75, 162, 0.8) 100%);
  border-radius: 10px;
  border: 2px solid rgba(26, 32, 44, 0.5);
  box-shadow: 0 2px 6px rgba(102, 126, 234, 0.3);
}

.main-area::-webkit-scrollbar-thumb:hover {
  background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
  border-color: rgba(26, 32, 44, 0.3);
  box-shadow: 0 0 12px rgba(102, 126, 234, 0.6);
}

/* Modal Container Scrollbar */
.modal-container {
  scrollbar-width: thin;
  scrollbar-color: rgba(102, 126, 234, 0.6) rgba(0, 0, 0, 0.3);
}

.modal-container::-webkit-scrollbar {
  width: 8px;
}

.modal-container::-webkit-scrollbar-track {
  background: rgba(0, 0, 0, 0.3);
  border-radius: 8px;
}

.modal-container::-webkit-scrollbar-thumb {
  background: linear-gradient(180deg, rgba(102, 126, 234, 0.7) 0%, rgba(118, 75, 162, 0.7) 100%);
  border-radius: 8px;
  border: 2px solid rgba(26, 32, 44, 0.6);
}

.modal-container::-webkit-scrollbar-thumb:hover {
  background: linear-gradient(180deg, rgba(102, 126, 234, 0.9) 0%, rgba(118, 75, 162, 0.9) 100%);
  box-shadow: 0 0 8px rgba(102, 126, 234, 0.5);
}

/* Sidebar Stats Scrollbar (for mobile horizontal scroll) */
.stats-container::-webkit-scrollbar {
  height: 6px;
}

.stats-container::-webkit-scrollbar-track {
  background: transparent;
}

.stats-container::-webkit-scrollbar-thumb {
  background: linear-gradient(90deg, rgba(102, 126, 234, 0.6) 0%, rgba(118, 75, 162, 0.6) 100%);
  border-radius: 6px;
}

.stats-container::-webkit-scrollbar-thumb:hover {
  background: linear-gradient(90deg, rgba(102, 126, 234, 0.8) 0%, rgba(118, 75, 162, 0.8) 100%);
}

/* ===== END SCROLLBAR STYLES ===== */

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

/* Responsive Design */
@media (max-width: 1024px) {
  .content-wrapper {
    grid-template-columns: 1fr;
    height: auto;
    overflow: visible;
  }

  .sidebar {
    flex-direction: column;
    position: static;
    gap: 1rem;
    margin-bottom: 1rem;
  }
  
  .back-button {
    width: fit-content;
  }

  .stats-container {
    flex-direction: row;
    width: 100%;
    gap: 1rem;
  }

  .stat-card {
    flex: 1;
    min-width: 0;
  }

  .main-area {
    height: auto;
    overflow: visible;
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
  
  .content-wrapper {
    gap: 1rem;
  }

  /* Compact Stats Cards for Mobile */
  .stats-container {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 8px;
    width: 100%;
  }

  .stat-card {
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    text-align: center;
    padding: 12px 4px;
    gap: 4px;
    min-height: 90px;
    width: 100%; /* Fill the grid cell */
    min-width: 0; /* Prevent overflow */
  }

  .stat-icon {
    width: 32px;
    height: 32px;
    border-radius: 10px;
    margin: 0 auto;
  }
  
  .stat-info {
    width: 100%;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
  }

  .stat-icon svg {
    width: 16px;
    height: 16px;
  }

  .stat-label {
    font-size: 0.6rem;
    line-height: 1.1;
    margin-bottom: 2px;
    white-space: normal; /* Allow wrapping */
    text-align: center;
    width: 100%;
    word-wrap: break-word;
  }

  .stat-value {
    font-size: 1.1rem;
    margin-top: 0;
  }

.main-area {
  padding: 1rem;
  border-radius: 12px;
  overflow-x: hidden;
}

.inventory-header {
  margin: -1rem -1rem 1.5rem -1rem;
  padding: 1.25rem 1rem;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.2);
}

.inventory-title h2 {
  font-size: 1.25rem;
}

.inventory-title p {
  font-size: 0.75rem;
}

  /* Improved Inventory Controls Layout */
.inventory-controls {
  flex-direction: column;
  gap: 10px;
}

.search-box {
  flex: 1 1 100%;
  width: 100%;
  min-width: 0;
}
  
.add-button,
.refresh-btn {
  width: 100%;
  justify-content: center;
  padding: 0.75rem 1rem;
  font-size: 0.875rem;
}

.refresh-btn {
  margin-right: 0 !important;
  background: linear-gradient(135deg, #4a5568 0%, #2d3748 100%) !important;
}
  
  .add-button svg {
    width: 16px;
    height: 16px;
  }

.modal-container {
  margin: 0.5rem;
  max-height: 90vh;
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

.form-group {
  margin-bottom: 1.25rem;
}
  
.table-container {
  border-radius: 8px;
  width: 100%;
  max-width: 100%;
  overflow-x: hidden;
}

/* Mobile Card Layout for Table */
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
}

.camera-table tbody td:first-child {
  border-top: none;
  padding-top: 0;
}

.camera-table tbody td:last-child {
  justify-content: flex-end;
  padding-bottom: 0;
  border-bottom: none;
}

.camera-table tbody td:last-child::before {
  display: none;
}

.camera-name-cell {
  justify-content: flex-end;
  flex: 1;
}
}
.spacer-row {
  height: 50px;
  pointer-events: none;
  background: transparent !important;
}

.spacer-row td {
  padding: 0 !important;
  border: none !important;
}
</style>