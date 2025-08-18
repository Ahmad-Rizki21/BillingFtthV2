<template>
  <div class="dashboard-container">
    <!-- Header Section -->
    <div class="dashboard-header">
      <div class="header-content">
        <div class="title-section">
          <h1 class="dashboard-title">
            <v-icon class="title-icon">mdi-view-dashboard</v-icon>
            Dashboard
          </h1>
          <p class="dashboard-subtitle">Monitor your billing system performance</p>
        </div>
        <div class="header-actions">
          <v-chip class="status-chip" color="success" size="small">
            <v-icon start size="12">mdi-circle</v-icon>
            System Active
          </v-chip>
        </div>
      </div>
    </div>

    <!-- Stats Cards Section -->
    <div v-if="loading" class="stats-grid mb-6">
      <v-skeleton-loader 
        v-for="n in 6" :key="n" 
        type="list-item-avatar-two-line" 
        class="stat-card-skeleton"
      ></v-skeleton-loader>
    </div>
    
    <div v-else class="stats-grid mb-6">
      <div 
        v-for="(stat, index) in stats" 
        :key="stat.title" 
        class="stat-card" 
        :class="`card-${index % 4}`"
      >
        <div class="stat-card-content">
          <div class="stat-header">
            <div class="stat-icon-container" :class="`icon-${index % 4}`">
              <v-icon :color="stat.color" size="20">{{ stat.icon }}</v-icon>
            </div>
          </div>
          <div class="stat-body">
            <h3 class="stat-value">{{ stat.value }}</h3>
            <p class="stat-title">{{ stat.title }}</p>
            <p class="stat-description">{{ stat.description }}</p>
          </div>
          <div class="stat-footer">
            <div class="progress-bar">
              <div class="progress-fill" :class="`progress-${index % 4}`"></div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Charts Section -->
    <div class="charts-section">
      <div class="charts-row">
        <!-- Location Chart -->
        <div class="chart-card location-chart">
          <div class="chart-header">
            <div class="chart-title-section">
              <h3 class="chart-title">
                <div class="chart-icon-wrapper">
                  <v-icon class="chart-icon">mdi-map-marker</v-icon>
                </div>
                Pelanggan per Lokasi
              </h3>
              <p class="chart-subtitle">Distribusi pelanggan berdasarkan lokasi</p>
            </div>
          </div>
          <div class="chart-container">
            <Chart v-if="!loading" type="bar" :data="lokasiChartData" :options="chartOptions" />
          </div>
        </div>

        <!-- Package Chart -->
        <div class="chart-card package-chart">
          <div class="chart-header">
            <div class="chart-title-section">
              <h3 class="chart-title">
                <div class="chart-icon-wrapper">
                  <v-icon class="chart-icon">mdi-package-variant</v-icon>
                </div>
                Pelanggan per Paket
              </h3>
              <p class="chart-subtitle">Distribusi pelanggan berdasarkan paket</p>
            </div>
          </div>
          <div class="chart-container">
            <Chart v-if="!loading" type="bar" :data="paketChartData" :options="chartOptions" />
          </div>
        </div>
      </div>
      
        <div class="charts-row">
        <!-- Growth Trend Chart -->
        <div class="chart-card growth-chart">
          <div class="chart-header">
            <div class="chart-title-section">
              <h3 class="chart-title">
                <div class="chart-icon-wrapper">
                  <v-icon class="chart-icon">mdi-chart-line</v-icon>
                </div>
                Tren Pertumbuhan Pelanggan
              </h3>
              <p class="chart-subtitle">Jumlah pelanggan baru per bulan</p>
            </div>
          </div>
          <div class="chart-container">
            <Chart v-if="!loading" type="line" :data="growthChartData" :options="chartOptions" />
          </div>
        </div>

        <!-- Invoice Chart -->
        <div class="chart-card invoice-chart">
          <div class="chart-header">
            <div class="chart-title-section">
              <h3 class="chart-title">
                <div class="chart-icon-wrapper">
                  <v-icon class="chart-icon">mdi-file-document-multiple</v-icon>
                </div>
                Invoice Bulanan
              </h3>
              <p class="chart-subtitle">Ringkasan status invoice per bulan</p>
            </div>
          </div>
          <div class="chart-container">
            <Chart v-if="!loading" type="bar" :data="invoiceChartData" :options="invoiceChartOptions" />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { Chart } from 'vue-chartjs';
