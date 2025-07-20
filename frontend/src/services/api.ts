import axios from 'axios';

// Konfigurasi instance axios
const apiClient = axios.create({
  baseURL: 'http://127.0.0.1:8000', // Sesuaikan dengan URL backend FastAPI Anda
  headers: {
    'Content-Type': 'application/json',
  },
});

// Tambahkan interceptor untuk menyisipkan token JWT dari localStorage ke setiap request
// Ini penting untuk mengakses endpoint yang terproteksi seperti /users/me
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

export default apiClient;