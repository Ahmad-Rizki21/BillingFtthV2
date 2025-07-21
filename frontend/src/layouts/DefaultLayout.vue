<template>
  <v-app class="modern-app">
    <v-navigation-drawer
      v-model="drawer"
      :rail="rail"
      permanent
      class="modern-drawer"
      width="280"
    >
      <v-list-item class="sidebar-header" :class="{'px-0': rail}" :ripple="false">
        <div class="header-flex-container">
          <img v-if="!rail" :src="logoJelantik" alt="Jelantik Logo" class="sidebar-logo-full"/>
          <v-icon v-if="rail" color="primary" size="large">mdi-alpha-j</v-icon>

          <div v-if="!rail" class="sidebar-title-wrapper">
            <h1 class="sidebar-title">Artacom</h1>
            <span class="sidebar-subtitle">BILLING SYSTEM</span>
          </div>

          <v-spacer v-if="!rail"></v-spacer>

          <v-btn
            v-if="!rail"
            icon="mdi-chevron-left"
            variant="text"
            size="small"
            @click.stop="rail = !rail"
          ></v-btn>
        </div>
      </v-list-item>

      <v-divider></v-divider>

      <div class="navigation-wrapper">
        <v-list nav class="navigation-menu">
          <template v-for="group in menuGroups" :key="group.title">
            <v-list-subheader v-if="!rail" class="menu-subheader">{{ group.title }}</v-list-subheader>
            <v-list-item
              v-for="item in group.items"
              :key="item.title"
              :prepend-icon="item.icon"
              :title="item.title"
              :value="item.value"
              :to="item.to"
              class="nav-item"
              :active-class="'v-list-item--active'"
            >
              <template v-slot:append v-if="item.badge !== undefined && !rail">
                <v-tooltip location="end" :disabled="item.badge === 0">
                  <template v-slot:activator="{ props }">
                    <v-chip 
                      v-bind="props"
                      v-if="item.badge > 0"
                      size="small" 
                      class="badge-chip" 
                      :color="item.badgeColor"
                    >
                      {{ item.badge }}
                    </v-chip>
                  </template>
                  <span v-if="item.value === 'langganan'">{{ item.badge }} langganan ditangguhkan</span>
                </v-tooltip>
              </template>
            </v-list-item>
          </template>
        </v-list>
      </div>

      <template v-slot:append>
        <div class="logout-section pa-4">
          <v-btn
            :block="!rail"
            variant="tonal"
            color="grey-darken-1"
            class="logout-btn"
            :icon="rail"
            @click="handleLogout"
          >
            <v-icon v-if="rail">mdi-logout</v-icon>
            <span v-if="!rail" class="d-flex align-center"><v-icon left>mdi-logout</v-icon>Logout</span>
          </v-btn>
        </div>
      </template>
    </v-navigation-drawer>

    <v-app-bar elevation="0" class="modern-app-bar">
      <v-btn
        icon="mdi-menu"
        variant="text"
        @click.stop="rail = !rail"
      ></v-btn>
      <v-spacer></v-spacer>
      
      <v-btn icon variant="text" @click="toggleTheme" class="header-action-btn theme-toggle-btn">
        <v-icon>{{ theme.global.current.value.dark ? 'mdi-weather-sunny' : 'mdi-weather-night' }}</v-icon>
      </v-btn>

      <v-menu offset-y>
        <template v-slot:activator="{ props }">
          <v-btn icon variant="text" class="header-action-btn" v-bind="props">
            <v-badge :content="notifications.length" color="error" :model-value="notifications.length > 0">
              <v-icon>mdi-bell-outline</v-icon>
            </v-badge>
          </v-btn>
        </template>
        <v-list class="pa-0" width="300">
          <v-list-item class="font-weight-bold bg-grey-lighten-4">
              Notifikasi
              <template v-slot:append v-if="notifications.length > 0">
                  <v-btn variant="text" size="small" @click="notifications = []">Bersihkan</v-btn>
              </template>
          </v-list-item>
          <v-divider></v-divider>
          <div v-if="notifications.length === 0" class="text-center text-medium-emphasis pa-4">
              Tidak ada notifikasi baru.
          </div>
          <v-list-item
            v-for="(notif, index) in notifications"
            :key="index"
            class="py-2"
          >
            <template v-slot:prepend>
              <v-avatar color="success" size="32" class="me-3">
                  <v-icon size="18">mdi-cash-check</v-icon>
              </v-avatar>
            </template>
            <v-list-item-title class="font-weight-medium text-body-2">Pembayaran Diterima</v-list-item-title>
            <v-list-item-subtitle class="text-caption">
              <strong>{{ notif.data.invoice_number }}</strong> dari <strong>{{ notif.data.pelanggan_nama }}</strong> ({{ notif.data.id_pelanggan }}) telah lunas.
            </v-list-item-subtitle>
          </v-list-item>
        </v-list>
      </v-menu>
    </v-app-bar>

    <v-main class="modern-main">
      <router-view></router-view>
    </v-main>
    
    <v-footer app height="60" class="d-flex align-center justify-center text-medium-emphasis" style="border-top: 1px solid rgba(0,0,0,0.08);">
      <div>
        &copy; {{ new Date().getFullYear() }} <strong>Artacom Billing System</strong>. All Rights Reserved by 
        <a 
          href="https://www.instagram.com/amad.dyk/" 
          target="_blank" 
          rel="noopener noreferrer"
          class="text-decoration-none text-primary"
        >
          amad.dyk
        </a>
      </div>
    </v-footer>

  </v-app>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router';
