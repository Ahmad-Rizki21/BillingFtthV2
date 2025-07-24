<template>
  <v-container fluid class="pa-4 pa-md-6">
    <div class="header-card mb-6">
      <div class="d-flex flex-column flex-md-row align-center gap-4">
        <div class="d-flex align-center">
          <div class="header-avatar-wrapper">
            <v-avatar class="header-avatar" color="transparent" size="50">
              <v-icon color="white" size="28">mdi-account-group</v-icon>
            </v-avatar>
          </div>
          <div class="ml-4">
            <h1 class="header-title">Data Pelanggan</h1>
            <p class="header-subtitle">Kelola semua data pelanggan Anda dengan mudah</p>
          </div>
        </div>
        <v-spacer class="d-none d-md-block"></v-spacer>
        <div class="d-flex flex-column flex-sm-row gap-2 gap-sm-3">
          <v-btn variant="outlined" color="success" @click="dialogImport = true" prepend-icon="mdi-file-upload-outline" class="text-none" size="default">Import</v-btn>
          <v-btn variant="outlined" color="primary" @click="exportToCsv" :loading="exporting" prepend-icon="mdi-file-download-outline" class="text-none" size="default">Export</v-btn>
          <v-btn color="primary" @click="openDialog()" prepend-icon="mdi-account-plus" class="text-none" size="default" elevation="2">Tambah Pelanggan</v-btn>
        </div>
      </div>
    </div>

    <v-card class="data-table-card" elevation="0">
      <div class="card-header">
        <div class="d-flex align-center">
          <div class="header-icon-wrapper">
            <v-icon color="primary" size="20">mdi-format-list-bulleted-square</v-icon>
          </div>
          <span class="card-title ml-3">Daftar Pelanggan</span>
        </div>
        <v-chip color="primary" variant="tonal" size="small" class="count-chip">
          {{ pelangganList.length }} pelanggan
        </v-chip>
      </div>
      <div class="table-container">
        <v-data-table
          :headers="headers"
          :items="pelangganList"
          :loading="loading"
          item-value="id"
          class="elegant-table"
          :items-per-page="10"
          :items-per-page-options="[5, 10, 25, 50]"
        >
          <template v-slot:loading>
            <div class="d-flex justify-center align-center py-8">
              <v-progress-circular color="primary" indeterminate size="40"></v-progress-circular>
            </div>
          </template>
          <template v-slot:item.nama="{ item }">
            <div>
              <div class="font-weight-bold">{{ item.nama }}</div>
              <div class="text-caption text-grey">{{ item.email }}</div>
            </div>
          </template>
          <template v-slot:item.id_brand="{ item }">
            <v-chip size="small" :color="getBrandChipColor(getBrandName(item.id_brand))" variant="tonal">
              {{ getBrandName(item.id_brand) }}
            </v-chip>
          </template>
          <template v-slot:item.tgl_instalasi="{ item }">
            {{ formatDate(item.tgl_instalasi) }}
          </template>
          <template v-slot:item.actions="{ item }">
            <div class="d-flex gap-1">
              <v-btn size="small" variant="tonal" color="primary" @click="openDialog(item)" icon="mdi-pencil"></v-btn>
              <v-btn size="small" variant="tonal" color="error" @click="openDeleteDialog(item)" icon="mdi-delete"></v-btn>
            </div>
          </template>
          <template v-slot:no-data>
            <div class="d-flex flex-column align-center justify-center text-center py-8">
              <v-icon size="48" color="grey-lighten-1">mdi-account-off</v-icon>
              <div class="mt-2 text-grey">Belum ada data pelanggan</div>
              <v-btn color="primary" variant="tonal" @click="openDialog()" class="mt-4 text-none">Tambah Pelanggan</v-btn>
            </div>
          </template>
        </v-data-table>
      </div>
    </v-card>

    <v-dialog v-model="dialog" max-width="900px" persistent>
       <v-card>
        <div class="form-header" style="background-color: #1A237E; color: white; padding: 16px;">
          <v-icon class="mr-2">mdi-account-edit</v-icon>
          <span class="text-h6">{{ formTitle }}</span>
        </div>
        <v-card-text class="pa-4">
          <v-form ref="form" v-model="isFormValid">
            <v-stepper v-model="currentStep" flat>
              <v-stepper-header>
                <v-stepper-item title="Info Pribadi" :value="1" :complete="currentStep > 1" color="primary"></v-stepper-item>
                <v-divider></v-divider>
                <v-stepper-item title="Alamat & Layanan" :value="2" color="primary"></v-stepper-item>
              </v-stepper-header>
              <v-stepper-window>
                <v-stepper-window-item :value="1">
                  <v-row class="mt-2">
                    <v-col cols="12" md="6"><v-text-field v-model="editedItem.nama" label="Nama Lengkap" :rules="[rules.required]" variant="outlined"></v-text-field></v-col>
                    <v-col cols="12" md="6"><v-text-field v-model="editedItem.no_ktp" label="Nomor KTP" :rules="[rules.required, rules.ktp]" variant="outlined" counter="16"></v-text-field></v-col>
                    <v-col cols="12" md="6"><v-text-field v-model="editedItem.email" label="Email" :rules="[rules.required, rules.email]" variant="outlined"></v-text-field></v-col>
                    <v-col cols="12" md="6"><v-text-field v-model="editedItem.no_telp" label="Nomor Telepon" :rules="[rules.required, rules.phone]" variant="outlined"></v-text-field></v-col>
                  </v-row>
                </v-stepper-window-item>
                <v-stepper-window-item :value="2">
                  <v-row class="mt-2">
                    <v-col cols="12"><v-text-field v-model="editedItem.alamat" label="Alamat Utama" :rules="[rules.required]" variant="outlined"></v-text-field></v-col>
                    <v-col cols="12"><v-text-field v-model="editedItem.alamat_2" label="Alamat Tambahan (Opsional)" variant="outlined"></v-text-field></v-col>
                    <v-col cols="12" md="6"><v-text-field v-model="editedItem.blok" label="Blok" :rules="[rules.required]" variant="outlined"></v-text-field></v-col>
                    <v-col cols="12" md="6"><v-text-field v-model="editedItem.unit" label="Unit" :rules="[rules.required]" variant="outlined"></v-text-field></v-col>
                    <v-col cols="12" md="4"><v-text-field v-model="editedItem.tgl_instalasi" label="Tanggal Instalasi" type="date" variant="outlined"></v-text-field></v-col>
                    <v-col cols="12" md="4"><v-text-field v-model="editedItem.layanan" label="Layanan" variant="outlined"></v-text-field></v-col>
                    <v-col cols="12" md="4"><v-select v-model="editedItem.id_brand" :items="hargaLayananList" item-title="brand" item-value="id_brand" label="Brand Provider" variant="outlined"></v-select></v-col>
                  </v-row>
                </v-stepper-window-item>
              </v-stepper-window>
            </v-stepper>
          </v-form>
        </v-card-text>
        <v-card-actions class="pa-4">
          <v-btn v-if="currentStep > 1" @click="currentStep--" text>Kembali</v-btn>
          <v-spacer></v-spacer>
          <v-btn @click="closeDialog" text>Batal</v-btn>
          <v-btn v-if="currentStep < 2" @click="currentStep++" color="primary">Lanjut</v-btn>
          <v-btn v-else @click="savePelanggan" :loading="saving" :disabled="!isFormValid" color="primary" variant="flat">Simpan</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-dialog v-model="dialogDelete" max-width="450px">
      <v-card>
        <div class="d-flex align-center pa-4" style="background-color: #D32F2F; color: white;">
          <v-icon class="mr-2">mdi-delete-alert</v-icon>
          <span class="text-h6">Konfirmasi Hapus</span>
        </div>
        <v-card-text class="text-center pa-6">
          <v-icon size="64" color="warning">mdi-alert-circle-outline</v-icon>
          <p class="mt-4">Anda yakin ingin menghapus pelanggan <strong>{{ itemToDelete?.nama }}</strong>?</p>
          <p class="text-caption text-grey">Tindakan ini tidak dapat dibatalkan!</p>
        </v-card-text>
        <v-card-actions class="pa-4">
          <v-spacer></v-spacer>
          <v-btn @click="closeDeleteDialog" text>Batal</v-btn>
          <v-btn @click="confirmDelete" :loading="deleting" color="error" variant="flat">Ya, Hapus</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-dialog v-model="dialogImport" max-width="700px" persistent>
      <v-card class="import-card">
        <div class="import-header" style="display: flex; align-items: center; background-color: #00695C; color: white; padding: 12px 16px;">
          <v-icon class="mr-3">mdi-upload</v-icon>
          <span class="import-title" style="font-size: 1.1rem; font-weight: 500;">Import Pelanggan dari CSV</span>
          <v-spacer></v-spacer>
          <v-btn icon variant="text" @click="closeImportDialog"><v-icon color="white">mdi-close</v-icon></v-btn>
        </div>
        <v-card-text class="pa-6">
          <v-sheet border rounded class="pa-4 mb-5">
            <div class="d-flex align-center">
              <v-avatar color="green-lighten-4" size="50"><v-icon color="success">mdi-file-document-outline</v-icon></v-avatar>
              <div class="ml-4">
                <div class="font-weight-bold">Gunakan Template Kami</div>
                <p class="text-caption text-grey-darken-1 mb-0">Unduh template CSV untuk memastikan format data sesuai.</p>
              </div>
              <v-spacer></v-spacer>
              <v-btn color="success" variant="flat" @click="downloadCsvTemplate" :loading="downloadingTemplate" prepend-icon="mdi-download" class="text-none">Unduh</v-btn>
            </div>
          </v-sheet>
          <div class="font-weight-bold mb-2">Unggah File Anda</div>
          <v-file-input 
  :model-value="fileToImport"
  @update:model-value="handleFileSelection"
  label="Pilih file .csv" 
  accept=".csv" 
  variant="outlined" 
  prepend-icon="" 
  prepend-inner-icon="mdi-paperclip" 
  show-size 
  clearable 
  hide-details="auto">
