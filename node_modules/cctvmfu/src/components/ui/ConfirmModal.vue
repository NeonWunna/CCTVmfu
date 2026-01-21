<script setup>
import { ref, watch, onMounted, onUnmounted } from 'vue';

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
      return '#3b82f6';
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
  <transition name="modal">
    <div v-if="visible" class="modal-overlay" @click="handleOverlayClick">
      <div class="modal-container" @click.stop role="dialog" aria-modal="true" :aria-labelledby="title">
        <div class="modal-header">
          <div class="icon-wrapper" :style="{ backgroundColor: getIconColor() + '20' }">
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
</template>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9998;
  padding: 1rem;
}

.modal-container {
  background: white;
  border-radius: 16px;
  width: 100%;
  max-width: 450px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  overflow: hidden;
}

.modal-header {
  padding: 1.5rem 1.5rem 1rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  position: relative;
}

.icon-wrapper {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 1rem;
}

.icon {
  width: 36px;
  height: 36px;
}

.modal-title {
  font-size: 1.25rem;
  font-weight: 700;
  color: #1f2937;
  margin: 0;
  text-align: center;
}

.modal-close {
  position: absolute;
  top: 1rem;
  right: 1rem;
  width: 32px;
  height: 32px;
  border-radius: 8px;
  border: none;
  background: #f3f4f6;
  color: #6b7280;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.modal-close:hover:not(:disabled) {
  background: #e5e7eb;
  color: #374151;
}

.modal-close:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.modal-close svg {
  width: 18px;
  height: 18px;
}

.modal-body {
  padding: 0 2rem 1.5rem;
}

.modal-message {
  font-size: 0.9375rem;
  color: #6b7280;
  line-height: 1.6;
  text-align: center;
  margin: 0;
}

.modal-footer {
  padding: 1.5rem;
  background: #f9fafb;
  display: flex;
  gap: 0.75rem;
  justify-content: flex-end;
}

.btn-cancel,
.btn-confirm {
  padding: 0.75rem 1.5rem;
  border-radius: 10px;
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 100px;
}

.btn-cancel {
  background: white;
  color: #374151;
  border: 2px solid #e5e7eb;
}

.btn-cancel:hover:not(:disabled) {
  background: #f3f4f6;
  border-color: #d1d5db;
}

.btn-cancel:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-confirm {
  color: white;
}

.btn-confirm.danger {
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
}

.btn-confirm.warning {
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
}

.btn-confirm.info {
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
}

.btn-confirm:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.2);
}

.btn-confirm:disabled {
  opacity: 0.7;
  cursor: not-allowed;
  transform: none;
}

/* Loading Spinner */
.spinner {
  width: 18px;
  height: 18px;
  border: 2px solid rgba(255, 255, 255, 0.3);
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
    padding: 1.25rem 1.25rem 0.75rem;
  }

  .icon-wrapper {
    width: 56px;
    height: 56px;
  }

  .icon {
    width: 32px;
    height: 32px;
  }

  .modal-title {
    font-size: 1.125rem;
  }

  .modal-body {
    padding: 0 1.5rem 1.25rem;
  }

  .modal-message {
    font-size: 0.875rem;
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