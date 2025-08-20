<template>
  <v-app class="modern-app">
    <v-navigation-drawer
      v-model="drawer"
      :rail="rail && !isMobile"
      :temporary="isMobile"
      :permanent="!isMobile"
      class="modern-drawer"
      :width="isMobile ? '280' : '280'"
    >
      <v-list-item class="sidebar-header" :class="{'px-0': rail && !isMobile}" :ripple="false">
        <div class="header-flex-container">
          <img v-if="!rail || isMobile" :src="logoSrc" alt="Jelantik Logo" class="sidebar-logo-full"/>
          
          <v-icon v-if="rail && !isMobile" color="primary" size="large">mdi-alpha-j</v-icon>

          <div v-if="!rail || isMobile" class="sidebar-title-wrapper">
            <h1 class="sidebar-title">Artacom Ftth</h1>
            <span class="sidebar-subtitle">BILLING SYSTEM V2.0</span>
          </div>

          <v-spacer v-if="!rail || isMobile"></v-spacer>

          <v-btn
            v-if="!isMobile"
            icon="mdi-chevron-left"
            variant="text"
            size="small"
            @click.stop="rail = !rail"
          ></v-btn>
          
          <v-btn
            v-if="isMobile"
            icon="mdi-close"
            variant="text"
            size="small"
            @click.stop="drawer = false"
          ></v-btn>
        </div>
      </v-list-item>

      <v-divider></v-divider>

      <div class="navigation-wrapper">
        <v-list nav class="navigation-menu">
          <template v-for="group in filteredMenuGroups" :key="group.title">
            <v-list-subheader v-if="!rail || isMobile" class="menu-subheader">{{ group.title }}</v-list-subheader>
            <v-list-item
                v-for="item in group.items"
                :key="item.title"
                :prepend-icon="item.icon"
                :title="item.title"
                :value="item.value"
                :to="item.to"
                class="nav-item"
              >
                <template v-slot:append>
                  <v-tooltip location="end">
                    <template v-slot:activator="{ props }">
                      <v-badge
                        v-if="item.value === 'langganan' && suspendedCount > 0"
                        color="error"
                        :content="suspendedCount"
                        inline
                        v-bind="props"
                      ></v-badge>
                    </template>
                    <span>{{ suspendedCount }} langganan berstatus "Suspended"</span>
                  </v-tooltip>

                  <v-tooltip location="end">
                    <template v-slot:activator="{ props }">
                      <v-badge
                        v-if="item.value === 'langganan' && stoppedCount > 0"
                        :content="stoppedCount"
                        inline
                        v-bind="props"
                        class="ml-2"
                      ></v-badge>
                    </template>
                    <span>{{ stoppedCount }} langganan telah berhenti</span>
                  </v-tooltip>
                  
                  <v-tooltip location="end">
                    <template v-slot:activator="{ props }">
                      <v-badge
                        v-if="item.value === 'invoices' && unpaidInvoiceCount > 0"
                        color="warning"
                        :content="unpaidInvoiceCount"
                        inline
                        v-bind="props"
                      ></v-badge>
                    </template>
                    <span>{{ unpaidInvoiceCount }} invoice belum dibayar</span>
                  </v-tooltip>
                </template>
              </v-list-item>
          </template>
        </v-list>
      </div>

      <template v-slot:append>
        <div class="logout-section pa-4">
          <v-btn
            :block="!rail || isMobile"
            variant="tonal"
            color="grey-darken-1"
            class="logout-btn"
            :icon="rail && !isMobile"
            @click="handleLogout"
          >
            <v-icon v-if="rail && !isMobile">mdi-logout</v-icon>
            <span v-if="!rail || isMobile" class="d-flex align-center"><v-icon left>mdi-logout</v-icon>Logout</span>
          </v-btn>
        </div>
      </template>
    </v-navigation-drawer>

    <v-app-bar elevation="0" class="modern-app-bar">
      <v-btn
        icon="mdi-menu"
        variant="text"
        @click.stop="toggleDrawer"
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
        <v-list class="pa-0" :width="isMobile ? '90vw' : '300'">
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
            class="py-2 notification-item"  :to="getNotificationLink(notif)"
          >
            <template v-slot:prepend>
              <v-avatar :color="getNotificationColor(notif.type)" size="32" class="me-3">
                  <v-icon size="18">{{ getNotificationIcon(notif.type) }}</v-icon>
              </v-avatar>
            </template>

            <div v-if="notif.type === 'new_payment'">
              <v-list-item-title class="font-weight-medium text-body-2">Pembayaran Diterima</v-list-item-title>
              <v-list-item-subtitle class="text-caption">
                <strong>{{ notif.data.invoice_number }}</strong> dari <strong>{{ notif.data.pelanggan_nama }}</strong> telah lunas.
              </v-list-item-subtitle>
            </div>

            <div v-if="notif.type === 'new_customer_for_noc'">
              <v-list-item-title class="font-weight-medium text-body-2">Pelanggan Baru</v-list-item-title>
              <v-list-item-subtitle class="text-caption">
                <strong>{{ notif.data.pelanggan_nama }}</strong> perlu dibuatkan Data Teknis.
              </v-list-item-subtitle>
            </div>

          </v-list-item>
          </v-list>
      </v-menu>
    </v-app-bar>

    <v-main class="modern-main">
      <router-view></router-view>
    </v-main>
    
    <v-footer app height="69px" class="d-flex align-center justify-center text-medium-emphasis footer-responsive" style="border-top: 1px solid rgba(0,0,0,0.08);">
      <div class="footer-content">
        &copy; {{ new Date().getFullYear() }} <strong>Artacom Billing System</strong>. All Rights Design Reserved by 
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
import { ref, onMounted, onUnmounted, computed } from 'vue';
import logoLight from '@/assets/images/Jelantik-Light.webp';
import logoDark from '@/assets/images/Jelantik-Dark.webp';
import { useTheme } from 'vuetify';
import { useDisplay } from 'vuetify';
import apiClient from '@/services/api';
import { useAuthStore } from '@/stores/auth';

