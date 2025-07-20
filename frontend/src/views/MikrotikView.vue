<template>
  <v-container fluid class="pa-6">
    <!-- Header Section -->
    <div class="d-flex align-center mb-6">
      <div class="d-flex align-center">
        <v-avatar class="me-3" color="info" size="40">
          <v-icon color="white">mdi-server-network</v-icon>
        </v-avatar>
        <div>
          <h1 class="text-h4 font-weight-bold text-info">Mikrotik Servers</h1>
          <p class="text-subtitle-1 text-medium-emphasis mb-0">Kelola koneksi ke server Mikrotik Anda</p>
        </div>
      </div>
      <v-spacer></v-spacer>
      <v-btn 
        color="info" 
        size="large"
        elevation="2"
        @click="openDialog()"
        prepend-icon="mdi-plus"
        class="text-none"
      >
        Tambah Server
      </v-btn>
    </div>

    <!-- Main Data Table Card -->
    <v-card elevation="3" class="rounded-lg">
      <v-card-title class="d-flex align-center pa-6 bg-grey-lighten-5">
        <v-icon start icon="mdi-format-list-bulleted-square" color="info"></v-icon>
        <span class="text-h6 font-weight-bold">Daftar Server</span>
        <v-spacer></v-spacer>
        <v-chip color="info" variant="outlined" size="small">
          {{ servers.length }} servers
        </v-chip>
      </v-card-title>
      
      <v-data-table
        :headers="headers"
        :items="servers"
        :loading="loading"
        item-value="id"
        class="elevation-0"
        :items-per-page="10"
      >
        <template v-slot:item.name="{ item }">
          <div class="font-weight-bold">{{ item.name }}</div>
          <div class="text-caption text-medium-emphasis">{{ item.host_ip }}:{{ item.port }}</div>
        </template>

        <template v-slot:item.is_active="{ item }">
          <v-chip :color="item.is_active ? 'success' : 'grey'" size="small" variant="tonal">
            <v-icon start size="14">{{ item.is_active ? 'mdi-check-circle' : 'mdi-close-circle' }}</v-icon>
            {{ item.is_active ? 'Aktif' : 'Nonaktif' }}
          </v-chip>
        </template>

        <template v-slot:item.last_connection_status="{ item }">
            <v-chip :color="getConnectionColor(item.last_connection_status)" variant="tonal" size="small">
              <v-icon start size="14">{{ getConnectionIcon(item.last_connection_status) }}</v-icon>
              {{ item.last_connection_status || 'Belum diuji' }}
            </v-chip>
        </template>

        <template v-slot:item.actions="{ item }">
          <div class="d-flex justify-center ga-2">
            <v-btn 
              size="small" 
              variant="tonal" 
              color="teal" 
              @click="handleTestConnection(item)"
              class="text-none"
              :loading="testingConnectionId === item.id"
            >
              <v-icon start size="16">mdi-connection</v-icon>
              Test
            </v-btn>
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

    <!-- Enhanced Add/Edit Dialog -->
    <v-dialog v-model="dialog" max-width="700px" persistent>
      <v-card class="rounded-xl elevation-8 dialog-card">
        <!-- Enhanced Header with Gradient -->
        <v-card-title class="pa-0">
          <div class="dialog-header pa-6">
            <div class="d-flex align-center">
              <v-avatar class="me-4" color="white" size="48">
                <v-icon color="info" size="28">{{ editedIndex === -1 ? 'mdi-server-plus' : 'mdi-server-edit' }}</v-icon>
              </v-avatar>
              <div>
                <h2 class="text-h5 text-white font-weight-bold mb-1">{{ formTitle }}</h2>
                <p class="text-subtitle-2 text-blue-lighten-4 mb-0">
                  {{ editedIndex === -1 ? 'Tambahkan server Mikrotik baru ke sistem' : 'Perbarui informasi server Mikrotik' }}
                </p>
              </div>
            </div>
          </div>
        </v-card-title>

        <v-card-text class="pa-8">
          <v-form ref="serverForm" v-model="formValid">
            <!-- Server Information Section -->
            <div class="form-section mb-6">
              <div class="section-header mb-4">
                <v-icon class="me-2" color="info">mdi-information-outline</v-icon>
                <span class="text-h6 font-weight-bold text-info">Informasi Server</span>
              </div>
              
              <v-row class="ma-0">
                <v-col cols="12" class="pb-2">
                  <v-text-field 
                    v-model="editedItem.name" 
                    label="Nama Server" 
                    variant="outlined"
                    prepend-inner-icon="mdi-server"
                    :rules="[rules.required]"
                    color="info"
                    class="elegant-input"
                    hint="Masukkan nama identifikasi untuk server ini"
                  ></v-text-field>
                </v-col>
                
                <v-col cols="12" md="8" class="pb-2">
                  <v-text-field 
                    v-model="editedItem.host_ip" 
                    label="Host / IP Address" 
                    variant="outlined"
                    prepend-inner-icon="mdi-ip-network"
                    :rules="[rules.required]"
                    color="info"
                    class="elegant-input"
                    hint="IP Address atau hostname server Mikrotik"
                  ></v-text-field>
                </v-col>
                
                <v-col cols="12" md="4" class="pb-2">
                  <v-text-field 
                    v-model.number="editedItem.port" 
                    label="Port API" 
                    type="number"
                    variant="outlined"
                    prepend-inner-icon="mdi-ethernet"
                    color="info"
                    class="elegant-input"
                    hint="Default: 8728"
                  ></v-text-field>
                </v-col>
              </v-row>
            </div>

            <!-- Authentication Section -->
            <div class="form-section mb-6">
              <div class="section-header mb-4">
                <v-icon class="me-2" color="deep-orange">mdi-shield-key</v-icon>
                <span class="text-h6 font-weight-bold text-deep-orange">Kredensial Login</span>
              </div>
              
              <v-row class="ma-0">
                <v-col cols="12" md="6" class="pb-2">
                  <v-text-field 
                    v-model="editedItem.username" 
                    label="Username" 
                    variant="outlined"
                    prepend-inner-icon="mdi-account"
                    :rules="[rules.required]"
                    color="deep-orange"
                    class="elegant-input"
                    autocomplete="username"
                  ></v-text-field>
                </v-col>
                
                <v-col cols="12" md="6" class="pb-2">
                  <v-text-field 
                    v-model="editedItem.password" 
                    label="Password" 
                    :type="showPassword ? 'text' : 'password'"
                    variant="outlined"
                    prepend-inner-icon="mdi-lock"
                    :append-inner-icon="showPassword ? 'mdi-eye' : 'mdi-eye-off'"
                    @click:append-inner="showPassword = !showPassword"
                    color="deep-orange"
                    class="elegant-input"
                    :placeholder="editedIndex > -1 ? 'Kosongkan jika tidak berubah' : 'Masukkan password'"
                    autocomplete="current-password"
                  ></v-text-field>
                </v-col>
              </v-row>
            </div>

            <!-- Server Status Section -->
            <div class="form-section">
              <div class="section-header mb-4">
                <v-icon class="me-2" color="success">mdi-toggle-switch</v-icon>
                <span class="text-h6 font-weight-bold text-success">Status Server</span>
              </div>
              
              <v-card variant="tonal" color="success" class="pa-4">
                <div class="d-flex align-center justify-space-between">
                  <div>
                    <h3 class="text-subtitle-1 font-weight-bold mb-1">Aktivasi Server</h3>
                    <p class="text-body-2 text-medium-emphasis mb-0">
                      {{ editedItem.is_active ? 'Server akan aktif dan dapat digunakan' : 'Server akan dinonaktifkan sementara' }}
                    </p>
                  </div>
                  <v-switch 
                    v-model="editedItem.is_active" 
                    color="success"
                    size="large"
                    inset
                    :label="editedItem.is_active ? 'Aktif' : 'Nonaktif'"
                  ></v-switch>
                </div>
              </v-card>
            </div>
          </v-form>
        </v-card-text>

        <!-- Enhanced Footer -->
        <v-card-actions class="pa-6 pt-0">
          <v-spacer></v-spacer>
          <v-btn 
            variant="outlined" 
            size="large" 
            @click="closeDialog"
            class="text-none me-3"
          >
            <v-icon start>mdi-close</v-icon>
            Batal
          </v-btn>
          <v-btn 
            color="info" 
            variant="flat" 
            size="large"
            @click="saveServer" 
            :loading="saving"
            :disabled="!formValid"
            class="text-none"
            elevation="2"
          >
            <v-icon start>{{ editedIndex === -1 ? 'mdi-content-save-plus' : 'mdi-content-save-edit' }}</v-icon>
            {{ editedIndex === -1 ? 'Tambah Server' : 'Update Server' }}
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Enhanced Delete Dialog -->
    <v-dialog v-model="dialogDelete" max-width="500px">
      <v-card class="rounded-xl elevation-8">
        <v-card-text class="pa-8 text-center">
          <v-avatar color="error" size="80" class="mb-4">
            <v-icon color="white" size="40">mdi-delete-alert</v-icon>
          </v-avatar>
          <h2 class="text-h5 font-weight-bold text-error mb-3">Konfirmasi Hapus</h2>
          <p class="text-body-1 text-medium-emphasis mb-4">
            Anda yakin ingin menghapus server 
            <strong class="text-error">{{ itemToDelete?.name }}</strong>?
          </p>
          <v-alert type="warning" variant="tonal" class="text-start">
            <template v-slot:prepend>
              <v-icon>mdi-alert-circle</v-icon>
            </template>
            Tindakan ini tidak dapat dibatalkan. Semua konfigurasi yang terkait dengan server ini akan hilang.
          </v-alert>
        </v-card-text>
        <v-card-actions class="pa-6 pt-0">
          <v-spacer></v-spacer>
          <v-btn 
            variant="outlined" 
            size="large" 
            @click="closeDeleteDialog"
            class="text-none me-3"
          >
            Batal
          </v-btn>
          <v-btn 
            color="error" 
            variant="flat" 
            size="large"
            @click="confirmDelete" 
            :loading="deleting"
            class="text-none"
          >
            <v-icon start>mdi-delete</v-icon>
            Ya, Hapus
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Snackbar for notifications -->
    <v-snackbar v-model="snackbar.show" :color="snackbar.color" timeout="4000" location="top right">
      <v-icon start>{{ snackbar.icon }}</v-icon>
      {{ snackbar.text }}
    </v-snackbar>

  </v-container>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import apiClient from '@/services/api';

