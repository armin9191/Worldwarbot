# ==============================
# World War - PostgreSQL Database
# ==============================

import os
import psycopg2
from psycopg2.extras import RealDictCursor


# =========================
# تنظیم اتصال
# =========================

DATABASE_URL = os.getenv("DATABASE_URL")


def get_connection():
    if not DATABASE_URL:
        raise RuntimeError(
            "DATABASE_URL پیدا نشد. "
            "متغیر DATABASE_URL را در Railway تنظیم کنید."
        )

    return psycopg2.connect(DATABASE_URL)


# =========================
# ساخت جداول
# =========================

def init_db():
    connection = get_connection()
    cursor = connection.cursor()

    try:

        # =========================
        # کاربران
        # =========================

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id BIGINT PRIMARY KEY,
                country TEXT,
                budget BIGINT DEFAULT 100000,
                hp INTEGER DEFAULT 100
            )
        """)

        # =========================
        # موجودی
        # =========================

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS inventory (
                user_id BIGINT NOT NULL,
                item_id TEXT NOT NULL,
                quantity BIGINT NOT NULL DEFAULT 0,
                PRIMARY KEY (user_id, item_id)
            )
        """)

        # =========================
        # وضعیت درآمد معدن
        # =========================

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS mine_income_state (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                last_payout_date TEXT
            )
        """)

        # =========================
        # اتحادها
        # =========================

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS alliances (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                tag TEXT NOT NULL,
                leader_id BIGINT NOT NULL,
                treasury BIGINT NOT NULL DEFAULT 0,
                status TEXT,
                created_at BIGINT
            )
        """)

        # =========================
        # اعضای اتحاد
        # =========================

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS alliance_members (
                alliance_id INTEGER NOT NULL,
                user_id BIGINT NOT NULL,
                role TEXT,
                joined_at BIGINT,
                PRIMARY KEY (alliance_id, user_id)
            )
        """)

        # =========================
        # تراکنش‌های اتحاد
        # =========================

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS alliance_transactions (
                id SERIAL PRIMARY KEY,
                alliance_id INTEGER NOT NULL,
                user_id BIGINT NOT NULL,
                tx_type TEXT,
                amount BIGINT,
                item_id TEXT,
                quantity BIGINT,
                note TEXT,
                created_at BIGINT
            )
        """)

        # =========================
        # انبار اتحاد
        # =========================

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS alliance_warehouse (
                alliance_id INTEGER NOT NULL,
                item_id TEXT NOT NULL,
                quantity BIGINT NOT NULL DEFAULT 0,
                PRIMARY KEY (alliance_id, item_id)
            )
        """)

        # =========================
        # شرکت‌های بین‌المللی
        # =========================

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS international_companies (
                company_id TEXT PRIMARY KEY,
                owner_user_id BIGINT,
                created_at TEXT
            )
        """)

        # =========================
        # کارمندان شرکت
        # =========================

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS company_employees (
                company_id TEXT NOT NULL,
                user_id BIGINT PRIMARY KEY,
                joined_at TEXT
            )
        """)

        # =========================
        # پرداخت‌های روزانه شرکت
        # =========================

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS company_daily_payouts (
                payout_date TEXT NOT NULL,
                user_id BIGINT NOT NULL,
                company_id TEXT NOT NULL,
                role TEXT,
                amount BIGINT,
                created_at TEXT,
                PRIMARY KEY (payout_date, user_id)
            )
        """)

        connection.commit()

    except Exception as error:
        connection.rollback()
        print(f"Database Init Error: {error}")
        raise

    finally:
        cursor.close()
        connection.close()


# =========================
# ساخت کاربر
# =========================

def create_user(user_id):
    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("""
            INSERT INTO users
            (user_id, country, budget, hp)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (user_id) DO NOTHING
        """, (
            user_id,
            None,
            200000000,
            100
        ))

        connection.commit()

    finally:
        cursor.close()
        connection.close()


# =========================
# گرفتن اطلاعات کاربر
# =========================

