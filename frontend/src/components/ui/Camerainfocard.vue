<template>
  <div class="custom-popup">
    <div class="popup-header">
      <div class="popup-title">{{ camera.name }}</div>
      <div class="popup-status-badge" :class="camera.status">
        <span class="status-dot"></span>
        {{ statusText }}
      </div>
    </div>
    <div class="popup-body">
      <div class="popup-info-grid">
        <div class="info-item">
          <div class="info-label">
            <svg class="info-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9"></path>
            </svg>
            IP Address
          </div>
          <div class="info-value ip-value">{{ camera.ipAddress || 'N/A' }}</div>
        </div>
        
        <div class="info-item">
          <div class="info-label">
            <svg class="info-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"></path>
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"></path>
            </svg>
            Location
          </div>
          <div class="info-value">{{ camera.location }}</div>
        </div>
        
        <div class="info-item">
          <div class="info-label">
            <svg class="info-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
            </svg>
            Last Update
          </div>
          <div class="info-value">{{ camera.lastUpdate || 'N/A' }}</div>
        </div>
        
        <div class="info-item">
          <div class="info-label">
            <svg class="info-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7"></path>
            </svg>
            Coordinates
          </div>
          <div class="info-value coords-value">{{ formattedCoordinates }}</div>
        </div>
      </div>
      
      <div class="popup-actions">
        <button 
          @click="handleViewCamera"
          class="view-camera-btn"
        >
          <svg class="btn-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"></path>
          </svg>
          View Camera
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  camera: {
    type: Object,
    required: true
  }
});

const emit = defineEmits(['view-camera']);

const statusText = computed(() => {
  return props.camera.status === "up" ? "Online" : "Offline";
});

const formattedCoordinates = computed(() => {
  return `${props.camera.lat.toFixed(4)}, ${props.camera.lng.toFixed(4)}`;
});

const handleViewCamera = () => {
  emit('view-camera', props.camera.name);
};
</script>

<style scoped>
/* Custom Popup Container - FIXED ZOOM SCALING */
.custom-popup {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  width: 360px;
  background: #1a202c;
  /* CRITICAL: Force fixed dimensions regardless of map zoom */
  transform: none !important;
  transform-origin: center center !important;
  zoom: 1 !important;
}

/* CRITICAL: Prevent all child elements from scaling */
.custom-popup * {
  transform: none !important;
  zoom: 1 !important;
}

/* Header Section */
.popup-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 24px;
  padding-right: 55px;
  border-top-left-radius: 14px;
  border-top-right-radius: 14px;
}

.popup-title {
  font-size: 20px;
  font-weight: 700;
  color: white;
  margin-bottom: 12px;
  letter-spacing: -0.5px;
  line-height: 1.3;
}

.popup-status-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  border-radius: 24px;
  font-size: 13px;
  font-weight: 600;
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.3);
  color: white;
}

.popup-status-badge .status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  animation: pulse-dot 2s ease-in-out infinite;
}

.popup-status-badge.up .status-dot {
  background: #10b981;
  box-shadow: 0 0 8px rgba(16, 185, 129, 0.8);
}

.popup-status-badge.down .status-dot {
  background: #ef4444;
  box-shadow: 0 0 8px rgba(239, 68, 68, 0.8);
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

/* Body Section */
.popup-body {
  background: #1a202c;
}

/* Info Grid */
.popup-info-grid {
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.info-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 11px;
  font-weight: 700;
  color: rgba(255, 255, 255, 0.5);
  text-transform: uppercase;
  letter-spacing: 0.8px;
}

.info-icon {
  width: 16px;
  height: 16px;
  color: rgba(102, 126, 234, 0.7);
  flex-shrink: 0;
}

.info-value {
  font-size: 15px;
  font-weight: 500;
  color: white;
  padding-left: 24px;
  line-height: 1.5;
}

.info-value.ip-value {
  font-family: 'SF Mono', 'Consolas', 'Monaco', monospace;
  font-size: 14px;
  color: #667eea;
  background: rgba(102, 126, 234, 0.12);
  padding: 8px 12px;
  padding-left: 12px;
  margin-left: 0;
  border-radius: 8px;
  border: 1px solid rgba(102, 126, 234, 0.2);
  display: inline-block;
  font-weight: 600;
}

.info-value.coords-value {
  font-family: 'SF Mono', 'Consolas', 'Monaco', monospace;
  font-size: 13px;
  color: rgba(255, 255, 255, 0.8);
}

/* Actions Section */
.popup-actions {
  padding: 0 24px 24px;
}

.view-camera-btn {
  width: 100%;
  padding: 14px 24px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 700;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 4px 16px rgba(102, 126, 234, 0.4);
  letter-spacing: 0.5px;
  text-transform: uppercase;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  position: relative;
  overflow: hidden;
}

.view-camera-btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, #7c8ef7 0%, #8b5cb5 100%);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.view-camera-btn:hover::before {
  opacity: 1;
}

.view-camera-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(102, 126, 234, 0.6);
}

.view-camera-btn:active {
  transform: translateY(0);
}

.view-camera-btn > * {
  position: relative;
  z-index: 1;
}

.btn-icon {
  width: 18px;
  height: 18px;
}
</style>