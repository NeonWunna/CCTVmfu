<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../stores/auth';
import logoUrl from '../assets/mfu-logo.png';
import api from '../services/api';
import Toast from '../components/ui/Toast.vue';
import ConfirmModal from '../components/ui/ConfirmModal.vue';
import AppHeader from '../components/dashboard/AppHeader.vue';
import StatsCards from '../components/dashboard/StatsCards.vue';
import FiltersBar from '../components/dashboard/FiltersBar.vue';
import MapView from '../components/dashboard/MapView.vue';
import CameraInfoPanel from '../components/dashboard/CameraInfoPanel.vue';
import StreamOverlay from '../components/dashboard/StreamOverlay.vue';

const router = useRouter();
const authStore = useAuthStore();
const isUser = computed(() => authStore.isUser);
const mapViewRef = ref(null);

const userName = computed(() => authStore.user?.name || 'User');
const userRole = computed(() => {
  const role = authStore.user?.role;
  if (role === 'superadmin') return 'Super Admin';
  if (role === 'admin') return 'Admin';
  return 'User';
});

const cctvs = ref([]);
const searchQuery = ref('');
const selectedFilter = ref('all');
const selectedCamera = ref(null);
const isStreamOpen = ref(false);
const streamUrl = ref('');
const loadingCameras = ref(true);
const isCheckingBlurry = ref(false);

const viewportWidth = ref(typeof window !== 'undefined' ? window.innerWidth : 1280);
const viewportHeight = ref(typeof window !== 'undefined' ? window.innerHeight : 720);
const sidebarExpanded = ref(viewportWidth.value >= 1200);
const mobileFiltersOpen = ref(false);
const mobileDrawerTab = ref('status');

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

const filterOptions = [
  { value: 'all', label: 'All Cameras' },
  { value: 'online', label: 'Online' },
  { value: 'offline', label: 'Offline' },
  { value: 'no_signal', label: 'No Signal' },
  { value: 'blurry', label: 'Blurry' }
];

const isCompactLandscape = computed(() =>
  viewportWidth.value <= 1024 && viewportHeight.value <= 560
);
const isMobile = computed(() => viewportWidth.value < 768 || isCompactLandscape.value);
const activeCameraId = computed(() => selectedCamera.value?.id ?? null);

const formatThailandDateTime = (date = new Date()) => {
  const dateParts = new Intl.DateTimeFormat('en-CA', {
    timeZone: 'Asia/Bangkok',
    year: 'numeric',
    month: '2-digit',
    day: '2-digit'
  }).formatToParts(date);

  const timeParts = new Intl.DateTimeFormat('en-GB', {
    timeZone: 'Asia/Bangkok',
    hour12: false,
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  }).formatToParts(date);

  const getPart = (parts, type) => parts.find((part) => part.type === type)?.value || '';

  return `${getPart(dateParts, 'year')}-${getPart(dateParts, 'month')}-${getPart(dateParts, 'day')} ${getPart(timeParts, 'hour')}:${getPart(timeParts, 'minute')}:${getPart(timeParts, 'second')}`;
};

const parseCoordinates = (coordString) => {
  if (!coordString) return { lat: 0, lng: 0 };

  try {
    const parts = coordString.split(',');
    if (parts.length !== 2) return { lat: 0, lng: 0 };

    const lat = parseFloat(parts[0].replace(/[^\d.-]/g, ''));
    const lng = parseFloat(parts[1].replace(/[^\d.-]/g, ''));

    return {
      lat: Number.isFinite(lat) ? lat : 0,
      lng: Number.isFinite(lng) ? lng : 0
    };
  } catch (error) {
    console.warn('Failed to parse coordinates:', coordString, error);
    return { lat: 0, lng: 0 };
  }
};

const normalizeCamera = (camera) => {
  const coords = parseCoordinates(camera.coordinates);

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
    lat: coords.lat,
    lng: coords.lng,
    ipAddress: camera.ip_address,
    lastUpdate: camera.last_update,
    imageStatus: camera.image_status,
    status: mappedStatus
  };
};

const fetchCameras = async () => {
  try {
    const response = await api.getCameras();
    const nextCameras = Array.isArray(response.data)
      ? response.data.map(normalizeCamera)
      : [];

    cctvs.value = nextCameras;

    if (selectedCamera.value) {
      selectedCamera.value =
        nextCameras.find((camera) => camera.id === selectedCamera.value.id) ?? null;
    }
  } catch (error) {
    console.error('Error fetching cameras:', error);
    showToast('Failed to load camera data', 'error');
  } finally {
    loadingCameras.value = false;
  }
};

