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
      <div class="spinner-wrapper">
        <div class="spinner" :class="sizeClasses" :style="{ borderTopColor: color }"></div>
        <div class="pulse-ring" :class="sizeClasses"></div>
      </div>
      <p v-if="message" class="spinner-message">{{ message }}</p>
    </div>
  </div>
  <div v-else class="spinner-inline">
    <div class="spinner-wrapper inline">
      <div class="spinner" :class="sizeClasses" :style="{ borderTopColor: color }"></div>
      <div class="pulse-ring" :class="sizeClasses"></div>
    </div>
    <p v-if="message" class="spinner-message">{{ message }}</p>
  </div>
</template>

<style scoped>
.spinner-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.85);
  backdrop-filter: blur(12px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
}

.spinner-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1.5rem;
  padding: 2rem;
  background: rgba(26, 32, 44, 0.9);
  backdrop-filter: blur(20px);
  border: 2px solid rgba(102, 126, 234, 0.3);
  border-radius: 20px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
  position: relative;
  overflow: hidden;
}

.spinner-content::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(90deg, transparent, rgba(102, 126, 234, 0.8), transparent);
  animation: scan-horizontal 2s linear infinite;
}

@keyframes scan-horizontal {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(100%); }
}

.spinner-inline {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.spinner-wrapper {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}

.spinner-wrapper.inline {
  width: auto;
  height: auto;
}

.spinner {
  border: 3px solid rgba(102, 126, 234, 0.2);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  position: relative;
  z-index: 2;
  box-shadow: 0 0 20px rgba(102, 126, 234, 0.3);
}

.pulse-ring {
  position: absolute;
  border: 2px solid rgba(102, 126, 234, 0.4);
  border-radius: 50%;
  animation: pulse-ring 2s cubic-bezier(0.215, 0.61, 0.355, 1) infinite;
  z-index: 1;
}

.w-4 { 
  width: 1rem; 
  height: 1rem; 
  border-width: 2px; 
}

.h-4 { 
  width: 1rem; 
  height: 1rem; 
  border-width: 2px; 
}

.w-8 { 
  width: 2rem; 
  height: 2rem; 
  border-width: 3px; 
}

.h-8 { 
  width: 2rem; 
  height: 2rem; 
  border-width: 3px; 
}

.w-12 { 
  width: 3rem; 
  height: 3rem; 
  border-width: 4px; 
}

.h-12 { 
  width: 3rem; 
  height: 3rem; 
  border-width: 4px; 
}

.spinner-message {
  margin: 0;
  font-size: 0.9375rem;
  font-weight: 600;
  color: white;
  text-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
  letter-spacing: 0.3px;
}

.spinner-inline .spinner-message {
  color: rgba(255, 255, 255, 0.8);
  font-size: 0.875rem;
  text-shadow: none;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

@keyframes pulse-ring {
  0% {
    transform: scale(1);
    opacity: 1;
  }
  100% {
    transform: scale(1.8);
    opacity: 0;
  }
}

/* Dark theme variant for inline spinners in light backgrounds */
@media (prefers-color-scheme: light) {
  .spinner-inline .spinner {
    box-shadow: 0 0 15px rgba(102, 126, 234, 0.2);
  }
  
  .spinner-inline .spinner-message {
    color: #4a5568;
  }
}
</style>