// --- State ---
const theme = useTheme();
const { mobile } = useDisplay();
const drawer = ref(true);
const rail = ref(false);
const router = useRouter();
const notifications = ref<any[]>([]);
const suspendedCount = ref(0);
const unpaidInvoiceCount = ref(0);
const stoppedCount = ref(0);
const userCount = ref(0);
const roleCount = ref(0);
const userPermissions = ref<string[]>([]);
const authStore = useAuthStore();
let socket: WebSocket | null = null;
let reconnectInterval: NodeJS.Timeout | null = null;

// Computed untuk mobile detection
const isMobile = computed(() => mobile.value);

// Toggle drawer function untuk mobile/desktop
function toggleDrawer() {
  if (isMobile.value) {
    drawer.value = !drawer.value;
  } else {
    rail.value = !rail.value;
  }
}

async function fetchSidebarBadges() {
  try {
    const response = await apiClient.get('/dashboard/sidebar-badges');
    suspendedCount.value = response.data.suspended_count;
    unpaidInvoiceCount.value = response.data.unpaid_invoice_count;
    stoppedCount.value = response.data.stopped_count; // <-- Ambil data baru
  } catch (error) {
    console.error("Gagal mengambil data badge sidebar:", error);
  }
}

// --- Fungsi WebSocket yang Diperbaiki ---
function connectWebSocket() {
  if (!authStore.token) return;
  if (socket && socket.readyState === WebSocket.OPEN) return;

  // Untuk development (localhost)
  if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
    const wsUrl = `ws://127.0.0.1:8000/ws/notifications?token=${authStore.token}`;
    console.log(`Connecting to WebSocket at ${wsUrl}`);
    socket = new WebSocket(wsUrl);
  } else {
    // Untuk production - gunakan wss dengan domain yang sama
    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${wsProtocol}//${window.location.host}/ws/notifications?token=${authStore.token}`;
    console.log(`Connecting to WebSocket at ${wsUrl}`);
    socket = new WebSocket(wsUrl);
  }

  socket.onopen = () => {
    console.log('WebSocket connection established.');
    // Clear reconnect interval jika berhasil
    if (reconnectInterval) {
      clearInterval(reconnectInterval);
      reconnectInterval = null;
    }
  };

  function playSound(type: string) {
  let audioFile = '';

  if (type === 'new_payment') {
    audioFile = '/pembayaran.mp3'; // Suara baru untuk pembayaran
  } else if (type === 'new_customer_for_noc') {
    audioFile = '/payment.mp3'; // Suara lama untuk pelanggan baru
  }

  if (audioFile) {
    const audio = new Audio(audioFile);
    audio.play().catch(error => {
      console.error(`Gagal memutar audio (${audioFile}):`, error);
    });
  }
}

  socket.onmessage = (event) => {
    console.log('WebSocket message received:', event.data);
    try {
      const data = JSON.parse(event.data);
      
      if (data.type === 'new_payment' || data.type === 'new_customer_for_noc') {
        notifications.value.unshift(data);
        
        // ===== TAMBAHKAN BARIS INI =====
        playSound(data.type);
        // ===============================

        if (notifications.value.length > 50) {
          notifications.value = notifications.value.slice(0, 50);
        }
      }
    } catch (error) {
      console.error('Error parsing WebSocket message:', error);
    }
  };

  socket.onerror = (error) => {
    console.error('WebSocket error:', error);
  };

  socket.onclose = (event) => {
    console.log('WebSocket closed:', event.code, event.reason);
    
    // Hanya reconnect jika user masih authenticated dan bukan intentional close
    if (authStore.isAuthenticated && event.code !== 1000) {
      console.log('WebSocket closed unexpectedly. Attempting to reconnect...');
      if (!reconnectInterval) {
        reconnectInterval = setInterval(() => {
          if (authStore.isAuthenticated) {
            connectWebSocket();
          } else {
            disconnectWebSocket();
          }
        }, 5000);
      }
    }
  };
}

