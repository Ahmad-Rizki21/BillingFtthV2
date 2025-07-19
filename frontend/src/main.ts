// frontend/src/main.ts

import './assets/main.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router' // <-- 1. Impor router

const app = createApp(App)

app.use(createPinia())
app.use(router) // <-- 2. Pasang router ke aplikasi

app.mount('#app')