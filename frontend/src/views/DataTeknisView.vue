<template>
  <v-container fluid class="pa-6">
    <div class="d-flex align-center mb-8">
      <div class="d-flex align-center">
        <v-avatar 
          class="me-4 gradient-avatar" 
          size="56"
          :style="{ 
            background: 'linear-gradient(135deg, #00ACC1 0%, #006064 100%)',
            boxShadow: '0 8px 24px rgba(0, 172, 193, 0.3)'
          }"
        >
          <v-icon color="white" size="28">mdi-lan</v-icon>
        </v-avatar>
        <div>
          <h1 class="text-h3 font-weight-bold mb-1 header-gradient">
            Data Teknis Pelanggan
          </h1>
          <p class="text-subtitle-1 text-medium-emphasis mb-0 opacity-80">
            Kelola informasi teknis dan infrastruktur pelanggan
          </p>
        </div>
      </div>
      <v-spacer></v-spacer>
      
      <v-btn 
        color="primary" 
        size="large"
        elevation="8"
        @click="openDialog()"
        prepend-icon="mdi-plus-network"
        class="text-none modern-btn px-8 py-3"
        :style="{
          background: 'linear-gradient(135deg, #00ACC1 0%, #006064 100%)',
          borderRadius: '16px',
          textTransform: 'none',
          fontWeight: '600',
          letterSpacing: '0.5px'
        }"
      >
        <template v-slot:prepend>
          <v-icon class="me-2 icon-bounce">mdi-plus-network</v-icon>
        </template>
        Tambah Data Teknis
      </v-btn>
    </div>

    <v-row class="mb-6" no-gutters>
      <v-col cols="12" sm="6" md="3" class="pa-2">
        <v-card 
          class="stats-card pa-4 h-100" 
          :style="{
            background: 'linear-gradient(135deg, rgba(76, 175, 80, 0.1) 0%, rgba(76, 175, 80, 0.05) 100%)',
            border: '1px solid rgba(76, 175, 80, 0.2)',
            backdropFilter: 'blur(10px)'
          }"
          elevation="2"
        >
          <div class="d-flex align-center">
            <v-avatar color="success" size="48" class="me-3">
              <v-icon color="white">mdi-check-network</v-icon>
            </v-avatar>
            <div>
              <div class="text-h5 font-weight-bold">{{ dataTeknisList.length }}</div>
              <div class="text-caption text-medium-emphasis">Total Pelanggan</div>
            </div>
          </div>
        </v-card>
      </v-col>
      
      <v-col cols="12" sm="6" md="3" class="pa-2">
        <v-card 
          class="stats-card pa-4 h-100"
          :style="{
            background: 'linear-gradient(135deg, rgba(255, 152, 0, 0.1) 0%, rgba(255, 152, 0, 0.05) 100%)',
            border: '1px solid rgba(255, 152, 0, 0.2)',
            backdropFilter: 'blur(10px)'
          }"
          elevation="2"
        >
          <div class="d-flex align-center">
            <v-avatar color="warning" size="48" class="me-3">
              <v-icon color="white">mdi-signal</v-icon>
            </v-avatar>
            <div>
              <div class="text-h5 font-weight-bold">{{ getSignalStats().good }}</div>
              <div class="text-caption text-medium-emphasis">Sinyal Baik</div>
            </div>
          </div>
        </v-card>
      </v-col>

      <v-col cols="12" sm="6" md="3" class="pa-2">
        <v-card 
          class="stats-card pa-4 h-100"
          :style="{
            background: 'linear-gradient(135deg, rgba(244, 67, 54, 0.1) 0%, rgba(244, 67, 54, 0.05) 100%)',
            border: '1px solid rgba(244, 67, 54, 0.2)',
            backdropFilter: 'blur(10px)'
          }"
          elevation="2"
        >
          <div class="d-flex align-center">
            <v-avatar color="error" size="48" class="me-3">
              <v-icon color="white">mdi-alert</v-icon>
            </v-avatar>
            <div>
              <div class="text-h5 font-weight-bold">{{ getSignalStats().poor }}</div>
              <div class="text-caption text-medium-emphasis">Sinyal Lemah</div>
            </div>
          </div>
        </v-card>
      </v-col>

      <v-col cols="12" sm="6" md="3" class="pa-2">
        <v-card 
          class="stats-card pa-4 h-100"
          :style="{
            background: 'linear-gradient(135deg, rgba(103, 58, 183, 0.1) 0%, rgba(103, 58, 183, 0.05) 100%)',
            border: '1px solid rgba(103, 58, 183, 0.2)',
            backdropFilter: 'blur(10px)'
          }"
          elevation="2"
        >
          <div class="d-flex align-center">
            <v-avatar color="deep-purple" size="48" class="me-3">
              <v-icon color="white">mdi-router-network</v-icon>
            </v-avatar>
            <div>
              <div class="text-h5 font-weight-bold">{{ getUniqueOLTCount() }}</div>
              <div class="text-caption text-medium-emphasis">OLT Aktif</div>
            </div>
          </div>
        </v-card>
      </v-col>
    </v-row>

    <v-card 
      elevation="8" 
      class="modern-card overflow-hidden"
      :style="{
        borderRadius: '20px',
        backdropFilter: 'blur(20px)',
        background: $vuetify.theme.current.dark 
          ? 'rgba(30, 30, 30, 0.8)' 
          : 'rgba(255, 255, 255, 0.9)',
        border: $vuetify.theme.current.dark 
          ? '1px solid rgba(255, 255, 255, 0.1)' 
          : '1px solid rgba(0, 0, 0, 0.05)'
      }"
    >
      <v-card-title 
        class="pa-6 d-flex align-center"
        :style="{
          background: 'linear-gradient(135deg, rgba(0, 172, 193, 0.1) 0%, rgba(0, 96, 100, 0.05) 100%)',
          borderBottom: '1px solid rgba(0, 172, 193, 0.2)'
        }"
      >
        <v-icon class="me-3 text-primary" size="24">mdi-table</v-icon>
        <span class="text-h5 font-weight-bold">Daftar Infrastruktur Pelanggan</span>
        <v-spacer></v-spacer>
        
        <v-text-field
          v-model="searchQuery"
          prepend-inner-icon="mdi-magnify"
          label="Cari pelanggan..."
          variant="outlined"
          density="compact"
          hide-details
          class="search-field"
          :style="{ maxWidth: '300px' }"
          clearable
        ></v-text-field>
      </v-card-title>

      <v-data-table
        :headers="headers"
        :items="filteredDataTeknisList"
        :loading="loading"
        item-value="id"
        class="elevation-0 modern-table"
        :items-per-page="10"
        :loading-text="'Memuat data...'"
        v-model:expanded="expanded"
        show-expand
      >
        <template v-slot:loading>
          <div class="text-center pa-8">
            <v-progress-circular indeterminate color="primary" size="64" width="6"></v-progress-circular>
            <div class="mt-4 text-h6">Memuat data...</div>
          </div>
        </template>

        <template v-slot:item.pelanggan_id="{ item }">
          <div class="d-flex align-center py-2">
            <v-avatar :color="getAvatarColor(item.pelanggan_id)" size="40" class="me-3" :style="{ boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)' }">
              <span class="text-white font-weight-bold">{{ getPelangganInitials(item.pelanggan_id) }}</span>
            </v-avatar>
            <div>
              <div class="font-weight-bold text-body-1">{{ getPelangganName(item.pelanggan_id) }}</div>
              <div class="text-caption text-medium-emphasis">ID: {{ item.id_pelanggan }}</div>
            </div>
          </div>
        </template>

        <template v-slot:item.ip_pelanggan="{ item }">
          <v-chip size="small" variant="tonal" color="primary" class="font-mono" :style="{ fontFamily: 'monospace' }">
            <v-icon start size="16">mdi-ip-network</v-icon>
            {{ item.ip_pelanggan }}
          </v-chip>
        </template>

        <template v-slot:item.olt="{ item }">
          <div class="d-flex align-center">
            <v-icon class="me-2 text-primary">mdi-router-network</v-icon>
            <div>
              <div class="font-weight-medium">{{ item.olt }}</div>
              <div v-if="item.olt_custom" class="text-caption text-medium-emphasis">{{ item.olt_custom }}</div>
            </div>
          </div>
        </template>

        <template v-slot:item.onu_power="{ item }">
          <div class="text-center">
            <v-chip :color="getOnuPowerColor(item.onu_power)" size="small" variant="flat" class="font-weight-bold px-3" :style="{ minWidth: '80px', borderRadius: '12px', boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)' }">
              <v-icon :icon="getOnuPowerIcon(item.onu_power)" start size="16"></v-icon>
              {{ item.onu_power }} dBm
            </v-chip>
            <div class="text-caption mt-1 text-medium-emphasis">{{ getOnuPowerStatus(item.onu_power) }}</div>
          </div>
        </template>

        <template v-slot:item.actions="{ item }">
            <div class="d-flex justify-center gap-2">
                <v-btn 
                size="small" 
                variant="tonal" 
                color="primary" 
                @click="openDialog(item)"
                class="action-btn"
                :style="{ borderRadius: '8px' }"
                >
                <v-icon size="16" class="me-1">mdi-pencil</v-icon>
                Edit
                </v-btn>
                <v-btn 
                size="small" 
                variant="tonal" 
                color="error" 
                @click="openDeleteDialog(item)"
                class="action-btn"
                :style="{ borderRadius: '8px' }"
                >
                <v-icon size="16" class="me-1">mdi-delete</v-icon>
                Hapus
                </v-btn>
            </div>
            </template>

        <template v-slot:expanded-row="{ columns, item }">
          <tr>
            <td :colspan="columns.length">
              <v-card flat class="pa-4 my-2" color="rgba(0, 172, 193, 0.05)">
                <div class="d-flex justify-space-between align-center mb-4">
                  <h4 class="text-h6 font-weight-bold text-cyan-darken-2">Detail Lengkap Infrastruktur</h4>
                  <v-chip size="small" variant="tonal" color="cyan-darken-2">
                    ID Pelanggan (PPPoE): {{ item.id_pelanggan }}
                  </v-chip>
                </div>
                <v-row>
                  <v-col cols="12" md="4">
                    <v-list-item-title class="font-weight-bold mb-2">Info Jaringan</v-list-item-title>
                    <v-list density="compact">
                      <v-list-item prepend-icon="mdi-key-variant">
                        <v-list-item-title>Password: {{ item.password_pppoe }}</v-list-item-title>
                      </v-list-item>
                      <v-list-item prepend-icon="mdi-account-details">
                        <v-list-item-title>Profile: {{ item.profile_pppoe }}</v-list-item-title>
                      </v-list-item>
                      <v-list-item prepend-icon="mdi-lan">
                        <v-list-item-title>VLAN: {{ item.id_vlan }}</v-list-item-title>
                      </v-list-item>
                    </v-list>
                  </v-col>
                  <v-col cols="12" md="4">
                    <v-list-item-title class="font-weight-bold mb-2">Info Infrastruktur</v-list-item-title>
                    <v-list density="compact">
                      <v-list-item prepend-icon="mdi-timeline">
                        <v-list-item-title>PON: {{ item.pon }}</v-list-item-title>
                      </v-list-item>
                      <v-list-item prepend-icon="mdi-cable-data">
                        <v-list-item-title>OTB: {{ item.otb }}</v-list-item-title>
                      </v-list-item>
                      <v-list-item prepend-icon="mdi-access-point-network">
                        <v-list-item-title>ODC: {{ item.odc }}</v-list-item-title>
                      </v-list-item>
                      <v-list-item prepend-icon="mdi-distribution-point">
                        <v-list-item-title>ODP: {{ item.odp }}</v-list-item-title>
                      </v-list-item>
                    </v-list>
                  </v-col>
                  <v-col cols="12" md="4">
                    <v-list-item-title class="font-weight-bold mb-2">Bukti Speedtest</v-list-item-title>
                    <v-img v-if="item.speedtest_proof" :src="`${apiClient.defaults.baseURL}${item.speedtest_proof}`" height="150" class="rounded-lg elevation-2" cover>
                      <template v-slot:placeholder>
                        <div class="d-flex align-center justify-center fill-height">
                          <v-progress-circular indeterminate color="grey-lighten-4"></v-progress-circular>
                        </div>
                      </template>
                    </v-img>
                    <div v-else class="text-medium-emphasis mt-2">
                      Tidak ada gambar.
                    </div>
                  </v-col>
                </v-row>
              </v-card>
            </td>
          </tr>
        </template>

        <template v-slot:no-data>
          <div class="text-center pa-8">
            <v-icon size="64" color="grey-lighten-1" class="mb-4">mdi-database-off</v-icon>
            <div class="text-h6 text-medium-emphasis mb-2">Tidak ada data</div>
            <div class="text-body-2 text-medium-emphasis">Belum ada data teknis yang tersedia</div>
          </div>
        </template>
      </v-data-table>
    </v-card>

    <v-dialog v-model="dialog" max-width="900px" persistent scrollable :style="{ zIndex: 2000 }">
      <v-card class="modern-dialog overflow-hidden" :style="{ borderRadius: '24px', backdropFilter: 'blur(20px)' }" elevation="24">
        <v-card-title class="pa-0" :style="{ background: 'linear-gradient(135deg, #00ACC1 0%, #006064 100%)', color: 'white' }">
          <div class="pa-6 d-flex align-center">
            <v-icon class="me-3" size="28">mdi-plus-network-outline</v-icon>
            <div>
              <div class="text-h4 font-weight-bold">{{ formTitle }}</div>
              <div class="text-body-2 opacity-90 mt-1">Lengkapi informasi teknis pelanggan</div>
            </div>
          </div>
        </v-card-title>

        <v-stepper 
  v-model="currentStep" 
  class="elevation-0"
  :style="{
    background: 'transparent'
  }"
