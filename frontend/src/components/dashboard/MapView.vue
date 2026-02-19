<script setup>
import { onBeforeUnmount, onMounted, ref, shallowRef, watch } from 'vue';
import LoadingSpinner from '../ui/LoadingSpinner.vue';

const props = defineProps({
  cameras: {
    type: Array,
    default: () => []
  },
  loading: {
    type: Boolean,
    default: false
  },
  activeCameraId: {
    type: [String, Number],
    default: null
  }
});

const emit = defineEmits(['select-camera']);

const mapContainer = ref(null);
const map = shallowRef(null);
const markers = shallowRef([]);
const markerCluster = shallowRef(null);
const isInitializing = ref(true);
const mapError = ref('');
const markerLookup = new Map();

const DEFAULT_CENTER = { lat: 20.0443, lng: 99.8937 };
const GOOGLE_MAPS_KEY = 'AIzaSyDBMns5PZsDXIfXsT1E1_79jx2934NTUHM';

const loadScript = (id, src) =>
  new Promise((resolve, reject) => {
    const existing = document.getElementById(id);
    if (existing) {
      if (existing.dataset.loaded === 'true') {
        resolve();
        return;
      }
      existing.addEventListener('load', resolve, { once: true });
      existing.addEventListener('error', () => reject(new Error(`Failed to load ${src}`)), { once: true });
      return;
    }

    const script = document.createElement('script');
    script.id = id;
    script.src = src;
    script.async = true;
    script.defer = true;
    script.dataset.loaded = 'false';
    script.onload = () => {
      script.dataset.loaded = 'true';
      resolve();
    };
    script.onerror = () => reject(new Error(`Failed to load ${src}`));
    document.head.appendChild(script);
  });

const ensureMapLibraries = async () => {
  if (!(window.google && window.google.maps)) {
    await loadScript(
      'google-maps-script',
      `https://maps.googleapis.com/maps/api/js?key=${GOOGLE_MAPS_KEY}`
    );
  }

  if (!window.MarkerClusterer) {
    try {
      await loadScript(
        'marker-clusterer-script',
        'https://unpkg.com/@googlemaps/markerclustererplus/dist/index.min.js'
      );
    } catch (error) {
      console.warn('Cluster library failed to load. Falling back to plain markers.', error);
    }
  }
};

const getStatusColor = (status) => {
  if (status === 'offline') return '#ef4444';
  if (status === 'no_signal') return '#f59e0b';
  if (status === 'blurry') return '#ec4899';
  return '#22c55e';
};

const createMarkerIcon = (status, isActive = false) => {
  const baseColor = getStatusColor(status);
  const borderColor = isActive ? '#f8fafc' : '#0f172a';
  const size = isActive ? 40 : 34;

  return {
    url: `data:image/svg+xml;charset=UTF-8,${encodeURIComponent(
      `<svg xmlns="http://www.w3.org/2000/svg" width="${size}" height="${size}" viewBox="0 0 ${size} ${size}">
        <circle cx="${size / 2}" cy="${size / 2}" r="${size / 2 - 1}" fill="${baseColor}" stroke="${borderColor}" stroke-width="2" />
        <path d="M${size * 0.32} ${size * 0.38}h${size * 0.26}v${size * 0.24}h-${size * 0.26}z" fill="white"/>
        <path d="M${size * 0.58} ${size * 0.43}l${size * 0.13}-${size * 0.07}v${size * 0.24}l-${size * 0.13}-${size * 0.07}z" fill="white"/>
        <circle cx="${size * 0.46}" cy="${size * 0.5}" r="${size * 0.08}" fill="${baseColor}" stroke="white" stroke-width="1.6"/>
      </svg>`
    )}`,
    scaledSize: new google.maps.Size(size, size),
    anchor: new google.maps.Point(size / 2, size / 2)
  };
};

