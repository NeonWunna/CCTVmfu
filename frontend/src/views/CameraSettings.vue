<script setup>
import { ref, computed } from 'vue';
import { useRouter } from 'vue-router';
import logoUrl from '../assets/mfu-logo.png';

const router = useRouter();

const userName = ref("Admin User");
const userRole = ref("Security Administrator");
const showDropdown = ref(false);
const searchQuery = ref("");
const viewMode = ref("grid");
const showAddModal = ref(false);
const isEditMode = ref(false);
const editingCameraId = ref(null);

const newCamera = ref({
  name: "",
  location: "",
  ipAddress: "",
  coordinates: "",
  brand: "",
  status: "up"
});

const cameras = ref([
  { 
    id: 1,
    name: "Main Gate CCTV", 
    status: "up",
    location: "Main Entrance",
    ipAddress: "192.168.1.10",
    coordinates: "20.0451° N, 99.8825° E",
    brand: "Hikvision",
    version: "V5.7.3",
    lastUpdate: "2 min ago"
  },
  { 
    id: 2,
    name: "Library CCTV", 
    status: "up",
    location: "Central Library",
    ipAddress: "192.168.1.11",
    coordinates: "20.0456° N, 99.8831° E",
    brand: "Dahua",
    version: "V2.840.0000000.28.R",
    lastUpdate: "1 min ago"
  },
  { 
    id: 3,
    name: "Dormitory CCTV", 
    status: "down",
    location: "Student Housing",
    ipAddress: "192.168.1.12",
    coordinates: "20.0448° N, 99.8819° E",
    brand: "Axis",
    version: "10.12.85",
    lastUpdate: "15 min ago"
  },
  { 
    id: 4,
    name: "Parking Lot CCTV", 
    status: "up",
    location: "Parking Area A",
    ipAddress: "192.168.1.13",
    coordinates: "20.0443° N, 99.8833° E",
    brand: "Hikvision",
    version: "V5.7.3",
    lastUpdate: "Just now"
  },
  { 
    id: 5,
    name: "Sports Complex CCTV", 
    status: "up",
    location: "Athletic Center",
    ipAddress: "192.168.1.14",
    coordinates: "20.0461° N, 99.8838° E",
    brand: "Uniview",
    version: "IPC_5E0000",
    lastUpdate: "3 min ago"
  },
  { 
    id: 6,
    name: "Cafeteria CCTV", 
    status: "up",
    location: "Student Cafeteria",
    ipAddress: "192.168.1.15",
    coordinates: "20.0454° N, 99.8827° E",
    brand: "Dahua",
    version: "V2.840.0000000.28.R",
    lastUpdate: "1 min ago"
  },
  { 
    id: 7,
    name: "Admin Building CCTV", 
    status: "up",
    location: "Administration Office",
    ipAddress: "192.168.1.16",
    coordinates: "20.0458° N, 99.8824° E",
    brand: "Hikvision",
    version: "V5.7.3",
    lastUpdate: "4 min ago"
  },
  { 
    id: 8,
    name: "Science Building CCTV", 
    status: "up",
    location: "Science Faculty",
    ipAddress: "192.168.1.17",
    coordinates: "20.0453° N, 99.8829° E",
    brand: "Axis",
    version: "10.12.85",
    lastUpdate: "2 min ago"
  },
  { 
    id: 9,
    name: "Engineering Hall CCTV", 
    status: "down",
    location: "Engineering Building",
    ipAddress: "192.168.1.18",
    coordinates: "20.0459° N, 99.8836° E",
    brand: "Hikvision",
    version: "V5.7.3",
    lastUpdate: "20 min ago"
  },
  { 
    id: 10,
    name: "East Gate CCTV", 
    status: "up",
    location: "East Entrance",
    ipAddress: "192.168.1.19",
    coordinates: "20.0449° N, 99.8842° E",
    brand: "Uniview",
    version: "IPC_5E0000",
    lastUpdate: "Just now"
  },
  { 
    id: 11,
    name: "West Gate CCTV", 
    status: "up",
    location: "West Entrance",
    ipAddress: "192.168.1.20",
    coordinates: "20.0452° N, 99.8815° E",
    brand: "Dahua",
    version: "V2.840.0000000.28.R",
    lastUpdate: "3 min ago"
  },
  { 
    id: 12,
    name: "Parking Area B CCTV", 
    status: "up",
    location: "Parking Lot B",
    ipAddress: "192.168.1.21",
    coordinates: "20.0446° N, 99.8821° E",
    brand: "Hikvision",
    version: "V5.7.3",
    lastUpdate: "5 min ago"
  },
  { 
    id: 13,
    name: "Student Center CCTV", 
    status: "up",
    location: "Student Activities Center",
    ipAddress: "192.168.1.22",
    coordinates: "20.0455° N, 99.8830° E",
    brand: "Axis",
    version: "10.12.85",
    lastUpdate: "2 min ago"
  },
  { 
    id: 14,
    name: "Basketball Court CCTV", 
    status: "up",
    location: "Outdoor Courts",
    ipAddress: "192.168.1.23",
    coordinates: "20.0460° N, 99.8834° E",
    brand: "Uniview",
    version: "IPC_5E0000",
    lastUpdate: "6 min ago"
  },
  { 
    id: 15,
    name: "Medical Center CCTV", 
    status: "up",
    location: "Health Services",
    ipAddress: "192.168.1.24",
    coordinates: "20.0457° N, 99.8828° E",
    brand: "Dahua",
    version: "V2.840.0000000.28.R",
    lastUpdate: "1 min ago"
  }
]);

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
  if (confirm('Are you sure you want to logout?')) {
    localStorage.removeItem('isAuthenticated');
    closeDropdown();
    router.push('/login');
  }
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
    status: camera.status
  };
  showAddModal.value = true;
};