const totalCount = computed(() => cctvs.value.length);
const onlineCount = computed(() => cctvs.value.filter((camera) => camera.status === 'online').length);
const offlineCount = computed(() => cctvs.value.filter((camera) => camera.status === 'offline').length);
const noSignalCount = computed(() => cctvs.value.filter((camera) => camera.status === 'no_signal').length);
const blurryCount = computed(() => cctvs.value.filter((camera) => camera.status === 'blurry').length);

const checkBlurryCameras = async () => {
  if (isCheckingBlurry.value) return;

  const blurryTargets = cctvs.value.filter((camera) => camera.status === 'blurry');
  if (blurryTargets.length === 0) {
    showToast('No blurry cameras to check right now', 'info');
    return;
  }

  isCheckingBlurry.value = true;
  try {
    await Promise.all(blurryTargets.map((camera) => api.checkCameraBlur(camera.id)));
    await fetchCameras();
    showToast('Blurry cameras rechecked', 'success');
  } catch (error) {
    console.error('Error checking blurry cameras:', error);
    showToast('Failed to recheck blurry cameras', 'error');
  } finally {
    isCheckingBlurry.value = false;
  }
};

const filteredCameras = computed(() => {
  const query = searchQuery.value.trim().toLowerCase();
  let filtered = cctvs.value;

  if (query) {
    filtered = filtered.filter((camera) =>
      camera.name.toLowerCase().includes(query) ||
      (camera.ipAddress && camera.ipAddress.toLowerCase().includes(query))
    );
  }

  if (selectedFilter.value !== 'all') {
    filtered = filtered.filter((camera) => camera.status === selectedFilter.value);
  }

  return [...filtered].sort((a, b) => a.name.localeCompare(b.name));
});

const showToast = (message, type = 'info') => {
  toast.value = {
    show: true,
    message,
    type
  };
};

const closeToast = () => {
  toast.value.show = false;
};

const clearFilters = async () => {
  searchQuery.value = '';
  selectedFilter.value = 'all';
  await nextTick();
  mapViewRef.value?.fitToVisibleMarkers();
};

const selectFilter = (filterValue) => {
  selectedFilter.value = filterValue;
};

const selectFilterFromStats = (filterValue) => {
  selectFilter(filterValue);
  if (isMobile.value) {
    mobileFiltersOpen.value = false;
  }
};

const focusCamera = (camera) => {
  selectedCamera.value = camera;
  mapViewRef.value?.focusCamera(camera, true);
  if (isMobile.value) {
    mobileFiltersOpen.value = false;
  }
};

const handleMarkerSelect = (camera) => {
  selectedCamera.value = camera;
};

const buildStreamUrl = (cameraId) =>
  cameraId !== null && cameraId !== undefined ? `/api/cameras/${cameraId}/stream` : '';

const openStreamOverlay = (camera = selectedCamera.value) => {
  if (!camera) return;

  selectedCamera.value = camera;
  streamUrl.value = buildStreamUrl(camera.id);
  isStreamOpen.value = true;

  if (isMobile.value) {
    mobileFiltersOpen.value = false;
  }
};

const closeStreamOverlay = () => {
  isStreamOpen.value = false;
};

