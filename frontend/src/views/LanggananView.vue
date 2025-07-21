<template>
  <v-container fluid class="pa-6">
    <div class="d-flex align-center mb-6">
      <div class="d-flex align-center">
        <v-avatar class="me-3" color="primary" size="40">
          <v-icon color="white">mdi-wifi-star</v-icon>
        </v-avatar>
        <div>
          <h1 class="text-h4 font-weight-bold text-primary">Manajemen Langganan</h1>
          <p class="text-subtitle-1 text-medium-emphasis mb-0">Kelola semua langganan pelanggan</p>
        </div>
      </div>
      <v-spacer></v-spacer>
      <v-btn 
        color="primary" 
        size="large"
        elevation="2"
        @click="openDialog()"
        prepend-icon="mdi-plus-circle"
        class="text-none"
      >
        Tambah Langganan
      </v-btn>
    </div>

    <v-card elevation="3" class="rounded-lg">
      <v-card-title class="d-flex align-center pa-6 bg-grey-lighten-5">
        <v-icon start icon="mdi-format-list-bulleted-square" color="primary"></v-icon>
        <span class="text-h6 font-weight-bold">Daftar Langganan</span>
        <v-spacer></v-spacer>
        <v-chip color="primary" variant="outlined" size="small">
          {{ langgananList.length }} langganan
        </v-chip>
      </v-card-title>
      
      <v-data-table
        :headers="headers"
        :items="langgananList"
        :loading="loading"
        item-value="id"
        class="elevation-0"
        :items-per-page="10"
      >
         <template v-slot:item.nomor="{ index }">
            {{ index + 1 }}
        </template>
        <template v-slot:item.pelanggan_id="{ item }">
          <div class="font-weight-bold">{{ getPelangganName(item.pelanggan_id) }}</div>
          <div class="text-caption text-medium-emphasis">ID: {{ item.pelanggan_id }}</div>
        </template>

        <template v-slot:item.paket_layanan_id="{ item }">
          <div class="font-weight-medium">{{ getPaketName(item.paket_layanan_id) }}</div>
        </template>
        
        <template v-slot:item.metode_pembayaran="{ item }">
          <v-chip
            size="small"
            variant="tonal"
            :color="item.metode_pembayaran === 'Prorate' ? 'blue' : 'grey-darken-1'"
          >
            {{ item.metode_pembayaran }}
          </v-chip>
        </template>

        <template v-slot:item.harga_awal="{ item }">
          <div class="font-weight-bold text-right">
            {{ formatCurrency(item.harga_awal) }}
          </div>
        </template>

        <template v-slot:item.status="{ item }">
          <v-chip
            size="small"
            :color="getStatusColor(item.status)"
            class="font-weight-bold"
          >
            {{ item.status }}
          </v-chip>
        </template>
        
        <template v-slot:item.tgl_jatuh_tempo="{ item }">
            {{ formatDate(item.tgl_jatuh_tempo) }}
        </template>

        <template v-slot:item.actions="{ item }">
          <div class="d-flex justify-center ga-2">
            <v-btn size="small" variant="tonal" color="primary" @click="openDialog(item)">
              <v-icon start size="16">mdi-pencil</v-icon> Edit
            </v-btn>
            <v-btn size="small" variant="tonal" color="error" @click="openDeleteDialog(item)">
              <v-icon start size="16">mdi-delete</v-icon> Hapus
            </v-btn>
          </div>
        </template>
      </v-data-table>
    </v-card>

    <!-- Enhanced Dialog Form -->
    <v-dialog v-model="dialog" max-width="800px" persistent scrollable>
      <v-card class="rounded-xl elevation-12">
        <!-- Enhanced Header with Gradient -->
        <v-card-title class="pa-0 position-relative overflow-hidden">
          <div class="form-header-gradient d-flex align-center pa-6 text-white">
            <div class="form-icon-container me-4">
              <v-avatar size="48" color="white" class="text-primary">
                <v-icon size="28">{{ editedIndex === -1 ? 'mdi-plus-circle' : 'mdi-pencil-circle' }}</v-icon>
              </v-avatar>
            </div>
            <div>
              <h2 class="text-h4 font-weight-bold mb-1">{{ formTitle }}</h2>
              <p class="text-subtitle-1 opacity-90 mb-0">
                {{ editedIndex === -1 ? 'Tambahkan langganan baru untuk pelanggan' : 'Perbarui informasi langganan pelanggan' }}
              </p>
            </div>
          </div>
          <div class="form-header-decoration"></div>
        </v-card-title>

        <v-card-text class="pa-0">
          <v-container class="pa-8">
            <!-- Step Indicator -->
            <div class="step-indicator mb-8">
              <div class="d-flex align-center justify-center mb-4">
                <div class="step-line"></div>
                <v-chip color="primary" variant="flat" size="small" class="mx-2 font-weight-bold">
                  <v-icon start size="16">mdi-form-select</v-icon>
                  Form Langganan
                </v-chip>
                <div class="step-line"></div>
              </div>
            </div>

            <v-form ref="formRef" v-model="formValid" lazy-validation>
              <v-row class="mb-4">
                <!-- Pelanggan Section -->
                <v-col cols="12">
                  <div class="form-section">
                    <div class="form-section-header mb-4">
                      <v-icon color="primary" class="me-2">mdi-account-group</v-icon>
                      <span class="text-h6 font-weight-bold text-primary">Informasi Pelanggan</span>
                    </div>
                    <v-card variant="tonal" color="blue-grey" class="pa-4 rounded-lg">
                      <v-autocomplete
                        v-model="editedItem.pelanggan_id"
                        :items="pelangganSelectList"
                        item-title="nama"
                        item-value="id"
                        label="Pilih Pelanggan"
                        placeholder="Ketik nama pelanggan untuk mencari..."
                        variant="solo-filled"
                        prepend-inner-icon="mdi-account-search"
                        :rules="[rules.required]"
                        :disabled="editedIndex !== -1"
                        class="enhanced-field"
                        clearable
                        hide-details="auto"
                      >
                        <template v-slot:item="{ props, item }">
                          <v-list-item v-bind="props" class="px-4">
                            <template v-slot:prepend>
                              <v-avatar color="primary" size="32">
                                <v-icon color="white" size="16">mdi-account</v-icon>
                              </v-avatar>
                            </template>
                            <v-list-item-title class="font-weight-medium">{{ item.raw.nama }}</v-list-item-title>
                            <v-list-item-subtitle>ID: {{ item.raw.id }}</v-list-item-subtitle>
                          </v-list-item>
                        </template>
                      </v-autocomplete>
                    </v-card>
                  </div>
                </v-col>

                <!-- Paket Layanan Section -->
                <v-col cols="12">
                  <div class="form-section">
                    <div class="form-section-header mb-4">
                      <v-icon color="primary" class="me-2">mdi-wifi</v-icon>
                      <span class="text-h6 font-weight-bold text-primary">Paket & Pembayaran</span>
                    </div>
                    <v-card variant="tonal" color="indigo" class="pa-4 rounded-lg">
                      <v-row>
                        <v-col cols="12">
                          <v-select
                            v-model="editedItem.paket_layanan_id"
                            :items="paketLayananSelectList"
                            :loading="paketLoading"
                            item-title="nama_paket" 
                            item-value="id"
                            label="Pilih Paket Layanan"
                            placeholder="Pilih paket yang sesuai"
                            variant="solo-filled"
                            prepend-inner-icon="mdi-wifi-star"
                            :rules="[rules.required]"
                            class="enhanced-field"
                            hide-details="auto"
                          >
                            <template v-slot:item="{ props, item }">
                              <v-list-item v-bind="props" class="px-4">
                                <template v-slot:prepend>
                                  <v-avatar color="indigo" size="32">
                                    <v-icon color="white" size="16">mdi-wifi</v-icon>
                                  </v-avatar>
                                </template>
                                <v-list-item-title class="font-weight-medium">{{ item.raw.nama_paket }}</v-list-item-title>
                                <v-list-item-subtitle>{{ item.raw.kecepatan }} Mbps - {{ formatCurrency(item.raw.harga) }}</v-list-item-subtitle>
                              </v-list-item>
                            </template>
                          </v-select>
                        </v-col>
                        
                        <v-col cols="12" md="6">
                          <v-select
                            v-model="editedItem.metode_pembayaran"
                            :items="[
                              { title: 'Otomatis (Bulanan)', value: 'Otomatis' },
                              { title: 'Prorate (Proporsional)', value: 'Prorate' }
                            ]"
                            label="Metode Pembayaran"
                            variant="solo-filled"
                            prepend-inner-icon="mdi-cash-multiple"
                            class="enhanced-field"
                            hide-details="auto"
                          ></v-select>
                        </v-col>
                        
                        <v-col cols="12" md="6">
                          <v-text-field
                            v-model="editedItem.harga_awal"
                            label="Total Harga Awal"
                            variant="solo-filled"
                            prepend-inner-icon="mdi-currency-usd"
                            prefix="Rp"
                            readonly
                            class="enhanced-field font-weight-bold price-field"
                            hide-details="auto"
                          ></v-text-field>
                        </v-col>
                      </v-row>
                    </v-card>
                  </div>
                </v-col>

                <!-- Status & Tanggal Section -->
                <v-col cols="12">
                  <div class="form-section">
                    <div class="form-section-header mb-4">
                      <v-icon color="primary" class="me-2">mdi-cog</v-icon>
                      <span class="text-h6 font-weight-bold text-primary">Status & Jadwal</span>
                    </div>
                    <v-card variant="tonal" color="green" class="pa-4 rounded-lg">
                      <v-row>
                        <v-col cols="12" sm="6">
                          <v-select
                            v-model="editedItem.status"
                            :items="[
                              { title: 'Aktif', value: 'Aktif' },
                              { title: 'Suspended', value: 'Suspended' },
                              { title: 'Berhenti', value: 'Berhenti' }
                            ]"
                            label="Status Langganan"
                            variant="solo-filled"
                            prepend-inner-icon="mdi-check-circle-outline"
                            :rules="[rules.required]"
                            class="enhanced-field"
                            hide-details="auto"
                          ></v-select>
                        </v-col>
                        
                        <v-col cols="12" sm="6">
                          <v-text-field
                            v-model="editedItem.tgl_jatuh_tempo"
                            label="Tanggal Jatuh Tempo"
                            type="date"
                            variant="solo-filled"
                            prepend-inner-icon="mdi-calendar-alert"
                            class="enhanced-field"
                            hide-details="auto"
                          ></v-text-field>
                        </v-col>
                      </v-row>
                    </v-card>
                  </div>
                </v-col>
              </v-row>
            </v-form>
          </v-container>
        </v-card-text>

        <!-- Enhanced Action Buttons -->
        <v-card-actions class="pa-0">
          <div class="action-footer w-100">
            <v-container class="pa-6">
              <v-row align="center" justify="end">
                <v-col cols="auto">
                  <v-btn 
                    variant="text" 
                    color="grey-darken-1" 
                    @click="closeDialog"
                    size="large"
                    class="me-4 text-none"
                  >
                    <v-icon start>mdi-close</v-icon>
                    Batal
                  </v-btn>
                </v-col>
                <v-col cols="auto">
                  <v-btn
                    color="primary"
                    variant="flat"
                    @click="saveLangganan"
                    :loading="saving"
                    :disabled="!isFormValid"
                    size="large"
                    class="text-none px-8 save-button"
                    elevation="2"
                  >
                    <v-icon start>{{ editedIndex === -1 ? 'mdi-plus' : 'mdi-content-save' }}</v-icon>
                    {{ editedIndex === -1 ? 'Tambah Langganan' : 'Simpan Perubahan' }}
                  </v-btn>
                </v-col>
              </v-row>
            </v-container>
          </div>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Enhanced Delete Dialog -->
    <v-dialog v-model="dialogDelete" max-width="500px">
      <v-card class="rounded-xl elevation-8">
        <div class="delete-header text-center pa-8">
          <v-avatar size="64" color="error" class="mb-4">
            <v-icon size="32" color="white">mdi-delete-alert</v-icon>
          </v-avatar>
          <h2 class="text-h5 font-weight-bold text-error mb-2">Konfirmasi Hapus</h2>
          <p class="text-body-1 text-medium-emphasis mb-0">
            Apakah Anda yakin ingin menghapus langganan untuk pelanggan 
            <strong class="text-primary">{{ getPelangganName(itemToDelete?.pelanggan_id) }}</strong>?
          </p>
          <v-alert variant="tonal" color="warning" class="mt-4 text-start">
            <v-icon start>mdi-alert-triangle</v-icon>
            Tindakan ini tidak dapat dibatalkan
          </v-alert>
        </div>
        
        <v-card-actions class="pa-6 pt-0">
          <v-spacer></v-spacer>
          <v-btn 
            variant="text" 
            color="grey-darken-1" 
            @click="closeDeleteDialog"
            class="text-none me-2"
          >
            Batal
          </v-btn>
          <v-btn 
            color="error" 
            variant="flat" 
            @click="confirmDelete" 
            :loading="deleting"
            class="text-none"
          >
            <v-icon start>mdi-delete</v-icon>
            Ya, Hapus
          </v-btn>
          <v-spacer></v-spacer>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue';
