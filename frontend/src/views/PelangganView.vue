<template>
  <v-container fluid class="pa-6">
    <!-- Header Section -->
    <div class="d-flex align-center mb-6">
      <div class="d-flex align-center">
        <v-avatar class="me-3" color="deep-purple" size="40">
          <v-icon color="white">mdi-account-group</v-icon>
        </v-avatar>
        <div>
          <h1 class="text-h4 font-weight-bold text-deep-purple">Data Pelanggan</h1>
          <p class="text-subtitle-1 text-medium-emphasis mb-0">Kelola semua data pelanggan Anda</p>
        </div>
      </div>
      <v-spacer></v-spacer>
      <v-btn 
        color="deep-purple" 
        size="large"
        elevation="2"
        @click="openDialog()"
        prepend-icon="mdi-account-plus"
        class="text-none"
      >
        Tambah Pelanggan
      </v-btn>
    </div>

    <!-- Main Data Table Card -->
    <v-card elevation="3" class="rounded-lg">
      <v-card-title class="d-flex align-center pa-6 bg-grey-lighten-5">
        <v-icon start icon="mdi-format-list-bulleted-square" color="deep-purple"></v-icon>
        <span class="text-h6 font-weight-bold">Daftar Pelanggan</span>
        <v-spacer></v-spacer>
        <v-chip color="deep-purple" variant="outlined" size="small">
          {{ pelangganList.length }} pelanggan
        </v-chip>
      </v-card-title>
      
      <v-data-table
        :headers="headers"
        :items="pelangganList"
        :loading="loading"
        item-value="id"
        class="elevation-0"
        :items-per-page="10"
      >
        <template v-slot:item.nama="{ item }">
          <div class="font-weight-bold">{{ item.nama }}</div>
          <div class="text-caption text-medium-emphasis">{{ item.email }}</div>
        </template>

        <template v-slot:item.alamat="{ item }">
          <div>{{ item.alamat }}</div>
          <div class="text-caption text-medium-emphasis">Blok {{ item.blok }} / Unit {{ item.unit }}</div>
        </template>
        
        <!-- PERUBAHAN 1: Menambahkan :class untuk gradient -->
        <template v-slot:item.id_brand="{ item }">
          <v-chip
            size="small"
            :color="getBrandColor(getBrandName(item.id_brand))"
            :class="{ 'gradient-chip-nagrak': getBrandName(item.id_brand)?.toLowerCase().includes('nagrak') }"
            class="font-weight-bold"
          >
            {{ getBrandName(item.id_brand) || 'N/A' }}
          </v-chip>
        </template>

        <template v-slot:item.tgl_instalasi="{ item }">
            {{ formatDate(item.tgl_instalasi) }}
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

    <!-- ENHANCED Add/Edit Dialog -->
    <v-dialog v-model="dialog" max-width="900px" persistent scrollable>
      <v-card class="rounded-xl elegant-form-card" elevation="24">
        <!-- Elegant Header with Gradient -->
        <div class="form-header-gradient pa-6">
          <div class="d-flex align-center text-white">
            <v-avatar color="white" class="me-4" size="48">
              <v-icon color="deep-purple" size="28">
                {{ editedIndex === -1 ? 'mdi-account-plus' : 'mdi-account-edit' }}
              </v-icon>
            </v-avatar>
            <div>
              <h2 class="text-h4 font-weight-bold mb-1">{{ formTitle }}</h2>
              <p class="text-subtitle-1 opacity-90 mb-0">
                {{ editedIndex === -1 ? 'Tambahkan pelanggan baru ke dalam sistem' : 'Perbarui informasi pelanggan' }}
              </p>
            </div>
          </div>
        </div>

        <!-- Form Content with Enhanced Styling -->
        <v-card-text class="pa-8">
          <!-- Progress Indicator -->
          <div class="form-progress-indicator mb-8">
            <div class="d-flex align-center justify-center">
              <div class="progress-step" :class="{ active: currentStep >= 1 }">
                <v-icon size="20">mdi-account</v-icon>
                <span class="step-label">Identitas</span>
              </div>
              <div class="progress-line" :class="{ active: currentStep >= 2 }"></div>
              <div class="progress-step" :class="{ active: currentStep >= 2 }">
                <v-icon size="20">mdi-home</v-icon>
                <span class="step-label">Alamat</span>
              </div>
              <div class="progress-line" :class="{ active: currentStep >= 3 }"></div>
              <div class="progress-step" :class="{ active: currentStep >= 3 }">
                <v-icon size="20">mdi-cog</v-icon>
                <span class="step-label">Layanan</span>
              </div>
            </div>
          </div>

          <!-- Step 1: Personal Information -->
          <v-expand-transition>
            <div v-show="currentStep === 1" class="form-section">
              <div class="section-header mb-6">
                <v-icon color="deep-purple" class="me-3">mdi-account-circle</v-icon>
                <h3 class="text-h6 font-weight-bold">Informasi Pribadi</h3>
              </div>
              
              <v-row class="form-row">
                <v-col cols="12" md="6">
                  <div class="input-group">
                    <label class="input-label">
                      <v-icon size="18" class="me-2">mdi-account</v-icon>
                      Nama Lengkap
                    </label>
                    <v-text-field 
                      v-model="editedItem.nama" 
                      placeholder="Masukkan nama lengkap"
                      variant="outlined" 
                      density="comfortable"
                      class="elegant-input"
                      :rules="[rules.required]"
                      hide-details="auto"
                    ></v-text-field>
                  </div>
                </v-col>
                
                <v-col cols="12" md="6">
                  <div class="input-group">
                    <label class="input-label">
                      <v-icon size="18" class="me-2">mdi-card-account-details</v-icon>
                      Nomor KTP
                    </label>
                    <v-text-field 
                      v-model="editedItem.no_ktp" 
                      placeholder="Masukkan nomor KTP"
                      variant="outlined" 
                      density="comfortable"
                      class="elegant-input"
                      :rules="[rules.required, rules.ktp]"
                      hide-details="auto"
                    ></v-text-field>
                  </div>
                </v-col>
                
                <v-col cols="12" md="6">
                  <div class="input-group">
                    <label class="input-label">
                      <v-icon size="18" class="me-2">mdi-email</v-icon>
                      Email Address
                    </label>
                    <v-text-field 
                      v-model="editedItem.email" 
                      placeholder="contoh@email.com"
                      type="email" 
                      variant="outlined" 
                      density="comfortable"
                      class="elegant-input"
                      :rules="[rules.required, rules.email]"
                      hide-details="auto"
                    ></v-text-field>
                  </div>
                </v-col>
                
                <v-col cols="12" md="6">
                  <div class="input-group">
                    <label class="input-label">
                      <v-icon size="18" class="me-2">mdi-phone</v-icon>
                      Nomor Telepon
                    </label>
                    <v-text-field 
                      v-model="editedItem.no_telp" 
                      placeholder="+62 812-3456-7890"
                      variant="outlined" 
                      density="comfortable"
                      class="elegant-input"
                      :rules="[rules.required, rules.phone]"
                      hide-details="auto"
                    ></v-text-field>
                  </div>
                </v-col>
              </v-row>
            </div>
          </v-expand-transition>

          <!-- Step 2: Address Information -->
          <v-expand-transition>
            <div v-show="currentStep === 2" class="form-section">
              <div class="section-header mb-6">
                <v-icon color="deep-purple" class="me-3">mdi-home-variant</v-icon>
                <h3 class="text-h6 font-weight-bold">Informasi Alamat</h3>
              </div>
              
              <v-row class="form-row">
                <v-col cols="12">
                  <div class="input-group">
                    <label class="input-label">
                      <v-icon size="18" class="me-2">mdi-map-marker</v-icon>
                      Alamat Utama
                    </label>
                    <v-textarea 
                      v-model="editedItem.alamat" 
                      placeholder="Masukkan alamat lengkap"
                      variant="outlined" 
                      rows="3"
                      density="comfortable"
                      class="elegant-input"
                      :rules="[rules.required]"
                      hide-details="auto"
                    ></v-textarea>
                  </div>
                </v-col>
                
                <v-col cols="12" md="6">
                  <div class="input-group">
                    <label class="input-label">
                      <v-icon size="18" class="me-2">mdi-home-city</v-icon>
                      Blok
                    </label>
                    <v-text-field 
                      v-model="editedItem.blok" 
                      placeholder="A, B, C, dll"
                      variant="outlined" 
                      density="comfortable"
                      class="elegant-input"
                      :rules="[rules.required]"
                      hide-details="auto"
                    ></v-text-field>
                  </div>
                </v-col>
                
                <v-col cols="12" md="6">
                  <div class="input-group">
                    <label class="input-label">
                      <v-icon size="18" class="me-2">mdi-numeric</v-icon>
                      Unit
                    </label>
                    <v-text-field 
                      v-model="editedItem.unit" 
                      placeholder="01, 02, 03, dll"
                      variant="outlined" 
                      density="comfortable"
                      class="elegant-input"
                      :rules="[rules.required]"
                      hide-details="auto"
                    ></v-text-field>
                  </div>
                </v-col>
                
                <v-col cols="12">
                  <div class="input-group">
                    <label class="input-label">
                      <v-icon size="18" class="me-2">mdi-map-marker-plus</v-icon>
                      Alamat Tambahan (Opsional)
                    </label>
                    <v-textarea 
                      v-model="editedItem.alamat_2" 
                      placeholder="Patokan atau detail tambahan alamat"
                      variant="outlined" 
                      rows="2"
                      density="comfortable"
                      class="elegant-input"
                      hide-details="auto"
                    ></v-textarea>
                  </div>
                </v-col>
              </v-row>
            </div>
          </v-expand-transition>

          <!-- Step 3: Service Information -->
          <v-expand-transition>
            <div v-show="currentStep === 3" class="form-section">
              <div class="section-header mb-6">
                <v-icon color="deep-purple" class="me-3">mdi-cog-outline</v-icon>
                <h3 class="text-h6 font-weight-bold">Informasi Layanan</h3>
              </div>
              
              <v-row class="form-row">
                <v-col cols="12" md="6">
                  <div class="input-group">
                    <label class="input-label">
                      <v-icon size="18" class="me-2">mdi-wifi</v-icon>
                      Layanan
                    </label>
                    <v-text-field 
                      v-model="editedItem.layanan" 
                      placeholder="Internet, TV, dsb"
                      variant="outlined" 
                      density="comfortable"
                      class="elegant-input"
                      hide-details="auto"
                    ></v-text-field>
                  </div>
                </v-col>
                
                <v-col cols="12" md="6">
                  <div class="input-group">
                    <label class="input-label">
                      <v-icon size="18" class="me-2">mdi-tag</v-icon>
                      Brand Provider
                    </label>
                    <v-select
                      v-model="editedItem.id_brand"
                      :items="hargaLayananList"
                      item-title="brand"
                      item-value="id_brand"
                      placeholder="Pilih brand provider"
                      variant="outlined"
                      density="comfortable"
                      class="elegant-input"
                      hide-details="auto"
                    ></v-select>
                  </div>
                </v-col>
                
                <v-col cols="12">
                  <div class="input-group">
                    <label class="input-label">
                      <v-icon size="18" class="me-2">mdi-calendar-clock</v-icon>
                      Tanggal Instalasi
                    </label>
                    <v-text-field 
                      v-model="editedItem.tgl_instalasi" 
                      type="date" 
                      variant="outlined" 
                      density="comfortable"
                      class="elegant-input"
                      hide-details="auto"
                    ></v-text-field>
                  </div>
                </v-col>
              </v-row>
            </div>
          </v-expand-transition>
        </v-card-text>

        <!-- Enhanced Action Buttons -->
        <v-card-actions class="pa-6 bg-grey-lighten-5">
          <div class="d-flex w-100 align-center">
            <!-- Navigation Buttons -->
            <div class="d-flex ga-3">
              <v-btn 
                v-if="currentStep > 1"
                variant="outlined" 
                color="deep-purple"
                @click="currentStep--"
                prepend-icon="mdi-chevron-left"
                class="nav-btn"
              >
                Sebelumnya
              </v-btn>
              
              <v-btn 
                v-if="currentStep < 3"
                color="deep-purple" 
                variant="flat"
                @click="currentStep++"
                append-icon="mdi-chevron-right"
                class="nav-btn"
              >
                Selanjutnya
              </v-btn>
            </div>

            <v-spacer></v-spacer>

            <!-- Action Buttons -->
            <div class="d-flex ga-3">
              <v-btn 
                variant="outlined" 
                color="grey"
                @click="closeDialog"
                prepend-icon="mdi-close"
                class="action-btn"
              >
                Batal
              </v-btn>
              
              <v-btn 
                color="deep-purple" 
                variant="flat" 
                @click="savePelanggan" 
                :loading="saving"
                :disabled="!isFormValid"
                prepend-icon="mdi-content-save"
                class="action-btn save-btn"
              >
                {{ editedIndex === -1 ? 'Tambah Pelanggan' : 'Simpan Perubahan' }}
              </v-btn>
            </div>
          </div>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Delete Dialog -->
    <v-dialog v-model="dialogDelete" max-width="500px">
      <v-card class="rounded-lg">
        <v-card-title class="text-h5 text-center pt-8 text-error">Konfirmasi Hapus</v-card-title>
        <v-card-text class="text-center pa-6">
          Anda yakin ingin menghapus pelanggan <strong>{{ itemToDelete?.nama }}</strong>?
        </v-card-text>
        <v-card-actions class="pa-4">
          <v-spacer></v-spacer>
          <v-btn variant="text" @click="closeDeleteDialog">Batal</v-btn>
          <v-btn color="error" variant="flat" @click="confirmDelete" :loading="deleting">Ya, Hapus</v-btn>
          <v-spacer></v-spacer>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import apiClient from '@/services/api';
