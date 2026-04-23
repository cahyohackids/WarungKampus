"""
handlers/order.py — Alur pemesanan lengkap dengan QRIS
States:
  SELECTING_QTY     → user memilih jumlah
  CONFIRM_ORDER     → user konfirmasi sebelum bayar
  UPLOAD_PROOF      → user upload bukti transfer
"""
import logging
import os
from telegram import Update, InputFile
from telegram.ext import (
    ContextTypes, CallbackQueryHandler, MessageHandler,
    ConversationHandler, filters, CommandHandler
)

import database as db
import messages as msg
import keyboards as kb
from config import ADMIN_IDS, QRIS_PATH, PAYMENT_INFO, PAYMENT_NAME
from utils.helpers import is_admin

log = logging.getLogger(__name__)

# Conversation states
SELECTING_QTY = 1
CONFIRM_ORDER = 2
UPLOAD_PROOF = 3
TYPING_QTY = 4

# Context keys
CTX_PRODUCT_ID = "order_product_id"
CTX_QTY = "order_qty"
CTX_PRICE = "order_price"
CTX_ORDER_ID = "order_id"


async def _send_order_result(chat_id: int, order: dict, result_data: str, payment_method: str, bot):
    """Send order result as .txt file + receipt message + CS contact, like RUMAH PREMIUM bot."""
    import io
    from telegram import InputFile
    from config import ADMIN_WA, BOT_USERNAME, STORE_NAME
    
    user_id = order.get("user_id", chat_id)
    order_code = order.get("order_code", "N/A")
    
    # 1) Send account data as a .txt file
    file_content = result_data
    filename = f"{user_id}-{order_code}.txt"
    txt_file = io.BytesIO(file_content.encode("utf-8"))
    txt_file.name = filename
    
    try:
        await bot.send_document(
            chat_id=chat_id,
            document=InputFile(txt_file, filename=filename),
            caption=f"📄 Data akun pesanan `{order_code}`",
            parse_mode="MarkdownV2"
        )
    except Exception as e:
        log.warning("Failed sending txt file: %s", e)
    
    # 2) Send formatted receipt message
    receipt_text = msg.order_completed_msg(order, result_data, payment_method)
    try:
        await bot.send_message(
            chat_id=chat_id,
            text=receipt_text,
            parse_mode="MarkdownV2"
        )
    except Exception as e:
        log.warning("Failed sending receipt: %s", e)
    
    # 3) Send CS contact card
    cs_wa_link = f"https://wa.me/{ADMIN_WA}" if ADMIN_WA else ""
    cs_tg_link = f"https://t.me/{BOT_USERNAME}"
    contact_text = (
        f"Telegram\n"
        f"{STORE_NAME} CS\n\n"
        f"Hubungi admin jika ada masalah:\n"
    )
    if cs_wa_link:
        contact_text += f"📱 WA: {cs_wa_link}\n"
    contact_text += f"💬 Telegram: {cs_tg_link}"
    
    try:
        await bot.send_message(
            chat_id=chat_id,
            text=contact_text,
            disable_web_page_preview=False
        )
    except Exception as e:
        log.warning("Failed sending CS contact: %s", e)


# ══════════════════════════════════════════════════════════════
#  STEP 1: Mulai order — pilih qty
# ══════════════════════════════════════════════════════════════

