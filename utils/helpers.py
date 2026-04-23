"""
utils/helpers.py — Fungsi utilitas umum
"""
import random
import string
import pytz
from datetime import datetime
from config import TIMEZONE


def fmt_rp(amount: int) -> str:
    return f"Rp {amount:,.0f}".replace(",", ".")


def now_local() -> datetime:
    tz = pytz.timezone(TIMEZONE)
    return datetime.now(tz)


def now_str() -> str:
    return now_local().strftime("%d/%m/%Y %H:%M WIB")


def generate_code(length: int = 8) -> str:
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))


def is_admin(user_id: int) -> bool:
    from config import ADMIN_IDS
    return user_id in ADMIN_IDS


def parse_accounts_text(text: str) -> list[str]:
    """Parse baris-baris akun digital dari teks (pisah per baris)."""
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return lines


def truncate(text: str, max_len: int = 50) -> str:
    return text[:max_len] + "..." if len(text) > max_len else text