>
  <v-stepper-header class="px-6 pt-6">
    <v-stepper-item 
      title="Info Jaringan" 
      :value="1" 
      editable
      :color="currentStep >= 1 ? 'primary' : 'grey'"
      :complete="currentStep > 1"
      class="stepper-item"
    >
      <template v-slot:icon>
        <v-icon>{{ currentStep > 1 ? 'mdi-check' : 'mdi-network' }}</v-icon>
      </template>
    </v-stepper-item>
    
    <v-divider class="mx-4"></v-divider>
    
    <v-stepper-item 
      title="Infrastruktur" 
      :value="2" 
      editable
      :color="currentStep >= 2 ? 'primary' : 'grey'"
      :complete="currentStep > 2"
      class="stepper-item"
    >
      <template v-slot:icon>
        <v-icon>{{ currentStep > 2 ? 'mdi-check' : 'mdi-router-network' }}</v-icon>
      </template>
    </v-stepper-item>
    
        <v-divider class="mx-4"></v-divider>
        
        <v-stepper-item 
        title="Detail ONU" 
        :value="3" 
        editable
        :color="currentStep >= 3 ? 'primary' : 'grey'"
        class="stepper-item"
        >
        <template v-slot:icon>
            <v-icon>mdi-signal</v-icon>
        </template>
        </v-stepper-item>
    </v-stepper-header>

    <v-stepper-window class="stepper-content">
        <v-stepper-window-item :value="1">
        <v-card-text class="pa-6">
            <div class="mb-6">
            <h3 class="text-h6 font-weight-bold mb-2 d-flex align-center">
                <v-icon class="me-2 text-primary">mdi-account-network</v-icon>
                Informasi Pelanggan
            </h3>
            <p class="text-body-2 text-medium-emphasis">
                Pilih pelanggan dan atur konfigurasi jaringan
            </p>
            </div>
            <v-select
            v-model="editedItem.pelanggan_id"
            :items="pelangganForSelect"
            item-title="nama"
            item-value="id"
            label="Pilih Pelanggan"
            :disabled="isEditMode"
            hint="Hanya pelanggan yang belum memiliki data teknis"
            persistent-hint
            variant="outlined"
            prepend-inner-icon="mdi-account"
            class="mb-6"
            :style="{ borderRadius: '12px' }"
            >
            <template v-slot:item="{ props, item }">
                <v-list-item v-bind="props" class="pa-3">
                <template v-slot:prepend>
                    <v-avatar :color="getAvatarColor(item.raw.id)" size="40">
                    <span class="text-white font-weight-bold">
                        {{ item.raw.nama.charAt(0).toUpperCase() }}
                    </span>
                    </v-avatar>
                </template>
                </v-list-item>
            </template>
            </v-select>
            <v-row>
            <v-col cols="12" sm="6">
                <v-text-field 
                v-model="editedItem.id_pelanggan" 
                label="ID Pelanggan (PPPoE Username)"
                variant="outlined"
                prepend-inner-icon="mdi-account-key"
                :style="{ borderRadius: '12px' }"
                ></v-text-field>
            </v-col>
            <v-col cols="12" sm="6">
                <v-text-field 
                v-model="editedItem.password_pppoe" 
                label="Password PPPoE"
                variant="outlined"
                prepend-inner-icon="mdi-key"
                type="password"
                :style="{ borderRadius: '12px' }"
                ></v-text-field>
            </v-col>
            <v-col cols="12" sm="6">
                <v-text-field 
                v-model="editedItem.ip_pelanggan" 
                label="IP Pelanggan"
                variant="outlined"
                prepend-inner-icon="mdi-ip"
                :style="{ borderRadius: '12px' }"
                ></v-text-field>
            </v-col>
            <v-col cols="12" sm="6">
            <v-combobox
                v-model="editedItem.profile_pppoe"
                :items="pppoeProfiles"
                label="Profile PPPoE"
                variant="outlined"
                prepend-inner-icon="mdi-account-settings"
                placeholder="Ketik atau pilih profil"
                :style="{ borderRadius: '12px' }"
            ></v-combobox>
            </v-col>
            <v-col cols="12" sm="6">
                <v-text-field 
                v-model="editedItem.id_vlan" 
                label="ID VLAN"
                variant="outlined"
                prepend-inner-icon="mdi-lan"
                :style="{ borderRadius: '12px' }"
                ></v-text-field>
            </v-col>
            </v-row>
        </v-card-text>
        </v-stepper-window-item>

        <v-stepper-window-item :value="2">
    <v-card-text class="pa-6">
        <div class="mb-6">
        <h3 class="text-h6 font-weight-bold mb-2 d-flex align-center">
            <v-icon class="me-2 text-primary">mdi-router-network</v-icon>
            Konfigurasi Infrastruktur
        </h3>
        <p class="text-body-2 text-medium-emphasis">
            Atur komponen infrastruktur jaringan
        </p>
        </div>
        <v-row>
        <v-col cols="12" sm="6">
            <v-select
                v-model="editedItem.olt"
                :items="mikrotikServers"
                item-title="name"
                item-value="name"
                label="OLT"
                variant="outlined"
                prepend-inner-icon="mdi-router"
                placeholder="Pilih server OLT"
                :style="{ borderRadius: '12px' }"
            ></v-select>
            </v-col>
        <v-col cols="12" sm="6">
            <v-text-field 
            v-model="editedItem.olt_custom" 
            label="OLT Custom (Opsional)"
            variant="outlined"
            prepend-inner-icon="mdi-router-plus"
            :style="{ borderRadius: '12px' }"
            ></v-text-field>
        </v-col>
        <v-col cols="12" sm="3">
            <v-text-field 
            v-model.number="editedItem.pon" 
            label="PON" 
            type="number"
            variant="outlined"
            prepend-inner-icon="mdi-timeline"
            :style="{ borderRadius: '12px' }"
            ></v-text-field>
        </v-col>
        <v-col cols="12" sm="3">
            <v-text-field 
            v-model.number="editedItem.otb" 
            label="OTB" 
            type="number"
            variant="outlined"
            prepend-inner-icon="mdi-cable-data"
            :style="{ borderRadius: '12px' }"
            ></v-text-field>
        </v-col>
        <v-col cols="12" sm="3">
            <v-text-field 
            v-model.number="editedItem.odc" 
            label="ODC" 
            type="number"
            variant="outlined"
            prepend-inner-icon="mdi-access-point-network"
            :style="{ borderRadius: '12px' }"
            ></v-text-field>
        </v-col>
        <v-col cols="12" sm="3">
            <v-text-field 
            v-model.number="editedItem.odp" 
            label="ODP" 
            type="number"
            variant="outlined"
            prepend-inner-icon="mdi-distribution-point"
            :style="{ borderRadius: '12px' }"
            ></v-text-field>
        </v-col>
        </v-row>
    </v-card-text>
    </v-stepper-window-item>

        <v-stepper-window-item :value="3">
        <v-card-text class="pa-6">
            <div class="mb-6">
            <h3 class="text-h6 font-weight-bold mb-2 d-flex align-center">
                <v-icon class="me-2 text-primary">mdi-signal</v-icon>
                Detail ONU & Performance
            </h3>
            </div>
            <v-row>
            <v-col cols="12" sm="6">
                <v-text-field 
                v-model.number="editedItem.onu_power" 
                label="ONU Power" 
                type="number" 
                suffix="dBm" 
                variant="outlined" 
                persistent-hint
                ></v-text-field>
            </v-col>
            <v-col cols="12" sm="6">
                <v-file-input 
                ref="fileInputComponent" 
                label="Unggah Bukti Speedtest" 
                variant="outlined" 
                prepend-icon="" 
                prepend-inner-icon="mdi-camera" 
                accept="image/png, image/jpeg, image/webp" 
                clearable 
                hint="Ganti gambar yang ada dengan unggah yang baru"
                ></v-file-input>
            </v-col>
            <v-col cols="12">
                <v-img 
                v-if="imagePreviewUrl" 
                :src="imagePreviewUrl" 
                height="200" 
                class="rounded-lg elevation-2" 
                cover
                >
                <template v-slot:placeholder>
                    <div class="d-flex align-center justify-center fill-height">
                    <v-progress-circular indeterminate color="grey-lighten-4"></v-progress-circular>
                    </div>
                </template>
                </v-img>
                <div v-else class="text-center text-medium-emphasis pa-8 border rounded-lg">
                Tidak ada gambar bukti speedtest.
                </div>
            </v-col>
            </v-row>
        </v-card-text>
        </v-stepper-window-item>
    </v-stepper-window>
    </v-stepper>

        <v-card-actions class="pa-6 pt-0" :style="{ background: 'rgba(0, 0, 0, 0.02)' }">
          <v-btn v-if="currentStep > 1" color="grey" variant="outlined" @click="currentStep--" prepend-icon="mdi-chevron-left" class="me-2" :style="{ borderRadius: '12px' }">
            Sebelumnya
          </v-btn>
          <v-spacer></v-spacer>
          <v-btn color="grey" variant="outlined" @click="closeDialog" class="me-3" :style="{ borderRadius: '12px' }">
            Batal
          </v-btn>
          <v-btn v-if="currentStep < 3" color="primary" variant="flat" @click="currentStep++" append-icon="mdi-chevron-right" :style="{ borderRadius: '12px' }">
            Lanjut
          </v-btn>
          <v-btn v-else color="primary" variant="flat" @click="saveDataTeknis" prepend-icon="mdi-content-save" :style="{ borderRadius: '12px' }" :loading="saving">
            Simpan
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-dialog v-model="dialogDelete" max-width="500px">
      <v-card class="modern-dialog" :style="{ borderRadius: '20px' }" elevation="16">
        <v-card-title class="pa-6 d-flex align-center" :style="{ background: 'linear-gradient(135deg, rgba(244, 67, 54, 0.1) 0%, rgba(244, 67, 54, 0.05) 100%)', borderBottom: '1px solid rgba(244, 67, 54, 0.2)' }">
          <v-avatar color="error" size="48" class="me-4">
            <v-icon color="white">mdi-alert</v-icon>
          </v-avatar>
          <div>
            <div class="text-h5 font-weight-bold">Konfirmasi Hapus</div>
            <div class="text-body-2 opacity-80">Tindakan ini tidak dapat dibatalkan</div>
          </div>
        </v-card-title>
        <v-card-text class="pa-6">
          <div class="text-center">
            <v-icon size="64" color="error" class="mb-4 opacity-60">
              mdi-delete-alert
            </v-icon>
            <p class="text-body-1 mb-2">
              Anda yakin ingin menghapus data teknis untuk pelanggan ini?
            </p>
            <p class="text-body-2 text-medium-emphasis">
              Semua informasi teknis dan konfigurasi akan dihapus secara permanen.
            </p>
          </div>
        </v-card-text>
        <v-card-actions class="pa-6 pt-0">
          <v-spacer></v-spacer>
          <v-btn variant="outlined" @click="closeDeleteDialog" class="me-3" :style="{ borderRadius: '12px' }">
            Batal
          </v-btn>
          <v-btn color="error" variant="flat" @click="confirmDelete" prepend-icon="mdi-delete" :style="{ borderRadius: '12px' }" :loading="deleting">
            Ya, Hapus
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import apiClient from '@/services/api';

