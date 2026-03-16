<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../../stores/auth';

const props = defineProps({
  logoUrl: {
    type: String,
    required: true
  },
  compactMode: {
    type: Boolean,
    default: false
  },
  showMobileFiltersButton: {
    type: Boolean,
    default: true
  },
  userName: {
    type: String,
    default: 'Admin User'
  },
  userRole: {
    type: String,
    default: 'Security Administrator'
  }
});

const emit = defineEmits(['camera-settings', 'logout', 'open-mobile-filters']);

const router = useRouter();
const authStore = useAuthStore();
const isSuperAdmin = computed(() => authStore.isSuperAdmin);

const profileMenuOpen = ref(false);
const profileMenuRef = ref(null);

const userInitials = computed(() =>
  props.userName
    .split(' ')
    .filter(Boolean)
    .map((part) => part[0])
    .join('')
    .toUpperCase()
    .slice(0, 2)
);

const toggleProfileMenu = () => {
  profileMenuOpen.value = !profileMenuOpen.value;
};

const closeProfileMenu = () => {
  profileMenuOpen.value = false;
};

const handleDocumentClick = (event) => {
  if (!profileMenuRef.value) return;
  if (!profileMenuRef.value.contains(event.target)) {
    closeProfileMenu();
  }
};

const goToCameraSettings = () => {
  closeProfileMenu();
  emit('camera-settings');
};

const goToAdminPanel = () => {
  closeProfileMenu();
  router.push('/admin');
};

const logout = () => {
  closeProfileMenu();
  emit('logout');
};

onMounted(() => {
  document.addEventListener('click', handleDocumentClick);
});

onBeforeUnmount(() => {
  document.removeEventListener('click', handleDocumentClick);
});
</script>

<template>
  <header class="app-header" :class="{ 'app-header--compact': compactMode }">
    <div class="brand">
      <img :src="logoUrl" alt="MFU Logo" class="logo">
      <div class="brand-copy">
        <h1>CCTV Monitoring System</h1>
        <p>Mae Fah Luang University</p>
      </div>
    </div>

    <div class="actions">
      <button
        v-if="showMobileFiltersButton"
        class="mobile-filters-btn"
        :class="{ 'mobile-filters-btn--visible': compactMode }"
        type="button"
        aria-label="Open dashboard menu"
        @click="$emit('open-mobile-filters')"
      >
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" aria-hidden="true">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 7h16M4 12h16M4 17h16" />
        </svg>
        <span>Menu</span>
      </button>

      <div ref="profileMenuRef" class="profile-menu">
        <button
          class="profile-trigger"
          type="button"
          aria-haspopup="menu"
          :aria-expanded="profileMenuOpen"
          @click.stop="toggleProfileMenu"
        >
          <span class="avatar">{{ userInitials }}</span>
          <span class="profile-meta">
            <strong>{{ userName }}</strong>
            <small>{{ userRole }}</small>
          </span>
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" aria-hidden="true">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 9l6 6 6-6" />
          </svg>
        </button>

        <transition name="menu-fade">
          <div v-if="profileMenuOpen" class="profile-dropdown" role="menu">
            <button v-if="isSuperAdmin" type="button" class="dropdown-item admin" role="menuitem" @click="goToAdminPanel">
              🛡 Admin Panel
            </button>
            <button type="button" class="dropdown-item" role="menuitem" @click="goToCameraSettings">
              Camera Settings
            </button>
            <button type="button" class="dropdown-item logout" role="menuitem" @click="logout">
              Logout
            </button>
          </div>
        </transition>
      </div>
    </div>
  </header>
</template>

<style scoped>
.app-header {
  position: relative;
  z-index: 1200;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 24px;
  background: rgba(15, 23, 42, 0.92);
  border-bottom: 1px solid rgba(148, 163, 184, 0.24);
  backdrop-filter: blur(12px);
}

.brand {
  display: flex;
  align-items: center;
  gap: 12px;
  min-width: 0;
}

.logo {
  width: 52px;
  height: 52px;
  object-fit: contain;
  border-radius: 12px;
  background: rgba(15, 23, 42, 0.48);
}

.brand-copy {
  min-width: 0;
}