</v-file-input>
          <v-expand-transition>
            <div v-if="importErrors.length > 0" class="mt-4">
              <v-alert type="error" variant="tonal" prominent border="start">
                <div class="d-flex justify-space-between align-center mb-2">
                  <h6 class="text-h6">Impor Gagal</h6>
                  <v-chip color="error" size="small">{{ importErrors.length }} Kesalahan</v-chip>
                </div>
                <p class="mb-3">Mohon perbaiki kesalahan berikut di file CSV Anda dan coba lagi.</p>
                <v-divider class="mb-3"></v-divider>
                <div class="error-list">
                  <div v-for="(error, i) in importErrors" :key="i" class="error-item">
                    <v-icon size="x-small" color="error" class="mr-2">mdi-alert-circle</v-icon>
                    <span>{{ error }}</span>
                  </div>
                </div>
              </v-alert>
            </div>
          </v-expand-transition>
        </v-card-text>
        <v-divider></v-divider>
        <v-card-actions class="pa-4">
          <v-spacer></v-spacer>
          <v-btn variant="text" @click="closeImportDialog">Batal</v-btn>
          <v-btn color="success" variant="flat" @click="importFromCsv" :loading="importing" :disabled="fileToImport.length === 0" prepend-icon="mdi-upload" class="text-none">Impor Sekarang</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-snackbar v-model="snackbar.show" :color="snackbar.color" :timeout="4000" location="top right">
      {{ snackbar.text }}
    </v-snackbar>
  </v-container>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import apiClient from '@/services/api';