import type { Pelanggan as BasePelanggan } from '@/interfaces/pelanggan';

// --- Interface ---
interface Pelanggan extends BasePelanggan {
  alamat_2?: string | null;
  id_brand?: string | null;
}

interface HargaLayanan {
  id_brand: string;
  brand: string;
}

// --- State ---
const pelangganList = ref<Pelanggan[]>([]);
const hargaLayananList = ref<HargaLayanan[]>([]);
const loading = ref(true);
const saving = ref(false);
const deleting = ref(false);
const dialog = ref(false);
const dialogDelete = ref(false);
const editedIndex = ref(-1);
const currentStep = ref(1); // New state for form steps

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
  tgl_instalasi: new Date(),
  alamat_2: '',
  id_brand: null
};
const editedItem = ref({ ...defaultItem });
const itemToDelete = ref<Pelanggan | null>(null);

// --- Validation Rules ---
const rules = {
  required: (value: any) => !!value || 'Field ini wajib diisi',
  email: (value: string) => {
    const pattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return pattern.test(value) || 'Format email tidak valid';
  },
  phone: (value: string) => {
    const pattern = /^[\+]?[0-9\s\-\(\)]{10,}$/;
    return pattern.test(value) || 'Format nomor telepon tidak valid';
  },
  ktp: (value: string) => {
    const pattern = /^[0-9]{16}$/;
    return pattern.test(value) || 'Nomor KTP harus 16 digit';
  }
};