// --- Interfaces ---
interface DataTeknis {
  id: number;
  pelanggan_id: number;
  id_vlan: string;
  id_pelanggan: string;
  password_pppoe: string;
  ip_pelanggan: string;
  profile_pppoe: string;
  olt: string;
  olt_custom?: string | null;
  pon: number;
  otb: number;
  odc: number;
  odp: number;
  speedtest_proof?: string | null;
  onu_power: number;
}

interface Pelanggan {
  id: number;
  nama: string;
}

interface MikrotikServer {
  id: number;
  name: string;
}

// --- State ---
const dataTeknisList = ref<DataTeknis[]>([]);
const pelangganList = ref<Pelanggan[]>([]);
const loading = ref(true);
const saving = ref(false);
const deleting = ref(false);
const dialog = ref(false);
const dialogDelete = ref(false);
const currentStep = ref(1);
const editedItem = ref<Partial<DataTeknis>>({});
const itemToDeleteId = ref<number | null>(null);
const searchQuery = ref('');
const mikrotikServers = ref<MikrotikServer[]>([]);

// Ref untuk komponen file input
const fileInputComponent = ref<any>(null);
const expanded = ref<readonly any[]>([]);

// --- Computed Properties ---
const isEditMode = computed(() => !!editedItem.value.id);
const formTitle = computed(() => isEditMode.value ? 'Edit Data Teknis' : 'Tambah Data Teknis');