import apiClient from '@/services/api';

// --- Interfaces ---
interface Langganan {
  id: number;
  pelanggan_id: number;
  paket_layanan_id: number;
  status: string;
  tgl_jatuh_tempo: string | null;
  tgl_invoice_terakhir: string | null;
  metode_pembayaran: string;
  harga_awal: number | null;
}

interface PelangganSelectItem {
  id: number;
  nama: string;
}

interface PaketLayananSelectItem {
  id: number;
  nama_paket: string;
  kecepatan: number;
  harga: number;
}

// --- State ---
const langgananList = ref<Langganan[]>([]);
const pelangganSelectList = ref<PelangganSelectItem[]>([]);
const paketLayananSelectList = ref<PaketLayananSelectItem[]>([]);

const loading = ref(true);
const paketLoading = ref(true);
const saving = ref(false);
const deleting = ref(false);
const dialog = ref(false);
const dialogDelete = ref(false);
const editedIndex = ref(-1);
const formValid = ref(false);

const defaultItem: Partial<Langganan> = {
  pelanggan_id: undefined,
  paket_layanan_id: undefined,
  status: 'Aktif',
  tgl_jatuh_tempo: null,
  tgl_invoice_terakhir: null,
  metode_pembayaran: 'Otomatis',
  harga_awal: 0,
};
const editedItem = ref({ ...defaultItem });
const itemToDelete = ref<Langganan | null>(null);

