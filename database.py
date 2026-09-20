# ==============================
# World War - Database
# ==============================

import os
import sqlite3
import time

from config import DATABASE_NAME


# =========================
# اتصال به دیتابیس
# =========================

def get_connection():
    # ساخت پوشه اگر وجود نداشت (مهم برای Railway)
    db_dir = os.path.dirname(DATABASE_NAME)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)

    return sqlite3.connect(DATABASE_NAME)


# =========================
# ساخت جداول
# =========================

def init_db():
    connection = get_connection()
    cursor = connection.cursor()

    # جدول کاربران
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            country TEXT,
            budget INTEGER DEFAULT 100000,
            hp INTEGER DEFAULT 100
        )
    """)

    # اضافه کردن ستون زمان انتخاب کشور (اگر وجود نداشت)
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN country_selected_at INTEGER")
    except:
        pass  # ستون از قبل وجود دارد

    # جدول موجودی
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS inventory (
            user_id INTEGER NOT NULL,
            item_id TEXT NOT NULL,
            quantity INTEGER NOT NULL DEFAULT 0,
            PRIMARY KEY (user_id, item_id)
        )
    """)

    # جدول ثبت آخرین واریز درآمد معادن
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS mine_income_state (
            id INTEGER PRIMARY KEY CHECK(id = 1),
            last_payout_date TEXT
        )
    """)

    connection.commit()
    connection.close()


# =========================
# ساخت کاربر
# =========================

def create_user(user_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT OR IGNORE INTO users
        (user_id, country, budget, hp)
        VALUES (?, ?, ?, ?)
    """, (
        user_id,
        None,
        200000000,
        100
    ))

    connection.commit()
    connection.close()


# =========================
# گرفتن اطلاعات کاربر
# =========================

def get_user(user_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT user_id, country, budget, hp, country_selected_at
        FROM users
        WHERE user_id = ?
    """, (user_id,))

    user = cursor.fetchone()

    connection.close()

    if user is None:
        return None

    return {
        "user_id": user[0],
        "country": user[1],
        "budget": user[2],
        "hp": user[3],
        "country_selected_at": user[4]
    }


# =========================
# گرفتن یا ساخت کاربر
# =========================

def get_or_create_user(user_id):
    user = get_user(user_id)

    if user is None:
        create_user(user_id)
        user = get_user(user_id)

    return user


# =========================
# گرفتن صاحب یک کشور
# =========================

def get_country_owner(country):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT user_id
        FROM users
        WHERE country = ?
        LIMIT 1
    """, (country,))

    result = cursor.fetchone()

    connection.close()

    if result is None:
        return None

    return result[0]


# =========================
# بررسی آزاد بودن کشور
# =========================

def is_country_available(country, user_id=None):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT user_id
        FROM users
        WHERE country = ?
        LIMIT 1
    """, (country,))

    result = cursor.fetchone()

    connection.close()

    if result is None:
        return True

    # اگر صاحب کشور خود همین کاربر باشد
    if user_id is not None and result[0] == user_id:
        return True

    return False


# =========================
# انتخاب کشور امن
# =========================

def set_country(user_id, country):
    """
    انتخاب کشور به صورت امن.

    خروجی:
    success        = انتخاب موفق
    occupied       = کشور قبلاً گرفته شده
    already_owned  = همین کاربر قبلاً همین کشور را دارد
    has_country    = کاربر از قبل کشور دیگری دارد
    not_found      = کاربر وجود ندارد
    """

    connection = get_connection()
    cursor = connection.cursor()

    try:
        # جلوگیری از تداخل همزمان
        cursor.execute("BEGIN IMMEDIATE")

        # بررسی کاربر
        cursor.execute("""
            SELECT country
            FROM users
            WHERE user_id = ?
        """, (user_id,))

        user = cursor.fetchone()

        if user is None:
            connection.rollback()
            return "not_found"

        current_country = user[0]

        # اگر همین کشور را دارد
        if current_country == country:
            connection.commit()
            return "already_owned"

        # اگر از قبل کشور دیگری دارد
        if current_country is not None:
            connection.commit()
            return "has_country"

        # بررسی اینکه کشور قبلاً گرفته شده یا نه
        cursor.execute("""
            SELECT user_id
            FROM users
            WHERE country = ?
            LIMIT 1
        """, (country,))

        owner = cursor.fetchone()

        if owner is not None:
            connection.commit()
            return "occupied"

        # انتخاب کشور + ثبت زمان تأسیس
        cursor.execute("""
            UPDATE users
            SET country = ?, country_selected_at = ?
            WHERE user_id = ?
            AND country IS NULL
        """, (
            country,
            int(time.time()),
            user_id
        ))

        if cursor.rowcount == 0:
            connection.commit()
            return "has_country"

        connection.commit()
        return "success"

    except Exception as error:
        connection.rollback()
        print(f"Set Country Error: {error}")
        return "error"

    finally:
        connection.close()


# =========================
# تغییر بودجه
# =========================

def update_budget(user_id, budget):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE users
        SET budget = ?
        WHERE user_id = ?
    """, (budget, user_id))

    connection.commit()
    connection.close()


