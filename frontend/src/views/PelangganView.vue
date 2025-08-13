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
        <div class="d-flex flex-column flex-sm-row gap-3">
          <v-btn
            color="success"
            @click="dialogImport = true"
            prepend-icon="mdi-file-upload-outline"
            class="action-btn text-none"
            size="large"
          >
            Import Data
          </v-btn>
          <v-btn
            color="primary"
            @click="exportToCsv"
            :loading="exporting"
            prepend-icon="mdi-file-download-outline"
            class="action-btn text-none"
            size="large"
          >
            Export Data
          </v-btn>
          <v-btn 
            color="primary" 
            @click="openDialog()" 
            prepend-icon="mdi-account-plus" 
            class="primary-btn text-none" 
            size="large" 
            elevation="3"
          >
            Tambah Pelanggan
          </v-btn>
        </div>
      </div>
    </div>

    <v-card class="filter-card mb-6" elevation="0">
      <div class="d-flex flex-wrap align-center gap-4 pa-4">
        <v-text-field
          v-model="searchQuery"
          label="Cari Pelanggan (Nama, Email, No. Telp)"
          prepend-inner-icon="mdi-magnify"
          variant="outlined"
          density="comfortable"
          hide-details
          class="flex-grow-1"
          style="min-width: 300px;"
        ></v-text-field>

        <v-select
          v-model="selectedAlamat"
          :items="alamatOptions"
          label="Filter Alamat"
          variant="outlined"
          density="comfortable"
          hide-details
          clearable
          class="flex-grow-1"
          style="min-width: 200px;"
        ></v-select>

        <v-select
          v-model="selectedBrand"
          :items="hargaLayananList"
          item-title="brand"
          item-value="id_brand"
          label="Filter Brand"
          variant="outlined"
          density="comfortable"
          hide-details
          clearable
          class="flex-grow-1"
          style="min-width: 200px;"
        ></v-select>
        
        <v-btn
            variant="text"
            @click="resetFilters"
            class="text-none"
        >
          Reset Filter
        </v-btn>
      </div>
    </v-card>

    <v-card class="data-table-card" elevation="0">
      <div class="card-header">
        <div class="d-flex align-center">
          <div class="header-icon-wrapper">
            <v-icon color="primary" size="20">mdi-format-list-bulleted-square</v-icon>
          </div>
          <span class="card-title ml-3">Daftar Pelanggan</span>
        </div>
        <v-chip color="primary" variant="tonal" size="default" class="count-chip">
          <v-icon start size="small">mdi-account-multiple</v-icon>
          {{ pelangganList.length }} pelanggan
        </v-chip>
      </div>
      <v-expand-transition>
        <div v-if="selectedPelanggan.length > 0" class="selection-toolbar">
          <span class="font-weight-bold text-primary">{{ selectedPelanggan.length }} pelanggan terpilih</span>
          <v-spacer></v-spacer>
         <v-btn 
            color="error" 
            variant="tonal" 
            prepend-icon="mdi-delete-sweep"
            @click="deleteSelectedPelanggan"
          >
            Hapus Terpilih
          </v-btn>
        </div>
      </v-expand-transition>
      <div class="table-container">
        <v-data-table
  v-model="selectedPelanggan"
  :headers="headers"
  :items="pelangganList"
  :loading="loading"
  item-value="id"
  class="elegant-table"
  :items-per-page="10"
  :items-per-page-options="[5, 10, 25, 50]"
  hover
  show-select
  return-object
