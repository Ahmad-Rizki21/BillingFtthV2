<script setup lang="ts">
import { RouterLink } from 'vue-router';
import { useAuthStore } from '@/stores/auth';

const authStore = useAuthStore();
</script>

<template>
  <div class="app-layout">
    <aside class="sidebar">
      <h2>Billing System</h2>
      <nav>
        <RouterLink to="/dashboard">Dashboard</RouterLink>
        <!-- <RouterLink to="/pelanggan">Pelanggan</RouterLink>
        <RouterLink to="/invoices">Invoices</RouterLink> -->
        <button @click="authStore.logout" class="logout-btn">Logout</button>
      </nav>
    </aside>
    <main class="main-content">
      <RouterView />
    </main>
  </div>
</template>

<style scoped>
.app-layout {
  display: flex;
}
.sidebar {
  width: 250px;
  background: #f4f4f4;
  padding: 1rem;
}
.logout-btn {
  margin-top: 1rem;
  padding: 0.5rem;
  background: #ff4444;
  color: white;
  border: none;
  cursor: pointer;
}
.main-content {
  flex: 1;
  padding: 1rem;
}
</style>