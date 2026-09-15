# ============================================
# World War - SQLite → PostgreSQL Migration
# ============================================

import os
import sqlite3
import psycopg2


# ============================================
# تنظیمات
# ============================================

SQLITE_DATABASE = "world_war.db"
POSTGRES_URL = os.getenv("DATABASE_URL")


# ============================================
# بررسی DATABASE_URL
# ============================================

if not POSTGRES_URL:
    raise RuntimeError(
        "DATABASE_URL پیدا نشد.\n"
        "DATABASE_URL را در محیط اجرای migrate.py تنظیم کنید."
    )


# ============================================
# اتصال‌ها
# ============================================

sqlite_connection = sqlite3.connect(SQLITE_DATABASE)
sqlite_cursor = sqlite_connection.cursor()

postgres_connection = psycopg2.connect(POSTGRES_URL)
postgres_cursor = postgres_connection.cursor()


# ============================================
# تابع انتقال یک جدول
# ============================================

def migrate_table(table_name, columns, conflict="DO NOTHING"):

    print(f"📦 انتقال جدول: {table_name}")

    sqlite_cursor.execute(
        f"SELECT {', '.join(columns)} FROM {table_name}"
    )

    rows = sqlite_cursor.fetchall()

    if not rows:
        print(f"   └─ خالی است")
        return

    placeholders = ", ".join(["%s"] * len(columns))

    query = f"""
        INSERT INTO {table_name}
        ({', '.join(columns)})
        VALUES ({placeholders})
        ON CONFLICT {conflict}
    """

    for row in rows:
        postgres_cursor.execute(query, row)

    print(f"   └─ {len(rows)} رکورد منتقل شد")


# ============================================
# شروع مهاجرت
# ============================================

try:

    print()
    print("============================================")
    print(" World War - Database Migration")
    print(" SQLite → PostgreSQL")
    print("============================================")
    print()

    # ----------------------------------------
    # کاربران
    # ----------------------------------------

    migrate_table(
        "users",
        [
            "user_id",
            "country",
            "budget",
            "hp"
        ]
    )

    # ----------------------------------------
    # موجودی
    # ----------------------------------------

    migrate_table(
        "inventory",
        [
            "user_id",
            "item_id",
            "quantity"
        ]
    )

    # ----------------------------------------
    # وضعیت درآمد معدن
    # ----------------------------------------

    migrate_table(
        "mine_income_state",
        [
            "id",
            "last_payout_date"
        ]
    )

    # ----------------------------------------
    # اتحادها
    # ----------------------------------------

    migrate_table(
        "alliances",
        [
            "id",
            "name",
            "tag",
            "leader_id",
            "treasury",
            "status",
            "created_at"
        ]
    )

    # ----------------------------------------
    # اعضای اتحاد
    # ----------------------------------------

    migrate_table(
        "alliance_members",
        [
            "alliance_id",
            "user_id",
            "role",
            "joined_at"
        ]
    )

    # ----------------------------------------
    # تراکنش‌های اتحاد
    # ----------------------------------------

    migrate_table(
        "alliance_transactions",
        [
            "id",
            "alliance_id",
            "user_id",
            "tx_type",
            "amount",
            "item_id",
            "quantity",
            "note",
            "created_at"
        ]
    )

    # ----------------------------------------
    # انبار اتحاد
    # ----------------------------------------

    migrate_table(
        "alliance_warehouse",
        [
            "alliance_id",
            "item_id",
            "quantity"
        ]
    )

    # ----------------------------------------
    # شرکت‌های بین‌المللی
    # ----------------------------------------

    migrate_table(
        "international_companies",
        [
            "company_id",
            "owner_user_id",
            "created_at"
        ]
    )

    # ----------------------------------------
    # کارمندان شرکت
    # ----------------------------------------

    migrate_table(
        "company_employees",
        [
            "company_id",
            "user_id",
            "joined_at"
        ]
    )

    # ----------------------------------------
    # پرداخت‌های روزانه شرکت
    # ----------------------------------------

    migrate_table(
        "company_daily_payouts",
        [
            "payout_date",
            "user_id",
            "company_id",
            "role",
            "amount",
            "created_at"
        ]
    )

    # ========================================
    # اصلاح Sequence های PostgreSQL
    # ========================================
    #
    # چون IDهای قدیمی اتحادها و تراکنش‌ها
    # حفظ شده‌اند، Sequence هم باید جلو برود.
    #

    print()
    print("🔧 تنظیم Sequence ها...")

    postgres_cursor.execute("""
        SELECT setval(
            pg_get_serial_sequence('alliances', 'id'),
            COALESCE((SELECT MAX(id) FROM alliances), 1),
            true
        )
    """)

    postgres_cursor.execute("""
        SELECT setval(
            pg_get_serial_sequence('alliance_transactions', 'id'),
            COALESCE((SELECT MAX(id) FROM alliance_transactions), 1),
            true
        )
    """)

    # ========================================
    # ثبت نهایی
    # ========================================

    postgres_connection.commit()

    print()
    print("============================================")
    print("✅ Migration با موفقیت انجام شد!")
    print("============================================")
    print()

except Exception as error:

    postgres_connection.rollback()

    print()
    print("❌ خطا در Migration:")
    print(error)
    print()

    raise

finally:

    sqlite_cursor.close()
    sqlite_connection.close()

    postgres_cursor.close()
    postgres_connection.close()
