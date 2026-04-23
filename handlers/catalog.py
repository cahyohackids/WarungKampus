"""
handlers/catalog.py — Browse kategori & produk
"""
import logging
from telegram import Update
from telegram.ext import ContextTypes, CallbackQueryHandler

import database as db
import messages as msg
import keyboards as kb

log = logging.getLogger(__name__)


async def show_catalog(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    categories = await db.get_categories(active_only=True)

    if not categories:
        await query.message.reply_text(
            "📭 Belum ada kategori produk tersedia\\.",
            parse_mode="MarkdownV2",
            reply_markup=kb.back_to_main_kb()
        )
        return

    await query.message.reply_text(
        msg.catalog_msg(categories),
        parse_mode="MarkdownV2",
        reply_markup=kb.categories_kb(categories)
    )


async def show_products(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data  # cat_<id>
    cat_id = int(data.split("_")[1])
    category = await db.get_category(cat_id)
    if not category:
        await query.answer("Kategori tidak ditemukan.", show_alert=True)
        return

    products = await db.get_products(category_id=cat_id, active_only=True)
    if not products:
        await query.message.reply_text(
            f"📭 Belum ada produk di kategori *{category['name']}*\\.",
            parse_mode="MarkdownV2",
            reply_markup=kb.back_to_main_kb()
        )
        return

    text = (
        f"{category['emoji']} *{category['name'].upper()}*\n"
        f"Tersedia *{len(products)} produk* \\- pilih untuk detail\\:"
    )
    await query.message.reply_text(
        text,
        parse_mode="MarkdownV2",
        reply_markup=kb.products_kb(products, page=0, cat_id=cat_id)
    )


async def product_page(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Handle pagination produk: ppage_<cat_id>_<page>"""
    query = update.callback_query
    await query.answer()
    _, cat_id, page = query.data.split("_")
    cat_id, page = int(cat_id), int(page)

    products = await db.get_products(category_id=cat_id, active_only=True)
    await query.edit_message_reply_markup(
        reply_markup=kb.products_kb(products, page=page, cat_id=cat_id)
    )


async def show_product_detail(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    product_id = int(query.data.split("_")[1])
    product = await db.get_product(product_id)
    if not product:
        await query.answer("Produk tidak ditemukan.", show_alert=True)
        return

    await query.message.reply_text(
        msg.product_card_msg(product),
        parse_mode="MarkdownV2",
        reply_markup=kb.product_detail_kb(product)
    )


def get_handlers():
    return [
        CallbackQueryHandler(show_catalog, pattern="^menu_catalog$"),
        CallbackQueryHandler(show_products, pattern=r"^cat_\d+$"),
        CallbackQueryHandler(product_page, pattern=r"^ppage_\d+_\d+$"),
        CallbackQueryHandler(show_product_detail, pattern=r"^prod_\d+$"),
    ]