>
        
          <template v-slot:loading>
            <div class="d-flex justify-center align-center py-12">
              <div class="text-center">
                <v-progress-circular color="primary" indeterminate size="48"></v-progress-circular>
                <p class="mt-4 text-medium-emphasis">Memuat data pelanggan...</p>
              </div>
            </div>
          </template>
          
          <template v-slot:item.nama="{ item }">
            <div class="customer-info">
              <div class="customer-name">{{ item.nama }}</div>
              <div class="customer-email">{{ item.email }}</div>
            </div>
          </template>
          
          <template v-slot:item.id_brand="{ item }">
            <v-chip 
              size="default" 
              :color="getBrandChipColor(getBrandName(item.id_brand))" 
              variant="tonal"
              class="brand-chip"
            >
              <v-icon start size="small">mdi-wifi</v-icon>
              {{ getBrandName(item.id_brand) }}
            </v-chip>
          </template>
          
          <template v-slot:item.tgl_instalasi="{ item }">
            <div class="date-cell">
              <v-icon size="small" class="mr-1">mdi-calendar</v-icon>
              {{ formatDate(item.tgl_instalasi) }}
            </div>
          </template>
          
          <template v-slot:item.actions="{ item }">
            <div class="action-buttons">
              <v-btn 
                size="small" 
                variant="tonal" 
                color="primary" 
                @click="openDialog(item)" 
                icon="mdi-pencil"
                class="action-btn-small"
              ></v-btn>
              <v-btn 
                size="small" 
                variant="tonal" 
                color="error" 
                @click="openDeleteDialog(item)" 
                icon="mdi-delete"
                class="action-btn-small"
              ></v-btn>
            </div>
          </template>
          
          <template v-slot:no-data>
            <div class="no-data-wrapper">
              <v-icon size="64" color="surface-variant">mdi-account-off</v-icon>
              <div class="no-data-text">Belum ada data pelanggan</div>
              <p class="text-medium-emphasis mt-2">Mulai dengan menambahkan pelanggan pertama Anda</p>
              <v-btn 
                color="primary" 
                variant="elevated" 
                @click="openDialog()" 
                class="mt-6 text-none"
                prepend-icon="mdi-account-plus"
              >
                Tambah Pelanggan
              </v-btn>
            </div>
          </template>
        </v-data-table>
      </div>
    </v-card>

    <v-dialog v-model="dialog" max-width="1000px" persistent class="form-dialog">
      <v-card class="form-card">
        <div class="form-header">
          <div class="form-header-content">
            <v-icon class="mr-3" size="24">mdi-account-edit</v-icon>
            <span class="form-title">{{ formTitle }}</span>
          </div>
        </div>
        
        <v-card-text class="form-content">
          <v-form ref="form" v-model="isFormValid">
            <v-stepper v-model="currentStep" flat class="elegant-stepper">
              <v-stepper-header class="stepper-header">
                <v-stepper-item 
                  title="Info Pribadi" 
                  :value="1" 
                  :complete="currentStep > 1" 
                  color="primary"
                ></v-stepper-item>
                <v-divider class="stepper-divider"></v-divider>
                <v-stepper-item 
                  title="Alamat & Layanan" 
                  :value="2" 
                  color="primary"
                ></v-stepper-item>
              </v-stepper-header>
              
              <v-stepper-window class="stepper-content">
                <v-stepper-window-item :value="1" class="step-content">
                  <div class="step-header">
                    <h3 class="step-title">Informasi Pribadi</h3>
                    <p class="step-subtitle">Masukkan data pribadi pelanggan dengan lengkap</p>
                  </div>
                  
                  <v-row class="form-row">
                    <v-col cols="12" md="6">
                      <div class="input-group">
                        <label class="input-label">
                          <v-icon size="small" class="mr-2">mdi-account</v-icon>
                          Nama Lengkap
                        </label>
                        <v-text-field 
                          v-model="editedItem.nama" 
                          :rules="[rules.required]" 
                          variant="outlined"
                          class="elegant-input"
                          density="comfortable"
                        ></v-text-field>
                      </div>
                    </v-col>
                    <v-col cols="12" md="6">
                      <div class="input-group">
                        <label class="input-label">
                          <v-icon size="small" class="mr-2">mdi-card-account-details</v-icon>
                          Nomor KTP
                        </label>
                        <v-text-field 
                          v-model="editedItem.no_ktp" 
                          :rules="[rules.required, rules.ktp]" 
                          variant="outlined" 
                          counter="16"
                          class="elegant-input"
                          density="comfortable"
                        ></v-text-field>
                      </div>
                    </v-col>
                    <v-col cols="12" md="6">
                      <div class="input-group">
                        <label class="input-label">
                          <v-icon size="small" class="mr-2">mdi-email</v-icon>
                          Email
                        </label>
                        <v-text-field 
                          v-model="editedItem.email" 
                          :rules="[rules.required, rules.email]" 
                          variant="outlined"
                          class="elegant-input"
                          density="comfortable"
                        ></v-text-field>
                      </div>
                    </v-col>
                    <v-col cols="12" md="6">
                      <div class="input-group">
                        <label class="input-label">
                          <v-icon size="small" class="mr-2">mdi-phone</v-icon>
                          Nomor Telepon
                        </label>
                        <v-text-field 
                          v-model="editedItem.no_telp" 
                          :rules="[rules.required, rules.phone]" 
                          variant="outlined"
                          class="elegant-input"
                          density="comfortable"
                        ></v-text-field>
                      </div>
                    </v-col>
                  </v-row>
                </v-stepper-window-item>
                
                <v-stepper-window-item :value="2" class="step-content">
                  <div class="step-header">
                    <h3 class="step-title">Alamat & Layanan</h3>
                    <p class="step-subtitle">Lengkapi informasi alamat dan layanan pelanggan</p>
                  </div>
                  
                  <v-row class="form-row">
                    <v-col cols="12">
                      <div class="input-group">
                        <label class="input-label">
                          <v-icon size="small" class="mr-2">mdi-map-marker</v-icon>
                          Alamat Utama
                        </label>
                        <v-combobox
                          v-model="editedItem.alamat"
                          :items="alamatOptions"
                          :rules="[rules.required]"
                          variant="outlined"
                          class="elegant-input"
                          density="comfortable"
                          placeholder="Pilih atau ketik alamat"
                        ></v-combobox>
                        </div>
                    </v-col>
                    <v-col cols="12">
                      <div class="input-group">
                        <label class="input-label">
                          <v-icon size="small" class="mr-2">mdi-map-marker-outline</v-icon>
                          Alamat Tambahan (Opsional)
                        </label>
                        <v-text-field 
                          v-model="editedItem.alamat_2" 
                          variant="outlined"
                          class="elegant-input"
                          density="comfortable"
                        ></v-text-field>
                      </div>
                    </v-col>
                    <v-col cols="12" md="6">
                      <div class="input-group">
                        <label class="input-label">
                          <v-icon size="small" class="mr-2">mdi-home-variant</v-icon>
                          Blok
                        </label>
                        <v-text-field 
                          v-model="editedItem.blok" 
                          :rules="[rules.required]" 
                          variant="outlined"
                          class="elegant-input"
                          density="comfortable"
                        ></v-text-field>
                      </div>
                    </v-col>
                    <v-col cols="12" md="6">
                      <div class="input-group">
                        <label class="input-label">
                          <v-icon size="small" class="mr-2">mdi-door</v-icon>
                          Unit
                        </label>
                        <v-text-field 
                          v-model="editedItem.unit" 
                          :rules="[rules.required]" 
                          variant="outlined"
                          class="elegant-input"
                          density="comfortable"
                        ></v-text-field>
                      </div>
                    </v-col>
                    <v-col cols="12" md="4">
                      <div class="input-group">
                        <label class="input-label">
                          <v-icon size="small" class="mr-2">mdi-calendar</v-icon>
                          Tanggal Instalasi
                        </label>
                        <v-text-field 
                          v-model="editedItem.tgl_instalasi" 
                          type="date" 
                          variant="outlined"
                          class="elegant-input"
                          density="comfortable"
                        ></v-text-field>
                      </div>
                    </v-col>
                    <v-col cols="12" md="4">
                      <div class="input-group">
                        <label class="input-label">
                          <v-icon size="small" class="mr-2">mdi-wifi</v-icon>
                          Layanan
                        </label>
                        <v-select
                          v-model="editedItem.layanan"
                          :items="layananOptions"
                          variant="outlined"
                          class="elegant-input"
                          density="comfortable"
                        ></v-select>
                      </div>
                    </v-col>
                    <v-col cols="12" md="4">
                      <div class="input-group">
                        <label class="input-label">
                          <v-icon size="small" class="mr-2">mdi-domain</v-icon>
                          Brand Provider
                        </label>
                        <v-select 
                          v-model="editedItem.id_brand" 
                          :items="hargaLayananList" 
                          item-title="brand" 
                          item-value="id_brand" 
                          variant="outlined"
                          class="elegant-input"
                          density="comfortable"
                        ></v-select>
                      </div>
                    </v-col>
                  </v-row>
                </v-stepper-window-item>
              </v-stepper-window>
            </v-stepper>
          </v-form>
        </v-card-text>
        
        <v-card-actions class="form-actions">
          <v-btn 
            v-if="currentStep > 1" 
            @click="currentStep--" 
            variant="text"
            class="nav-btn"
            prepend-icon="mdi-arrow-left"
          >
            Kembali
          </v-btn>
          <v-spacer></v-spacer>
          <v-btn 
            @click="closeDialog" 
            variant="text" 
            class="nav-btn"
          >
            Batal
          </v-btn>
          <v-btn 
            v-if="currentStep < 2" 
            @click="currentStep++" 
            color="primary"
            class="nav-btn"
            append-icon="mdi-arrow-right"
          >
            Lanjut
          </v-btn>
          <v-btn 
            v-else 
            @click="savePelanggan" 
            :loading="saving" 
            :disabled="!isFormValid" 
            color="primary" 
            variant="elevated"
            class="save-btn"
            prepend-icon="mdi-content-save"
          >
            Simpan
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-dialog v-model="dialogDelete" max-width="500px" class="delete-dialog">
      <v-card class="delete-card">
        <div class="delete-header">
          <v-icon class="mr-3">mdi-delete-alert</v-icon>
          <span class="delete-title">Konfirmasi Hapus</span>
        </div>
        
        <v-card-text class="delete-content">
          <div class="delete-message">
            <v-icon size="72" color="warning" class="mb-4">mdi-alert-circle-outline</v-icon>
            <p class="delete-text">
              Anda yakin ingin menghapus pelanggan 
              <strong class="customer-name-delete">{{ itemToDelete?.nama }}</strong>?
            </p>
            <p class="delete-warning">Tindakan ini tidak dapat dibatalkan!</p>
          </div>
        </v-card-text>
        
        <v-card-actions class="delete-actions">
          <v-spacer></v-spacer>
          <v-btn 
            @click="closeDeleteDialog" 
            variant="text"
            class="cancel-btn"
          >
            Batal
          </v-btn>
          <v-btn 
            @click="confirmDelete"  
            :loading="deleting" 
            color="error" 
            variant="elevated"
            class="delete-btn"
            prepend-icon="mdi-delete"
          >
            Ya, Hapus
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>


    <v-dialog v-model="dialogBulkDelete" max-width="500px" class="delete-dialog">
      <v-card class="delete-card">
        <div class="delete-header">
          <v-icon class="mr-3">mdi-delete-sweep-outline</v-icon>
          <span class="delete-title">Konfirmasi Hapus Massal</span>
        </div>

        <v-card-text class="delete-content">
          <div class="delete-message">
            <v-icon size="72" color="warning" class="mb-4">mdi-alert-circle-outline</v-icon>
            <p class="delete-text">
              Anda yakin ingin menghapus 
              <strong>{{ selectedPelanggan.length }} pelanggan</strong> yang dipilih?
            </p>
            <p class="delete-warning">Tindakan ini tidak dapat dibatalkan!</p>
          </div>
        </v-card-text>

        <v-card-actions class="delete-actions">
          <v-spacer></v-spacer>
            <v-btn 
              @click="dialogBulkDelete = false" 
              variant="text"
              class="cancel-btn"
            >
              Batal
            </v-btn>
            <v-btn
              @click="confirmBulkDelete"
              :loading="deleting"
              color="error"
              variant="elevated"
              class="delete-btn"
              prepend-icon="mdi-delete"
            >
              Ya, Hapus
            </v-btn>
          </v-card-actions>
        </v-card>
    </v-dialog>

    <v-dialog v-model="dialogImport" max-width="800px" persistent class="import-dialog">
      <v-card class="import-card">
        <div class="import-header">
          <v-icon class="mr-3">mdi-upload</v-icon>
          <span class="import-title">Import Pelanggan dari CSV</span>
          <v-spacer></v-spacer>
          <v-btn 
            icon 
            variant="text" 
            @click="closeImportDialog"
            size="small"
          >
            <v-icon color="white">mdi-close</v-icon>
          </v-btn>
        </div>
        
        <v-card-text class="import-content">
          <v-sheet 
            border 
            rounded="lg" 
            class="template-card pa-4 mb-6"
            color="surface-variant"
          >
            <div class="d-flex align-center">
              <div class="template-icon">
                <v-icon color="success" size="32">mdi-file-document-outline</v-icon>
              </div>
              <div class="ml-4 flex-grow-1">
                <div class="template-title">Gunakan Template Kami</div>
                <p class="template-subtitle">
                  Unduh template CSV untuk memastikan format data sesuai dengan sistem.
                </p>
              </div>
              <v-btn 
                color="success" 
                variant="elevated" 
                @click="downloadCsvTemplate" 
                :loading="downloadingTemplate" 
                prepend-icon="mdi-download" 
                class="template-btn"
              >
                Unduh Template
              </v-btn>
            </div>
          </v-sheet>

          <div class="mb-4">
            <h6 class="text-h6 mb-3 d-flex align-center upload-title">
              <v-icon class="mr-2">mdi-cloud-upload</v-icon>
              Unggah File CSV
            </h6>
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
              hide-details="auto"
              class="file-input"
              density="comfortable"
            >
            </v-file-input>
          </div>

          <v-expand-transition>
            <div v-if="importErrors.length > 0" class="mt-4">
              <v-alert 
                type="error" 
                variant="tonal" 
                prominent 
                border="start"
                class="error-alert"
              >
                <template v-slot:title>
                  <div class="d-flex justify-space-between align-center">
                    <span>Import Gagal</span>
                    <v-chip color="error" size="small">
                      {{ importErrors.length }} Kesalahan
                    </v-chip>
                  </div>
                </template>
                
                <p class="mb-3">Mohon perbaiki kesalahan berikut di file CSV Anda dan coba lagi.</p>
                <v-divider class="mb-3"></v-divider>
                
                <div class="error-list">
                  <div 
                    v-for="(error, i) in importErrors" 
                    :key="i" 
                    class="error-item d-flex align-start mb-2"
                  >
                    <v-icon size="small" color="error" class="mr-2 mt-1">mdi-alert-circle</v-icon>
                    <span class="text-body-2">{{ error }}</span>
                  </div>
                </div>
              </v-alert>
            </div>
          </v-expand-transition>
        </v-card-text>
        
        <v-divider></v-divider>
        
        <v-card-actions class="import-actions">
          <v-spacer></v-spacer>
          <v-btn 
            variant="text" 
            @click="closeImportDialog"
            class="nav-btn"
          >
            Batal
          </v-btn>
          <v-btn 
            color="success" 
            variant="elevated" 
            @click="importFromCsv" 
            :loading="importing" 
            :disabled="fileToImport.length === 0" 
            prepend-icon="mdi-upload" 
            class="import-btn"
          >
            Import Sekarang
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-snackbar 
      v-model="snackbar.show" 
      :color="snackbar.color" 
      :timeout="4000" 
      location="top right"
      class="enhanced-snackbar"
    >
      <div class="d-flex align-center">
        <v-icon class="mr-2">
          {{ snackbar.color === 'success' ? 'mdi-check-circle' : 
             snackbar.color === 'error' ? 'mdi-alert-circle' : 'mdi-information' }}
        </v-icon>
        {{ snackbar.text }}
      </div>
    </v-snackbar>
  </v-container>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue';
