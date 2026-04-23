"""
keyboards.py — Semua keyboard inline & reply untuk bot
"""
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton, WebAppInfo

# ══════════════════════════════════════════════════════════════
#  MAIN MENU
# ══════════════════════════════════════════════════════════════

def main_menu_kb() -> InlineKeyboardMarkup:
    # Check config for dynamic URL
    import config
    web_app_url = getattr(config, 'WEBAPP_URL', None)
    
    buttons = []
    
    if web_app_url:
        buttons.append([InlineKeyboardButton("🚀 Buka Web App (NEW)", web_app=WebAppInfo(url=web_app_url))])
        
    buttons.extend([
        [InlineKeyboardButton("List Produk 🛒", callback_data="menu_catalog"),
         InlineKeyboardButton("💰 Saldo", callback_data="menu_saldo")],
        [InlineKeyboardButton("🧾 Riwayat Transaksi", callback_data="menu_orders")],
        [InlineKeyboardButton("Produk Populer ✨", callback_data="menu_popular"),
         InlineKeyboardButton("Menu Lain ⏩", callback_data="menu_other")],
    ])
    
    return InlineKeyboardMarkup(buttons)


# ══════════════════════════════════════════════════════════════
#  CATALOG
# ══════════════════════════════════════════════════════════════

def categories_kb(categories: list[dict], page: int = 0) -> InlineKeyboardMarkup:
    # Build numeric keypad corresponding to the 1-based index of categories
    buttons = []
    current_row = []
    
    for i, cat in enumerate(categories):
        num_label = str(i + 1)
        current_row.append(InlineKeyboardButton(num_label, callback_data=f"cat_{cat['id']}"))
        if len(current_row) == 5:
            buttons.append(current_row)
            current_row = []
            
    if current_row:
        buttons.append(current_row)
        
    buttons.append([InlineKeyboardButton("🔙 Kembali ke Menu", callback_data="menu_main")])
    return InlineKeyboardMarkup(buttons)


def products_kb(products: list[dict], page: int = 0,
                per_page: int = 5, cat_id: int = None) -> InlineKeyboardMarkup:
    start = page * per_page
    end = start + per_page
    page_products = products[start:end]
    total_pages = (len(products) + per_page - 1) // per_page

    buttons = []
    for p in page_products:
        stok = f"✅ {p['stock']}" if p['stock'] > 0 else "❌ Habis"
        buttons.append([InlineKeyboardButton(
            f"{p['name']} | Rp {p['price']:,} | {stok}",
            callback_data=f"prod_{p['id']}"
        )])

    # Navigation
    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton("⬅️ Prev", callback_data=f"ppage_{cat_id}_{page-1}"))
    if page < total_pages - 1:
        nav.append(InlineKeyboardButton("Next ➡️", callback_data=f"ppage_{cat_id}_{page+1}"))
    if nav:
        buttons.append(nav)

    buttons.append([InlineKeyboardButton("🔙 Kembali ke Kategori", callback_data="menu_catalog")])
    return InlineKeyboardMarkup(buttons)


def product_detail_kb(product: dict) -> InlineKeyboardMarkup:
    buttons = []
    if product.get("stock", 0) > 0:
        buttons.append([InlineKeyboardButton(
            "🛒 Pesan Sekarang", callback_data=f"order_start_{product['id']}"
        )])
    buttons.append([InlineKeyboardButton(
        "🔙 Kembali", callback_data=f"cat_{product.get('category_id', 0)}"
    )])
    return InlineKeyboardMarkup(buttons)


# ══════════════════════════════════════════════════════════════
#  ORDER FLOW
# ══════════════════════════════════════════════════════════════

def qty_kb() -> InlineKeyboardMarkup:
    """Dynamic keyboard built inside the handler based on current qty and stock."""
    pass

def order_checkout_kb(qty: int, max_qty: int) -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton("-1", callback_data="qty_-1"),
         InlineKeyboardButton("Ketik Jumlah", callback_data="qty_custom"),
         InlineKeyboardButton("+1", callback_data="qty_+1")],
        [InlineKeyboardButton("-10", callback_data="qty_-10"),
         InlineKeyboardButton("-5", callback_data="qty_-5"),
         InlineKeyboardButton("+5", callback_data="qty_+5"),
         InlineKeyboardButton("+10", callback_data="qty_+10")],
        [InlineKeyboardButton("Take All 📦", callback_data="qty_all")],
        [InlineKeyboardButton("Qris 1️⃣", callback_data="pay_qris"),
         InlineKeyboardButton("Balance 2️⃣", callback_data="pay_balance")],
        [InlineKeyboardButton("Back 🔙", callback_data="order_cancel")]
    ]
    return InlineKeyboardMarkup(rows)


def confirm_order_kb(order_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Konfirmasi & Bayar", callback_data=f"confirm_pay_{order_id}")],
        [InlineKeyboardButton("❌ Batalkan Order", callback_data=f"cancel_order_{order_id}")],
    ])


def cancel_order_kb(order_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("❌ Batalkan Order", callback_data=f"cancel_order_{order_id}")
    ]])


def after_payment_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📦 Lihat Pesanan Saya", callback_data="menu_orders")],
        [InlineKeyboardButton("🏠 Menu Utama", callback_data="menu_main")],
    ])


# ══════════════════════════════════════════════════════════════
#  ADMIN — ORDER
# ══════════════════════════════════════════════════════════════

