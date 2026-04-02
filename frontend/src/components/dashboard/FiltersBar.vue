<script setup>
import { computed } from 'vue';

const props = defineProps({
  searchQuery: {
    type: String,
    default: ''
  },
  selectedFilter: {
    type: String,
    default: 'all'
  },
  cameras: {
    type: Array,
    default: () => []
  },
  allCameras: {
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
  },
  hideCheck: {
    type: Boolean,
    default: false
  },
  checkingBlurry: {
    type: Boolean,
    default: false
  }
});

const emit = defineEmits([
  'update:searchQuery',
  'update:selectedFilter',
  'clear-filters',
  'focus-camera',
  'check-blurry'
]);

const hasFiltersApplied = computed(() =>
  props.searchQuery.trim() !== '' || props.selectedFilter !== 'all'
);

const statusCounts = computed(() => {
  const counts = {
    all: props.allCameras.length,
    online: 0,
    offline: 0,
    no_signal: 0,
    blurry: 0
  };

  for (const camera of props.allCameras) {
    if (camera.status === 'online') counts.online += 1;
    if (camera.status === 'offline') counts.offline += 1;
    if (camera.status === 'no_signal') counts.no_signal += 1;
    if (camera.status === 'blurry') counts.blurry += 1;
  }

  return counts;
});

const statusChips = computed(() => [
  {
    value: 'all',
    label: 'All',
    count: statusCounts.value.all,
    icon: 'all'
  },
  {
    value: 'online',
    label: 'Online',
    count: statusCounts.value.online,
    icon: 'online'
  },
  {
    value: 'offline',
    label: 'Offline',
    count: statusCounts.value.offline,
    icon: 'offline'
  },
  {
    value: 'no_signal',
    label: 'No Signal',
    count: statusCounts.value.no_signal,
    icon: 'no_signal'
  },
  {
    value: 'blurry',
    label: 'Blurry',
    count: statusCounts.value.blurry,
    icon: 'blurry'
  }
]);

const statusText = (status) => {
  if (status === 'offline') return 'Offline';
  if (status === 'no_signal') return 'No Signal';
  if (status === 'blurry') return 'Blurry';
  return 'Online';
};

const updateSearch = (event) => {
  emit('update:searchQuery', event.target.value);
};

const selectFilter = (filterValue) => {
  emit('update:selectedFilter', filterValue);
};

const triggerBlurryCheck = () => {
  emit('check-blurry');
};

const handleBlurryCheckKeydown = (event) => {
  if (props.checkingBlurry || statusCounts.value.blurry === 0) return;
  if (event.key === 'Enter' || event.key === ' ') {
    event.preventDefault();
    triggerBlurryCheck();
  }
};
</script>

