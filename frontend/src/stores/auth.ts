// src/stores/auth.ts
import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import apiClient from '@/services/api';

// Definisikan tipe data untuk Role dan Permission
interface Permission {
  name: string;
}

interface Role {
  name: string;
  permissions?: Permission[];
}

// Definisikan tipe data untuk User
interface User {
  id: number;
  email: string;
  name: string;
  // Role bisa berupa objek atau string (untuk kasus sederhana)
  role?: Role | string; 
}

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(localStorage.getItem('access_token'));
  const user = ref<User | null>(null);
  
  const isAuthenticated = computed(() => !!token.value);

  function setToken(newToken: string) {
    localStorage.setItem('access_token', newToken);
    token.value = newToken;
  }

  function logout() {
    localStorage.removeItem('access_token');
    token.value = null;
    user.value = null;
  }

  async function verifyToken(): Promise<boolean> {
    if (!token.value) {
        return false;
    }
    try {
        const response = await apiClient.get<User>('/users/me');
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
        const response = await apiClient.post(
            '/users/token',
            `username=${encodeURIComponent(email)}&password=${encodeURIComponent(password)}`,
            {
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
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