"""
handlers/admin.py — Panel admin lengkap
Fitur: kelola produk, kategori, order, broadcast, statistik, user management
"""
import logging
from telegram import Update
from telegram.ext import (
    ContextTypes, CallbackQueryHandler, CommandHandler,
    ConversationHandler, MessageHandler, filters
)

import database as db
import messages as msg
import keyboards as kb
from utils.helpers import is_admin, parse_accounts_text

log = logging.getLogger(__name__)

# ══════════════════════════════════════════════════════════════
#  CONVERSATION STATES
# ══════════════════════════════════════════════════════════════
# Tambah kategori
ADD_CAT_NAME, ADD_CAT_EMOJI, ADD_CAT_DESC = 100, 101, 102

# Tambah produk
ADD_PROD_CAT, ADD_PROD_NAME, ADD_PROD_DESC_S = 110, 111, 112
ADD_PROD_PRICE, ADD_PROD_WS_PRICE, ADD_PROD_DURATION = 113, 114, 115

# Tambah stok akun
ADD_STOCK_DATA = 120

# Edit produk
EDIT_PROD_FIELD, EDIT_PROD_VALUE = 130, 131

# Broadcast
BROADCAST_TEXT = 140

# Reject reason
REJECT_REASON = 150

# Context keys
CTX_NEW_CAT = "new_cat"
CTX_NEW_PROD = "new_prod"
CTX_TARGET_PROD = "target_prod_id"
CTX_TARGET_CAT = "target_cat_id"
CTX_EDIT_FIELD = "edit_field"
CTX_PENDING_ORDER = "pending_order_id"


# ══════════════════════════════════════════════════════════════
#  ACCESS GUARD
# ══════════════════════════════════════════════════════════════