const imagePreviewUrl = computed(() => {
  if (fileInputComponent.value?.files && fileInputComponent.value.files.length > 0) {
    return URL.createObjectURL(fileInputComponent.value.files[0]);
  }
  if (editedItem.value.speedtest_proof) {
    const baseUrl = apiClient.defaults.baseURL || ''; 
    return `${baseUrl}${editedItem.value.speedtest_proof}`;
  }
  return null;
});

const pelangganForSelect = computed(() => {
  if (isEditMode.value) {
    return pelangganList.value;
  }
  const existingIds = new Set(dataTeknisList.value.map(dt => dt.pelanggan_id));
  return pelangganList.value.filter(p => !existingIds.has(p.id));
});

const filteredDataTeknisList = computed(() => {
  if (!searchQuery.value) return dataTeknisList.value;
  
  const query = searchQuery.value.toLowerCase();
  return dataTeknisList.value.filter(item => {
    const pelangganName = getPelangganName(item.pelanggan_id).toLowerCase();
    return pelangganName.includes(query) ||
           item.id_pelanggan.toLowerCase().includes(query) ||
           item.ip_pelanggan.toLowerCase().includes(query) ||
           item.olt.toLowerCase().includes(query);
  });
});

// --- Table Headers ---
const headers = [
  { title: 'Nama Pelanggan', key: 'pelanggan_id' },
  { title: 'IP Pelanggan', key: 'ip_pelanggan' },
  { title: 'OLT', key: 'olt' },
  { title: 'ONU Power', key: 'onu_power', align: 'center' as const },
  { title: 'Actions', key: 'actions', sortable: false, align: 'center' as const },
];

