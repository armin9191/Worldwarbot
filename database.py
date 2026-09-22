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

    # اضافه کردن ستون زمان انتخاب کشور
    try:
        cursor.execute(
            "ALTER TABLE users ADD COLUMN country_selected_at INTEGER"
        )
    except:
        pass

    # اضافه کردن username
    try:
        cursor.execute(
            "ALTER TABLE users ADD COLUMN username TEXT"
        )
    except:
        pass

    # اضافه کردن زمان اولین ورود کاربر
    try:
        cursor.execute(
            "ALTER TABLE users ADD COLUMN created_at INTEGER"
        )
    except:
        pass

    # اضافه کردن زمان آخرین فعالیت کاربر
    try:
        cursor.execute(
            "ALTER TABLE users ADD COLUMN last_active_at INTEGER"
        )
    except:
        pass

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

    # =========================================
    # جدول کاربران بن شده
    # =========================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS banned_users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            reason TEXT NOT NULL,
            banned_at INTEGER NOT NULL,
            banned_by INTEGER
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

    now = int(time.time())

    cursor.execute("""
        INSERT OR IGNORE INTO users
        (user_id, country, budget, hp, created_at, last_active_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        user_id,
        None,
        200000000,
        100,
        now,
        now
    ))

    connection.commit()
    connection.close()


# =========================
# دریافت کاربر
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
# دریافت یا ساخت کاربر
# =========================

def get_or_create_user(user_id):
    user = get_user(user_id)

    if user is None:
        create_user(user_id)
        user = get_user(user_id)

    return user


# =========================
# ثبت فعالیت کاربر
# =========================

def update_last_active(user_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE users
        SET last_active_at = ?
        WHERE user_id = ?
    """, (
        int(time.time()),
        user_id
    ))

    connection.commit()
    connection.close()


# =========================
# ذخیره Username
# =========================

def update_username(user_id, username):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE users
        SET username = ?
        WHERE user_id = ?
    """, (
        username,
        user_id
    ))

    connection.commit()
    connection.close()


# =========================
# دریافت Username
# =========================

def get_username(user_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT username
        FROM users
        WHERE user_id = ?
    """, (user_id,))

    result = cursor.fetchone()

    connection.close()

    if result is None:
        return None

    return result[0]


# =========================
# آمار کاربران
# =========================

def get_bot_stats():

    now = int(time.time())

    today_start = now - 86400
    seven_days_start = now - (7 * 86400)
    thirty_days_start = now - (30 * 86400)
    twenty_four_hours_start = now - 86400

    connection = get_connection()
    cursor = connection.cursor()

    # کل کاربران
    cursor.execute("""
        SELECT COUNT(*)
        FROM users
    """)

    total_users = cursor.fetchone()[0]

    # کاربران ثبت شده در 24 ساعت اخیر
    cursor.execute("""
        SELECT COUNT(*)
        FROM users
        WHERE created_at IS NOT NULL
        AND created_at >= ?
    """, (today_start,))

    users_today = cursor.fetchone()[0]

    # کاربران ثبت شده در 7 روز اخیر
    cursor.execute("""
        SELECT COUNT(*)
        FROM users
        WHERE created_at IS NOT NULL
        AND created_at >= ?
    """, (seven_days_start,))

    users_7_days = cursor.fetchone()[0]

    # کاربران ثبت شده در 30 روز اخیر
    cursor.execute("""
        SELECT COUNT(*)
        FROM users
        WHERE created_at IS NOT NULL
        AND created_at >= ?
    """, (thirty_days_start,))

    users_30_days = cursor.fetchone()[0]

    # کاربران دارای کشور
    cursor.execute("""
        SELECT COUNT(*)
        FROM users
        WHERE country IS NOT NULL
    """)

    selected_countries = cursor.fetchone()[0]

    # کاربران بدون کشور
    cursor.execute("""
        SELECT COUNT(*)
        FROM users
        WHERE country IS NULL
    """)

    users_without_country = cursor.fetchone()[0]

    # کشورهایی که در 24 ساعت اخیر انتخاب شده‌اند
    cursor.execute("""
        SELECT COUNT(*)
        FROM users
        WHERE country IS NOT NULL
        AND country_selected_at IS NOT NULL
        AND country_selected_at >= ?
    """, (twenty_four_hours_start,))

    countries_selected_24h = cursor.fetchone()[0]

    # کاربران فعال امروز
    cursor.execute("""
        SELECT COUNT(*)
        FROM users
        WHERE last_active_at IS NOT NULL
        AND last_active_at >= ?
    """, (today_start,))

    active_today = cursor.fetchone()[0]

    # کاربران فعال در 7 روز گذشته
    cursor.execute("""
        SELECT COUNT(*)
        FROM users
        WHERE last_active_at IS NOT NULL
        AND last_active_at >= ?
    """, (seven_days_start,))

    active_7_days = cursor.fetchone()[0]

    connection.close()

    return {
        "total_users": total_users,
        "users_today": users_today,
        "users_7_days": users_7_days,
        "users_30_days": users_30_days,
        "selected_countries": selected_countries,
        "users_without_country": users_without_country,
        "countries_selected_24h": countries_selected_24h,
        "active_today": active_today,
        "active_7_days": active_7_days
    }


