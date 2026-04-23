"""
main.py — Entry point Warung Kampus Auto Order Bot
Menginisialisasi semua handler, database, dan scheduler.
"""
import asyncio
import logging
import os
import sys

from telegram import BotCommand, Update
from telegram.ext import ApplicationBuilder, ContextTypes

from config import BOT_TOKEN, ADMIN_IDS, STORE_NAME
import database as db
from utils.scheduler import register_jobs

# ── Handlers ──
from handlers import start, catalog, order, user, topup, admin as admin_handler

# ══════════════════════════════════════════════════════════════
#  LOGGING SETUP
# ══════════════════════════════════════════════════════════════

logging.basicConfig(
    format="%(asctime)s | %(levelname)-8s | %(name)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("bot.log", encoding="utf-8"),
    ]
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("telegram").setLevel(logging.WARNING)
log = logging.getLogger(__name__)


# ══════════════════════════════════════════════════════════════
#  BOT COMMANDS MENU
# ══════════════════════════════════════════════════════════════

USER_COMMANDS = [
    BotCommand("start",  "🏠 Menu utama"),
    BotCommand("orders", "📦 Riwayat pesanan saya"),
    BotCommand("cancel", "❌ Batalkan proses saat ini"),
]

ADMIN_COMMANDS = [
    BotCommand("start",    "🏠 Menu utama"),
    BotCommand("admin",    "⚙️ Panel admin"),
    BotCommand("orders",   "📦 Riwayat pesanan"),
    BotCommand("ban",      "🔨 Ban user"),
    BotCommand("unban",    "✅ Unban user"),
    BotCommand("reseller", "👑 Set reseller"),
    BotCommand("info",     "ℹ️ Info user"),
    BotCommand("cancel",   "❌ Batalkan proses saat ini"),
]


async def post_init(app):
    """Callback setelah bot siap — set commands & kirim notif ke admin."""
    bot = app.bot

    # Set command untuk user biasa
    await bot.set_my_commands(USER_COMMANDS)

    # Set command khusus admin
    from telegram import BotCommandScopeChat
    for admin_id in ADMIN_IDS:
        try:
            await bot.set_my_commands(ADMIN_COMMANDS, scope=BotCommandScopeChat(admin_id))
        except Exception as e:
            log.warning("Gagal set admin commands untuk %s: %s", admin_id, e)

    # Notif ke admin bahwa bot nyala
    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(
                chat_id=admin_id,
                text=(
                    f"✅ *{STORE_NAME}* \— Bot aktif\\!\n\n"
                    f"Ketik /admin untuk membuka panel admin\\."
                ),
                parse_mode="MarkdownV2"
            )
        except Exception:
            pass

    log.info("🚀 Bot %s siap!", STORE_NAME)


# ══════════════════════════════════════════════════════════════
#  ERROR HANDLER
# ══════════════════════════════════════════════════════════════

async def error_handler(update: object, ctx: ContextTypes.DEFAULT_TYPE):
    log.error("Update %s caused error: %s", update, ctx.error, exc_info=ctx.error)
    if isinstance(update, Update) and update.effective_message:
        try:
            await update.effective_message.reply_text(
                "⚠️ Terjadi error internal\\. Silakan coba lagi atau hubungi admin\\.",
                parse_mode="MarkdownV2"
            )
        except Exception:
            pass


# ══════════════════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════════════════

def main():
    if not BOT_TOKEN:
        log.critical("BOT_TOKEN tidak ditemukan di .env!")
        sys.exit(1)

    # Init database
    asyncio.run(db.init_db())

    # Build application
    app = (
        ApplicationBuilder()
        .token(BOT_TOKEN)
        .post_init(post_init)
        .build()
    )

    # ── Register handlers (URUTAN PENTING: ConversationHandler lebih dulu) ──

    # 1. Admin conversation handlers (prioritas tertinggi)
    app.add_handler(admin_handler.get_add_category_conv())
    app.add_handler(admin_handler.get_add_product_conv())
    app.add_handler(admin_handler.get_edit_product_conv())
    app.add_handler(admin_handler.get_add_stock_conv())
    app.add_handler(admin_handler.get_broadcast_conv())

    # 2. Order & Topup & QRIS conversation handler
    app.add_handler(order.get_conversation_handler())
    app.add_handler(topup.get_topup_conv())
    from handlers import checkout
    app.add_handler(checkout.get_qris_checkout_conv())

    # 3. Regular handlers
    for handler in start.get_handlers():
        app.add_handler(handler)

    for handler in catalog.get_handlers():
        app.add_handler(handler)

    for handler in order.get_handlers():
        app.add_handler(handler)

    for handler in user.get_handlers():
        app.add_handler(handler)

    for handler in admin_handler.get_handlers():
        app.add_handler(handler)

    # 4. Error handler
    app.add_error_handler(error_handler)

    # 🔥 Automatically start HTTPS tunnel for the Web App
    import subprocess, re, time
    log.info("Starting Cloudflare tunnel...")
    try:
        import os
        if os.path.exists("cloudflare.log"): os.remove("cloudflare.log")
        subprocess.Popen("./cloudflared tunnel --url http://localhost:8080 > cloudflare.log 2>&1", shell=True)
        
        for _ in range(15):
            time.sleep(1)
            if os.path.exists("cloudflare.log"):
                with open("cloudflare.log", "r") as f:
                    content = f.read()
                    match = re.search(r"https://[a-zA-Z0-9-]+\.trycloudflare\.com", content)
                    if match:
                        import config
                        config.WEBAPP_URL = match.group(0)
                        log.info("✅ Tunnel active: %s", config.WEBAPP_URL)
                        break
    except Exception as e:
        log.warning("Tunnel start failed: %s", e)

    log.info("▶️  Starting %s bot with FastAPI server...", STORE_NAME)
    
    async def run_all():
        import uvicorn
        import api
        from api import app as fastapi_app
        api.bot_instance = app.bot
        
        config = uvicorn.Config(fastapi_app, host="0.0.0.0", port=8080, log_level="info")
        server = uvicorn.Server(config)
        
        await app.initialize()
        await app.start()
        await app.updater.start_polling(drop_pending_updates=True, allowed_updates=Update.ALL_TYPES)
        
        try:
            await server.serve()
        except Exception as e:
            log.error("Uvicorn stopped: %s", e)
        finally:
            await app.updater.stop()
            await app.stop()
            await app.shutdown()
            
    asyncio.run(run_all())

if __name__ == "__main__":
    main()
