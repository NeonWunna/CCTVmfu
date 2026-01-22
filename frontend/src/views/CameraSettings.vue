<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';
import logoUrl from '../assets/mfu-logo.png';
import Toast from '../components/ui/Toast.vue';
import ConfirmModal from '../components/ui/ConfirmModal.vue';
import LoadingSpinner from '../components/ui/LoadingSpinner.vue';
import { mockCameraAPI as cameraAPI } from '@/services/mockApi';

const router = useRouter();

const userName = ref("Admin User");
const userRole = ref("Security Administrator");
const showDropdown = ref(false);
const searchQuery = ref("");
const viewMode = ref("grid");
const showAddModal = ref(false);
const isEditMode = ref(false);
const editingCameraId = ref(null);
const loading = ref(false);

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
  coordinates: "",
  brand: "",
  version: "",
  status: "up"
});

const cameras = ref([]);

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
  if (!searchQuery.value) return cameras.value;
  
  const query = searchQuery.value.toLowerCase();
  return cameras.value.filter(camera => 
    camera.name.toLowerCase().includes(query) ||
    camera.location.toLowerCase().includes(query) ||
    camera.ipAddress.toLowerCase().includes(query)
  );
});

// Fetch cameras from API
const fetchCameras = async () => {
  loading.value = true;
  try {
    const response = await cameraAPI.getAll();
    cameras.value = response.data.cameras || response.data;
  } catch (error) {
    console.error('Failed to load cameras:', error);
    showToast('Failed to load cameras', 'error');
  } finally {
    loading.value = false;
  }
};

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
  
  validationErrors.value = errors;
  return Object.keys(errors).length === 0;
};

// Format coordinates with degree symbols - FIXED VERSION
const formatCoordinates = (value) => {
  if (!value || !value.trim()) return '';
  
  // Remove all non-numeric characters except dots, minus signs, and spaces/commas
  const cleaned = value.replace(/[^\d.\-,\s]/g, '');
  
  // Split by comma or multiple spaces to get latitude and longitude
  const parts = cleaned.split(/[,\s]+/).filter(p => p.length > 0);
  
  if (parts.length >= 2) {
    const lat = parseFloat(parts[0]);
    const lng = parseFloat(parts[1]);
    
    // Validate ranges
    if (!isNaN(lat) && !isNaN(lng) && lat >= -90 && lat <= 90 && lng >= -180 && lng <= 180) {
      return `${lat.toFixed(4)}° N, ${lng.toFixed(4)}° E`;
    }
  }
  
  // If formatting fails, return original value
  return value;
};

// Handle coordinates input blur
const handleCoordinatesBlur = () => {
  if (newCamera.value.coordinates && newCamera.value.coordinates.trim()) {
    const formatted = formatCoordinates(newCamera.value.coordinates);
    newCamera.value.coordinates = formatted;
  }
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
      localStorage.removeItem('authToken');
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
  newCamera.value = {
    name: camera.name,
    location: camera.location,
    ipAddress: camera.ipAddress,
    coordinates: camera.coordinates,
    brand: camera.brand,
    version: camera.version,
    status: camera.status
  };
  validationErrors.value = {};
  showAddModal.value = true;
};