const removeCamera = (camera) => {
  if (confirm(`Are you sure you want to remove "${camera.name}"?`)) {
    cameras.value = cameras.value.filter(c => c.id !== camera.id);
  }
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
    status: "up"
  };
  showAddModal.value = true;
};

const closeModal = () => {
  showAddModal.value = false;
  isEditMode.value = false;
  editingCameraId.value = null;
  newCamera.value = {
    name: "",
    location: "",
    ipAddress: "",
    coordinates: "",
    brand: "",
    status: "up"
  };
};

const saveCamera = () => {
  if (!newCamera.value.name || !newCamera.value.location || !newCamera.value.ipAddress) {
    alert('Please fill in all required fields (Name, Location, IP Address)');
    return;
  }

  if (isEditMode.value) {
    // Update existing camera
    const index = cameras.value.findIndex(c => c.id === editingCameraId.value);
    if (index !== -1) {
      cameras.value[index] = {
        ...cameras.value[index],
        ...newCamera.value,
        lastUpdate: "Just now"
      };
    }
  } else {
    // Add new camera
    const newId = Math.max(...cameras.value.map(c => c.id)) + 1;
    cameras.value.push({
      id: newId,
      ...newCamera.value,
      lastUpdate: "Just now"
    });
  }

  closeModal();
};

const toggleViewMode = () => {
  viewMode.value = viewMode.value === 'grid' ? 'list' : 'grid';
};
</script>

