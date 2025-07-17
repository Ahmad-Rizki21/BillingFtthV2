import routeros_api
from sqlalchemy.future import select # <-- Tambahkan impor ini

# Impor semua model yang dibutuhkan oleh layanan ini
from ..models.data_teknis import DataTeknis
from ..models.mikrotik_server import MikrotikServer
from ..models.mikrotik_server import MikrotikServer as MikrotikServerModel # <-- Tambahkan impor ini juga

def get_api_connection(server: MikrotikServer):
    """Membuka koneksi ke API Mikrotik."""
    try:
        connection = routeros_api.RouterOsApiPool(
            server.host_ip,
            username=server.username,
            password=server.password,
            port=server.port,
            plaintext_login=True
        )
        api = connection.get_api()
        return api, connection
    except routeros_api.exceptions.RouterOsApiConnectionError as e:
        print(f"Gagal terhubung ke Mikrotik {server.name}: {e}")
        return None, None

def update_pppoe_secret(api, data_teknis: DataTeknis, new_status: str):
    """
    Mengubah status PPPoE secret di Mikrotik.
    """
    try:
        # Cari pppoe secret berdasarkan nama (username pppoe)
        secrets = api.get_resource('/ppp/secret')
        target_secret = secrets.get(name=data_teknis.id_pelanggan)

        if not target_secret:
            print(f"PPPoE secret untuk '{data_teknis.id_pelanggan}' tidak ditemukan.")
            return

        # Tentukan aksi berdasarkan status baru
        if new_status == "Aktif":
            print(f"Mengaktifkan {data_teknis.id_pelanggan}, profil diubah ke {data_teknis.profile_pppoe}")
            secrets.set(id=target_secret[0]['id'], disabled='no', profile=data_teknis.profile_pppoe)
        elif new_status == "Suspended":
            print(f"Menonaktifkan {data_teknis.id_pelanggan}, profil diubah ke SUSPENDED")
            # Pastikan Anda punya profile bernama 'SUSPENDED' di Mikrotik
            secrets.set(id=target_secret[0]['id'], disabled='yes', profile='SUSPENDED')
        
        print("Update PPPoE secret berhasil.")

    except Exception as e:
        print(f"Terjadi error saat update PPPoE secret: {e}")

async def trigger_mikrotik_update(db, langganan):
    """
    Fungsi utama yang akan dipanggil dari router.
    """
    # Asumsi: Nama Mikrotik Server sama dengan nama OLT di Data Teknis
    if not langganan.pelanggan or not langganan.pelanggan.data_teknis:
        print("Data pelanggan atau data teknis tidak ditemukan untuk langganan ini.")
        return

    olt_name = langganan.pelanggan.data_teknis.olt
    
    # Cari server Mikrotik yang sesuai di database
    mikrotik_server = (await db.execute(
        select(MikrotikServerModel).where(MikrotikServerModel.name == olt_name)
    )).scalar_one_or_none()

    if not mikrotik_server:
        print(f"Server Mikrotik dengan nama '{olt_name}' tidak ditemukan di database.")
        return

    # Buka koneksi dan lakukan update
    api, connection = get_api_connection(mikrotik_server)
    if api and connection:
        try:
            update_pppoe_secret(api, langganan.pelanggan.data_teknis, langganan.status)
        finally:
            # Selalu tutup koneksi setelah selesai
            connection.disconnect()
