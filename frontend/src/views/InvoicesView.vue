<template>
  <v-container fluid class="pa-6">
    <!-- Header Section dengan gradient background -->
    <div class="invoice-header mb-8 pa-6 rounded-xl">
      <div class="d-flex align-center">
        <div class="header-content d-flex align-center">
          <div class="icon-container me-4">
            <v-icon size="32" color="white">mdi-receipt-text-outline</v-icon>
          </div>
          <div>
            <h1 class="text-h3 font-weight-bold text-white mb-1">Invoices</h1>
            <p class="text-subtitle-1 text-white text-opacity-90 mb-0">
              Kelola semua tagihan dan pembayaran pelanggan
            </p>
          </div>
        </div>
        <v-spacer></v-spacer>
        <v-btn 
          color="white"
          variant="elevated"
          size="large"
          elevation="4"
          @click="dialogGenerate = true"
          prepend-icon="mdi-plus-circle-outline"
          class="text-none font-weight-bold"
          style="color: #4338ca !important;"
        >
          Buat Invoice Manual
        </v-btn>
      </div>
    </div>

    <!-- Stats Cards -->
    <v-row class="mb-6">
      <v-col cols="12" md="3">
        <v-card class="stats-card pa-4" elevation="2">
          <div class="d-flex align-center">
            <div class="stats-icon success me-3">
              <v-icon color="success">mdi-check-circle</v-icon>
            </div>
            <div>
              <div class="text-h6 font-weight-bold">{{ getPaidCount() }}</div>
              <div class="text-caption text-medium-emphasis">Invoice Lunas</div>
            </div>
          </div>
        </v-card>
      </v-col>
      <v-col cols="12" md="3">
        <v-card class="stats-card pa-4" elevation="2">
          <div class="d-flex align-center">
            <div class="stats-icon warning me-3">
              <v-icon color="warning">mdi-clock-outline</v-icon>
            </div>
            <div>
              <div class="text-h6 font-weight-bold">{{ getPendingCount() }}</div>
              <div class="text-caption text-medium-emphasis">Belum Dibayar</div>
            </div>
          </div>
        </v-card>
      </v-col>
      <v-col cols="12" md="3">
        <v-card class="stats-card pa-4" elevation="2">
          <div class="d-flex align-center">
            <div class="stats-icon error me-3">
              <v-icon color="error">mdi-alert-circle</v-icon>
            </div>
            <div>
              <div class="text-h6 font-weight-bold">{{ getOverdueCount() }}</div>
              <div class="text-caption text-medium-emphasis">Kadaluarsa</div>
            </div>
          </div>
        </v-card>
      </v-col>
      <v-col cols="12" md="3">
        <v-card class="stats-card pa-4" elevation="2">
          <div class="d-flex align-center">
            <div class="stats-icon primary me-3">
              <v-icon color="primary">mdi-receipt-text</v-icon>
            </div>
            <div>
              <div class="text-h6 font-weight-bold">{{ invoices.length }}</div>
              <div class="text-caption text-medium-emphasis">Total Invoice</div>
            </div>
          </div>
        </v-card>
      </v-col>
    </v-row>

    <!-- Data Table Card -->
    <v-card class="invoice-table-card" elevation="3">
      <!-- Table Header -->
      <div class="table-header pa-6">
        <div class="d-flex align-center">
          <div>
            <h2 class="text-h5 font-weight-bold mb-1">Daftar Tagihan</h2>
            <p class="text-body-2 text-medium-emphasis mb-0">
              Kelola dan pantau status pembayaran invoice
            </p>
          </div>
          <v-spacer></v-spacer>
          <v-text-field
            v-model="searchQuery"
            prepend-inner-icon="mdi-magnify"
            label="Cari Invoice..."
            variant="outlined"
            density="comfortable"
            hide-details
            style="max-width: 350px;"
            clearable
            class="search-field"
          ></v-text-field>
        </div>
      </div>
      
      <!-- Data Table -->
      <v-data-table
        :headers="headers"
        :items="filteredInvoices"
        :loading="loading"
        item-value="id"
        class="invoice-table"
        :items-per-page="15"
        :loading-text="'Memuat data invoice...'"
        :no-data-text="'Tidak ada data invoice'"
      >
        <!-- Loading slot -->
        <template v-slot:loading>
          <div class="text-center pa-8">
            <v-progress-circular indeterminate color="primary"></v-progress-circular>
            <p class="mt-4 text-medium-emphasis">Memuat data invoice...</p>
          </div>
        </template>

        <!-- Invoice Number Column -->
        <template v-slot:item.invoice_number="{ item }">
          <div class="invoice-number-cell">
            <div class="font-weight-bold text-primary">{{ item.invoice_number }}</div>
            <div class="text-caption text-medium-emphasis">
              <v-icon size="12" class="me-1">mdi-calendar</v-icon>
              {{ formatDate(item.tgl_invoice) }}
            </div>
          </div>
        </template>

        <!-- Customer Column -->
        <template v-slot:item.pelanggan_id="{ item }">
          <div class="customer-cell">
            <div class="d-flex align-center">
              <v-avatar size="32" color="primary" class="me-2">
                <v-icon color="white" size="16">mdi-account</v-icon>
              </v-avatar>
              <div>
                <div class="font-weight-medium">{{ getPelangganName(item.pelanggan_id) }}</div>
                <div class="text-caption text-medium-emphasis">
                  <v-icon size="12" class="me-1">mdi-identifier</v-icon>
                  ID: {{ item.id_pelanggan }}
                </div>
              </div>
            </div>
          </div>
        </template>
        
        <!-- Total Amount Column -->
        <template v-slot:item.total_harga="{ item }">
          <div class="amount-cell">
            <span class="text-h6 font-weight-bold text-success">
              {{ formatCurrency(item.total_harga) }}
            </span>
          </div>
        </template>

        <!-- Status Column -->
        <template v-slot:item.status_invoice="{ item }">
          <v-chip 
            :color="getStatusColor(item.status_invoice)" 
            variant="elevated"
            size="small" 
            class="font-weight-bold status-chip"
            :prepend-icon="getStatusIcon(item.status_invoice)"
          >
            {{ item.status_invoice }}
          </v-chip>
        </template>

        <!-- Due Date Column -->
        <template v-slot:item.tgl_jatuh_tempo="{ item }">
          <div class="due-date-cell">
            <div class="font-weight-medium">{{ formatDate(item.tgl_jatuh_tempo) }}</div>
            <div class="text-caption" :class="getDueDateClass(item.tgl_jatuh_tempo)">
              {{ getDueDateLabel(item.tgl_jatuh_tempo) }}
            </div>
          </div>
        </template>

        <!-- Actions Column -->
        <template v-slot:item.actions="{ item }">
          <div class="action-buttons">
            <v-tooltip location="top">
              <template v-slot:activator="{ props }">
                <v-btn 
                  icon
                  v-bind="props"
                  variant="text" 
                  size="small" 
                  color="primary" 
                  @click="copyPaymentLink(item.payment_link)"
                  :disabled="!item.payment_link"
                  class="action-btn"
                >
                  <v-icon>mdi-content-copy</v-icon>
                </v-btn>
              </template>
              <span>Salin Link Pembayaran</span>
            </v-tooltip>
            
            <v-tooltip location="top">
              <template v-slot:activator="{ props }">
                <v-btn 
                  icon="mdi-eye" 
                  v-bind="props"
                  variant="text" 
                  size="small" 
                  
                  @click="openDetailDialog(item)"
                ></v-btn>
              </template>
              <span>Lihat Detail</span>
            </v-tooltip>

            <v-tooltip location="top">
              <template v-slot:activator="{ props }">
                <v-btn 
                  icon="mdi-delete" 
                  v-bind="props"
                  variant="text" 
                  size="small" 
                  color="error" 
                  @click="openDeleteDialog(item)"
                  class="action-btn"
                ></v-btn>
              </template>
              <span>Hapus Invoice</span>
            </v-tooltip>

            <v-tooltip location="top">
  <template v-slot:activator="{ props }">
    <v-btn 
      v-if="item.status_invoice !== 'Lunas'"
      icon="mdi-check-decagram" 
      v-bind="props"
      variant="text" 
      size="small" 
      color="success" 
      @click="openMarkAsPaidDialog(item)"
    ></v-btn>
  </template>
  <span>Tandai Lunas</span>