<template>
  <section class="filters-bar" aria-label="Camera search and filters">
    <div class="control">
      <label for="camera-search">Search</label>
      <div class="input-shell">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" aria-hidden="true">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-4.35-4.35M10 18a8 8 0 100-16 8 8 0 000 16z" />
        </svg>
        <input
          id="camera-search"
          :value="searchQuery"
          type="search"
          autocomplete="off"
          placeholder="Search cameras by name or IP"
          @input="updateSearch"
        >
      </div>
    </div>

    <div class="status-controls" aria-label="Status filters">
      <button
        v-for="chip in statusChips"
        :key="chip.value"
        type="button"
        class="status-chip"
        :class="[
          `status-chip--${chip.value}`,
          { 'status-chip--active': selectedFilter === chip.value }
        ]"
        @click="selectFilter(chip.value)"
      >
        <span class="status-chip__icon" aria-hidden="true">
          <svg v-if="chip.icon === 'all'" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
          </svg>
          <svg v-else-if="chip.icon === 'online'" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <svg v-else-if="chip.icon === 'offline'" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <svg v-else-if="chip.icon === 'no_signal'" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728L5.636 5.636M12 3v3m0 12v3m9-9h-3M6 12H3" />
          </svg>
          <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
          </svg>
        </span>
        <span class="status-chip__label">{{ chip.label }}</span>
        <span class="status-chip__count">{{ chip.count }}</span>
      </button>

      <span
        v-if="!hideCheck"
        class="check-pill"
        role="button"
        tabindex="0"
        :aria-disabled="checkingBlurry || statusCounts.blurry === 0"
        :class="{ 'check-pill--disabled': checkingBlurry || statusCounts.blurry === 0 }"
        @click="!checkingBlurry && statusCounts.blurry > 0 && triggerBlurryCheck()"
        @keydown="handleBlurryCheckKeydown"
      >
        {{ checkingBlurry ? 'Checking...' : 'Check blurry' }}
      </span>
    </div>

    <button
      type="button"
      class="clear-btn"
      :disabled="!hasFiltersApplied"
      @click="$emit('clear-filters')"
    >
      Clear filters
    </button>

    <div class="results">
      <div class="results-header">
        <h3>Matching Cameras</h3>
        <span class="results-count">
          <strong>{{ cameras.length }}</strong>
          <small>Total</small>
        </span>
      </div>

      <div v-if="loading" class="results-loading" aria-hidden="true">
        <span v-for="row in 5" :key="row"></span>
      </div>

      <p v-else-if="cameras.length === 0" class="results-empty">
        No cameras match the current search and filter.
      </p>

      <ul v-else class="results-list">
        <li v-for="camera in cameras" :key="camera.id">
          <button
            type="button"
            class="result-row"
            :class="{ active: activeCameraId === camera.id }"
            @click="$emit('focus-camera', camera)"
          >
            <div class="result-main">
              <strong>{{ camera.name }}</strong>
              <span>{{ camera.ipAddress || 'N/A' }}</span>
            </div>
            <span class="status-pill" :class="`status-pill--${camera.status}`">
              {{ statusText(camera.status) }}
            </span>
          </button>
        </li>
      </ul>
    </div>
  </section>
</template>

<style scoped>
.filters-bar {
  display: flex;
  flex-direction: column;
  gap: 12px;
  min-height: 0;
  height: 100%;
  overflow: hidden;
}

.control {
  display: grid;
  gap: 6px;
}

.control label {
  color: #94a3b8;
  font-size: 0.76rem;
  text-transform: uppercase;
  letter-spacing: 0.06em;
}

.input-shell {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 12px;
  border: 1px solid rgba(148, 163, 184, 0.24);
  border-radius: 10px;
  background: rgba(15, 23, 42, 0.72);
}

.input-shell svg {
  width: 18px;
  height: 18px;
  color: #64748b;
  flex-shrink: 0;
}

.input-shell input {
  border: 0;
  outline: none;
  width: 100%;
  background: transparent;
  color: #e2e8f0;
  font-size: 0.9rem;
}

.input-shell input::placeholder {
  color: #64748b;
}

.input-shell:focus-within,
.status-chip:focus-visible,
.clear-btn:focus-visible,
.result-row:focus-visible {
  border-color: rgba(56, 189, 248, 0.7);
  box-shadow: 0 0 0 2px rgba(56, 189, 248, 0.2);
  outline: none;
}

.status-controls {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
}

.status-chip {
  border: 1px solid rgba(148, 163, 184, 0.22);
  background: rgba(15, 23, 42, 0.62);
  color: #cbd5e1;
  border-radius: 10px;
  padding: 8px 10px;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 0.84rem;
  cursor: pointer;
  transition: border-color 0.2s ease, background 0.2s ease, transform 0.2s ease;
}

.status-chip:hover {
  transform: translateY(-1px);
  border-color: rgba(56, 189, 248, 0.46);
}

.status-chip--active {
  border-color: rgba(56, 189, 248, 0.64);
  background: rgba(14, 165, 233, 0.2);
  box-shadow: inset 0 0 0 1px rgba(56, 189, 248, 0.24);
}

.status-chip__icon {
  width: 18px;
  height: 18px;
  display: grid;
  place-items: center;
}

.status-chip__icon svg {
  width: 16px;
  height: 16px;
}

.status-chip__label {
  font-weight: 600;
}

.status-chip__count {
  font-weight: 700;
  letter-spacing: 0.01em;
}

.status-chip--online .status-chip__icon {
  color: #4ade80;
}

.status-chip--offline .status-chip__icon {
  color: #f87171;
}

.status-chip--no_signal .status-chip__icon {
  color: #60a5fa;
}

.status-chip--blurry .status-chip__icon {
  color: #fb923c;
}

.status-chip--all .status-chip__icon {
  color: #7dd3fc;
}