import { ref, onMounted } from 'vue';
import logoJelantik from '@/assets/images/Jelantik.webp';
import { useTheme } from 'vuetify';
import apiClient from '@/services/api';

const theme = useTheme();
const drawer = ref(true);
const rail = ref(false);
const router = useRouter();
const notifications = ref<any[]>([]);

// SOLUSI YANG BENAR: Gunakan metode yang tidak deprecated
function toggleTheme() {
  const newTheme = theme.global.current.value.dark ? 'light' : 'dark';
  theme.global.name.value = newTheme;
  localStorage.setItem('theme', newTheme);
}
const suspendedCount = ref(0);

// Saat komponen pertama kali dimuat, cek localStorage
onMounted(() => {
  const savedTheme = localStorage.getItem('theme');
  if (savedTheme && (savedTheme === 'light' || savedTheme === 'dark')) {
    theme.global.name.value = savedTheme;
  }
});


//Notifikasi
function setupWebSocket() {
    // Gunakan wss:// jika production Anda menggunakan HTTPS
    const ws = new WebSocket("ws://127.0.0.1:8000/ws/notifications");

    ws.onmessage = (event) => {
        console.log("Menerima notifikasi:", event.data);
        const message = JSON.parse(event.data);

        // Tambahkan notifikasi baru ke awal daftar
        if (message.type === 'new_payment') {
            notifications.value.unshift(message);
            
            // (Opsional) Batasi jumlah notifikasi yang ditampilkan
            if (notifications.value.length > 10) {
                notifications.value.pop();
            }
        }
    };

    ws.onopen = () => {
        console.log("WebSocket terhubung.");
    };

    ws.onclose = () => {
        console.log("WebSocket terputus. Mencoba menghubungkan kembali dalam 5 detik...");
        setTimeout(setupWebSocket, 5000); // Coba hubungkan kembali
    };

    ws.onerror = (error) => {
        console.error("WebSocket error:", error);
        ws.close();
    };
}


const menuGroups = ref([
  { title: 'DASHBOARD', items: [{ title: 'Dashboard', icon: 'mdi-home-variant', value: 'dashboard', to: '/dashboard' }] },
  { title: 'FTTH', items: [
      { title: 'Data Pelanggan', icon: 'mdi-account-group-outline', value: 'pelanggan', to: '/pelanggan' },
      { title: 'Langganan', icon: 'mdi-wifi-star', value: 'langganan', to: '/langganan', badge: suspendedCount, badgeColor: 'orange' },
      { title: 'Data Teknis', icon: 'mdi-database-cog-outline', value: 'teknis', to: '/data-teknis' },
      { title: 'Brand & Paket', icon: 'mdi-tag-multiple-outline', value: 'harga', to: '/harga-layanan' },
  ]},
  { title: 'BILLING', items: [{ title: 'Invoices', icon: 'mdi-file-document-outline', value: 'invoices', to: '/invoices', badge: 0, badgeColor: 'grey-darken-1' }] },
  { title: 'NETWORK MANAGEMENT', items: [{ title: 'Mikrotik Servers', icon: 'mdi-server', value: 'mikrotik', to: '/mikrotik' }] },
  { title: 'MANAGEMENT', items: [
     { title: 'Users', icon: 'mdi-account-cog-outline', value: 'users', to: '/users', badge: 0, badgeColor: 'primary' },
      { title: 'Roles', icon: 'mdi-shield-account-outline', value: 'roles', to: '/roles', badge: 0, badgeColor: 'primary' }]},
      

]);

