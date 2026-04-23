"""
messages.py — Template pesan terformat (MarkdownV2)
"""
from config import STORE_NAME, STATUS_LABELS, PAYMENT_NAME, PAYMENT_INFO


def _e(text: str) -> str:
    """Escape karakter khusus MarkdownV2."""
    special = r"\_*[]()~`>#+-=|{}.!"
    return "".join(f"\\{c}" if c in special else c for c in str(text))


def fmt_rp(amount: int) -> str:
    return f"Rp {amount:,}".replace(",", ".")

def fmt_date_id(dt) -> str:
    months = ["", "Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"]
    return f"{dt.day:02d} {months[dt.month]} {dt.year} {dt.strftime('%H:%M')} WIB"


# ══════════════════════════════════════════════════════════════
#  WELCOME
# ══════════════════════════════════════════════════════════════

def welcome_msg(user: dict, stats: dict) -> str:
    from datetime import datetime
    now_str = fmt_date_id(datetime.now())
    
    # User Info
    u_id = user.get("user_id", "-")
    u_uname = f"@{user['username']}" if user.get("username") else "-"
    u_saldo = fmt_rp(user.get("balance", 0))
    u_beli = f"{user.get('total_orders', 0)} pcs"
    u_spent = fmt_rp(user.get("total_spent", 0))
    
    # Bot Info
    b_sold = f"{stats.get('total_sold_items', 0)} pcs"
    b_rev = fmt_rp(stats.get("total_revenue", 0))
    b_users = f"{stats.get('total_users', 0)}"

    text = (
        f"Halo {_e(user.get('full_name', 'Kawan'))} 👋\n"
        f"{_e(now_str)}\n\n"
        f"*User Info*\n"
        f"├ ID : `{u_id}`\n"
        f"├ Username : {_e(u_uname)}\n"
        f"├ Saldo : *{_e(u_saldo)}*\n"
        f"├ Total Beli : *{_e(u_beli)}*\n"
        f"└ Total Transaksi : *{_e(u_spent)}*\n\n"
        f"*Bot Info*\n"
        f"├ Terjual : *{_e(b_sold)}*\n"
        f"├ Total Transaksi : *{_e(b_rev)}*\n"
        f"└ Total Pengguna : *{_e(b_users)}*\n\n"
        f"*Shortcuts :*\n"
        f"/start \\- Mulai Bot\n"
        f"/info \\- Info Bot\n"
    )
    return text


def how_to_order_msg() -> str:
    return (
        "📋 *CARA ORDER*\n\n"
        "1\\. Klik *🛒 Katalog Produk*\n"
        "2\\. Pilih *Kategori* produk yang diinginkan\n"
        "3\\. Pilih *Produk* dan klik *Pesan Sekarang*\n"
        "4\\. Tentukan *jumlah \\(qty\\)*\n"
        "5\\. Cek *ringkasan order* lalu konfirmasi\n"
        "6\\. *Scan QRIS* dan bayar sesuai nominal\n"
        "7\\. *Upload bukti bayar* sebagai foto\n"
        "8\\. Tunggu konfirmasi admin \\(biasanya \\< 5 menit\\)\n"
        "9\\. Produk akan *otomatis dikirim* ke chat ini\\! 🎉\n\n"
        "⚠️ *Penting:* Pastikan nominal transfer sesuai persis\\."
    )


# ══════════════════════════════════════════════════════════════
#  CATALOG
# ══════════════════════════════════════════════════════════════

def catalog_msg(categories: list[dict]) -> str:
    lines = [
        "🛒 *KATALOG PRODUK*",
        "",
        "Berikut adalah daftar kategori produk yang tersedia:",
        "\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-"
    ]
    for i, cat in enumerate(categories):
        lines.append(f"\\[{i + 1}\\] {_e(cat['name'])}")
    
    lines.append("\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-")
    return "\n".join(lines)