# =========================
# بررسی بن بودن کاربر
# =========================

def get_ban_info(user_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT user_id, username, reason, banned_at, banned_by
        FROM banned_users
        WHERE user_id = ?
        LIMIT 1
    """, (user_id,))

    result = cursor.fetchone()

    connection.close()

    if result is None:
        return None

    return {
        "user_id": result[0],
        "username": result[1],
        "reason": result[2],
        "banned_at": result[3],
        "banned_by": result[4]
    }


def is_user_banned(user_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT 1
        FROM banned_users
        WHERE user_id = ?
        LIMIT 1
    """, (user_id,))

    result = cursor.fetchone()

    connection.close()

    return result is not None


# =========================
# بن کردن + حذف کشور
# =========================

def ban_user_and_reset(
    user_id,
    reason,
    username=None,
    banned_by=None
):

    connection = get_connection()
    cursor = connection.cursor()

    try:

        cursor.execute("BEGIN IMMEDIATE")

        # بررسی وجود کاربر
        cursor.execute("""
            SELECT country
            FROM users
            WHERE user_id = ?
        """, (user_id,))

        user = cursor.fetchone()

        if user is None:
            connection.rollback()
            return "not_found"

        # اگر username جدید داریم ذخیره شود
        if username is not None:
            cursor.execute("""
                UPDATE users
                SET username = ?
                WHERE user_id = ?
            """, (
                username,
                user_id
            ))

        # ثبت بن
        cursor.execute("""
            INSERT INTO banned_users
            (
                user_id,
                username,
                reason,
                banned_at,
                banned_by
            )
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(user_id)
            DO UPDATE SET
                username = excluded.username,
                reason = excluded.reason,
                banned_at = excluded.banned_at,
                banned_by = excluded.banned_by
        """, (
            user_id,
            username,
            reason,
            int(time.time()),
            banned_by
        ))

        # حذف کشور و ریست اطلاعات
        cursor.execute("""
            UPDATE users
            SET country = NULL,
                budget = 200000000,
                hp = 100,
                country_selected_at = NULL
            WHERE user_id = ?
        """, (user_id,))

        # حذف موجودی
        cursor.execute("""
            DELETE FROM inventory
            WHERE user_id = ?
        """, (user_id,))

        connection.commit()

        return "success"

    except Exception as error:

        connection.rollback()

        print(
            f"Ban User Error: {error}"
        )

        return "error"

    finally:
        connection.close()


# =========================
# آنبن کردن کاربر
# =========================

def unban_user(user_id):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        DELETE FROM banned_users
        WHERE user_id = ?
    """, (user_id,))

    success = cursor.rowcount > 0

    connection.commit()
    connection.close()

    return success


# =========================
# لیست کاربران بن شده
# =========================

def get_banned_users():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT user_id, username, reason, banned_at, banned_by
        FROM banned_users
        ORDER BY banned_at DESC
    """)

    rows = cursor.fetchall()

    connection.close()

    users = []

    for user_id, username, reason, banned_at, banned_by in rows:

        users.append({
            "user_id": user_id,
            "username": username,
            "reason": reason,
            "banned_at": banned_at,
            "banned_by": banned_by
        })

    return users


# =========================
# دریافت صاحب کشور
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

    if user_id is not None and result[0] == user_id:
        return True

    return False


# =========================
# انتخاب کشور
# =========================

def set_country(user_id, country):
    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("BEGIN IMMEDIATE")

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

        if current_country == country:
            connection.commit()
            return "already_owned"

        if current_country is not None:
            connection.commit()
            return "has_country"

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
# بروزرسانی بودجه
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
# افزایش بودجه
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
# کاهش بودجه
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
# بروزرسانی HP
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
# افزودن موجودی
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
# کاهش موجودی
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
# دریافت یک آیتم
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
# دریافت کل موجودی
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


# =========================
# کشورهای انتخاب شده
# =========================

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


# =========================
# ریست بازیکن بعد از شکست
# =========================

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


# =========================
# آخرین درآمد معدن
# =========================

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


# =========================
# ثبت آخرین درآمد معدن
# =========================

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
