<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../stores/auth';
import api from '../services/api';
import ConfirmModal from '../components/ui/ConfirmModal.vue';
import Toast from '../components/ui/Toast.vue';

const router = useRouter();
const authStore = useAuthStore();

const users = ref([]);
const loading = ref(true);
const toast = ref({ show: false, message: '', type: 'info' });
const confirmModal = ref({ show: false, title: '', message: '', onConfirm: null, loading: false });

const showToast = (message, type = 'info') => {
  toast.value = { show: true, message, type };
};

const fetchUsers = async () => {
  loading.value = true;
  try {
    const res = await api.getUsers();
    users.value = res.data;
  } catch (err) {
    showToast('Failed to load users', 'error');
  } finally {
    loading.value = false;
  }
};

const confirmDelete = (user) => {
  confirmModal.value = {
    show: true,
    title: 'Delete User',
    message: `Are you sure you want to delete "${user.name}" (${user.email})? This action cannot be undone.`,
    loading: false,
    onConfirm: async () => {
      confirmModal.value.loading = true;
      try {
        await api.deleteUser(user.id);
        showToast(`Deleted ${user.email}`, 'success');
        await fetchUsers();
        confirmModal.value.show = false;
      } catch (err) {
        showToast(err.response?.data?.detail || 'Failed to delete user', 'error');
      } finally {
        confirmModal.value.loading = false;
      }
    }
  };
};

const toggleRole = async (user) => {
  const newRole = user.role === 'user' ? 'admin' : 'user';
  try {
    await api.updateUserRole(user.id, newRole);
    showToast(`Role updated to "${newRole}" for ${user.email}`, 'success');
    await fetchUsers();
  } catch (err) {
    showToast(err.response?.data?.detail || 'Failed to update role', 'error');
  }
};

const formatDate = (dateStr) => {
  if (!dateStr) return '-';
  return new Date(dateStr).toLocaleString('th-TH', { timeZone: 'Asia/Bangkok' });
};

onMounted(fetchUsers);
</script>

<template>
  <div class="admin-page">
    <Toast :show="toast.show" :message="toast.message" :type="toast.type" @close="toast.show = false" />
    <ConfirmModal
      :show="confirmModal.show"
      :title="confirmModal.title"
      :message="confirmModal.message"
      :loading="confirmModal.loading"
      confirm-text="Delete"
      cancel-text="Cancel"
      type="danger"
      @confirm="confirmModal.onConfirm"
      @cancel="confirmModal.show = false"
      @close="confirmModal.show = false"
    />

    <!-- Header -->
    <header class="admin-header">
      <div class="header-left">
        <button class="back-btn" @click="router.push('/')">
          <svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"/></svg>
          Dashboard
        </button>
        <div>
          <h1>🛡 Admin Panel</h1>
          <p>Manage user accounts</p>
        </div>
      </div>
      <div class="header-badge">
        Superadmin: {{ authStore.user?.email }}
      </div>
    </header>

    <!-- Content -->
    <main class="admin-content">
      <div class="panel">
        <div class="panel-header">
          <h2>Users <span class="count">{{ users.length }}</span></h2>
        </div>

        <div v-if="loading" class="loading-state">
          <div class="spinner"></div>
          <p>Loading users...</p>
        </div>

        <div v-else-if="users.length === 0" class="empty-state">
          <p>No users found.</p>
        </div>

        <table v-else class="users-table">
          <thead>
            <tr>
              <th>Name</th>
              <th>Email</th>
              <th>Role</th>
              <th>Created</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="user in users" :key="user.id" :class="{ 'row--self': user.email === authStore.user?.email }">
              <td>
                <div class="user-info">
                  <div class="avatar">{{ user.name?.slice(0,2).toUpperCase() }}</div>
                  <span>{{ user.name }}</span>
                </div>
              </td>
              <td class="email-cell">{{ user.email }}</td>
              <td>
                <span class="role-badge" :class="user.role">{{ user.role }}</span>
              </td>
              <td>{{ formatDate(user.created_at) }}</td>
              <td>
                <div class="action-buttons">
                  <button
                    v-if="user.email !== authStore.user?.email && user.role !== 'superadmin'"
                    class="btn btn-role"
                    :title="user.role === 'admin' ? 'Demote to user' : 'Promote to admin'"
                    @click="toggleRole(user)"
                  >
                    {{ user.role === 'admin' ? '⬇ Demote' : '⬆ Promote to Admin' }}
                  </button>
                  <button
                    v-if="user.email !== authStore.user?.email"
                    class="btn btn-delete"
                    @click="confirmDelete(user)"
                  >
                    🗑 Delete
                  </button>
                  <span v-else class="self-label">You</span>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </main>
  </div>
</template>

