<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import axios, { AxiosError } from 'axios'; // Impor AxiosResponse

// Definisikan tipe untuk respons error dari backend
interface ErrorResponse {
  detail?: string;
  message?: string;
}

const email = ref('');
const password = ref('');
const resetEmail = ref('');
const newPassword = ref('');
const error = ref('');
const successMessage = ref('');
const loading = ref(false);
const showForgotPassword = ref(false);
const router = useRouter();
const authStore = useAuthStore();
const resetToken = ref(''); // Untuk menyimpan token dari forgot password

async function handleLogin() {
  if (!email.value || !password.value) {
    error.value = 'Email dan password harus diisi';
    return;
  }

  error.value = '';
  loading.value = true;

  try {
    const success = await authStore.login(email.value, password.value);
    // console.log('Login success:', success);
    if (success) {
      router.push('/dashboard');
    } else {
      error.value = 'Email atau password salah!';
    }
  } catch (err) {
    const errorResponse = err as AxiosError<ErrorResponse>;
    console.error('Login error:', errorResponse.response?.data || errorResponse.message);
    error.value = errorResponse.response?.data?.detail || errorResponse.response?.data?.message || 'Terjadi kesalahan saat login';
  } finally {
    loading.value = false;
  }
}

async function handleResetPassword() {
  if (!resetEmail.value || !newPassword.value || !resetToken.value) {
    error.value = 'Email, password baru, dan token harus diisi';
    return;
  }

  error.value = '';
  successMessage.value = '';
  loading.value = true;

  try {
    const response = await axios.post<{ message: string }>('http://127.0.0.1:8000/users/reset-password', {
      email: resetEmail.value,
      new_password: newPassword.value,
      token: resetToken.value,
    }, {
      headers: { 'Content-Type': 'application/json' },
    });
    successMessage.value = response.data.message;
    showForgotPassword.value = false; // Kembali ke login setelah sukses
    setTimeout(() => router.push('/login'), 2000);
  } catch (err) {
    const errorResponse = err as AxiosError<ErrorResponse>;
    console.error('Reset password error:', errorResponse.response?.data || errorResponse.message);
    error.value = errorResponse.response?.data?.detail || errorResponse.response?.data?.message || 'Terjadi kesalahan saat reset password';
  } finally {
    loading.value = false;
  }
}

// function toggleForgotPassword() {
//   showForgotPassword.value = !showForgotPassword.value;
//   error.value = '';
//   successMessage.value = '';
//   resetEmail.value = '';
//   newPassword.value = '';
//   resetToken.value = ''; // Reset token
// }

function backToLogin() {
  showForgotPassword.value = false;
  error.value = '';
  successMessage.value = '';
}
</script>

