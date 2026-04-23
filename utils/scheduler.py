"""
utils/scheduler.py — Background jobs menggunakan APScheduler via PTB JobQueue
"""
import logging
from datetime import datetime, timedelta
from telegram.ext import ContextTypes

import database as db
from config import ADMIN_IDS, PAYMENT_TIMEOUT_HOURS, TIMEZONE
from utils.helpers import fmt_rp

log = logging.getLogger(__name__)


async def job_reminder_pending_orders(ctx: ContextTypes.DEFAULT_TYPE):
    """
    Cek order yang sudah lama waiting_payment dan belum bayar.
    Kirim reminder ke user + notif ke admin.
    """
    orders = await db.get_orders_by_status("waiting_payment", limit=100)
    now = datetime.now()
    reminded = 0

    for order in orders:
        try:
            created = datetime.strptime(order["created_at"][:19], "%Y-%m-%d %H:%M:%S")
            age_hours = (now - created).total_seconds() / 3600

            # Belum lewat batas waktu, kirim reminder di 1 jam
            if 0.9 <= age_hours < 1.1:
                try:
                    await ctx.bot.send_message(
                        chat_id=order["user_id"],
                        text=(
                            f"⏰ *REMINDER PEMBAYARAN*\n\n"
                            f"Order `{order['order_code']}` kamu belum dibayar\\!\n"
                            f"Total: *Rp {order['total_price']:,}*\n\n"
                            f"Segera bayar sebelum order otomatis dibatalkan dalam "
                            f"{PAYMENT_TIMEOUT_HOURS - 1} jam lagi\\."
                        ),
                        parse_mode="MarkdownV2"
                    )
                    reminded += 1
                except Exception:
                    pass

            # Sudah melewati batas waktu → auto cancel
            elif age_hours >= PAYMENT_TIMEOUT_HOURS:
                await db.update_order_status(order["id"], "cancelled")
                try:
                    await ctx.bot.send_message(
                        chat_id=order["user_id"],
                        text=(
                            f"❌ *ORDER OTOMATIS DIBATALKAN*\n\n"
                            f"Order `{order['order_code']}` dibatalkan karena melewati batas waktu pembayaran\\."
                        ),
                        parse_mode="MarkdownV2"
                    )
                except Exception:
                    pass

        except Exception as e:
            log.warning("Error cek order %s: %s", order.get("order_code"), e)

    if reminded > 0:
        log.info("Sent %d payment reminders", reminded)


async def job_daily_report(ctx: ContextTypes.DEFAULT_TYPE):
    """Kirim laporan harian ke semua admin."""
    stats = await db.get_stats()
    text = (
        f"📊 *LAPORAN HARIAN*\n"
        f"{'─' * 30}\n"
        f"👥 Total User    : *{stats['total_users']:,}*\n"
        f"📦 Total Order   : *{stats['total_orders']:,}*\n"
        f"✅ Selesai       : *{stats['completed_orders']:,}*\n"
        f"⏳ Pending Bayar : *{stats['pending_payment']:,}*\n"
        f"💰 Revenue Hari Ini: *Rp {stats['today_revenue']:,}*\n"
        f"💵 Total Revenue : *Rp {stats['total_revenue']:,}*"
    )
    for admin_id in ADMIN_IDS:
        try:
            await ctx.bot.send_message(
                chat_id=admin_id,
                text=text,
                parse_mode="MarkdownV2"
            )
        except Exception as e:
            log.warning("Gagal kirim laporan ke admin %s: %s", admin_id, e)


def register_jobs(app):
    """Daftarkan semua job ke ApplicationBuilder's job_queue."""
    jq = app.job_queue

    # Cek order pending setiap 30 menit
    jq.run_repeating(
        job_reminder_pending_orders,
        interval=1800,   # 30 menit
        first=60         # mulai setelah 60 detik
    )

    # Laporan harian setiap jam 23:59 WIB
    import pytz
    tz = pytz.timezone(TIMEZONE)
    from datetime import time as dtime
    jq.run_daily(
        job_daily_report,
        time=dtime(hour=23, minute=59, tzinfo=tz)
    )

    log.info("✅ Scheduled jobs registered")
