# 📖 PANDUAN ADMIN — Warung Kampus Auto Order Bot

> **Bot:** @WarungKampus_Bot  
> **Dibuat oleh:** Ahmad Putra Cahyo  
> **Versi:** 1.0.0

---

## 📋 DAFTAR ISI

1. [Persiapan Awal](#1-persiapan-awal)
2. [Setup & Instalasi](#2-setup--instalasi)
3. [Konfigurasi .env](#3-konfigurasi-env)
4. [Menjalankan Bot](#4-menjalankan-bot)
5. [Panel Admin](#5-panel-admin)
6. [Mengelola Kategori](#6-mengelola-kategori)
7. [Mengelola Produk & Stok](#7-mengelola-produk--stok)
8. [Memproses Order](#8-memproses-order)
9. [Broadcast Pesan](#9-broadcast-pesan)
10. [Manajemen User](#10-manajemen-user)
11. [Statistik & Laporan](#11-statistik--laporan)
12. [Command Lengkap Admin](#12-command-lengkap-admin)
13. [Troubleshooting](#13-troubleshooting)

---

## 1. Persiapan Awal

### Yang Kamu Butuhkan

| Kebutuhan | Keterangan |
|---|---|
| Python 3.10+ | Pastikan sudah terinstall |
| Bot Token | Dari @BotFather di Telegram |
| Telegram User ID | Dari @userinfobot di Telegram |
| Gambar QRIS | File `.jpg` QRIS pembayaran kamu |

### Cek Python
Buka Terminal dan ketik:
```bash
python3 --version
```
Harus muncul `Python 3.10.x` atau lebih baru.

### Cek Telegram User ID Kamu
1. Buka Telegram
2. Cari **@userinfobot**
3. Klik Start → bot akan balas dengan **ID kamu**
4. Simpan ID tersebut, akan dipakai di `.env`

---

## 2. Setup & Instalasi

Buka Terminal (Mac: `Cmd + Space` → ketik "Terminal"):

```bash
# Masuk ke folder bot
cd /Users/al-birra/Documents/cahyo

# Install semua dependencies
pip3 install -r requirements.txt
```

Tunggu hingga selesai. Jika berhasil akan muncul pesan sukses.

---

## 3. Konfigurasi .env

Buka file `.env` di folder bot (bisa pakai TextEdit atau VS Code):

```bash
# Buka dengan TextEdit
open -e /Users/al-birra/Documents/cahyo/.env
```

Isi / sesuaikan nilai berikut:

```env
# Token dari BotFather — JANGAN SHARE KE SIAPAPUN
BOT_TOKEN=YOUR_TELEGRAM_BOT_TOKEN_HERE

# Username bot (tanpa @)
BOT_USERNAME=WarungKampus_Bot

# Nama toko yang tampil di bot
STORE_NAME=Warung Kampus Auto Order

# ⚠️ WAJIB DIISI: ID Telegram kamu sebagai admin
# Cara cek: chat ke @userinfobot
ADMIN_IDS=123456789

# Jika ada 2 admin, pisah dengan koma:
# ADMIN_IDS=123456789,987654321

# Nama pemilik toko
OWNER_NAME=Cahyo

# Nomor WhatsApp untuk kontak (format: 628xxx tanpa +)
ADMIN_WA=6281234567890

# Path gambar QRIS (jangan diubah kalau sudah taruh di assets/)
QRIS_PATH=assets/qris.jpg

# Info nomor rekening / nama QRIS
PAYMENT_NAME=Warung Kampus
PAYMENT_INFO=Scan QRIS di bawah untuk pembayaran

# Waktu maksimal bayar sebelum order auto-cancel (jam)
PAYMENT_TIMEOUT_HOURS=3
```

> ⚠️ **PENTING:** Simpan file setelah diedit!

---

## 4. Menjalankan Bot

### Langkah Wajib: Taruh Gambar QRIS

Salin file QRIS kamu ke folder `assets/` dan rename menjadi `qris.jpg`:

```bash
# Contoh jika QRIS ada di Desktop
cp ~/Desktop/qris-ku.jpg /Users/al-birra/Documents/cahyo/assets/qris.jpg
```

### (Opsional) Isi Data Produk Contoh

Jika mau mulai dengan produk demo:

```bash
cd /Users/al-birra/Documents/cahyo
python3 seed.py
```

### Jalankan Bot

```bash
cd /Users/al-birra/Documents/cahyo
python3 main.py
```

Jika berhasil, kamu akan terima pesan di Telegram:
> ✅ **Warung Kampus Auto Order** — Bot aktif!

Untuk **menghentikan bot**: tekan `Ctrl + C` di Terminal.

### Jalankan Bot di Background (agar Terminal bisa ditutup)

```bash
cd /Users/al-birra/Documents/cahyo
nohup python3 main.py > bot.log 2>&1 &
echo "Bot berjalan di background. PID: $!"
```

Untuk menghentikan:
```bash
# Cari PID
ps aux | grep main.py

# Hentikan (ganti 12345 dengan PID yang muncul)
kill 12345
```

---

## 5. Panel Admin

Ketik `/admin` di chat dengan bot untuk membuka panel admin.

```
⚙️ PANEL ADMIN
Warung Kampus Auto Order

[📦 Produk]        [📂 Kategori]
[📋 Order Masuk]   [📊 Statistik]
[📣 Broadcast]     [👥 Users]
[⚙️ Pengaturan]
```

---

## 6. Mengelola Kategori

### Tambah Kategori Baru

1. Buka `/admin` → klik **📂 Kategori**
2. Klik **➕ Tambah Kategori**
3. Bot akan tanya satu per satu:
   - **Nama kategori** → contoh: `Netflix & Streaming`
   - **Emoji** → contoh: `🎬` (atau ketik `skip` untuk default 📦)
   - **Deskripsi** → contoh: `Layanan streaming premium` (atau `skip`)
4. Selesai! Kategori langsung aktif.

### Nonaktifkan / Aktifkan Kategori

1. `/admin` → **📂 Kategori** → pilih kategori
2. Klik **⏸️ Nonaktifkan** atau **▶️ Aktifkan**
3. Kategori yang nonaktif tidak akan tampil ke user.

### Hapus Kategori

1. `/admin` → **📂 Kategori** → pilih kategori
2. Klik **🗑️ Hapus**

> ⚠️ **Hati-hati:** Menghapus kategori tidak menghapus produk di dalamnya, tapi produk kehilangan kategorinya.

---

## 7. Mengelola Produk & Stok

### Tambah Produk Baru

1. `/admin` → **📦 Produk** → **➕ Tambah Produk**
2. Ikuti langkah bot:

   | Langkah | Contoh Input |
   |---|---|
   | ID Kategori | `1` (lihat dari daftar yang tampil) |
   | Nama produk | `Netflix Private 1 Bulan` |
   | Deskripsi | `Akun Netflix private profile, garansi 1 bulan` |
   | Harga | `15000` |
   | Harga grosir | `13000:5` (harga:min_qty) atau `skip` |
   | Durasi | `1 Bulan` atau `skip` |

3. Produk berhasil dibuat dengan **stok 0**.

### Tambah Stok Akun Digital

1. `/admin` → **📦 Produk** → pilih produk
2. Klik **📥 Tambah Stok/Akun**
3. Kirim data akun (satu baris = satu akun):

```
email1@gmail.com:password123
email2@gmail.com:password456
email3@gmail.com:pass789
```

Atau bisa format lain sesuai jenis produk:
```
user1:pass1:profile_name
https://canva.com/invite/abc123
API_KEY_1234567890
```

4. Bot akan konfirmasi: `✅ 3 akun berhasil ditambahkan!`

> 💡 **Tips:** Stok akan otomatis berkurang saat order diapprove. Cek stok secara rutin!

### Cek Stok Produk

1. `/admin` → **📦 Produk** → pilih produk
2. Lihat info: `Stok: 10 (akun tersedia: 10)`

### Hapus Produk

1. `/admin` → **📦 Produk** → pilih produk
2. Klik **🗑️ Hapus Produk**

---

## 8. Memproses Order

### Cara Kerja Alur Order

```
User Upload Bukti Bayar
        ↓
Kamu Terima Notifikasi di Telegram
        ↓
   Foto bukti bayar + tombol [✅ APPROVE] [❌ REJECT]
        ↓
Klik APPROVE → Akun otomatis terkirim ke user ✅
Klik REJECT  → User diberitahu order ditolak ❌
```

### Saat Ada Order Masuk

Kamu akan terima pesan seperti ini:

```
🔔 ORDER BARU MASUK!
──────────────────────────────
🔖 Kode    : WK123456
👤 User    : @username (ID: 12345678)
📦 Produk  : Netflix Private 1 Bulan
🔢 Qty     : 1
💵 Total   : Rp 15.000
──────────────────────────────
📸 Bukti bayar dikirim bersamaan dengan pesan ini

[✅ APPROVE]  [❌ REJECT]
```

**Verifikasi Pembayaran:**
- Cek apakah nominal transfer sesuai
- Cek apakah nama/tanggal transfer valid
- Jika valid → klik **✅ APPROVE**
- Jika tidak valid → klik **❌ REJECT**

### Lihat Semua Order Pending

`/admin` → **📋 Order Masuk**

Akan tampil daftar order yang sudah bayar dan belum diproses.

### Lihat Detail Order Tertentu

`/admin` → **📋 Order Masuk** → pilih order

---

## 9. Broadcast Pesan

Kirim pesan promosi / pengumuman ke **semua user terdaftar** sekaligus.

### Broadcast Teks

1. `/admin` → **📣 Broadcast**
2. Ketik pesan yang ingin dikirim
3. Kamu bisa pakai format Markdown:
   ```
   🔥 *PROMO SPESIAL HARI INI!*
   
   Netflix 1 Bulan hanya *Rp 12.000*!
   Stok terbatas, buruan order! 🛒
   ```
4. Kirim → bot akan kirim ke semua user

### Broadcast dengan Foto

1. `/admin` → **📣 Broadcast**
2. **Kirim foto** (dengan atau tanpa caption)
3. Foto + caption akan terkirim ke semua user

### Tips Broadcast Efektif

- 📅 Broadcast di jam ramai: **pagi 08.00–10.00** atau **malam 19.00–21.00**
- 🎯 Sertakan info harga, stok, dan cara order
- ⚠️ Jangan terlalu sering broadcast agar user tidak terganggu

---

## 10. Manajemen User

### Lihat Info User

```bash
/info 123456789
```

Akan tampil: nama, username, total order, tanggal daftar.

### Ban User (Blokir dari Bot)

```bash
/ban 123456789
```

User yang dibanned tidak bisa menggunakan bot.

### Unban User

```bash
/unban 123456789
```

### Jadikan Reseller

Reseller mendapat harga khusus yang sudah kamu set per produk:

```bash
/reseller 123456789
```

---

## 11. Statistik & Laporan

### Lihat Statistik Sekarang

`/admin` → **📊 Statistik**

```
📊 STATISTIK TOKO
──────────────────────────────
👥 Total User      : 1,234
📦 Total Order     : 856
✅ Order Selesai   : 820
⏳ Pending Bayar   : 3
──────────────────────────────
💰 Total Revenue   : Rp 12.450.000
📅 Revenue Hari Ini: Rp 345.000
```

### Laporan Harian Otomatis

Setiap hari pukul **23:59 WIB**, bot otomatis mengirim laporan harian ke kamu. Pastikan bot tetap berjalan!

---

## 12. Command Lengkap Admin

| Command | Fungsi | Contoh |
|---|---|---|
| `/admin` | Buka panel admin | `/admin` |
| `/info <id>` | Lihat info user | `/info 123456789` |
| `/ban <id>` | Ban user | `/ban 123456789` |
| `/unban <id>` | Unban user | `/unban 123456789` |
| `/reseller <id>` | Set user sebagai reseller | `/reseller 123456789` |
| `/orders` | Lihat riwayat ordermu | `/orders` |
| `/cancel` | Batalkan proses yang sedang berjalan | `/cancel` |

---

## 13. Troubleshooting

### ❌ Bot tidak merespon setelah `/start`

**Cek:**
- Apakah `python3 main.py` masih berjalan di Terminal?
- Lihat log error di `bot.log`:
  ```bash
  cat /Users/al-birra/Documents/cahyo/bot.log
  ```

---

### ❌ QRIS tidak muncul saat user order

**Cek:**
- Apakah file ada di `assets/qris.jpg`?
  ```bash
  ls /Users/al-birra/Documents/cahyo/assets/
  ```
- Pastikan nama file persis `qris.jpg` (huruf kecil semua)

---

### ❌ Tidak terima notifikasi order masuk

**Cek:**
- Apakah `ADMIN_IDS` di `.env` sudah diisi dengan ID Telegram kamu?
- Verifikasi ID kamu: chat ke @userinfobot
- Restart bot setelah edit `.env`

---

### ❌ Approve order tapi akun tidak terkirim

**Penyebab:** Stok akun habis.

**Solusi:**
1. `/admin` → **📦 Produk** → pilih produk bermasalah
2. Klik **📥 Tambah Stok/Akun**
3. Masukkan data akun baru
4. Minta user order ulang atau kirim akun manual

---

### ❌ Error saat install requirements

```bash
# Coba dengan pip3 eksplisit
pip3 install python-telegram-bot==20.7 aiosqlite python-dotenv pytz

# Atau update pip dulu
pip3 install --upgrade pip
pip3 install -r requirements.txt
```

---

### 🔄 Restart Bot

```bash
# Hentikan bot yang berjalan (Ctrl+C di Terminal)
# Lalu jalankan ulang:
cd /Users/al-birra/Documents/cahyo
python3 main.py
```

---

## 💡 Tips & Best Practices

> **Backup database secara rutin!**

```bash
# Backup database
cp /Users/al-birra/Documents/cahyo/data/warungkampus.db \
   ~/Desktop/backup_warungkampus_$(date +%Y%m%d).db
```

> **Cek stok setiap hari** sebelum promosi untuk menghindari oversell.

> **Segera approve order** setelah user upload bukti bayar — pengalaman user lebih baik jika diproses cepat.

> **Format data akun konsisten** agar mudah dibaca. Rekomendasikan: `email:password`

---

*Panduan ini dibuat untuk admin bot @WarungKampus_Bot*  
*Last updated: April 2026*
