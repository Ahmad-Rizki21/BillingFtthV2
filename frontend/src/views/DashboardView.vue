<template>
  <div class="dashboard-container">
    <div class="dashboard-header">
      <h1 class="dashboard-title">Dashboard</h1>
      <p class="dashboard-subtitle">Monitor your billing system performance</p>
    </div>

    <div class="stats-grid">
      <div v-for="stat in stats" :key="stat.title" class="stat-card">
        <div class="stat-card-content">
          <p class="stat-title">{{ stat.title }}</p>
          <h3 class="stat-number">{{ stat.value }}</h3>
          <div class="stat-footer">
            <v-icon :color="stat.color" size="16">{{ stat.icon }}</v-icon>
            <span class="stat-subtitle">{{ stat.subtitle }}</span>
          </div>
        </div>
        <div class="stat-border" :style="{ background: stat.color }"></div>
      </div>
    </div>

    <div class="charts-section">
      <div class="charts-row">
        <div class="chart-container">
          <div class="chart-card">
            <div class="chart-header">
              <h3 class="chart-title">Pelanggan per Lokasi</h3>
              <div class="chart-legend">
                <span class="legend-item">
                  <div class="legend-dot" style="background: #6366f1"></div>
                  Jumlah Pelanggan
                </span>
              </div>
            </div>
            <div class="chart-content">
              <Chart type="bar" :data="lokasiChartData" :options="chartOptions" />
            </div>
          </div>
        </div>
        
        <div class="chart-container">
          <div class="chart-card">
            <div class="chart-header">
              <h3 class="chart-title">Pelanggan per Paket</h3>
              <div class="chart-legend">
                <span class="legend-item">
                  <div class="legend-dot" style="background: #6366f1"></div>
                  10 Mbps
                </span>
                <span class="legend-item">
                  <div class="legend-dot" style="background: #06b6d4"></div>
                  20 Mbps
                </span>
              </div>
            </div>
            <div class="chart-content">
              <Chart type="bar" :data="paketChartData" :options="chartOptions" />
            </div>
          </div>
        </div>
      </div>

      <div class="chart-container full-width">
        <div class="chart-card">
          <div class="chart-header">
            <h3 class="chart-title">Invoice Bulanan</h3>
            <div class="chart-legend horizontal">
              <span class="legend-item">
                <div class="legend-dot" style="background: #71dd37"></div>
                Lunas
              </span>
              <span class="legend-item">
                <div class="legend-dot" style="background: #ffab5a"></div>
                Menunggu
              </span>
              <span class="legend-item">
                <div class="legend-dot" style="background: #ff3e1d"></div>
                Kadaluarsa
              </span>
            </div>
          </div>
          <div class="chart-content large">
            <Chart type="bar" :data="invoiceChartData" :options="invoiceChartOptions" />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { Chart } from 'vue-chartjs';
import {
  Chart as ChartJS, Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale, PointElement, LineElement, ChartData,
} from 'chart.js';

ChartJS.register(Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale, PointElement, LineElement);

// Struktur data baru untuk stats
const stats = ref([
  { title: 'Jumlah Pelanggan Jakinet', value: '0', subtitle: 'Total Pelanggan Jakinet', icon: 'mdi-account-group', color: '#6366f1' },
  { title: 'Jumlah Pelanggan Jelantik', value: '75', subtitle: 'Total Pelanggan Jelantik', icon: 'mdi-account-group', color: '#06b6d4' },
  { title: 'Pelanggan Jelantik Nagrak', value: '0', subtitle: 'Total Pelanggan Rusun Nagrak', icon: 'mdi-home-city', color: '#f59e0b' },
  { title: 'Total Servers', value: '3', subtitle: 'Total Mikrotik servers', icon: 'mdi-server', color: '#8b5cf6' },
  { title: 'Online Servers', value: '3', subtitle: 'Servers currently online', icon: 'mdi-server-network', color: '#10b981' },
  { title: 'Offline Servers', value: '0', subtitle: 'Servers currently offline', icon: 'mdi-server-network-off', color: '#ef4444' },
]);

