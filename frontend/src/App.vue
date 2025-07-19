<script setup lang="ts">
import { RouterLink, RouterView } from 'vue-router'
</script>

<template>
  <div> <header>
      <div class="wrapper">
        <nav>
          <RouterLink to="/">Home</RouterLink>
          <RouterLink to="/login">Login</RouterLink>
        </nav>
      </div>
    </header>

    <RouterView />
  </div> </template>

<style scoped>
/* Anda bisa menambahkan styling dasar di sini */
header {
  line-height: 1.5;
  max-height: 100vh;
  padding: 1rem 0;
  border-bottom: 1px solid #333;
}
nav {
  width: 100%;
  font-size: 12px;
  text-align: center;
}
nav a {
  display: inline-block;
  padding: 0 1rem;
  border-left: 1px solid var(--color-border);
}
nav a:first-of-type {
  border: 0;
}
</style>