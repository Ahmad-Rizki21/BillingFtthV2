<template>
  <div>
    <h1>Selamat Datang di Dashboard!</h1>
    <p>Anda berhasil login sebagai {{ authStore.user?.email }}.</p>
    <router-link to="/pelanggan">Ke Halaman Pelanggan</router-link>
    <button @click="authStore.logout">Logout</button>
  </div>
</template>
<script setup lang="ts">
import { useAuthStore } from '@/stores/auth';
const authStore = useAuthStore();
</script>