</v-tooltip>

<v-dialog v-model="dialogMarkAsPaid" max-width="500px" persistent>
  <v-card>
    <v-card-title class="text-h5">Tandai Lunas?</v-card-title>
    <v-card-text>
      <p>Anda akan menandai invoice <strong>{{ itemToMark?.invoice_number }}</strong> sebagai lunas.</p>
      <v-select
        v-model="paymentMethod"
        :items="['Cash', 'Bank Transfer', 'Lainnya']"
        label="Metode Pembayaran"
        variant="outlined"
        density="compact"
        class="mt-4"
      ></v-select>
    </v-card-text>
    <v-card-actions>
      <v-spacer></v-spacer>
      <v-btn text @click="closeMarkAsPaidDialog">Batal</v-btn>
      <v-btn 
        color="success" 
        @click="confirmMarkAsPaid"
        :loading="markingAsPaid"
      >
        Konfirmasi
      </v-btn>
    </v-card-actions>
  </v-card>
</v-dialog>
            
          </div>
        </template>
      </v-data-table>
      
    </v-card>

    <v-dialog v-model="dialogDelete" max-width="500px" persistent>
  <v-card>
    <v-card-title class="text-h5">Konfirmasi Hapus</v-card-title>
    <v-card-text>
      Anda yakin ingin menghapus invoice <strong>{{ itemToDelete?.invoice_number }}</strong> secara permanen?
    </v-card-text>
    
    <v-card-actions>
      <v-spacer></v-spacer>
      <v-btn text @click="closeDeleteDialog">Batal</v-btn>
      <v-btn 
        color="error" 
        :loading="deleting"
        @click="confirmDelete"
      >
        Ya, Hapus
      </v-btn>
    </v-card-actions>
    
  </v-card>
