<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue';

const props = defineProps({
  camera: {
    type: Object,
    default: null
  },
  streamUrl: {
    type: String,
    default: ''
  }
});

const emit = defineEmits(['close']);

const streamFrame = ref(null);
const streamFailed = ref(false);
const isFullscreen = ref(false);
const now = ref(new Date());

const getStatusLabel = (status) => {
  if (status === 'offline') return 'Offline';
  if (status === 'no_signal') return 'No Signal';
  if (status === 'blurry') return 'Blurry';
  return 'Online';
};

const statusLabel = computed(() => getStatusLabel(props.camera?.status));
const statusClass = computed(() => props.camera?.status || 'online');
const hasStreamUrl = computed(() => Boolean(props.streamUrl));
const timestampText = computed(() => props.camera?.lastUpdate || now.value.toLocaleString());

const handleImageError = () => {
  streamFailed.value = true;
};

const handleImageLoad = () => {
  streamFailed.value = false;
};

const enterFullscreen = (element) =>
  (element.requestFullscreen ?? element.webkitRequestFullscreen)?.call(element);

const exitFullscreen = () =>
  (document.exitFullscreen ?? document.webkitExitFullscreen)?.call(document);

const getFullscreenElement = () =>
  document.fullscreenElement || document.webkitFullscreenElement || null;

const syncFullscreenState = () => {
  isFullscreen.value = Boolean(getFullscreenElement());
};

const toggleFullscreen = () => {
  if (!streamFrame.value) return;
  if (getFullscreenElement()) {
    exitFullscreen();
    return;
  }
  enterFullscreen(streamFrame.value);
};

watch(
  () => props.streamUrl,
  () => {
    streamFailed.value = false;
  },
  { immediate: true }
);

watch(
  () => props.camera?.id,
  () => {
    streamFailed.value = false;
  }
);

let clockTimer = null;

onMounted(() => {
  clockTimer = setInterval(() => {
    now.value = new Date();
  }, 1000);

  document.addEventListener('fullscreenchange', syncFullscreenState);
  document.addEventListener('webkitfullscreenchange', syncFullscreenState);
});

onBeforeUnmount(() => {
  if (clockTimer) {
    clearInterval(clockTimer);
    clockTimer = null;
  }
  document.removeEventListener('fullscreenchange', syncFullscreenState);
  document.removeEventListener('webkitfullscreenchange', syncFullscreenState);
});
</script>

<template>
  <section
    class="stream-overlay"
    role="dialog"
    aria-modal="false"
    aria-label="Live camera stream viewer"
  >
    <header class="stream-header">
      <button type="button" class="back-btn" @click="emit('close')">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
        </svg>
        Back to Map
      </button>

      <div class="camera-summary">
        <p>Live Camera View</p>
        <h3>{{ camera?.name || 'Selected Camera' }}</h3>
      </div>

      <span class="status-badge" :class="`status-badge--${statusClass}`">
        <span class="status-dot"></span>
        {{ statusLabel }}
      </span>
    </header>

    <div ref="streamFrame" class="stream-frame">
      <div v-if="!hasStreamUrl || streamFailed" class="stream-placeholder">
        <div class="placeholder-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
          </svg>
        </div>
        <h4>Stream Unavailable</h4>
        <p>{{ camera?.ipAddress || 'Camera IP unavailable' }}</p>
      </div>

      <img
        v-else
        :src="streamUrl"
        class="stream-image"
        alt="Live camera feed"
        @error="handleImageError"
        @load="handleImageLoad"
      />

      <div v-if="hasStreamUrl && !streamFailed" class="timestamp-pill">
        {{ timestampText }}
      </div>

      <button
        type="button"
        class="fullscreen-btn"
        :title="isFullscreen ? 'Exit fullscreen' : 'Enter fullscreen'"
        @click="toggleFullscreen"
      >
        <svg v-if="!isFullscreen" viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4" />
        </svg>
        <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
    </div>
  </section>
</template>

<style scoped>
.stream-overlay {
  position: absolute;
  inset: 0;
  z-index: 12;
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding: 12px;
  background:
    radial-gradient(circle at 14% 12%, rgba(102, 126, 234, 0.24), transparent 48%),
    radial-gradient(circle at 84% 88%, rgba(14, 165, 233, 0.15), transparent 42%),
    rgba(2, 6, 23, 0.95);
  pointer-events: auto;
}

.stream-header {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr) auto;
  align-items: center;
  gap: 10px;
  padding: 10px;
  border: 1px solid rgba(148, 163, 184, 0.28);
  border-radius: 12px;
  background: rgba(15, 23, 42, 0.82);
}