def get_user(user_id):
    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("""
            SELECT user_id, country, budget, hp
            FROM users
            WHERE user_id = %s
        """, (user_id,))

        user = cursor.fetchone()

    finally:
        cursor.close()
        connection.close()

    if user is None:
        return None

    return {
        "user_id": user[0],
        "country": user[1],
        "budget": user[2],
        "hp": user[3]
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
# گرفتن صاحب کشور
# =========================

def get_country_owner(country):
    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("""
            SELECT user_id
            FROM users
            WHERE country = %s
            LIMIT 1
        """, (country,))

        result = cursor.fetchone()

    finally:
        cursor.close()
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

    try:
        cursor.execute("""
            SELECT user_id
            FROM users
            WHERE country = %s
            LIMIT 1
        """, (country,))

        result = cursor.fetchone()

    finally:
        cursor.close()
        connection.close()

    if result is None:
        return True

    if user_id is not None and result[0] == user_id:
        return True

    return False


# =========================
# انتخاب کشور امن
# =========================

def set_country(user_id, country):

    connection = get_connection()
    cursor = connection.cursor()

    try:

        # قفل کردن رکورد کاربر
        cursor.execute("""
            SELECT country
            FROM users
            WHERE user_id = %s
            FOR UPDATE
        """, (user_id,))

        user = cursor.fetchone()

        if user is None:
            connection.rollback()
            return "not_found"

        current_country = user[0]

        # همین کشور
        if current_country == country:
            connection.commit()
            return "already_owned"

        # کشور دیگری دارد
        if current_country is not None:
            connection.commit()
            return "has_country"

        # بررسی کشور گرفته شده
        cursor.execute("""
            SELECT user_id
            FROM users
            WHERE country = %s
            LIMIT 1
            FOR UPDATE
        """, (country,))

        owner = cursor.fetchone()

        if owner is not None:
            connection.commit()
            return "occupied"

        # انتخاب کشور
        cursor.execute("""
            UPDATE users
            SET country = %s
            WHERE user_id = %s
            AND country IS NULL
        """, (
            country,
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
        cursor.close()
        connection.close()


# =========================
# تغییر بودجه
# =========================

def update_budget(user_id, budget):

    connection = get_connection()
    cursor = connection.cursor()

    try:

        cursor.execute("""
            UPDATE users
            SET budget = %s
            WHERE user_id = %s
        """, (budget, user_id))

        connection.commit()

    finally:
        cursor.close()
        connection.close()


# =========================
# اضافه کردن بودجه
# =========================

def add_budget(user_id, amount):

    if amount <= 0:
        return False

    connection = get_connection()
    cursor = connection.cursor()

    try:

        cursor.execute("""
            UPDATE users
            SET budget = budget + %s
            WHERE user_id = %s
        """, (amount, user_id))

        success = cursor.rowcount > 0

        connection.commit()

        return success

    finally:
        cursor.close()
        connection.close()


# =========================
# کم کردن بودجه
# =========================

def decrease_budget(user_id, amount):

    if amount <= 0:
        return False

    connection = get_connection()
    cursor = connection.cursor()

    try:

        cursor.execute("""
            UPDATE users
            SET budget = budget - %s
            WHERE user_id = %s
            AND budget >= %s
        """, (
            amount,
            user_id,
            amount
        ))

        success = cursor.rowcount > 0

        connection.commit()

        return success

    finally:
        cursor.close()
        connection.close()


# =========================
# تغییر HP
# =========================

def update_hp(user_id, hp):

    connection = get_connection()
    cursor = connection.cursor()

    try:

        cursor.execute("""
            UPDATE users
            SET hp = %s
            WHERE user_id = %s
        """, (hp, user_id))

        connection.commit()

    finally:
        cursor.close()
        connection.close()


# =========================
# اضافه کردن موجودی
# =========================

def add_inventory(user_id, item_id, quantity):

    connection = get_connection()
    cursor = connection.cursor()

    try:

        cursor.execute("""
            INSERT INTO inventory
            (user_id, item_id, quantity)
            VALUES (%s, %s, %s)

            ON CONFLICT (user_id, item_id)

            DO UPDATE SET
                quantity =
                    inventory.quantity
                    + EXCLUDED.quantity
        """, (
            user_id,
            item_id,
            quantity
        ))

        connection.commit()

    finally:
        cursor.close()
        connection.close()


# =========================
# کم کردن موجودی
# =========================

def decrease_inventory(user_id, item_id, quantity):

    if quantity <= 0:
        return False

    connection = get_connection()
    cursor = connection.cursor()

    try:

        cursor.execute("""
            UPDATE inventory
            SET quantity = quantity - %s
            WHERE user_id = %s
            AND item_id = %s
            AND quantity >= %s
        """, (
            quantity,
            user_id,
            item_id,
            quantity
        ))

        success = cursor.rowcount > 0

        cursor.execute("""
            DELETE FROM inventory
            WHERE user_id = %s
            AND quantity <= 0
        """, (user_id,))

        connection.commit()

        return success

    finally:
        cursor.close()
        connection.close()


# =========================
# تعداد یک آیتم
# =========================

def get_inventory_item(user_id, item_id):

    connection = get_connection()
    cursor = connection.cursor()

    try:

        cursor.execute("""
            SELECT quantity
            FROM inventory
            WHERE user_id = %s
            AND item_id = %s
        """, (
            user_id,
            item_id
        ))

        result = cursor.fetchone()

    finally:
        cursor.close()
        connection.close()

    if result is None:
        return 0

    return result[0]


# =========================
# کل موجودی
# =========================

def get_inventory(user_id):

    connection = get_connection()
    cursor = connection.cursor()

    try:

        cursor.execute("""
            SELECT item_id, quantity
            FROM inventory
            WHERE user_id = %s
            AND quantity > 0
            ORDER BY item_id
        """, (user_id,))

        rows = cursor.fetchall()

    finally:
        cursor.close()
        connection.close()

    inventory = {}

    for item_id, quantity in rows:
        inventory[item_id] = quantity

    return inventory


# ==============================
# کشورهای انتخاب شده
# ==============================

def get_selected_countries():

    connection = get_connection()
    cursor = connection.cursor()

    try:

        cursor.execute("""
            SELECT user_id, country
            FROM users
            WHERE country IS NOT NULL
            ORDER BY country
        """)

        rows = cursor.fetchall()

    finally:
        cursor.close()
        connection.close()

    countries = []

    for user_id, country in rows:

        countries.append({
            "user_id": user_id,
            "country": country
        })

    return countries


# ==============================
# ریست بازیکن بعد از شکست
# ==============================

def reset_player_after_defeat(user_id):

    connection = get_connection()
    cursor = connection.cursor()

    try:

        cursor.execute("""
            UPDATE users
            SET country = NULL,
                budget = 200000000,
                hp = 100
            WHERE user_id = %s
        """, (user_id,))

        cursor.execute("""
            DELETE FROM inventory
            WHERE user_id = %s
        """, (user_id,))

        connection.commit()

    finally:
        cursor.close()
        connection.close()


# =========================
# انتقال بودجه
# =========================

def transfer_budget(from_user_id, to_user_id, amount):

    if amount <= 0:
        return False

    connection = get_connection()
    cursor = connection.cursor()

    try:

        # قفل کردن فرستنده
        cursor.execute("""
            SELECT budget
            FROM users
            WHERE user_id = %s
            FOR UPDATE
        """, (from_user_id,))

        sender = cursor.fetchone()

        if sender is None:
            connection.rollback()
            return False

        if sender[0] < amount:
            connection.rollback()
            return False

        # کم کردن پول فرستنده
        cursor.execute("""
            UPDATE users
            SET budget = budget - %s
            WHERE user_id = %s
        """, (
            amount,
            from_user_id
        ))

        # اضافه کردن پول گیرنده
        cursor.execute("""
            UPDATE users
            SET budget = budget + %s
            WHERE user_id = %s
        """, (
            amount,
            to_user_id
        ))

        if cursor.rowcount == 0:
            connection.rollback()
            return False

        connection.commit()

        return True

    except Exception as error:

        connection.rollback()
        print(f"Transfer Budget Error: {error}")

        return False

    finally:
        cursor.close()
        connection.close()


# ==============================
# درآمد روزانه معادن
# ==============================

def get_last_mine_payout_date():

    connection = get_connection()
    cursor = connection.cursor()

    try:

        cursor.execute("""
            SELECT last_payout_date
            FROM mine_income_state
            WHERE id = 1
        """)

        result = cursor.fetchone()

    finally:
        cursor.close()
        connection.close()

    if result is None:
        return None

    return result[0]


# ==============================
# ثبت آخرین پرداخت معدن
# ==============================

def set_last_mine_payout_date(date):

    connection = get_connection()
    cursor = connection.cursor()

    try:

        cursor.execute("""
            INSERT INTO mine_income_state
            (id, last_payout_date)
            VALUES (1, %s)

            ON CONFLICT (id)

            DO UPDATE SET
                last_payout_date = EXCLUDED.last_payout_date
        """, (date,))

        connection.commit()

    finally:
        cursor.close()
        connection.close()


# ==============================
# پایان Database
# ==============================