const removeCamera = (camera) => {
  confirmModal.value = {
    show: true,
    title: 'Delete Camera',
    message: `Are you sure you want to remove "${camera.name}"? This action cannot be undone.`,
    onConfirm: async () => {
      confirmModal.value.loading = true;
      
      try {
        await cameraAPI.delete(camera.id);
        await fetchCameras();
        confirmModal.value.show = false;
        showToast(`Camera "${camera.name}" has been removed successfully`, 'success');
      } catch (error) {
        console.error('Delete failed:', error);
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
    coordinates: "",
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
                     newCamera.value.coordinates || 
                     newCamera.value.brand ||
                     newCamera.value.version;
  
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

const resetForm = () => {
  isEditMode.value = false;
  editingCameraId.value = null;
  newCamera.value = {
    name: "",
    location: "",
    ipAddress: "",
    coordinates: "",
    brand: "",
    version: "",
    status: "up"
  };
  validationErrors.value = {};
};

const saveCamera = async () => {
  if (!validateForm()) {
    showToast('Please fix the errors in the form', 'error');
    return;
  }

  // Format coordinates one final time before saving
  if (newCamera.value.coordinates && newCamera.value.coordinates.trim()) {
    newCamera.value.coordinates = formatCoordinates(newCamera.value.coordinates);
  }

  try {
  if (isEditMode.value) {
    await cameraAPI.update(editingCameraId.value, newCamera.value);
    showToast('Camera updated successfully', 'success');
    await fetchCameras();
  } else {
    const response = await cameraAPI.create(newCamera.value);
    const newCameraData = response.data;
    
    // Add new camera at the TOP of the list
    cameras.value.unshift(newCameraData);
    
    showToast('Camera added successfully', 'success');
  }
  
  showAddModal.value = false;
  resetForm();

  } catch (error) {
    console.error('Save failed:', error);
    showToast('Failed to save camera', 'error');
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

// Add event listener for ESC key
onMounted(() => {
  fetchCameras();
  document.addEventListener('keydown', handleKeyDown);
});

onUnmounted(() => {
  document.removeEventListener('keydown', handleKeyDown);
});
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

    <!-- Loading Spinner -->
    <LoadingSpinner v-if="loading" overlay message="Loading cameras..." />

    <!-- Header -->
    <header class="header">
      <div class="header-content">
        <div class="header-left">
          <img :src="logoUrl" alt="MFU Logo" class="logo" @error="handleLogoError">
          <div class="header-text">
            <h1>Camera Management</h1>
            <p>Mae Fah Luang University Security System</p>
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
                  type="text" 
                  placeholder="Search by name, location, or IP address..."
                  class="search-input"
                  aria-label="Search cameras"
                >
              </div>

              <button class="view-toggle" @click="toggleViewMode" aria-label="Toggle view mode">
                <svg v-if="viewMode === 'grid'" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"></path>
                </svg>
                <svg v-else fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z"></path>
                </svg>
              </button>

              <button class="add-button" @click="addNewCamera">
                <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path>
                </svg>
                Add Camera
              </button>
            </div>
          </div>

          <!-- Camera Grid -->
          <div v-if="filteredCameras.length === 0" class="empty-state">
            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
            </svg>
            <h3>No cameras found</h3>
            <p>Try adjusting your search criteria</p>
          </div>

          <div v-else class="camera-grid" :class="{ 'list-view': viewMode === 'list' }">
            <div v-for="camera in filteredCameras" :key="camera.id" class="camera-card">
              <div class="card-header">
                <div class="camera-icon">
                  <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"></path>
                  </svg>
                </div>
                <span class="status-badge" :class="camera.status">
                  <span class="status-dot"></span>
                  {{ camera.status === 'up' ? 'Online' : 'Offline' }}
                </span>
              </div>

              <div class="card-body">
                <h3 class="camera-name">{{ camera.name }}</h3>
                
                <div class="camera-meta">
                  <div class="meta-row">
                    <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"></path>
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"></path>
                    </svg>
                    <span>{{ camera.location }}</span>
                  </div>

                  <div class="meta-row">
                    <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9"></path>
                    </svg>
                    <span>{{ camera.ipAddress }}</span>
                  </div>

                  <div class="meta-row" v-if="camera.coordinates">
                    <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7"></path>
                    </svg>
                    <span>{{ camera.coordinates }}</span>
                  </div>

                  <div class="meta-row">
                    <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z"></path>
                    </svg>
                    <span>{{ camera.brand }}</span>
                  </div>

                  <div class="meta-row">
                    <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4"></path>
                    </svg>
                    <span>{{ camera.version }}</span>
                  </div>

                  <div class="meta-row">
                    <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                    </svg>
                    <span>{{ camera.lastUpdate }}</span>
                  </div>
                </div>
              </div>

              <div class="card-actions">
                <button class="action-button edit" @click="editCamera(camera)" aria-label="Edit camera">
                  <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
                  </svg>
                  Edit
                </button>
                <button class="action-button delete" @click="removeCamera(camera)" aria-label="Delete camera">
                  <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
                  </svg>
                  Delete
                </button>
              </div>
            </div>
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
              <label for="camera-coordinates">Coordinates</label>
              <input 
                id="camera-coordinates"
                v-model="newCamera.coordinates"
                type="text" 
                placeholder="e.g., 20.0451, 99.8825 (auto-formats to °N, °E)"
                @blur="handleCoordinatesBlur"
              >
              <span class="input-hint">Enter latitude and longitude separated by comma (e.g., 20.0451, 99.8825)</span>
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

            <div class="form-group">
              <label for="camera-status">Status</label>
              <select id="camera-status" v-model="newCamera.status">
                <option value="up">Online</option>
                <option value="down">Offline</option>
              </select>
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
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

/* Header Styles */
.header {
  background: rgba(255, 255, 255, 0.98);
  box-shadow: 0 2px 20px rgba(0, 0, 0, 0.1);
  position: sticky;
  top: 0;
  z-index: 100;
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
}

.header-text h1 {
  font-size: 24px;
  color: #2d3748;
  font-weight: 700;
}

.header-text p {
  font-size: 14px;
  color: #718096;
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
}

.profile-section:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
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
  background: white;
  border-radius: 12px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.15);
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
  color: #4a5568;
  font-size: 0.875rem;
  border-radius: 8px;
  transition: all 0.2s ease;
}

.dropdown-item:hover {
  background: #f7fafc;
  color: #667eea;
}

.dropdown-item.logout:hover {
  background: #fff5f5;
  color: #e53e3e;
}

.dropdown-item svg {
  width: 20px;
  height: 20px;
}

.dropdown-divider {
  height: 1px;
  background: #e2e8f0;
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
  max-width: 1400px;
  margin: 0 auto;
  padding: 2rem;
}

.content-wrapper {
  display: grid;
  grid-template-columns: 280px 1fr;
  gap: 2rem;
  height: calc(100vh - 200px); /* Adjust based on header height */
  overflow: hidden;
}

/* Sidebar */
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
  background: white;
  border: none;
  border-radius: 12px;
  color: #667eea;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.back-button:hover {
  transform: translateX(-4px);
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
  background: white;
  border-radius: 12px;
  padding: 1.25rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
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
}

.stat-online .stat-icon {
  background: linear-gradient(135deg, #48bb78 0%, #38a169 100%);
}

.stat-offline .stat-icon {
  background: linear-gradient(135deg, #f56565 0%, #e53e3e 100%);
}

.stat-info {
  flex: 1;
}

.stat-label {
  font-size: 0.75rem;
  color: #718096;
  font-weight: 600;
  letter-spacing: 0.5px;
}

.stat-value {
  font-size: 1.75rem;
  font-weight: 700;
  color: #2d3748;
  margin-top: 0.25rem;
}

/* Main Area */
.main-area {
  background: white;
  border-radius: 16px;
  padding: 2rem;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  overflow-y: auto;
  height: 100%;
}

.inventory-header {
  margin-bottom: 2rem;
}

.inventory-title h2 {
  font-size: 1.75rem;
  color: #2d3748;
  font-weight: 700;
  margin-bottom: 0.5rem;
}

.inventory-title p {
  color: #718096;
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
  color: #a0aec0;
}

.search-input {
  width: 100%;
  padding: 0.75rem 1rem 0.75rem 3rem;
  border: 2px solid #e2e8f0;
  border-radius: 12px;
  font-size: 0.875rem;
  transition: all 0.3s ease;
}

.search-input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.view-toggle {
  padding: 0.75rem 1rem;
  background: #f7fafc;
  border: 2px solid #e2e8f0;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.view-toggle:hover {
  background: #edf2f7;
  border-color: #cbd5e0;
}

.view-toggle svg {
  width: 20px;
  height: 20px;
  color: #4a5568;
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
}

.add-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.add-button svg {
  width: 20px;
  height: 20px;
}

/* Camera Grid */
.camera-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 1.5rem;
}

.camera-grid.list-view {
  grid-template-columns: 1fr;
}

.camera-card {
  background: #f7fafc;
  border: 2px solid #e2e8f0;
  border-radius: 12px;
  padding: 1.5rem;
  transition: all 0.3s ease;
}

.camera-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
  border-color: #667eea;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.camera-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
}

.camera-icon svg {
  width: 24px;
  height: 24px;
  color: white;
}

.status-badge {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 600;
}

.status-badge.up {
  background: #c6f6d5;
  color: #22543d;
}

.status-badge.down {
  background: #fed7d7;
  color: #742a2a;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.status-badge.up .status-dot {
  background: #38a169;
  animation: pulse 2s ease-in-out infinite;
}

.status-badge.down .status-dot {
  background: #e53e3e;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

.card-body {
  margin-bottom: 1.5rem;
}

.camera-name {
  font-size: 1.25rem;
  color: #2d3748;
  font-weight: 700;
  margin-bottom: 1rem;
}

.camera-meta {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.meta-row {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  color: #4a5568;
  font-size: 0.875rem;
}

.meta-row svg {
  width: 18px;
  height: 18px;
  color: #a0aec0;
  flex-shrink: 0;
}

.card-actions {
  display: flex;
  gap: 0.75rem;
  padding-top: 1rem;
  border-top: 2px solid #e2e8f0;
}

.action-button {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.75rem;
  border: 2px solid;
  border-radius: 8px;
  font-weight: 600;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.action-button svg {
  width: 18px;
  height: 18px;
}

.action-button.edit {
  background: white;
  border-color: #667eea;
  color: #667eea;
}

.action-button.edit:hover {
  background: #667eea;
  color: white;
}

.action-button.delete {
  background: white;
  border-color: #e53e3e;
  color: #e53e3e;
}

.action-button.delete:hover {
  background: #e53e3e;
  color: white;
}

/* Empty State */
.empty-state {
  text-align: center;
  padding: 4rem 2rem;
  color: #a0aec0;
}

.empty-state svg {
  width: 64px;
  height: 64px;
  margin: 0 auto 1rem;
}

.empty-state h3 {
  font-size: 1.5rem;
  color: #4a5568;
  margin-bottom: 0.5rem;
}

.empty-state p {
  color: #718096;
}

/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
}

.modal-container {
  background: white;
  border-radius: 16px;
  max-width: 600px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem 2rem;
  border-bottom: 2px solid #e2e8f0;
}

.modal-header h3 {
  font-size: 1.5rem;
  color: #2d3748;
  font-weight: 700;
}

.close-button {
  width: 40px;
  height: 40px;
  border: none;
  background: #f7fafc;
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

.close-button:hover {
  background: #e2e8f0;
}

.close-button svg {
  width: 20px;
  height: 20px;
  color: #4a5568;
}

.modal-body {
  padding: 2rem;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  color: #2d3748;
  font-weight: 600;
  font-size: 0.875rem;
}

.required {
  color: #e53e3e;
}

.form-group input,
.form-group select {
  width: 100%;
  padding: 0.75rem 1rem;
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  font-size: 0.875rem;
  transition: all 0.3s ease;
}

.form-group input:focus,
.form-group select:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.form-group input.error {
  border-color: #e53e3e;
}

.error-message {
  display: block;
  margin-top: 0.5rem;
  color: #e53e3e;
  font-size: 0.75rem;
}

.input-hint {
  display: block;
  margin-top: 0.5rem;
  color: #718096;
  font-size: 0.75rem;
  font-style: italic;
}

.modal-footer {
  display: flex;
  gap: 1rem;
  padding-top: 1.5rem;
  border-top: 2px solid #e2e8f0;
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
  background: #f7fafc;
  color: #4a5568;
}

.button-secondary:hover {
  background: #e2e8f0;
}

.button-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.button-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
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
  }

  .sidebar {
    flex-direction: row;
    overflow-x: auto;
  }

  .stats-container {
    flex-direction: row;
    min-width: min-content;
  }

  .stat-card {
    min-width: 200px;
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

  .main-content {
    padding: 1rem;
  }

  .main-area {
    padding: 1.5rem;
  }

  .inventory-controls {
    flex-direction: column;
  }

  .search-box {
    min-width: 100%;
  }

  .camera-grid {
    grid-template-columns: 1fr;
  }

  .modal-container {
    margin: 1rem;
  }

  .modal-header,
  .modal-body {
    padding: 1.5rem;
  }
}

@media (max-width: 480px) {
  .logo {
    height: 45px;
  }

  .inventory-title h2 {
    font-size: 1.5rem;
  }

  .card-actions {
    flex-direction: column;
  }

  .action-button {
    width: 100%;
  }
}
</style>

<style>
/* Global z-index hierarchy for modals and overlays */
/* Base modal (Add/Edit Camera): z-index 1000 */
/* Confirm Modal should be above: z-index 2000 */
/* Toast should be on top of everything: z-index 9999 */

/* Confirm modal overlay - appears above regular modals */
.confirm-modal,
.confirm-modal-overlay,
[class*="confirm"][class*="modal"] {
  z-index: 2000 !important;
}

/* Toast notification - appears above everything */
.toast,
.toast-container,
[class*="toast"] {
  z-index: 9999 !important;
}
</style>