# =========================
# اضافه کردن بودجه
# =========================

def add_budget(user_id, amount):
    if amount <= 0:
        return False

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE users
        SET budget = budget + ?
        WHERE user_id = ?
    """, (amount, user_id))

    success = cursor.rowcount > 0

    connection.commit()
    connection.close()

    return success


# =========================
# کم کردن بودجه
# =========================

def decrease_budget(user_id, amount):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE users
        SET budget = budget - ?
        WHERE user_id = ?
        AND budget >= ?
    """, (
        amount,
        user_id,
        amount
    ))

    success = cursor.rowcount > 0

    connection.commit()
    connection.close()

    return success


# =========================
# تغییر HP
# =========================

def update_hp(user_id, hp):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE users
        SET hp = ?
        WHERE user_id = ?
    """, (hp, user_id))

    connection.commit()
    connection.close()


# =========================
# اضافه کردن به موجودی
# =========================

def add_inventory(user_id, item_id, quantity):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO inventory
        (user_id, item_id, quantity)
        VALUES (?, ?, ?)
        ON CONFLICT(user_id, item_id)
        DO UPDATE SET
            quantity = quantity + excluded.quantity
    """, (
        user_id,
        item_id,
        quantity
    ))

    connection.commit()
    connection.close()


# =========================
# کم کردن از موجودی
# =========================

def decrease_inventory(user_id, item_id, quantity):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE inventory
        SET quantity = quantity - ?
        WHERE user_id = ?
        AND item_id = ?
        AND quantity >= ?
    """, (
        quantity,
        user_id,
        item_id,
        quantity
    ))

    success = cursor.rowcount > 0

    cursor.execute("""
        DELETE FROM inventory
        WHERE user_id = ?
        AND quantity <= 0
    """, (user_id,))

    connection.commit()
    connection.close()

    return success


# =========================
# گرفتن تعداد یک آیتم
# =========================

def get_inventory_item(user_id, item_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT quantity
        FROM inventory
        WHERE user_id = ?
        AND item_id = ?
    """, (
        user_id,
        item_id
    ))

    result = cursor.fetchone()

    connection.close()

    if result is None:
        return 0

    return result[0]


# =========================
# گرفتن کل موجودی کاربر
# =========================

def get_inventory(user_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT item_id, quantity
        FROM inventory
        WHERE user_id = ?
        AND quantity > 0
        ORDER BY item_id
    """, (user_id,))

    rows = cursor.fetchall()

    connection.close()

    inventory = {}

    for item_id, quantity in rows:
        inventory[item_id] = quantity

    return inventory


# ==============================
# کشورهای انتخاب شده توسط بازیکنان
# ==============================

def get_selected_countries():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT user_id, country, country_selected_at
        FROM users
        WHERE country IS NOT NULL
        ORDER BY country
    """)

    rows = cursor.fetchall()

    connection.close()

    countries = []

    for user_id, country, selected_at in rows:
        countries.append({
            "user_id": user_id,
            "country": country,
            "country_selected_at": selected_at
        })

    return countries


# ==============================
# ریست کامل بازیکن بعد از نابودی کشور
# ==============================

def reset_player_after_defeat(user_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE users
        SET country = NULL,
            budget = 200000000,
            hp = 100,
            country_selected_at = NULL
        WHERE user_id = ?
    """, (user_id,))

    cursor.execute("""
        DELETE FROM inventory
        WHERE user_id = ?
    """, (user_id,))

    connection.commit()
    connection.close()


# =========================
# انتقال بودجه
# =========================

def transfer_budget(from_user_id, to_user_id, amount):
    if amount <= 0:
        return False

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE users
        SET budget = budget - ?
        WHERE user_id = ?
        AND budget >= ?
    """, (amount, from_user_id, amount))

    if cursor.rowcount == 0:
        connection.rollback()
        connection.close()
        return False

    cursor.execute("""
        UPDATE users
        SET budget = budget + ?
        WHERE user_id = ?
    """, (amount, to_user_id))

    if cursor.rowcount == 0:
        connection.rollback()
        connection.close()
        return False

    connection.commit()
    connection.close()
    return True


# ==============================
# درآمد روزانه معادن
# ==============================

def get_last_mine_payout_date():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT last_payout_date
        FROM mine_income_state
        WHERE id = 1
    """)

    result = cursor.fetchone()
    connection.close()

    if result is None:
        return None

    return result[0]


def set_last_mine_payout_date(date):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO mine_income_state
        (id, last_payout_date)
        VALUES (1, ?)
        ON CONFLICT(id)
        DO UPDATE SET
            last_payout_date = excluded.last_payout_date
    """, (date,))

    connection.commit()
    connection.close()