async def start_order(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    product_id = int(query.data.split("_")[2])  # order_start_<id>
    product = await db.get_product(product_id)

    if not product or product["stock"] <= 0:
        await query.answer("❌ Stok produk habis!", show_alert=True)
        return ConversationHandler.END

    ctx.user_data[CTX_PRODUCT_ID] = product_id
    ctx.user_data[CTX_PRICE] = product["price"]
    ctx.user_data[CTX_QTY] = 1

    user_data = await db.get_user(update.effective_user.id)
    if user_data and user_data.get("is_reseller") and product.get("reseller_price"):
        ctx.user_data[CTX_PRICE] = product["reseller_price"]

    max_qty = product["stock"]

    await query.message.reply_text(
        msg.order_summary_msg(product, 1, user_data or {}),
        parse_mode="MarkdownV2",
        reply_markup=kb.order_checkout_kb(1, max_qty)
    )
    return SELECTING_QTY


# ══════════════════════════════════════════════════════════════
#  STEP 2: Modifikasi Jumlah / Checkout
# ══════════════════════════════════════════════════════════════

async def select_qty(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "order_cancel":
        await query.edit_message_text("❌ Order dibatalkan\\.", parse_mode="MarkdownV2")
        ctx.user_data.clear()
        return ConversationHandler.END

    product_id = ctx.user_data.get(CTX_PRODUCT_ID)
    product = await db.get_product(product_id)
    if not product:
        return ConversationHandler.END
        
    user_data = await db.get_user(update.effective_user.id)
    max_qty = product["stock"]

    # Handle payments
    if data in ["pay_qris", "pay_balance"]:
        qty = ctx.user_data.get(CTX_QTY, 1)
        price = product["price"]
        if qty >= (product.get("wholesale_min_qty") or 999) and product.get("wholesale_price"):
            price = product["wholesale_price"]
        elif user_data and user_data.get("is_reseller") and product.get("reseller_price"):
            price = product["reseller_price"]
        
        total = price * qty
        
        if data == "pay_balance":
            if user_data.get("balance", 0) < total:
                await query.answer("❌ Kouta saldo kamu tidak mencukupi!", show_alert=True)
                return SELECTING_QTY
                
            # Process balance payment directly
            order = await db.create_order(
                user_id=update.effective_user.id, product_id=product_id,
                product_name=product["name"], qty=qty, unit_price=price
            )
            # deduct balance and approve
            await db.deduct_balance(update.effective_user.id, total)
            await db.update_order_status(order["id"], "paid", payment_proof="balance")
            # Complete order logic is same as admin_approve_order
            accounts = await db.take_accounts(order["product_id"], order["qty"])
            if not accounts:
                await query.edit_message_text("❌ Stok akun habis di server\\! Silakan hubungi admin\\.", parse_mode="MarkdownV2")
                return ConversationHandler.END
            result_data = "\n".join(accounts)
            await db.complete_order(order["id"], result_data)
            
            # Send account data as .txt file
            await _send_order_result(query.message.chat_id, order, result_data, "balance", ctx.bot)
            
            ctx.user_data.clear()
            return ConversationHandler.END
            
        else:
            # Pay using QRIS
            order = await db.create_order(
                user_id=update.effective_user.id, product_id=product_id,
                product_name=product["name"], qty=qty, unit_price=price
            )
            ctx.user_data[CTX_ORDER_ID] = order["id"]
            
            # Show QRIS
            invoice_text = msg.invoice_msg(order)
            try:
                import os
                if os.path.exists(QRIS_PATH):
                    with open(QRIS_PATH, "rb") as qris_file:
                        await query.message.reply_photo(
                            photo=qris_file, caption=invoice_text, parse_mode="MarkdownV2",
                            reply_markup=kb.cancel_order_kb(order["id"])
                        )
                else:
                    raise FileNotFoundError
            except FileNotFoundError:
                await query.message.reply_text(
                    invoice_text + "\n\n📷 \\[Upload QRIS kamu di folder assets/qris\\.jpg\\]",
                    parse_mode="MarkdownV2", reply_markup=kb.cancel_order_kb(order["id"])
                )
            await query.message.reply_text("📸 *Kirim foto bukti transfer di sini* setelah membayar\\.", parse_mode="MarkdownV2")
            return UPLOAD_PROOF

    # Handle quantity modifications
    current_qty = ctx.user_data.get(CTX_QTY, 1)
    if data.startswith("qty_"):
        val = data.split("_")[1]
        if val == "custom":
            msg_sent = await query.message.reply_text("Silakan ketik angka jumlah pesanan:")
            ctx.user_data["prompt_msg_id"] = msg_sent.message_id
            return TYPING_QTY
        elif val == "all":
            current_qty = max_qty
        else:
            current_qty += int(val)
            
    # Clamp quantity
    if current_qty < 1:
        current_qty = 1
    if current_qty > max_qty:
        current_qty = max_qty
        
    ctx.user_data[CTX_QTY] = current_qty

    # Update message if modified
    try:
        await query.edit_message_text(
            msg.order_summary_msg(product, current_qty, user_data or {}),
            parse_mode="MarkdownV2",
            reply_markup=kb.order_checkout_kb(current_qty, max_qty)
        )
    except Exception:
        pass
        
    return SELECTING_QTY


# ══════════════════════════════════════════════════════════════
#  STEP 3: Tampilkan QRIS — upload bukti bayar
# ══════════════════════════════════════════════════════════════

async def confirm_payment(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    order_id = int(query.data.split("_")[2])  # confirm_pay_<id>
    order = await db.get_order(order_id)

    if not order:
        await query.answer("Order tidak ditemukan.", show_alert=True)
        return ConversationHandler.END

    ctx.user_data[CTX_ORDER_ID] = order_id

    # Kirim QRIS
    invoice_text = msg.invoice_msg(order)
    try:
        with open(QRIS_PATH, "rb") as qris_file:
            await query.message.reply_photo(
                photo=qris_file,
                caption=invoice_text,
                parse_mode="MarkdownV2",
                reply_markup=kb.cancel_order_kb(order_id)
            )
    except FileNotFoundError:
        await query.message.reply_text(
            invoice_text + "\n\n📷 \\[Upload QRIS kamu di folder assets/qris\\.jpg\\]",
            parse_mode="MarkdownV2",
            reply_markup=kb.cancel_order_kb(order_id)
        )

    await query.message.reply_text(
        "📸 *Kirim foto bukti transfer di sini* setelah membayar\\.",
        parse_mode="MarkdownV2"
    )
    return UPLOAD_PROOF


async def cancel_order_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    order_id = int(query.data.split("_")[2])  # cancel_order_<id>
    await db.update_order_status(order_id, "cancelled")
    order = await db.get_order(order_id)

    await query.message.reply_text(
        msg.order_cancelled_msg(order.get("order_code", str(order_id))),
        parse_mode="MarkdownV2",
        reply_markup=kb.back_to_main_kb()
    )
    ctx.user_data.clear()
    return ConversationHandler.END


# ══════════════════════════════════════════════════════════════
#  STEP 4: User upload bukti bayar → notif admin
# ══════════════════════════════════════════════════════════════

async def receive_payment_proof(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Terima foto bukti bayar dari user."""
    order_id = ctx.user_data.get(CTX_ORDER_ID)
    if not order_id:
        await update.message.reply_text(
            "⚠️ Sesi order tidak ditemukan\\. Silakan mulai order ulang\\.",
            parse_mode="MarkdownV2",
            reply_markup=kb.back_to_main_kb()
        )
        return ConversationHandler.END

    if not update.message.photo:
        await update.message.reply_text(
            "📸 Harap kirim *foto* bukti transfer\\.",
            parse_mode="MarkdownV2"
        )
        return UPLOAD_PROOF

    file_id = update.message.photo[-1].file_id
    order = await db.get_order(order_id)
    if not order:
        return ConversationHandler.END

    await db.set_payment_proof(order_id, file_id)
    order = await db.get_order(order_id)

    # Konfirmasi ke user
    await update.message.reply_text(
        msg.payment_received_msg(order),
        parse_mode="MarkdownV2",
        reply_markup=kb.after_payment_kb()
    )

    # Notif ke semua admin
    user = await db.get_user(update.effective_user.id)
    admin_caption = msg.admin_new_order_msg(order, user or {})
    for admin_id in ADMIN_IDS:
        try:
            await ctx.bot.send_photo(
                chat_id=admin_id,
                photo=file_id,
                caption=admin_caption,
                parse_mode="MarkdownV2",
                reply_markup=kb.admin_order_kb(order_id)
            )
        except Exception as e:
            log.warning("Gagal notif admin %s: %s", admin_id, e)

    ctx.user_data.clear()
    return ConversationHandler.END


# ══════════════════════════════════════════════════════════════
#  ADMIN: Approve / Reject order
# ══════════════════════════════════════════════════════════════

async def admin_approve_order(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if not is_admin(update.effective_user.id):
        await query.answer("⛔ Bukan admin!", show_alert=True)
        return

    order_id = int(query.data.split("_")[2])  # adm_approve_<id>
    order = await db.get_order(order_id)
    if not order:
        await query.answer("Order tidak ditemukan.", show_alert=True)
        return

    if order["status"] not in ("paid", "waiting_payment", "processing"):
        await query.answer(f"Status order sudah: {order['status']}", show_alert=True)
        return

    # Ambil akun dari stok
    accounts = await db.take_accounts(order["product_id"], order["qty"])

    if not accounts:
        await query.answer("❌ Stok akun habis! Tambahkan stok dulu.", show_alert=True)
        await ctx.bot.send_message(
            update.effective_user.id,
            f"⚠️ Stok akun untuk produk *{order['product_name']}* habis\\! Tambahkan stok segera\\.",
            parse_mode="MarkdownV2"
        )
        return

    result_data = "\n".join(accounts)
    await db.complete_order(order_id, result_data)

    # Update users stats
    async with __import__("aiosqlite").connect(__import__("config").DB_PATH) as dbc:
        await dbc.execute("""
            UPDATE users SET total_orders=total_orders+1, total_spent=total_spent+?
            WHERE user_id=?
        """, (order["total_price"], order["user_id"]))
        await dbc.commit()

    # Kirim hasil ke user (file .txt + receipt + CS contact)
    try:
        payment_method = order.get("payment_proof", "qris")
        if payment_method == "balance":
            pm = "balance"
        else:
            pm = "qris"
        await _send_order_result(order["user_id"], order, result_data, pm, ctx.bot)
    except Exception as e:
        log.warning("Gagal kirim produk ke user: %s", e)

    # Update pesan admin
    await query.edit_message_caption(
        caption=f"✅ *ORDER DIAPPROVE*\n\nKode: `{order['order_code']}`\nProduk terkirim ke user\\.",
        parse_mode="MarkdownV2"
    )


async def admin_reject_order(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if not is_admin(update.effective_user.id):
        await query.answer("⛔ Bukan admin!", show_alert=True)
        return

    order_id = int(query.data.split("_")[2])  # adm_reject_<id>
    order = await db.get_order(order_id)
    if not order:
        await query.answer("Order tidak ditemukan.", show_alert=True)
        return

    await db.update_order_status(order_id, "rejected")

    try:
        await ctx.bot.send_message(
            chat_id=order["user_id"],
            text=msg.order_cancelled_msg(order["order_code"], "Pembayaran tidak valid"),
            parse_mode="MarkdownV2",
            reply_markup=kb.back_to_main_kb()
        )
    except Exception as e:
        log.warning("Gagal notif user: %s", e)

    await query.edit_message_caption(
        caption=f"❌ *ORDER DITOLAK*\n\nKode: `{order['order_code']}`",
        parse_mode="MarkdownV2"
    )

async def typing_qty_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    try:
        qty = int(update.message.text.replace(".", "").replace(",", ""))
    except ValueError:
        await update.message.reply_text("❌ Harap masukkan *angka*.", parse_mode="MarkdownV2")
        return TYPING_QTY
        
    product_id = ctx.user_data.get(CTX_PRODUCT_ID)
    product = await db.get_product(product_id)
    max_qty = product["stock"]
    
    if qty < 1:
        qty = 1
    if qty > max_qty:
        qty = max_qty
        
    ctx.user_data[CTX_QTY] = qty
    
    # Try to edit the older prompt if we know its message_id
    user_data_db = await db.get_user(update.effective_user.id)
    prompt_id = ctx.user_data.get("prompt_msg_id")
    if prompt_id:
        try:
            await ctx.bot.delete_message(chat_id=update.effective_chat.id, message_id=prompt_id)
        except Exception:
            pass
            
    await update.message.reply_text(
        msg.order_summary_msg(product, qty, user_data_db or {}),
        parse_mode="MarkdownV2",
        reply_markup=kb.order_checkout_kb(qty, max_qty)
    )
    return SELECTING_QTY

async def cancel_conv(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data.clear()
    return ConversationHandler.END

async def receive_payment_text(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "⚠️ Silakan *kirim foto/gambar* bukti transfer.\nJika ingin membatalkan order ini, ketik /cancel",
        parse_mode="MarkdownV2"
    )
    return UPLOAD_PROOF


def get_conversation_handler() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[
            CallbackQueryHandler(start_order, pattern=r"^order_start_\d+$"),
        ],
        states={
            SELECTING_QTY: [
                CallbackQueryHandler(select_qty, pattern=r"^(qty_.*|pay_.*|order_cancel)$"),
            ],
            TYPING_QTY: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, typing_qty_handler)
            ],
            CONFIRM_ORDER: [
                CallbackQueryHandler(confirm_payment, pattern=r"^confirm_pay_\d+$"),
                CallbackQueryHandler(cancel_order_handler, pattern=r"^cancel_order_\d+$"),
            ],
            UPLOAD_PROOF: [
                MessageHandler(filters.PHOTO, receive_payment_proof),
                CallbackQueryHandler(cancel_order_handler, pattern=r"^cancel_order_\d+$"),
            ],
        },
        fallbacks=[
            CommandHandler("start", cancel_conv),
            CommandHandler("cancel", cancel_conv),
            MessageHandler(filters.TEXT & ~(filters.COMMAND), receive_payment_text)
        ],
        per_user=True,
        per_chat=True,
        allow_reentry=True,
    )


def get_handlers():
    return [
        CallbackQueryHandler(admin_approve_order, pattern=r"^adm_approve_\d+$"),
        CallbackQueryHandler(admin_reject_order, pattern=r"^adm_reject_\d+$"),
    ]
