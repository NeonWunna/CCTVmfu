import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import Login from '../views/Login.vue'
import CameraSettings from '../views/CameraSettings.vue'
import CameraView from '../views/CameraView.vue'

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
          }
    ]
})

// Mock authentication guard
router.beforeEach((to, from, next) => {
    // Check for authentication flag in localStorage
    const isAuthenticated = localStorage.getItem('isAuthenticated') === 'true';

    if (to.meta.requiresAuth && !isAuthenticated) {
        next('/login');
    } else if (to.name === 'login' && isAuthenticated) {
        // Redirect to home if already logged in and trying to access login page
        next('/');
    } else {
        next();
    }
});

export default router
