<script setup>
import { computed } from 'vue';

const props = defineProps({
  total: {
    type: Number,
    default: 0
  },
  online: {
    type: Number,
    default: 0
  },
  offline: {
    type: Number,
    default: 0
  },
  noSignal: {
    type: Number,
    default: 0
  },
  blurry: {
    type: Number,
    default: 0
  },
  selectedFilter: {
    type: String,
    default: 'all'
  },
  loading: {
    type: Boolean,
    default: false
  }
});

const emit = defineEmits(['select-filter']);

const cards = computed(() => [
  {
    key: 'total',
    label: 'Total',
    value: props.total,
    filterValue: 'all',
    tooltip: 'All registered cameras'
  },
  {
    key: 'online',
    label: 'Online',
    value: props.online,
    filterValue: 'online',
    tooltip: 'Camera is reachable and stream is healthy'
  },
  {
    key: 'offline',
    label: 'Offline',
    value: props.offline,
    filterValue: 'offline',
    tooltip: 'Camera host is not reachable'
  },
  {
    key: 'no_signal',
    label: 'No Signal',
    value: props.noSignal,
    filterValue: 'no_signal',
    tooltip: 'Camera is connected but no video signal'
  },
  {
    key: 'blurry',
    label: 'Blurry',
    value: props.blurry,
    filterValue: 'blurry',
    tooltip: 'Image quality is degraded'
  }
]);

const iconPaths = {
  total: ['M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14', 'M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z'],
  online: ['M9 12l2 2 4-4', 'M21 12a9 9 0 11-18 0 9 9 0 0118 0z'],
  offline: ['M12 8v4', 'M12 16h.01', 'M21 12a9 9 0 11-18 0 9 9 0 0118 0z'],
  no_signal: ['M18.364 18.364A9 9 0 005.636 5.636', 'M12 3v3m0 12v3m9-9h-3M6 12H3', 'M4.222 4.222l15.556 15.556'],
  blurry: ['M15 12a3 3 0 11-6 0 3 3 0 016 0z', 'M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z']
};

const getIconPaths = (key) => iconPaths[key] || [];

const selectFilter = (filterValue) => {
  emit('select-filter', filterValue);
};
</script>

<template>
  <section class="stats-grid" aria-label="System status summary">
    <template v-if="loading">
      <article v-for="index in 5" :key="index" class="stats-card stats-card--skeleton" aria-hidden="true">
        <div class="skeleton-icon"></div>
        <div class="skeleton-copy">
          <span></span>
          <span></span>
        </div>
      </article>
    </template>

    <button
      v-for="card in cards"
      v-else
      :key="card.key"
      type="button"
      class="stats-card"
      :class="[
        `stats-card--${card.key}`,
        { 'stats-card--active': selectedFilter === card.filterValue }
      ]"
      :title="card.tooltip"
      @click="selectFilter(card.filterValue)"
    >
      <span class="stats-icon" aria-hidden="true">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <path
            v-for="(path, pathIndex) in getIconPaths(card.key)"
            :key="`${card.key}-${pathIndex}`"
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            :d="path"
          />
        </svg>
      </span>

      <span class="stats-copy">
        <span class="stats-label">{{ card.label }}</span>
        <strong class="stats-value">{{ card.value }}</strong>
      </span>
    </button>
  </section>
</template>

<style scoped>
.stats-grid {
  display: grid;
  grid-template-columns: repeat(5, minmax(120px, 1fr));
  gap: 12px;
}

.stats-card {
  border: 1px solid rgba(148, 163, 184, 0.24);
  border-radius: 14px;
  background: rgba(15, 23, 42, 0.72);
  color: #dbeafe;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px;
  text-align: left;
  cursor: pointer;
  min-height: 86px;
  transition: border-color 0.2s ease, transform 0.2s ease, background 0.2s ease;
}

.stats-card:hover {
  transform: translateY(-1px);
  border-color: rgba(56, 189, 248, 0.5);
}

.stats-card:focus-visible {
  outline: 2px solid #38bdf8;
  outline-offset: 2px;
}

.stats-card--active {
  border-color: rgba(56, 189, 248, 0.7);
  box-shadow: inset 0 0 0 1px rgba(56, 189, 248, 0.25);
}

.stats-icon {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  display: grid;
  place-items: center;
  flex-shrink: 0;
}

.stats-icon svg {
  width: 20px;
  height: 20px;
}

.stats-card--total .stats-icon {
  color: #e0f2fe;
  background: rgba(14, 165, 233, 0.26);
}

.stats-card--online .stats-icon {
  color: #bbf7d0;
  background: rgba(22, 163, 74, 0.24);
}

.stats-card--offline .stats-icon {
  color: #fecaca;
  background: rgba(220, 38, 38, 0.2);
}

.stats-card--no_signal .stats-icon {
  color: #fef3c7;
  background: rgba(217, 119, 6, 0.24);
}

.stats-card--blurry .stats-icon {
  color: #fbcfe8;
  background: rgba(190, 24, 93, 0.24);
}

.stats-copy {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.stats-label {
  color: #94a3b8;
  font-size: 0.75rem;
  line-height: 1.2;
}

.stats-value {
  color: #f8fafc;
  font-size: 1.45rem;
  line-height: 1.15;
  letter-spacing: -0.02em;
}

.stats-card--skeleton {
  pointer-events: none;
}

.skeleton-icon {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  background: linear-gradient(90deg, rgba(30, 41, 59, 0.8), rgba(51, 65, 85, 0.95), rgba(30, 41, 59, 0.8));
  background-size: 220% 100%;
  animation: shimmer 1.2s linear infinite;
}

.skeleton-copy {
  display: flex;
  flex-direction: column;
  gap: 8px;
  width: 100%;
}

.skeleton-copy span {
  display: block;
  height: 10px;
  border-radius: 999px;
  background: linear-gradient(90deg, rgba(30, 41, 59, 0.8), rgba(51, 65, 85, 0.95), rgba(30, 41, 59, 0.8));
  background-size: 220% 100%;
  animation: shimmer 1.2s linear infinite;
}

.skeleton-copy span:last-child {
  width: 50%;
  height: 18px;
}

@keyframes shimmer {
  0% {
    background-position: 220% 0;
  }
  100% {
    background-position: -220% 0;
  }
}

@media (max-width: 1120px) {
  .stats-grid {
    grid-template-columns: repeat(3, minmax(140px, 1fr));
  }
}

@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: repeat(2, minmax(130px, 1fr));
  }
}

@media (max-width: 460px) {
  .stats-card {
    min-height: 78px;
    padding: 10px;
  }

  .stats-value {
    font-size: 1.2rem;
  }
}
</style>