// --- Validation Rules ---
const rules = {
  required: (value: any) => !!value || 'Field ini wajib diisi',
};

// --- Headers ---
const headers = [
  { title: 'No', key: 'nomor', sortable: false, width: '10px' }, 
  { title: 'Nama Pelanggan', key: 'pelanggan_id', sortable: true, width: '20%' },
  { title: 'Paket Layanan', key: 'paket_layanan_id' },
  { title: 'Metode Bayar', key: 'metode_pembayaran', align: 'center' },
  { title: 'Harga', key: 'harga_awal', align: 'end' },
  { title: 'Status', key: 'status', align: 'center' },
  { title: 'Jatuh Tempo', key: 'tgl_jatuh_tempo', align: 'center' },
  { title: 'Actions', key: 'actions', sortable: false, align: 'center', width: '180px' },
] as const;

// --- Computed Properties ---
const formTitle = computed(() => (editedIndex.value === -1 ? 'Tambah Langganan Baru' : 'Edit Langganan'));
const isFormValid = computed(() => !!(editedItem.value.pelanggan_id && editedItem.value.paket_layanan_id && editedItem.value.status && editedItem.value.harga_awal! > 0));

// --- Lifecycle ---
onMounted(() => {
  fetchLangganan();
  fetchPelangganForSelect();
  fetchPaketLayananForSelect();
});

