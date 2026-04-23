"""
handlers/topup.py — Alur Top-Up Saldo
"""
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import (
    ContextTypes, CallbackQueryHandler, MessageHandler,
    filters, ConversationHandler, CommandHandler
)

import database as db
import messages as msg
import keyboards as kb
from config import ADMIN_IDS, QRIS_PATH

log = logging.getLogger(__name__)

# States for topup conversation
TOPUP_AMOUNT, TOPUP_PROOF = range(40, 42)

async def cancel_topup(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data.clear()
    if update.message:
        await update.message.reply_text("Top-Up dibatalkan.", reply_markup=kb.back_to_main_kb())
    elif update.callback_query:
        await update.callback_query.message.reply_text("Top-Up dibatalkan.", reply_markup=kb.back_to_main_kb())
    return ConversationHandler.END


async def start_topup(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user = await db.get_user(update.effective_user.id)
    saldo = msg.fmt_rp(user.get("balance", 0))
    
    text = (
        f"💰 *SALDO AKUN*\n\n"
        f"Saldo kamu saat ini: *{msg._e(saldo)}*\n\n"
        f"Silakan pilih nominal Top\\-Up di bawah ini, atau ketik nominal secara manual \\(minimal Rp 5\\.000\\)\\:"
    )
    
    buttons = [
        [InlineKeyboardButton("Rp 10.000", callback_data="topup_10000"),
         InlineKeyboardButton("Rp 20.000", callback_data="topup_20000")],
        [InlineKeyboardButton("Rp 50.000", callback_data="topup_50000"),
         InlineKeyboardButton("Rp 100.000", callback_data="topup_100000")],
        [InlineKeyboardButton("❌ Batalkan", callback_data="cancel_topup")]
    ]
    await query.edit_message_text(text, parse_mode="MarkdownV2", reply_markup=InlineKeyboardMarkup(buttons))
    return TOPUP_AMOUNT

async def topup_amount_btn(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    amount = int(query.data.split("_")[1])
    return await process_topup_amount(update, ctx, amount)

async def topup_amount_txt(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    try:
        amount = int(update.message.text.replace(".", "").replace(",", ""))
        if amount < 5000:
            await update.message.reply_text("Minimal top-up adalah Rp 5.000. Silakan masukkan nominal yang benar:")
            return TOPUP_AMOUNT
        return await process_topup_amount(update, ctx, amount)
    except ValueError:
        await update.message.reply_text("Silakan masukkan *angka* nominal top-up yang benar.", parse_mode="MarkdownV2")
        return TOPUP_AMOUNT

async def process_topup_amount(update: Update, ctx: ContextTypes.DEFAULT_TYPE, amount: int):
    ctx.user_data['topup_amount'] = amount
    
    import os
    if not os.path.exists(QRIS_PATH):
        qris_caption = f"📸 [Upload QRIS kamu di folder {QRIS_PATH}]\n\n"
    else:
        qris_caption = ""
        
    text = (
        f"💳 *PEMBAYARAN TOP\\-UP*\n\n"
        f"Nominal: *{msg._e(msg.fmt_rp(amount))}*\n\n"
        f"Silakan scan QRIS di atas untuk melakukan pembayaran\\.\n"
        f"Jika sudah, *kirimkan foto bukti transfer* ke obrolan ini\\."
    )
    
    msg_obj = update.callback_query.message if update.callback_query else update.message
    
    if os.path.exists(QRIS_PATH):
        with open(QRIS_PATH, "rb") as f:
            await msg_obj.reply_photo(photo=f, caption=text, parse_mode="MarkdownV2", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ Batal", callback_data="cancel_topup")]]))
    else:
        await msg_obj.reply_text(msg._e(qris_caption) + text, parse_mode="MarkdownV2", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ Batal", callback_data="cancel_topup")]]))
    
    return TOPUP_PROOF

async def topup_proof_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not update.message.photo:
        await update.message.reply_text("⚠️ Silakan kirim *foto/gambar* bukti transfer, bukan file atau teks.", parse_mode="MarkdownV2")
        return TOPUP_PROOF

    photo_id = update.message.photo[-1].file_id
    amount = ctx.user_data.get('topup_amount', 0)
    user_id = update.effective_user.id
    
    # Create topup record
    topup_id = await db.create_topup(user_id, amount, photo_id)
    
    await update.message.reply_text(
        f"✅ *BUKTI DITERIMA*\n\nPermintaan Top\\-Up Saldo senilai *{msg._e(msg.fmt_rp(amount))}* sedang diproses oleh admin\\.",
        parse_mode="MarkdownV2",
        reply_markup=kb.back_to_main_kb()
    )
    
    # Notify admin
    admin_text = (
        f"💳 *REQUEST TOP\\-UP BARU*\n\n"
        f"ID Topup: `{topup_id}`\n"
        f"User ID: `{user_id}`\n"
        f"Nominal: *{msg._e(msg.fmt_rp(amount))}*\n"
    )
    admin_kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ APPROVE TOPUP", callback_data=f"admtp_acc_{topup_id}")],
        [InlineKeyboardButton("❌ REJECT TOPUP", callback_data=f"admtp_rej_{topup_id}")]
    ])
    
    for admin in ADMIN_IDS:
        try:
            await ctx.bot.send_photo(chat_id=admin, photo=photo_id, caption=admin_text, parse_mode="MarkdownV2", reply_markup=admin_kb)
        except Exception as e:
            log.error("Gagal kirim notif topup ke admin %s: %s", admin, e)
            
    ctx.user_data.clear()
    return ConversationHandler.END


def get_topup_conv():
    return ConversationHandler(
        entry_points=[CallbackQueryHandler(start_topup, pattern="^menu_saldo$")],
        states={
            TOPUP_AMOUNT: [
                CallbackQueryHandler(topup_amount_btn, pattern="^topup_\\d+$"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, topup_amount_txt)
            ],
            TOPUP_PROOF: [
                MessageHandler(filters.PHOTO, topup_proof_handler),
                MessageHandler(filters.TEXT & ~filters.COMMAND, topup_proof_handler)
            ]
        },
        fallbacks=[
            CommandHandler("cancel", cancel_topup),
            CallbackQueryHandler(cancel_topup, pattern="^cancel_topup$")
        ],
        per_user=True, allow_reentry=True
    )