</v-dialog>


    <!-- Generate Invoice Dialog -->
    <v-dialog v-model="dialogGenerate" max-width="600px" persistent>
  <v-card class="generate-dialog">
    <div class="dialog-header pa-6">
      <h2 class="text-h5 font-weight-bold text-white mb-1">Buat Invoice Manual</h2>
      <p class="text-body-2 text-white text-opacity-90 mb-0">
        Pilih langganan pelanggan untuk membuat invoice baru
      </p>
    </div>
    
    <v-card-text class="pa-6">
      <div class="mb-4">
        <v-icon color="info" class="me-2">mdi-information</v-icon>
        <span class="text-body-2 text-medium-emphasis">
          Pilih langganan pelanggan yang ingin dibuatkan invoice-nya sekarang.
        </span>
      </div>
      
      <v-autocomplete
        v-model="selectedLanggananId"
        :items="langgananForSelect"
        item-title="display_name"
        item-value="id"
        label="Pilih Langganan Pelanggan"
        placeholder="Ketik nama pelanggan atau ID langganan..."
        variant="outlined"
        density="comfortable"
        clearable
        :prepend-inner-icon="'mdi-account-search'"
        class="mb-4"
      >
        <template v-slot:item="{ props }">
          <v-list-item v-bind="props">
            <template v-slot:prepend>
              <v-avatar size="32" color="primary">
                <v-icon color="white" size="16">mdi-account</v-icon>
              </v-avatar>
            </template>
          </v-list-item>
        </template>
      </v-autocomplete>

      <v-expand-transition>
        <div v-if="selectedLanggananDetails">
          <v-row>
            <v-col cols="12" md="6">
              <v-text-field
                :model-value="formatCurrency(selectedLanggananDetails.paket_layanan?.harga)"
                label="Harga Paket"
                variant="outlined"
                readonly
                prepend-inner-icon="mdi-cash"
              ></v-text-field>
            </v-col>
            <v-col cols="12" md="6">
              <v-text-field
                :model-value="formatDate(selectedLanggananDetails.tgl_jatuh_tempo)"
                label="Jatuh Tempo"
                variant="outlined"
                readonly
                prepend-inner-icon="mdi-calendar-end"
              ></v-text-field>
            </v-col>
          </v-row>
          <p class="text-caption text-medium-emphasis mt-n2">
            * Total tagihan akhir akan ditambahkan pajak sesuai brand.
          </p>
        </div>
      </v-expand-transition>
      
    </v-card-text>
    
    <v-card-actions class="pa-6 pt-0">
      <v-spacer></v-spacer>
      <v-btn 
        variant="outlined" 
        @click="closeDialog"
        size="large"
        class="text-none"
      >
        Batal
      </v-btn>
      <v-btn 
        color="primary" 
        @click="generateManualInvoice"
        :loading="generating"
        :disabled="!selectedLanggananId"
        variant="elevated"
        size="large"
        class="text-none font-weight-bold"
      >
        <v-icon class="me-2">mdi-plus</v-icon>
        Buat Invoice
      </v-btn>
    </v-card-actions>
  </v-card>
