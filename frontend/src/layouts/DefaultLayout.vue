<template>
  <div class="app-layout">
    <aside class="sidebar">
      <h2>Billing System</h2>
      <nav>
        <RouterLink to="/dashboard">Dashboard</RouterLink>
        <RouterLink to="/pelanggan">Pelanggan</RouterLink>
        <RouterLink to="/invoices">Invoices</RouterLink>
      </nav>
    </aside>
    <main class="main-content">
      <header class="top-nav">
        </header>
      <div class="content-wrapper">
        <RouterView />
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { RouterLink, RouterView } from 'vue-router';
</script>

<style scoped>
/* ... (tambahkan styling untuk layout, sidebar, dll) ... */
</style>