<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();
const isLoading = ref(false);
const googleLoading = ref(false);

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
    <!-- Main Content -->
    <main class="main-content">
      <div class="login-card">
        <!-- CCTV Icon Animation -->
        <div class="cctv-icon-wrapper">
          <div class="cctv-camera">
            <svg class="camera-svg" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"></path>
            </svg>
            <div class="scanning-line"></div>
          </div>
          <div class="signal-waves">
            <div class="wave wave-1"></div>
            <div class="wave wave-2"></div>
            <div class="wave wave-3"></div>
          </div>
        </div>

        <!-- Login Title -->
        <h2 class="login-title">CCTV Monitoring System</h2>
        <p class="login-subtitle">Mae Fah Luang University</p>
        <p class="login-status">
          <span class="status-dot"></span>
          System Online - Secure Access
        </p>

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
            <span>{{ googleLoading ? 'Authenticating...' : 'Sign in with Google' }}</span>
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
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"></path>
            </svg>
            <div v-else class="spinner"></div>
            <span>{{ isLoading ? 'Authenticating...' : 'Sign in with SSO' }}</span>
          </button>
        </div>

        <!-- Security Info -->
        <div class="security-info">
          <div class="security-badge">
            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"></path>
            </svg>
            <span>Secured Connection</span>
          </div>
          <p class="support-text">Need help? Contact IT Support</p>
        </div>
      </div>

      <!-- Floating Info Card -->
      <div class="info-card">
        <div class="info-item">
          <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
          </svg>
          <div>
            <div class="info-label">24/7 Monitoring</div>
            <div class="info-value">Always Active</div>
          </div>
        </div>
        <div class="info-item">
          <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"></path>
          </svg>
          <div>
            <div class="info-label">Secure Access</div>
            <div class="info-value">Encrypted</div>
          </div>
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
  background-image: linear-gradient(135deg, rgba(26, 32, 44, 0.75) 0%, rgba(45, 55, 72, 0.85) 100%), url('../assets/envi.jpg');
  background-size: cover;
  background-position: center;
  background-attachment: fixed;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  position: relative;
}

.login-container::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: radial-gradient(circle at 50% 50%, rgba(102, 126, 234, 0.1) 0%, transparent 50%);
  pointer-events: none;
}

/* Main Content */
.main-content {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 3rem 1.5rem;
  gap: 3rem;
  flex-wrap: wrap;
  position: relative;
  z-index: 1;
}

/* Login Card with CCTV Theme */
.login-card {
  background: rgba(26, 32, 44, 0.95);
  backdrop-filter: blur(20px);
  border: 2px solid rgba(102, 126, 234, 0.3);
  border-radius: 24px;
  padding: 3rem 2.5rem;
  box-shadow: 
    0 20px 60px rgba(0, 0, 0, 0.5),
    0 0 0 1px rgba(255, 255, 255, 0.1) inset,
    0 0 40px rgba(102, 126, 234, 0.2);
  max-width: 440px;
  width: 100%;
  text-align: center;
  animation: slideUp 0.6s ease-out;
  position: relative;
  overflow: hidden;
}

.login-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, #667eea 0%, #764ba2 50%, #667eea 100%);
  background-size: 200% 100%;
  animation: shimmer 3s linear infinite;
}

@keyframes shimmer {
  0% { background-position: -200% 0; }
  100% { background-position: 200% 0; }
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

/* CCTV Camera Icon with Animation */
.cctv-icon-wrapper {
  position: relative;
  width: 120px;
  height: 120px;
  margin: 0 auto 2rem;
}

.cctv-camera {
  width: 100px;
  height: 100px;
  margin: 10px auto;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 
    0 10px 40px rgba(102, 126, 234, 0.4),
    0 0 0 8px rgba(102, 126, 234, 0.1),
    0 0 0 16px rgba(102, 126, 234, 0.05);
  position: relative;
  overflow: hidden;
}

.camera-svg {
  width: 48px;
  height: 48px;
  color: white;
  position: relative;
  z-index: 2;
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.3));
}

/* Scanning Line Effect */
.scanning-line {
  position: absolute;
  top: -100%;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.8), transparent);
  animation: scan 2s ease-in-out infinite;
}

@keyframes scan {
  0%, 100% {
    top: -100%;
    opacity: 0;
  }
  10% {
    opacity: 1;
  }
  90% {
    opacity: 1;
  }
  100% {
    top: 200%;
    opacity: 0;
  }
}

/* Signal Waves */
.signal-waves {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 100%;
  height: 100%;
}

.wave {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 100%;
  height: 100%;
  border: 2px solid rgba(102, 126, 234, 0.5);
  border-radius: 50%;
  animation: pulse-wave 3s ease-out infinite;
}

.wave-1 { animation-delay: 0s; }
.wave-2 { animation-delay: 1s; }
.wave-3 { animation-delay: 2s; }

@keyframes pulse-wave {
  0% {
    width: 100%;
    height: 100%;
    opacity: 1;
  }
  100% {
    width: 200%;
    height: 200%;
    opacity: 0;
  }
}

