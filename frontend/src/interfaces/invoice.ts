export interface Invoice {
  id: number;
  invoice_number: string;
  pelanggan_id: number;
  id_pelanggan: string; 
  total_harga: number;
  tgl_invoice: string; 
  tgl_jatuh_tempo: string; 
  status_invoice: 'Lunas' | 'Belum Dibayar' | 'Kadaluarsa';
  payment_link?: string | null;
  paid_at?: string | null; 
  email: string;
  no_telp: string;
}

export interface PelangganSelectItem {
  id: number;
  nama: string;
}

export interface LanggananSelectItem {
  id: number;
  pelanggan_id: number;
  display_name: string;
}