const pppoeProfiles = (() => {
  const speeds = ['10Mbps', '20Mbps', '30Mbps', '50Mbps'];
  const alphabet = 'abcdefghijklmnopqrstuvwxyz'.split('');
  const profiles: string[] = [];

  for (const speed of speeds) {
    for (const letter of alphabet) {
      profiles.push(`${speed}-${letter}`);
    }
  }
  return profiles;
})();

// --- Methods ---
onMounted(() => {
  fetchDataTeknis();
  fetchPelanggan();
  fetchMikrotikServers();
});

async function fetchDataTeknis() {
  loading.value = true;
  try {
    const response = await apiClient.get('/data_teknis/');
    dataTeknisList.value = response.data;
  } finally {
    loading.value = false;
  }
}

async function fetchMikrotikServers() {
  try {
    // Asumsi endpoint Anda adalah /mikrotik_server/
    const response = await apiClient.get('/mikrotik_server/');
    mikrotikServers.value = response.data;
  } catch (error) {
    console.error("Gagal mengambil daftar server Mikrotik:", error);
  }
}

async function fetchPelanggan() {
  try {
    const response = await apiClient.get('/pelanggan/');
    pelangganList.value = response.data;
  } catch(error) {
    console.error("Gagal mengambil daftar pelanggan:", error);
  }
}