import apiClient from '@/services/api';
import type { Pelanggan as BasePelanggan } from '@/interfaces/pelanggan';
import { debounce } from 'lodash-es';

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
const dialogBulkDelete = ref(false);
const editedIndex = ref(-1);
const currentStep = ref(1);
const isFormValid = ref(false);
const selectedPelanggan = ref<any[]>([]);

const dialogImport = ref(false);
const importing = ref(false);
const exporting = ref(false);
const downloadingTemplate = ref(false);
const fileToImport = ref<File[]>([]);
const importErrors = ref<string[]>([]);

const searchQuery = ref('');
const selectedAlamat = ref<string | null>(null);
const selectedBrand = ref<string | null>(null);


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

// MODIFIKASI DIMULAI DI SINI
const alamatOptions = ref([
  'Tambun',
  'Rusun Pinus Elok',
  'Luar Pinus Elok',
  'Rusun Pulogebang',
  'Rusun Cakung KM2',
  'Rusun Tipar Cakung',
  'Rusun Albo',
  'Rusun Nagrak',
  'Waringin',
  'Parama'
]);
// MODIFIKASI SELESAI

const layananOptions = ref([
  'Internet 10 Mbps',
  'Internet 20 Mbps',
  'Internet 30 Mbps',
  'Internet 50 Mbps'
]);

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