// --- Logic Watcher ---
watch(
  () => [editedItem.value.metode_pembayaran, editedItem.value.paket_layanan_id],
  ([metode, paketId]) => {
    if (!dialog.value || !paketId) {
      // Jika form baru dibuka dan belum ada paket, set harga ke 0 atau nilai dari item yang diedit
      if(editedIndex.value === -1) {
        editedItem.value.harga_awal = 0;
      }
      return;
    }

    const selectedPaket = paketLayananSelectList.value.find(p => p.id === paketId);
    if (!selectedPaket) return;

    const fullPrice = selectedPaket.harga;
    const today = new Date();

    if (metode === 'Otomatis') {
      editedItem.value.harga_awal = fullPrice;
      const nextMonth = new Date(today.getFullYear(), today.getMonth() + 1, 1);
      editedItem.value.tgl_jatuh_tempo = nextMonth.toISOString().split('T')[0];
    } 
    else if (metode === 'Prorate') {
      const date = today.getDate();
      const lastDayOfMonth = new Date(today.getFullYear(), today.getMonth() + 1, 0).getDate();
      const remainingDays = lastDayOfMonth - date + 1;
      
      const proratedPriceBeforeTax = (fullPrice / lastDayOfMonth) * remainingDays;
      const proratedPriceWithTax = proratedPriceBeforeTax * 1.11;
      
      editedItem.value.harga_awal = Math.round(proratedPriceWithTax);
      editedItem.value.tgl_jatuh_tempo = today.toISOString().split('T')[0];
    }
  }
);