const buildClusterStyle = (size, fill, ring) => ({
  url: `data:image/svg+xml;charset=UTF-8,${encodeURIComponent(
    `<svg xmlns="http://www.w3.org/2000/svg" width="${size}" height="${size}" viewBox="0 0 ${size} ${size}">
      <circle cx="${size / 2}" cy="${size / 2}" r="${size / 2 - 2}" fill="${fill}" />
      <circle cx="${size / 2}" cy="${size / 2}" r="${size / 2 - 4}" fill="none" stroke="${ring}" stroke-width="2" />
    </svg>`
  )}`,
  width: size,
  height: size,
  textColor: '#f8fafc',
  textSize: size < 52 ? 12 : 14,
  fontWeight: '700'
});

const clearMarkers = () => {
  if (markerCluster.value) {
    markerCluster.value.clearMarkers();
    markerCluster.value = null;
  }

  markers.value.forEach((marker) => {
    google.maps.event.clearInstanceListeners(marker);
    marker.setMap(null);
  });

  markers.value = [];
  markerLookup.clear();
};

const fitToVisibleMarkers = () => {
  if (!map.value || markers.value.length === 0) return;

  if (markers.value.length === 1) {
    map.value.setCenter(markers.value[0].getPosition());
    map.value.setZoom(17);
    return;
  }

  const bounds = new google.maps.LatLngBounds();
  markers.value.forEach((marker) => bounds.extend(marker.getPosition()));
  map.value.fitBounds(bounds, 80);

  google.maps.event.addListenerOnce(map.value, 'bounds_changed', () => {
    if ((map.value.getZoom() || 0) > 18) {
      map.value.setZoom(18);
    }
  });
};

const highlightActiveMarker = (cameraId) => {
  markers.value.forEach((marker) => {
    const isActive = marker.cameraId === cameraId;
    marker.setIcon(createMarkerIcon(marker.cameraStatus, isActive));
    marker.setZIndex(isActive ? 999 : 1);
  });
};

const renderMarkers = (autoFit = true) => {
  if (!map.value) return;

  clearMarkers();

  const visibleCameras = props.cameras.filter(
    (camera) =>
      Number.isFinite(camera.lat) &&
      Number.isFinite(camera.lng) &&
      camera.lat !== 0 &&
      camera.lng !== 0
  );

  const nextMarkers = visibleCameras.map((camera) => {
    const marker = new google.maps.Marker({
      position: { lat: camera.lat, lng: camera.lng },
      title: camera.name,
      icon: createMarkerIcon(camera.status, camera.id === props.activeCameraId),
      map: window.MarkerClusterer ? null : map.value
    });

    marker.cameraId = camera.id;
    marker.cameraStatus = camera.status;
    marker.cameraData = camera;

    marker.addListener('click', () => {
      emit('select-camera', camera);
      highlightActiveMarker(camera.id);
    });

    markerLookup.set(camera.id, marker);
    return marker;
  });

  markers.value = nextMarkers;

  if (window.MarkerClusterer && nextMarkers.length > 1) {
    markerCluster.value = new window.MarkerClusterer(map.value, nextMarkers, {
      gridSize: 56,
      maxZoom: 18,
      minimumClusterSize: 2,
      zoomOnClick: false,
      styles: [
        buildClusterStyle(44, '#0369a1', '#7dd3fc'),
        buildClusterStyle(52, '#0e7490', '#5eead4'),
        buildClusterStyle(60, '#155e75', '#67e8f9')
      ]
    });

    google.maps.event.addListener(markerCluster.value, 'clusterclick', (cluster) => {
      const bounds = cluster.getBounds?.();
      if (bounds) {
        map.value.fitBounds(bounds);
      }
      map.value.setZoom(Math.min((map.value.getZoom() || 10) + 2, 19));
    });
  } else {
    nextMarkers.forEach((marker) => marker.setMap(map.value));
  }

  if (autoFit) {
    fitToVisibleMarkers();
  }

  highlightActiveMarker(props.activeCameraId);
};

