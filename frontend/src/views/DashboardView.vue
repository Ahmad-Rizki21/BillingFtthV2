<template>
  <div class="dashboard-container pa-6">
    <div class="dashboard-header">
      <h1 class="dashboard-title">Dashboard</h1>
      <p class="dashboard-subtitle">Monitor your billing system performance</p>
    </div>

    <div class="dashboard-grid grid-3 mb-8">
    <v-card v-for="stat in stats" :key="stat.title" class="dashboard-widget">
      <div class="widget-content">
        <div class="d-flex align-center justify-space-between">
          <div>
            <p class="widget-title">{{ stat.title }}</p>
            <h2 class="widget-value">{{ stat.value }}</h2>
            <p class="widget-description">{{ stat.description }}</p>
          </div>
          <v-icon :color="stat.color" size="48">{{ stat.icon }}</v-icon>
        </div>
      </div>
    </v-card>
</div>

    <div class="dashboard-grid grid-2">
      <v-card class="chart-widget">
        <h3 class="chart-title">Pelanggan per Lokasi</h3>
        <div class="chart-container">
            <Chart type="bar" :data="lokasiChartData" :options="chartOptions" />
        </div>
      </v-card>

      <v-card class="chart-widget">
        <h3 class="chart-title">Pelanggan per Paket</h3>
        <div class="chart-container">
            <Chart type="bar" :data="paketChartData" :options="chartOptions" />
        </div>
      </v-card>
    </div>

    <v-card class="chart-widget mt-8">
      <h3 class="chart-title">Invoice Bulanan</h3>
      <div class="chart-container" style="height: 350px;">
          <Chart type="bar" :data="invoiceChartData" :options="invoiceChartOptions" />
      </div>
    </v-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { Chart } from 'vue-chartjs';
import {
  Chart as ChartJS, Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale, PointElement, LineElement, ChartData
} from 'chart.js';
import { useTheme } from 'vuetify';

// 1. Registrasi semua elemen Chart.js yang dibutuhkan
ChartJS.register(Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale, PointElement, LineElement);

const theme = useTheme();

// 2. Data dummy untuk kartu statistik
const stats = ref([
    { title: 'Jumlah Pelanggan Jakinet', value: 0, description: 'Total Pelanggan Jakinet', icon: 'mdi-account-network', color: 'primary' },
    { title: 'Jumlah Pelanggan Jelantik', value: 75, description: 'Total Pelanggan Jelantik', icon: 'mdi-account-group', color: 'success' },
    { title: 'Pelanggan Jelantik Nagrak', value: 0, description: 'Total Pelanggan Rusun Nagrak', icon: 'mdi-home-group', color: 'warning' },
    { title: 'Total Servers', value: 3, description: 'Total Mikrotik servers', icon: 'mdi-server', color: 'info' },
    { title: 'Online Servers', value: 3, description: 'Servers currently online', icon: 'mdi-server-network', color: 'success' },
    { title: 'Offline Servers', value: 0, description: 'Servers currently offline', icon: 'mdi-server-off', color: 'error' },
]);

// 3. Konfigurasi dan data untuk semua chart
const chartAxisColor = computed(() => theme.global.current.value.dark ? 'rgba(255, 255, 255, 0.6)' : 'rgba(0, 0, 0, 0.6)');
const chartGridColor = computed(() => theme.global.current.value.dark ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)');

const chartOptions = computed(() => ({
  responsive: true,
  maintainAspectRatio: false,
  plugins: { legend: { display: false } },
  scales: {
    y: { beginAtZero: true, grid: { color: chartGridColor.value }, ticks: { color: chartAxisColor.value } },
    x: { grid: { display: false }, ticks: { color: chartAxisColor.value } },
  },
}));

const invoiceChartOptions = computed(() => ({
  responsive: true,
  maintainAspectRatio: false,
  plugins: { legend: { position: 'top' as const, labels: { color: chartAxisColor.value } } },
  scales: {
    y: { stacked: true, beginAtZero: true, grid: { color: chartGridColor.value }, ticks: { color: chartAxisColor.value } },
    x: { stacked: true, grid: { display: false }, ticks: { color: chartAxisColor.value } },
  },
}));