async function fetchSuspendedCount() {
  try {
    // Gunakan filter status yang sudah dibuat di backend
    const response = await apiClient.get('/langganan?status=Ditangguhkan');
    suspendedCount.value = response.data.length;
  } catch (error) {
    console.error("Gagal mengambil jumlah langganan yang ditangguhkan:", error);
    suspendedCount.value = 0;
  }
}


async function fetchRoleCount() {
  try {
    const response = await apiClient.get('/roles/');
    const roleCount = response.data.length; // Hitung jumlah data

    // Cari grup 'MANAGEMENT' dan item 'Roles' untuk memperbarui badge
    const managementGroup = menuGroups.value.find(g => g.title === 'MANAGEMENT');
    if (managementGroup) {
      const rolesItem = managementGroup.items.find(i => i.value === 'roles');
      if (rolesItem) {
        rolesItem.badge = roleCount;
      }
    }
  } catch (error) {
    console.error("Gagal mengambil jumlah roles:", error);
    // Jika gagal, badge tidak akan ditampilkan atau tetap 0
  }
}

async function fetchUserCount() {
  try {
    const response = await apiClient.get('/users/');
    const userCount = response.data.length;

    const managementGroup = menuGroups.value.find(g => g.title === 'MANAGEMENT');
    if (managementGroup) {
      const usersItem = managementGroup.items.find(i => i.value === 'users');
      if (usersItem) {
        usersItem.badge = userCount;
      }
    }
  } catch (error) {
    console.error("Gagal mengambil jumlah users:", error);
  }
}

onMounted(() => {
  const savedTheme = localStorage.getItem('theme');
  if (savedTheme && (savedTheme === 'light' || savedTheme === 'dark')) {
    theme.global.name.value = savedTheme;
  }
  fetchRoleCount();
  fetchUserCount();
  fetchSuspendedCount(); // Panggil fungsi baru di sini
  setupWebSocket();
});

onMounted(() => {
  const savedTheme = localStorage.getItem('theme');
  if (savedTheme && (savedTheme === 'light' || savedTheme === 'dark')) {
    theme.global.name.value = savedTheme;
  }
  // Panggil fungsi untuk mengambil data saat komponen dimuat
  fetchRoleCount();
});


function handleLogout() {
  localStorage.removeItem('access_token');
  router.push('/login');
}
</script>

<style scoped>
/* LIGHT THEME */
.modern-app {
  background-color: rgb(var(--v-theme-background));
  transition: background-color 0.3s ease;
}

.modern-drawer {
  border-right: none;
  background: rgb(var(--v-theme-surface));
  box-shadow: 0 0 20px rgba(0, 0, 0, 0.08);
  overflow: hidden !important;
  transition: all 0.3s ease;
}

.modern-drawer :deep(.v-navigation-drawer__content) {
  overflow: hidden !important;
  display: flex;
  flex-direction: column;
  height: 100%;
}

.sidebar-header {
  height: 75px;
  padding: 0 16px !important;
  border-bottom: 1px solid rgba(var(--v-border-color), var(--v-border-opacity));
  flex-shrink: 0;
  transition: border-color 0.3s ease;
}

.header-flex-container {
  display: flex;
  align-items: center;
  width: 100%;
}

.sidebar-logo-full {
  height: 45px;
  margin-right: 12px;
  flex-shrink: 0;
  filter: brightness(1);
  transition: filter 0.3s ease;
}

/* Dark mode logo adjustment */
.v-theme--dark .sidebar-logo-full {
  filter: brightness(1.2) contrast(1.1);
}

.sidebar-title-wrapper {
  overflow: hidden;
  white-space: nowrap;
}

.sidebar-title {
  font-size: 1.3rem;
  font-weight: 700;
  color: rgb(var(--v-theme-on-surface));
  line-height: 1.2;
  margin-bottom: 2px;
  transition: color 0.3s ease;
}

.sidebar-subtitle {
  font-size: 0.75rem;
  font-weight: 500;
  color: rgba(var(--v-theme-on-surface), 0.7);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  transition: color 0.3s ease;
}

