import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { jwtDecode } from 'jwt-decode';
import api from '../services/api';
import { getTokenFromStorage, setToken, removeToken, isTokenExpired } from '../utils/jwt';

export const useAuthStore = defineStore('auth', () => {
    // State
    const user = ref(null);
    const token = ref(null);

    // Getters
    const isAuthenticated = computed(() => {
        return !!token.value && !isTokenExpired(token.value);
    });

    const userProfile = computed(() => user.value);

    // Actions
    function login(accessToken) {
        token.value = accessToken;
        setToken(accessToken);

        // Decode token to get user info
        try {
            const decoded = jwtDecode(accessToken);
            user.value = {
                id: decoded.sub,
                email: decoded.email,
                name: decoded.name
            };
        } catch (error) {
            console.error('Failed to decode token:', error);
            logout();
        }
    }

    function logout() {
        user.value = null;
        token.value = null;
        removeToken();
    }

    async function checkAuth() {
        const storedToken = getTokenFromStorage();

        if (!storedToken || isTokenExpired(storedToken)) {
            logout();
            return false;
        }

        token.value = storedToken;
        try {
            const decoded = jwtDecode(storedToken);
            user.value = {
                id: decoded.sub,
                email: decoded.email,
                name: decoded.name
            };
            return true;
        } catch (error) {
            console.error('Failed to validate stored token:', error);
            logout();
            return false;
        }
    }

    async function fetchUser() {
        try {
            const response = await api.getMe();
            user.value = response.data;
            return user.value;
        } catch (error) {
            console.error('Failed to fetch user:', error);
            logout();
            throw error;
        }
    }

    return {
        // State
        user,
        token,
        // Getters
        isAuthenticated,
        userProfile,
        // Actions
        login,
        logout,
        checkAuth,
        fetchUser
    };
});