// --- Type Definitions ---
interface MikrotikServer {
  id: number | null;
  name: string;
  host_ip: string;
  port: number;
  username: string;
  password?: string;
  is_active: boolean;
}

// --- State ---
const servers = ref<any[]>([]);
const loading = ref(true);
const saving = ref(false);
const deleting = ref(false);
const dialog = ref(false);
const dialogDelete = ref(false);
const editedIndex = ref(-1);
const testingConnectionId = ref<number | null>(null);
const showPassword = ref(false);
const formValid = ref(false);

const defaultItem: MikrotikServer = { 
  id: null, 
  name: '', 
  host_ip: '', 
  port: 8728, 
  username: '', 
  password: '', 
  is_active: true 
};
const editedItem = ref<MikrotikServer>({ ...defaultItem });
const itemToDelete = ref<any>(null);

const snackbar = ref({ show: false, text: '', color: 'success', icon: 'mdi-check-circle' });

// --- Validation Rules ---
const rules = {
  required: (value: any) => !!value || 'Field ini wajib diisi',
};

// --- Headers ---
const headers = [
  { title: 'Server Info', key: 'name', sortable: true },
  { title: 'ROS Version', key: 'ros_version', sortable: false, align: 'center' },
  { title: 'Status', key: 'is_active', align: 'center' },
  { title: 'Koneksi Terakhir', key: 'last_connection_status', align: 'center' },
  { title: 'Actions', key: 'actions', sortable: false, align: 'center', width: '320px' },
] as const;