<template>
  <div class="page-container">
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
                >
              </div>

              <button class="view-toggle" @click="toggleViewMode">
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

                  <div class="meta-row">
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
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                    </svg>
                    <span>{{ camera.lastUpdate }}</span>
                  </div>
                </div>
              </div>

              <div class="card-actions">
                <button class="action-btn edit-btn" @click="editCamera(camera)">
                  <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
                  </svg>
                  Edit
                </button>
                <button class="action-btn remove-btn" @click="removeCamera(camera)">
                  <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
                  </svg>
                  Remove
                </button>
              </div>
            </div>
          </div>
        </section>
      </div>
    </main>

    <!-- Add/Edit Camera Modal -->
    <transition name="modal">
      <div v-if="showAddModal" class="modal-overlay" @click="closeModal">
        <div class="modal-container" @click.stop>
          <div class="modal-header">
            <h2>{{ isEditMode ? 'Edit Camera' : 'Add New Camera' }}</h2>
            <button class="modal-close" @click="closeModal">
              <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
              </svg>
            </button>
          </div>

          <div class="modal-body">
            <form @submit.prevent="saveCamera">
              <div class="form-grid">
                <div class="form-group">
                  <label for="cameraName">
                    Camera Name <span class="required">*</span>
                  </label>
                  <input
                    id="cameraName"
                    v-model="newCamera.name"
                    type="text"
                    placeholder="e.g., Main Gate CCTV"
                    required
                  >
                </div>

                <div class="form-group">
                  <label for="cameraLocation">
                    Location <span class="required">*</span>
                  </label>
                  <input
                    id="cameraLocation"
                    v-model="newCamera.location"
                    type="text"
                    placeholder="e.g., Main Entrance"
                    required
                  >
                </div>

                <div class="form-group">
                  <label for="cameraIP">
                    IP Address <span class="required">*</span>
                  </label>
                  <input
                    id="cameraIP"
                    v-model="newCamera.ipAddress"
                    type="text"
                    placeholder="e.g., 192.168.1.10"
                    pattern="^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$"
                    required
                  >
                </div>

                <div class="form-group">
                  <label for="cameraCoordinates">
                    Coordinates
                  </label>
                  <input
                    id="cameraCoordinates"
                    v-model="newCamera.coordinates"
                    type="text"
                    placeholder="e.g., 20.0451° N, 99.8825° E"
                  >
                </div>

                <div class="form-group">
                  <label for="cameraBrand">
                    Brand
                  </label>
                  <select id="cameraBrand" v-model="newCamera.brand">
                    <option value="">Select Brand</option>
                    <option value="Hikvision">Hikvision</option>
                    <option value="Dahua">Dahua</option>
                    <option value="Axis">Axis</option>
                    <option value="Uniview">Uniview</option>
                    <option value="Bosch">Bosch</option>
                    <option value="Samsung">Samsung</option>
                  </select>
                </div>

                <div class="form-group">
                  <label for="cameraStatus">
                    Status
                  </label>
                  <select id="cameraStatus" v-model="newCamera.status">
                    <option value="up">Online</option>
                    <option value="down">Offline</option>
                  </select>
                </div>
              </div>

              <div class="modal-footer">
                <button type="button" class="btn-secondary" @click="closeModal">
                  Cancel
                </button>
                <button type="submit" class="btn-primary">
                  <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                  </svg>
                  {{ isEditMode ? 'Update Camera' : 'Add Camera' }}
                </button>
              </div>
            </form>
          </div>
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
  background: linear-gradient(180deg, #e8ecf1 0%, #f5f7fa 100%);
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

/* Header */
.header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-content {
  max-width: 1600px;
  margin: 0 auto;
  padding: 1.25rem 2rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.logo {
  height: 50px;
  width: auto;
}

.header-text h1 {
  font-size: 1.5rem;
  font-weight: 700;
  margin-bottom: 0.25rem;
}

.header-text p {
  font-size: 0.875rem;
  opacity: 0.95;
}

.header-right {
  position: relative;
}

.profile-section {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  background: rgba(255, 255, 255, 0.15);
  padding: 0.5rem 1rem;
  border-radius: 50px;
  cursor: pointer;
  transition: all 0.2s;
  backdrop-filter: blur(10px);
}

.profile-section:hover {
  background: rgba(255, 255, 255, 0.25);
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
  font-size: 0.875rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.profile-info {
  display: flex;
  flex-direction: column;
}

.profile-name {
  font-size: 0.875rem;
  font-weight: 600;
}

.profile-role {
  font-size: 0.75rem;
  opacity: 0.9;
}

.dropdown-arrow {
  width: 18px;
  height: 18px;
  transition: transform 0.3s;
}

.dropdown-arrow.open {
  transform: rotate(180deg);
}

/* Dropdown */
.profile-dropdown {
  position: absolute;
  top: calc(100% + 0.75rem);
  right: 0;
  background: white;
  border-radius: 12px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.15);
  min-width: 240px;
  overflow: hidden;
  z-index: 101;
}

.dropdown-header {
  padding: 1.5rem;
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
  font-size: 1.5rem;
  margin: 0 auto 0.75rem;
  border: 3px solid rgba(255, 255, 255, 0.3);
}

.dropdown-name {
  font-size: 1rem;
  font-weight: 600;
  margin-bottom: 0.25rem;
}

.dropdown-role {
  font-size: 0.8125rem;
  opacity: 0.95;
}

.dropdown-menu {
  padding: 0.5rem 0;
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1.25rem;
  width: 100%;
  border: none;
  background: none;
  color: #374151;
  font-size: 0.875rem;
  text-align: left;
  cursor: pointer;
  transition: background 0.2s;
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
  margin: 0.5rem 0;
}

.dropdown-item.logout {
  color: #ef4444;
}

.dropdown-item.logout svg {
  color: #ef4444;
}

.dropdown-overlay {
  position: fixed;
  inset: 0;
  z-index: 99;
}

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
}

.content-wrapper {
  display: grid;
  grid-template-columns: 300px 1fr;
  gap: 2rem;
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
  padding: 0.75rem 1.25rem;
  background: white;
  border: 2px solid #e5e7eb;
  border-radius: 10px;
  color: #374151;
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.back-button:hover {
  border-color: #667eea;
  color: #667eea;
  transform: translateX(-3px);
}

.back-button svg {
  width: 18px;
  height: 18px;
}

.stats-container {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.stat-card {
  background: white;
  border-radius: 14px;
  padding: 1.25rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  border: 2px solid transparent;
  transition: all 0.3s;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
}

.stat-icon {
  width: 56px;
  height: 56px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 1rem;
}

.stat-icon svg {
  width: 28px;
  height: 28px;
  color: white;
}

.stat-total .stat-icon {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.stat-total:hover {
  border-color: #667eea;
}

.stat-online .stat-icon {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
}

.stat-online:hover {
  border-color: #10b981;
}

.stat-offline .stat-icon {
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
}

.stat-offline:hover {
  border-color: #ef4444;
}

.stat-label {
  font-size: 0.75rem;
  color: #6b7280;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 0.5rem;
}

.stat-value {
  font-size: 2rem;
  font-weight: 700;
  color: #1f2937;
}

/* Main Area */
.main-area {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.inventory-header {
  background: white;
  border-radius: 14px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.inventory-title {
  margin-bottom: 1.25rem;
}

.inventory-title h2 {
  font-size: 1.5rem;
  font-weight: 700;
  color: #1f2937;
  margin-bottom: 0.25rem;
}

.inventory-title p {
  font-size: 0.875rem;
  color: #6b7280;
}

.inventory-controls {
  display: flex;
  gap: 0.75rem;
  align-items: center;
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
  color: #9ca3af;
}

.search-input {
  width: 100%;
  padding: 0.75rem 1rem 0.75rem 3rem;
  border: 2px solid #e5e7eb;
  border-radius: 10px;
  font-size: 0.875rem;
  background: #f9fafb;
  transition: all 0.2s;
}

.search-input:focus {
  outline: none;
  border-color: #667eea;
  background: white;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.view-toggle {
  padding: 0.75rem;
  background: #f3f4f6;
  border: 2px solid #e5e7eb;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.view-toggle:hover {
  background: #e5e7eb;
  border-color: #667eea;
}

.view-toggle svg {
  width: 20px;
  height: 20px;
  color: #374151;
}

.add-button {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 10px;
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
}

.add-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(102, 126, 234, 0.3);
}

.add-button svg {
  width: 20px;
  height: 20px;
}

/* Empty State */
.empty-state {
  background: white;
  border-radius: 14px;
  padding: 4rem 2rem;
  text-align: center;
  color: #9ca3af;
}

.empty-state svg {
  width: 64px;
  height: 64px;
  margin-bottom: 1rem;
  opacity: 0.5;
}

.empty-state h3 {
  font-size: 1.125rem;
  color: #6b7280;
  margin-bottom: 0.5rem;
}

.empty-state p {
  font-size: 0.875rem;
}

/* Camera Grid */
.camera-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
  gap: 1.25rem;
}

.camera-grid.list-view {
  grid-template-columns: 1fr;
}

/* Camera Card */
.camera-card {
  background: white;
  border-radius: 14px;
  padding: 1.25rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  border: 2px solid #f3f4f6;
  transition: all 0.3s;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.camera-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
  border-color: #667eea;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
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
  width: 26px;
  height: 26px;
  color: white;
}

.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.375rem 0.875rem;
  border-radius: 20px;
  font-size: 0.8125rem;
  font-weight: 600;
}

.status-badge.up {
  background: #d1fae5;
  color: #065f46;
}

.status-badge.down {
  background: #fee2e2;
  color: #991b1b;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: currentColor;
}

.card-body {
  flex: 1;
}

.camera-name {
  font-size: 1.125rem;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 0.875rem;
}

.camera-meta {
  display: flex;
  flex-direction: column;
  gap: 0.625rem;
}

.meta-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  color: #6b7280;
}

.meta-row svg {
  width: 16px;
  height: 16px;
  color: #9ca3af;
  flex-shrink: 0;
}

.card-actions {
  display: flex;
  gap: 0.75rem;
  padding-top: 0.75rem;
  border-top: 1px solid #f3f4f6;
}

.action-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.625rem 1rem;
  border-radius: 8px;
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  border: 2px solid;
}

.action-btn svg {
  width: 16px;
  height: 16px;
}

.edit-btn {
  background: white;
  color: #667eea;
  border-color: #667eea;
}

.edit-btn:hover {
  background: #667eea;
  color: white;
}

.remove-btn {
  background: white;
  color: #ef4444;
  border-color: #ef4444;
}

.remove-btn:hover {
  background: #ef4444;
  color: white;
}

/* Responsive */
@media (max-width: 1200px) {
  .content-wrapper {
    grid-template-columns: 1fr;
  }

  .stats-container {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  }
}

@media (max-width: 768px) {
  .header-content {
    padding: 1rem 1.25rem;
  }

  .logo {
    height: 40px;
  }

  .header-text h1 {
    font-size: 1.25rem;
  }

  .header-text p {
    font-size: 0.75rem;
  }

  .main-content {
    padding: 1.25rem;
  }

  .inventory-controls {
    flex-direction: column;
    align-items: stretch;
  }

  .view-toggle,
  .add-button {
    width: 100%;
    justify-content: center;
  }

  .camera-grid {
    grid-template-columns: 1fr;
  }
}

/* Modal Styles */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
}

.modal-container {
  background: white;
  border-radius: 16px;
  width: 100%;
  max-width: 700px;
  max-height: 90vh;
  overflow: hidden;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  display: flex;
  flex-direction: column;
}

.modal-header {
  padding: 1.5rem 2rem;
  border-bottom: 2px solid #f3f4f6;
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.modal-header h2 {
  font-size: 1.5rem;
  font-weight: 700;
  margin: 0;
}

.modal-close {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  border: none;
  background: rgba(255, 255, 255, 0.2);
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.modal-close:hover {
  background: rgba(255, 255, 255, 0.3);
}

.modal-close svg {
  width: 20px;
  height: 20px;
}

.modal-body {
  padding: 2rem;
  overflow-y: auto;
  flex: 1;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1.5rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-group label {
  font-size: 0.875rem;
  font-weight: 600;
  color: #374151;
}

.required {
  color: #ef4444;
}

.form-group input,
.form-group select {
  padding: 0.75rem 1rem;
  border: 2px solid #e5e7eb;
  border-radius: 10px;
  font-size: 0.875rem;
  transition: all 0.2s;
  background: #f9fafb;
}

.form-group input:focus,
.form-group select:focus {
  outline: none;
  border-color: #667eea;
  background: white;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.form-group select {
  cursor: pointer;
}

.modal-footer {
  padding: 1.5rem 2rem;
  border-top: 2px solid #f3f4f6;
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  background: #f9fafb;
}

.btn-secondary,
.btn-primary {
  padding: 0.75rem 1.5rem;
  border-radius: 10px;
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  border: none;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.btn-secondary {
  background: white;
  color: #374151;
  border: 2px solid #e5e7eb;
}

.btn-secondary:hover {
  background: #f3f4f6;
  border-color: #d1d5db;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(102, 126, 234, 0.3);
}

.btn-primary svg {
  width: 18px;
  height: 18px;
}

/* Modal Animations */
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.3s ease;
}

.modal-enter-active .modal-container,
.modal-leave-active .modal-container {
  transition: transform 0.3s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-from .modal-container,
.modal-leave-to .modal-container {
  transform: scale(0.9) translateY(-20px);
}

/* Responsive Modal */
@media (max-width: 768px) {
  .modal-container {
    max-width: 100%;
    max-height: 95vh;
    margin: 0;
  }

  .modal-header {
    padding: 1.25rem 1.5rem;
  }

  .modal-header h2 {
    font-size: 1.25rem;
  }

  .modal-body {
    padding: 1.5rem;
  }

  .form-grid {
    grid-template-columns: 1fr;
    gap: 1.25rem;
  }

  .modal-footer {
    padding: 1.25rem 1.5rem;
    flex-direction: column-reverse;
  }

  .btn-secondary,
  .btn-primary {
    width: 100%;
    justify-content: center;
  }
}
</style>