.check-pill {
  margin-left: auto;
  border: 1px solid rgba(249, 115, 22, 0.66);
  color: #fdba74;
  background: rgba(124, 45, 18, 0.38);
  border-radius: 999px;
  padding: 5px 10px;
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.01em;
  cursor: pointer;
  transition: opacity 0.2s ease, transform 0.15s ease;
}

.check-pill:hover {
  transform: translateY(-1px);
}

.check-pill:focus-visible {
  outline: 2px solid #fb923c;
  outline-offset: 2px;
}

.check-pill--disabled {
  opacity: 0.55;
  cursor: not-allowed;
}

.clear-btn {
  width: 100%;
  border: 1px solid rgba(148, 163, 184, 0.24);
  background: rgba(30, 41, 59, 0.7);
  color: #cbd5e1;
  border-radius: 10px;
  padding: 8px 12px;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
}

.clear-btn:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

.results {
  border: 1px solid rgba(148, 163, 184, 0.2);
  border-radius: 12px;
  background: rgba(15, 23, 42, 0.45);
  padding: 10px;
  display: flex;
  flex-direction: column;
  min-height: 0;
  flex: 1;
}

.results-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.results-header h3 {
  margin: 0;
  color: #e2e8f0;
  font-size: 0.9rem;
  font-weight: 600;
}

.results-header span {
  color: #7dd3fc;
  font-weight: 700;
}

.results-count {
  display: inline-flex;
  align-items: baseline;
  gap: 6px;
}

.results-count strong {
  color: #7dd3fc;
  font-size: 1.65rem;
  line-height: 1;
}

.results-count small {
  color: #94a3b8;
  font-size: 0.8rem;
  font-weight: 500;
}

.results-loading {
  display: grid;
  gap: 8px;
  flex: 1;
}

.results-loading span {
  height: 46px;
  border-radius: 10px;
  background: linear-gradient(90deg, rgba(30, 41, 59, 0.9), rgba(51, 65, 85, 0.95), rgba(30, 41, 59, 0.9));
  background-size: 220% 100%;
  animation: loading-shimmer 1.25s linear infinite;
}

.results-empty {
  margin: 0;
  color: #94a3b8;
  font-size: 0.85rem;
  line-height: 1.45;
}

.results-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: 8px;
  min-height: 0;
  overflow: auto;
}

.result-row {
  width: 100%;
  border: 1px solid rgba(148, 163, 184, 0.18);
  background: rgba(15, 23, 42, 0.7);
  border-radius: 10px;
  padding: 10px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  color: #e2e8f0;
  cursor: pointer;
  text-align: left;
}

.result-row:hover {
  border-color: rgba(56, 189, 248, 0.48);
}

.result-row.active {
  border-color: rgba(56, 189, 248, 0.82);
  box-shadow: inset 0 0 0 1px rgba(56, 189, 248, 0.35);
}

.result-main {
  display: flex;
  flex-direction: column;
  gap: 3px;
  min-width: 0;
}

.result-main strong {
  font-size: 0.88rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.result-main span {
  color: #93c5fd;
  font-size: 0.76rem;
  font-family: 'Consolas', 'Courier New', monospace;
}

.status-pill {
  border-radius: 999px;
  padding: 4px 8px;
  font-size: 0.7rem;
  font-weight: 600;
  border: 1px solid transparent;
  flex-shrink: 0;
}

.status-pill--online {
  color: #86efac;
  background: rgba(34, 197, 94, 0.16);
  border-color: rgba(34, 197, 94, 0.36);
}

.status-pill--offline {
  color: #fda4af;
  background: rgba(239, 68, 68, 0.16);
  border-color: rgba(239, 68, 68, 0.36);
}

.status-pill--no_signal {
  color: #bfdbfe;
  background: rgba(59, 130, 246, 0.16);
  border-color: rgba(59, 130, 246, 0.36);
}

.status-pill--blurry {
  color: #fdba74;
  background: rgba(249, 115, 22, 0.16);
  border-color: rgba(249, 115, 22, 0.35);
}

@media (max-width: 560px) {
  .check-pill {
    margin-left: 0;
  }
}

@keyframes loading-shimmer {
  0% {
    background-position: 220% 0;
  }
  100% {
    background-position: -220% 0;
  }
}
</style>