/* Login Text */
.login-title {
  font-size: 1.875rem;
  color: white;
  font-weight: 700;
  margin-bottom: 0.5rem;
  text-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
}

.login-subtitle {
  font-size: 1rem;
  color: rgba(255, 255, 255, 0.8);
  margin-bottom: 1rem;
  line-height: 1.5;
}

.login-status {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: rgba(16, 185, 129, 0.15);
  border: 1px solid rgba(16, 185, 129, 0.3);
  border-radius: 20px;
  font-size: 0.875rem;
  color: #10b981;
  font-weight: 600;
  margin-bottom: 2rem;
}

.status-dot {
  width: 8px;
  height: 8px;
  background: #10b981;
  border-radius: 50%;
  box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.2);
  animation: pulse-dot 2s ease-in-out infinite;
}

@keyframes pulse-dot {
  0%, 100% {
    box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.2);
  }
  50% {
    box-shadow: 0 0 0 6px rgba(16, 185, 129, 0.1);
  }
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
  padding: 1rem 1.5rem;
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

.login-btn::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 0;
  height: 0;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
  transition: width 0.6s, height 0.6s;
}

.login-btn:hover::before {
  width: 300px;
  height: 300px;
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
  background: rgba(255, 255, 255, 0.1);
  color: white;
  border: 2px solid rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
}

.google-btn:not(:disabled):hover {
  border-color: rgba(255, 255, 255, 0.3);
  background: rgba(255, 255, 255, 0.15);
  box-shadow: 0 4px 20px rgba(255, 255, 255, 0.1);
}

.google-icon {
  width: 20px;
  height: 20px;
  flex-shrink: 0;
}

.sso-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: 2px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 4px 20px rgba(102, 126, 234, 0.4);
}

.sso-btn:not(:disabled):hover {
  box-shadow: 0 6px 30px rgba(102, 126, 234, 0.6);
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
  background: rgba(255, 255, 255, 0.1);
}

.divider span {
  position: relative;
  display: inline-block;
  padding: 0 1rem;
  background: rgba(26, 32, 44, 0.95);
  color: rgba(255, 255, 255, 0.5);
  font-size: 0.75rem;
  font-weight: 600;
  letter-spacing: 1px;
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

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Security Info */
.security-info {
  padding-top: 1.5rem;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  margin-top: 1rem;
}

.security-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 6px 14px;
  background: rgba(16, 185, 129, 0.1);
  border: 1px solid rgba(16, 185, 129, 0.2);
  border-radius: 20px;
  margin-bottom: 0.75rem;
}

.security-badge svg {
  width: 16px;
  height: 16px;
  color: #10b981;
}

.security-badge span {
  font-size: 0.75rem;
  color: #10b981;
  font-weight: 600;
}

.support-text {
  font-size: 0.875rem;
  color: rgba(255, 255, 255, 0.6);
}

/* Floating Info Card */
.info-card {
  background: rgba(26, 32, 44, 0.9);
  backdrop-filter: blur(20px);
  border: 2px solid rgba(102, 126, 234, 0.2);
  border-radius: 20px;
  padding: 2rem;
  max-width: 320px;
  width: 100%;
  box-shadow: 
    0 20px 60px rgba(0, 0, 0, 0.4),
    0 0 0 1px rgba(255, 255, 255, 0.05) inset;
  animation: slideUp 0.8s ease-out;
  animation-delay: 0.2s;
  opacity: 0;
  animation-fill-mode: forwards;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 12px;
  margin-bottom: 1rem;
}

.info-item:last-child {
  margin-bottom: 0;
}

.info-item svg {
  width: 32px;
  height: 32px;
  color: #667eea;
  flex-shrink: 0;
}

.info-label {
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.6);
  margin-bottom: 4px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.info-value {
  font-size: 1rem;
  color: white;
  font-weight: 600;
}

/* Footer */
.footer {
  background: rgba(0, 0, 0, 0.3);
  backdrop-filter: blur(10px);
  padding: 1.5rem;
  text-align: center;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.footer p {
  color: rgba(255, 255, 255, 0.8);
  font-size: 0.875rem;
}

/* Responsive Design */
@media (max-width: 1024px) {
  .main-content {
    flex-direction: column;
    gap: 2rem;
  }

  .info-card {
    max-width: 440px;
  }
}

@media (max-width: 768px) {
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

  .cctv-icon-wrapper {
    width: 100px;
    height: 100px;
  }

  .cctv-camera {
    width: 80px;
    height: 80px;
  }

  .camera-svg {
    width: 40px;
    height: 40px;
  }

  .info-card {
    padding: 1.5rem;
  }
}

@media (max-width: 480px) {
  .login-card {
    padding: 1.5rem 1rem;
  }

  .login-btn {
    font-size: 0.875rem;
    padding: 0.875rem 1.25rem;
  }

  .info-item {
    padding: 0.75rem;
  }

  .info-item svg {
    width: 28px;
    height: 28px;
  }
}

/* Focus States for Accessibility */
.login-btn:focus {
  outline: none;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.5);
}

.google-btn:focus {
  box-shadow: 0 0 0 3px rgba(255, 255, 255, 0.3);
}
</style>