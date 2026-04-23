"""
database.py — Database layer menggunakan SQLite + aiosqlite
Dirancang untuk menampung ribuan user, produk, dan order.
"""
import os
import asyncio
import aiosqlite
import logging
from datetime import datetime
from config import DB_PATH

log = logging.getLogger(__name__)

async def _execute_fetchone(self, sql, parameters=None):
    if parameters is None: parameters = ()
    async with self.execute(sql, parameters) as cursor:
        return await cursor.fetchone()
aiosqlite.Connection.execute_fetchone = _execute_fetchone

# ══════════════════════════════════════════════════════════════
#  INISIALISASI DATABASE
# ══════════════════════════════════════════════════════════════

async def init_db():
    """Buat semua tabel jika belum ada, aktifkan WAL mode untuk performa."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    async with aiosqlite.connect(DB_PATH) as db:
        # WAL mode → lebih cepat untuk banyak concurrent read
        await db.execute("PRAGMA journal_mode=WAL")
        await db.execute("PRAGMA foreign_keys=ON")
        await db.execute("PRAGMA cache_size=10000")

        # ── USERS ──────────────────────────────────────────────
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id        INTEGER PRIMARY KEY,
                username       TEXT,
                full_name      TEXT,
                phone          TEXT,
                balance        INTEGER DEFAULT 0,
                referral_code  TEXT UNIQUE,
                referred_by    INTEGER,
                is_banned      INTEGER DEFAULT 0,
                is_reseller    INTEGER DEFAULT 0,
                total_orders   INTEGER DEFAULT 0,
                total_spent    INTEGER DEFAULT 0,
                created_at     TEXT DEFAULT (datetime('now','localtime')),
                last_active    TEXT DEFAULT (datetime('now','localtime'))
            )
        """)

        # ── CATEGORIES ─────────────────────────────────────────
        await db.execute("""
            CREATE TABLE IF NOT EXISTS categories (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                name        TEXT NOT NULL,
                emoji       TEXT DEFAULT '📦',
                description TEXT,
                is_active   INTEGER DEFAULT 1,
                order_num   INTEGER DEFAULT 0,
                created_at  TEXT DEFAULT (datetime('now','localtime'))
            )
        """)

        # ── PRODUCTS ───────────────────────────────────────────
        await db.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id                  INTEGER PRIMARY KEY AUTOINCREMENT,
                category_id         INTEGER REFERENCES categories(id) ON DELETE SET NULL,
                name                TEXT NOT NULL,
                description         TEXT,
                price               INTEGER NOT NULL,
                reseller_price      INTEGER,
                wholesale_price     INTEGER,
                wholesale_min_qty   INTEGER DEFAULT 2,
                stock               INTEGER DEFAULT 0,
                duration            TEXT,
                product_type        TEXT DEFAULT 'account',
                is_active           INTEGER DEFAULT 1,
                sold_count          INTEGER DEFAULT 0,
                created_at          TEXT DEFAULT (datetime('now','localtime'))
            )
        """)

        # ── PRODUCT ACCOUNTS (stok digital) ────────────────────
        await db.execute("""
            CREATE TABLE IF NOT EXISTS product_accounts (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id  INTEGER REFERENCES products(id) ON DELETE CASCADE,
                data        TEXT NOT NULL,
                is_used     INTEGER DEFAULT 0,
                order_id    INTEGER,
                added_at    TEXT DEFAULT (datetime('now','localtime')),
                used_at     TEXT
            )
        """)
        await db.execute("CREATE INDEX IF NOT EXISTS idx_accounts_product ON product_accounts(product_id, is_used)")

        # ── ORDERS ─────────────────────────────────────────────
        await db.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                order_code      TEXT UNIQUE,
                user_id         INTEGER REFERENCES users(user_id),
                product_id      INTEGER REFERENCES products(id),
                product_name    TEXT,
                qty             INTEGER DEFAULT 1,
                unit_price      INTEGER,
                total_price     INTEGER,
                status          TEXT DEFAULT 'pending',
                payment_proof   TEXT,
                notes           TEXT,
                result_data     TEXT,
                created_at      TEXT DEFAULT (datetime('now','localtime')),
                paid_at         TEXT,
                completed_at    TEXT,
                cancelled_at    TEXT
            )
        """)
        await db.execute("CREATE INDEX IF NOT EXISTS idx_orders_user ON orders(user_id)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_orders_code ON orders(order_code)")

        # ── BROADCASTS ─────────────────────────────────────────
        await db.execute("""
            CREATE TABLE IF NOT EXISTS broadcasts (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                message     TEXT,
                photo_id    TEXT,
                sent_by     INTEGER,
                total_sent  INTEGER DEFAULT 0,
                total_fail  INTEGER DEFAULT 0,
                created_at  TEXT DEFAULT (datetime('now','localtime'))
            )
        """)

        # ── SETTINGS ───────────────────────────────────────────
        await db.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key     TEXT PRIMARY KEY,
                value   TEXT
            )
        """)

        # ── TOPUPS ───────────────────────────────────────────
        await db.execute("""
            CREATE TABLE IF NOT EXISTS topups (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id         INTEGER REFERENCES users(user_id),
                amount          INTEGER NOT NULL,
                status          TEXT DEFAULT 'pending',
                payment_proof   TEXT,
                created_at      TEXT DEFAULT (datetime('now','localtime')),
                completed_at    TEXT
            )
        """)

        # ── REFERRALS ──────────────────────────────────────────
        await db.execute("""
            CREATE TABLE IF NOT EXISTS referrals (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                referrer_id INTEGER REFERENCES users(user_id),
                referred_id INTEGER REFERENCES users(user_id),
                bonus       INTEGER DEFAULT 0,
                created_at  TEXT DEFAULT (datetime('now','localtime'))
            )
        """)

        await db.commit()
    log.info("✅ Database initialized: %s", DB_PATH)


# ══════════════════════════════════════════════════════════════
#  USER OPERATIONS
# ══════════════════════════════════════════════════════════════

async def get_or_create_user(user_id: int, username: str = "", full_name: str = "",
                              referral_code: str = None, referred_by: int = None) -> dict:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        row = await db.execute_fetchone("SELECT * FROM users WHERE user_id=?", (user_id,))
        if row:
            await db.execute("UPDATE users SET last_active=datetime('now','localtime'), username=?, full_name=? WHERE user_id=?",
                             (username, full_name, user_id))
            await db.commit()
            return dict(row)

        import random, string
        ref_code = referral_code or ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        await db.execute("""
            INSERT INTO users (user_id, username, full_name, referral_code, referred_by)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, username, full_name, ref_code, referred_by))
        await db.commit()
        row = await db.execute_fetchone("SELECT * FROM users WHERE user_id=?", (user_id,))
        return dict(row)