const lokasiChartData = ref<ChartData<'bar'>>({
  labels: ['Rusun Nagrak', 'Luar Pinus Elok', 'Rusunawa', 'Perumahan Tambun', 'Warung Kuning'],
  datasets: [{
    label: 'Jumlah Pelanggan', data: [7, 2, 5, 71, 2], backgroundColor: '#818cf8', borderRadius: 4,
  }],
});

const paketChartData = ref<ChartData<'bar'>>({
  labels: ['10 Mbps', '20 Mbps', '30 Mbps', '50 Mbps'],
  datasets: [{
    label: 'Jumlah Pelanggan', data: [56, 14, 2, 1], backgroundColor: ['#818cf8', '#34d399', '#fbbf24', '#f87171'], borderRadius: 4,
  }],
});

const invoiceChartData = ref({
  labels: ['Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun', 'Jul'],
  datasets: [
    {
      type: 'line' as const,
      label: 'Total Invoice',
      data: [22, 25, 27, 22, 32, 29, 32],
      borderColor: '#a78bfa',
      backgroundColor: '#a78bfa',
      tension: 0.4,
      yAxisID: 'y',
    },
    {
      type: 'bar' as const,
      label: 'Lunas',
      data: [15, 20, 22, 18, 25, 23, 28],
      backgroundColor: 'rgba(52, 211, 153, 0.8)',
      stack: 'Stack 0',
    },
    {
      type: 'bar' as const,
      label: 'Menunggu',
      data: [5, 4, 2, 3, 5, 6, 4],
      backgroundColor: 'rgba(251, 191, 36, 0.8)',
      stack: 'Stack 0',
    },
    {
      type: 'bar' as const,
      label: 'Kadaluarsa',
      data: [2, 1, 3, 1, 2, 1, 0],
      backgroundColor: 'rgba(248, 113, 113, 0.8)',
      stack: 'Stack 0',
    },
  ],
});
</script>

<style scoped>
.dashboard-container {
  animation: fadeIn 0.5s ease-out;
}
.page-title {
  color: rgb(var(--v-theme-on-background));
  font-weight: 800;
  font-size: 1.8rem;
}
.page-subtitle {
  color: rgba(var(--v-theme-on-surface), 0.7);
  font-size: 1rem;
  margin-bottom: 24px;
}
.dashboard-grid {
  display: grid;
  gap: 24px;
}
.grid-3 {
  grid-template-columns: repeat(3, 1fr);
}
.grid-2 {
  grid-template-columns: repeat(2, 1fr);
}

/* KUNCI UTAMA: Styling untuk kartu agar tidak tumpang tindih */
.dashboard-widget,
.chart-widget {
  background-color: rgb(var(--v-theme-surface));
  border: 1px solid rgba(var(--v-border-color), var(--v-border-opacity));
  border-radius: 16px;
  box-shadow: none;
  transition: all 0.2s ease-in-out;
}
.dashboard-widget:hover,
.chart-widget:hover {
  transform: translateY(-4px);
  border-color: rgb(var(--v-theme-primary));
}

/* Penyesuaian untuk struktur kartu yang Anda inginkan */
.widget-content {
  padding: 24px;
}
.widget-title {
  font-size: 0.85rem;
  color: rgba(var(--v-theme-on-surface), 0.7);
  margin-bottom: 4px;
}
.widget-value {
  font-size: 2.2rem;
  font-weight: 700;
  color: rgb(var(--v-theme-on-surface));
  line-height: 1;
}
.widget-description {
  font-size: 0.8rem;
  margin-top: 4px;
  color: rgba(var(--v-theme-on-surface), 0.6);
}

/* Styling untuk Chart */
.chart-widget {
  padding: 24px;
}
.chart-title {
  font-size: 1.2rem;
  font-weight: 600;
  color: rgb(var(--v-theme-on-surface));
  margin-bottom: 16px;
}
.chart-container {
  height: 300px;
  position: relative;
}

/* Responsif */
@media (max-width: 960px) {
  .grid-3, .grid-2 {
    grid-template-columns: 1fr 1fr;
  }
}
@media (max-width: 600px) {
  .grid-3, .grid-2 {
    grid-template-columns: 1fr;
  }
}
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}
</style>