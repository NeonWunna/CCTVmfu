<script setup>
import { ref, watch, onMounted } from 'vue';

const props = defineProps({
  message: {
    type: String,
    required: true
  },
  type: {
    type: String,
    default: 'info', // 'success', 'error', 'warning', 'info'
    validator: (value) => ['success', 'error', 'warning', 'info'].includes(value)
  },
  duration: {
    type: Number,
    default: 3000
  },
  show: {
    type: Boolean,
    default: false
  }
});

const emit = defineEmits(['close']);

const visible = ref(false);
let timeoutId = null;

watch(() => props.show, (newVal) => {
  if (newVal) {
    visible.value = true;
    
    if (timeoutId) {
      clearTimeout(timeoutId);
    }
    
    timeoutId = setTimeout(() => {
      close();
    }, props.duration);
  }
});

const close = () => {
  visible.value = false;
  setTimeout(() => {
    emit('close');
  }, 300);
};

const getIcon = () => {
  switch (props.type) {
    case 'success':
      return `<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>`;
    case 'error':
      return `<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z"></path>`;
    case 'warning':
      return `<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path>`;
    case 'info':
    default:
      return `<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>`;
  }
};
</script>

<template>
  <transition name="toast">
    <div v-if="visible" class="toast-container" :class="type">
      <div class="toast-content">
        <div class="toast-icon">
          <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" v-html="getIcon()"></svg>
        </div>
        <p class="toast-message">{{ message }}</p>
        <button class="toast-close" @click="close" aria-label="Close notification">
          <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
          </svg>
        </button>
      </div>
    </div>
  </transition>
</template>

<style scoped>
.toast-container {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 9999;
  min-width: 300px;
  max-width: 500px;
  border-radius: 12px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
  backdrop-filter: blur(10px);
  animation: slideIn 0.3s ease-out;
}

.toast-content {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px 20px;
  color: white;
}

.toast-icon {
  flex-shrink: 0;
  width: 24px;
  height: 24px;
}

.toast-icon svg {
  width: 100%;
  height: 100%;
}

.toast-message {
  flex: 1;
  margin: 0;
  font-size: 14px;
  font-weight: 500;
  line-height: 1.5;
}

.toast-close {
  flex-shrink: 0;
  width: 20px;
  height: 20px;
  border: none;
  background: transparent;
  cursor: pointer;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  opacity: 0.8;
  transition: opacity 0.2s;
}

.toast-close:hover {
  opacity: 1;
}

.toast-close svg {
  width: 100%;
  height: 100%;
}

/* Toast Types */
.toast-container.success {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
}

.toast-container.error {
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
}

.toast-container.warning {
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
}

.toast-container.info {
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
}

/* Animations */
.toast-enter-active,
.toast-leave-active {
  transition: all 0.3s ease;
}

.toast-enter-from {
  opacity: 0;
  transform: translateX(100px);
}

.toast-leave-to {
  opacity: 0;
  transform: translateX(100px);
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateX(100px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

/* Mobile responsive */
@media (max-width: 640px) {
  .toast-container {
    top: 10px;
    right: 10px;
    left: 10px;
    min-width: auto;
    max-width: none;
  }
  
  .toast-content {
    padding: 14px 16px;
  }
  
  .toast-message {
    font-size: 13px;
  }
}
</style>