</v-dialog>
    
    <!-- Enhanced Snackbar -->
    <v-snackbar 
      v-model="snackbar.show" 
      :color="snackbar.color" 
      :timeout="4000"
      location="top right"
      variant="elevated"
      class="custom-snackbar"
    >
      <div class="d-flex align-center">
        <v-icon class="me-2">{{ getSnackbarIcon(snackbar.color) }}</v-icon>
        {{ snackbar.text }}
      </div>
      <template v-slot:actions>
        <v-btn
          variant="text"
          @click="snackbar.show = false"
          icon="mdi-close"
          size="small"
        ></v-btn>
      </template>
    </v-snackbar>

    <InvoiceDetailDialog 
      v-model="dialogDetail" 
      :invoice="selectedInvoice"
    />
    

  </v-container>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import apiClient from '@/services/api';
import type { Invoice, PelangganSelectItem, LanggananSelectItem } from '@/interfaces/invoice';
import InvoiceDetailDialog from '@/components/dialogs/InvoiceDetailDialog.vue';

// --- State ---
const invoices = ref<Invoice[]>([]);
const pelangganList = ref<PelangganSelectItem[]>([]);
const langgananList = ref<any[]>([]);
const loading = ref(true);
const generating = ref(false);
const searchQuery = ref('');
const dialogGenerate = ref(false);
const selectedLanggananId = ref<number | null>(null);
const dialogDetail = ref(false);
const selectedInvoice = ref<Invoice | null>(null);
const snackbar = ref({ show: false, text: '', color: 'success' });
const dialogDelete = ref(false);
const deleting = ref(false);
const itemToDelete = ref<Invoice | null>(
  null
);
const dialogMarkAsPaid = ref(false);
const markingAsPaid = ref(false);
const itemToMark = ref<Invoice | null>(null);
const paymentMethod = ref('Cash');

// --- Table Headers ---
const headers = [
  { title: 'Nomor Invoice', key: 'invoice_number', width: '200px' },
  { title: 'Pelanggan', key: 'pelanggan_id', width: '250px' },
  { title: 'Total Tagihan', key: 'total_harga', align: 'end' as const, width: '150px' },
  { title: 'Status', key: 'status_invoice', align: 'center' as const, width: '130px' },
  { title: 'Jatuh Tempo', key: 'tgl_jatuh_tempo', align: 'center' as const, width: '150px' },
  { title: 'Actions', key: 'actions', sortable: false, align: 'center' as const, width: '120px' },
];

// --- Computed Properties ---
const filteredInvoices = computed(() => {
  if (!searchQuery.value) return invoices.value;
  const query = searchQuery.value.toLowerCase();
  return invoices.value.filter(inv => 
    inv.invoice_number.toLowerCase().includes(query) ||
    getPelangganName(inv.pelanggan_id).toLowerCase().includes(query) ||
    inv.id_pelanggan.toLowerCase().includes(query)
  );
});

const langgananForSelect = computed((): LanggananSelectItem[] => {
  return langgananList.value.map(langganan => {
    const pelanggan = pelangganList.value.find(p => p.id === langganan.pelanggan_id);
    return {
      id: langganan.id,
      pelanggan_id: langganan.pelanggan_id,
      display_name: `${pelanggan?.nama || 'N/A'} (Langganan ID: ${langganan.id})`
    };
  });
});


function openDeleteDialog(item: Invoice) {
  itemToDelete.value = item;
  dialogDelete.value = true;
}

function closeDeleteDialog() {
  dialogDelete.value = false;
  itemToDelete.value = null;
}

async function confirmDelete() {
  if (!itemToDelete.value) return;
  
  deleting.value = true;
  try {
    // Asumsi endpoint hapus adalah DELETE /invoices/{id}
    await apiClient.delete(`/invoices/${itemToDelete.value.id}`);
    showSnackbar('Invoice berhasil dihapus', 'success');
    fetchInvoices(); // Refresh tabel
    closeDeleteDialog();
  } catch (error: any) {
    const detail = error.response?.data?.detail || 'Gagal menghapus invoice.';
    showSnackbar(detail, 'error');
  } finally {
    deleting.value = false;
  }
}

const selectedLanggananDetails = computed(() => {
  if (!selectedLanggananId.value) return null;
  // Cari langganan yang cocok di dalam daftar
  return langgananList.value.find(lang => lang.id === selectedLanggananId.value);
})