<template>
  <div class="login-wrapper">
    <!-- Background Network Animation -->
    <div class="network-bg">
      <div class="network-node" v-for="i in 20" :key="i" :style="{
        left: Math.random() * 100 + '%',
        top: Math.random() * 100 + '%',
        animationDelay: Math.random() * 2 + 's'
      }"></div>
    </div>

    <!-- Main Login Container -->
    <div class="login-container">
      <!-- Left Panel - Branding -->
      <div class="branding-panel">
        <div class="brand-content">
         <div class="logo-container">
            <div class="logo-icon">
              <img src="@/assets/images/Jelantik 1.webp" alt="Logo" style="width: 200px; height: 110px; bottom: 100px; border-radius: 10px;" />
            </div>
            <h1 class="brand-name">Artacom Billing V1</h1>
          </div>
          
          <div class="brand-description">
            <h2>System Managemant</h2>
            <p>Sistem yang di rancang dengan detail serta memberikan
              kemudahan akses ke Third Party dengan Payment Gateway.
            </p>
            
            <div class="features-list">
              <div class="feature-item">
                <div class="feature-icon">⚡</div>
                <span>Billing Otomatis</span>
              </div>
              <div class="feature-item">
                <div class="feature-icon">📊</div>
                <span>Real-time Monitoring</span>
              </div>
              <div class="feature-item">
                <div class="feature-icon">👥</div>
                <span>Manajemen Pelanggan</span>
              </div>
              <div class="feature-item">
                <div class="feature-icon">🔒</div>
                <span>Keamanan Tinggi</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Right Panel - Login/Forgot Password Form -->
      <div class="login-panel">
        <div class="login-form-container">
          <!-- Login Form -->
          <div v-if="!showForgotPassword" class="form-section">
            <div class="form-header">
              <h3>Masuk ke Sistem</h3>
              <p>Akses dashboard billing dan monitoring</p>
            </div>

            <form @submit.prevent="handleLogin" class="login-form">
              <div class="form-group">
                <label for="email" class="form-label">
                  <span class="label-icon">📧</span>
                  Email Address
                </label>
                <div class="input-container">
                  <input 
                    id="email"
                    type="email" 
                    v-model="email" 
                    required 
                    :disabled="loading"
                    placeholder="admin@provider.com"
                    class="form-input"
                  />
                </div>
              </div>
              
              <div class="form-group">
                <label for="password" class="form-label">
                  <span class="label-icon">🔐</span>
                  Password
                </label>
                <div class="input-container">
                  <input 
                    id="password"
                    type="password" 
                    v-model="password" 
                    required 
                    :disabled="loading"
                    placeholder="••••••••"
                    class="form-input"
                  />
                </div>
              </div>
              
              <div v-if="error" class="error-message">
                <div class="error-icon">⚠️</div>
                <span>{{ error }}</span>
              </div>
              
              <button type="submit" :disabled="loading" class="login-button">
                <span v-if="loading" class="loading-spinner"></span>
                <span class="button-text">
                  {{ loading ? 'Memproses...' : 'Masuk ke Sistem' }}
                </span>
                <span v-if="!loading" class="button-arrow">→</span>
              </button>

              <!-- <div class="form-footer">
                <button type="button" @click="toggleForgotPassword" class="forgot-link">
                  Lupa password?
                </button>
              </div> -->
            </form>
          </div>

          <!-- Forgot Password Form -->
          <div v-else class="form-section forgot-section">
            <div class="form-header">
              <div class="back-button" @click="backToLogin">
                <span class="back-arrow">←</span>
              </div>
              <h3>Reset Password</h3>
              <p>Masukkan email dan password baru untuk mengatur ulang</p>
            </div>

            <form @submit.prevent="handleResetPassword" class="forgot-form">
              <div class="form-group">
                <label for="reset-email" class="form-label">
                  <span class="label-icon">📧</span>
                  Email Address
                </label>
                <div class="input-container">
                  <input 
                    id="reset-email"
                    type="email" 
                    v-model="resetEmail" 
                    required 
                    :disabled="loading"
                    placeholder="admin@provider.com"
                    class="form-input"
                  />
                </div>
              </div>
              
              <div class="form-group">
                <label for="new-password" class="form-label">
                  <span class="label-icon">🔐</span>
                  Password Baru
                </label>
                <div class="input-container">
                  <input 
                    id="new-password"
                    type="password" 
                    v-model="newPassword" 
                    required 
                    :disabled="loading"
                    placeholder="••••••••"
                    class="form-input"
                  />
                </div>
              </div>
              
              <div v-if="error" class="error-message">
                <div class="error-icon">⚠️</div>
                <span>{{ error }}</span>
              </div>

              <div v-if="successMessage" class="success-message">
                <div class="success-icon">✅</div>
                <span>{{ successMessage }}</span>
              </div>
              
              <button type="submit" :disabled="loading" class="reset-button">
                <span v-if="loading" class="loading-spinner"></span>
                <span class="button-text">
                  {{ loading ? 'Mengirim...' : 'Atur Ulang Password' }}
                </span>
                <span v-if="!loading" class="button-arrow">📤</span>
              </button>

              <div class="form-footer">
                <button type="button" @click="backToLogin" class="back-to-login">
                  Kembali ke halaman login
                </button>
              </div>
            </form>

            <!-- Security Notice -->
            <div class="security-notice">
              <div class="notice-icon">🔐</div>
              <div class="notice-content">
                <h4>Catatan Keamanan</h4>
                <p>Password yang sudah di ubah, tolong di ingat kembali, karena tidak ada OTP saat kembali Login.</p>
              </div>
            </div>
          </div>
        </div>

        <!-- System Status -->
        <div class="system-status">
          <div class="status-item">
            <div class="status-indicator online"></div>
            <span>Sistem Online</span>
          </div>
          <div class="status-item">
            <div class="status-indicator"></div>
            <span>Database Connected</span>
          </div>
          <div class="status-item">
            <div class="status-indicator"></div>
            <span>Email Service Active</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Hapus 'space-y' karena bukan properti CSS standar */
.login-form,
.forgot-form {
  /* Ganti 'space-y: 1.5rem' dengan margin-bottom manual */
  margin-bottom: 1.5rem; /* Sesuaikan dengan kebutuhan */
}

.form-group {
  margin-bottom: 1.5rem;
}

