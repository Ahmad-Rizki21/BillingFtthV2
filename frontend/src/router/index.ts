import { createRouter, createWebHistory } from 'vue-router';
import DefaultLayout from '@/layouts/DefaultLayout.vue';

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      redirect: '/dashboard'
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('@/views/LoginView.vue'),
      meta: { guest: true }
    },
    {
      path: '/',
      component: DefaultLayout,
      meta: { requiresAuth: true },
      children: [
        {
          path: 'dashboard',
          name: 'dashboard',
          component: () => import('@/views/DashboardView.vue'),
        },
        // {
        //   path: 'pelanggan',
        //   name: 'pelanggan',
        //   component: () => import('@/views/PelangganView.vue'), // Buat view ini nanti
        // },
        // {
        //   path: 'invoices',
        //   name: 'invoices', 
        //   component: () => import('@/views/InvoicesView.vue'), // Buat view ini nanti
        // }
      ],
    },
  ],
});

// Navigation guard
router.beforeEach(async (to, _from, next) => {
  const token = localStorage.getItem('access_token');
  const isAuthenticated = !!token;
  
  // Jika route memerlukan autentikasi tapi user belum login
  if (to.meta.requiresAuth && !isAuthenticated) {
    return next('/login');
  }
  
  // Jika user sudah login tapi mengakses halaman guest (login)
  if (to.meta.guest && isAuthenticated) {
    return next('/dashboard');
  }
  
  next();
});

export default router;