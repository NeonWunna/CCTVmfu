import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import Login from '../views/Login.vue'
import CameraSettings from '../views/CameraSettings.vue'
import CameraView from '../views/CameraView.vue'
import AdminPanel from '../views/AdminPanel.vue'
import { useAuthStore } from '../stores/auth'
import { isTokenExpired, getTokenFromStorage } from '../utils/jwt'

const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes: [
        {
            path: '/login',
            name: 'login',
            component: Login
        },
        {
            path: '/',
            name: 'home',
            component: Home,
            meta: { requiresAuth: true }
        },
        {
            path: '/camera-settings',
            name: 'CameraSettings',
            component: CameraSettings,
            meta: { requiresAuth: true }
        },
        {
            path: '/camera/:id',
            name: 'CameraView',
            component: CameraView,
            meta: { requiresAuth: true }
          },
          {
            path: '/admin',
            name: 'AdminPanel',
            component: AdminPanel,
            meta: { requiresAuth: true, requiresSuperAdmin: true }
          }
    ]
})

// Authentication guard with JWT validation
router.beforeEach(async (to, from, next) => {
    const authStore = useAuthStore();
    const token = getTokenFromStorage();

    if (to.meta.requiresAuth) {
        // Route requires authentication
        if (!token || isTokenExpired(token)) {
            // No token or expired - redirect to login
            next('/login');
        } else {
            // Valid token exists
            if (!authStore.user) {
                // User not loaded yet - restore from token
                await authStore.checkAuth();
            }
            // Check superadmin requirement
            if (to.meta.requiresSuperAdmin && !authStore.isSuperAdmin) {
                next('/');
                return;
            }
            next();
        }
    } else if (to.name === 'login' && token && !isTokenExpired(token)) {
        // Already logged in - redirect to home
        next('/');
    } else {
        // Public route or unauthenticated user on login page
        next();
    }
});

export default router