function disconnectWebSocket() {
  if (reconnectInterval) clearInterval(reconnectInterval);
  reconnectInterval = null;
  if (socket) {
    socket.onclose = null; 
    socket.close();
    socket = null;
    console.log('WebSocket connection intentionally disconnected.');
  }
}
// --- AKHIR BLOK KODE WEBSOCKET ---


const menuGroups = ref([
  { title: 'DASHBOARD', items: [{ title: 'Dashboard', icon: 'mdi-home-variant', value: 'dashboard', to: '/dashboard', permission: 'view_dashboard' }] },
  { title: 'FTTH', items: [
      { title: 'Data Pelanggan', icon: 'mdi-account-group-outline', value: 'pelanggan', to: '/pelanggan', permission: 'view_pelanggan' },
      { title: 'Langganan', icon: 'mdi-wifi-star', value: 'langganan', to: '/langganan', badge: suspendedCount, badgeColor: 'orange', permission: 'view_langganan' },
      { title: 'Data Teknis', icon: 'mdi-database-cog-outline', value: 'teknis', to: '/data-teknis', permission: 'view_data_teknis' },
      { title: 'Brand & Paket', icon: 'mdi-tag-multiple-outline', value: 'harga', to: '/harga-layanan', permission: 'view_brand_&_paket' },
  ]},
  { title: 'LAINNYA', items: [
    { title: 'Simulasi Harga', icon: 'mdi-calculator', value: 'kalkulator', to: '/kalkulator', permission: 'view_simulasi_harga' },
    { title: 'S&K', icon: 'mdi-file-document-outline', value: 'sk', to: '/syarat-ketentuan', permission: null } // <-- Tambahkan ini
  ]},
  { title: 'BILLING', items: [{ title: 'Invoices', icon: 'mdi-file-document-outline', value: 'invoices', to: '/invoices', badge: 0, badgeColor: 'grey-darken-1', permission: 'view_invoices' }] },
  { title: 'NETWORK MANAGEMENT', items: [{ title: 'Mikrotik Servers', icon: 'mdi-server', value: 'mikrotik', to: '/mikrotik', permission: 'view_mikrotik_servers' }] },
  { title: 'MANAGEMENT', items: [
      { title: 'Users', icon: 'mdi-account-cog-outline', value: 'users', to: '/users', badge: userCount, badgeColor: 'primary', permission: 'view_users' },
      { title: 'Roles', icon: 'mdi-shield-account-outline', value: 'roles', to: '/roles', badge: roleCount, badgeColor: 'primary', permission: 'view_roles' },
      { title: 'Permissions', icon: 'mdi-shield-key-outline', value: 'permissions', to: '/permissions', permission: 'view_permissions' },
      { title: 'Kelola S&K', icon: 'mdi-file-edit-outline', value: 'sk-management', to: '/management/sk', permission: 'manage_sk' }
  ]},
]);

const filteredMenuGroups = computed(() => {
  if (userPermissions.value.includes('*')) return menuGroups.value;
  return menuGroups.value.map(group => ({
    ...group,
    items: group.items.filter(item => !item.permission || userPermissions.value.includes(item.permission)),
  })).filter(group => group.items.length > 0);
});

const logoSrc = computed(() => theme.global.current.value.dark ? logoDark : logoLight);

onMounted(async () => {
  const savedTheme = localStorage.getItem('theme');
  if (savedTheme) theme.global.name.value = savedTheme;

  // Set drawer behavior based on screen size
  if (isMobile.value) {
    drawer.value = false;
    rail.value = false;
  }

  const enableAudioContext = () => {
    // Fungsi ini akan dijalankan sekali saat user mengklik
    // dan setelah itu listener-nya akan dihapus.
    console.log('User interaction detected. Audio playback is now enabled for this session.');
    document.removeEventListener('click', enableAudioContext);
  };
  document.addEventListener('click', enableAudioContext);
  
  const userIsValid = await authStore.verifyToken();
  if (userIsValid && authStore.user?.role) {
    const role = authStore.user.role;
    if (typeof role === 'object' && role !== null && role.name) {
      if (role.name.toLowerCase() === 'admin') userPermissions.value = ['*'];
      else userPermissions.value = role.permissions?.map((p: any) => p.name) || [];
    } else if (typeof role === 'string') {
      if (role.toLowerCase() === 'admin') userPermissions.value = ['*'];
    }
    fetchRoleCount();
    fetchUserCount();
    // fetchSuspendedCount();
    fetchSidebarBadges();
    connectWebSocket(); // Memulai WebSocket setelah user terverifikasi
  }
});