function openDialog(item?: DataTeknis) {
  editedItem.value = item ? { ...item } : {};
  currentStep.value = 1;
  dialog.value = true;
}

function closeDialog() {
  dialog.value = false;
  // Reset komponen file input saat dialog ditutup
  if (fileInputComponent.value) {
    fileInputComponent.value.reset();
  }
  editedItem.value = {};
  currentStep.value = 1;
}

async function saveDataTeknis() {
  saving.value = true;
  try {
    // Ambil file langsung dari ref komponen
    const files = fileInputComponent.value?.files;
    const fileToUpload = files?.[0];

    if (fileToUpload) {
      //console.log("✅ File terdeteksi dari ref. Memulai upload...");
      const formData = new FormData();
      formData.append('file', fileToUpload);
      
      const uploadResponse = await apiClient.post('/uploads/speedtest/', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      
      if (uploadResponse?.data?.file_url) {
        editedItem.value.speedtest_proof = uploadResponse.data.file_url;
      } else {
         console.error("❌ Gagal mendapatkan file_url dari respons upload!");
      }
    }

    if (isEditMode.value) {
      await apiClient.patch(`/data_teknis/${editedItem.value.id}`, editedItem.value);
    } else {
      await apiClient.post('/data_teknis/', editedItem.value);
    }
    
    fetchDataTeknis();
    closeDialog();
  } catch (error) {
    console.error("❌ Gagal saat menyimpan data teknis:", error);
  } finally {
    saving.value = false;
  }
}

function openDeleteDialog(item: DataTeknis) {
  itemToDeleteId.value = item.id;
  dialogDelete.value = true;
}

function closeDeleteDialog() {
  dialogDelete.value = false;
  itemToDeleteId.value = null;
}

async function confirmDelete() {
  if (itemToDeleteId.value === null) return;
  deleting.value = true;
  try {
    await apiClient.delete(`/data_teknis/${itemToDeleteId.value}`);
    fetchDataTeknis();
    closeDeleteDialog();
  } catch (error) {
    console.error("Gagal menghapus data teknis:", error);
  } finally {
    deleting.value = false;
  }
}

// --- Helper Functions ---
function getPelangganName(pelangganId: number) {
  const pelanggan = pelangganList.value.find(p => p.id === pelangganId);
  return pelanggan?.nama || 'Tidak Ditemukan';
}

function getPelangganInitials(pelangganId: number) {
  const name = getPelangganName(pelangganId);
  if (name === 'Tidak Ditemukan') return '?';
  return name.split(' ').map(word => word.charAt(0)).join('').substring(0, 2).toUpperCase();
}

function getAvatarColor(pelangganId: number) {
  const colors = ['primary', 'secondary', 'accent', 'success', 'info', 'warning', 'error'];
  return colors[pelangganId % colors.length];
}

function getOnuPowerColor(power: number) {
  if (!power) return 'grey';
  if (power <= -27) return 'error';
  if (power <= -24) return 'warning';
  return 'success';
}

function getOnuPowerIcon(power: number) {
  if (!power) return 'mdi-help-circle';
  if (power <= -27) return 'mdi-signal-off';
  if (power <= -24) return 'mdi-signal-2g';
  return 'mdi-signal-4g';
}

function getOnuPowerStatus(power: number) {
  if (!power) return 'N/A';
  if (power <= -27) return 'Sinyal Lemah';
  if (power <= -24) return 'Sinyal Sedang';
  return 'Sinyal Baik';
}

function getSignalStats() {
  const good = dataTeknisList.value.filter(item => item.onu_power > -24).length;
  const poor = dataTeknisList.value.filter(item => item.onu_power <= -27).length;
  return { good, poor };
}

function getUniqueOLTCount() {
  const uniqueOLTs = new Set(dataTeknisList.value.map(item => item.olt));
  return uniqueOLTs.size;
}
</script>

<style scoped>
.header-gradient {
  background: linear-gradient(135deg, #00ACC1 0%, #006064 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.gradient-avatar {
  position: relative;
  overflow: hidden;
}

.gradient-avatar::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.2) 0%, transparent 100%);
  z-index: 1;
}

