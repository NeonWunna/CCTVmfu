import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import Login from '../views/Login.vue'

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
        }
    ]
})

// Mock authentication guard
router.beforeEach((to, from, next) => {
    // In a real app, check for token/session here
    const isAuthenticated = false; // Mock: set to true to allow easy testing, or false to force login flow

    if (to.meta.requiresAuth && !isAuthenticated) {
        next('/login');
    } else {
        next();
    }
});

export default router