// --- Headers ---
const headers = [
  { title: 'Nama Pelanggan', key: 'nama', sortable: true },
  { title: 'Alamat', key: 'alamat' },
  { title: 'No. Telepon', key: 'no_telp' },
  { title: 'Email', key: 'email'},
  { title: 'Layanan', key: 'layanan'},
  { title: 'Brand', key: 'id_brand'},
  { title: 'Tgl Instalasi', key: 'tgl_instalasi', align: 'center' },
  { title: 'Actions', key: 'actions', sortable: false, align: 'center', width: '200px' },
] as const;

// --- Computed Properties ---
const formTitle = computed(() => editedIndex.value === -1 ? 'Tambah Pelanggan Baru' : 'Edit Pelanggan');

const isFormValid = computed(() => {
  return !!(editedItem.value.nama && editedItem.value.no_ktp && editedItem.value.email && 
           editedItem.value.no_telp && editedItem.value.alamat && editedItem.value.blok && 
           editedItem.value.unit);
});

// --- Lifecycle ---
onMounted(() => {
  fetchPelanggan();
  fetchHargaLayanan();
});

// --- Methods ---
async function fetchPelanggan() {
  loading.value = true;
  try {
    const response = await apiClient.get('/pelanggan/');
    pelangganList.value = response.data;
  } catch (error) { console.error("Gagal mengambil data pelanggan:", error); } 
  finally { loading.value = false; }
}