// Chart data & options tetap sama
const chartOptions = ref({
  responsive: true,
  maintainAspectRatio: false,
  plugins: { legend: { display: false }, tooltip: { backgroundColor: 'rgba(0, 0, 0, 0.8)', titleColor: 'white', bodyColor: 'white', borderColor: '#e5e7eb', borderWidth: 1, cornerRadius: 8 } },
  scales: { y: { beginAtZero: true, grid: { color: '#f1f5f9', drawBorder: false }, ticks: { color: '#64748b', font: { size: 12 } } }, x: { grid: { display: false }, ticks: { color: '#64748b', font: { size: 12 } }, border: { display: false } } },
});
const invoiceChartOptions = ref({
  responsive: true,
  maintainAspectRatio: false,
  plugins: { legend: { display: false }, tooltip: { backgroundColor: 'rgba(0, 0, 0, 0.8)', titleColor: 'white', bodyColor: 'white', borderColor: '#e5e7eb', borderWidth: 1, cornerRadius: 8 } },
  scales: { x: { stacked: true, grid: { display: false }, ticks: { color: '#64748b', font: { size: 12 } }, border: { display: false } }, y: { stacked: true, grid: { color: '#f1f5f9', drawBorder: false }, ticks: { color: '#64748b', font: { size: 12 } } } },
});
const lokasiChartData = ref<ChartData<'bar'>>({ labels: ['Rusun Nagrak', 'Luar Pinus Elok', 'Rusunawa', 'Perumahan Tambun', 'Warung Kuning'], datasets: [{ label: 'Jumlah Pelanggan', data: [7, 2, 5, 71, 2], backgroundColor: '#6366f1', borderRadius: 6, borderSkipped: false }] });
const paketChartData = ref<ChartData<'bar'>>({ labels: ['10 Mbps', '20 Mbps', '30 Mbps', '50 Mbps'], datasets: [{ label: 'Jumlah Pelanggan', data: [56, 14, 2, 1], backgroundColor: ['#6366f1', '#06b6d4', '#f59e0b', '#ef4444'], borderRadius: 6, borderSkipped: false }] });
const invoiceChartData = ref({ labels: ['Ags', 'Sep', 'Okt', 'Nov', 'Des', 'Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun', 'Jul'], datasets: [{ type: 'line' as const, label: 'Total Invoice', data: [0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 12, 1], borderColor: '#64748b', tension: 0.4, pointBackgroundColor: '#64748b', pointBorderColor: '#ffffff', pointBorderWidth: 2,}, { type: 'bar' as const, label: 'Lunas', data: [0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 8, 0], backgroundColor: '#71dd37', borderRadius: 4, borderSkipped: false,}, { type: 'bar' as const, label: 'Menunggu', data: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 0], backgroundColor: '#ffab5a', borderRadius: 4, borderSkipped: false,}, { type: 'bar' as const, label: 'Kadaluarsa', data: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1], backgroundColor: '#ff3e1d', borderRadius: 4, borderSkipped: false,},],});
</script>

<style scoped>
/* PERBAIKAN: Hapus max-width agar responsif */
.dashboard-container {
  padding: 24px;
  margin: 0 auto;
}

.dashboard-header {
  margin-bottom: 32px;
}

.dashboard-title {
  font-size: 2rem;
  font-weight: 800;
  color: #1e293b;
  margin-bottom: 4px;
}

.dashboard-subtitle {
  color: #64748b;
  font-size: 1rem;
  font-weight: 400;
  margin: 0;
}

/* DESAIN BARU: Stats Grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr); /* <-- UBAH BARIS INI */
  gap: 24px;
  margin-bottom: 32px;
}

.stat-card {
  background: white;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  transition: all 0.3s ease;
  overflow: hidden; /* Penting untuk border bawah */
  display: flex;
  flex-direction: column;
}

.stat-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.07);
}

.stat-card-content {
  padding: 20px;
  flex-grow: 1;
  display: flex !important;
  flex-direction: column !important;
}

.stat-title {
  color: #64748b;
  font-size: 0.95rem;
  font-weight: 500;
  margin: 0 0 8px 0;
}

.stat-number {
  color: #1e293b;
  font-size: 2.1rem;
  font-weight: 700;
  margin: 0 0 10px 0;
}

.stat-footer {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: auto; /* Mendorong footer ke bawah */
}

.stat-subtitle {
  color: #64748b;
  font-size: 0.85rem;
}

.stat-border {
  height: 4px;
  width: 100%;
}

/* CSS untuk Chart (tidak berubah) */
.charts-section { display: flex; flex-direction: column; gap: 24px; }
.charts-row { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; }
.chart-container { min-width: 0; }
.chart-container.full-width { grid-column: 1 / -1; }
.chart-card { background: white; border-radius: 16px; border: 1px solid #f1f5f9; overflow: hidden; transition: all 0.3s ease; }
.chart-card:hover { box-shadow: 0 8px 25px rgba(0, 0, 0, 0.08); }
.chart-header { padding: 24px 24px 16px 24px; border-bottom: 1px solid #f1f5f9; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px; }
.chart-title { font-size: 1.1rem; font-weight: 700; color: #1e293b; margin: 0; }
.chart-legend { display: flex; flex-wrap: wrap; gap: 16px; }
.chart-legend.horizontal { gap: 20px; }
.legend-item { display: flex; align-items: center; gap: 8px; font-size: 0.85rem; color: #64748b; font-weight: 500; }
.legend-dot { width: 12px; height: 12px; border-radius: 50%; }
.chart-content { padding: 24px; height: 320px; position: relative; }
.chart-content.large { height: 380px; }

@media (max-width: 1200px) {
  .charts-row { grid-template-columns: 1fr; }
}

@media (max-width: 768px) {
  .dashboard-container { padding: 16px; }
  .stats-grid { gap: 16px; margin-bottom: 24px; }
  .dashboard-title { font-size: 1.75rem; }
  .stat-card-content { padding: 20px; }
  .stat-number { font-size: 2rem; }
  .chart-header { padding: 20px 20px 12px 20px; flex-direction: column; align-items: flex-start; }
  .chart-content { padding: 20px; height: 280px; }
  .chart-content.large { height: 320px; }
}
</style>