import type { Pelanggan as BasePelanggan } from '@/interfaces/pelanggan';

// --- INTERFACES ---
interface Pelanggan extends BasePelanggan {
  alamat_2?: string | null;
  id_brand?: string | null;
}
interface HargaLayanan {
  id_brand: string;
  brand: string;
}

// --- STATE MANAGEMENT ---
const pelangganList = ref<Pelanggan[]>([]);
const hargaLayananList = ref<HargaLayanan[]>([]);
const loading = ref(true);
const saving = ref(false);
const deleting = ref(false);
const dialog = ref(false);
const dialogDelete = ref(false);
const editedIndex = ref(-1);
const currentStep = ref(1);
const isFormValid = ref(false);

const dialogImport = ref(false);
const importing = ref(false);
const exporting = ref(false);
const downloadingTemplate = ref(false);
const fileToImport = ref<File[]>([]);
const importErrors = ref<string[]>([]);

const defaultItem: Partial<Pelanggan> = { 
  id: undefined, 
  nama: '', 
  no_ktp: '', 
  email: '', 
  no_telp: '', 
  layanan: '',
  alamat: '', 
  blok: '', 
  unit: '', 
  tgl_instalasi: new Date().toISOString().split('T')[0], // Format to YYYY-MM-DD
  alamat_2: '',
  id_brand: null
};
const editedItem = ref<Partial<Pelanggan>>({ ...defaultItem });
const itemToDelete = ref<Pelanggan | null>(null);
const snackbar = ref({ show: false, text: '', color: 'success' as 'success' | 'error' | 'warning' });