def admin_order_kb(order_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ APPROVE", callback_data=f"adm_approve_{order_id}"),
         InlineKeyboardButton("❌ REJECT", callback_data=f"adm_reject_{order_id}")],
        [InlineKeyboardButton("📋 Panel Admin", callback_data="adm_panel")],
    ])


# ══════════════════════════════════════════════════════════════
#  ADMIN — PANEL
# ══════════════════════════════════════════════════════════════

def admin_panel_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📦 Produk", callback_data="adm_products"),
         InlineKeyboardButton("📂 Kategori", callback_data="adm_categories")],
        [InlineKeyboardButton("📋 Order Masuk", callback_data="adm_orders"),
         InlineKeyboardButton("📊 Statistik", callback_data="adm_stats")],
        [InlineKeyboardButton("📣 Broadcast", callback_data="adm_broadcast"),
         InlineKeyboardButton("👥 Users", callback_data="adm_users")],
        [InlineKeyboardButton("⚙️ Pengaturan", callback_data="adm_settings")],
    ])


def admin_products_kb(products: list[dict], cat_id: int = None) -> InlineKeyboardMarkup:
    buttons = []
    for p in products[:15]:
        stok_icon = "✅" if p["stock"] > 0 else "❌"
        buttons.append([InlineKeyboardButton(
            f"{stok_icon} {p['name']} [stok:{p['stock']}]",
            callback_data=f"adm_prod_{p['id']}"
        )])
    buttons.append([InlineKeyboardButton("➕ Tambah Produk", callback_data="adm_add_product")])
    buttons.append([InlineKeyboardButton("🔙 Panel Admin", callback_data="adm_panel")])
    return InlineKeyboardMarkup(buttons)


def admin_product_detail_kb(product_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📥 Tambah Stok/Akun", callback_data=f"adm_addstock_{product_id}"),
         InlineKeyboardButton("🧹 Kosongkan Stok", callback_data=f"adm_clearstock_{product_id}")],
        [InlineKeyboardButton("✏️ Edit Produk", callback_data=f"adm_editprod_{product_id}"),
         InlineKeyboardButton("🗑️ Hapus Produk", callback_data=f"adm_delprod_{product_id}")],
        [InlineKeyboardButton("🔙 Kembali", callback_data="adm_products")],
    ])


def admin_categories_kb(categories: list[dict]) -> InlineKeyboardMarkup:
    buttons = []
    for c in categories[:15]:
        icon = "✅" if c["is_active"] else "🔴"
        buttons.append([InlineKeyboardButton(
            f"{icon} {c['emoji']} {c['name']}",
            callback_data=f"adm_cat_{c['id']}"
        )])
    buttons.append([InlineKeyboardButton("➕ Tambah Kategori", callback_data="adm_add_category")])
    buttons.append([InlineKeyboardButton("🔙 Panel Admin", callback_data="adm_panel")])
    return InlineKeyboardMarkup(buttons)


def admin_category_detail_kb(cat_id: int, is_active: int) -> InlineKeyboardMarkup:
    toggle_label = "⏸️ Nonaktifkan" if is_active else "▶️ Aktifkan"
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(toggle_label, callback_data=f"adm_togglecat_{cat_id}"),
         InlineKeyboardButton("✏️ Edit", callback_data=f"adm_editcat_{cat_id}")],
        [InlineKeyboardButton("🗑️ Hapus", callback_data=f"adm_delcat_{cat_id}")],
        [InlineKeyboardButton("🔙 Kembali", callback_data="adm_categories")],
    ])


def admin_orders_pending_kb(orders: list[dict]) -> InlineKeyboardMarkup:
    buttons = []
    for o in orders[:10]:
        buttons.append([InlineKeyboardButton(
            f"#{o['order_code']} — Rp {o['total_price']:,}",
            callback_data=f"adm_vieworder_{o['id']}"
        )])
    buttons.append([InlineKeyboardButton("🔙 Panel Admin", callback_data="adm_panel")])
    return InlineKeyboardMarkup(buttons)


# ══════════════════════════════════════════════════════════════
#  USER PROFILE & ORDERS
# ══════════════════════════════════════════════════════════════

def profile_kb(user_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📦 Riwayat Order", callback_data="menu_orders")],
        [InlineKeyboardButton("🔗 Link Referral Saya", callback_data="my_referral")],
        [InlineKeyboardButton("🏠 Menu Utama", callback_data="menu_main")],
    ])


def orders_kb(orders: list[dict], page: int = 0, per_page: int = 8) -> InlineKeyboardMarkup:
    start = page * per_page
    end = start + per_page
    page_orders = orders[start:end]
    total_pages = (len(orders) + per_page - 1) // per_page

    buttons = []
    for o in page_orders:
        buttons.append([InlineKeyboardButton(
            f"#{o['order_code']} | {o['product_name']} | {o['status']}",
            callback_data=f"view_order_{o['id']}"
        )])

    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton("⬅️ Prev", callback_data=f"orders_page_{page-1}"))
    if page < total_pages - 1:
        nav.append(InlineKeyboardButton("Next ➡️", callback_data=f"orders_page_{page+1}"))
    if nav:
        buttons.append(nav)

    buttons.append([InlineKeyboardButton("🏠 Menu Utama", callback_data="menu_main")])
    return InlineKeyboardMarkup(buttons)


def back_to_main_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("🏠 Menu Utama", callback_data="menu_main")
    ]])
