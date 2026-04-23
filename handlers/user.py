"""
handlers/user.py — Profil user & riwayat order
"""
import logging
from telegram import Update
from telegram.ext import ContextTypes, CallbackQueryHandler, CommandHandler

import database as db
import messages as msg
import keyboards as kb

log = logging.getLogger(__name__)


async def show_profile(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user = await db.get_user(update.effective_user.id)
    if not user:
        await query.answer("User tidak ditemukan.", show_alert=True)
        return

    orders = await db.get_user_orders(update.effective_user.id, limit=1000)
    await query.message.reply_text(
        msg.profile_msg(user, len(orders)),
        parse_mode="MarkdownV2",
        reply_markup=kb.profile_kb(update.effective_user.id)
    )


async def show_my_referral(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user = await db.get_user(update.effective_user.id)
    if not user:
        return

    from config import BOT_USERNAME
    ref_link = f"https://t\\.me/{BOT_USERNAME}?start=ref_{user['referral_code']}"
    text = (
        f"🔗 *LINK REFERRAL KAMU*\n\n"
        f"`{ref_link}`\n\n"
        f"Share link ini ke temanmu\\! Setiap teman yang daftar via linkmu akan tercatat\\."
    )
    await query.message.reply_text(
        text,
        parse_mode="MarkdownV2",
        reply_markup=kb.back_to_main_kb()
    )


async def show_orders(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    orders = await db.get_user_orders(update.effective_user.id, limit=50)
    if not orders:
        await query.message.reply_text(
            "📭 Kamu belum memiliki order apapun\\.",
            parse_mode="MarkdownV2",
            reply_markup=kb.back_to_main_kb()
        )
        return

    page = int(ctx.user_data.get("orders_page", 0))
    await query.message.reply_text(
        f"📦 *RIWAYAT ORDER* \\({len(orders)} transaksi\\)",
        parse_mode="MarkdownV2",
        reply_markup=kb.orders_kb(orders, page=page)
    )


async def orders_pagination(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    page = int(query.data.split("_")[2])
    ctx.user_data["orders_page"] = page
    orders = await db.get_user_orders(update.effective_user.id, limit=50)
    await query.edit_message_reply_markup(reply_markup=kb.orders_kb(orders, page=page))


async def view_order_detail(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    order_id = int(query.data.split("_")[2])
    order = await db.get_order(order_id)

    if not order or order["user_id"] != update.effective_user.id:
        await query.answer("Order tidak ditemukan.", show_alert=True)
        return

    await query.message.reply_text(
        msg.order_detail_msg(order),
        parse_mode="MarkdownV2",
        reply_markup=kb.back_to_main_kb()
    )


async def cmd_orders(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    orders = await db.get_user_orders(update.effective_user.id, limit=50)
    if not orders:
        await update.message.reply_text(
            "📭 Belum ada order\\.",
            parse_mode="MarkdownV2"
        )
        return
    await update.message.reply_text(
        f"📦 *RIWAYAT ORDER* \\({len(orders)} transaksi\\)",
        parse_mode="MarkdownV2",
        reply_markup=kb.orders_kb(orders, page=0)
    )


def get_handlers():
    return [
        CommandHandler("orders", cmd_orders),
        CallbackQueryHandler(show_profile, pattern="^menu_profile$"),
        CallbackQueryHandler(show_my_referral, pattern="^my_referral$"),
        CallbackQueryHandler(show_orders, pattern="^menu_orders$"),
        CallbackQueryHandler(orders_pagination, pattern=r"^orders_page_\d+$"),
        CallbackQueryHandler(view_order_detail, pattern=r"^view_order_\d+$"),
    ]
