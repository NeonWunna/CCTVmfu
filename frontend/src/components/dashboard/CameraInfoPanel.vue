<script setup>
import { computed } from 'vue';

const props = defineProps({
  camera: {
    type: Object,
    default: null
  }
});

defineEmits(['view-stream', 'details', 'close']);

const statusText = computed(() => {
  if (!props.camera) return '';
  if (props.camera.status === 'offline') return 'Offline';
  if (props.camera.status === 'no_signal') return 'No Signal';
  if (props.camera.status === 'blurry') return 'Blurry';
  return 'Online';
});

const hasCamera = computed(() => Boolean(props.camera));
</script>

<template>
  <aside
    class="camera-info"
    :class="{ 'camera-info--empty': !hasCamera }"
    aria-live="polite"
  >
    <template v-if="hasCamera">
      <header class="camera-info__header">
        <div>
          <p>Selected Camera</p>
          <h3>{{ camera.name }}</h3>
        </div>
        <button type="button" class="close-btn" aria-label="Close camera details" @click="$emit('close')">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </header>

      <span class="status-chip" :class="`status-chip--${camera.status}`">{{ statusText }}</span>

      <dl class="camera-meta">
        <div>
          <dt>IP Address</dt>
          <dd>{{ camera.ipAddress || 'N/A' }}</dd>
        </div>
        <div>
          <dt>Location</dt>
          <dd>{{ camera.location || 'N/A' }}</dd>
        </div>
        <div>
          <dt>Last Updated</dt>
          <dd>{{ camera.lastUpdate || 'N/A' }}</dd>
        </div>
      </dl>

      <div class="actions">
        <button type="button" class="primary" @click="$emit('view-stream', camera)">
          View Stream
        </button>
        <button type="button" class="secondary" @click="$emit('details', camera)">
          Details
        </button>
      </div>
    </template>

    <template v-else>
      <h3>Select a Camera</h3>
      <p>Click a marker or choose a camera in the filters panel to inspect details.</p>
    </template>
  </aside>
</template>

<style scoped>
.camera-info {
  border: 1px solid rgba(148, 163, 184, 0.24);
  border-radius: 14px;
  background: rgba(15, 23, 42, 0.9);
  backdrop-filter: blur(12px);
  box-shadow: 0 12px 24px rgba(2, 6, 23, 0.35);
  color: #e2e8f0;
  padding: 14px;
  pointer-events: auto;
}

.camera-info--empty {
  text-align: left;
}

.camera-info--empty h3 {
  margin: 0 0 6px;
  font-size: 1rem;
  color: #f8fafc;
}

.camera-info--empty p {
  margin: 0;
  color: #94a3b8;
  font-size: 0.85rem;
  line-height: 1.4;
}

.camera-info__header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
}

.camera-info__header p {
  margin: 0;
  color: #94a3b8;
  font-size: 0.72rem;
  text-transform: uppercase;
  letter-spacing: 0.06em;
}

.camera-info__header h3 {
  margin: 4px 0 0;
  font-size: 1.05rem;
  color: #f8fafc;
}

.close-btn {
  width: 30px;
  height: 30px;
  border-radius: 8px;
  border: 1px solid rgba(148, 163, 184, 0.3);
  background: rgba(30, 41, 59, 0.7);
  color: #cbd5e1;
  cursor: pointer;
  display: grid;
  place-items: center;
  flex-shrink: 0;
}

.close-btn svg {
  width: 14px;
  height: 14px;
}

.close-btn:focus-visible,
.actions button:focus-visible {
  outline: 2px solid #38bdf8;
  outline-offset: 2px;
}

.status-chip {
  display: inline-flex;
  margin-top: 10px;
  margin-bottom: 12px;
  border-radius: 999px;
  border: 1px solid transparent;
  padding: 5px 10px;
  font-size: 0.75rem;
  font-weight: 700;
}

.status-chip--online {
  background: rgba(34, 197, 94, 0.2);
  color: #86efac;
  border-color: rgba(34, 197, 94, 0.34);
}

.status-chip--offline {
  background: rgba(239, 68, 68, 0.2);
  color: #fca5a5;
  border-color: rgba(239, 68, 68, 0.34);
}

.status-chip--no_signal {
  background: rgba(245, 158, 11, 0.2);
  color: #fcd34d;
  border-color: rgba(245, 158, 11, 0.34);
}

.status-chip--blurry {
  background: rgba(236, 72, 153, 0.2);
  color: #f9a8d4;
  border-color: rgba(236, 72, 153, 0.34);
}

.camera-meta {
  margin: 0;
  display: grid;
  gap: 10px;
}

.camera-meta div {
  display: grid;
  gap: 3px;
}

.camera-meta dt {
  margin: 0;
  font-size: 0.72rem;
  color: #94a3b8;
  text-transform: uppercase;
  letter-spacing: 0.06em;
}

.camera-meta dd {
  margin: 0;
  font-size: 0.86rem;
  color: #f8fafc;
  word-break: break-word;
}

.actions {
  margin-top: 12px;
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 8px;
}

.actions button {
  border-radius: 10px;
  border: 1px solid rgba(148, 163, 184, 0.26);
  padding: 9px 10px;
  font-size: 0.84rem;
  font-weight: 600;
  cursor: pointer;
}

.actions .primary {
  background: linear-gradient(135deg, #0284c7 0%, #0d9488 100%);
  border-color: transparent;
  color: #f8fafc;
}

.actions .secondary {
  background: rgba(15, 23, 42, 0.78);
  color: #cbd5e1;
}

@media (max-width: 640px) {
  .camera-info {
    padding: 12px;
  }
}
</style>
