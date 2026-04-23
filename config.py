"""
config.py — Konfigurasi global bot Warung Kampus
Membaca semua setting dari file .env
"""
import os
from dotenv import load_dotenv

load_dotenv()

# ─────────────────── BOT ───────────────────
BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
BOT_USERNAME: str = os.getenv("BOT_USERNAME", "WarungKampus_Bot")
STORE_NAME: str = os.getenv("STORE_NAME", "Warung Kampus Auto Order")

# ─────────────────── ADMIN ─────────────────
_raw_admins = os.getenv("ADMIN_IDS", "")
ADMIN_IDS: list[int] = [int(x.strip()) for x in _raw_admins.split(",") if x.strip().isdigit()]
OWNER_NAME: str = os.getenv("OWNER_NAME", "Admin")
ADMIN_WA: str = os.getenv("ADMIN_WA", "")

# ─────────────────── PAYMENT ───────────────
QRIS_PATH: str = os.getenv("QRIS_PATH", "assets/qris.jpg")
PAYMENT_NAME: str = os.getenv("PAYMENT_NAME", "Warung Kampus")
PAYMENT_INFO: str = os.getenv("PAYMENT_INFO", "Scan QRIS di bawah untuk pembayaran")
PAYMENT_TIMEOUT_HOURS: int = int(os.getenv("PAYMENT_TIMEOUT_HOURS", "3"))

# ─────────────────── DATABASE ──────────────
DB_PATH: str = os.getenv("DB_PATH", "data/warungkampus.db")

# ─────────────────── TIMEZONE ──────────────
TIMEZONE: str = os.getenv("TIMEZONE", "Asia/Jakarta")

# ─────────────────── CONSTANTS ─────────────
MAX_PRODUCTS_PER_PAGE = 5
MAX_ORDERS_PER_PAGE = 8
ORDER_ID_PREFIX = "WK"

# Status order
STATUS_PENDING = "pending"
STATUS_WAITING = "waiting_payment"
STATUS_PAID = "paid"
STATUS_PROCESSING = "processing"
STATUS_COMPLETED = "completed"
STATUS_CANCELLED = "cancelled"
STATUS_REJECTED = "rejected"

STATUS_LABELS = {
    STATUS_PENDING:    "⏳ Pending",
    STATUS_WAITING:    "💳 Menunggu Bayar",
    STATUS_PAID:       "✅ Dibayar",
    STATUS_PROCESSING: "🔄 Diproses",
    STATUS_COMPLETED:  "✅ Selesai",
    STATUS_CANCELLED:  "❌ Dibatalkan",
    STATUS_REJECTED:   "🚫 Ditolak",
}