.navigation-wrapper {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  padding: 8px 0;
  scrollbar-width: none;
  -ms-overflow-style: none;
}

.navigation-wrapper::-webkit-scrollbar {
  display: none;
}

.navigation-menu {
  padding: 0 16px;
}

.menu-subheader {
  font-size: 0.7rem;
  font-weight: 700;
  color: rgba(var(--v-theme-on-surface), 0.6) !important;
  text-transform: uppercase;
  letter-spacing: 0.8px;
  margin-top: 20px;
  margin-bottom: 8px;
  padding: 0 16px;
  transition: color 0.3s ease;
}

.nav-item {
  border-radius: 10px;
  margin-bottom: 4px;
  color: rgba(var(--v-theme-on-surface), 0.8);
  min-height: 44px;
  transition: all 0.3s ease;
}

.nav-item .v-list-item-title {
  font-size: 0.9rem;
  font-weight: 500;
}

.nav-item:not(.v-list-item--active):hover {
  background-color: rgba(var(--v-theme-primary), 0.1);
  color: rgb(var(--v-theme-primary));
  transform: translateX(2px);
}

.v-list-item--active {
  background: linear-gradient(135deg, rgb(var(--v-theme-primary)) 0%, rgb(var(--v-theme-secondary)) 100%);
  color: white !important;
  box-shadow: 0 4px 12px rgba(var(--v-theme-primary), 0.3);
}

.v-list-item--active .v-list-item-title {
  font-weight: 600;
}

.badge-chip {
  font-size: 0.7rem;
  height: 20px;
  font-weight: 600;
  border-radius: 10px;
  /* Hapus 'color: white;' dari sini agar warna default Vuetify berlaku */
}

/* Tambahkan aturan baru ini */
.v-list-item--active .badge-chip {
  color: white !important; /* Jadikan warna teks putih HANYA saat item aktif */
}

.logout-section {
  flex-shrink: 0;
  border-top: 1px solid rgba(var(--v-border-color), var(--v-border-opacity));
  background: rgba(var(--v-theme-surface), 0.5);
  transition: all 0.3s ease;
}

.logout-btn {
  border-radius: 10px;
  font-weight: 500;
  text-transform: none;
  letter-spacing: normal;
  transition: all 0.3s ease;
}

.logout-btn:hover {
  background-color: #ef4444 !important;
  color: white !important;
}

.modern-app-bar {
  background: rgb(var(--v-theme-surface)) !important;
  border-bottom: 1px solid rgba(var(--v-border-color), var(--v-border-opacity));
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
}

.header-action-btn {
  color: rgba(var(--v-theme-on-surface), 0.8);
  transition: all 0.3s ease;
}

.header-action-btn:hover {
  background-color: rgba(var(--v-theme-primary), 0.1);
  color: rgb(var(--v-theme-primary));
}

.theme-toggle-btn:hover {
  background-color: rgba(var(--v-theme-warning), 0.1) !important;
  color: rgb(var(--v-theme-warning)) !important;
}

.modern-main {
  background-color: rgb(var(--v-theme-background));
  transition: background-color 0.3s ease;
}

/* DARK THEME SPECIFIC STYLES */
.v-theme--dark .modern-app {
  background-color: #0f172a;
}

.v-theme--dark .modern-drawer {
  background: #1e293b;
  box-shadow: 0 0 20px rgba(0, 0, 0, 0.3);
}

.v-theme--dark .sidebar-header {
  border-bottom: 1px solid #334155;
}

.v-theme--dark .modern-app-bar {
  background: #1e293b !important;
  border-bottom: 1px solid #334155;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
}

.v-theme--dark .logout-section {
  background: #0f1629;
  border-top: 1px solid #334155;
}

.v-theme--dark .nav-item:not(.v-list-item--active):hover {
  background-color: rgba(129, 140, 248, 0.15);
}

/* Mobile responsiveness */
@media (max-width: 768px) {
  .modern-drawer {
    width: 260px !important;
  }
  
  .sidebar-title {
    font-size: 1.1rem;
  }
  
  .nav-item {
    min-height: 48px;
  }
  
  .nav-item .v-list-item-title {
    font-size: 0.95rem;
  }
}

@media (max-width: 480px) {
  .modern-drawer {
    width: 240px !important;
  }
}
</style>