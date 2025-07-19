<script setup lang="ts">
import { ref } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';

const email = ref('');
const password = ref('');
const error = ref('');
const router = useRouter();

async function handleLogin() {
  error.value = '';

  const params = new URLSearchParams();
  params.append('username', email.value);
  params.append('password', password.value);

  try {
    const response = await axios.post('http://127.0.0.1:8000/users/token', params);
    localStorage.setItem('access_token', response.data.access_token);
    await router.push('/dashboard'); // Nanti kita buat halaman ini
  } catch (err) {
    console.error('Login failed:', err);
    error.value = 'Login gagal. Periksa kembali email dan password Anda.';
  }
}
</script>

<template>
  <div class="login-container">
    <form @submit.prevent="handleLogin" class="login-form">
      <h2>Halaman Login</h2>
      <div class="form-group">
        <label for="email">Email</label>
        <input type="email" id="email" v-model="email" required />
      </div>
      <div class="form-group">
        <label for="password">Password</label>
        <input type="password" id="password" v-model="password" required />
      </div>
      <div v-if="error" class="error-message">{{ error }}</div>
      <button type="submit">Login</button>
    </form>
  </div>
</template>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  padding-top: 5rem;
}
.login-form {
  padding: 2rem;
  border: 1px solid #444;
  border-radius: 8px;
  width: 100%;
  max-width: 400px;
}
.form-group {
  margin-bottom: 1rem;
}
label {
  display: block;
  margin-bottom: 0.5rem;
}
input {
  width: 100%;
  padding: 0.5rem;
  box-sizing: border-box;
}
.error-message {
  color: red;
  margin-bottom: 1rem;
}
button {
  width: 100%;
  padding: 0.75rem;
  border: none;
  background-color: #42b883;
  color: white;
  cursor: pointer;
  border-radius: 4px;
}
</style>