// --- API Methods ---
async function fetchLangganan() {
  loading.value = true;
  try {
    const response = await apiClient.get<Langganan[]>('/langganan/');
    langgananList.value = response.data;
  } catch (error) {
    console.error("Gagal mengambil data langganan:", error);
  } finally {
    loading.value = false;
  }
}

async function fetchPelangganForSelect() {
  try {
    const response = await apiClient.get<PelangganSelectItem[]>('/pelanggan/');
    pelangganSelectList.value = response.data;
  } catch (error) {
    console.error("Gagal mengambil data pelanggan untuk select:", error);
  }
}

async function fetchPaketLayananForSelect() {
  paketLoading.value = true;
  try {
    const response = await apiClient.get<PaketLayananSelectItem[]>('/paket_layanan/');
    paketLayananSelectList.value = response.data;
  } catch (error) {
    console.error("Gagal mengambil data paket layanan untuk select:", error);
    paketLayananSelectList.value = [];
  } finally {
    paketLoading.value = false;
  }
}

function openDialog(item?: Langganan) {
  editedIndex.value = item ? langgananList.value.findIndex(l => l.id === item.id) : -1;
  editedItem.value = item ? { ...item } : { ...defaultItem };
  dialog.value = true;
}

function closeDialog() {
  dialog.value = false;
  setTimeout(() => {
    editedItem.value = { ...defaultItem };
    editedIndex.value = -1;
  }, 300);
}

async function saveLangganan() {
  if (!isFormValid.value) return;
  
  saving.value = true;
  const dataToSave = { ...editedItem.value };

  try {
    if (editedIndex.value > -1) {
      await apiClient.patch(`/langganan/${dataToSave.id}`, {
        paket_layanan_id: dataToSave.paket_layanan_id,
        status: dataToSave.status,
        tgl_jatuh_tempo: dataToSave.tgl_jatuh_tempo,
        metode_pembayaran: dataToSave.metode_pembayaran,
        harga_awal: dataToSave.harga_awal,
      });
    } else {
      await apiClient.post('/langganan/', dataToSave);
    }
    fetchLangganan();
    closeDialog();
  } catch (error) { 
    console.error("Gagal menyimpan data langganan:", error);
  } finally {
    saving.value = false;
  }
}

function openDeleteDialog(item: Langganan) {
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
    await apiClient.delete(`/langganan/${itemToDelete.value.id}`);
    fetchLangganan();
    closeDeleteDialog();
  } catch (error) {
    console.error("Gagal menghapus langganan:", error);
  } finally {
    deleting.value = false;
  }
}

// --- Helper Methods ---
function getPelangganName(pelangganId: number | undefined): string {
  if (!pelangganId) return 'N/A';
  const pelanggan = pelangganSelectList.value.find(p => p.id === pelangganId);
  return pelanggan?.nama || `ID ${pelangganId}`;
}

function getPaketName(paketId: number | undefined): string {
    if (!paketId) return 'N/A';
    const paket = paketLayananSelectList.value.find(p => p.id === paketId);
    return paket?.nama_paket || `ID Paket ${paketId}`;
}

function getStatusColor(status: string): string {
  switch (status.toLowerCase()) {
    case 'aktif': return 'green';
    case 'non-aktif': return 'orange';
    case 'ditangguhkan': return 'amber';
    case 'berhenti': return 'red';
    default: return 'grey';
  }
}

function formatCurrency(value: number | null | undefined): string {
  if (value === null || value === undefined) return 'N/A';
  
  return new Intl.NumberFormat('id-ID', {
    style: 'currency',
    currency: 'IDR',
    minimumFractionDigits: 0,
  }).format(value);
}

function formatDate(dateString: string | Date | null | undefined): string {
  if (!dateString) return 'N/A';
  const date = new Date(dateString);
  if (isNaN(date.getTime())) return 'Invalid Date';
  return date.toLocaleDateString('id-ID', {
    year: 'numeric', month: 'long', day: 'numeric'
  });
}
</script>

