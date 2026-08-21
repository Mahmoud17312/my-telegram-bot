import aiosqlite
from datetime import datetime
from bot.config import settings


SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    full_name TEXT,
    balance REAL DEFAULT 0,
    created_at TEXT
);

CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    emoji TEXT DEFAULT ''
);

CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_id INTEGER,
    name TEXT NOT NULL,
    description TEXT,
    price REAL NOT NULL,
    stock INTEGER DEFAULT 0,
    delivery_type TEXT DEFAULT 'manual', -- manual / text / link
    delivery_content TEXT DEFAULT '',
    active INTEGER DEFAULT 1,
    FOREIGN KEY(category_id) REFERENCES categories(id)
);

CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    product_id INTEGER,
    quantity INTEGER,
    unit_price REAL,
    total_price REAL,
    status TEXT DEFAULT 'pending', -- pending / completed / cancelled
    created_at TEXT
);

CREATE TABLE IF NOT EXISTS topups (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    method TEXT,
    order_ref TEXT,
    amount REAL,
    status TEXT DEFAULT 'pending', -- pending / approved / rejected
    created_at TEXT
);
"""


async def init_db():
    async with aiosqlite.connect(settings.db_path) as db:
        await db.executescript(SCHEMA)
        await db.commit()


# ---------- Users ----------

async def get_or_create_user(user_id: int, username: str, full_name: str):
    async with aiosqlite.connect(settings.db_path) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
        row = await cur.fetchone()
        if row:
            return dict(row)
        await db.execute(
            "INSERT INTO users (user_id, username, full_name, balance, created_at) VALUES (?,?,?,?,?)",
            (user_id, username, full_name, 0, datetime.utcnow().isoformat()),
        )
        await db.commit()
        cur = await db.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
        row = await cur.fetchone()
        return dict(row)


async def get_balance(user_id: int) -> float:
    async with aiosqlite.connect(settings.db_path) as db:
        cur = await db.execute("SELECT balance FROM users WHERE user_id=?", (user_id,))
        row = await cur.fetchone()
        return row[0] if row else 0.0


async def adjust_balance(user_id: int, delta: float):
    async with aiosqlite.connect(settings.db_path) as db:
        await db.execute(
            "UPDATE users SET balance = balance + ? WHERE user_id=?", (delta, user_id)
        )
        await db.commit()


# ---------- Categories / Products ----------

async def list_categories():
    async with aiosqlite.connect(settings.db_path) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute("SELECT * FROM categories ORDER BY id")
        return [dict(r) for r in await cur.fetchall()]


async def list_products(category_id: int | None = None):
    async with aiosqlite.connect(settings.db_path) as db:
        db.row_factory = aiosqlite.Row
        if category_id:
            cur = await db.execute(
                "SELECT * FROM products WHERE category_id=? AND active=1 ORDER BY id",
                (category_id,),
            )
        else:
            cur = await db.execute("SELECT * FROM products WHERE active=1 ORDER BY id")
        return [dict(r) for r in await cur.fetchall()]


async def get_product(product_id: int):
    async with aiosqlite.connect(settings.db_path) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute("SELECT * FROM products WHERE id=?", (product_id,))
        row = await cur.fetchone()
        return dict(row) if row else None


async def decrement_stock(product_id: int, qty: int):
    async with aiosqlite.connect(settings.db_path) as db:
        await db.execute(
            "UPDATE products SET stock = stock - ? WHERE id=?", (qty, product_id)
        )
        await db.commit()


# ---------- Orders ----------

async def create_order(user_id: int, product_id: int, quantity: int, unit_price: float):
    total = round(unit_price * quantity, 2)
    async with aiosqlite.connect(settings.db_path) as db:
        cur = await db.execute(
            """INSERT INTO orders (user_id, product_id, quantity, unit_price, total_price, status, created_at)
               VALUES (?,?,?,?,?, 'pending', ?)""",
            (user_id, product_id, quantity, unit_price, total, datetime.utcnow().isoformat()),
        )
        await db.commit()
        return cur.lastrowid


async def set_order_status(order_id: int, status: str):
    async with aiosqlite.connect(settings.db_path) as db:
        await db.execute("UPDATE orders SET status=? WHERE id=?", (status, order_id))
        await db.commit()


async def get_order(order_id: int):
    async with aiosqlite.connect(settings.db_path) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute("SELECT * FROM orders WHERE id=?", (order_id,))
        row = await cur.fetchone()
        return dict(row) if row else None


# ---------- Topups ----------

async def create_topup(user_id: int, method: str, order_ref: str, amount: float = 0):
    async with aiosqlite.connect(settings.db_path) as db:
        cur = await db.execute(
            """INSERT INTO topups (user_id, method, order_ref, amount, status, created_at)
               VALUES (?,?,?,?, 'pending', ?)""",
            (user_id, method, order_ref, amount, datetime.utcnow().isoformat()),
        )
        await db.commit()
        return cur.lastrowid


async def reject_topup(topup_id: int):
    async with aiosqlite.connect(settings.db_path) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute("SELECT * FROM topups WHERE id=?", (topup_id,))
        row = await cur.fetchone()
        if not row or row["status"] != "pending":
            return None
        await db.execute("UPDATE topups SET status='rejected' WHERE id=?", (topup_id,))
        await db.commit()
        return dict(row)


async def approve_topup(topup_id: int, amount: float):
    async with aiosqlite.connect(settings.db_path) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute("SELECT * FROM topups WHERE id=?", (topup_id,))
        row = await cur.fetchone()
        if not row or row["status"] != "pending":
            return None
        await db.execute(
            "UPDATE topups SET status='approved', amount=? WHERE id=?", (amount, topup_id)
        )
        await db.execute(
            "UPDATE users SET balance = balance + ? WHERE user_id=?", (amount, row["user_id"])
        )
        await db.commit()
        return dict(row)
