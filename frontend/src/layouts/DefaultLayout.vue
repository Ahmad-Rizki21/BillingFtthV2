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
                <v-chip size="small" class="badge-chip" :color="item.badgeColor">
                  {{ item.badge }}
                </v-chip>
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
      
      <v-btn icon variant="text" class="header-action-btn">
        <v-icon>mdi-bell-outline</v-icon>
      </v-btn>
      <v-btn icon variant="text" class="header-action-btn">
        <v-icon>mdi-cog-outline</v-icon>
      </v-btn>
  </v-app-bar>

    <v-main class="modern-main">
  <router-view></router-view>
</v-main>
  </v-app>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router';
import { ref, onMounted } from 'vue';
import logoJelantik from '@/assets/images/Jelantik.webp';
import { useTheme } from 'vuetify';

const theme = useTheme();
const drawer = ref(true);
const rail = ref(false);
const router = useRouter();

// SOLUSI YANG BENAR: Gunakan metode yang tidak deprecated
function toggleTheme() {
  const newTheme = theme.global.current.value.dark ? 'light' : 'dark';
  theme.global.name.value = newTheme;
  localStorage.setItem('theme', newTheme);
}

// Saat komponen pertama kali dimuat, cek localStorage
onMounted(() => {
  const savedTheme = localStorage.getItem('theme');
  if (savedTheme && (savedTheme === 'light' || savedTheme === 'dark')) {
    theme.global.name.value = savedTheme;
  }
});

const menuGroups = ref([
  { title: 'DASHBOARD', items: [{ title: 'Dashboard', icon: 'mdi-home-variant', value: 'dashboard', to: '/dashboard' }] },
  { title: 'FTTH', items: [
      { title: 'Data Pelanggan', icon: 'mdi-account-group-outline', value: 'pelanggan', to: '/pelanggan' },
      { title: 'Langganan / Paket', icon: 'mdi-wifi', value: 'paket', to: '/paket', badge: 1, badgeColor: 'orange' },
      { title: 'Data Teknis', icon: 'mdi-database-cog-outline', value: 'teknis', to: '/teknis' },
      { title: 'Harga Layanan', icon: 'mdi-cash', value: 'harga', to: '/harga' },
  ]},
  { title: 'BILLING', items: [{ title: 'Invoices', icon: 'mdi-file-document-outline', value: 'invoices', to: '/invoices', badge: 0, badgeColor: 'grey-darken-1' }] },
  { title: 'SETTINGS', items: [
      { title: 'Logs System', icon: 'mdi-math-log', value: 'logs', to: '/logs' },
      { title: 'Activity Log', icon: 'mdi-timeline-text-outline', value: 'activity', to: '/activity' },
  ]},
  { title: 'NETWORK MANAGEMENT', items: [{ title: 'Mikrotik Servers', icon: 'mdi-server', value: 'mikrotik', to: '/mikrotik' }] },
  { title: 'MANAGEMENT', items: [{ title: 'Users', icon: 'mdi-account-cog-outline', value: 'users', to: '/users' }] },
  { title: 'FILAMENT SHIELD', items: [{ title: 'Roles', icon: 'mdi-shield-account-outline', value: 'roles', to: '/roles', badge: 3, badgeColor: 'primary' }] },
]);

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
  color: white;
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