import axios from 'axios';
import { getTokenFromStorage, removeToken } from '../utils/jwt';

const api = axios.create({
    baseURL: import.meta.env.VITE_API_URL || '/api',
    headers: {
        'Content-Type': 'application/json',
    },
});

// Request interceptor - Add Authorization header with JWT token
api.interceptors.request.use(
    (config) => {
        const token = getTokenFromStorage();
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

// Response interceptor - Handle 401 errors (unauthorized)
api.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response?.status === 401) {
            // Token invalid/expired - redirect to login
            removeToken();
            window.location.href = '/login';
        }
        return Promise.reject(error);
    }
);

export default {
    // Camera endpoints
    getCameras() {
        return api.get('/cameras');
    },
    getCamera(id) {
        return api.get(`/cameras/${id}`);
    },
    createCamera(data) {
        return api.post('/cameras', data);
    },
    updateCamera(id, data) {
        return api.put(`/cameras/${id}`, data);
    },
    deleteCamera(id) {
        return api.delete(`/cameras/${id}`);
    },
    checkCameraBlur(id) {
        return api.post(`/cameras/${id}/check-blur`);
    },
    getStatus() {
        return api.get('/status');
    },
    checkAllCamerasStatus() {
        return api.post('/cameras/check-status');
    },
    checkCameraStatus(id) {
        return api.post(`/cameras/${id}/check`);
    },

    // Auth endpoints
    getMe() {
        return api.get('/auth/me');
    },
    logout() {
        return api.post('/auth/logout');
    },
    getAuthStatus() {
        return api.get('/auth/status');
    },

    // User management endpoints (superadmin only)
    getUsers() {
        return api.get('/users');
    },
    deleteUser(id) {
        return api.delete(`/users/${id}`);
    },
    updateUserRole(id, role) {
        return api.put(`/users/${id}/role`, { role });
    }
};
