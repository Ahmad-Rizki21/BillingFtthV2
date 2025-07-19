// src/router/index.ts

import { createRouter, createWebHistory } from 'vue-router';
import DefaultLayout from '@/layouts/DefaultLayout.vue';
import DashboardView from '../views/DashboardView.vue';

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    // Rute untuk halaman yang memerlukan login (DIBUNGKUS OLEH DefaultLayout)
    {
      path: '/',
      component: DefaultLayout,
      meta: { requiresAuth: true },
      children: [
        // TAMBAHKAN INI: Jika user ke path '/', langsung arahkan ke dashboard
        { path: '', redirect: '/dashboard' },
        
        // Definisikan semua halaman di sini
        {
          path: 'dashboard',
          name: 'dashboard',
          component: DashboardView
        },
        // Contoh jika ada halaman lain
        // {
        //   path: 'pelanggan',
        //   name: 'pelanggan',
        //   component: () => import('../views/PelangganView.vue')
        // },
      ],
    },

    // Rute untuk halaman login (TIDAK ADA LAYOUT)
    {
      path: '/login',
      name: 'login',
      component: () => import('../views/LoginView.vue'),
      meta: { guest: true }
    },
  ],
});

// Navigation guard Anda sudah benar, biarkan seperti ini.
router.beforeEach(async (to, _from, next) => {
  const token = localStorage.getItem('access_token');
  const isAuthenticated = !!token;
  
  if (to.meta.requiresAuth && !isAuthenticated) {
    return next('/login');
  }
  
  if (to.meta.guest && isAuthenticated) {
    return next('/dashboard');
  }
  
  next();
});

export default router;