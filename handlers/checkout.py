import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    ContextTypes, CallbackQueryHandler, MessageHandler,
    filters, ConversationHandler, CommandHandler
)

import database as db
import messages as msg
import keyboards as kb
from config import ADMIN_IDS

log = logging.getLogger(__name__)

# State
UPLOAD_QRIS_PROOF = 50

async def cancel_qris_proof(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data.pop("qris_order_ids", None)
    if update.message:
        await update.message.reply_text("Upload bukti QRIS dibatalkan.", reply_markup=kb.back_to_main_kb())
    elif update.callback_query:
        await update.callback_query.message.reply_text("Upload bukti QRIS dibatalkan.", reply_markup=kb.back_to_main_kb())
    return ConversationHandler.END

async def start_upload_proof(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    # data: qrisproof_12,13,14
    order_ids_str = query.data.split("_")[1]
    ctx.user_data["qris_order_ids"] = order_ids_str
    
    text = (
        "📸 *UPLOAD BUKTI TRANSFER*\n\n"
        "Silakan kirim foto/gambar bukti transfer pembayaran QRIS Anda ke obrolan ini\\."
    )
    markup = InlineKeyboardMarkup([[InlineKeyboardButton("❌ Batal", callback_data="cancel_qris_proof")]])
    await query.message.reply_text(text, parse_mode="MarkdownV2", reply_markup=markup)
    return UPLOAD_QRIS_PROOF

async def receive_qris_proof(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not update.message.photo:
        await update.message.reply_text("⚠️ Silakan kirim *foto* bukti transfer, bukan file dokumen.", parse_mode="MarkdownV2")
        return UPLOAD_QRIS_PROOF
        
    order_ids_str = ctx.user_data.get("qris_order_ids")
    if not order_ids_str:
        await update.message.reply_text("Sesi upload kadaluarsa. Silakan mulai ulang.")
        return ConversationHandler.END
        
    photo_file_id = update.message.photo[-1].file_id
    user = update.effective_user
    
    # Forward to Admins
    order_ids = order_ids_str.split(",")
    total_cost = 0
    items_desc = ""
    
    # Calculate total dynamically based on pending orders
    for oid in order_ids:
        order = await db.get_order(int(oid))
        if order:
            total_cost += order["total_price"]
            items_desc += f"- {order['product_name']} x{order['qty']}\n"
            # Update proof in DB
            await db.update_order_status(order["id"], "pending_admin", payment_proof=photo_file_id)
            
    admin_text = (
        f"🚨 *NEW QRIS ORDER PENDING!*\n\n"
        f"👤 User: {user.first_name} (`{user.id}`)\n"
        f"💰 Total: *Rp {total_cost:,.0f}*\n"
        f"📦 Items:\n{items_desc}\n\n"
        f"Silakan periksa bukti bayar ini."
    )
    markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Approve", callback_data=f"approveqris_{order_ids_str}")],
        [InlineKeyboardButton("❌ Reject", callback_data=f"rejectqris_{order_ids_str}")]
    ])
    
    for admin_id in ADMIN_IDS:
        try:
            await ctx.bot.send_photo(chat_id=admin_id, photo=photo_file_id, caption=msg._e(admin_text), parse_mode="MarkdownV2", reply_markup=markup)
        except Exception as e:
            log.warning("Failed sending QRIS approval to admin %s: %s", admin_id, e)
            
    await update.message.reply_text(
        msg._e(
            "✅ *Bukti transfer berhasil dikirim!*\n\n"
            "Admin akan segera mengecek pembayaran Anda. Mohon tunggu beberapa saat 😊"
        ),
        parse_mode="MarkdownV2"
    )
    
    ctx.user_data.pop("qris_order_ids", None)
    return ConversationHandler.END

def get_qris_checkout_conv():
    return ConversationHandler(
        entry_points=[CallbackQueryHandler(start_upload_proof, pattern=r"^qrisproof_")],
        states={
            UPLOAD_QRIS_PROOF: [MessageHandler(filters.PHOTO, receive_qris_proof)]
        },
        fallbacks=[
            CommandHandler("cancel", cancel_qris_proof),
            CallbackQueryHandler(cancel_qris_proof, pattern="^cancel_qris_proof$")
        ],
        per_user=True, allow_reentry=True,
    )