const openCameraDetails = (camera = selectedCamera.value) => {
  if (!camera) return;

  router.push({
    name: 'CameraView',
    params: { id: camera.id },
    query: {
      name: camera.name,
      location: camera.location,
      ip: camera.ipAddress,
      status: camera.status,
      imageStatus: camera.imageStatus,
      coordinates: `${camera.lat}, ${camera.lng}`,
      brand: camera.brand || 'N/A',
      lastUpdate: camera.lastUpdate || formatThailandDateTime()
    }
  });
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

const handleConfirmCancel = () => {
  confirmModal.value.show = false;
};

const toggleSidebar = () => {
  sidebarExpanded.value = !sidebarExpanded.value;
};

const openMobileFilters = () => {
  if (isMobile.value) {
    mobileDrawerTab.value = 'status';
    mobileFiltersOpen.value = true;
  }
};

const handleResize = () => {
  viewportWidth.value = window.innerWidth;
  viewportHeight.value = window.innerHeight;
  if (!isMobile.value) {
    mobileFiltersOpen.value = false;
  }
};

let pollInterval = null;

onMounted(() => {
  fetchCameras();
  pollInterval = setInterval(fetchCameras, 30000);
  window.addEventListener('resize', handleResize);
});

onBeforeUnmount(() => {
  if (pollInterval) clearInterval(pollInterval);
  window.removeEventListener('resize', handleResize);
});

watch(isMobile, (mobile) => {
  if (!mobile) {
    mobileFiltersOpen.value = false;
  }
});

watch(filteredCameras, (nextCameras) => {
  if (!selectedCamera.value) return;
  const stillVisible = nextCameras.some((camera) => camera.id === selectedCamera.value.id);
  if (!stillVisible) {
    selectedCamera.value = null;
  }
});

watch(selectedCamera, (camera) => {
  if (!camera) {
    isStreamOpen.value = false;
    streamUrl.value = '';
    return;
  }

  if (isStreamOpen.value) {
    streamUrl.value = buildStreamUrl(camera.id);
  }
});
</script>

<template>
  <div class="dashboard-page" :class="{ 'dashboard-page--mobile': isMobile }">
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

    <AppHeader
      :logo-url="logoUrl"
      :user-name="userName"
      :user-role="userRole"
      :compact-mode="isMobile"
      @camera-settings="goToCameraSettings"
      @logout="logout"
      @open-mobile-filters="openMobileFilters"
    />

    <section v-if="!isMobile" class="stats-strip">
      <StatsCards
        :total="totalCount"
        :online="onlineCount"
        :offline="offlineCount"
        :no-signal="noSignalCount"
        :blurry="blurryCount"
        :selected-filter="selectedFilter"
        :loading="loadingCameras"
        @select-filter="selectFilterFromStats"
        @check-blurry="checkBlurryCameras"
      />
    </section>

    <section
      class="workspace"
      :class="{
        'workspace--collapsed': !sidebarExpanded || isMobile,
        'workspace--mobile': isMobile
      }"
    >
      <aside
        v-if="!isMobile"
        class="sidebar-panel"
        :class="{ 'sidebar-panel--collapsed': !sidebarExpanded }"
      >
        <div class="sidebar-panel__header">
          <div v-if="sidebarExpanded" class="sidebar-heading">
            <h2>Camera Controls</h2>
            <p>Search, filter, and focus map markers.</p>
          </div>

          <button
            type="button"
            class="icon-btn"
            :aria-label="sidebarExpanded ? 'Collapse control panel' : 'Expand control panel'"
            @click="toggleSidebar"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
            </svg>
          </button>
        </div>

        <FiltersBar
          v-if="sidebarExpanded"
          :search-query="searchQuery"
          :selected-filter="selectedFilter"
          :filter-options="filterOptions"
          :cameras="filteredCameras"
          :loading="loadingCameras"
          :active-camera-id="activeCameraId"
          @update:search-query="searchQuery = $event"
          @update:selected-filter="selectFilter"
          @clear-filters="clearFilters"
          @focus-camera="focusCamera"
        />

        <div v-else class="collapsed-cta">
          <button type="button" @click="sidebarExpanded = true">Open Filters</button>
        </div>
      </aside>

      <main class="map-shell">
        <div class="map-shell__toolbar">
          <button
            v-if="!isMobile && !sidebarExpanded"
            type="button"
            class="toolbar-btn"
            @click="sidebarExpanded = true"
          >
            Show Filters
          </button>

          <button
            v-if="selectedCamera && !isStreamOpen && !isUser"
            type="button"
            class="toolbar-btn toolbar-btn--ghost"
            @click="openStreamOverlay(selectedCamera)"
          >
            View Stream
          </button>
        </div>

        <MapView
          ref="mapViewRef"
          :cameras="filteredCameras"
          :loading="loadingCameras"
          :active-camera-id="activeCameraId"
          :suspend-effects="isStreamOpen"
          @select-camera="handleMarkerSelect"
        />

        <transition name="stream-fade">
          <StreamOverlay
            v-if="isStreamOpen && selectedCamera"
            :camera="selectedCamera"
            :stream-url="streamUrl"
            @close="closeStreamOverlay"
          />
        </transition>

        <div v-if="!isStreamOpen && selectedCamera" class="camera-info-wrap">
          <CameraInfoPanel
            class="camera-info-panel"
            :camera="selectedCamera"
            :is-user="isUser"
            @view-stream="openStreamOverlay"
            @details="openCameraDetails"
            @close="selectedCamera = null"
          />
        </div>
      </main>
    </section>

    <transition name="drawer-fade">
      <div
        v-if="isMobile && mobileFiltersOpen"
        class="mobile-drawer-backdrop"
        @click.self="mobileFiltersOpen = false"
      >
        <aside class="mobile-drawer" role="dialog" aria-modal="true" aria-label="Dashboard menu">
          <header class="mobile-drawer__header">
            <div>
              <h2>Dashboard Menu</h2>
              <p>{{ filteredCameras.length }} cameras visible</p>
            </div>
            <button type="button" class="icon-btn" aria-label="Close filters panel" @click="mobileFiltersOpen = false">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </header>

          <div class="mobile-drawer__tabs" role="tablist" aria-label="Dashboard menu tabs">
            <button
              type="button"
              class="mobile-tab"
              :class="{ 'mobile-tab--active': mobileDrawerTab === 'status' }"
              role="tab"
              :aria-selected="mobileDrawerTab === 'status'"
              @click="mobileDrawerTab = 'status'"
            >
              Camera Status
            </button>
            <button
              type="button"
              class="mobile-tab"
              :class="{ 'mobile-tab--active': mobileDrawerTab === 'filters' }"
              role="tab"
              :aria-selected="mobileDrawerTab === 'filters'"
              @click="mobileDrawerTab = 'filters'"
            >
              Filters
            </button>
          </div>

          <section
            v-show="mobileDrawerTab === 'status'"
            class="mobile-drawer__section mobile-status-strip"
            aria-label="Camera status"
          >
            <h3>Camera Status</h3>
            <StatsCards
              :total="totalCount"
              :online="onlineCount"
              :offline="offlineCount"
              :no-signal="noSignalCount"
              :blurry="blurryCount"
              :selected-filter="selectedFilter"
              :loading="loadingCameras"
              @select-filter="selectFilterFromStats"
              @check-blurry="checkBlurryCameras"
            />
          </section>

          <section
            v-show="mobileDrawerTab === 'filters'"
            class="mobile-drawer__section"
            aria-label="Filters and search"
          >
            <h3>Filters & Search</h3>
            <FiltersBar
              :search-query="searchQuery"
              :selected-filter="selectedFilter"
              :filter-options="filterOptions"
              :cameras="filteredCameras"
              :loading="loadingCameras"
              :active-camera-id="activeCameraId"
              @update:search-query="searchQuery = $event"
              @update:selected-filter="selectFilter"
              @clear-filters="clearFilters"
              @focus-camera="focusCamera"
            />
          </section>
        </aside>
      </div>
    </transition>
  </div>