//Buat hapus data
function deleteSelectedPelanggan() {
  if (selectedPelanggan.value.length === 0) {
    showSnackbar('Tidak ada pelanggan yang dipilih.', 'warning');
    return;
  }
  // Tugasnya sekarang hanya membuka dialog
  dialogBulkDelete.value = true;
}

async function confirmBulkDelete() {
  const itemsToDelete = [...selectedPelanggan.value];
  deleting.value = true; // Menggunakan state 'deleting' yang sudah ada

  try {
    const deletePromises = itemsToDelete.map(pelanggan =>
      apiClient.delete(`/pelanggan/${pelanggan.id}`)
    );

    await Promise.all(deletePromises);

    showSnackbar(`${itemsToDelete.length} pelanggan berhasil dihapus.`, 'success');

    await fetchPelanggan();
    selectedPelanggan.value = []; // Kosongkan pilihan

  } catch (error) {
    console.error("Gagal melakukan hapus massal:", error);
    showSnackbar('Terjadi kesalahan saat menghapus data.', 'error');
  } finally {
    deleting.value = false;
    dialogBulkDelete.value = false; // Tutup dialog setelah selesai
  }
}

// --- METODE CRUD ---
async function fetchPelanggan() {
  loading.value = true;
  try {
    const params = new URLSearchParams();
    if (searchQuery.value) {
      params.append('search', searchQuery.value);
    }
    if (selectedAlamat.value) {
      params.append('alamat', selectedAlamat.value);
    }
    if (selectedBrand.value) {
      params.append('id_brand', selectedBrand.value);
    }

    const response = await apiClient.get(`/pelanggan/?${params.toString()}`);
    pelangganList.value = response.data;
  } catch (error) { 
    console.error("Gagal mengambil data pelanggan:", error);
    showSnackbar('Gagal mengambil data pelanggan', 'error');
  } finally { 
    loading.value = false; 
  }
}