// --- Computed Properties ---
const formTitle = computed(() => editedIndex.value === -1 ? 'Tambah Server Baru' : 'Edit Server');

// --- Lifecycle ---
onMounted(() => {
  fetchServers();
});

// --- Methods ---
async function fetchServers() {
  loading.value = true;
  try {
    const response = await apiClient.get('/mikrotik_servers/');
    servers.value = response.data;
  } catch (error) { console.error(error); } 
  finally { loading.value = false; }
}

function openDialog(item?: any) {
  editedIndex.value = item ? servers.value.indexOf(item) : -1;
  editedItem.value = item ? { ...item, password: '' } : { ...defaultItem };
  showPassword.value = false;
  dialog.value = true;
}

function closeDialog() {
  dialog.value = false;
  editedItem.value = { ...defaultItem };
  editedIndex.value = -1;
  showPassword.value = false;
}

async function saveServer() {
  saving.value = true;
  const payload: Partial<MikrotikServer> = { ...editedItem.value };
  
  if (editedIndex.value > -1 && !payload.password) {
    delete payload.password;
  }

  try {
    if (editedIndex.value > -1) {
      await apiClient.patch(`/mikrotik_servers/${payload.id}`, payload);
    } else {
      await apiClient.post('/mikrotik_servers/', payload);
    }
    fetchServers();
    closeDialog();
    showSnackbar(
      editedIndex.value > -1 ? 'Server berhasil diperbarui!' : 'Server baru berhasil ditambahkan!', 
      'success'
    );
  } catch (error) { 
    console.error(error);
    showSnackbar('Gagal menyimpan server. Silakan coba lagi.', 'error');
  } 
  finally { saving.value = false; }
}

