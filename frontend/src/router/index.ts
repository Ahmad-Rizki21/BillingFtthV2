// frontend/src/router/index.ts

import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import LoginView from '../views/LoginView.vue'
import DashboardView from '../views/DashboardView.vue';

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView
    },
    {
      path: '/login',
      name: 'login',
      component: LoginView
    },
    {
      path: '/dashboard',
      name: 'dashboard',
      component: DashboardView
    }
  ]
})

router.beforeEach((to, from, next) => {
  const isAuthenticated = !!localStorage.getItem('access_token');
  const publicPages = ['/login']; // Halaman yang bisa diakses tanpa login

  const authRequired = !publicPages.includes(to.path);

  if (authRequired && !isAuthenticated) {
    // Jika butuh login tapi belum login, arahkan ke halaman login
    return next('/login');
  }

  next(); // Lanjutkan navigasi
});

export default router