const focusCamera = (camera, shouldZoom = true) => {
  if (!map.value || !camera) return;

  const marker = markerLookup.get(camera.id);
  if (marker) {
    map.value.panTo(marker.getPosition());
    if (shouldZoom) {
      map.value.setZoom(Math.max(map.value.getZoom() || 16, 17));
    }
    marker.setAnimation(google.maps.Animation.BOUNCE);
    setTimeout(() => marker.setAnimation(null), 650);
    emit('select-camera', marker.cameraData);
    highlightActiveMarker(marker.cameraId);
    return;
  }

  if (Number.isFinite(camera.lat) && Number.isFinite(camera.lng)) {
    map.value.panTo({ lat: camera.lat, lng: camera.lng });
    if (shouldZoom) {
      map.value.setZoom(Math.max(map.value.getZoom() || 16, 17));
    }
    emit('select-camera', camera);
  }
};

defineExpose({
  focusCamera,
  fitToVisibleMarkers
});

const initMap = async () => {
  try {
    await ensureMapLibraries();

    if (!mapContainer.value) return;

    map.value = new google.maps.Map(mapContainer.value, {
      center: DEFAULT_CENTER,
      zoom: 16,
      mapTypeId: 'hybrid',
      mapTypeControl: false,
      streetViewControl: false,
      fullscreenControl: false,
      gestureHandling: 'greedy',
      clickableIcons: false
    });

    renderMarkers(true);
  } catch (error) {
    console.error('Map initialization failed:', error);
    mapError.value = 'Unable to load the map at the moment.';
  } finally {
    isInitializing.value = false;
  }
};

onMounted(() => {
  initMap();
});

onBeforeUnmount(() => {
  if (map.value) {
    google.maps.event.clearInstanceListeners(map.value);
  }
  clearMarkers();
  map.value = null;
});

watch(
  () => props.cameras,
  () => {
    if (map.value) {
      renderMarkers(true);
    }
  },
  { deep: true }
);

watch(
  () => props.activeCameraId,
  (cameraId) => {
    if (map.value) {
      highlightActiveMarker(cameraId);
    }
  }
);
</script>

<template>
  <div class="map-view">
    <div ref="mapContainer" class="map-canvas"></div>

    <div v-if="isInitializing" class="map-overlay">
      <LoadingSpinner size="large" message="Loading map..." />
    </div>

    <div v-else-if="loading" class="map-overlay map-overlay--soft">
      <LoadingSpinner size="medium" message="Syncing camera status..." />
    </div>

    <div v-if="!isInitializing && !loading && cameras.length === 0" class="empty-state">
      <h3>No Cameras Found</h3>
      <p>Try adjusting filters or search terms to display cameras on the map.</p>
    </div>

    <div v-if="mapError" class="map-error">
      {{ mapError }}
    </div>
  </div>
</template>

<style scoped>
.map-view {
  position: relative;
  width: 100%;
  height: 100%;
  min-height: 480px;
}

.map-canvas {
  width: 100%;
  height: 100%;
}

.map-overlay {
  position: absolute;
  inset: 0;
  background: rgba(2, 6, 23, 0.74);
  display: grid;
  place-items: center;
  z-index: 6;
}

.map-overlay--soft {
  background: rgba(2, 6, 23, 0.36);
  pointer-events: none;
}

.empty-state {
  position: absolute;
  left: 50%;
  bottom: 24px;
  transform: translateX(-50%);
  z-index: 5;
  background: rgba(15, 23, 42, 0.92);
  border: 1px solid rgba(148, 163, 184, 0.3);
  border-radius: 12px;
  padding: 14px 16px;
  width: min(420px, calc(100% - 32px));
  text-align: center;
}

.empty-state h3 {
  margin: 0 0 4px;
  color: #f8fafc;
  font-size: 0.95rem;
}

.empty-state p {
  margin: 0;
  color: #94a3b8;
  font-size: 0.82rem;
  line-height: 1.4;
}

.map-error {
  position: absolute;
  left: 50%;
  top: 16px;
  transform: translateX(-50%);
  z-index: 7;
  background: rgba(127, 29, 29, 0.92);
  color: #fecaca;
  padding: 10px 14px;
  border-radius: 10px;
  border: 1px solid rgba(252, 165, 165, 0.4);
  font-size: 0.85rem;
}

@media (max-width: 768px) {
  .map-view {
    min-height: 62vh;
  }
}
</style>