// --- ATURAN VALIDASI ---
const rules = {
  required: (value: any) => !!value || 'Field ini wajib diisi',
  email: (value: string) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value) || 'Format email tidak valid',
  phone: (value: string) => /^[\+]?[0-9\s\-\(\)]{10,}$/.test(value) || 'Format nomor telepon tidak valid',
  ktp: (value: string) => (value && value.length === 16 && /^[0-9]+$/.test(value)) || 'Nomor KTP harus 16 digit angka',
};

// --- HEADER TABEL ---
const headers = [
  { title: 'Pelanggan', key: 'nama', sortable: true },
  { title: 'Alamat', key: 'alamat', sortable: false },
  { title: 'No. Telepon', key: 'no_telp', sortable: false },
  { title: 'Layanan', key: 'layanan', sortable: false },
  { title: 'Brand', key: 'id_brand', sortable: true },
  { title: 'Tgl Instalasi', key: 'tgl_instalasi', align: 'center', sortable: true },
  { title: 'Aksi', key: 'actions', sortable: false, align: 'center', width: '120px' },
] as const;

// --- COMPUTED PROPERTIES ---
const formTitle = computed(() => editedIndex.value === -1 ? 'Tambah Pelanggan Baru' : 'Edit Pelanggan');

// --- LIFECYCLE HOOK ---
onMounted(() => {
  fetchPelanggan();
  fetchHargaLayanan();
});

// --- METODE CRUD ---
async function fetchPelanggan() {
  loading.value = true;
  try {
    const response = await apiClient.get('/pelanggan/');
    pelangganList.value = response.data;
  } catch (error) { 
    console.error("Gagal mengambil data pelanggan:", error);
    showSnackbar('Gagal mengambil data pelanggan', 'error');
  } finally { 
    loading.value = false; 
  }
}

function handleFileSelection(newFiles: File | File[]) {
  importErrors.value = []; // Bersihkan error lama

  // Cek apakah data yang masuk adalah sebuah array
  if (Array.isArray(newFiles)) {
    // Jika ya, langsung gunakan
    fileToImport.value = newFiles;
  } else if (newFiles) {
    // Jika bukan array (artinya hanya 1 file), bungkus menjadi array
    fileToImport.value = [newFiles];
  } else {
    // Jika kosong (null atau undefined, misal saat file dihapus), jadikan array kosong
    fileToImport.value = [];
  }
  
  console.log('File state diperbarui:', fileToImport.value);
}


async function fetchHargaLayanan() {
  try {
    const response = await apiClient.get('/harga_layanan');
    hargaLayananList.value = response.data;
  } catch (error) { 
    console.error("Gagal mengambil data harga layanan:", error);
  }
}

