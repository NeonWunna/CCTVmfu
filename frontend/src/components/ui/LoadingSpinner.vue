<script setup>
import { computed } from 'vue';

const props = defineProps({
  size: {
    type: String,
    default: 'medium', // 'small', 'medium', 'large'
    validator: (value) => ['small', 'medium', 'large'].includes(value)
  },
  color: {
    type: String,
    default: '#667eea'
  },
  overlay: {
    type: Boolean,
    default: false
  },
  message: {
    type: String,
    default: ''
  }
});

const sizeClasses = computed(() => {
  const sizes = {
    small: 'w-4 h-4',
    medium: 'w-8 h-8',
    large: 'w-12 h-12'
  };
  return sizes[props.size];
});
</script>

<template>
  <div v-if="overlay" class="spinner-overlay">
    <div class="spinner-content">
      <div class="spinner" :class="sizeClasses" :style="{ borderTopColor: color }"></div>
      <p v-if="message" class="spinner-message">{{ message }}</p>
    </div>
  </div>
  <div v-else class="spinner-inline">
    <div class="spinner" :class="sizeClasses" :style="{ borderTopColor: color }"></div>
    <p v-if="message" class="spinner-message">{{ message }}</p>
  </div>
</template>

<style scoped>
.spinner-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
}

.spinner-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

.spinner-inline {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.spinner {
  border: 3px solid rgba(0, 0, 0, 0.1);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

.w-4 { width: 1rem; height: 1rem; border-width: 2px; }
.h-4 { width: 1rem; height: 1rem; border-width: 2px; }
.w-8 { width: 2rem; height: 2rem; border-width: 3px; }
.h-8 { width: 2rem; height: 2rem; border-width: 3px; }
.w-12 { width: 3rem; height: 3rem; border-width: 4px; }
.h-12 { width: 3rem; height: 3rem; border-width: 4px; }

.spinner-message {
  margin: 0;
  font-size: 0.875rem;
  font-weight: 500;
  color: white;
}

.spinner-inline .spinner-message {
  color: #6b7280;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>