async function handleTestConnection(item: any) {
  testingConnectionId.value = item.id;
  try {
    const response = await apiClient.post(`/mikrotik_servers/${item.id}/test_connection`);
    showSnackbar(`Berhasil terhubung! ROS: ${response.data.ros_version || response.data.router_os_version}`, 'success');
    fetchServers();
  } catch (error: any) {
    const detail = error.response?.data?.detail || 'Gagal terhubung ke server.';
    showSnackbar(`Error: ${detail}`, 'error');
    fetchServers();
  } finally {
    testingConnectionId.value = null;
  }
}

function openDeleteDialog(item: any) {
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
    await apiClient.delete(`/mikrotik_servers/${itemToDelete.value.id}`);
    fetchServers();
    closeDeleteDialog();
    showSnackbar('Server berhasil dihapus!', 'success');
  } catch (error) { 
    console.error(error);
    showSnackbar('Gagal menghapus server. Silakan coba lagi.', 'error');
  }
  finally { deleting.value = false; }
}

// --- Helper Methods ---
function showSnackbar(text: string, color: 'success' | 'error' | 'info') {
  snackbar.value = {
    show: true,
    text,
    color,
    icon: color === 'success' ? 'mdi-check-circle' : 'mdi-alert-circle'
  };
}

function getConnectionColor(status: string | null): string {
    if (status === 'Success' || status === 'Connected') return 'success';
    if (status === 'Failed') return 'error';
    return 'grey';
}

function getConnectionIcon(status: string | null): string {
    if (status === 'Success' || status === 'Connected') return 'mdi-check-circle';
    if (status === 'Failed') return 'mdi-close-circle';
    return 'mdi-help-circle';
}
</script>

<style scoped>
.dialog-card {
  background: #fafafa;
}

.dialog-header {
  background: linear-gradient(135deg, #2196F3 0%, #21CBF3 100%);
  position: relative;
}

.dialog-header::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: url('data:image/svg+xml,<svg width="60" height="60" viewBox="0 0 60 60" xmlns="http://www.w3.org/2000/svg"><g fill="none" fill-rule="evenodd"><g fill="%23ffffff" fill-opacity="0.1"><circle cx="30" cy="30" r="2"/></g></svg>');
  opacity: 0.3;
}

.form-section {
  position: relative;
}

.section-header {
  display: flex;
  align-items: center;
  padding-bottom: 8px;
  border-bottom: 2px solid #f5f5f5;
}

.elegant-input :deep(.v-field) {
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
  transition: all 0.3s ease;
}

.elegant-input :deep(.v-field:hover) {
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.elegant-input :deep(.v-field--focused) {
  box-shadow: 0 4px 20px rgba(33, 150, 243, 0.2);
}

.v-card {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.v-btn {
  transition: all 0.3s ease;
  text-transform: none;
  font-weight: 600;
}

.v-btn:hover {
  transform: translateY(-2px);
}

.v-switch :deep(.v-switch__thumb) {
  transition: all 0.3s ease;
}
</style>