function openDialog(item?: Pelanggan) {
  editedIndex.value = item ? pelangganList.value.findIndex(p => p.id === item.id) : -1;
  const targetItem = item ? { ...item } : { ...defaultItem };
  // Ensure date is in YYYY-MM-DD format for the input
  if (targetItem.tgl_instalasi) {
    targetItem.tgl_instalasi = new Date(targetItem.tgl_instalasi).toISOString().split('T')[0];
  }
  editedItem.value = targetItem;
  currentStep.value = 1;
  dialog.value = true;
}

function closeDialog() {
  dialog.value = false;
  editedItem.value = { ...defaultItem };
  editedIndex.value = -1;
  currentStep.value = 1;
}

async function savePelanggan() {
  if (!isFormValid.value) return;
  saving.value = true;
  try {
    if (editedIndex.value > -1) {
      await apiClient.patch(`/pelanggan/${editedItem.value.id}`, editedItem.value);
      showSnackbar('Data pelanggan berhasil diperbarui', 'success');
    } else {
      await apiClient.post('/pelanggan/', editedItem.value);
      showSnackbar('Data pelanggan berhasil ditambahkan', 'success');
    }
    await fetchPelanggan();
    closeDialog();
  } catch (error) {
    console.error("Gagal menyimpan data pelanggan:", error);
    showSnackbar('Gagal menyimpan data pelanggan', 'error');
  } finally {
    saving.value = false;
  }
}

function openDeleteDialog(item: Pelanggan) {
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
    await apiClient.delete(`/pelanggan/${itemToDelete.value.id}`);
    await fetchPelanggan();
    showSnackbar('Data pelanggan berhasil dihapus', 'success');
    closeDeleteDialog();
  } catch (error) {
    console.error("Gagal menghapus data pelanggan:", error);
    showSnackbar('Gagal menghapus data pelanggan', 'error');
  } finally {
    deleting.value = false;
  }
}

// --- METODE IMPORT / EXPORT ---
function closeImportDialog() {
  dialogImport.value = false;
  importing.value = false;
  fileToImport.value = [];
  importErrors.value = [];
}

async function downloadCsvTemplate() {
  downloadingTemplate.value = true;
  try {
    const response = await apiClient.get('/pelanggan/template/csv', { responseType: 'blob' });
    downloadFile(response.data, 'template_import_pelanggan.csv');
  } catch (error) {
    console.error("Gagal mengunduh template:", error);
    showSnackbar('Gagal mengunduh template.', 'error');
  } finally {
    downloadingTemplate.value = false;
  }
}

async function exportToCsv() {
  exporting.value = true;
  try {
    const response = await apiClient.get('/pelanggan/export/csv', { responseType: 'blob' });
    const date = new Date().toISOString().split('T')[0];
    downloadFile(response.data, `export_pelanggan_${date}.csv`);
  } catch (error) {
    console.error("Gagal mengekspor data:", error);
    showSnackbar('Tidak ada data untuk diekspor atau terjadi kesalahan.', 'error');
  } finally {
    exporting.value = false;
  }
}

