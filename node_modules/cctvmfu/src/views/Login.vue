<script setup>
import { useRouter } from 'vue-router';
import logoUrl from '../assets/mfu-logo.png';
import '../assets/login.css';

const router = useRouter();

const loginWithGoogle = () => {
    alert('Google Sign-In will be implemented here');
    // For testing, let's also allow Google login to work
    localStorage.setItem('isAuthenticated', 'true');
    router.push('/');
};

const loginWithSSO = () => {
    // Set authentication token
    localStorage.setItem('isAuthenticated', 'true');
    // Navigate to the Dashboard
    router.push('/');
};
</script>

<template>
    <div class="login-container">
                 <!-- Header - Space for Logo and University Name -->
        <div class="header" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
            <div class="header-content">
                <img :src="logoUrl" alt="MFU Logo" class="logo">
                <div class="title-placeholder" style="color: white;">
                    <h1 style="color: white;">มหาวิทยาลัยแม่ฟ้าหลวง</h1>
                    <p style="color: white;">MAE FAH LUANG UNIVERSITY</p>
                </div>
            </div>
        </div>

        <!-- Main Content -->
        <div class="main-content">
            <div class="login-card">
                <!-- MFU Logo Circle -->
                <div class="mfu-logo-circle">
                    <span>MFU</span>
                </div>

                <!-- Login Title -->
                <h1 class="login-title">Login to CCTV Spot</h1>
                <p class="login-subtitle">Login to view CCTV within Mae Fah Luang University</p>
                <p class="login-time">24/7 time</p>

                <!-- Login Buttons -->
                <div class="login-buttons">
                    <button class="login-btn google-btn" @click="loginWithGoogle">
                        <svg class="google-icon" viewBox="0 0 24 24">
                            <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                            <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                            <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                            <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
                        </svg>
                        Sign in with Google
                    </button>

                    <button class="login-btn sso-btn" @click="loginWithSSO">
                        Login
                    </button>
                </div>
            </div>
        </div>

        <!-- Footer -->
        <div class="footer">
            © 2025 Mae Fah Luang University. All rights reserved.
        </div>
    </div>
</template>