import {
  Chart as ChartJS, 
  Title, 
  Tooltip, 
  Legend, 
  BarElement, 
  BarController,
  LineElement,
  LineController,
  PointElement,
  CategoryScale, 
  LinearScale, 
  Filler,
  ChartData,
  ChartOptions
} from 'chart.js';
import { useTheme } from 'vuetify';
import apiClient from '@/services/api';

// Mendaftarkan semua komponen yang dibutuhkan
ChartJS.register(
  Title, Tooltip, Legend, BarElement, BarController, LineElement, LineController, PointElement, CategoryScale, LinearScale, Filler
);

const theme = useTheme();
const loading = ref(true);

const stats = ref<any[]>([]);
const lokasiChartData = ref<ChartData<'bar'>>({ labels: [], datasets: [] });
const paketChartData = ref<ChartData<'bar'>>({ labels: [], datasets: [] });
const invoiceChartData = ref<any>({ labels: [], datasets: [] });
const growthChartData = ref<ChartData<'line'>>({ labels: [], datasets: [] });

async function fetchMikrotikStats() {
  try {
    // FIX: Menghapus /api/ dari URL karena sudah ada di baseURL
    const response = await apiClient.get('/dashboard/mikrotik-status');
    const { online, offline } = response.data;

    const onlineStat = stats.value.find(s => s.title === "Online Servers");
    if (onlineStat) onlineStat.value = online;

    const offlineStat = stats.value.find(s => s.title === "Offline Servers");
    if (offlineStat) offlineStat.value = offline;

  } catch (error) {
    console.error("Failed to fetch Mikrotik server status:", error);
    const onlineStat = stats.value.find(s => s.title === "Online Servers");
    if (onlineStat) onlineStat.value = 'N/A';
    const offlineStat = stats.value.find(s => s.title === "Offline Servers");
    if (offlineStat) offlineStat.value = 'N/A';
  }
}

onMounted(async () => {
  try {
    // FIX: Menghapus /api/ dari URL karena sudah ada di baseURL
    const response = await apiClient.get('/dashboard/');
    const data = response.data;

    stats.value = data.stat_cards.map((card: any) => ({
      ...card,
      icon: getIconForStat(card.title),
      color: getColorForStat(card.title)
    }));

    lokasiChartData.value = {
      labels: data.lokasi_chart.labels,
      datasets: [{
        label: 'Jumlah Pelanggan',
        data: data.lokasi_chart.data,
        backgroundColor: 'rgba(99, 102, 241, 0.8)',
        borderColor: 'rgb(99, 102, 241)',
        borderWidth: 2,
        borderRadius: 8,
        borderSkipped: false,
      }],
    };

    paketChartData.value = {
      labels: data.paket_chart.labels,
      datasets: [{
        label: 'Jumlah Pelanggan',
        data: data.paket_chart.data,
        backgroundColor: [
          'rgba(99, 102, 241, 0.8)',
          'rgba(34, 197, 94, 0.8)',
          'rgba(251, 191, 36, 0.8)',
          'rgba(239, 68, 68, 0.8)'
        ],
        borderColor: [
          'rgb(99, 102, 241)',
          'rgb(34, 197, 94)',
          'rgb(251, 191, 36)',
          'rgb(239, 68, 68)'
        ],
        borderWidth: 2,
        borderRadius: 8,
        borderSkipped: false,
      }],
    };
    
    invoiceChartData.value = {
      labels: data.invoice_summary_chart.labels,
      datasets: [
        { 
          type: 'line' as const, 
          label: 'Total Invoice', 
          data: data.invoice_summary_chart.total, 
          borderColor: 'rgb(168, 85, 247)', 
          backgroundColor: 'rgba(168, 85, 247, 0.1)', 
          tension: 0.4,
          borderWidth: 3,
          pointBackgroundColor: 'rgb(168, 85, 247)',
          pointBorderColor: '#fff',
          pointBorderWidth: 2,
          pointRadius: 6,
          fill: true
        },
        { 
          type: 'bar' as const, 
          label: 'Lunas', 
          data: data.invoice_summary_chart.lunas, 
          backgroundColor: 'rgba(34, 197, 94, 0.8)', 
          borderColor: 'rgb(34, 197, 94)',
          borderWidth: 2,
          borderRadius: 6,
          stack: 'Stack 0' 
        },
        { 
          type: 'bar' as const, 
          label: 'Menunggu', 
          data: data.invoice_summary_chart.menunggu, 
          backgroundColor: 'rgba(251, 191, 36, 0.8)', 
          borderColor: 'rgb(251, 191, 36)',
          borderWidth: 2,
          borderRadius: 6,
          stack: 'Stack 0' 
        },
        { 
          type: 'bar' as const, 
          label: 'Kadaluarsa', 
          data: data.invoice_summary_chart.kadaluarsa, 
          backgroundColor: 'rgba(239, 68, 68, 0.8)', 
          borderColor: 'rgb(239, 68, 68)',
          borderWidth: 2,
          borderRadius: 6,
          stack: 'Stack 0' 
        },
      ],
    };
    fetchGrowthTrendData();
 } catch (error) {
    console.error("Failed to fetch dashboard data:", error);
  } finally {
    loading.value = false;
    fetchMikrotikStats();
  }
});