// --- Stats Methods ---
const getPaidCount = () => invoices.value.filter(inv => inv.status_invoice === 'Lunas').length;
const getPendingCount = () => invoices.value.filter(inv => inv.status_invoice === 'Belum Dibayar').length;
const getOverdueCount = () => invoices.value.filter(inv => inv.status_invoice === 'Kadaluarsa').length;

// --- Methods ---
onMounted(() => {
  fetchInvoices();
  fetchPelangganForSelect();
  fetchLanggananForSelect();
});

async function fetchInvoices() {
  loading.value = true;
  try {
    const response = await apiClient.get<Invoice[]>('/invoices/');
    invoices.value = response.data.sort((a, b) => b.id - a.id);
  } finally {
    loading.value = false;
  }
}

async function fetchPelangganForSelect() {
  try {
    const response = await apiClient.get<PelangganSelectItem[]>('/pelanggan/');
    pelangganList.value = response.data;
  } catch (error) { console.error(error); }
}

async function fetchLanggananForSelect() {
  try {
    const response = await apiClient.get<any[]>('/langganan/');
    langgananList.value = response.data;
  } catch (error) { console.error(error); }
}

function openDetailDialog(item: Invoice) {
  selectedInvoice.value = item;
  dialogDetail.value = true;
}

async function generateManualInvoice() {
  if (!selectedLanggananId.value) return;
  generating.value = true;
  try {
    await apiClient.post('/invoices/generate', {
      langganan_id: selectedLanggananId.value
    });
    showSnackbar('Invoice berhasil dibuat!', 'success');
    fetchInvoices();
    closeDialog();
  } catch (error: any) {
    const detail = error.response?.data?.detail || 'Gagal membuat invoice.';
    showSnackbar(detail, 'error');
  } finally {
    generating.value = false;
  }
}

function closeDialog() {
  dialogGenerate.value = false;
  selectedLanggananId.value = null;
}

async function copyPaymentLink(link: string | null | undefined) {
  if (!link) {
    showSnackbar('Tidak ada link pembayaran', 'warning');
    return;
  }
  try {
    await navigator.clipboard.writeText(link);
    showSnackbar('Link pembayaran berhasil disalin!', 'success');
  } catch (err) {
    showSnackbar('Gagal menyalin link', 'error');
  }
}

function showSnackbar(text: string, color: string) {
  snackbar.value.text = text;
  snackbar.value.color = color;
  snackbar.value.show = true;
}

// --- Helper Functions ---
function getPelangganName(pelangganId: number): string {
  const pelanggan = pelangganList.value.find(p => p.id === pelangganId);
  return pelanggan?.nama || `ID: ${pelangganId}`;
}

function getStatusColor(status: string): string {
  switch (status) {
    case 'Lunas': return 'success';
    case 'Belum Dibayar': return 'warning';
    case 'Kadaluarsa': return 'error';
    default: return 'grey';
  }
}

function getStatusIcon(status: string): string {
  switch (status) {
    case 'Lunas': return 'mdi-check-circle';
    case 'Belum Dibayar': return 'mdi-clock-outline';
    case 'Kadaluarsa': return 'mdi-alert-circle';
    default: return 'mdi-help-circle';
  }
}

function getSnackbarIcon(color: string): string {
  switch (color) {
    case 'success': return 'mdi-check-circle';
    case 'error': return 'mdi-alert-circle';
    case 'warning': return 'mdi-alert';
    default: return 'mdi-information';
  }
}

function getDueDateClass(dueDateString: string | null | undefined): string {
  if (!dueDateString) return '';
  const dueDate = new Date(dueDateString);
  const today = new Date();
  const diffTime = dueDate.getTime() - today.getTime();
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
  
  if (diffDays < 0) return 'text-error';
  if (diffDays <= 3) return 'text-warning';
  return 'text-success';
}

function getDueDateLabel(dueDateString: string | null | undefined): string {
  if (!dueDateString) return '';
  const dueDate = new Date(dueDateString);
  const today = new Date();
  const diffTime = dueDate.getTime() - today.getTime();
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
  
  if (diffDays < 0) return `${Math.abs(diffDays)} hari terlambat`;
  if (diffDays === 0) return 'Jatuh tempo hari ini';
  if (diffDays === 1) return 'Jatuh tempo besok';
  if (diffDays <= 7) return `${diffDays} hari lagi`;
  return '';
}

function formatDate(dateString: string | null | undefined): string {
  if (!dateString) return 'N/A';
  return new Date(dateString).toLocaleDateString('id-ID', {
    day: '2-digit', month: 'long', year: 'numeric'
  });
}