<style scoped>
.admin-page {
  min-height: 100vh;
  background:
    radial-gradient(circle at 15% 10%, rgba(14, 165, 233, 0.12), transparent 40%),
    radial-gradient(circle at 85% 5%, rgba(139, 92, 246, 0.10), transparent 40%),
    #020617;
  color: #e2e8f0;
  font-family: 'Trebuchet MS', 'Segoe UI', sans-serif;
}

.admin-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 12px;
  padding: 20px 28px;
  background: rgba(15, 23, 42, 0.92);
  border-bottom: 1px solid rgba(148, 163, 184, 0.2);
  backdrop-filter: blur(12px);
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.header-left h1 {
  margin: 0;
  font-size: 1.4rem;
  color: #f8fafc;
}

.header-left p {
  margin: 2px 0 0;
  font-size: 0.8rem;
  color: #94a3b8;
}

.back-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  border: 1px solid rgba(148, 163, 184, 0.3);
  border-radius: 10px;
  background: rgba(15, 23, 42, 0.78);
  color: #cbd5e1;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}
.back-btn:hover { background: rgba(51, 65, 85, 0.6); }
.back-btn svg { width: 16px; height: 16px; }

.header-badge {
  padding: 6px 14px;
  border: 1px solid rgba(139, 92, 246, 0.4);
  border-radius: 999px;
  background: rgba(139, 92, 246, 0.12);
  color: #c4b5fd;
  font-size: 0.78rem;
}

.admin-content {
  padding: 28px;
  max-width: 1200px;
  margin: 0 auto;
}

.panel {
  border: 1px solid rgba(148, 163, 184, 0.2);
  border-radius: 16px;
  background: rgba(15, 23, 42, 0.74);
  overflow: hidden;
}

.panel-header {
  padding: 16px 20px;
  border-bottom: 1px solid rgba(148, 163, 184, 0.18);
}

.panel-header h2 {
  margin: 0;
  font-size: 1.1rem;
  color: #f8fafc;
  display: flex;
  align-items: center;
  gap: 10px;
}

.count {
  padding: 2px 10px;
  background: rgba(14, 165, 233, 0.2);
  border-radius: 999px;
  color: #38bdf8;
  font-size: 0.8rem;
}

.loading-state, .empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 60px 20px;
  color: #64748b;
}

.spinner {
  width: 36px;
  height: 36px;
  border: 3px solid rgba(56, 189, 248, 0.2);
  border-top-color: #38bdf8;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

.users-table {
  width: 100%;
  border-collapse: collapse;
}

.users-table th {
  padding: 12px 16px;
  text-align: left;
  font-size: 0.78rem;
  font-weight: 600;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  border-bottom: 1px solid rgba(148, 163, 184, 0.18);
}

.users-table td {
  padding: 14px 16px;
  font-size: 0.88rem;
  color: #cbd5e1;
  border-bottom: 1px solid rgba(148, 163, 184, 0.1);
}

.users-table tr:last-child td { border-bottom: none; }

.row--self td { background: rgba(14, 165, 233, 0.04); }

.user-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.avatar {
  width: 34px;
  height: 34px;
  border-radius: 50%;
  background: linear-gradient(135deg, #0ea5e9, #8b5cf6);
  color: white;
  font-size: 0.75rem;
  font-weight: 700;
  display: grid;
  place-items: center;
  flex-shrink: 0;
}

.email-cell { color: #94a3b8; font-size: 0.82rem; }

.role-badge {
  padding: 3px 10px;
  border-radius: 999px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
}
.role-badge.superadmin {
  background: rgba(139, 92, 246, 0.2);
  color: #c4b5fd;
  border: 1px solid rgba(139, 92, 246, 0.35);
}
.role-badge.admin {
  background: rgba(14, 165, 233, 0.15);
  color: #38bdf8;
  border: 1px solid rgba(14, 165, 233, 0.35);
}
.role-badge.user {
  background: rgba(100, 116, 139, 0.2);
  color: #94a3b8;
  border: 1px solid rgba(100, 116, 139, 0.3);
}

.action-buttons {
  display: flex;
  gap: 8px;
  align-items: center;
}

.btn {
  padding: 6px 12px;
  border-radius: 8px;
  font-size: 0.8rem;
  font-weight: 600;
  border: 1px solid;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-role {
  background: rgba(14, 165, 233, 0.1);
  border-color: rgba(14, 165, 233, 0.35);
  color: #38bdf8;
}
.btn-role:hover { background: rgba(14, 165, 233, 0.2); }

.btn-delete {
  background: rgba(239, 68, 68, 0.1);
  border-color: rgba(239, 68, 68, 0.3);
  color: #f87171;
}
.btn-delete:hover { background: rgba(239, 68, 68, 0.2); }

.self-label {
  font-size: 0.78rem;
  color: #475569;
  font-style: italic;
}
</style>