/* Sisanya biarkan seperti aslinya */
.login-wrapper {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: linear-gradient(135deg, #0f172a 0%, #1e293b 25%, #334155 100%);
  overflow: hidden;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

/* Network Background Animation */
.network-bg {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  opacity: 0.1;
  z-index: 1;
}

.network-node {
  position: absolute;
  width: 4px;
  height: 4px;
  background: #3b82f6;
  border-radius: 50%;
  animation: pulse 2s infinite ease-in-out;
}

.network-node::before {
  content: '';
  position: absolute;
  width: 20px;
  height: 20px;
  border: 1px solid #3b82f6;
  border-radius: 50%;
  top: -8px;
  left: -8px;
  animation: ripple 2s infinite ease-out;
}

@keyframes pulse {
  0%, 100% { opacity: 0.3; transform: scale(1); }
  50% { opacity: 1; transform: scale(1.2); }
}

@keyframes ripple {
  0% { opacity: 1; transform: scale(0); }
  100% { opacity: 0; transform: scale(1); }
}

/* Main Layout */
.login-container {
  position: relative;
  display: flex;
  width: 100%;
  height: 100vh;
  z-index: 2;
}

.branding-panel {
  flex: 1;
  background: rgba(15, 23, 42, 0.8);
  backdrop-filter: blur(20px);
  border-right: 1px solid rgba(59, 130, 246, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 3rem;
}

.brand-content {
  max-width: 500px;
  text-align: center;
}

.logo-container {
  margin-bottom: 3rem;
}

.logo-icon {
  width: 80px;
  height: 80px;
  margin: 0 auto 1rem;
  background: linear-gradient(135deg, #3b82f6, #1d4ed8);
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 10px 30px rgba(59, 130, 246, 0.3);
}

.logo-icon svg {
  width: 40px;
  height: 40px;
  color: white;
}

.brand-name {
  font-size: 2.5rem;
  font-weight: 700;
  color: white;
  margin-bottom: 0.5rem;
  text-shadow: 0 2px 10px rgba(59, 130, 246, 0.3);
}

.brand-description h2 {
  font-size: 1.5rem;
  color: #e2e8f0;
  margin-bottom: 1rem;
  font-weight: 600;
}

.brand-description p {
  color: #94a3b8;
  font-size: 1.1rem;
  line-height: 1.6;
  margin-bottom: 2rem;
}

.features-list {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  margin-top: 2rem;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #cbd5e1;
  font-size: 0.95rem;
}

.feature-icon {
  font-size: 1.2rem;
}

/* Login Panel */
.login-panel {
  flex: 1;
  background: rgba(255, 255, 255, 0.98);
  backdrop-filter: blur(20px);
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 3rem;
  position: relative;
}

.login-form-container {
  max-width: 400px;
  width: 100%;
  margin: 0 auto;
}

.form-section {
  transition: all 0.3s ease;
}

.forgot-section {
  animation: slideIn 0.3s ease-out;
}

@keyframes slideIn {
  from { opacity: 0; transform: translateX(20px); }
  to { opacity: 1; transform: translateX(0); }
}

.form-header {
  text-align: center;
  margin-bottom: 2.5rem;
  position: relative;
}

.back-button {
  position: absolute;
  left: 0;
  top: 0;
  width: 40px;
  height: 40px;
  border-radius: 10px;
  background: #f8fafc;
  border: 1px solid #e5e7eb;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 1.2rem;
  color: #64748b;
}

.back-button:hover {
  background: #e2e8f0;
  transform: translateX(-2px);
}

.form-header h3 {
  font-size: 1.8rem;
  color: #1e293b;
  font-weight: 700;
  margin-bottom: 0.5rem;
}

.form-header p {
  color: #64748b;
  font-size: 1rem;
}

.login-form, .forgot-form {
  margin-bottom: 1.5rem
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
  font-weight: 600;
  color: #374151;
  font-size: 0.9rem;
}

.label-icon {
  font-size: 1rem;
}

.input-container {
  position: relative;
}

.form-input {
  width: 100%;
  padding: 1rem 1.2rem;
  border: 2px solid #e5e7eb;
  border-radius: 12px;
  font-size: 1rem;
  background: #f9fafb;
  transition: all 0.3s ease;
  color: #1f2937;
}

.form-input:focus {
  outline: none;
  border-color: #3b82f6;
  background: white;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
  transform: translateY(-1px);
}

.form-input:disabled {
  background-color: #f3f4f6;
  cursor: not-allowed;
  opacity: 0.7;
}

.error-message {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #dc2626;
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.2);
  padding: 0.75rem 1rem;
  border-radius: 10px;
  font-size: 0.9rem;
  margin-bottom: 1.5rem;
  animation: shake 0.5s ease-in-out;
}

.success-message {
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
  color: #059669;
  background: rgba(16, 185, 129, 0.1);
  border: 1px solid rgba(16, 185, 129, 0.2);
  padding: 0.75rem 1rem;
  border-radius: 10px;
  font-size: 0.9rem;
  margin-bottom: 1.5rem;
  line-height: 1.4;
}

.login-button, .reset-button {
  width: 100%;
  padding: 1.2rem;
  background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  box-shadow: 0 4px 15px rgba(59, 130, 246, 0.4);
  position: relative;
  overflow: hidden;
}

.reset-button {
  background: linear-gradient(135deg, #059669 0%, #047857 100%);
  box-shadow: 0 4px 15px rgba(5, 150, 105, 0.4);
}

.login-button:hover:not(:disabled), .reset-button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 25px rgba(59, 130, 246, 0.6);
}

.reset-button:hover:not(:disabled) {
  box-shadow: 0 6px 25px rgba(5, 150, 105, 0.6);
}

.login-button:active:not(:disabled), .reset-button:active:not(:disabled) {
  transform: translateY(0px);
}

.login-button:disabled, .reset-button:disabled {
  background: linear-gradient(135deg, #9ca3af 0%, #6b7280 100%);
  cursor: not-allowed;
  transform: none;
}

.loading-spinner {
  width: 20px;
  height: 20px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top: 2px solid white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.button-arrow {
  transition: transform 0.3s ease;
}

.login-button:hover .button-arrow, .reset-button:hover .button-arrow {
  transform: translateX(4px);
}

.form-footer {
  text-align: center;
  margin-top: 1.5rem;
}

.forgot-link, .back-to-login {
  color: #3b82f6;
  background: none;
  border: none;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: color 0.3s ease;
  text-decoration: none;
}

.forgot-link:hover, .back-to-login:hover {
  color: #1d4ed8;
  text-decoration: underline;
}

/* Security Notice */
.security-notice {
  margin-top: 2rem;
  padding: 1rem;
  background: rgba(59, 130, 246, 0.05);
  border: 1px solid rgba(59, 130, 246, 0.1);
  border-radius: 10px;
  display: flex;
  gap: 0.75rem;
  align-items: flex-start;
}

.notice-icon {
  font-size: 1.2rem;
  flex-shrink: 0;
}

.notice-content h4 {
  font-size: 0.9rem;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 0.25rem;
}

.notice-content p {
  font-size: 0.8rem;
  color: #64748b;
  line-height: 1.4;
}

/* System Status */
.system-status {
  position: absolute;
  bottom: 2rem;
  left: 3rem;
  right: 3rem;
  display: flex;
  justify-content: center;
  gap: 2rem;
}

.status-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.8rem;
  color: #6b7280;
}

.status-indicator {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #22c55e;
  position: relative;
}

.status-indicator::before {
  content: '';
  position: absolute;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: inherit;
  animation: ping 1s cubic-bezier(0, 0, 0.2, 1) infinite;
}

.status-indicator.online {
  background: #22c55e;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

@keyframes shake {
  0%, 100% { transform: translateX(0); }
  25% { transform: translateX(-3px); }
  75% { transform: translateX(3px); }
}

@keyframes ping {
  75%, 100% {
    transform: scale(2);
    opacity: 0;
  }
}

/* Responsive */
@media (max-width: 768px) {
  .login-container {
    flex-direction: column;
  }
  
  .branding-panel {
    flex: 0 0 auto;
    padding: 2rem 1.5rem 1rem;
  }
  
  .brand-content {
    max-width: none;
  }
  
  .brand-name {
    font-size: 1.8rem;
  }
  
  .features-list {
    grid-template-columns: 1fr;
    gap: 0.5rem;
  }
  
  .login-panel {
    flex: 1;
    padding: 1.5rem;
    justify-content: flex-start;
  }
  
  .system-status {
    position: static;
    margin-top: 2rem;
    flex-direction: column;
    gap: 1rem;
    align-items: center;
  }
}

@media (max-width: 480px) {
  .branding-panel {
    padding: 1.5rem 1rem 0.5rem;
  }
  
  .login-panel {
    padding: 1rem;
  }
  
  .login-form-container {
    max-width: none;
  }
  
  .form-header h3 {
    font-size: 1.5rem;
  }
  
  .brand-description p {
    font-size: 1rem;
  }

  .system-status {
    gap: 0.5rem;
  }
}
</style>