function formatCurrency(value: number): string {
  return new Intl.NumberFormat('id-ID', { style: 'currency', currency: 'IDR', minimumFractionDigits: 0 }).format(value);
}


function openMarkAsPaidDialog(item: Invoice) {
  itemToMark.value = item;
  paymentMethod.value = 'Cash'; // Reset ke default
  dialogMarkAsPaid.value = true;
}

function closeMarkAsPaidDialog() {
  dialogMarkAsPaid.value = false;
  itemToMark.value = null;
}

async function confirmMarkAsPaid() {
  if (!itemToMark.value) return;
  
  markingAsPaid.value = true;
  try {
    await apiClient.post(`/invoices/${itemToMark.value.id}/mark-as-paid`, {
      metode_pembayaran: paymentMethod.value
    });
    showSnackbar('Invoice berhasil ditandai lunas', 'success');
    fetchInvoices(); // Refresh tabel
    closeMarkAsPaidDialog();
  } catch (error: any) {
    const detail = error.response?.data?.detail || 'Gagal menandai lunas.';
    showSnackbar(detail, 'error');
  } finally {
    markingAsPaid.value = false;
  }
}


</script>

<style scoped>
/* Main Header with gradient */
.invoice-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3);
}

.theme--dark .invoice-header {
  background: linear-gradient(135deg, #4338ca 0%, #6366f1 100%);
}

.icon-container {
  width: 56px;
  height: 56px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  backdrop-filter: blur(10px);
}

/* Stats Cards */
.stats-card {
  border-radius: 16px;
  transition: all 0.3s ease;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.stats-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.theme--dark .stats-card {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.stats-icon {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.stats-icon.success { background: rgba(76, 175, 80, 0.1); }
.stats-icon.warning { background: rgba(255, 152, 0, 0.1); }
.stats-icon.error { background: rgba(244, 67, 54, 0.1); }
.stats-icon.primary { background: rgba(103, 58, 183, 0.1); }

/* Invoice Table Card */
.invoice-table-card {
  border-radius: 20px;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.theme--dark .invoice-table-card {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.table-header {
  background: rgba(103, 58, 183, 0.05);
  border-bottom: 1px solid rgba(103, 58, 183, 0.1);
}

.theme--dark .table-header {
  background: rgba(103, 58, 183, 0.1);
  border-bottom: 1px solid rgba(103, 58, 183, 0.2);
}

/* Search Field */
.search-field :deep(.v-field) {
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.8);
}

.theme--dark .search-field :deep(.v-field) {
  background: rgba(255, 255, 255, 0.1);
}

/* Table Styling */
.invoice-table :deep(.v-data-table__td) {
  padding: 16px 12px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
}

.theme--dark .invoice-table :deep(.v-data-table__td) {
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}

.invoice-table :deep(.v-data-table__tr:hover) {
  background: rgba(103, 58, 183, 0.04) !important;
}

.theme--dark .invoice-table :deep(.v-data-table__tr:hover) {
  background: rgba(103, 58, 183, 0.1) !important;
}

/* Cell Styling */
.invoice-number-cell,
.customer-cell,
.amount-cell,
.due-date-cell {
  padding: 4px 0;
}

.status-chip {
  min-width: 100px;
  border-radius: 12px !important;
}

.action-buttons {
  display: flex;
  gap: 4px;
  justify-content: center;
}

.action-btn {
  border-radius: 8px;
  transition: all 0.2s ease;
}

.action-btn:hover {
  background: rgba(103, 58, 183, 0.1);
  transform: scale(1.05);
}

/* Dialog Styling */
.generate-dialog {
  border-radius: 20px;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.dialog-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.theme--dark .dialog-header {
  background: linear-gradient(135deg, #4338ca 0%, #6366f1 100%);
}

/* Custom Snackbar */
.custom-snackbar {
  border-radius: 12px;
}

/* Responsive */
@media (max-width: 960px) {
  .invoice-header {
    flex-direction: column;
    align-items: flex-start !important;
    gap: 16px;
  }
  
  .header-content {
    width: 100%;
  }
  
  .search-field {
    max-width: 100% !important;
  }
  
  .table-header .d-flex {
    flex-direction: column;
    gap: 16px;
  }
}

/* Dark mode transitions */
.v-theme--dark .invoice-header,
.v-theme--dark .stats-card,
.v-theme--dark .invoice-table-card,
.v-theme--dark .generate-dialog {
  transition: all 0.3s ease;
}
</style>