// Menampilkan pertumbuhan pelanggan
async function fetchGrowthTrendData() {
  try {
    const response = await apiClient.get('/dashboard/growth-trend');
    const data = response.data;
    
    growthChartData.value = {
      labels: data.labels,
      datasets: [{
        label: 'Pelanggan Baru',
        data: data.data,
        borderColor: 'rgb(236, 72, 153)',
        backgroundColor: 'rgba(236, 72, 153, 0.1)',
        tension: 0.4,
        borderWidth: 3,
        pointBackgroundColor: 'rgb(236, 72, 153)',
        pointBorderColor: '#fff',
        pointBorderWidth: 2,
        pointRadius: 6,
        fill: true,
      }]
    };
  } catch (error) {
    console.error("Gagal mengambil data tren pertumbuhan:", error);
  }
}


function getIconForStat(title: string) {
  if (title.toLowerCase().includes('jakinet')) return 'mdi-account-network';
  if (title.toLowerCase().includes('jelantik')) return 'mdi-account-group';
  if (title.toLowerCase().includes('nagrak')) return 'mdi-home-group';
  if (title.toLowerCase().includes('total servers')) return 'mdi-server';
  if (title.toLowerCase().includes('online')) return 'mdi-check-circle';
  if (title.toLowerCase().includes('offline')) return 'mdi-close-circle';
  return 'mdi-chart-box';
}

function getColorForStat(title: string) {
  if (title.toLowerCase().includes('jakinet')) return 'primary';
  if (title.toLowerCase().includes('jelantik')) return 'success';
  if (title.toLowerCase().includes('nagrak')) return 'warning';
  if (title.toLowerCase().includes('total servers')) return 'error';
  if (title.toLowerCase().includes('online')) return 'success';
  if (title.toLowerCase().includes('offline')) return 'error';
  return 'primary';
}

const chartAxisColor = computed(() => theme.global.current.value.dark ? 'rgba(255, 255, 255, 0.7)' : 'rgba(0, 0, 0, 0.7)');
const chartGridColor = computed(() => theme.global.current.value.dark ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)');

const chartOptions = computed((): ChartOptions<'bar'> => ({
  responsive: true,
  maintainAspectRatio: false,
  plugins: { 
    legend: { display: false },
    tooltip: {
      backgroundColor: theme.global.current.value.dark ? 'rgba(0, 0, 0, 0.9)' : 'rgba(255, 255, 255, 0.95)',
      titleColor: chartAxisColor.value,
      bodyColor: chartAxisColor.value,
      borderColor: chartGridColor.value,
      borderWidth: 1,
      cornerRadius: 8,
      displayColors: true,
    }
  },
  scales: {
    y: { 
      beginAtZero: true, 
      grid: { color: chartGridColor.value },
      ticks: { 
        color: chartAxisColor.value,
        font: { 
          size: 12, 
          weight: 'normal' as const
        }
      }
    },
    x: { 
      grid: { display: false },
      ticks: { 
        color: chartAxisColor.value,
        font: { 
          size: 12, 
          weight: 'normal' as const
        }
      }
    },
  },
}));