async def get_user(user_id: int) -> dict | None:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        row = await db.execute_fetchone("SELECT * FROM users WHERE user_id=?", (user_id,))
        return dict(row) if row else None


async def get_user_by_referral(code: str) -> dict | None:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        row = await db.execute_fetchone("SELECT * FROM users WHERE referral_code=?", (code,))
        return dict(row) if row else None


async def get_all_users() -> list[dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute("SELECT * FROM users WHERE is_banned=0 ORDER BY created_at DESC")
        rows = await cur.fetchall()
        return [dict(r) for r in rows]


async def count_users() -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        row = await db.execute_fetchone("SELECT COUNT(*) FROM users")
        return row[0]


async def ban_user(user_id: int, ban: bool = True):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE users SET is_banned=? WHERE user_id=?", (1 if ban else 0, user_id))
        await db.commit()


async def set_reseller(user_id: int, is_reseller: bool = True):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE users SET is_reseller=? WHERE user_id=?", (1 if is_reseller else 0, user_id))
        await db.commit()


async def add_balance(user_id: int, amount: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE users SET balance=balance+? WHERE user_id=?", (amount, user_id))
        await db.commit()


async def deduct_balance(user_id: int, amount: int) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        row = await db.execute_fetchone("SELECT balance FROM users WHERE user_id=?", (user_id,))
        if not row or row["balance"] < amount:
            return False
        await db.execute("UPDATE users SET balance=balance-? WHERE user_id=?", (amount, user_id))
        await db.commit()
        return True


# ══════════════════════════════════════════════════════════════
#  CATEGORY OPERATIONS
# ══════════════════════════════════════════════════════════════

async def get_categories(active_only: bool = True) -> list[dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        q = "SELECT * FROM categories"
        if active_only:
            q += " WHERE is_active=1"
        q += " ORDER BY order_num, id"
        cur = await db.execute(q)
        rows = await cur.fetchall()
        return [dict(r) for r in rows]


async def get_category(cat_id: int) -> dict | None:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        row = await db.execute_fetchone("SELECT * FROM categories WHERE id=?", (cat_id,))
        return dict(row) if row else None


async def add_category(name: str, emoji: str = "📦", description: str = "") -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("""
            INSERT INTO categories (name, emoji, description)
            VALUES (?, ?, ?)
        """, (name, emoji, description))
        await db.commit()
        return cur.lastrowid


async def update_category(cat_id: int, name: str, emoji: str, description: str, is_active: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            UPDATE categories SET name=?, emoji=?, description=?, is_active=? WHERE id=?
        """, (name, emoji, description, is_active, cat_id))
        await db.commit()


async def delete_category(cat_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM categories WHERE id=?", (cat_id,))
        await db.commit()


# ══════════════════════════════════════════════════════════════
#  PRODUCT OPERATIONS
# ══════════════════════════════════════════════════════════════

async def get_products(category_id: int = None, active_only: bool = True) -> list[dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        conditions = []
        params = []
        if active_only:
            conditions.append("p.is_active=1")
        if category_id:
            conditions.append("p.category_id=?")
            params.append(category_id)
        q = "SELECT p.*, c.name as cat_name, c.emoji as cat_emoji FROM products p LEFT JOIN categories c ON p.category_id=c.id"
        if conditions:
            q += " WHERE " + " AND ".join(conditions)
        q += " ORDER BY p.id"
        cur = await db.execute(q, params)
        rows = await cur.fetchall()
        return [dict(r) for r in rows]


async def get_product(product_id: int) -> dict | None:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        row = await db.execute_fetchone("""
            SELECT p.*, c.name as cat_name, c.emoji as cat_emoji
            FROM products p LEFT JOIN categories c ON p.category_id=c.id
            WHERE p.id=?
        """, (product_id,))
        return dict(row) if row else None


async def add_product(category_id: int, name: str, description: str, price: int,
                       stock: int = 0, duration: str = "",
                       wholesale_price: int = None, wholesale_min_qty: int = 2,
                       reseller_price: int = None) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("""
            INSERT INTO products (category_id, name, description, price, stock, duration,
                                  wholesale_price, wholesale_min_qty, reseller_price)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (category_id, name, description, price, stock, duration,
              wholesale_price, wholesale_min_qty, reseller_price))
        await db.commit()
        return cur.lastrowid


async def update_product_stock(product_id: int, delta: int):
    """Tambah/kurangi stok produk secara atomik."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE products SET stock=MAX(0, stock+?) WHERE id=?", (delta, product_id))
        await db.commit()


async def update_product(product_id: int, **fields):
    if not fields:
        return
    set_clause = ", ".join(f"{k}=?" for k in fields.keys())
    values = list(fields.values()) + [product_id]
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(f"UPDATE products SET {set_clause} WHERE id=?", values)
        await db.commit()


async def delete_product(product_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM products WHERE id=?", (product_id,))
        await db.commit()


# ── Product Accounts (Stok Digital) ──

async def add_account(product_id: int, data: str):
    """Tambah 1 akun digital ke stok produk."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("INSERT INTO product_accounts (product_id, data) VALUES (?, ?)", (product_id, data))
        await db.execute("UPDATE products SET stock=stock+1 WHERE id=?", (product_id,))
        await db.commit()

async def clear_product_accounts(product_id: int):
    """Hapus semua stok akun untuk produk ini."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM product_accounts WHERE product_id=?", (product_id,))
        await db.execute("UPDATE products SET stock=0 WHERE id=?", (product_id,))
        await db.commit()


async def add_accounts_bulk(product_id: int, data_list: list[str]):
    """Tambah banyak akun sekaligus."""
    async with aiosqlite.connect(DB_PATH) as db:
        rows = [(product_id, d) for d in data_list if d.strip()]
        await db.executemany("INSERT INTO product_accounts (product_id, data) VALUES (?, ?)", rows)
        await db.execute("UPDATE products SET stock=stock+? WHERE id=?", (len(rows), product_id))
        await db.commit()
    return len(rows)


async def take_accounts(product_id: int, qty: int) -> list[str]:
    """Ambil sejumlah akun dari stok (FIFO), tandai sebagai terpakai."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute("""
            SELECT id, data FROM product_accounts
            WHERE product_id=? AND is_used=0
            ORDER BY id LIMIT ?
        """, (product_id, qty))
        rows = await cur.fetchall()
        if len(rows) < qty:
            return []
        ids = [r["id"] for r in rows]
        placeholders = ",".join("?" * len(ids))
        await db.execute(f"UPDATE product_accounts SET is_used=1, used_at=datetime('now','localtime') WHERE id IN ({placeholders})", ids)
        await db.execute("UPDATE products SET stock=MAX(0,stock-?), sold_count=sold_count+? WHERE id=?", (qty, qty, product_id))
        await db.commit()
        return [r["data"] for r in rows]


async def count_available_accounts(product_id: int) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        row = await db.execute_fetchone("SELECT COUNT(*) FROM product_accounts WHERE product_id=? AND is_used=0", (product_id,))
        return row[0]


# ══════════════════════════════════════════════════════════════
#  ORDER OPERATIONS
# ══════════════════════════════════════════════════════════════

async def _gen_order_code() -> str:
    import random
    from config import ORDER_ID_PREFIX
    async with aiosqlite.connect(DB_PATH) as db:
        while True:
            code = f"{ORDER_ID_PREFIX}{random.randint(100000, 999999)}"
            row = await db.execute_fetchone("SELECT 1 FROM orders WHERE order_code=?", (code,))
            if not row:
                return code


async def create_order(user_id: int, product_id: int, product_name: str,
                        qty: int, unit_price: int) -> dict:
    code = await _gen_order_code()
    total = unit_price * qty
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute("""
            INSERT INTO orders (order_code, user_id, product_id, product_name, qty, unit_price, total_price, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, 'waiting_payment')
        """, (code, user_id, product_id, product_name, qty, unit_price, total))
        await db.commit()
        row = await db.execute_fetchone("SELECT * FROM orders WHERE id=?", (cur.lastrowid,))
        return dict(row)


async def get_order(order_id: int) -> dict | None:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        row = await db.execute_fetchone("SELECT * FROM orders WHERE id=?", (order_id,))
        return dict(row) if row else None


async def get_order_by_code(code: str) -> dict | None:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        row = await db.execute_fetchone("SELECT * FROM orders WHERE order_code=?", (code,))
        return dict(row) if row else None


async def get_user_orders(user_id: int, limit: int = 20, offset: int = 0) -> list[dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute("""
            SELECT o.*, p.name as prod_name FROM orders o
            LEFT JOIN products p ON o.product_id=p.id
            WHERE o.user_id=? ORDER BY o.created_at DESC LIMIT ? OFFSET ?
        """, (user_id, limit, offset))
        rows = await cur.fetchall()
        return [dict(r) for r in rows]


async def get_orders_by_status(status: str, limit: int = 50) -> list[dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute("""
            SELECT o.*, u.username, u.full_name FROM orders o
            LEFT JOIN users u ON o.user_id=u.user_id
            WHERE o.status=? ORDER BY o.created_at DESC LIMIT ?
        """, (status, limit))
        rows = await cur.fetchall()
        return [dict(r) for r in rows]


async def update_order_status(order_id: int, status: str, **extra):
    fields = {"status": status}
    if status == "paid":
        fields["paid_at"] = "datetime('now','localtime')"
    if status in ("completed",):
        fields["completed_at"] = "datetime('now','localtime')"
    if status in ("cancelled", "rejected"):
        fields["cancelled_at"] = "datetime('now','localtime')"
    fields.update(extra)

    # Build query manually to handle raw SQL expressions
    literal_fields = {k: v for k, v in fields.items() if not isinstance(v, str) or "datetime" not in v}
    raw_fields = {k: v for k, v in fields.items() if isinstance(v, str) and "datetime" in v}

    set_parts = [f"{k}=?" for k in literal_fields.keys()]
    set_raw = [f"{k}={v}" for k, v in raw_fields.items()]
    all_parts = set_parts + set_raw
    values = list(literal_fields.values()) + [order_id]

    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(f"UPDATE orders SET {', '.join(all_parts)} WHERE id=?", values)
        await db.commit()


async def set_payment_proof(order_id: int, file_id: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE orders SET payment_proof=?, status='paid' WHERE id=?", (file_id, order_id))
        await db.commit()


async def complete_order(order_id: int, result_data: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            UPDATE orders SET status='completed', result_data=?,
            completed_at=datetime('now','localtime') WHERE id=?
        """, (result_data, order_id))
        await db.commit()


async def get_stats() -> dict:
    async with aiosqlite.connect(DB_PATH) as db:
        total_users = (await db.execute_fetchone("SELECT COUNT(*) FROM users"))[0]
        total_orders = (await db.execute_fetchone("SELECT COUNT(*) FROM orders"))[0]
        
        # Ambil total pemasukan & total item terjual
        completed = (await db.execute_fetchone("SELECT COUNT(*), COALESCE(SUM(total_price),0), COALESCE(SUM(qty),0) FROM orders WHERE status='completed'"))
        
        pending_pay = (await db.execute_fetchone("SELECT COUNT(*) FROM orders WHERE status='paid'"))[0]
        today_rev = (await db.execute_fetchone(
            "SELECT COALESCE(SUM(total_price),0) FROM orders WHERE status='completed' AND date(completed_at)=date('now','localtime')"
        ))[0]
    return {
        "total_users": total_users,
        "total_orders": total_orders,
        "completed_orders": completed[0],
        "total_revenue": completed[1],
        "total_sold_items": completed[2],
        "pending_payment": pending_pay,
        "today_revenue": today_rev,
    }

# ══════════════════════════════════════════════════════════════
#  TOPUP OPERATIONS
# ══════════════════════════════════════════════════════════════

async def create_topup(user_id: int, amount: int, proof_file_id: str) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("""
            INSERT INTO topups (user_id, amount, payment_proof, status)
            VALUES (?, ?, ?, 'pending')
        """, (user_id, amount, proof_file_id))
        await db.commit()
        return cur.lastrowid

async def get_topup(topup_id: int) -> dict | None:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        row = await db.execute_fetchone("SELECT * FROM topups WHERE id=?", (topup_id,))
        return dict(row) if row else None

async def update_topup_status(topup_id: int, status: str):
    async with aiosqlite.connect(DB_PATH) as db:
        if status == 'completed':
            await db.execute("UPDATE topups SET status=?, completed_at=datetime('now','localtime') WHERE id=?", (status, topup_id))
        else:
            await db.execute("UPDATE topups SET status=? WHERE id=?", (status, topup_id))
        await db.commit()

async def get_pending_topups() -> list[dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute("""
            SELECT t.*, u.username, u.full_name FROM topups t
            LEFT JOIN users u ON t.user_id=u.user_id
            WHERE t.status='pending' ORDER BY t.created_at ASC
        """)
        rows = await cur.fetchall()
        return [dict(r) for r in rows]


# ══════════════════════════════════════════════════════════════
#  SETTINGS
# ══════════════════════════════════════════════════════════════

async def get_setting(key: str, default: str = "") -> str:
    async with aiosqlite.connect(DB_PATH) as db:
        row = await db.execute_fetchone("SELECT value FROM settings WHERE key=?", (key,))
        return row[0] if row else default


async def set_setting(key: str, value: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, value))
        await db.commit()