onUnmounted(() => disconnectWebSocket());

function toggleTheme() {
  const newTheme = theme.global.current.value.dark ? 'light' : 'dark';
  theme.global.name.value = newTheme;
  localStorage.setItem('theme', newTheme);
}

function getNotificationIcon(type: string) {
  switch (type) {
    case 'new_payment': return 'mdi-cash-check';
    case 'new_customer_for_noc': return 'mdi-account-plus-outline';
    default: return 'mdi-bell-outline';
  }
}

function getNotificationColor(type: string) {
  switch (type) {
    case 'new_payment': return 'success';
    case 'new_customer_for_noc': return 'info';
    default: return 'grey';
  }
}

function getNotificationLink(notification: any) {
  if (notification.type === 'new_customer_for_noc') {
    return '/data-teknis';
  }
  return undefined;
}

// async function fetchSuspendedCount() {
//   try {
//     const response = await apiClient.get('/langganan?status=Ditangguhkan');
//     suspendedCount.value = response.data.length;
//   } catch (error) {
//     console.error("Gagal mengambil jumlah langganan yang ditangguhkan:", error);
//   }
// }

async function fetchRoleCount() {
  try {
    const response = await apiClient.get('/roles/');
    roleCount.value = response.data.length;
  } catch (error) {
    console.error("Gagal mengambil jumlah roles:", error);
  }
}

async function fetchUserCount() {
  try {
    const response = await apiClient.get('/users/');
    userCount.value = response.data.length;
  } catch (error) {
    console.error("Gagal mengambil jumlah users:", error);
  }
}

function handleLogout() {
  disconnectWebSocket();
  authStore.logout();
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

.notification-item .v-list-item-subtitle {
  white-space: normal !important;      /* Izinkan teks untuk wrap ke baris baru */
  line-height: 1.4;                  /* Perbaiki jarak antar baris agar mudah dibaca */
  -webkit-line-clamp: 2; 
  line-clamp: 2;              /* Batasi teks hingga 2 baris */
  -webkit-box-orient: vertical;
  display: -webkit-box;
  overflow: hidden;
  text-overflow: ellipsis;
}

.notification-item.v-list-item {
  min-height: 60px !important;         /* Beri tinggi minimal untuk menampung 2 baris */
  height: auto !important;             /* Biarkan tinggi item menyesuaikan konten */
  align-items: center;               /* Posisikan avatar dan teks di tengah */
}

.sidebar-header {
  height: 65px;
  padding: 0 11.5px !important;
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
  flex: 2;
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

/* Footer responsive */
.footer-responsive {
  padding: 0 1rem;
}

.footer-content {
  text-align: center;
  font-size: 0.85rem;
  line-height: 1.4;
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
    width: 280px !important;
  }
  
  .sidebar-title {
    font-size: 1.15rem;
  }
  
  .sidebar-subtitle {
    font-size: 0.7rem;
  }
  
  .nav-item {
    min-height: 48px;
  }
  
  .nav-item .v-list-item-title {
    font-size: 0.9rem;
  }
  
  .menu-subheader {
    font-size: 0.68rem;
  }
  
  .footer-content {
    font-size: 0.8rem;
  }
}

@media (max-width: 480px) {
  .modern-drawer {
    width: 260px !important;
  }
  
  .sidebar-logo-full {
    height: 40px;
  }
  
  .sidebar-title {
    font-size: 1.1rem;
  }
  
  .sidebar-subtitle {
    font-size: 0.65rem;
  }
  
  .nav-item .v-list-item-title {
    font-size: 0.85rem;
  }
  
  .menu-subheader {
    font-size: 0.65rem;
  }
  
  .footer-content {
    font-size: 0.75rem;
    padding: 0.5rem 0;
  }
}

@media (max-width: 360px) {
  .modern-drawer {
    width: 240px !important;
  }
  
  .sidebar-logo-full {
    height: 35px;
  }
  
  .sidebar-title {
    font-size: 1rem;
  }
  
  .sidebar-subtitle {
    font-size: 0.6rem;
  }
  
  .nav-item .v-list-item-title {
    font-size: 0.8rem;
  }
  
  .footer-content {
    font-size: 0.7rem;
  }
}
</style>