</template>

<style scoped>
.dashboard-page {
  --space-1: 8px;
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
  height: 100%;
  display: grid;
  grid-template-rows: minmax(0, 1fr);
  grid-template-columns: minmax(300px, 360px) 1fr;
  gap: var(--space-2);
  padding: 0 var(--space-3) var(--space-3);
  overflow: hidden;
}

.workspace--collapsed {
  grid-template-columns: 88px 1fr;
}

.workspace--mobile {
  display: block;
  padding: 0 12px 12px;
}

.workspace--mobile .map-shell {
  /* Apply mobile map sizing for portrait and rotated phones. */
  height: clamp(300px, calc(100dvh - 108px), 88dvh);
  min-height: 300px;
}

.workspace--mobile .map-shell__toolbar {
  top: 8px;
  left: 8px;
  right: 8px;
  max-width: none;
  gap: 6px;
  flex-wrap: wrap;
}

.workspace--mobile .toolbar-btn {
  padding: 7px 10px;
  font-size: 0.76rem;
}

.workspace--mobile .camera-info-wrap {
  top: auto;
  bottom: 8px;
  right: 8px;
  left: 8px;
  width: auto;
}

.sidebar-panel {
  border: 1px solid rgba(148, 163, 184, 0.24);
  background: rgba(15, 23, 42, 0.74);
  border-radius: 16px;
  padding: 12px;
  height: 100%;
  min-height: 0;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.sidebar-panel--collapsed {
  align-items: center;
  padding: 12px 8px;
}

.sidebar-panel__header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 10px;
  margin-bottom: 12px;
}

.sidebar-heading h2 {
  margin: 0;
  color: #f8fafc;
  font-size: 1.02rem;
}

.sidebar-heading p {
  margin: 4px 0 0;
  color: #94a3b8;
  font-size: 0.78rem;
  line-height: 1.3;
}

.icon-btn {
  width: 34px;
  height: 34px;
  border: 1px solid rgba(148, 163, 184, 0.28);
  border-radius: 10px;
  background: rgba(15, 23, 42, 0.76);
  color: #cbd5e1;
  cursor: pointer;
  display: grid;
  place-items: center;
  flex-shrink: 0;
}

.icon-btn svg {
  width: 16px;
  height: 16px;
}

.sidebar-panel--collapsed .icon-btn svg {
  transform: rotate(180deg);
}

.icon-btn:focus-visible,
.toolbar-btn:focus-visible,
.collapsed-cta button:focus-visible {
  outline: 2px solid #38bdf8;
  outline-offset: 2px;
}