// Fungsi yang di-debounce untuk menerapkan filter
// Ini mencegah API dipanggil pada setiap ketikan, lebih efisien!
const applyFilters = debounce(() => {
  fetchPelanggan();
}, 500); // Tunda 500ms setelah user berhenti mengetik/memilih

// Perhatikan perubahan pada filter dan panggil fungsi applyFilters
watch([searchQuery, selectedAlamat, selectedBrand], () => {
  applyFilters();
});

// Fungsi untuk mereset semua filter
function resetFilters() {
  searchQuery.value = '';
  selectedAlamat.value = null;
  selectedBrand.value = null;
  // Watch akan otomatis terpanggil dan me-refresh data
}
// ============================================

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
/* ============================================
   REVISI TOTAL GAYA TEMA - LEBIH STABIL
   ============================================ */

/* Header Utama */
.header-card {
  background: linear-gradient(135deg, rgb(var(--v-theme-primary)) 0%, rgb(var(--v-theme-secondary)) 100%);
  border-radius: 24px;
  padding: 32px;
  color: rgb(var(--v-theme-on-primary));
  box-shadow: 0 12px 40px rgba(var(--v-theme-primary), 0.25);
  position: relative;
}

.header-avatar-wrapper {
  background: rgba(255, 255, 255, 0.15);
  border-radius: 50%;
  padding: 12px;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.header-title {
  font-size: 2.25rem;
  font-weight: 800;
  line-height: 1.2;
}

.header-subtitle {
  font-size: 1.1rem;
  opacity: 0.85;
  margin-top: 8px;
}

/* Tombol Header (di luar primary-btn) */
.action-btn {
  border-radius: 16px;
  font-weight: 600;
  height: 52px;
  /* Gaya "kaca" tembus pandang yang konsisten */
  background-color: rgba(255, 255, 255, 0.15) !important;
  color: white !important;
  border: 1px solid rgba(255, 255, 255, 0.3) !important;
  backdrop-filter: blur(5px);
  transition: background-color 0.3s ease;
  margin-left: 12px;
}

.action-btn:hover {
    background-color: rgba(255, 255, 255, 0.25) !important;
}

/* Tombol Primary di Header (Tambah Pelanggan) */
.primary-btn {
  border-radius: 16px;
  font-weight: 700;
  height: 52px;
  background: white !important; /* Latar belakang solid putih */
  color: rgb(var(--v-theme-primary)) !important;
  border: 1px solid transparent;
  margin-left: 12px;
}

/* ============================================
   ENHANCED FILTER CARD STYLING
   ============================================ */

.filter-card {
  border-radius: 20px;
  border: 1px solid rgba(var(--v-theme-primary), 0.12);
  background: linear-gradient(145deg, 
    rgba(var(--v-theme-surface), 0.95) 0%, 
    rgba(var(--v-theme-background), 0.98) 100%);
  backdrop-filter: blur(10px);
  box-shadow: 
    0 4px 20px rgba(var(--v-theme-shadow), 0.08),
    0 1px 3px rgba(var(--v-theme-shadow), 0.12);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
}

/* Efek hover pada filter card */
.filter-card:hover {
  transform: translateY(-2px);
  box-shadow: 
    0 8px 30px rgba(var(--v-theme-shadow), 0.12),
    0 2px 6px rgba(var(--v-theme-shadow), 0.16);
  border-color: rgba(var(--v-theme-primary), 0.2);
}

/* Efek glow subtle di bagian atas card */
.filter-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(90deg, 
    transparent 0%, 
    rgba(var(--v-theme-primary), 0.6) 50%, 
    transparent 100%);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.filter-card:hover::before {
  opacity: 1;
}

/* Container utama filter */
.filter-card .d-flex {
  padding: 28px 32px !important;
  gap: 20px !important;
}

/* Styling untuk text field pencarian */
.filter-card .v-text-field {
  min-width: 320px !important;
}

.filter-card .v-text-field :deep(.v-field) {
  background: rgba(var(--v-theme-surface), 0.8) !important;
  border: 2px solid rgba(var(--v-theme-outline-variant), 0.3) !important;
  border-radius: 16px !important;
  box-shadow: inset 0 2px 4px rgba(var(--v-theme-shadow), 0.06);
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}

.filter-card .v-text-field :deep(.v-field:hover) {
  border-color: rgba(var(--v-theme-primary), 0.4) !important;
  background: rgba(var(--v-theme-surface), 1) !important;
  transform: translateY(-1px);
  box-shadow: 
    inset 0 2px 4px rgba(var(--v-theme-shadow), 0.06),
    0 4px 12px rgba(var(--v-theme-primary), 0.1);
}

.filter-card .v-text-field :deep(.v-field--focused) {
  border-color: rgb(var(--v-theme-primary)) !important;
  background: rgba(var(--v-theme-surface), 1) !important;
  box-shadow: 
    inset 0 2px 4px rgba(var(--v-theme-shadow), 0.06),
    0 0 0 3px rgba(var(--v-theme-primary), 0.12);
}

/* Icon pencarian */
.filter-card .v-text-field :deep(.v-field__prepend-inner) {
  padding-right: 12px;
}

.filter-card .v-text-field :deep(.v-field__prepend-inner .v-icon) {
  color: rgba(var(--v-theme-primary), 0.7) !important;
  transition: color 0.2s ease;
}

.filter-card .v-text-field:hover :deep(.v-field__prepend-inner .v-icon) {
  color: rgb(var(--v-theme-primary)) !important;
}

/* Styling untuk select fields (alamat & brand) */
.filter-card .v-select {
  min-width: 220px !important;
}

.filter-card .v-select :deep(.v-field) {
  background: rgba(var(--v-theme-surface), 0.8) !important;
  border: 2px solid rgba(var(--v-theme-outline-variant), 0.3) !important;
  border-radius: 16px !important;
  box-shadow: inset 0 2px 4px rgba(var(--v-theme-shadow), 0.06);
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}

.filter-card .v-select :deep(.v-field:hover) {
  border-color: rgba(var(--v-theme-primary), 0.4) !important;
  background: rgba(var(--v-theme-surface), 1) !important;
  transform: translateY(-1px);
  box-shadow: 
    inset 0 2px 4px rgba(var(--v-theme-shadow), 0.06),
    0 4px 12px rgba(var(--v-theme-primary), 0.1);
}

.filter-card .v-select :deep(.v-field--focused) {
  border-color: rgb(var(--v-theme-primary)) !important;
  background: rgba(var(--v-theme-surface), 1) !important;
  box-shadow: 
    inset 0 2px 4px rgba(var(--v-theme-shadow), 0.06),
    0 0 0 3px rgba(var(--v-theme-primary), 0.12);
}

/* Label styling yang lebih refined */
.filter-card .v-field :deep(.v-field__label) {
  color: rgba(var(--v-theme-on-surface), 0.7) !important;
  font-weight: 500 !important;
  font-size: 0.875rem !important;
}

.filter-card .v-field--focused :deep(.v-field__label) {
  color: rgb(var(--v-theme-primary)) !important;
}

/* Tombol Reset Filter */
.filter-card .v-btn[variant="text"] {
  border-radius: 14px !important;
  font-weight: 600 !important;
  height: 48px !important;
  min-width: 120px !important;
  color: rgba(var(--v-theme-primary), 0.8) !important;
  background: rgba(var(--v-theme-primary), 0.08) !important;
  border: 1px solid rgba(var(--v-theme-primary), 0.2) !important;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
}

.filter-card .v-btn[variant="text"]:hover {
  background: rgba(var(--v-theme-primary), 0.12) !important;
  color: rgb(var(--v-theme-primary)) !important;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(var(--v-theme-primary), 0.2);
}

.filter-card .v-btn[variant="text"]:active {
  transform: translateY(0);
}

/* Efek ripple custom untuk tombol reset */
.filter-card .v-btn[variant="text"]::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  width: 0;
  height: 0;
  border-radius: 50%;
  background: rgba(var(--v-theme-primary), 0.3);
  transition: width 0.3s ease, height 0.3s ease;
  transform: translate(-50%, -50%);
  z-index: 0;
}