async function fetchHargaLayanan() {
  try {
    const response = await apiClient.get('/harga_layanan');
    hargaLayananList.value = response.data;
  } catch (error) { console.error("Gagal mengambil data harga layanan:", error); }
}

function openDialog(item?: Pelanggan) {
  editedIndex.value = item ? pelangganList.value.findIndex(p => p.id === item.id) : -1;
  editedItem.value = item ? { ...item } : { ...defaultItem };
  currentStep.value = 1; // Reset to first step
  dialog.value = true;
}

function closeDialog() {
  dialog.value = false;
  editedItem.value = { ...defaultItem };
  editedIndex.value = -1;
  currentStep.value = 1; // Reset step
}

async function savePelanggan() {
  if (!isFormValid.value) return;
  
  saving.value = true;
  try {
    if (editedIndex.value > -1) {
      await apiClient.patch(`/pelanggan/${editedItem.value.id}`, editedItem.value);
    } else {
      await apiClient.post('/pelanggan/', editedItem.value);
    }
    fetchPelanggan();
    closeDialog();
  } catch (error) { console.error("Gagal menyimpan data pelanggan:", error); } 
  finally { saving.value = false; }
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
    fetchPelanggan();
    closeDeleteDialog();
  } catch (error) { console.error("Gagal menghapus pelanggan:", error); }
  finally { deleting.value = false; }
}