const invoiceChartOptions = computed((): ChartOptions<'bar'> => ({
  responsive: true,
  maintainAspectRatio: false,
  plugins: { 
    legend: { 
      position: 'top' as const, 
      labels: { 
        color: chartAxisColor.value,
        usePointStyle: true,
        pointStyle: 'circle' as const,
        font: { 
          size: 12, 
          weight: 'bold' as const
        }
      } 
    },
    tooltip: {
      backgroundColor: theme.global.current.value.dark ? 'rgba(0, 0, 0, 0.9)' : 'rgba(255, 255, 255, 0.95)',
      titleColor: chartAxisColor.value,
      bodyColor: chartAxisColor.value,
      borderColor: chartGridColor.value,
      borderWidth: 1,
      cornerRadius: 8,
      displayColors: true,
    }
  },
  scales: {
    y: { 
      stacked: true, 
      beginAtZero: true, 
      grid: { color: chartGridColor.value },
      ticks: { 
        color: chartAxisColor.value,
        font: { 
          size: 12, 
          weight: 'normal' as const
        }
      }
    },
    x: { 
      stacked: true, 
      grid: { display: false },
      ticks: { 
        color: chartAxisColor.value,
        font: { 
          size: 12, 
          weight: 'normal' as const
        }
      }
    },
  },
}));
</script>

<style scoped>
/* Base Styling */
.dashboard-container {
  padding: 1.5rem;
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.02) 0%, rgba(34, 197, 94, 0.02) 100%);
  min-height: 100vh;
  animation: fadeIn 0.6s ease-out;
}

/* Header Section - Improved Responsive Layout */
.dashboard-header {
  margin-bottom: 1.5rem;
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(20px);
  border-radius: 16px;
  padding: 1.25rem 1.5rem;
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
}

.title-section {
  flex: 1;
  min-width: 0; /* Prevents flex item from overflowing */
}

.dashboard-title {
  color: rgb(var(--v-theme-on-background));
  font-weight: 800;
  font-size: 2rem;
  margin-bottom: 0.25rem;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  background: linear-gradient(135deg, #6366f1 0%, #22c55e 100%);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
  line-height: 1.2;
}

.title-icon {
  background: linear-gradient(135deg, #6366f1 0%, #22c55e 100%);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
  flex-shrink: 0;
}

.dashboard-subtitle {
  color: rgba(var(--v-theme-on-surface), 0.7);
  font-size: 0.95rem;
  font-weight: 500;
  line-height: 1.4;
}

/* Header Actions - Improved Layout */
.header-actions {
  flex-shrink: 0;
  display: flex;
  align-items: flex-start;
}

.status-chip {
  font-weight: 600;
  font-size: 0.75rem;
  height: 32px;
  white-space: nowrap;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(34, 197, 94, 0.2);
  transition: all 0.2s ease;
}

.status-chip:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(34, 197, 94, 0.3);
}

/* Stats Grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1rem;
}

@media (min-width: 1200px) {
  .stats-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

/* Stat Cards */
.stat-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 16px;
  padding: 0;
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
  cursor: pointer;
}

.stat-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
}

