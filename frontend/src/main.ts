// frontend/src/main.ts

import './assets/main.css'
import { createApp } from 'vue'
import { createPinia } from 'pinia'

// 1. Impor semua yang dibutuhkan
import App from './App.vue'
import router from './router'
import 'vuetify/styles'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'
import '@mdi/font/css/materialdesignicons.css'

// 2. Buat instance Vuetify TERLEBIH DAHULU
const vuetify = createVuetify({
  components,
  directives,
})

// 3. Buat aplikasi Vue
const app = createApp(App)

// 4. Pasang semua plugin (Pinia, Router, dan Vuetify)
app.use(createPinia())
app.use(router)
app.use(vuetify) // Sekarang variabel 'vuetify' sudah ada

// 5. Mount aplikasi
app.mount('#app')