def product_card_msg(product: dict) -> str:
    stok = product.get("stock", 0)
    stok_txt = f"✅ *{stok} item tersedia*" if stok > 0 else "❌ *Stok habis*"

    harga_txt = f"{_e(fmt_rp(product['price']))}"
    if product.get("duration"):
        harga_txt += f" \\/ *{_e(product['duration'])}*"

    grosir_txt = ""
    if product.get("wholesale_price") and product.get("wholesale_min_qty"):
        grosir_txt = (
            f"\n💎 *Harga Grosir:* {_e(fmt_rp(product['wholesale_price']))} "
            f"\\(min {product['wholesale_min_qty']}pcs\\)"
        )

    reseller_txt = ""
    if product.get("reseller_price"):
        reseller_txt = f"\n👥 *Harga Reseller:* {_e(fmt_rp(product['reseller_price']))}"

    return (
        f"📦 *{_e(product['name'])}*\n"
        f"{'─' * 30}\n"
        f"💰 *Harga:* {harga_txt}"
        f"{grosir_txt}{reseller_txt}\n"
        f"📊 *Stok:* {stok_txt}\n\n"
        f"📝 *Deskripsi:*\n{_e(product.get('description', 'Tidak ada deskripsi'))}\n\n"
        f"🔥 *Terjual:* {product.get('sold_count', 0)} item"
    )


# ══════════════════════════════════════════════════════════════
#  ORDER
# ══════════════════════════════════════════════════════════════

def order_summary_msg(product: dict, qty: int, user: dict) -> str:
    price = product["price"]
    if qty >= product.get("wholesale_min_qty", 999) and product.get("wholesale_price"):
        price = product["wholesale_price"]
    elif user.get("is_reseller") and product.get("reseller_price"):
        price = product["reseller_price"]
    total = price * qty

    cat_name = product.get("cat_name", "PRODUK")
    stock = product.get("stock", 0)

    return (
        f"🛒 *KONFIRMASI PESANAN*\n\n"
        f"— Produk: {_e(cat_name)}\n"
        f"— Variasi: {_e(product['name'])}\n"
        f"— Harga Satuan: {_e(fmt_rp(price))}\n"
        f"— Stok Tersedia: {stock}\n"
        f"— Jumlah Pesanan: {qty}\n"
        f"— Subtotal: {_e(fmt_rp(total))}\n"
        f"— Total Pembayaran: {_e(fmt_rp(total))}\n\n"
        f"{_e(product.get('description', ''))}"
    )


def invoice_msg(order: dict) -> str:
    return (
        f"🧾 *INVOICE ORDER*\n"
        f"{'─' * 30}\n"
        f"🔖 Kode    : `{order['order_code']}`\n"
        f"📦 Produk  : *{_e(order['product_name'])}*\n"
        f"🔢 Qty     : *{order['qty']} item*\n"
        f"💵 Total   : *{_e(fmt_rp(order['total_price']))}*\n"
        f"{'─' * 30}\n"
        f"📌 *{_e(PAYMENT_INFO)}*\n\n"
        f"⚠️ *Transfer TEPAT* senilai *{_e(fmt_rp(order['total_price']))}*\n"
        f"Setelah bayar, kirim bukti transfer \\(foto/screenshot\\) ke bot ini\\."
    )


def payment_received_msg(order: dict) -> str:
    return (
        f"✅ *BUKTI PEMBAYARAN DITERIMA\\!*\n\n"
        f"🔖 Kode Order: `{order['order_code']}`\n"
        f"💵 Total: *{_e(fmt_rp(order['total_price']))}*\n\n"
        f"⏳ Admin sedang memverifikasi pembayaran kamu\\.\n"
        f"Produk akan segera dikirim setelah dikonfirmasi\\. \\(biasanya \\< 5 menit\\)"
    )


def order_completed_msg(order: dict, result: str, payment_method: str = "balance") -> str:
    method_label = "Saldo" if payment_method == "balance" else "Qris"
    unit_price = order.get('unit_price', order.get('total_price', 0))
    qty = order.get('qty', 1)
    return (
        f"📦 *Pembelian Berhasil*\n"
        f"_Terima kasih telah melakukan pembelian pada store kami\\._\n\n"
        f"Informasi Pembelian:\n"
        f"— Produk: {_e(order['product_name'])}\n"
        f"— Harga Satuan: {_e(fmt_rp(unit_price))}\n"
        f"— Jumlah Pesanan: {qty}\n"
        f"— Total Pembayaran: {_e(fmt_rp(order['total_price']))}\n"
        f"— Metode Pembayaran: {_e(method_label)}\n"
    )


