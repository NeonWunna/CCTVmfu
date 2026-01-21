<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import logoUrl from '../assets/mfu-logo.png';
import backgroundImg from '../assets/envi.jpg';

const router = useRouter();
const isLoading = ref(false);
const googleLoading = ref(false);

const handleLogoError = (event) => {
  event.target.style.display = 'none';
};

const loginWithGoogle = async () => {
  googleLoading.value = true;
  
  // Simulate API call delay
  await new Promise(resolve => setTimeout(resolve, 1500));
  
  // For testing, allow Google login
  localStorage.setItem('isAuthenticated', 'true');
  router.push('/');
};

const loginWithSSO = async () => {
  isLoading.value = true;
  
  // Simulate API call delay
  await new Promise(resolve => setTimeout(resolve, 1500));
  
  // Set authentication token
  localStorage.setItem('isAuthenticated', 'true');
  // Navigate to the Dashboard
  router.push('/');
};
</script>

<template>
  <div class="login-container">
    <!-- Header - Matching Home.vue -->
    <header class="header">
      <div class="header-content">
        <div class="header-left">
          <img :src="logoUrl" alt="MFU Logo" class="logo" @error="handleLogoError">
          <div class="header-text">
            <h1>CCTV Monitoring System</h1>
            <p>Mae Fah Luang University - Real-time Surveillance</p>
          </div>
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <main class="main-content">
      <div class="login-card">
        <!-- MFU Logo Circle -->
        <div class="mfu-logo-circle">
          <span>MFU</span>
        </div>

        <!-- Login Title -->
        <h2 class="login-title">Welcome Back</h2>
        <p class="login-subtitle">Sign in to access the CCTV Monitoring System</p>
        <p class="login-time">Available 24/7</p>

        <!-- Login Buttons -->
        <div class="login-buttons">
          <button 
            class="login-btn google-btn" 
            @click="loginWithGoogle"
            :disabled="googleLoading || isLoading"
          >
            <svg v-if="!googleLoading" class="google-icon" viewBox="0 0 24 24">
              <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
              <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
              <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
              <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
            </svg>
            <div v-else class="spinner"></div>
            <span>{{ googleLoading ? 'Signing in...' : 'Sign in with Google' }}</span>
          </button>

          <div class="divider">
            <span>OR</span>
          </div>

          <button 
            class="login-btn sso-btn" 
            @click="loginWithSSO"
            :disabled="isLoading || googleLoading"
          >
            <svg v-if="!isLoading" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1"></path>
            </svg>
            <div v-else class="spinner"></div>
            <span>{{ isLoading ? 'Signing in...' : 'Sign in with SSO' }}</span>
          </button>
        </div>

        <!-- Additional Info -->
        <div class="login-info">
          <p>Need help? Contact IT Support</p>
        </div>
      </div>
    </main>

    <!-- Footer -->
    <footer class="footer">
      <p>© 2025 Mae Fah Luang University. All rights reserved.</p>
    </footer>
  </div>
</template>

<style scoped>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

.login-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background-image: linear-gradient(135deg, rgba(102, 126, 234, 0.85) 0%, rgba(118, 75, 162, 0.85) 100%), url('../assets/envi.jpg');
  background-size: cover;
  background-position: center;
  background-attachment: fixed;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

