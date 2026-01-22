import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000',
  timeout: 30000,
});

// Add token to every request
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('authToken');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle 401 errors (redirect to login)
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('authToken');
      localStorage.removeItem('isAuthenticated');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth functions
export const authAPI = {
  loginWithGoogle: (token) => api.post('/api/auth/google', { token }),
  loginWithSSO: (token) => api.post('/api/auth/sso', { token }),
  logout: () => api.post('/api/auth/logout'),
};

// Camera functions
export const cameraAPI = {
  getAll: () => api.get('/api/cameras'),
  create: (data) => api.post('/api/cameras', data),
  update: (id, data) => api.put(`/api/cameras/${id}`, data),
  delete: (id) => api.delete(`/api/cameras/${id}`),
};

export default api;