// --- Helper Methods ---
function getBrandName(idBrand: string | null | undefined): string | null {
  if (!idBrand) return null;
  const brand = hargaLayananList.value.find(h => h.id_brand === idBrand);
  return brand?.brand || idBrand;
}

function getBrandColor(brandName: string | null): string {
  if (!brandName) return 'grey';
  const lowerBrandName = brandName.toLowerCase();

  if (lowerBrandName.includes('nagrak')) return ''; 
  if (lowerBrandName.includes('jakinet')) return 'error';
  if (lowerBrandName.includes('jelantik')) return 'info';
  
  return 'primary';
}

function formatDate(dateString: string | Date | undefined): string {
  if (!dateString) return 'N/A';
  const date = new Date(dateString);
  if (isNaN(date.getTime())) return 'Invalid Date';
  return date.toLocaleDateString('id-ID', {
    year: 'numeric', month: 'long', day: 'numeric'
  });
}
</script>

<style scoped>
/* Original gradient chip style */
.gradient-chip-nagrak {
  background: linear-gradient(to right, #ef4444, #3b82f6) !important;
  color: white !important;
  border: none;
}

/* Enhanced Form Styles */
.elegant-form-card {
  overflow: hidden;
  border: 1px solid rgba(124, 58, 237, 0.1);
  box-shadow: 0 20px 60px rgba(124, 58, 237, 0.15) !important;
}

.form-header-gradient {
  background: linear-gradient(135deg, #7c3aed 0%, #4f46e5 50%, #3b82f6 100%);
  position: relative;
}

.form-header-gradient::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, #fbbf24, #f59e0b, #d97706);
}

/* Progress Indicator */
.form-progress-indicator {
  padding: 0 24px;
}

.progress-step {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 16px;
  border-radius: 12px;
  background: #f8fafc;
  border: 2px solid #e2e8f0;
  min-width: 120px;
  transition: all 0.3s ease;
  position: relative;
}

.progress-step.active {
  background: linear-gradient(135deg, #7c3aed, #4f46e5);
  border-color: #7c3aed;
  color: white;
  transform: scale(1.05);
  box-shadow: 0 8px 25px rgba(124, 58, 237, 0.3);
}

.progress-step .v-icon {
  transition: all 0.3s ease;
}

.progress-step.active .v-icon {
  color: white !important;
}

.step-label {
  font-size: 12px;
  font-weight: 600;
  text-align: center;
}

.progress-line {
  flex: 1;
  height: 4px;
  background: linear-gradient(90deg, #e2e8f0, #cbd5e1);
  border-radius: 2px;
  margin: 0 16px;
  transition: all 0.3s ease;
}

.progress-line.active {
  background: linear-gradient(90deg, #7c3aed, #4f46e5);
  box-shadow: 0 2px 8px rgba(124, 58, 237, 0.3);
}

/* Form Sections */
.form-section {
  animation: fadeInUp 0.5s ease-out;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.section-header {
  display: flex;
  align-items: center;
  padding-bottom: 16px;
  border-bottom: 2px solid #f1f5f9;
  margin-bottom: 24px;
}

.section-header h3 {
  color: #1e293b;
  margin: 0;
}

/* Enhanced Input Styling */
.input-group {
  margin-bottom: 24px;
}

.input-label {
  display: flex;
  align-items: center;
  font-weight: 600;
  color: #374151;
  font-size: 14px;
  margin-bottom: 8px;
  letter-spacing: 0.025em;
}

.elegant-input :deep(.v-field) {
  border-radius: 12px !important;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.04);
  transition: all 0.3s ease;
  border: 2px solid transparent;
}

.elegant-input :deep(.v-field):hover {
  box-shadow: 0 4px 20px rgba(124, 58, 237, 0.1);
  border-color: rgba(124, 58, 237, 0.3);
}

.elegant-input :deep(.v-field--focused) {
  box-shadow: 0 4px 25px rgba(124, 58, 237, 0.2) !important;
  border-color: #7c3aed !important;
}

.elegant-input :deep(.v-field__input) {
  padding: 16px 20px;
  font-size: 15px;
  line-height: 1.4;
}

.elegant-input :deep(.v-field__input)::placeholder {
  color: #9ca3af;
  opacity: 1;
}

.elegant-input :deep(.v-field__outline) {
  --v-field-border-opacity: 0.12;
}

.elegant-input :deep(.v-field--error) {
  --v-field-border-color: #ef4444;
}

/* Form Row Spacing */
.form-row {
  margin: 0 -12px;
}

.form-row .v-col {
  padding: 0 12px 8px;
}

/* Enhanced Button Styles */
.nav-btn {
  min-width: 120px;
  height: 44px;
  border-radius: 10px;
  font-weight: 600;
  text-transform: none;
  letter-spacing: 0.025em;
  transition: all 0.3s ease;
}

.nav-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
}

.action-btn {
  min-width: 140px;
  height: 48px;
  border-radius: 12px;
  font-weight: 600;
  text-transform: none;
  letter-spacing: 0.025em;
  transition: all 0.3s ease;
}

.action-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

.save-btn {
  background: linear-gradient(135deg, #7c3aed, #4f46e5) !important;
  position: relative;
  overflow: hidden;
}

.save-btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  transition: left 0.5s;
}

.save-btn:hover::before {
  left: 100%;
}

.save-btn:disabled {
  opacity: 0.6;
  transform: none !important;
  box-shadow: none !important;
}

/* Card Actions Enhancement */
.v-card-actions {
  border-top: 1px solid rgba(0, 0, 0, 0.06);
  background: linear-gradient(to right, #fafafa, #f8fafc);
}

/* Responsive Design */
@media (max-width: 768px) {
  .form-progress-indicator {
    padding: 0 12px;
  }
  
  .progress-step {
    min-width: 80px;
    padding: 12px 8px;
  }
  
  .step-label {
    font-size: 11px;
  }
  
  .progress-line {
    margin: 0 8px;
  }
  
  .section-header h3 {
    font-size: 18px;
  }
  
  .nav-btn, .action-btn {
    min-width: 100px;
    font-size: 14px;
  }
  
  .elegant-input :deep(.v-field__input) {
    padding: 14px 16px;
    font-size: 14px;
  }
}

/* ===== PERBAIKAN UNTUK MODE GELAP (DARK MODE FIX) ===== */
.v-theme--dark .bg-grey-lighten-5 {
  background-color: rgba(var(--v-theme-surface-variant), 0.5) !important;
}

.v-theme--dark .v-card-actions.bg-grey-lighten-5 {
    background: linear-gradient(to right, rgb(var(--v-theme-surface)), rgba(var(--v-theme-surface-variant), 0.5)) !important;
    border-top: 1px solid rgba(var(--v-theme-on-surface), 0.12) !important;
}

.v-theme--dark .progress-step {
  background: rgba(var(--v-theme-on-surface), 0.08);
  border-color: rgba(var(--v-theme-on-surface), 0.12);
}

.v-theme--dark .progress-step .step-label,
.v-theme--dark .progress-step .v-icon:not(.v-icon--size-default) {
  color: rgba(var(--v-theme-on-surface), 0.87) !important;
}

.v-theme--dark .progress-line {
  background: linear-gradient(90deg, rgba(var(--v-theme-on-surface), 0.12), rgba(var(--v-theme-on-surface), 0.2));
}

.v-theme--dark .section-header {
  border-bottom: 2px solid rgba(var(--v-theme-on-surface), 0.12);
}

.v-theme--dark .section-header h3 {
  color: #FFFFFF;
}

.v-theme--dark .input-label {
  color: rgba(var(--v-theme-on-surface), 0.85);
}

.v-theme--dark .elegant-input :deep(.v-field) {
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
}

.v-theme--dark .elegant-input :deep(.v-field):hover {
  box-shadow: 0 4px 20px rgba(124, 58, 237, 0.2);
  border-color: rgba(124, 58, 237, 0.4);
}

/* Additional Polish */
.v-dialog > .v-overlay__content {
  animation: dialogSlideIn 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
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

/* Focus States */
.elegant-input :deep(.v-field--focused .v-field__outline) {
  --v-field-border-width: 2px;
  --v-field-border-color: #7c3aed;
}

/* Error States */
.elegant-input :deep(.v-field--error .v-field__outline) {
  --v-field-border-width: 2px;
  --v-field-border-color: #ef4444;
}

/* Loading States */
.save-btn.v-btn--loading {
  pointer-events: none;
}

.save-btn.v-btn--loading .v-btn__content {
  opacity: 0;
}

/* Enhanced Select Styling */
.elegant-input :deep(.v-select .v-field__append-inner) {
  padding-inline-start: 16px;
}

.elegant-input :deep(.v-select__selection-text) {
  color: #374151;
  font-weight: 500;
}

/* Textarea specific styles */
.elegant-input :deep(.v-textarea .v-field__input) {
  padding-top: 20px;
  padding-bottom: 20px;
}

/* Date input specific styles */
.elegant-input :deep(input[type="date"]) {
  color: #374151;
  font-weight: 500;
}

.elegant-input :deep(input[type="date"]::-webkit-calendar-picker-indicator) {
  color: #7c3aed;
  opacity: 0.7;
  cursor: pointer;
}

.elegant-input :deep(input[type="date"]::-webkit-calendar-picker-indicator):hover {
  opacity: 1;
  background-color: rgba(124, 58, 237, 0.1);
  border-radius: 4px;
}
</style>