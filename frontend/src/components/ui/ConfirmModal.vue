<script setup>
import { ref, watch, onMounted, onUnmounted, Teleport } from 'vue';

const props = defineProps({
  show: {
    type: Boolean,
    default: false
  },
  title: {
    type: String,
    default: 'Confirm Action'
  },
  message: {
    type: String,
    required: true
  },
  confirmText: {
    type: String,
    default: 'Confirm'
  },
  cancelText: {
    type: String,
    default: 'Cancel'
  },
  type: {
    type: String,
    default: 'danger', // 'danger', 'warning', 'info'
    validator: (value) => ['danger', 'warning', 'info'].includes(value)
  },
  loading: {
    type: Boolean,
    default: false
  }
});

const emit = defineEmits(['confirm', 'cancel', 'close']);

const visible = ref(false);

watch(() => props.show, (newVal) => {
  visible.value = newVal;
  if (newVal) {
    document.body.style.overflow = 'hidden';
  } else {
    document.body.style.overflow = '';
  }
});

const handleConfirm = () => {
  if (!props.loading) {
    emit('confirm');
  }
};

const handleCancel = () => {
  if (!props.loading) {
    emit('cancel');
    emit('close');
  }
};

const handleOverlayClick = () => {
  if (!props.loading) {
    handleCancel();
  }
};

// Handle ESC key
const handleEscape = (e) => {
  if (e.key === 'Escape' && visible.value && !props.loading) {
    handleCancel();
  }
};

onMounted(() => {
  document.addEventListener('keydown', handleEscape);
});

onUnmounted(() => {
  document.removeEventListener('keydown', handleEscape);
  document.body.style.overflow = '';
});

const getIconColor = () => {
  switch (props.type) {
    case 'danger':
      return '#ef4444';
    case 'warning':
      return '#f59e0b';
    case 'info':
      return '#667eea';
    default:
      return '#ef4444';
  }
};

const getIcon = () => {
  switch (props.type) {
    case 'danger':
      return `<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path>`;
    case 'warning':
      return `<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path>`;
    case 'info':
      return `<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>`;
    default:
      return `<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path>`;
  }
};
</script>

<template>
  <Teleport to="body">
    <transition name="modal">
      <div v-if="visible" class="modal-overlay" @click="handleOverlayClick">
        <div class="modal-container" @click.stop role="dialog" aria-modal="true" :aria-labelledby="title">
        <div class="modal-header">
          <div class="icon-wrapper" :style="{ backgroundColor: getIconColor() + '20', borderColor: getIconColor() + '40' }">
            <svg 
              class="icon" 
              :style="{ color: getIconColor() }"
              fill="none" 
              stroke="currentColor" 
              viewBox="0 0 24 24"
              v-html="getIcon()"
            ></svg>
          </div>
          <h2 class="modal-title">{{ title }}</h2>
          <button 
            class="modal-close" 
            @click="handleCancel"
            :disabled="loading"
            aria-label="Close dialog"
          >
            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
            </svg>
          </button>
        </div>

        <div class="modal-body">
          <p class="modal-message">{{ message }}</p>
        </div>

        <div class="modal-footer">
          <button 
            class="btn-cancel" 
            @click="handleCancel"
            :disabled="loading"
          >
            {{ cancelText }}
          </button>
          <button 
            class="btn-confirm" 
            :class="type"
            @click="handleConfirm"
            :disabled="loading"
          >
            <span v-if="loading" class="spinner"></span>
            <span v-else>{{ confirmText }}</span>
          </button>
        </div>
      </div>
    </div>
  </transition>
  </Teleport>
</template>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.8);
  backdrop-filter: blur(10px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10000;
  padding: 1rem;
}

.modal-container {
  background: rgba(26, 32, 44, 0.98);
  backdrop-filter: blur(20px);
  border: 2px solid rgba(102, 126, 234, 0.3);
  border-radius: 16px;
  width: 100%;
  max-width: 450px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
  overflow: hidden;
  position: relative;
}

.modal-container::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, #667eea 0%, #764ba2 50%, #667eea 100%);
  background-size: 200% 100%;
  animation: shimmer 3s linear infinite;
}

@keyframes shimmer {
  0% { background-position: -200% 0; }
  100% { background-position: 200% 0; }
}