.modern-btn {
  position: relative;
  overflow: hidden;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  transform: translateY(0);
}

.modern-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 32px rgba(0, 172, 193, 0.4) !important;
}

.modern-btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  transition: left 0.5s;
}

.modern-btn:hover::before {
  left: 100%;
}

.icon-bounce {
  animation: bounce 2s infinite;
}

@keyframes bounce {
  0%, 20%, 50%, 80%, 100% {
    transform: translateY(0);
  }
  40% {
    transform: translateY(-4px);
  }
  60% {
    transform: translateY(-2px);
  }
}

.stats-card {
  position: relative;
  overflow: hidden;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  border-radius: 16px !important;
}

.stats-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 16px 40px rgba(0, 0, 0, 0.1) !important;
}

.stats-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, #00ACC1, #006064);
}

.modern-card {
  position: relative;
  overflow: hidden;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.modern-card:hover {
  transform: translateY(-2px);
}

.modern-table {
  background: transparent !important;
}

.modern-table :deep(.v-data-table-header) {
  background: rgba(0, 172, 193, 0.05) !important;
}

.modern-table :deep(.v-data-table__tr:hover) {
  background: rgba(0, 172, 193, 0.05) !important;
}

.action-btn {
  transition: all 0.2s ease;
}

.action-btn:hover {
  transform: translateY(-1px);
}

.modern-dialog {
  position: relative;
  overflow: hidden;
}

.modern-dialog::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, #00ACC1, #006064);
  z-index: 1;
}

