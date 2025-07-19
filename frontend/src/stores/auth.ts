// frontend/src/stores/auth.ts
import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { useRouter } from 'vue-router';

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('access_token'));
  const router = useRouter();

  const isAuthenticated = computed(() => !!token.value);

  function setToken(newToken: string) {
    localStorage.setItem('access_token', newToken);
    token.value = newToken;
  }

  function logout() {
    localStorage.removeItem('access_token');
    token.value = null;
    router.push('/login');
  }

  return { token, isAuthenticated, setToken, logout };
});