.filter-card .v-btn[variant="text"]:hover::before {
  width: 100%;
  height: 100%;
}

/* Responsive design untuk mobile */
@media (max-width: 960px) {
  .filter-card .d-flex {
    padding: 20px 24px !important;
    gap: 16px !important;
  }
  
  .filter-card .v-text-field,
  .filter-card .v-select {
    min-width: 100% !important;
  }
  
  .filter-card .v-btn[variant="text"] {
    width: 100% !important;
    margin-top: 8px;
  }
}

@media (max-width: 600px) {
  .filter-card .d-flex {
    padding: 16px 20px !important;
    flex-direction: column !important;
    gap: 12px !important;
  }
  
  .filter-card {
    border-radius: 16px;
    margin: 0 8px;
  }
}

/* Dark mode adjustments */
.v-theme--dark .filter-card {
  background: linear-gradient(145deg, 
    rgba(var(--v-theme-surface), 0.9) 0%, 
    rgba(var(--v-theme-background), 0.95) 100%);
  border-color: rgba(var(--v-theme-primary), 0.2);
}

.v-theme--dark .filter-card:hover {
  border-color: rgba(var(--v-theme-primary), 0.3);
}

.v-theme--dark .filter-card .v-text-field :deep(.v-field),
.v-theme--dark .filter-card .v-select :deep(.v-field) {
  background: rgba(var(--v-theme-surface), 0.6) !important;
  border-color: rgba(var(--v-theme-outline), 0.3) !important;
}

