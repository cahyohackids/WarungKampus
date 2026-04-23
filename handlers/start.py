"""
handlers/start.py — Handler /start, menu utama, cara order, kontak
"""
import logging
import os
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler

import database as db
import messages as msg
import keyboards as kb
from config import STORE_NAME, ADMIN_WA, QRIS_PATH
from utils.helpers import is_admin

log = logging.getLogger(__name__)


async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Handler /start — registrasi user, deteksi referral."""
    user = update.effective_user
    args = ctx.args

    referred_by = None
    if args:
        arg = args[0]
        if arg.startswith("ref_"):
            ref_code = arg[4:]
            referrer = await db.get_user_by_referral(ref_code)
            if referrer and referrer["user_id"] != user.id:
                referred_by = referrer["user_id"]

    user_data = await db.get_or_create_user(
        user_id=user.id,
        username=user.username or "",
        full_name=user.full_name or "",
        referred_by=referred_by
    )

    if user_data.get("is_banned"):
        await update.message.reply_text("⛔ Akun kamu telah dibanned. Hubungi admin.")
        return

    stats = await db.get_stats()
    welcome_text = msg.welcome_msg(user_data, stats)
    welcome_banner = "assets/welcome.jpg"
    banner_exists = os.path.exists(welcome_banner)

    if banner_exists:
        try:
            with open(welcome_banner, "rb") as f:
                await update.message.reply_photo(
                    photo=f,
                    caption=welcome_text,
                    parse_mode="MarkdownV2",
                    reply_markup=kb.main_menu_kb()
                )
        except Exception:
            await update.message.reply_text(
                welcome_text, parse_mode="MarkdownV2", reply_markup=kb.main_menu_kb()
            )
    else:
        await update.message.reply_text(
            welcome_text, parse_mode="MarkdownV2", reply_markup=kb.main_menu_kb()
        )


async def menu_main(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_data = await db.get_user(update.effective_user.id)
    stats = await db.get_stats()
    welcome_text = msg.welcome_msg(user_data, stats)
    try:
        if query.message.photo:
            await query.edit_message_caption(
                caption=welcome_text,
                parse_mode="MarkdownV2",
                reply_markup=kb.main_menu_kb()
            )
        else:
            await query.edit_message_text(
                text=welcome_text,
                parse_mode="MarkdownV2",
                reply_markup=kb.main_menu_kb()
            )
    except Exception as e:
        log.warning("Failed to edit menu_main: %s", e)


async def how_to_order(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.message.reply_text(
        msg.how_to_order_msg(),
        parse_mode="MarkdownV2",
        reply_markup=kb.back_to_main_kb()
    )


async def contact_admin(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    wa_link = f"https://wa.me/{ADMIN_WA}" if ADMIN_WA else ""
    text = (
        f"📞 *Hubungi Admin*\n\n"
        f"Jika ada pertanyaan/keluhan, silakan hubungi:\n"
        + (f"📱 WhatsApp: [Klik di sini]({wa_link})\n" if wa_link else "")
        + f"📨 Ketik /start untuk kembali ke menu utama\\."
    )
    await query.message.reply_text(text, parse_mode="MarkdownV2", reply_markup=kb.back_to_main_kb())


def get_handlers():
    async def dummy_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        await update.callback_query.answer("Fitur ini sedang dalam pengembangan 🛠️", show_alert=True)

    return [
        CommandHandler("start", start),
        CallbackQueryHandler(menu_main, pattern="^menu_main$"),
        CallbackQueryHandler(how_to_order, pattern="^menu_howto$"),
        CallbackQueryHandler(contact_admin, pattern="^menu_contact$"),
        CallbackQueryHandler(dummy_handler, pattern="^menu_popular$"),
        CallbackQueryHandler(dummy_handler, pattern="^menu_other$"),
    ]