async function importFromCsv() {
  // 1. Ambil file dari array terlebih dahulu
  const file = fileToImport.value[0]; 

  // 2. Lakukan pengecekan yang lebih kuat pada file itu sendiri
  if (!file) {
    showSnackbar('Silakan pilih file CSV terlebih dahulu.', 'warning');
    return; // Langsung hentikan fungsi jika tidak ada file
  }

  importing.value = true;
  importErrors.value = [];
  
  const formData = new FormData();
  // 3. Sekarang aman untuk menambahkan file ke FormData
  formData.append('file', file); 
  
  try {
    const response = await apiClient.post('/pelanggan/import', formData);
    
    showSnackbar(response.data.message, 'success');
    await fetchPelanggan();
    closeImportDialog();
  } catch (error: any) {
    console.error("Gagal mengimpor data:", error);
    if (error.response?.data) {
      const errors = error.response.data.errors;
      // Cek jika ada array 'errors', jika tidak, buat array dari pesan 'detail'
      if (Array.isArray(errors) && errors.length > 0) {
        importErrors.value = errors;
      } else {
        // Jika tidak ada array 'errors', tampilkan pesan utama sebagai satu-satunya error
        const detailMsg = error.response.data.detail;
        if (typeof detailMsg === 'string') {
          importErrors.value = [detailMsg];
        } else if (Array.isArray(detailMsg)) {
          // Menangani kasus jika 'detail' adalah array objek seperti pada error Anda
          importErrors.value = detailMsg.map(err => err.msg || 'Error tidak diketahui');
        } else {
          importErrors.value = ["Terjadi kesalahan yang tidak diketahui."];
        }
      }
    } else {
      // Fallback untuk error jaringan atau error tak terduga lainnya
      importErrors.value = ["Tidak dapat terhubung ke server atau terjadi error."];
    }
  } finally {
    importing.value = false;
  }
}

// --- FUNGSI BANTU (HELPERS) ---
function downloadFile(blobData: any, filename: string) {
  const url = window.URL.createObjectURL(new Blob([blobData]));
  const link = document.createElement('a');
  link.href = url;
  link.setAttribute('download', filename);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  window.URL.revokeObjectURL(url);
}

function getBrandName(id_brand: string | null | undefined): string {
  if (!id_brand) return 'N/A';
  const brand = hargaLayananList.value.find(h => h.id_brand === id_brand);
  return brand ? brand.brand : 'Unknown';
}

function getBrandChipColor(brandName: string): string {
  if (brandName.includes('Jakinet')) return 'blue';
  if (brandName.includes('Jelantik')) return 'purple';
  return 'grey';
}

function formatDate(date: string | Date | null): string {
  if (!date) return '-';
  const d = new Date(date);
  if (isNaN(d.getTime())) return '-';
  // Add timezone offset to prevent date from shifting
  const offset = d.getTimezoneOffset();
  const correctedDate = new Date(d.getTime() + (offset * 60 * 1000));
  return correctedDate.toLocaleDateString('id-ID', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  });
}

function showSnackbar(text: string, color: 'success' | 'error' | 'warning') {
  snackbar.value = { show: true, text, color };
}
</script>

<style scoped>
/* Header Styles */
.header-card {
  background: linear-gradient(135deg, #383f5a 0%, #764ba2 100%);
  border-radius: 16px;
  padding: 24px;
  color: white;
  box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3);
}

.header-avatar-wrapper {
  background: rgba(255, 255, 255, 0.2);
  border-radius: 50%;
  padding: 8px;
  backdrop-filter: blur(10px);
}

.header-avatar {
  background: rgba(255, 255, 255, 0.1) !important;
  backdrop-filter: blur(5px);
}

.header-title {
  font-size: 2rem;
  font-weight: 700;
  margin: 0;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.header-subtitle {
  font-size: 1rem;
  opacity: 0.9;
  margin: 4px 0 0;
  font-weight: 400;
}

.action-btn, .primary-btn {
  border-radius: 12px;
  font-weight: 600;
  text-transform: none;
  gap: 12px;
  margin-right: 12px;
  padding: 10 30px;
  height: 55px;
  transition: all 0.3s ease;
}

.action-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
}

.primary-btn {
  background: linear-gradient(135deg, #97aafe 0%, #764ba2 100%) !important;
  color: white !important;
}

.primary-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(164, 177, 235, 0.4);
}