.stat-card.card-0::before { background: linear-gradient(90deg, #6366f1, #8b5cf6); }
.stat-card.card-1::before { background: linear-gradient(90deg, #22c55e, #10b981); }
.stat-card.card-2::before { background: linear-gradient(90deg, #f59e0b, #f97316); }
.stat-card.card-3::before { background: linear-gradient(90deg, #ef4444, #ec4899); }

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.12);
  border-color: rgba(99, 102, 241, 0.3);
}

.stat-card-content {
  padding: 1.25rem;
}

.stat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.stat-icon-container {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.1), rgba(99, 102, 241, 0.05));
  transition: all 0.2s ease;
}

.stat-card:hover .stat-icon-container {
  transform: scale(1.1);
}

.stat-icon-container.icon-0 { background: linear-gradient(135deg, rgba(99, 102, 241, 0.15), rgba(139, 92, 246, 0.05)); }
.stat-icon-container.icon-1 { background: linear-gradient(135deg, rgba(34, 197, 94, 0.15), rgba(16, 185, 129, 0.05)); }
.stat-icon-container.icon-2 { background: linear-gradient(135deg, rgba(245, 158, 11, 0.15), rgba(249, 115, 22, 0.05)); }
.stat-icon-container.icon-3 { background: linear-gradient(135deg, rgba(239, 68, 68, 0.15), rgba(236, 72, 153, 0.05)); }

.stat-body {
  margin-bottom: 1rem;
}

.stat-value {
  font-size: 2rem;
  font-weight: 800;
  color: rgb(var(--v-theme-on-surface));
  line-height: 1;
  margin-bottom: 0.5rem;
}

.stat-title {
  font-size: 0.85rem;
  color: rgb(var(--v-theme-on-surface));
  font-weight: 600;
  margin-bottom: 0.25rem;
}

.stat-description {
  font-size: 0.75rem;
  color: rgba(var(--v-theme-on-surface), 0.6);
  line-height: 1.4;
}

.progress-bar {
  height: 3px;
  background: rgba(var(--v-theme-on-surface), 0.1);
  border-radius: 2px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  border-radius: 2px;
  width: 75%;
  animation: progressFill 1.5s ease-out;
}

.progress-fill.progress-0 { background: linear-gradient(90deg, #6366f1, #8b5cf6); }
.progress-fill.progress-1 { background: linear-gradient(90deg, #22c55e, #10b981); }
.progress-fill.progress-2 { background: linear-gradient(90deg, #f59e0b, #f97316); }
.progress-fill.progress-3 { background: linear-gradient(90deg, #ef4444, #ec4899); }

/* Charts Section */
.charts-section {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.charts-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(360px, 1fr));
  gap: 1.5rem;
}

.chart-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 16px;
  padding: 1.25rem;
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.chart-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.12);
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1.25rem;
}

.chart-title-section {
  flex: 1;
}

.chart-title {
  font-size: 1.1rem;
  font-weight: 700;
  color: rgb(var(--v-theme-on-surface));
  margin-bottom: 0.25rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.chart-icon-wrapper {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.1), rgba(99, 102, 241, 0.05));
  transition: all 0.2s ease;
}

.chart-card:hover .chart-icon-wrapper {
  transform: scale(1.1);
}

.chart-icon {
  color: rgb(var(--v-theme-primary));
  font-size: 16px;
}

.chart-subtitle {
  font-size: 0.8rem;
  color: rgba(var(--v-theme-on-surface), 0.6);
  font-weight: 500;
}

.chart-container {
  height: 250px;
  position: relative;
}

.large-chart {
  height: 350px;
}

/* Animations */
@keyframes fadeIn {
  from { 
    opacity: 0; 
    transform: translateY(20px);
  }
  to { 
    opacity: 1; 
    transform: translateY(0);
  }
}

@keyframes progressFill {
  from { width: 0; }
  to { width: 75%; }
}

/* Dark Theme */
.v-theme--dark .dashboard-header,
.v-theme--dark .stat-card,
.v-theme--dark .chart-card {
  background: rgba(30, 30, 30, 0.95);
  border-color: rgba(255, 255, 255, 0.1);
}

.v-theme--dark .dashboard-container {
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.05) 0%, rgba(34, 197, 94, 0.05) 100%);
}

.v-theme--dark .status-chip {
  box-shadow: 0 2px 8px rgba(34, 197, 94, 0.4);
}

.stat-card-skeleton {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 16px;
  padding: 1.25rem;
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

/* Responsive Design */
@media (max-width: 768px) {
  .dashboard-container {
    padding: 1rem;
  }
  
  .dashboard-header {
    padding: 1rem;
  }
  
  .header-content {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
  
  .header-actions {
    align-self: flex-end;
  }
  
  .dashboard-title {
    font-size: 1.75rem;
  }
  
  .dashboard-subtitle {
    font-size: 0.9rem;
  }
  
  .stats-grid {
    grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
    gap: 0.875rem;
  }
  
  .charts-row {
    grid-template-columns: 1fr;
    gap: 1rem;
  }
}

@media (max-width: 480px) {
  .dashboard-container {
    padding: 0.75rem;
  }
  
  .dashboard-header {
    padding: 0.875rem;
    margin-bottom: 1rem;
  }
  
  .dashboard-title {
    font-size: 1.5rem;
    gap: 0.5rem;
  }
  
  .dashboard-subtitle {
    font-size: 0.85rem;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
    gap: 0.75rem;
  }
  
  .stat-card-content {
    padding: 1rem;
  }
  
  .chart-card {
    padding: 1rem;
  }
  
  .status-chip {
    font-size: 0.7rem;
    height: 28px;
  }
}

@media (max-width: 360px) {
  .header-content {
    gap: 0.75rem;
  }
  
  .dashboard-title {
    font-size: 1.375rem;
  }
  
  .dashboard-subtitle {
    font-size: 0.8rem;
  }
  
  .status-chip {
    font-size: 0.65rem;
    height: 26px;
  }
}

/* Improved Mobile Layout for System Active */
@media (max-width: 640px) {
  .header-content {
    align-items: stretch;
  }
  
  .header-actions {
    margin-top: 0.5rem;
    justify-content: flex-end;
  }
  
  .status-chip {
    align-self: flex-start;
  }
}
</style>