.modal-header {
  padding: 2rem 1.5rem 1rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  position: relative;
}

.icon-wrapper {
  width: 72px;
  height: 72px;
  border-radius: 50%;
  border: 2px solid;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 1.25rem;
  position: relative;
  overflow: hidden;
}

.icon-wrapper::before {
  content: '';
  position: absolute;
  top: -100%;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.6), transparent);
  animation: scan 3s ease-in-out infinite;
}

@keyframes scan {
  0%, 100% {
    top: -100%;
    opacity: 0;
  }
  10% {
    opacity: 1;
  }
  90% {
    opacity: 1;
  }
  100% {
    top: 200%;
    opacity: 0;
  }
}

.icon {
  width: 40px;
  height: 40px;
  filter: drop-shadow(0 2px 8px currentColor);
}

.modal-title {
  font-size: 1.375rem;
  font-weight: 700;
  color: white;
  margin: 0;
  text-align: center;
  text-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
}

.modal-close {
  position: absolute;
  top: 1rem;
  right: 1rem;
  width: 36px;
  height: 36px;
  border-radius: 8px;
  border: none;
  background: rgba(255, 255, 255, 0.05);
  color: rgba(255, 255, 255, 0.8);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.modal-close:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.1);
  color: white;
}

.modal-close:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.modal-close svg {
  width: 20px;
  height: 20px;
}

.modal-body {
  padding: 0 2rem 2rem;
}

.modal-message {
  font-size: 1rem;
  color: rgba(255, 255, 255, 0.8);
  line-height: 1.6;
  text-align: center;
  margin: 0;
}

.modal-footer {
  padding: 1.5rem;
  background: rgba(255, 255, 255, 0.03);
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  gap: 0.75rem;
  justify-content: flex-end;
}

.btn-cancel,
.btn-confirm {
  padding: 0.875rem 1.75rem;
  border-radius: 10px;
  font-size: 0.9375rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 110px;
}

.btn-cancel {
  background: rgba(255, 255, 255, 0.05);
  color: rgba(255, 255, 255, 0.9);
  border: 2px solid rgba(255, 255, 255, 0.1);
}

.btn-cancel:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.2);
}

.btn-cancel:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-confirm {
  color: white;
  border: 2px solid transparent;
}

.btn-confirm.danger {
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
  box-shadow: 0 4px 15px rgba(239, 68, 68, 0.4);
}

.btn-confirm.warning {
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
  box-shadow: 0 4px 15px rgba(245, 158, 11, 0.4);
}

.btn-confirm.info {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
}

.btn-confirm:hover:not(:disabled) {
  transform: translateY(-2px);
}

.btn-confirm.danger:hover:not(:disabled) {
  box-shadow: 0 6px 20px rgba(239, 68, 68, 0.5);
}

.btn-confirm.warning:hover:not(:disabled) {
  box-shadow: 0 6px 20px rgba(245, 158, 11, 0.5);
}

.btn-confirm.info:hover:not(:disabled) {
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.5);
}

.btn-confirm:disabled {
  opacity: 0.7;
  cursor: not-allowed;
  transform: none;
}

/* Loading Spinner */
.spinner {
  width: 20px;
  height: 20px;
  border: 3px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Modal Animations */
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.3s ease;
}

.modal-enter-active .modal-container,
.modal-leave-active .modal-container {
  transition: transform 0.3s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-from .modal-container,
.modal-leave-to .modal-container {
  transform: scale(0.9) translateY(-20px);
}

/* Mobile responsive */
@media (max-width: 640px) {
  .modal-container {
    max-width: 100%;
    margin: 0 1rem;
  }

  .modal-header {
    padding: 1.75rem 1.25rem 0.75rem;
  }

  .icon-wrapper {
    width: 64px;
    height: 64px;
  }

  .icon {
    width: 36px;
    height: 36px;
  }

  .modal-title {
    font-size: 1.25rem;
  }

  .modal-body {
    padding: 0 1.5rem 1.5rem;
  }

  .modal-message {
    font-size: 0.9375rem;
  }

  .modal-footer {
    padding: 1.25rem;
    flex-direction: column-reverse;
  }

  .btn-cancel,
  .btn-confirm {
    width: 100%;
  }
}
</style>