<style scoped>
.v-data-table {
  --v-data-table-header-height: 60px;
}

/* Enhanced Form Styling */
.form-header-gradient {
  background: linear-gradient(135deg, #1976d2 0%, #1565c0 50%, #0d47a1 100%);
  position: relative;
  overflow: hidden;
}

.form-header-decoration {
  position: absolute;
  top: 0;
  right: -50px;
  width: 100px;
  height: 100%;
  background: rgba(255, 255, 255, 0.1);
  transform: skewX(-15deg);
}

.form-icon-container {
  position: relative;
  z-index: 2;
}

.step-indicator {
  position: relative;
}

.step-line {
  height: 2px;
  background: linear-gradient(90deg, transparent 0%, #1976d2 50%, transparent 100%);
  flex: 1;
  opacity: 0.3;
}

.form-section {
  margin-bottom: 2rem;
}

.form-section-header {
  display: flex;
  align-items: center;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid rgba(25, 118, 210, 0.1);
}

.enhanced-field {
  margin-bottom: 1rem;
}

.enhanced-field .v-field {
  background-color: rgba(255, 255, 255, 0.8) !important;
  border-radius: 12px !important;
  transition: all 0.3s ease;
}

.enhanced-field .v-field:hover {
  background-color: rgba(255, 255, 255, 0.95) !important;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.enhanced-field .v-field--focused {
  background-color: white !important;
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(25, 118, 210, 0.15);
}

.price-field .v-field {
  background: linear-gradient(135deg, #e8f5e8 0%, #f1f8e9 100%) !important;
  border: 2px solid rgba(76, 175, 80, 0.2) !important;
}

.action-footer {
  background: linear-gradient(135deg, #fafafa 0%, #f5f5f5 100%);
  border-top: 1px solid rgba(0, 0, 0, 0.08);
}

.save-button {
  background: linear-gradient(135deg, #1976d2 0%, #1565c0 100%) !important;
  box-shadow: 0 4px 12px rgba(25, 118, 210, 0.3) !important;
  transition: all 0.3s ease !important;
}

.save-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(25, 118, 210, 0.4) !important;
}

.delete-header {
  background: linear-gradient(135deg, #fafafa 0%, #f8f8f8 100%);
}

/* Custom scrollbar for dialog */
.v-overlay__content::-webkit-scrollbar {
  width: 6px;
}

.v-overlay__content::-webkit-scrollbar-track {
  background: rgba(0, 0, 0, 0.1);
  border-radius: 3px;
}

.v-overlay__content::-webkit-scrollbar-thumb {
  background: rgba(25, 118, 210, 0.3);
  border-radius: 3px;
}

.v-overlay__content::-webkit-scrollbar-thumb:hover {
  background: rgba(25, 118, 210, 0.5);
}

/* Smooth animations */
.v-dialog > .v-overlay__content {
  animation: dialogSlideIn 0.3s ease-out;
}

@keyframes dialogSlideIn {
  from {
    opacity: 0;
    transform: translateY(-50px) scale(0.9);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

/* Enhanced card styling */
.v-card.rounded-xl {
  border-radius: 16px !important;
  overflow: hidden;
}

/* Field focus effects */
.enhanced-field .v-input--focused .v-field__outline {
  border-color: #1976d2 !important;
  border-width: 2px !important;
}

/* Improved spacing and typography */
.form-section .v-card {
  transition: all 0.3s ease;
}

.form-section .v-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.08) !important;
}

/* Enhanced button styles */
.v-btn.text-none {
  text-transform: none !important;
  font-weight: 500 !important;
  letter-spacing: 0.5px;
}

/* Loading animation enhancement */
.v-btn--loading {
  pointer-events: none;
}

.v-btn--loading .v-btn__overlay {
  background: rgba(255, 255, 255, 0.1);
}

/* Responsive improvements */
@media (max-width: 768px) {
  .form-header-gradient {
    padding: 1.5rem !important;
  }
  
  .form-header-gradient h2 {
    font-size: 1.5rem !important;
  }
  
  .v-dialog > .v-overlay__content {
    margin: 1rem !important;
    max-width: calc(100vw - 2rem) !important;
  }
  
  .step-indicator {
    margin-bottom: 1.5rem !important;
  }
  
  .form-section {
    margin-bottom: 1.5rem !important;
  }
}
</style>