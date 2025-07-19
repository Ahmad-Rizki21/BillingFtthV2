import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
// Hapus import useRouter yang tidak digunakan
// import { useRouter } from 'vue-router';
import axios from 'axios';

interface User {
  id: number;
  email: string;
  name: string;
  role?: string;
}

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(localStorage.getItem('access_token'));
  const user = ref<User | null>(null);
  
  // Computed
  const isAuthenticated = computed(() => !!token.value);

  // Actions
  function setToken(newToken: string) {
    localStorage.setItem('access_token', newToken);
    token.value = newToken;
  }

  function logout() {
    localStorage.removeItem('access_token');
    token.value = null;
    user.value = null;
    
    // Redirect ke login - gunakan window.location
    window.location.href = '/login';
  }

  async function verifyToken(): Promise<boolean> {
    if (!token.value) {
      return false;
    }

    try {
      const response = await axios.get('http://127.0.0.1:8000/users/me', {
        headers: {
          Authorization: `Bearer ${token.value}`,
        },
      });
      
      user.value = response.data;
      return true;
    } catch (error) {
      console.error('Token verification failed:', error);
      logout();
      return false;
    }
  }

  async function login(email: string, password: string): Promise<boolean> {
    try {
      const response = await axios.post(
        'http://127.0.0.1:8000/users/token',
        `username=${encodeURIComponent(email)}&password=${encodeURIComponent(password)}`,
        {
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
          },
        }
      );

      setToken(response.data.access_token);
      return await verifyToken();
    } catch (error) {
      console.error('Login failed:', error);
      return false;
    }
  }

  return { 
    token, 
    user, 
    isAuthenticated, 
    setToken, 
    logout, 
    verifyToken,
    login
  };
});