def admin_only(func):
    async def wrapper(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        uid = update.effective_user.id
        if not is_admin(uid):
            if update.callback_query:
                await update.callback_query.answer("⛔ Akses ditolak!", show_alert=True)
            else:
                await update.message.reply_text("⛔ Kamu bukan admin\\.", parse_mode="MarkdownV2")
            return ConversationHandler.END
        return await func(update, ctx)
    wrapper.__name__ = func.__name__
    return wrapper


# ══════════════════════════════════════════════════════════════
#  PANEL UTAMA
# ══════════════════════════════════════════════════════════════

@admin_only
async def admin_panel(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Entry point: /admin atau callback adm_panel"""
    text = (
        "⚙️ *PANEL ADMIN*\n"
        "Warung Kampus Auto Order\n\n"
        "Pilih menu di bawah\\:"
    )
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.message.reply_text(
            text, parse_mode="MarkdownV2", reply_markup=kb.admin_panel_kb()
        )
    else:
        await update.message.reply_text(
            text, parse_mode="MarkdownV2", reply_markup=kb.admin_panel_kb()
        )


# ══════════════════════════════════════════════════════════════
#  ADMIN — TOPUP APPROVAL
# ══════════════════════════════════════════════════════════════

async def admin_approve_topup(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    topup_id = int(query.data.split("_")[2])
    topup = await db.get_topup(topup_id)
    if not topup:
        await query.answer("Top-up tidak ditemukan.", show_alert=True)
        return

    if topup["status"] != "pending":
        await query.answer(f"Status top-up ini: {topup['status']}", show_alert=True)
        return

    user_id = topup["user_id"]
    amount = topup["amount"]

    # Tambah saldo
    await db.add_balance(user_id, amount)
    await db.update_topup_status(topup_id, "completed")

    await query.edit_message_caption(
        caption=f"💳 *REQUEST TOP\\-UP BARU*\n\nID Topup: `{topup_id}`\nUser ID: `{user_id}`\nNominal: *{msg._e(msg.fmt_rp(amount))}*\n\n✅ *TOPUP APPROVED*",
        parse_mode="MarkdownV2",
        reply_markup=None
    )

    try:
        await ctx.bot.send_message(
            chat_id=user_id,
            text=f"✅ *Top\\-Up Berhasil\\!*\n\nSaldo sebesar *{msg._e(msg.fmt_rp(amount))}* telah ditambahkan ke akunmu\\.",
            parse_mode="MarkdownV2"
        )
    except Exception:
        log.warning("Gagal kirim notif topup success ke user %s", user_id)


async def admin_reject_topup(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    topup_id = int(query.data.split("_")[2])
    topup = await db.get_topup(topup_id)
    if not topup:
        await query.answer("Top-up tidak ditemukan.", show_alert=True)
        return

    if topup["status"] != "pending":
        await query.answer(f"Status top-up ini: {topup['status']}", show_alert=True)
        return

    await db.update_topup_status(topup_id, "rejected")

    await query.edit_message_caption(
        caption=f"💳 *REQUEST TOP\\-UP BARU*\n\nID Topup: `{topup_id}`\nUser ID: `{topup['user_id']}`\nNominal: *{msg._e(msg.fmt_rp(topup['amount']))}*\n\n❌ *TOPUP REJECTED*",
        parse_mode="MarkdownV2",
        reply_markup=None
    )

    user_id = topup["user_id"]
    try:
        await ctx.bot.send_message(
            chat_id=user_id,
            text=f"❌ *Top\\-Up Ditolak*\n\nTop\\-up sebesar *{msg._e(msg.fmt_rp(topup['amount']))}* ditolak oleh admin\\. Pastikan nominal dan bukti transfer valid\\.",
            parse_mode="MarkdownV2"
        )
    except Exception:
        pass


# ══════════════════════════════════════════════════════════════
#  ADMIN — QRIS ORDER APPROVAL
# ══════════════════════════════════════════════════════════════

async def admin_approve_qris(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    # Callback data: approveqris_12,13,14
    order_ids_str = query.data.split("_")[1]
    order_ids = order_ids_str.split(",")

    user_id = None
    total_cost = 0
    all_success = True
    
    from handlers.order import _send_order_result

    for oid in order_ids:
        order = await db.get_order(int(oid))
        if not order or order["status"] != "pending_admin":
            continue
            
        user_id = order["user_id"]
        qty = order["qty"]
        product_id = order["product_id"]

        # Take accounts dynamically
        accounts = await db.take_accounts(product_id, qty)
        if accounts:
            result_data = "\n".join(accounts)
            await db.update_order_status(order["id"], "paid")
            await db.complete_order(order["id"], result_data)
            total_cost += order["total_price"]
            
            # Send .txt + receipt + CS to user
            await _send_order_result(user_id, order, result_data, "qris", ctx.bot)
        else:
            all_success = False
            try:
                await ctx.bot.send_message(
                    chat_id=user_id,
                    text=f"❌ Stok {msg._e(order['product_name'])} habis di server\\. Hubungi admin\\.",
                    parse_mode="MarkdownV2"
                )
            except:
                pass
            
    await query.edit_message_caption(
        caption=query.message.caption + f"\n\n✅ *APPROVED*\nStatus: {'Sukses' if all_success else 'Sebagian/Semua Stok Kosong'}",
        parse_mode="MarkdownV2",
        reply_markup=None
    )

async def admin_reject_qris(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    order_ids_str = query.data.split("_")[1]
    order_ids = order_ids_str.split(",")
    
    user_id = None
    for oid in order_ids:
        order = await db.get_order(int(oid))
        if order and order["status"] == "pending_admin":
            user_id = order["user_id"]
            await db.update_order_status(order["id"], "cancelled_qris")
            
    if user_id:
        try:
            await ctx.bot.send_message(
                chat_id=user_id, 
                text=msg._e("❌ *Pembayaran Ditolak*\nPembayaran via QRIS Anda ditolak oleh admin. Pastikan bukti transfer valid atau hubungi admin."), 
                parse_mode="MarkdownV2"
            )
        except:
            pass

    await query.edit_message_caption(
        caption=query.message.caption + "\n\n❌ *REJECTED*",
        parse_mode="MarkdownV2",
        reply_markup=None
    )

# ══════════════════════════════════════════════════════════════
#  STATISTIK
# ══════════════════════════════════════════════════════════════

@admin_only
async def admin_stats(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    stats = await db.get_stats()
    await query.message.reply_text(
        msg.admin_stats_msg(stats),
        parse_mode="MarkdownV2",
        reply_markup=kb.back_to_main_kb()
    )


# ══════════════════════════════════════════════════════════════
#  KELOLA KATEGORI
# ══════════════════════════════════════════════════════════════

@admin_only
async def admin_categories(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    cats = await db.get_categories(active_only=False)
    await query.message.reply_text(
        f"📂 *KATEGORI* \\({len(cats)} total\\)\nPilih untuk detail atau tambah baru\\:",
        parse_mode="MarkdownV2",
        reply_markup=kb.admin_categories_kb(cats)
    )


@admin_only
async def admin_category_detail(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    cat_id = int(query.data.split("_")[2])
    cat = await db.get_category(cat_id)
    if not cat:
        await query.answer("Kategori tidak ditemukan.", show_alert=True)
        return
    text = (
        f"📂 *Detail Kategori*\n\n"
        f"Nama  : *{cat['name']}*\n"
        f"Emoji : {cat['emoji']}\n"
        f"Deskripsi: {cat.get('description') or '\\-'}\n"
        f"Status: {'✅ Aktif' if cat['is_active'] else '🔴 Nonaktif'}"
    )
    await query.message.reply_text(
        text, parse_mode="MarkdownV2",
        reply_markup=kb.admin_category_detail_kb(cat_id, cat["is_active"])
    )


@admin_only
async def admin_toggle_category(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    cat_id = int(query.data.split("_")[2])
    cat = await db.get_category(cat_id)
    if not cat:
        return
    new_status = 0 if cat["is_active"] else 1
    await db.update_category(cat_id, cat["name"], cat["emoji"], cat.get("description",""), new_status)
    label = "diaktifkan" if new_status else "dinonaktifkan"
    await query.answer(f"Kategori {label}!", show_alert=False)
    # Refresh
    cat = await db.get_category(cat_id)
    text = (
        f"📂 *Detail Kategori*\n\n"
        f"Nama  : *{cat['name']}*\n"
        f"Status: {'✅ Aktif' if cat['is_active'] else '🔴 Nonaktif'}"
    )
    await query.edit_message_text(
        text, parse_mode="MarkdownV2",
        reply_markup=kb.admin_category_detail_kb(cat_id, cat["is_active"])
    )


# ── Tambah Kategori (ConversationHandler) ──

@admin_only
async def add_cat_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    ctx.user_data[CTX_NEW_CAT] = {}
    await query.message.reply_text(
        "📂 *Tambah Kategori Baru*\n\nKetik *nama kategori*\\:",
        parse_mode="MarkdownV2"
    )
    return ADD_CAT_NAME


async def add_cat_name(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data[CTX_NEW_CAT]["name"] = update.message.text.strip()
    await update.message.reply_text(
        "Ketik *emoji* untuk kategori ini \\(misal: 🎵 🎮 📱\\) atau ketik `skip` untuk default 📦\\:",
        parse_mode="MarkdownV2"
    )
    return ADD_CAT_EMOJI


async def add_cat_emoji(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    ctx.user_data[CTX_NEW_CAT]["emoji"] = "📦" if text.lower() == "skip" else text
    await update.message.reply_text(
        "Ketik *deskripsi kategori* atau `skip` untuk lewati\\:",
        parse_mode="MarkdownV2"
    )
    return ADD_CAT_DESC


async def add_cat_desc(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    data = ctx.user_data[CTX_NEW_CAT]
    data["desc"] = "" if text.lower() == "skip" else text

    cat_id = await db.add_category(data["name"], data["emoji"], data["desc"])
    await update.message.reply_text(
        f"✅ Kategori *{data['name']}* berhasil ditambahkan\\! \\(ID: {cat_id}\\)",
        parse_mode="MarkdownV2",
        reply_markup=kb.admin_panel_kb()
    )
    ctx.user_data.pop(CTX_NEW_CAT, None)
    return ConversationHandler.END


# ══════════════════════════════════════════════════════════════
#  KELOLA PRODUK
# ══════════════════════════════════════════════════════════════

@admin_only
async def admin_products(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    products = await db.get_products(active_only=False)
    await query.message.reply_text(
        f"📦 *PRODUK* \\({len(products)} total\\)\nPilih produk untuk detail\\:",
        parse_mode="MarkdownV2",
        reply_markup=kb.admin_products_kb(products)
    )


@admin_only
async def admin_product_detail(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    prod_id = int(query.data.split("_")[2])
    product = await db.get_product(prod_id)
    if not product:
        await query.answer("Produk tidak ditemukan.", show_alert=True)
        return

    avail_accounts = await db.count_available_accounts(prod_id)
    text = (
        f"📦 *{msg._e(product['name'])}*\n"
        f"Kategori : {product.get('cat_emoji','')} {msg._e(product.get('cat_name','-'))}\n"
        f"Harga    : {msg._e(msg.fmt_rp(product['price']))}\n"
        f"Stok     : {product['stock']} \\(akun tersedia: {avail_accounts}\\)\n"
        f"Terjual  : {product.get('sold_count', 0)}\n"
        f"Durasi   : {msg._e(str(product.get('duration') or '-'))}\n"
        f"Status   : {'✅ Aktif' if product['is_active'] else '🔴 Nonaktif'}\n\n"
        f"📝 {msg._e(product.get('description') or 'Tidak ada deskripsi')}"
    )
    await query.message.reply_text(
        text, parse_mode="MarkdownV2",
        reply_markup=kb.admin_product_detail_kb(prod_id)
    )


@admin_only
async def admin_clear_stock(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    prod_id = int(query.data.split("_")[2])
    
    await db.clear_product_accounts(prod_id)
    await query.answer("✅ Stok/Akun berhasil dikosongkan!", show_alert=True)
    
    # Reload detail
    product = await db.get_product(prod_id)
    avail_accounts = await db.count_available_accounts(prod_id)
    text = (
        f"📦 *{msg._e(product['name'])}*\n"
        f"Kategori : {product.get('cat_emoji','')} {msg._e(product.get('cat_name','-'))}\n"
        f"Harga    : {msg._e(msg.fmt_rp(product['price']))}\n"
        f"Stok     : {product['stock']} \\(akun tersedia: {avail_accounts}\\)\n"
        f"Terjual  : {product.get('sold_count', 0)}\n"
        f"Durasi   : {msg._e(str(product.get('duration') or '-'))}\n"
        f"Status   : {'✅ Aktif' if product['is_active'] else '🔴 Nonaktif'}\n\n"
        f"📝 {msg._e(product.get('description') or 'Tidak ada deskripsi')}"
    )
    await query.edit_message_text(
        text, parse_mode="MarkdownV2",
        reply_markup=kb.admin_product_detail_kb(prod_id)
    )


# ── Tambah Produk (ConversationHandler) ──

@admin_only
async def add_prod_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    cats = await db.get_categories(active_only=True)
    if not cats:
        await query.message.reply_text(
            "⚠️ Tambahkan kategori dulu sebelum menambah produk\\.",
            parse_mode="MarkdownV2"
        )
        return ConversationHandler.END

    ctx.user_data[CTX_NEW_PROD] = {}
    # Tampilkan pilihan kategori
    buttons = [[f"{c['emoji']} {c['name']} (ID:{c['id']})" ] for c in cats]
    cat_list = "\n".join([f"  *{c['id']}*\\. {c['emoji']} {c['name']}" for c in cats])
    await query.message.reply_text(
        f"📦 *Tambah Produk Baru*\n\nKategori tersedia:\n{cat_list}\n\nKetik *ID kategori*\\:",
        parse_mode="MarkdownV2"
    )
    return ADD_PROD_CAT


async def add_prod_cat(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    try:
        cat_id = int(update.message.text.strip())
        cat = await db.get_category(cat_id)
        if not cat:
            await update.message.reply_text("ID kategori tidak valid. Coba lagi\\:", parse_mode="MarkdownV2")
            return ADD_PROD_CAT
        ctx.user_data[CTX_NEW_PROD]["category_id"] = cat_id
    except ValueError:
        await update.message.reply_text("Ketik angka ID kategori\\:", parse_mode="MarkdownV2")
        return ADD_PROD_CAT

    await update.message.reply_text("Ketik *nama produk*\\:", parse_mode="MarkdownV2")
    return ADD_PROD_NAME


async def add_prod_name(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data[CTX_NEW_PROD]["name"] = update.message.text.strip()
    await update.message.reply_text("Ketik *deskripsi produk* atau `skip`\\:", parse_mode="MarkdownV2")
    return ADD_PROD_DESC_S


async def add_prod_desc_s(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    ctx.user_data[CTX_NEW_PROD]["description"] = "" if text.lower() == "skip" else text
    await update.message.reply_text("Ketik *harga* produk \\(angka saja, contoh: 5000\\)\\:", parse_mode="MarkdownV2")
    return ADD_PROD_PRICE


async def add_prod_price(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    try:
        price = int(update.message.text.strip().replace(".", "").replace(",", ""))
        ctx.user_data[CTX_NEW_PROD]["price"] = price
    except ValueError:
        await update.message.reply_text("Harga harus berupa angka\\:", parse_mode="MarkdownV2")
        return ADD_PROD_PRICE

    await update.message.reply_text(
        "Ketik *harga grosir* \\(opsional, format: `harga:min_qty` contoh `4000:5`\\) atau `skip`\\:",
        parse_mode="MarkdownV2"
    )
    return ADD_PROD_WS_PRICE


async def add_prod_ws_price(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if text.lower() != "skip" and ":" in text:
        try:
            ws_price, ws_min = text.split(":")
            ctx.user_data[CTX_NEW_PROD]["wholesale_price"] = int(ws_price)
            ctx.user_data[CTX_NEW_PROD]["wholesale_min_qty"] = int(ws_min)
        except Exception:
            pass

    await update.message.reply_text(
        "Ketik *durasi produk* \\(contoh: 1 Bulan, 1 Tahun\\) atau `skip`\\:",
        parse_mode="MarkdownV2"
    )
    return ADD_PROD_DURATION


async def add_prod_duration(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    data = ctx.user_data[CTX_NEW_PROD]
    data["duration"] = "" if text.lower() == "skip" else text

    prod_id = await db.add_product(
        category_id=data["category_id"],
        name=data["name"],
        description=data.get("description", ""),
        price=data["price"],
        stock=0,
        duration=data.get("duration", ""),
        wholesale_price=data.get("wholesale_price"),
        wholesale_min_qty=data.get("wholesale_min_qty", 2),
    )
    await update.message.reply_text(
        f"✅ Produk *{data['name']}* ditambahkan\\! \\(ID: {prod_id}\\)\n\n"
        f"Sekarang tambahkan stok akun melalui panel produk\\.",
        parse_mode="MarkdownV2",
        reply_markup=kb.admin_panel_kb()
    )
    ctx.user_data.pop(CTX_NEW_PROD, None)
    return ConversationHandler.END


# ── Tambah Stok Akun ──

@admin_only
async def add_stock_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    prod_id = int(query.data.split("_")[2])  # adm_addstock_<id>
    ctx.user_data[CTX_TARGET_PROD] = prod_id
    product = await db.get_product(prod_id)

    await query.message.reply_text(
        f"📥 *Tambah Stok Akun*\nProduk: *{product['name']}*\n\n"
        f"Kirim data akun \\(satu akun per baris\\)\\:\n"
        f"Contoh format:\n"
        f"```\nemail@gmail.com:password123\nemail2@gmail.com:pass456\n```",
        parse_mode="MarkdownV2"
    )
    return ADD_STOCK_DATA


async def add_stock_data(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    prod_id = ctx.user_data.get(CTX_TARGET_PROD)
    if not prod_id:
        return ConversationHandler.END

    accounts = parse_accounts_text(update.message.text)
    if not accounts:
        await update.message.reply_text("Tidak ada data valid. Kirim ulang\\:", parse_mode="MarkdownV2")
        return ADD_STOCK_DATA

    added = await db.add_accounts_bulk(prod_id, accounts)
    product = await db.get_product(prod_id)
    await update.message.reply_text(
        f"✅ *{added} akun* berhasil ditambahkan ke *{product['name']}*\\!\n"
        f"Stok sekarang: *{product['stock'] + added}*",
        parse_mode="MarkdownV2",
        reply_markup=kb.admin_panel_kb()
    )
    ctx.user_data.pop(CTX_TARGET_PROD, None)
    return ConversationHandler.END


# ── Hapus produk ──

@admin_only
async def delete_product(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    prod_id = int(query.data.split("_")[2])
    product = await db.get_product(prod_id)
    if product:
        await db.delete_product(prod_id)
        await query.edit_message_text(
            f"🗑️ Produk *{product['name']}* berhasil dihapus\\.",
            parse_mode="MarkdownV2",
            reply_markup=kb.admin_panel_kb()
        )


# ══════════════════════════════════════════════════════════════
#  KELOLA ORDER
# ══════════════════════════════════════════════════════════════

@admin_only
async def admin_orders(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    paid_orders = await db.get_orders_by_status("paid")
    waiting_orders = await db.get_orders_by_status("waiting_payment")
    all_pending = paid_orders + waiting_orders

    if not all_pending:
        await query.message.reply_text(
            "✅ Tidak ada order yang perlu diproses\\.",
            parse_mode="MarkdownV2",
            reply_markup=kb.admin_panel_kb()
        )
        return

    await query.message.reply_text(
        f"📋 *ORDER MASUK* \\({len(all_pending)} order\\)\n"
        f"💳 Sudah bayar: {len(paid_orders)} \\| ⏳ Belum bayar: {len(waiting_orders)}",
        parse_mode="MarkdownV2",
        reply_markup=kb.admin_orders_pending_kb(all_pending)
    )


@admin_only
async def admin_view_order(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    order_id = int(query.data.split("_")[2])
    order = await db.get_order(order_id)
    if not order:
        await query.answer("Order tidak ditemukan.", show_alert=True)
        return

    await query.message.reply_text(
        msg.order_detail_msg(order),
        parse_mode="MarkdownV2",
        reply_markup=kb.admin_order_kb(order_id)
    )

    if order.get("payment_proof"):
        await ctx.bot.send_photo(
            chat_id=update.effective_user.id,
            photo=order["payment_proof"],
            caption=f"📸 Bukti bayar order `{order['order_code']}`",
            parse_mode="MarkdownV2"
        )


# ══════════════════════════════════════════════════════════════
#  BROADCAST
# ══════════════════════════════════════════════════════════════

@admin_only
async def broadcast_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.message.reply_text(
        "📣 *Broadcast Pesan*\n\nKetik pesan yang ingin dikirim ke semua user\\:\n"
        "\\(Mendukung Markdown, bisa kirim teks atau foto dengan caption\\)",
        parse_mode="MarkdownV2"
    )
    return BROADCAST_TEXT


async def broadcast_send(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    users = await db.get_all_users()
    message = update.message
    sent, failed = 0, 0

    await update.message.reply_text(
        f"📣 Mengirim ke *{len(users)} user*\\.\\.\\.",
        parse_mode="MarkdownV2"
    )

    for user in users:
        try:
            if message.photo:
                await ctx.bot.send_photo(
                    chat_id=user["user_id"],
                    photo=message.photo[-1].file_id,
                    caption=message.caption or "",
                    parse_mode="MarkdownV2"
                )
            else:
                await ctx.bot.send_message(
                    chat_id=user["user_id"],
                    text=message.text,
                    parse_mode="MarkdownV2"
                )
            sent += 1
        except Exception:
            failed += 1

    await update.message.reply_text(
        f"✅ Broadcast selesai\\!\n"
        f"Terkirim: *{sent}* \\| Gagal: *{failed}*",
        parse_mode="MarkdownV2",
        reply_markup=kb.admin_panel_kb()
    )
    return ConversationHandler.END


# ══════════════════════════════════════════════════════════════
#  USER MANAGEMENT
# ══════════════════════════════════════════════════════════════

@admin_only
async def admin_users(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    count = await db.count_users()
    await query.message.reply_text(
        f"👥 *USER MANAGEMENT*\n\nTotal user terdaftar: *{count}*\n\n"
        f"Gunakan command berikut\\:\n"
        f"`/ban <user_id>` \\- Ban user\n"
        f"`/unban <user_id>` \\- Unban user\n"
        f"`/reseller <user_id>` \\- Jadikan reseller\n"
        f"`/info <user_id>` \\- Info user",
        parse_mode="MarkdownV2",
        reply_markup=kb.admin_panel_kb()
    )


@admin_only
async def cmd_ban(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not ctx.args:
        await update.message.reply_text("Usage: `/ban <user_id>`", parse_mode="MarkdownV2")
        return
    uid = int(ctx.args[0])
    await db.ban_user(uid, True)
    await update.message.reply_text(f"🔨 User `{uid}` telah dibanned\\.", parse_mode="MarkdownV2")


@admin_only
async def cmd_unban(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not ctx.args:
        await update.message.reply_text("Usage: `/unban <user_id>`", parse_mode="MarkdownV2")
        return
    uid = int(ctx.args[0])
    await db.ban_user(uid, False)
    await update.message.reply_text(f"✅ User `{uid}` telah diunban\\.", parse_mode="MarkdownV2")


@admin_only
async def cmd_reseller(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not ctx.args:
        await update.message.reply_text("Usage: `/reseller <user_id>`", parse_mode="MarkdownV2")
        return
    uid = int(ctx.args[0])
    await db.set_reseller(uid, True)
    await update.message.reply_text(f"👑 User `{uid}` dijadikan reseller\\.", parse_mode="MarkdownV2")


@admin_only
async def cmd_user_info(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not ctx.args:
        await update.message.reply_text("Usage: `/info <user_id>`", parse_mode="MarkdownV2")
        return
    uid = int(ctx.args[0])
    user = await db.get_user(uid)
    if not user:
        await update.message.reply_text("User tidak ditemukan\\.", parse_mode="MarkdownV2")
        return
    orders = await db.get_user_orders(uid)
    await update.message.reply_text(
        msg.profile_msg(user, len(orders)),
        parse_mode="MarkdownV2"
    )


@admin_only
async def admin_settings(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.message.reply_text(
        "⚙️ *PENGATURAN*\n\nGunakan command untuk ubah setting\\:\n"
        "`/setstore <nama toko>`\n"
        "`/setwelcome <pesan willkommen>`",
        parse_mode="MarkdownV2",
        reply_markup=kb.admin_panel_kb()
    )


# ══════════════════════════════════════════════════════════════
#  CONVERSATION HANDLERS
# ══════════════════════════════════════════════════════════════

async def cancel_conv(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data.clear()
    return ConversationHandler.END

def get_add_category_conv():
    return ConversationHandler(
        entry_points=[CallbackQueryHandler(add_cat_start, pattern="^adm_add_category$")],
        states={
            ADD_CAT_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_cat_name)],
            ADD_CAT_EMOJI: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_cat_emoji)],
            ADD_CAT_DESC: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_cat_desc)],
        },
        fallbacks=[CommandHandler("cancel", cancel_conv)],
        per_user=True, allow_reentry=True,
    )


def get_add_product_conv():
    return ConversationHandler(
        entry_points=[CallbackQueryHandler(add_prod_start, pattern="^adm_add_product$")],
        states={
            ADD_PROD_CAT:    [MessageHandler(filters.TEXT & ~filters.COMMAND, add_prod_cat)],
            ADD_PROD_NAME:   [MessageHandler(filters.TEXT & ~filters.COMMAND, add_prod_name)],
            ADD_PROD_DESC_S: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_prod_desc_s)],
            ADD_PROD_PRICE:  [MessageHandler(filters.TEXT & ~filters.COMMAND, add_prod_price)],
            ADD_PROD_WS_PRICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_prod_ws_price)],
            ADD_PROD_DURATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_prod_duration)],
        },
        fallbacks=[CommandHandler("cancel", cancel_conv)],
        per_user=True, allow_reentry=True,
    )


async def edit_prod_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    product_id = int(query.data.split("_")[2])
    ctx.user_data[CTX_TARGET_PROD] = product_id
    
    product = await db.get_product(product_id)
    safe_name = msg._e(product['name'])
    text = (
        f"✏️ *Edit Produk*: {safe_name}\n\n"
        f"Ketik format berikut untuk memilih data yang diedit:\n"
        f"`nama` \n"
        f"`harga` \n"
        f"`desc` \n\n"
        f"Contoh kamu mengetik: `harga`\n"
        f"Lalu bot akan meminta ketik nominal harganya\\."
    )
    await query.message.reply_text(text, parse_mode="MarkdownV2", reply_markup=kb.admin_panel_kb())
    return EDIT_PROD_FIELD

async def edit_prod_field(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    field = update.message.text.strip().lower()
    if field not in ['nama', 'harga', 'desc']:
        await update.message.reply_text("Field tidak valid. Pilih: nama, harga, desc")
        return EDIT_PROD_FIELD
        
    ctx.user_data[CTX_EDIT_FIELD] = field
    await update.message.reply_text(f"Masukkan nilai *{field}* yang baru:", parse_mode="MarkdownV2")
    return EDIT_PROD_VALUE

async def edit_prod_value(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    val = update.message.text.strip()
    field = ctx.user_data.get(CTX_EDIT_FIELD)
    pid = ctx.user_data.get(CTX_TARGET_PROD)
    
    if field == 'harga':
        try:
            val = int(val.replace(".", "").replace(",", ""))
            await db.update_product(pid, price=val)
        except ValueError:
            await update.message.reply_text("Harga harus berupa angka.")
            return EDIT_PROD_VALUE
    elif field == 'nama':
        await db.update_product(pid, name=val)
    elif field == 'desc':
        await db.update_product(pid, description_short=val)
        
    await update.message.reply_text("✅ Produk berhasil diupdate!", reply_markup=kb.admin_panel_kb())
    ctx.user_data.clear()
    return ConversationHandler.END

def get_edit_product_conv():
    return ConversationHandler(
        entry_points=[CallbackQueryHandler(edit_prod_start, pattern=r"^adm_editprod_\d+$")],
        states={
            EDIT_PROD_FIELD: [MessageHandler(filters.TEXT & ~filters.COMMAND, edit_prod_field)],
            EDIT_PROD_VALUE: [MessageHandler(filters.TEXT & ~filters.COMMAND, edit_prod_value)],
        },
        fallbacks=[CommandHandler("cancel", cancel_conv)],
        per_user=True, allow_reentry=True,
    )

def get_add_stock_conv():
    return ConversationHandler(
        entry_points=[CallbackQueryHandler(add_stock_start, pattern=r"^adm_addstock_\d+$")],
        states={
            ADD_STOCK_DATA: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_stock_data)],
        },
        fallbacks=[CommandHandler("cancel", cancel_conv)],
        per_user=True, allow_reentry=True,
    )
def get_broadcast_conv():
    return ConversationHandler(
        entry_points=[CallbackQueryHandler(broadcast_start, pattern="^adm_broadcast$")],
        states={
            BROADCAST_TEXT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, broadcast_send),
                MessageHandler(filters.PHOTO, broadcast_send),
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel_conv)],
        per_user=True, allow_reentry=True,
    )


def get_handlers():
    return [
        CommandHandler("admin", admin_panel),
        CommandHandler("ban", cmd_ban),
        CommandHandler("unban", cmd_unban),
        CommandHandler("reseller", cmd_reseller),
        CommandHandler("info", cmd_user_info),
        CallbackQueryHandler(admin_panel, pattern="^adm_panel$"),
        CallbackQueryHandler(admin_stats, pattern="^adm_stats$"),
        CallbackQueryHandler(admin_categories, pattern="^adm_categories$"),
        CallbackQueryHandler(admin_category_detail, pattern=r"^adm_cat_\d+$"),
        CallbackQueryHandler(admin_toggle_category, pattern=r"^adm_togglecat_\d+$"),
        CallbackQueryHandler(admin_products, pattern="^adm_products$"),
        CallbackQueryHandler(admin_product_detail, pattern=r"^adm_prod_\d+$"),
        CallbackQueryHandler(admin_clear_stock, pattern=r"^adm_clearstock_\d+$"),
        CallbackQueryHandler(delete_product, pattern=r"^adm_delprod_\d+$"),
        CallbackQueryHandler(admin_orders, pattern="^adm_orders$"),
        CallbackQueryHandler(admin_view_order, pattern=r"^adm_vieworder_\d+$"),
        CallbackQueryHandler(admin_users, pattern="^adm_users$"),
        CallbackQueryHandler(admin_settings, pattern="^adm_settings$"),
        # Admin Topup Approvals
        CallbackQueryHandler(admin_approve_topup, pattern=r"^admtp_acc_\d+$"),
        CallbackQueryHandler(admin_reject_topup, pattern=r"^admtp_rej_\d+$"),
        # Admin QRIS Approvals
        CallbackQueryHandler(admin_approve_qris, pattern=r"^approveqris_"),
        CallbackQueryHandler(admin_reject_qris, pattern=r"^rejectqris_"),
    ]
