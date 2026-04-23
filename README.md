# Warung Kampus Auto Order Bot

Bot Telegram auto-order produk digital dengan pembayaran QRIS.

## ✨ Fitur

| Fitur | Keterangan |
|---|---|
| 🛒 Katalog Produk | Kategori bertingkat, stok real-time, harga grosir |
| 💳 QRIS Payment | Scan QRIS → upload bukti → admin konfirmasi |
| 📦 Auto Kirim | Akun digital otomatis terkirim setelah diapprove |
| 👤 Profil & Riwayat | Riwayat order lengkap tiap user |
| 🔧 Panel Admin | Kelola produk, kategori, order, broadcast |
| 📣 Broadcast | Kirim pesan promosi ke semua user sekaligus |
| ⏰ Reminder Otomatis | Notif user yang belum bayar |
| 📊 Laporan Harian | Statistik penjualan ke admin setiap malam |
| 👑 Reseller | Harga khusus reseller per produk |
| 🔗 Referral | Link referral per user |

---

## 🚀 Cara Setup

### 1. Install dependencies
```bash
cd /Users/al-birra/Documents/cahyo
pip install -r requirements.txt
```

### 2. Konfigurasi `.env`
Edit file `.env`:
```
BOT_TOKEN=token_dari_botfather
ADMIN_IDS=telegram_user_id_kamu
ADMIN_WA=628xxxxxxxxxx
```

> **Cara cek Telegram User ID kamu:** Chat ke @userinfobot di Telegram

### 3. Taruh QRIS kamu
Simpan gambar QRIS ke `assets/qris.jpg`

### 4. Isi database dengan contoh produk
```bash
python seed.py
```

### 5. Jalankan bot
```bash
python main.py
```

---

## 📁 Struktur Folder

```
cahyo/
├── .env                  ← Konfigurasi rahasia
├── main.py               ← Entry point
├── config.py             ← Konfigurasi global
├── database.py           ← Database SQLite (aiosqlite)
├── keyboards.py          ← Semua keyboard Telegram
├── messages.py           ← Template pesan
├── seed.py               ← Data contoh
├── assets/
│   └── qris.jpg          ← Gambar QRIS kamu
├── data/
│   └── warungkampus.db   ← Database (auto dibuat)
├── handlers/
│   ├── start.py          ← /start, menu utama
│   ├── catalog.py        ← Browse produk
│   ├── order.py          ← Alur pemesanan + QRIS
│   ├── user.py           ← Profil & riwayat
│   └── admin.py          ← Panel admin
└── utils/
    ├── helpers.py        ← Fungsi utilitas
    └── scheduler.py     ← Background jobs
```

---

## ⚙️ Command Admin

| Command | Fungsi |
|---|---|
| `/admin` | Buka panel admin |
| `/ban <id>` | Ban user |
| `/unban <id>` | Unban user |
| `/reseller <id>` | Jadikan reseller |
| `/info <id>` | Lihat info user |

---

## 🔄 Alur Order

```
User /start
  → Pilih Kategori
    → Pilih Produk
      → Tentukan Qty
        → Konfirmasi Order
          → Tampil QRIS + Invoice
            → User Upload Bukti Bayar
              → Admin Approve ✅
                → Produk Otomatis Terkirim ke User 🎉
```

---

## 📊 Database

Database menggunakan **SQLite** dengan **WAL mode** — dapat menampung:
- Jutaan baris order
- Ribuan produk dan kategori  
- Ratusan ribu user

Untuk scale lebih besar, migrasi ke **PostgreSQL** cukup ganti koneksi di `database.py`.
