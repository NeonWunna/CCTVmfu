import axios from 'axios';

const api = axios.create({
    baseURL: '/api',
    headers: {
        'Content-Type': 'application/json',
    },
});

export default {
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
    getStatus() {
        return api.get('/status');
    }
};
