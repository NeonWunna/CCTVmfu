<template>
  <div class="login-page" :style="{ '--bg-image': `url(${backgroundImage})` }">
    <div class="header">
      <div class="header-content">
        <img :src="logoSrc" alt="MFU Logo" class="logo" @error="handleLogoError">
        <div class="title-placeholder">
          <h1>มหาวิทยาลัยแม่ฟ้าหลวง</h1>
          <p>MAE FAH LUANG UNIVERSITY</p>
        </div>
      </div>
    </div>

    <div class="main-content">
      <div class="login-card">
        <div class="mfu-logo-circle">
          <span>MFU</span>
        </div>

        <h1 class="login-title">Login to CCTV Spot</h1>
        <p class="login-subtitle">Login to view CCTV within Mae Fah Luang University</p>
        <p class="login-time">24/7 time</p>

        <div class="login-buttons">
          <button class="login-btn google-btn" @click="loginWithGoogle">
            <svg class="google-icon" viewBox="0 0 24 24">
              <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" />
              <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" />
              <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" />
              <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" />
            </svg>
            Sign in with Google
          </button>

          <button class="login-btn sso-btn" @click="loginWithSSO">
            Login
          </button>
        </div>
      </div>
    </div>

    <div class="footer">
      © 2025 Mae Fah Luang University. All rights reserved.
    </div>
  </div>
</template>

<script>
import backgroundImage from '../assets/envi.jpg';
import logoSrc from '../assets/mfu-logo.png';

export default {
  name: 'LoginPage',
  data() {
    return {
      backgroundImage,
      logoSrc,
    };
  },
  methods: {
    loginWithGoogle() {
      alert('Google Sign-In will be implemented here');
    },
    loginWithSSO() {
      this.$router.push('/monitoring');
    },
    handleLogoError(event) {
      event.target.style.display = 'none';
    },
  },
};
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

.login-page {
  --bg-image: url('../assets/envi.jpg');
  margin: 0;
  padding: 0;
  box-sizing: border-box;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  background: var(--bg-image) no-repeat center center fixed;
  background-size: cover;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  position: relative;
}

.login-page::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.3);
  z-index: 1;
}

.header,
.main-content,
.footer {
  position: relative;
  z-index: 2;
}

.header {
  padding: 12px 20px;
  background: rgba(255, 255, 255, 0.95);
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.header-content {
  display: flex;
  align-items: center;
  gap: 15px;
  max-width: none;
  margin: 0;
}

.logo {
  height: 48px;
  width: auto;
}

.title-placeholder {
  flex: 1;
}

.title-placeholder h1 {
  font-size: 24px;
  color: #374151;
  margin-bottom: 4px;
}

.title-placeholder p {
  font-size: 14px;
  color: #6b7280;
}

.main-content {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
}

.login-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  padding: 40px;
  width: 100%;
  max-width: 440px;
  text-align: center;
}

.mfu-logo-circle {
  width: 80px;
  height: 80px;
  background: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 24px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.mfu-logo-circle span {
  font-size: 28px;
  font-weight: 700;
  color: #991b1b;
}

.login-title {
  font-size: 28px;
  font-weight: 700;
  color: #1f2937;
  margin-bottom: 8px;
}

.login-subtitle {
  font-size: 14px;
  color: #6b7280;
  margin-bottom: 8px;
}

.login-time {
  font-size: 13px;
  color: #9ca3af;
  margin-bottom: 32px;
}

.login-buttons {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.login-btn {
  width: 100%;
  padding: 14px 24px;
  border: none;
  border-radius: 8px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
}

.google-btn {
  background: white;
  color: #374151;
  border: 2px solid #e5e7eb;
}

.google-btn:hover {
  background: #f9fafb;
  border-color: #d1d5db;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.google-icon {
  width: 20px;
  height: 20px;
}

.sso-btn {
  background: #991b1b;
  color: white;
}

.sso-btn:hover {
  background: #7f1d1d;
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(153, 27, 27, 0.4);
}

.footer {
  padding: 20px;
  text-align: center;
  color: white;
  font-size: 13px;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.5);
}

@media (max-width: 768px) {
  .header {
    padding: 10px 14px;
  }

  .header-content h1 {
    font-size: 18px;
  }

  .header-content p {
    font-size: 12px;
  }

  .logo {
    height: 40px;
  }

  .login-card {
    padding: 32px 24px;
  }

  .login-title {
    font-size: 24px;
  }

  .main-content {
    padding: 20px;
  }
}
</style>