/* Data Table Card */
.data-table-card {
  border-radius: 16px;
  overflow: hidden;
  border: 1px solid rgba(0, 0, 0, 0.05);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

.card-header {
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  padding: 20px 24px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-icon-wrapper {
  background: rgba(102, 126, 234, 0.1);
  border-radius: 8px;
  padding: 8px;
}

.card-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1e293b;
}

.count-chip {
  font-weight: 600;
}

.table-container {
  background: white;
}

.elegant-table {
  background: transparent !important;
}

.elegant-table ::v-deep(.v-data-table__wrapper) {
  border-radius: 0;
}

.elegant-table ::v-deep(th) {
  background: #f8fafc !important;
  color: #64748b !important;
  font-weight: 600 !important;
  border-bottom: 2px solid #e2e8f0 !important;
  padding: 16px !important;
}

.elegant-table ::v-deep(td) {
  padding: 16px !important;
  border-bottom: 1px solid #f1f5f9 !important;
}

.elegant-table ::v-deep(tr:hover) {
  background: #f8fafc !important;
}

.loading-wrapper {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 40px;
}

.customer-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.customer-name {
  font-weight: 600;
  color: #1e293b;
}

.customer-email {
  font-size: 0.875rem;
  color: #64748b;
}

.brand-chip {
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.brand-chip-indihome {
  background-color: #fef3c7 !important;
  color: #92400e !important;
}

.brand-chip-firstmedia {
  background-color: #dbeafe !important;
  color: #1e40af !important;
}

.brand-chip-biznet {
  background-color: #dcfce7 !important;
  color: #166534 !important;
}

.brand-chip-mncplay {
  background-color: #fce7f3 !important;
  color: #be185d !important;
}

.brand-chip-cbn {
  background-color: #f3e8ff !important;
  color: #7c3aed !important;
}

.brand-chip-myrepublic {
  background-color: #fed7d7 !important;
  color: #c53030 !important;
}

.brand-chip-default {
  background-color: #f1f5f9 !important;
  color: #64748b !important;
}

.date-cell {
  font-weight: 500;
  color: #475569;
}

.action-buttons {
  display: flex;
  gap: 8px;
}

.action-btn-small {
  min-width: 36px !important;
  width: 36px;
  height: 36px;
  border-radius: 8px;
}

.no-data-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 60px 20px;
  text-align: center;
}

.no-data-text {
  font-size: 1.125rem;
  color: #64748b;
  margin-top: 16px;
  font-weight: 500;
}

/* Form Dialog */
.form-dialog ::v-deep(.v-overlay__content) {
  margin: 24px;
  max-height: calc(100vh - 48px);
  overflow-y: auto;
}

.form-card {
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 25px 50px rgba(0, 0, 0, 0.15);
}

.form-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 24px;
  color: white;
}

.form-header-content {
  display: flex;
  align-items: center;
}

.form-title {
  font-size: 1.5rem;
  font-weight: 600;
}

.form-content {
  padding: 32px !important;
  background: #fafbfc;
}

.elegant-stepper {
  background: transparent !important;
  box-shadow: none !important;
}

.stepper-header {
  background: white;
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 24px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}

.stepper-divider {
  margin: 0 16px;
}

.stepper-content {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}

.step-content {
  padding: 0 !important;
}

.step-header {
  margin-bottom: 24px;
  text-align: center;
}

.step-header h3 {
  color: #1e293b;
  margin-bottom: 8px;
  font-weight: 600;
}

.step-header p {
  color: #64748b;
  margin: 0;
}

.form-row {
  margin: 0 -12px;
}

.input-group {
  margin-bottom: 20px;
}

.input-label {
  display: flex;
  align-items: center;
  font-weight: 600;
  color: #374151;
  margin-bottom: 8px;
  font-size: 0.875rem;
}

.elegant-input ::v-deep(.v-field) {
  border-radius: 12px;
  background: #f8fafc;
  border: 2px solid #e2e8f0;
  transition: all 0.3s ease;
}

.elegant-input ::v-deep(.v-field:hover) {
  border-color: #cbd5e1;
  background: white;
}

.elegant-input ::v-deep(.v-field--focused) {
  background: white;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.elegant-input ::v-deep(.v-field__input) {
  padding: 12px 16px;
  font-size: 0.95rem;
}

.form-actions {
  padding: 24px 32px !important;
  background: #f8fafc;
  border-top: 1px solid #e2e8f0;
}

.nav-btn, .save-btn {
  border-radius: 12px;
  font-weight: 600;
  padding: 0 24px;
  height: 44px;
  text-transform: none;
}

.save-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
  color: white !important;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
}