.v-theme--dark .filter-card .v-text-field :deep(.v-field:hover),
.v-theme--dark .filter-card .v-select :deep(.v-field:hover) {
  background: rgba(var(--v-theme-surface), 0.8) !important;
  border-color: rgba(var(--v-theme-primary), 0.5) !important;
}

/* Loading state untuk field */
.filter-card .v-field--loading :deep(.v-field) {
  opacity: 0.7;
  pointer-events: none;
}

/* Animasi untuk smooth transitions */
.filter-card * {
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

/* Focus ring yang lebih halus */
.filter-card .v-field--focused :deep(.v-field__outline) {
  border-width: 2px !important;
  border-color: rgb(var(--v-theme-primary)) !important;
}

/* Custom scrollbar untuk dropdown */
.filter-card .v-select :deep(.v-list) {
  border-radius: 12px;
  box-shadow: 0 8px 30px rgba(var(--v-theme-shadow), 0.15);
}

.filter-card .v-select :deep(.v-list-item) {
  border-radius: 8px;
  margin: 2px 8px;
  transition: all 0.2s ease;
}

.filter-card .v-select :deep(.v-list-item:hover) {
  background: rgba(var(--v-theme-primary), 0.08) !important;
  transform: translateX(4px);
}

/* --- Gaya Komprehensif untuk Dialog Impor --- */
.import-dialog .v-card {
  border-radius: 20px;
  overflow: hidden;
  background: rgb(var(--v-theme-surface));
  border: 1px solid rgba(var(--v-theme-success), 0.2);
}

.import-header {
  background: linear-gradient(135deg, rgb(var(--v-theme-success)) 0%, rgb(var(--v-theme-success-darken-1)) 100%);
  padding: 24px 28px;
  color: rgb(var(--v-theme-on-success));
  display: flex;
  align-items: center;
}

.import-header .import-title {
  font-size: 1.4rem;
  font-weight: 700;
}

.import-content {
  padding: 32px !important;
  background: rgb(var(--v-theme-background));
}

.template-card {
  border: 2px dashed rgba(var(--v-theme-success), 0.3);
  background: rgba(var(--v-theme-success), 0.05);
  border-radius: 16px;
  transition: all 0.3s ease;
}

.template-card:hover {
  border-color: rgb(var(--v-theme-success));
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(var(--v-theme-success), 0.15);
}

.template-title, .upload-title {
  font-weight: 700;
  color: rgb(var(--v-theme-on-surface));
  margin-bottom: 6px;
}

.template-subtitle {
  color: rgb(var(--v-theme-on-surface-variant));
  line-height: 1.4;
}

.file-input :deep(.v-field) {
  border: 2px dashed rgb(var(--v-theme-outline-variant)) !important;
  background: rgb(var(--v-theme-surface)) !important;
  border-radius: 16px;
  transition: all 0.2s ease-in-out;
}

.file-input :deep(.v-field:hover) {
  border-color: rgb(var(--v-theme-success)) !important;
  background: rgba(var(--v-theme-success), 0.05) !important;
}

.import-actions {
  padding: 16px 24px !important;
  background: rgb(var(--v-theme-surface));
  border-top: 1px solid rgb(var(--v-theme-outline-variant));
}

.import-btn {
  background: rgb(var(--v-theme-success)) !important;
  color: rgb(var(--v-theme-on-success)) !important;
  border-radius: 10px;
  font-weight: 600;
  text-transform: none;
}

/* Penyesuaian Tombol Header untuk Dark Mode */
.v-theme--dark .action-btn {
  background: rgba(255, 255, 255, 0.1) !important;
  color: white !important;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

/* Kartu Tabel Data */
.data-table-card {
  border-radius: 20px;
  overflow: hidden;
  border: 1px solid rgb(var(--v-theme-outline-variant));
  background: rgb(var(--v-theme-surface));
}

.data-table-card .card-header {
  padding: 24px 28px;
  border-bottom: 1px solid rgb(var(--v-theme-outline-variant));
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: rgba(var(--v-theme-primary), 0.03);
}

.data-table-card .card-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: rgb(var(--v-theme-on-surface));
}

/* Tabel */
.elegant-table {
  background: transparent !important;
}

.elegant-table :deep(th) {
  font-weight: 600 !important;
  font-size: 0.875rem !important;
  color: rgb(var(--v-theme-on-surface)) !important;
  opacity: 0.8;
  border-bottom: 1px solid rgb(var(--v-theme-outline-variant)) !important;
}

.elegant-table :deep(td) {
  border-bottom: 1px solid rgb(var(--v-theme-outline-variant)) !important;
}

.customer-name {
  font-weight: 600;
  color: rgb(var(--v-theme-on-surface));
}

.customer-email {
  font-size: 0.85rem;
  color: rgb(var(--v-theme-on-surface));
  opacity: 0.7;
}

.selection-toolbar {
  display: flex;
  align-items: center;
  padding: 12px 28px;
  background-color: rgba(var(--v-theme-primary), 0.08);
  border-bottom: 1px solid rgba(var(--v-theme-primary), 0.15);
}

/* Dialog Form */
.form-card {
  border-radius: 24px;
  overflow: hidden;
  background: rgb(var(--v-theme-background));
  border: 1px solid rgb(var(--v-theme-outline-variant));
}

.form-header {
  background: linear-gradient(135deg, rgb(var(--v-theme-primary)) 0%, rgb(var(--v-theme-secondary)) 100%);
  padding: 28px 32px;
  color: rgb(var(--v-theme-on-primary));
}

.form-title {
  font-size: 1.75rem;
  font-weight: 700;
}

.form-content {
  padding: 36px !important;
  background: rgb(var(--v-theme-background));
}

.stepper-header, .stepper-content {
  background: rgb(var(--v-theme-surface));
  border-radius: 16px;
  border: 1px solid rgb(var(--v-theme-outline-variant));
}

.stepper-header {
  margin-bottom: 24px;
  padding: 12px;
}

.stepper-content {
  padding: 32px;
}

.step-header {
  margin-bottom: 32px;
  text-align: center;
}

.step-title {
  color: rgb(var(--v-theme-on-surface));
  font-weight: 700;
  font-size: 1.5rem;
}

.step-subtitle {
  color: rgb(var(--v-theme-on-surface));
  opacity: 0.7;
  font-size: 1rem;
}

.input-label {
  display: flex;
  align-items: center;
  font-weight: 600;
  color: rgb(var(--v-theme-on-surface));
  margin-bottom: 12px;
}

.elegant-input :deep(.v-field) {
  border-radius: 16px;
  background: rgb(var(--v-theme-background));
}

.form-actions {
  padding: 24px 36px !important;
  border-top: 1px solid rgb(var(--v-theme-outline-variant));
  background: rgb(var(--v-theme-surface));
}

/* Tombol Navigasi Form */
.nav-btn, .save-btn {
  border-radius: 14px;
  font-weight: 600;
  height: 48px;
}

/* Dialog Hapus & Import (Disederhanakan) */
.delete-card, .import-card {
  border-radius: 20px;
  background: rgb(var(--v-theme-surface));
}

.delete-header {
  background: rgb(var(--v-theme-error));
  color: rgb(var(--v-theme-on-error));
  padding: 24px;
}

.import-header {
  background: rgb(var(--v-theme-success));
  color: rgb(var(--v-theme-on-success));
  padding: 24px;
}

.delete-content, .import-content {
  padding: 32px !important;
}

.delete-actions, .import-actions {
  padding: 16px 24px !important;
  border-top: 1px solid rgb(var(--v-theme-outline-variant));
}

/* Penyesuaian lainnya */
:deep(.v-snackbar__wrapper) {
  border-radius: 12px;
  box-shadow: 0 8px 25px rgba(0,0,0,0.15);
}


@media (max-width: 768px) {
  .header-card, .card-header, .form-content, .stepper-content { padding: 16px; }
  .header-title { font-size: 1.5rem; }
}
</style>