def order_cancelled_msg(order_code: str, reason: str = "") -> str:
    reason_txt = f"\n📝 *Alasan:* {_e(reason)}" if reason else ""
    return (
        f"❌ *PESANAN DIBATALKAN*\n\n"
        f"🔖 Kode Order: `{order_code}`\n"
        f"{reason_txt}\n\n"
        f"Silakan hubungi admin jika ada pertanyaan\\."
    )


def order_detail_msg(order: dict) -> str:
    status_label = STATUS_LABELS.get(order['status'], order['status'])
    return (
        f"📋 *DETAIL ORDER*\n"
        f"{'─' * 30}\n"
        f"🔖 Kode    : `{order['order_code']}`\n"
        f"📦 Produk  : *{_e(order.get('product_name', '-'))}*\n"
        f"🔢 Qty     : *{order['qty']}*\n"
        f"💵 Total   : *{_e(fmt_rp(order['total_price']))}*\n"
        f"📊 Status  : *{_e(status_label)}*\n"
        f"📅 Tanggal : *{_e(order['created_at'][:16])}*\n"
        + (f"🔑 *Hasil:*\n```\n{order.get('result_data','')}\n```" if order.get("result_data") else "")
    )


# ══════════════════════════════════════════════════════════════
#  ADMIN
# ══════════════════════════════════════════════════════════════

def admin_new_order_msg(order: dict, user: dict) -> str:
    username = f"@{user['username']}" if user.get("username") else user.get("full_name", "-")
    return (
        f"🔔 *ORDER BARU MASUK\\!*\n"
        f"{'─' * 30}\n"
        f"🔖 Kode    : `{order['order_code']}`\n"
        f"👤 User    : {_e(username)} \\(ID: `{order['user_id']}`\\)\n"
        f"📦 Produk  : *{_e(order['product_name'])}*\n"
        f"🔢 Qty     : *{order['qty']}*\n"
        f"💵 Total   : *{_e(fmt_rp(order['total_price']))}*\n"
        f"{'─' * 30}\n"
        f"📸 *Bukti bayar dikirim bersamaan dengan pesan ini*"
    )


def admin_stats_msg(stats: dict) -> str:
    return (
        f"📊 *STATISTIK TOKO*\n"
        f"{'─' * 30}\n"
        f"👥 Total User    : *{stats['total_users']:,}*\n"
        f"📦 Total Order   : *{stats['total_orders']:,}*\n"
        f"✅ Order Selesai : *{stats['completed_orders']:,}*\n"
        f"⏳ Menunggu Bayar: *{stats['pending_payment']:,}*\n"
        f"{'─' * 30}\n"
        f"💰 Total Revenue : *{_e(fmt_rp(stats['total_revenue']))}*\n"
        f"📅 Revenue Hari Ini: *{_e(fmt_rp(stats['today_revenue']))}*"
    )


def profile_msg(user: dict, total_orders: int) -> str:
    ref_link = f"https://t.me/?start=ref_{user.get('referral_code','')}"
    reseller_badge = " 👑 *Reseller*" if user.get("is_reseller") else ""
    return (
        f"👤 *PROFIL AKUN*{reseller_badge}\n"
        f"{'─' * 30}\n"
        f"🆔 User ID   : `{user['user_id']}`\n"
        f"📛 Nama      : *{_e(user.get('full_name', '-'))}*\n"
        f"🔖 Username  : @{_e(user.get('username', '-'))}\n"
        f"📦 Total Order: *{total_orders}*\n"
        f"📅 Bergabung  : *{_e(str(user.get('created_at',''))[:10])}*\n"
        f"{'─' * 30}\n"
        f"🔗 *Referral Link:*\n`{_e(ref_link)}`"
    )