.save-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
}

/* Delete Dialog */
.delete-dialog ::v-deep(.v-overlay__content) {
  margin: 24px;
}

.delete-card {
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
}

.delete-header {
  background: linear-gradient(135deg, #dc2626 0%, #b91c1c 100%);
  padding: 20px 24px;
  color: white;
  display: flex;
  align-items: center;
}

.delete-title {
  font-size: 1.25rem;
  font-weight: 600;
  margin-left: 12px;
}

.delete-content {
  padding: 32px 24px !important;
}

.delete-message {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}

.delete-text {
  font-size: 1.1rem;
  color: #374151;
  margin-bottom: 8px;
}

.customer-name-delete {
  color: #dc2626;
}

.delete-warning {
  font-size: 0.9rem;
  color: #6b7280;
  font-style: italic;
}

.delete-actions {
  padding: 16px 24px !important;
  background: #f9fafb;
}

.cancel-btn, .delete-btn {
  border-radius: 10px;
  font-weight: 600;
  text-transform: none;
  padding: 0 20px;
}

.delete-btn {
  background: linear-gradient(135deg, #dc2626 0%, #b91c1c 100%) !important;
  color: white !important;
}

/* Import Dialog */
.import-dialog ::v-deep(.v-overlay__content) {
  margin: 24px;
}

.import-card {
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
}

.import-header {
  background: linear-gradient(135deg, #059669 0%, #047857 100%);
  padding: 20px 24px;
  color: white;
  display: flex;
  align-items: center;
}

.import-title {
  font-size: 1.25rem;
  font-weight: 600;
}

.import-content {
  padding: 32px 24px !important;
}

.alert-content {
  line-height: 1.6;
}

.alert-title {
  font-weight: 600;
  margin-bottom: 8px;
}

.alert-text {
  font-size: 0.9rem;
  opacity: 0.9;
}

.template-card {
  border: 2px dashed #d1d5db;
  transition: all 0.3s ease;
}

.template-card:hover {
  border-color: #059669;
  background: #f0fdf4;
}

.template-icon {
  background: #dcfce7;
  border-radius: 50%;
  padding: 12px;
}

.template-title {
  font-weight: 600;
  color: #374151;
  margin-bottom: 4px;
}

.template-subtitle {
  font-size: 0.875rem;
  color: #6b7280;
}

.template-btn {
  border-radius: 10px;
  font-weight: 600;
  text-transform: none;
}

.file-input ::v-deep(.v-field) {
  border: 2px dashed #d1d5db !important;
  background: #f9fafb;
  border-radius: 12px;
}

.file-input ::v-deep(.v-field:hover) {
  border-color: #059669 !important;
  background: #f0fdf4;
}

.import-actions {
  padding: 16px 24px !important;
  background: #f9fafb;
}

.import-btn {
  background: linear-gradient(135deg, #059669 0%, #047857 100%) !important;
  color: white !important;
  border-radius: 10px;
  font-weight: 600;
  text-transform: none;
  padding: 0 20px;
}

/* Enhanced Snackbar */
.enhanced-snackbar ::v-deep(.v-snackbar__wrapper) {
  border-radius: 12px;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
  backdrop-filter: blur(10px);
}

/* Responsive Design */
@media (max-width: 768px) {
  .header-card {
    padding: 16px;
  }
  
  .header-title {
    font-size: 1.5rem;
  }
  
  .card-header {
    padding: 16px;
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  
  .form-content {
    padding: 24px 16px !important;
  }
  
  .stepper-content {
    padding: 16px;
  }
  
  .form-actions {
    padding: 16px !important;
  }
}

@media (max-width: 480px) {
  .action-buttons {
    flex-direction: column;
    gap: 4px;
  }
  
  .action-btn-small {
    width: 100%;
    min-width: auto !important;
  }
}
</style>