.brand-copy h1 {
  margin: 0;
  color: #e2e8f0;
  font-size: clamp(1rem, 1.8vw, 1.3rem);
  font-family: 'Trebuchet MS', 'Segoe UI', sans-serif;
  letter-spacing: 0.02em;
}

.brand-copy p {
  margin: 4px 0 0;
  color: #94a3b8;
  font-size: 0.8rem;
}

.actions {
  display: flex;
  align-items: center;
  gap: 12px;
  position: relative;
  z-index: 1;
}

.mobile-filters-btn {
  display: none;
  border: 1px solid rgba(56, 189, 248, 0.35);
  background: rgba(15, 23, 42, 0.75);
  color: #dbeafe;
  border-radius: 10px;
  padding: 9px 12px;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  gap: 8px;
}

.mobile-filters-btn svg {
  width: 16px;
  height: 16px;
}

.mobile-filters-btn--visible {
  display: inline-flex;
  align-items: center;
}

.profile-menu {
  position: relative;
  z-index: 1300;
}

.profile-trigger {
  display: flex;
  align-items: center;
  gap: 10px;
  border: 1px solid rgba(148, 163, 184, 0.22);
  border-radius: 999px;
  background: rgba(15, 23, 42, 0.78);
  color: #e2e8f0;
  padding: 6px 10px 6px 6px;
  cursor: pointer;
  min-width: 0;
  touch-action: manipulation;
}

.profile-trigger:focus-visible,
.mobile-filters-btn:focus-visible {
  outline: 2px solid #38bdf8;
  outline-offset: 2px;
}

.avatar {
  width: 36px;
  height: 36px;
  border-radius: 999px;
  display: grid;
  place-items: center;
  background: linear-gradient(135deg, #0ea5e9 0%, #14b8a6 100%);
  color: #082f49;
  font-size: 0.78rem;
  font-weight: 700;
}

.profile-meta {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  text-align: left;
  min-width: 0;
}

.profile-meta strong {
  font-size: 0.82rem;
  white-space: nowrap;
}

.profile-meta small {
  color: #94a3b8;
  font-size: 0.7rem;
  white-space: nowrap;
}

.profile-trigger svg {
  width: 18px;
  height: 18px;
  color: #94a3b8;
  flex-shrink: 0;
}

.profile-dropdown {
  position: absolute;
  top: calc(100% + 8px);
  right: 0;
  width: 200px;
  border: 1px solid rgba(148, 163, 184, 0.24);
  border-radius: 12px;
  background: rgba(15, 23, 42, 0.96);
  box-shadow: 0 14px 28px rgba(2, 6, 23, 0.45);
  overflow: hidden;
  z-index: 1400;
  pointer-events: auto;
}

.dropdown-item {
  width: 100%;
  text-align: left;
  border: 0;
  background: transparent;
  color: #cbd5e1;
  font-size: 0.9rem;
  padding: 12px 14px;
  cursor: pointer;
}

.dropdown-item:hover {
  background: rgba(51, 65, 85, 0.52);
}

.dropdown-item.logout {
  color: #fca5a5;
}

.dropdown-item.admin {
  color: #c4b5fd;
  border-bottom: 1px solid rgba(148, 163, 184, 0.15);
}
.dropdown-item.admin:hover {
  background: rgba(139, 92, 246, 0.15);
}

.menu-fade-enter-active,
.menu-fade-leave-active {
  transition: opacity 0.16s ease, transform 0.16s ease;
}

.menu-fade-enter-from,
.menu-fade-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}

.app-header--compact {
  padding: 12px 14px;
}

.app-header--compact .logo {
  width: 44px;
  height: 44px;
}

.app-header--compact .brand-copy p,
.app-header--compact .profile-meta {
  display: none;
}

@media (max-width: 840px) {
  .app-header {
    padding: 14px 16px;
  }

  .brand-copy p,
  .profile-meta {
    display: none;
  }

  .mobile-filters-btn {
    display: inline-flex;
    align-items: center;
  }

  .profile-dropdown {
    position: fixed;
    top: 66px;
    right: 10px;
    width: min(220px, calc(100vw - 20px));
  }
}
</style>
