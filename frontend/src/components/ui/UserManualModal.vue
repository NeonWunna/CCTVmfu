<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue';

const props = defineProps({
  show: {
    type: Boolean,
    default: false
  }
});

const emit = defineEmits(['close']);

const modalRef = ref(null);

const handleKeydown = (e) => {
  if (e.key === 'Escape' && props.show) {
    emit('close');
  }
};

onMounted(() => {
  document.addEventListener('keydown', handleKeydown);
});

onUnmounted(() => {
  document.removeEventListener('keydown', handleKeydown);
});
</script>

<template>
  <transition name="modal-fade">
    <div v-if="show" class="modal-backdrop" @click.self="$emit('close')">
      <div class="modal-content" role="dialog" aria-modal="true" ref="modalRef">
        <header class="modal-header">
          <div class="header-title">
            <svg class="header-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <h2>How to use CCTV MFU</h2>
          </div>
          <button type="button" class="close-btn" aria-label="Close manual" @click="$emit('close')">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </header>

        <div class="modal-body">
          <section class="manual-section">
            <h3 class="section-title">GENERAL USER (User)</h3>
            <ul class="feature-list">
              <li>
                <svg class="bullet-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" /></svg>
                <span><strong>Interactive Map:</strong> View all CCTV locations across the university campus. Zoom and pan the map to explore.</span>
              </li>
              <li>
                <svg class="bullet-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" /></svg>
                <span><strong>Camera Status:</strong> Colored markers indicate current status:
                  <span class="status-badge status-online">Online</span>
                  <span class="status-badge status-offline">Offline</span>
                  <span class="status-badge status-no-signal">No Signal</span>
                  <span class="status-badge status-blurry">Blurry</span>
                </span>
              </li>
              <li>
                <svg class="bullet-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" /></svg>
                <span>Click on any camera marker to view basic information (Name, Location, IP).</span>
              </li>
            </ul>
          </section>

          <section class="manual-section">
            <h3 class="section-title">ADMINISTRATOR (Admin)</h3>
            <ul class="feature-list">
              <li>
                <svg class="bullet-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" /></svg>
                <span><strong>Live Stream:</strong> Click <strong>"View Stream"</strong> on a camera to watch real-time video feeds.</span>
              </li>
              <li>
                <svg class="bullet-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" /></svg>
                <span><strong>Manage Cameras:</strong> Access <strong>Camera Settings</strong> to Add, Edit, or Delete cameras in the system.</span>
              </li>
              <li>
                <svg class="bullet-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" /></svg>
                <span><strong>Manual Checks:</strong> Click the check buttons to manually verify online status or use AI to detect blurry footage.</span>
              </li>
            </ul>
          </section>

          <section class="manual-section">
            <h3 class="section-title">SUPER ADMINISTRATOR (SuperAdmin)</h3>
            <ul class="feature-list">
              <li>
                <svg class="bullet-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" /></svg>
                <span><strong>User Management:</strong> Access the <strong>Admin Panel</strong> to manage all system users.</span>
              </li>
              <li>
                <svg class="bullet-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" /></svg>
                <span><strong>Role Assignment:</strong> Promote or demote users (e.g., upgrade a User to an Admin).</span>
              </li>
            </ul>
          </section>

          <section class="manual-section">
            <h3 class="section-title">SYSTEM INFO</h3>
            <ul class="feature-list">
              <li>
                <svg class="bullet-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" /></svg>
                <span>Status is automatically checked every <strong>30 seconds</strong>.</span>
              </li>
              <li>
                <svg class="bullet-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" /></svg>
                <span>AI Blurry detection runs every <strong>6 hours</strong>.</span>
              </li>
            </ul>
          </section>
        </div>
      </div>
    </div>
  </transition>
</template>

<style scoped>
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(2, 6, 23, 0.65);
  backdrop-filter: blur(4px);
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.modal-content {
  background: #111827; /* Dark grayish-blue matching the reference */
  border: 1px solid #1f2937;
  border-radius: 12px;
  width: 100%;
  max-width: 460px;
  max-height: 85vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4);
  color: #f3f4f6;
  font-family: 'Inter', 'Trebuchet MS', sans-serif;
  overflow: hidden;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  border-bottom: 1px solid #1f2937;
  background: rgba(17, 24, 39, 0.95);
}

.header-title {
  display: flex;
  align-items: center;
  gap: 10px;
}

.header-icon {
  width: 20px;
  height: 20px;
  color: #60a5fa;
  background: rgba(59, 130, 246, 0.15);
  border-radius: 50%;
  padding: 4px;
}

.header-title h2 {
  margin: 0;
  font-size: 1.05rem;
  font-weight: 600;
  color: #ffffff;
}

.close-btn {
  background: transparent;
  border: none;
  color: #9ca3af;
  cursor: pointer;
  padding: 4px;
  border-radius: 6px;
  display: grid;
  place-items: center;
  transition: all 0.2s;
}

.close-btn:hover {
  background: #1f2937;
  color: #f3f4f6;
}

.close-btn svg {
  width: 20px;
  height: 20px;
}

.modal-body {
  padding: 20px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.manual-section {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.section-title {
  margin: 0;
  font-size: 0.75rem;
  font-weight: 700;
  color: #3b82f6; /* Blue matching reference */
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.feature-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.feature-list li {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  font-size: 0.85rem;
  line-height: 1.5;
  color: #d1d5db;
}

.feature-list strong {
  color: #f9fafb;
}

.bullet-icon {
  width: 16px;
  height: 16px;
  color: #60a5fa; /* Blue icon */
  flex-shrink: 0;
  margin-top: 2px;
}

.status-badge {
  display: inline-block;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 0.7rem;
  font-weight: 600;
  margin: 0 2px;
  vertical-align: middle;
}

.status-online { background: rgba(16, 185, 129, 0.15); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.3); }
.status-offline { background: rgba(239, 68, 68, 0.15); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.3); }
.status-no-signal { background: rgba(245, 158, 11, 0.15); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.3); }
.status-blurry { background: rgba(249, 115, 22, 0.15); color: #fb923c; border: 1px solid rgba(249, 115, 22, 0.3); }

/* Transitions */
.modal-fade-enter-active,
.modal-fade-leave-active {
  transition: opacity 0.2s ease;
}

.modal-fade-enter-from,
.modal-fade-leave-to {
  opacity: 0;
}

.modal-fade-enter-active .modal-content {
  animation: modal-pop 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}

@keyframes modal-pop {
  0% { opacity: 0; transform: scale(0.95) translateY(10px); }
  100% { opacity: 1; transform: scale(1) translateY(0); }
}

/* Scrollbar styling for body */
.modal-body::-webkit-scrollbar {
  width: 6px;
}
.modal-body::-webkit-scrollbar-track {
  background: transparent;
}
.modal-body::-webkit-scrollbar-thumb {
  background: #374151;
  border-radius: 10px;
}
.modal-body::-webkit-scrollbar-thumb:hover {
  background: #4b5563;
}
</style>