.collapsed-cta {
  display: grid;
  place-items: center;
  flex: 1;
}

.collapsed-cta button {
  width: 100%;
  border: 1px solid rgba(148, 163, 184, 0.28);
  border-radius: 10px;
  background: rgba(15, 23, 42, 0.76);
  color: #cbd5e1;
  font-size: 0.8rem;
  padding: 10px 8px;
  cursor: pointer;
}

.map-shell {
  position: relative;
  height: 100%;
  border: 1px solid rgba(148, 163, 184, 0.24);
  border-radius: 16px;
  overflow: hidden;
  min-height: 0;
  background: rgba(15, 23, 42, 0.5);
}

.map-shell__toolbar {
  position: absolute;
  top: 12px;
  left: 12px;
  max-width: calc(100% - 24px);
  z-index: 9;
  display: flex;
  gap: 8px;
}

.toolbar-btn {
  border: 1px solid rgba(148, 163, 184, 0.28);
  border-radius: 10px;
  background: rgba(15, 23, 42, 0.88);
  color: #e2e8f0;
  padding: 8px 12px;
  font-size: 0.8rem;
  font-weight: 600;
  cursor: pointer;
}

.toolbar-btn--ghost {
  background: rgba(2, 6, 23, 0.74);
}

.camera-info-wrap {
  position: absolute;
  top: 12px;
  right: 12px;
  z-index: 9;
  width: min(340px, calc(100% - 24px));
  pointer-events: none;
}

.camera-info-panel {
  pointer-events: auto;
}

.stream-fade-enter-active,
.stream-fade-leave-active {
  transition: opacity 0.18s ease;
}

.stream-fade-enter-from,
.stream-fade-leave-to {
  opacity: 0;
}

.mobile-drawer-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(2, 6, 23, 0.5);
  backdrop-filter: blur(6px);
  z-index: 2000;
}

.mobile-drawer {
  position: absolute;
  left: 10px;
  right: 10px;
  bottom: 0;
  max-height: min(88vh, 88dvh);
  background: rgba(15, 23, 42, 0.62);
  border: 1px solid rgba(148, 163, 184, 0.3);
  border-top-left-radius: 18px;
  border-top-right-radius: 18px;
  padding: 14px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  overflow: auto;
  backdrop-filter: blur(16px) saturate(140%);
}

.mobile-drawer__header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}

.mobile-drawer__header h2 {
  margin: 0;
  color: #f8fafc;
  font-size: 1rem;
}

.mobile-drawer__header p {
  margin: 4px 0 0;
  color: #94a3b8;
  font-size: 0.8rem;
}

.mobile-drawer__section h3 {
  margin: 0 0 8px;
  color: #f8fafc;
  font-size: 0.9rem;
}

.mobile-drawer__tabs {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 8px;
}

.mobile-tab {
  height: 36px;
  border-radius: 10px;
  border: 1px solid rgba(148, 163, 184, 0.28);
  background: rgba(15, 23, 42, 0.28);
  color: #cbd5e1;
  font-size: 0.78rem;
  font-weight: 600;
  cursor: pointer;
}

.mobile-tab--active {
  background: rgba(14, 165, 233, 0.24);
  border-color: rgba(56, 189, 248, 0.56);
  color: #e0f2fe;
  box-shadow: inset 0 0 0 1px rgba(56, 189, 248, 0.26);
}

.mobile-status-strip :deep(.stats-grid) {
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 8px;
}

.mobile-status-strip :deep(.stats-card) {
  min-height: 72px;
  padding: 10px;
}

.mobile-status-strip :deep(.stats-value) {
  font-size: 1.14rem;
}

.drawer-fade-enter-active,
.drawer-fade-leave-active {
  transition: opacity 0.2s ease;
}

.drawer-fade-enter-from,
.drawer-fade-leave-to {
  opacity: 0;
}

@media (max-width: 1199px) {
  .workspace {
    grid-template-columns: minmax(260px, 320px) 1fr;
    padding: 0 var(--space-2) var(--space-2);
  }

  .workspace--collapsed {
    grid-template-columns: 78px 1fr;
  }

  .stats-strip {
    padding: 12px var(--space-2);
  }
}

@media (max-width: 1024px) {
  .camera-info-wrap {
    top: auto;
    bottom: 12px;
  }
}

@media (max-width: 767px) {
  .mobile-drawer {
    left: 6px;
    right: 6px;
    padding: 12px;
  }
}

.dashboard-page--mobile {
  height: auto;
  min-height: 100vh;
  min-height: 100dvh;
  overflow: auto;
}
</style>
