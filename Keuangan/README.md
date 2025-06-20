# 💰 Aplikasi Manajemen Keuangan Pribadi

Aplikasi web profesional untuk mengelola keuangan pribadi dengan fitur lengkap dan interface yang modern.

## ✨ Fitur Utama

### 📊 Dashboard Interaktif
- **Ringkasan Keuangan**: Lihat total pemasukan, pengeluaran, dan saldo dalam satu tampilan
- **Transaksi Terbaru**: Monitor aktivitas keuangan terkini
- **Status Budget**: Pantau progress budget per kategori
- **Target Keuangan**: Lihat perkembangan pencapaian target

### 💸 Manajemen Transaksi
- **Pencatatan Mudah**: Tambah transaksi dengan kategori yang sudah tersedia
- **Kategorisasi Otomatis**: 11 kategori default (Gaji, Freelance, Makanan, Transportasi, dll.)
- **Riwayat Lengkap**: Lihat semua transaksi dengan pagination
- **Filter & Pencarian**: Cari transaksi berdasarkan kategori atau tanggal

### 📈 Budget Planning
- **Budget per Kategori**: Atur budget untuk setiap kategori pengeluaran
- **Periode Fleksibel**: Budget mingguan, bulanan, atau tahunan
- **Monitoring Real-time**: Lihat persentase penggunaan budget
- **Alert System**: Peringatan ketika budget hampir habis

### 🎯 Target Keuangan
- **Goal Setting**: Buat target tabungan untuk berbagai keperluan
- **Progress Tracking**: Monitor pencapaian dengan progress bar
- **Deadline Management**: Atur tanggal target dan lihat sisa waktu
- **Multiple Goals**: Kelola beberapa target sekaligus

### 📊 Laporan & Analisis
- **Grafik Interaktif**: Pie chart pengeluaran per kategori
- **Tren Bulanan**: Line chart pemasukan vs pengeluaran
- **Statistik Detail**: Ringkasan per kategori dengan rata-rata
- **Export Data**: Export laporan ke PDF dan Excel (coming soon)

## 🛠️ Teknologi yang Digunakan

### Backend
- **Python 3.8+**
- **Flask 2.3.3** - Web framework
- **SQLAlchemy** - Database ORM
- **SQLite** - Database
- **Flask-Login** - User authentication
- **Werkzeug** - Password hashing

### Frontend
- **HTML5 & CSS3**
- **Bootstrap 5.3** - UI framework
- **Font Awesome 6** - Icons
- **Chart.js** - Interactive charts
- **JavaScript ES6+**

### Libraries Tambahan
- **Pandas** - Data analysis
- **Plotly** - Advanced charting
- **Matplotlib** - Data visualization
- **OpenPyXL** - Excel export

## 🚀 Instalasi & Setup

### Prasyarat
- Python 3.8 atau lebih baru
- pip (Python package installer)

### Langkah Instalasi

1. **Clone repository**
   ```bash
   git clone <repository-url>
   cd Keuangan
   ```

2. **Buat virtual environment**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   # source venv/bin/activate  # Linux/Mac
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Jalankan aplikasi**
   ```bash
   python app.py
   ```

5. **Buka di browser**
   ```
   http://localhost:5000
   ```

## 📱 Penggunaan

### 1. Registrasi & Login
- Buat akun baru dengan username, email, dan password
- Login dengan credentials yang sudah dibuat

### 2. Menambah Transaksi
- Klik "Tambah Transaksi" di halaman Transaksi
- Pilih kategori (pemasukan/pengeluaran)
- Masukkan jumlah, deskripsi, dan tanggal
- Simpan transaksi

### 3. Membuat Budget
- Masuk ke halaman Budget
- Klik "Tambah Budget"
- Pilih kategori pengeluaran
- Tentukan jumlah budget dan periode
- Atur tanggal mulai dan selesai

### 4. Setting Target
- Buka halaman Target
- Klik "Tambah Target"
- Masukkan nama target dan jumlah yang diinginkan
- Tentukan tanggal target
- Tambahkan deskripsi (opsional)

### 5. Melihat Laporan
- Akses halaman Laporan untuk melihat analisis
- Grafik pie chart menunjukkan distribusi pengeluaran
- Line chart menampilkan tren bulanan
- Tabel ringkasan memberikan detail per kategori

## 🔧 Konfigurasi

### Database
- Default: SQLite (`finance_manager.db`)
- Untuk production, ganti ke PostgreSQL atau MySQL

### Security
- Ganti `SECRET_KEY` di `app.py` untuk production
- Aktifkan HTTPS untuk deployment

### Customization
- Tambah kategori baru melalui admin panel
- Ubah warna tema di file CSS
- Sesuaikan periode budget sesuai kebutuhan

## 📊 Struktur Database

### Tabel User
- `id`, `username`, `email`, `password_hash`, `created_at`

### Tabel Category
- `id`, `name`, `type`, `color`, `icon`

### Tabel Transaction
- `id`, `user_id`, `category_id`, `amount`, `description`, `date`

### Tabel Budget
- `id`, `user_id`, `category_id`, `amount`, `period`, `start_date`, `end_date`

### Tabel Goal
- `id`, `user_id`, `name`, `target_amount`, `current_amount`, `target_date`

## 🎨 Kategori Default

### Pemasukan
- 💼 Gaji
- 💻 Freelance
- 📈 Investasi
- 🎁 Bonus

### Pengeluaran
- 🍽️ Makanan
- 🚗 Transportasi
- 🛍️ Belanja
- 🎬 Hiburan
- 🏥 Kesehatan
- 📄 Tagihan
- 📚 Pendidikan

## 🚧 Roadmap & Fitur Mendatang

- [ ] **Export ke PDF/Excel** - Laporan dalam format file
- [ ] **Notifikasi Push** - Alert budget dan target
- [ ] **Multi-currency** - Support mata uang internasional
- [ ] **Integrasi Bank** - Sinkronisasi otomatis dengan rekening
- [ ] **Mobile App** - Aplikasi Android dan iOS
- [ ] **Machine Learning** - Prediksi pengeluaran dan rekomendasi
- [ ] **Social Features** - Berbagi tips dan challenge
- [ ] **API Integration** - Webhook dan third-party services

## 🤝 Kontribusi

Kami welcome kontribusi dari developer lain! Silakan:

1. Fork repository ini
2. Buat feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push ke branch (`git push origin feature/AmazingFeature`)
5. Buat Pull Request

## 📝 License

Distributed under the MIT License. See `LICENSE` file for more information.

## 📞 Support

Jika ada pertanyaan atau butuh bantuan:
- Email: support@keuangan-app.com
- GitHub Issues: [Create Issue](https://github.com/username/personal-finance/issues)

## 🙏 Acknowledgments

- Bootstrap team untuk UI framework yang amazing
- Chart.js untuk library grafik yang powerful
- Font Awesome untuk icon set yang lengkap
- Flask community untuk framework yang excellent

---

<div align="center">
  <strong>Made with ❤️ for better financial management</strong>
</div>