/* Header Styles - Matching Home.vue */
.header {
  background: rgba(255, 255, 255, 0.98);
  box-shadow: 0 2px 20px rgba(0, 0, 0, 0.1);
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-content {
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px 30px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 15px;
}

.logo {
  height: 60px;
  width: auto;
}

.header-text h1 {
  font-size: 24px;
  color: #2d3748;
  font-weight: 700;
  margin-bottom: 4px;
  letter-spacing: -0.5px;
}

.header-text p {
  font-size: 14px;
  color: #718096;
  font-weight: 400;
}

/* Main Content */
.main-content {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 3rem 1.5rem;
}

.login-card {
  background: white;
  border-radius: 20px;
  padding: 3rem 2.5rem;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  max-width: 440px;
  width: 100%;
  text-align: center;
  animation: slideUp 0.6s ease-out;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* MFU Logo Circle */
.mfu-logo-circle {
  width: 100px;
  height: 100px;
  margin: 0 auto 2rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% {
    box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
  }
  50% {
    box-shadow: 0 10px 40px rgba(102, 126, 234, 0.5);
  }
}

.mfu-logo-circle span {
  font-size: 2rem;
  font-weight: 700;
  color: white;
  letter-spacing: 2px;
}

/* Login Text */
.login-title {
  font-size: 1.875rem;
  color: #2d3748;
  font-weight: 700;
  margin-bottom: 0.5rem;
}

.login-subtitle {
  font-size: 1rem;
  color: #718096;
  margin-bottom: 0.5rem;
  line-height: 1.5;
}

.login-time {
  font-size: 0.875rem;
  color: #667eea;
  font-weight: 600;
  margin-bottom: 2rem;
}

/* Login Buttons */
.login-buttons {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.login-btn {
  width: 100%;
  padding: 0.875rem 1.5rem;
  border: none;
  border-radius: 12px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  position: relative;
  overflow: hidden;
}

.login-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.login-btn:not(:disabled):hover {
  transform: translateY(-2px);
}

.login-btn:not(:disabled):active {
  transform: translateY(0);
}

.google-btn {
  background: white;
  color: #2d3748;
  border: 2px solid #e2e8f0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.google-btn:not(:disabled):hover {
  border-color: #cbd5e0;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.google-icon {
  width: 20px;
  height: 20px;
  flex-shrink: 0;
}

.sso-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
}

.sso-btn:not(:disabled):hover {
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.5);
}

.sso-btn svg {
  width: 20px;
  height: 20px;
  flex-shrink: 0;
}

/* Divider */
.divider {
  position: relative;
  text-align: center;
  margin: 0.5rem 0;
}

.divider::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 0;
  right: 0;
  height: 1px;
  background: #e2e8f0;
}

.divider span {
  position: relative;
  display: inline-block;
  padding: 0 1rem;
  background: white;
  color: #a0aec0;
  font-size: 0.875rem;
  font-weight: 600;
}

/* Loading Spinner */
.spinner {
  width: 20px;
  height: 20px;
  border: 3px solid rgba(255, 255, 255, 0.3);
  border-top-color: currentColor;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

.google-btn .spinner {
  border: 3px solid rgba(0, 0, 0, 0.1);
  border-top-color: #667eea;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Login Info */
.login-info {
  padding-top: 1.5rem;
  border-top: 1px solid #e2e8f0;
  margin-top: 1rem;
}

.login-info p {
  font-size: 0.875rem;
  color: #718096;
}

/* Footer */
.footer {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  padding: 1.5rem;
  text-align: center;
}

.footer p {
  color: white;
  font-size: 0.875rem;
  opacity: 0.9;
}

/* Responsive Design */
@media (max-width: 768px) {
  .header-content {
    padding: 15px 20px;
  }

  .header-text h1 {
    font-size: 18px;
  }

  .header-text p {
    font-size: 12px;
  }

  .logo {
    height: 45px;
  }

  .main-content {
    padding: 2rem 1rem;
  }

  .login-card {
    padding: 2rem 1.5rem;
  }

  .login-title {
    font-size: 1.5rem;
  }

  .login-subtitle {
    font-size: 0.875rem;
  }

  .mfu-logo-circle {
    width: 80px;
    height: 80px;
  }

  .mfu-logo-circle span {
    font-size: 1.5rem;
  }
}

@media (max-width: 480px) {
  .header-left {
    gap: 10px;
  }

  .header-text h1 {
    font-size: 16px;
  }

  .header-text p {
    display: none;
  }

  .login-card {
    padding: 1.5rem 1rem;
  }

  .login-btn {
    font-size: 0.875rem;
    padding: 0.75rem 1.25rem;
  }
}

/* Focus States for Accessibility */
.login-btn:focus {
  outline: none;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.3);
}

.google-btn:focus {
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.2), 0 2px 8px rgba(0, 0, 0, 0.1);
}
</style>