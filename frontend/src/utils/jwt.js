import { jwtDecode } from 'jwt-decode';

const TOKEN_KEY = 'auth_token';

/**
 * Decode a JWT token
 * @param {string} token - JWT token string
 * @returns {object} Decoded token payload
 */
export function decodeToken(token) {
    try {
        return jwtDecode(token);
    } catch (error) {
        console.error('Failed to decode token:', error);
        return null;
    }
}

/**
 * Check if a JWT token is expired
 * @param {string} token - JWT token string
 * @returns {boolean} True if expired, false otherwise
 */
export function isTokenExpired(token) {
    if (!token) return true;

    try {
        const decoded = jwtDecode(token);
        if (!decoded.exp) return false;

        const currentTime = Date.now() / 1000;
        return decoded.exp < currentTime;
    } catch (error) {
        console.error('Failed to check token expiration:', error);
        return true;
    }
}

/**
 * Get token from localStorage
 * @returns {string|null} Token string or null
 */
export function getTokenFromStorage() {
    return localStorage.getItem(TOKEN_KEY);
}

/**
 * Save token to localStorage
 * @param {string} token - JWT token string
 */
export function setToken(token) {
    localStorage.setItem(TOKEN_KEY, token);
}

/**
 * Remove token from localStorage
 */
export function removeToken() {
    localStorage.removeItem(TOKEN_KEY);
}
