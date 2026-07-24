# Eventify - Aplikasi Manajemen Event & Penjualan Tiket Online

Tugas Ujian Akhir Semester (UAS) **Web Programming Kelas B**  
Tahun Akademik **2025/2026** — Framework **Django (Python)**

---

## 👥 Kelompok 4 (Kelas B) & Pembagian Tugas Anggota

| No | NIM | Nama Anggota | Pembagian Tugas & Tanggung Jawab |
|---|---|---|---|
| 1 | **2421400008** | **Aprilia Nur Kholisah** | **Project Leader & Database Architect**: Merancang skema ORM Model (`Event`, `Category`, `Order`, `Ticket`, `UserProfile`), URL routing, dan arsitektur utama project Django. |
| 2 | **2421400152** | **Nabila Fajrin** | **Frontend Specialist**: Mengembangkan UI Design System (Dark Glassmorphism aesthetic), layout responsif, landing page catalog, dan komponen visual UI. |
| 3 | **2421400072** | **Sifriah Aini** | **Backend Specialist**: Mengembangkan fitur Autentikasi User (Register, Login, Role system), manajemen profile, serta fitur CRUD Event & Kategori untuk Organizer. |
| 4 | **2421400037** | **Lyda Ramadhani** | **Checkout & E-Ticket Engineer**: Mengembangkan alur pemesanan tiket, kalkulasi otomatis, simulasi payment gateway (QRIS/Bank/E-Wallet), serta pembuatan E-Ticket dinamis dengan QR Code. |
| 5 | **2421400035** | **Khoiratus Sholehah** | **Quality & Reporting Specialist**: Mengembangkan fitur Gate Check-in Ticket Scanner, Dashboard Analytics EO, Rekapitulasi Laporan Keuangan/Cetak PDF, dan penyiapan seed data. |

---

## 🚀 Deskripsi Singkat Aplikasi

**Eventify** adalah aplikasi web berbasis Django yang dirancang untuk mempermudah Event Organizer (EO) dalam mengelola kegiatan/event dan memfasilitasi peserta dalam melakukan pemesanan tiket secara online. 

Aplikasi ini dilengkapi dengan penanganan peran pengakses (Role-Based Access Control), verifikasi pembayaran transfer/QRIS, generator **E-Ticket dengan QR Code unik**, sistem **check-in gate scanner**, serta **dashboard analitik dan rekapitulasi laporan penjualan**.

---

## 🌟 Fitur Utama Aplikasi

### 1. Pembeli / Peserta Event
- **Jelajah Catalog & Filter**: Pencarian event interaktif berdasarkan kata kunci, kategori (Konser, Workshop, Olahraga, Pameran, Kuliner), dan status (Upcoming, Ongoing, Selesai).
- **Detail Event & Status Kuota**: Tampilan visual event, lokasi/venue, jadwal, deskripsi lengkap, serta indikator kuota tersisa.
- **Pemesanan Tiket & Form Pemesan**: Pemilihan kuantitas tiket, pengisian data pemegang tiket, dan kalkulasi total biaya real-time.
- **Simulasi Pembayaran Multi-Channel**: Mendukung pembayaran via QRIS National Standard, Transfer Bank (BCA/BNI/BRI), dan E-Wallet (GoPay/OVO/DANA) disertai pengunggahan bukti transfer atau konfirmasi instan.
- **E-Ticket Hub ("Tiket Saya")**: Tampilan E-Ticket terbit otomatis lengkap dengan **QR Code khusus**, Kode Unik Tiket (e.g. `TKT-20260724-XXXX`), status pembayaran, dan opsi **Cetak / Simpan PDF**.

### 2. Administrator & Event Organizer (EO)
- **Dashboard Analytics EO**: Pemantauan metrik utama secara visual (Total Event, Event Aktif, Tiket Terjual, Total Pendapatan, dan Pesanan Menunggu Verifikasi).
- **CRUD Manajemen Event**: Tambah event baru, edit rincian/kuota/harga/status, hapus event, dan unggah gambar poster.
- **CRUD Manajemen Kategori**: Pengelolaan kategori event beserta ikon visual FontAwesome.
- **Verifikasi Pesanan & Pembayaran**: Peninjauan bukti transfer pembeli dengan fitur pengesahan (Approve/Reject) instan.
- **Gate Check-in Ticket Scanner**: Alat pemindaian/input kode tiket di pintu masuk event dengan konfirmasi status validasi real-time untuk mencegah penggunaan tiket ganda.
- **Laporan & Rekapitulasi**: Rekapitulasi data transaksi penjualan tiket, total pendapatan, tingkat kehadiran pengunjung (checked-in vs total), dan fitur **Cetak Laporan Format PDF**.

---

## 🛠️ Teknologi yang Digunakan

- **Backend Core**: Python 3.14+ & **Django 6.0.6**
- **Database**: SQLite3 (Django ORM)
- **Library QR Code**: `qrcode 8.2` & `Pillow 12.3`
- **Frontend & Styling**: HTML5, Vanilla CSS, **Bootstrap 5.3**, FontAwesome 6.5, Google Fonts (Plus Jakarta Sans)

---

## 📦 Cara Instalasi & Menjalankan Aplikasi

1. **Clone / Buka Direktori Project**:
   ```bash
   cd C:\Users\HP\.gemini\antigravity\scratch\eventify_kelompok4
   ```

2. **Instal Dependensi Python**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Jalankan Migrasi Database**:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

4. **Isi Data Awal (Seed Data Demo)**:
   ```bash
   python manage.py seed_data
   ```

5. **Jalankan Server Lokal**:
   ```bash
   python manage.py runserver
   ```
   Aplikasi dapat diakses melalui browser di: **`http://127.0.0.1:8000/`**

---

## 🔑 Akun Uji Coba (Demo Credentials)

| Peran (Role) | Username | Password | Keterangan |
|---|---|---|---|
| **Superuser / Admin** | `admin` | `admin123` | Akses penuh seluruh sistem & admin panel |
| **Event Organizer (EO)** | `organizer` | `organizer123` | Akses ke Dashboard EO, Kelola Event, Scanner, Laporan |
| **Peserta (Buyer)** | `peserta1` | `peserta123` | Akses untuk memesan tiket & melihat E-Ticket |

---

## 🗄️ Skema Tabel Database

1. **`auth_user` & `UserProfile`**: Menyimpan kredensial pengguna, nomor kontak, dan peran pengakses (`is_organizer`).
2. **`Category`**: Menyimpan kategori event (Nama, Slug, Ikon, Deskripsi).
3. **`Event`**: Menyimpan detail kegiatan (Judul, Slug, Kategori, Organizer, Deskripsi, Venue, Tanggal Mulai/Selesai, Harga, Kuota, Poster Image, Status).
4. **`Order`**: Menyimpan transaksi pemesanan tiket (Kode Order, Pembuat, Event, Qty, Total Amount, Metode Pembayaran, Bukti Transfer Image, Status Pembayaran, Catatan).
5. **`Ticket`**: Menyimpan e-ticket individu (Kode Tiket, Relasi Order, Nama Pemegang, Email, QR Code Image, Status Check-in, Waktu Check-in).
