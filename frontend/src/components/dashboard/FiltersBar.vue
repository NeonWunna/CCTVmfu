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
  filterOptions: {
    type: Array,
    default: () => []
  },
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

const emit = defineEmits([
  'update:searchQuery',
  'update:selectedFilter',
  'clear-filters',
  'focus-camera'
]);

const hasFiltersApplied = computed(() =>
  props.searchQuery.trim() !== '' || props.selectedFilter !== 'all'
);

const statusText = (status) => {
  if (status === 'offline') return 'Offline';
  if (status === 'no_signal') return 'No Signal';
  if (status === 'blurry') return 'Blurry';
  return 'Online';
};

const updateSearch = (event) => {
  emit('update:searchQuery', event.target.value);
};

const updateFilter = (event) => {
  emit('update:selectedFilter', event.target.value);
};
</script>

<template>
  <section class="filters-bar" aria-label="Camera search and filters">
    <div class="controls-group">
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

      <div class="control">
        <label for="camera-filter">Status</label>
        <select id="camera-filter" :value="selectedFilter" @change="updateFilter">
          <option
            v-for="option in filterOptions"
            :key="option.value"
            :value="option.value"
          >
            {{ option.label }}
          </option>
        </select>
      </div>
    </div>

    <div class="legend" aria-label="Status legend">
      <span class="legend-item" title="Camera is reachable and streaming">
        <span class="dot dot--online"></span>Online
      </span>
      <span class="legend-item" title="Device is unreachable">
        <span class="dot dot--offline"></span>Offline
      </span>
      <span class="legend-item" title="Stream has no video signal">
        <span class="dot dot--no-signal"></span>No Signal
      </span>
      <span class="legend-item" title="Image quality is blurred">
        <span class="dot dot--blurry"></span>Blurry
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
        <span>{{ cameras.length }}</span>
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
  gap: 14px;
  min-height: 0;
  height: 100%;
}

.controls-group {
  display: grid;
  gap: 10px;
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
  background: rgba(15, 23, 42, 0.65);
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

.control select {
  border: 1px solid rgba(148, 163, 184, 0.24);
  border-radius: 10px;
  background: rgba(15, 23, 42, 0.65);
  color: #e2e8f0;
  padding: 10px 12px;
  font-size: 0.9rem;
}

.input-shell:focus-within,
.control select:focus-visible {
  border-color: rgba(56, 189, 248, 0.7);
  box-shadow: 0 0 0 2px rgba(56, 189, 248, 0.2);
}

.legend {
  display: flex;
  flex-wrap: wrap;
  gap: 8px 12px;
}

.legend-item {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  color: #cbd5e1;
  font-size: 0.8rem;
}

.dot {
  width: 9px;
  height: 9px;
  border-radius: 999px;
}

.dot--online {
  background: #22c55e;
}

.dot--offline {
  background: #ef4444;
}

.dot--no-signal {
  background: #f59e0b;
}

.dot--blurry {
  background: #ec4899;
}

.clear-btn {
  justify-self: start;
  border: 1px solid rgba(148, 163, 184, 0.24);
  background: rgba(30, 41, 59, 0.7);
  color: #cbd5e1;
  border-radius: 10px;
  padding: 8px 12px;
  font-size: 0.85rem;
  cursor: pointer;
}

.clear-btn:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

.clear-btn:focus-visible,
.result-row:focus-visible {
  outline: 2px solid #38bdf8;
  outline-offset: 2px;
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
  color: #fcd34d;
  background: rgba(245, 158, 11, 0.16);
  border-color: rgba(245, 158, 11, 0.36);
}

.status-pill--blurry {
  color: #f9a8d4;
  background: rgba(236, 72, 153, 0.16);
  border-color: rgba(236, 72, 153, 0.36);
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