.stepper-item {
  transition: all 0.3s ease;
}

.stepper-content {
  min-height: 400px;
}

.search-field :deep(.v-field) {
  border-radius: 12px !important;
}

.search-field :deep(.v-field--focused) {
  box-shadow: 0 0 0 2px rgba(0, 172, 193, 0.2);
}

/* Dark mode enhancements */
.v-theme--dark .stats-card {
  background: rgba(255, 255, 255, 0.05) !important;
  border: 1px solid rgba(255, 255, 255, 0.1) !important;
}

.v-theme--dark .modern-card {
  background: rgba(255, 255, 255, 0.05) !important;
  border: 1px solid rgba(255, 255, 255, 0.1) !important;
}

.v-theme--dark .modern-dialog {
  background: rgba(30, 30, 30, 0.95) !important;
  border: 1px solid rgba(255, 255, 255, 0.1) !important;
}

/* Responsive enhancements */
@media (max-width: 768px) {
  .stats-card {
    margin-bottom: 8px;
  }
  
  .modern-btn {
    width: 100%;
    margin-top: 16px;
  }
  
  .action-btn {
    min-width: 80px;
  }
}

/* Custom scrollbar */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: rgba(0, 0, 0, 0.05);
  border-radius: 4px;
}

::-webkit-scrollbar-thumb {
  background: rgba(0, 172, 193, 0.3);
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: rgba(0, 172, 193, 0.5);
}

/* Loading animation */
.v-progress-circular {
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% {
    box-shadow: 0 0 0 0 rgba(0, 172, 193, 0.4);
  }
  70% {
    box-shadow: 0 0 0 10px rgba(0, 172, 193, 0);
  }
  100% {
    box-shadow: 0 0 0 0 rgba(0, 172, 193, 0);
  }
}

/* Form field enhancements */
:deep(.v-text-field .v-field) {
  border-radius: 12px !important;
  transition: all 0.3s ease;
}

:deep(.v-text-field .v-field--focused) {
  box-shadow: 0 0 0 2px rgba(0, 172, 193, 0.2);
  border-color: #00ACC1 !important;
}

:deep(.v-select .v-field) {
  border-radius: 12px !important;
  transition: all 0.3s ease;
}

:deep(.v-select .v-field--focused) {
  box-shadow: 0 0 0 2px rgba(0, 172, 193, 0.2);
  border-color: #00ACC1 !important;
}

/* Chip enhancements */
.v-chip {
  transition: all 0.2s ease;
}

.v-chip:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}
</style>