.back-btn {
  border: 1px solid rgba(148, 163, 184, 0.3);
  border-radius: 10px;
  background: rgba(30, 41, 59, 0.72);
  color: #f8fafc;
  font-size: 0.82rem;
  font-weight: 700;
  line-height: 1;
  padding: 9px 12px;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.back-btn svg {
  width: 15px;
  height: 15px;
}

.camera-summary {
  min-width: 0;
}

.camera-summary p {
  margin: 0;
  font-size: 0.68rem;
  color: #94a3b8;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}

.camera-summary h3 {
  margin: 4px 0 0;
  font-size: 1rem;
  color: #f8fafc;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.status-badge {
  border: 1px solid transparent;
  border-radius: 999px;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 6px 10px;
  font-size: 0.74rem;
  font-weight: 700;
  white-space: nowrap;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 999px;
}

.status-badge--online {
  background: rgba(16, 185, 129, 0.18);
  border-color: rgba(16, 185, 129, 0.4);
  color: #6ee7b7;
}

.status-badge--online .status-dot {
  background: #10b981;
}

.status-badge--offline {
  background: rgba(239, 68, 68, 0.18);
  border-color: rgba(239, 68, 68, 0.4);
  color: #fca5a5;
}

.status-badge--offline .status-dot {
  background: #ef4444;
}

.status-badge--no_signal {
  background: rgba(59, 130, 246, 0.18);
  border-color: rgba(59, 130, 246, 0.4);
  color: #93c5fd;
}

.status-badge--no_signal .status-dot {
  background: #3b82f6;
}

.status-badge--blurry {
  background: rgba(249, 115, 22, 0.18);
  border-color: rgba(249, 115, 22, 0.4);
  color: #fdba74;
}

.status-badge--blurry .status-dot {
  background: #f97316;
}

.stream-frame {
  position: relative;
  flex: 1;
  min-height: 0;
  border-radius: 14px;
  overflow: hidden;
  border: 1px solid rgba(148, 163, 184, 0.28);
  background: rgba(2, 6, 23, 0.9);
}

.stream-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.stream-placeholder {
  position: absolute;
  inset: 0;
  display: grid;
  place-items: center;
  gap: 6px;
  padding: 16px;
  text-align: center;
  background: linear-gradient(135deg, rgba(15, 23, 42, 0.96) 0%, rgba(30, 41, 59, 0.94) 100%);
}

.placeholder-icon {
  width: 64px;
  height: 64px;
  border-radius: 16px;
  display: grid;
  place-items: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #ffffff;
  box-shadow: 0 8px 24px rgba(102, 126, 234, 0.36);
}

.placeholder-icon svg {
  width: 28px;
  height: 28px;
}

.stream-placeholder h4 {
  margin: 0;
  color: #f8fafc;
  font-size: 1.1rem;
}

.stream-placeholder p {
  margin: 0;
  color: #93c5fd;
  font-family: 'Courier New', monospace;
  font-size: 0.92rem;
}

.timestamp-pill {
  position: absolute;
  top: 14px;
  left: 14px;
  z-index: 2;
  border: 1px solid rgba(148, 163, 184, 0.34);
  background: rgba(2, 6, 23, 0.72);
  color: #f8fafc;
  border-radius: 999px;
  padding: 6px 12px;
  font-size: 0.8rem;
  letter-spacing: 0.02em;
}

.fullscreen-btn {
  position: absolute;
  right: 14px;
  bottom: 14px;
  z-index: 2;
  width: 42px;
  height: 42px;
  border: 1px solid rgba(148, 163, 184, 0.34);
  border-radius: 10px;
  background: rgba(2, 6, 23, 0.72);
  color: #e2e8f0;
  cursor: pointer;
  display: grid;
  place-items: center;
}

.fullscreen-btn svg {
  width: 20px;
  height: 20px;
}

.back-btn:focus-visible,
.fullscreen-btn:focus-visible {
  outline: 2px solid #38bdf8;
  outline-offset: 2px;
}

@media (max-width: 1024px) {
  .stream-header {
    grid-template-columns: 1fr auto;
    grid-template-areas:
      'back status'
      'summary summary';
  }

  .back-btn {
    grid-area: back;
    justify-self: start;
  }

  .camera-summary {
    grid-area: summary;
  }

  .status-badge {
    grid-area: status;
    justify-self: end;
  }
}

@media (max-width: 767px) {
  .stream-overlay {
    position: fixed;
    inset: 0;
    z-index: 2500;
    border-radius: 0;
    padding: calc(10px + env(safe-area-inset-top)) 10px calc(10px + env(safe-area-inset-bottom));
  }

  .stream-header {
    padding: 10px;
  }

  .camera-summary h3 {
    font-size: 0.94rem;
  }

  .timestamp-pill {
    left: 10px;
    top: 10px;
    font-size: 0.72rem;
    padding: 5px 10px;
  }

  .fullscreen-btn {
    right: 10px;
    bottom: 10px;
  }
}
</style>
