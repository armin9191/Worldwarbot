# ==============================
# World War - International Companies
# Standalone Company System
# ==============================

import sqlite3
from datetime import datetime
from zoneinfo import ZoneInfo

import database


# ==============================
# Company Data
# ==============================

COMPANIES = {
    "oil": {
        "name": "🛢️ نفت پارس",
        "price": 1_800_000_000_000,
        "base_profit": 180_000_000_000,
        "capacity": 5,
        "owner_employee_profit": 30_000_000_000,
        "employee_income": 8_000_000_000,
    },

    "mines": {
        "name": "⛏️ معادن جهانی",
        "price": 2_400_000_000_000,
        "base_profit": 220_000_000_000,
        "capacity": 6,
        "owner_employee_profit": 32_000_000_000,
        "employee_income": 10_000_000_000,
    },

    "auto": {
        "name": "🚗 خودروسازی جهانی",
        "price": 3_200_000_000_000,
        "base_profit": 280_000_000_000,
        "capacity": 7,
        "owner_employee_profit": 35_000_000_000,
        "employee_income": 12_000_000_000,
    },

    "energy": {
        "name": "⚡ انرژی جهانی",
        "price": 4_500_000_000_000,
        "base_profit": 350_000_000_000,
        "capacity": 8,
        "owner_employee_profit": 40_000_000_000,
        "employee_income": 14_000_000_000,
    },

    "technology": {
        "name": "💻 فناوری جهانی",
        "price": 6_000_000_000_000,
        "base_profit": 450_000_000_000,
        "capacity": 9,
        "owner_employee_profit": 45_000_000_000,
        "employee_income": 16_000_000_000,
    },

    "bank": {
        "name": "🏦 بانک جهانی",
        "price": 8_000_000_000_000,
        "base_profit": 600_000_000_000,
        "capacity": 10,
        "owner_employee_profit": 50_000_000_000,
        "employee_income": 20_000_000_000,
    },
}


# ==============================
# Bot Connection
# ==============================

send_message = None
edit_message = None


def setup(send_message_function, edit_message_function):

    global send_message
    global edit_message

    send_message = send_message_function
    edit_message = edit_message_function

    init_company_tables()


# ==============================
# Database
# ==============================

def init_company_tables():

    conn = database.get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS international_companies (
            company_id TEXT PRIMARY KEY,
            owner_user_id INTEGER,
            created_at TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS company_employees (
            company_id TEXT NOT NULL,
            user_id INTEGER PRIMARY KEY,
            joined_at TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS company_daily_payouts (
            payout_date TEXT NOT NULL,
            user_id INTEGER NOT NULL,
            company_id TEXT NOT NULL,
            role TEXT NOT NULL,
            amount INTEGER NOT NULL,
            created_at TEXT NOT NULL,
            PRIMARY KEY (payout_date, user_id)
        )
    """)

    now = datetime.now().isoformat()

    for company_id in COMPANIES:

        cursor.execute(
            """
            INSERT OR IGNORE INTO international_companies
            (company_id, owner_user_id, created_at)
            VALUES (?, NULL, ?)
            """,
            (company_id, now)
        )

    conn.commit()
    conn.close()


# ==============================
# Helpers
# ==============================

def money(value):
    return f"{int(value):,}$"


def get_iran_time():
    return datetime.now(ZoneInfo("Asia/Tehran"))


def today_iran():
    return get_iran_time().strftime("%Y-%m-%d")


def keyboard(rows):
    return {
        "inline_keyboard": rows
    }


def button(text, callback_data):
    return {
        "text": text,
        "callback_data": callback_data
    }


def back_button():
    return [
        button(
            "🔙 بازگشت",
            "international_companies"
        )
    ]


def safe_edit(
    chat_id,
    message_id,
    text,
    reply_markup=None
):

    if edit_message is None:
        return False

    try:

        edit_message(
            chat_id,
            message_id,
            text,
            reply_markup
        )

        return True

    except TypeError:

        try:

            edit_message(
                chat_id,
                message_id,
                text
            )

            return True

        except Exception:

            return False

    except Exception:

        return False


def safe_send(
    chat_id,
    text,
    reply_markup=None
):

    if send_message is None:
        return False

    try:

        send_message(
            chat_id,
            text,
            reply_markup
        )

        return True

    except TypeError:

        try:

            send_message(
                chat_id,
                text
            )

            return True

        except Exception:

            return False

    except Exception:

        return False


def show_page(
    chat_id,
    message_id,
    text,
    reply_markup=None
):

    if message_id is not None:

        if safe_edit(
            chat_id,
            message_id,
            text,
            reply_markup
        ):

            return

    safe_send(
        chat_id,
        text,
        reply_markup
    )


# ==============================
# Database Read
# ==============================

def get_company(company_id):

    return COMPANIES.get(company_id)


def get_owner(company_id):

    conn = database.get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT owner_user_id
        FROM international_companies
        WHERE company_id = ?
        """,
        (company_id,)
    )

    row = cursor.fetchone()

    conn.close()

    return row[0] if row else None


def get_employee_count(company_id):

    conn = database.get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM company_employees
        WHERE company_id = ?
        """,
        (company_id,)
    )

    count = cursor.fetchone()[0]

    conn.close()

    return count


def get_employee_company(user_id):

    conn = database.get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT company_id
        FROM company_employees
        WHERE user_id = ?
        """,
        (user_id,)
    )

    row = cursor.fetchone()

    conn.close()

    return row[0] if row else None


def is_owner(user_id, company_id):

    return get_owner(company_id) == user_id


def is_employee(user_id, company_id):

    conn = database.get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT 1
        FROM company_employees
        WHERE company_id = ?
        AND user_id = ?
        """,
        (company_id, user_id)
    )

    result = cursor.fetchone() is not None

    conn.close()

    return result


def get_user_country(user_id):

    conn = database.get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT country
        FROM users
        WHERE user_id = ?
        """,
        (user_id,)
    )

    row = cursor.fetchone()

    conn.close()

    return row[0] if row and row[0] else "نامشخص"


# ==============================
# Companies Menu
# ==============================

def show_companies(
    chat_id,
    message_id=None
):

    rows = []

    for company_id, company in COMPANIES.items():

        owner = get_owner(company_id)

        if owner is None:

            status = "🟢 آماده خرید"

        else:

            status = "🔴 دارای مالک"

        rows.append([
            button(
                company["name"],
                f"company_view_{company_id}"
            )
        ])

    rows.append([
        button(
            "🔙 بازگشت",
            "back_main_menu"
        )
    ])

    text = (
        "🌐 شرکت‌های بین‌المللی\n\n"
        "شرکت موردنظر خود را انتخاب کنید:"
    )

    show_page(
        chat_id,
        message_id,
        text,
        keyboard(rows)
    )


# ==============================
# Company Details
# ==============================

def show_company(
    chat_id,
    message_id,
    user_id,
    company_id
):

    company = get_company(company_id)

    if not company:

        show_companies(
            chat_id,
            message_id
        )

        return

    owner_id = get_owner(company_id)

    employee_count = get_employee_count(
        company_id
    )

    if owner_id is None:

        owner_text = "❌ بدون مالک"

    else:

        owner_text = (
            f"🌍 {get_user_country(owner_id)}"
        )

    owner_daily_profit = (
        company["base_profit"]
        +
        employee_count
        *
        company["owner_employee_profit"]
    )

    text = (
        f"🏢 {company['name']}\n\n"

        f"💰 قیمت خرید: "
        f"{money(company['price'])}\n"

        f"👑 مالک: {owner_text}\n\n"

        f"💵 سود پایه روزانه: "
        f"{money(company['base_profit'])}\n"

        f"👥 کارکنان: "
        f"{employee_count}/{company['capacity']}\n"

        f"💰 سود مالک از هر کارمند: "
        f"{money(company['owner_employee_profit'])}\n"

        f"💵 درآمد هر کارمند: "
        f"{money(company['employee_income'])}\n\n"

        f"📈 سود روزانه فعلی مالک: "
        f"{money(owner_daily_profit)}"
    )

    rows = []

    if owner_id is None:

        rows.append([
            button(
                "💰 خرید شرکت",
                f"company_buy_{company_id}"
            )
        ])

    elif owner_id == user_id:

        rows.append([
            button(
                "💰 فروش شرکت",
                f"company_sell_{company_id}"
            )
        ])

    elif is_employee(
        user_id,
        company_id
    ):

        rows.append([
            button(
                "🚪 ترک شرکت",
                f"company_leave_{company_id}"
            )
        ])

    else:

        current_company = get_employee_company(
            user_id
        )

        if current_company is None:

            if employee_count < company["capacity"]:

                rows.append([
                    button(
                        "👷 استخدام شدن",
                        f"company_join_{company_id}"
                    )
                ])

        else:

            other_company = COMPANIES.get(
                current_company
            )

            if other_company:

                text += (
                    "\n\n⚠️ تو در حال حاضر "
                    f"کارمند {other_company['name']} هستی."
                )

    rows.append(
        back_button()
    )

    show_page(
        chat_id,
        message_id,
        text,
        keyboard(rows)
    )


# ==============================
# Buy Company
# ==============================

def buy_company(
    chat_id,
    message_id,
    user_id,
    company_id
):

    company = get_company(company_id)

    if not company:

        show_companies(
            chat_id,
            message_id
        )

        return

    conn = database.get_connection()
    cursor = conn.cursor()

    try:

        cursor.execute(
            "BEGIN IMMEDIATE"
        )

        cursor.execute(
            """
            SELECT owner_user_id
            FROM international_companies
            WHERE company_id = ?
            """,
            (company_id,)
        )

        row = cursor.fetchone()

        if not row or row[0] is not None:

            conn.rollback()

            show_company(
                chat_id,
                message_id,
                user_id,
                company_id
            )

            return

        cursor.execute(
            """
            SELECT budget
            FROM users
            WHERE user_id = ?
            """,
            (user_id,)
        )

        user = cursor.fetchone()

        if not user:

            conn.rollback()

            show_page(
                chat_id,
                message_id,
                "❌ اطلاعات کاربر پیدا نشد.",
                keyboard([
                    back_button()
                ])
            )

            return

        budget = int(user[0])

        if budget < company["price"]:

            conn.rollback()

            show_page(
                chat_id,
                message_id,
                (
                    "❌ موجودی کافی نیست.\n\n"
                    f"💰 قیمت: "
                    f"{money(company['price'])}\n"
                    f"💳 موجودی: "
                    f"{money(budget)}"
                ),
                keyboard([
                    back_button()
                ])
            )

            return

        cursor.execute(
            """
            UPDATE users
            SET budget = budget - ?
            WHERE user_id = ?
            AND budget >= ?
            """,
            (
                company["price"],
                user_id,
                company["price"]
            )
        )

        if cursor.rowcount != 1:

            conn.rollback()

            return

        cursor.execute(
            """
            UPDATE international_companies
            SET owner_user_id = ?
            WHERE company_id = ?
            AND owner_user_id IS NULL
            """,
            (
                user_id,
                company_id
            )
        )

        if cursor.rowcount != 1:

            conn.rollback()

            return

        conn.commit()

    except Exception:

        conn.rollback()

        raise

    finally:

        conn.close()

    show_company(
        chat_id,
        message_id,
        user_id,
        company_id
    )


# ==============================
# Join Company
# ==============================

def join_company(
    chat_id,
    message_id,
    user_id,
    company_id
):

    company = get_company(company_id)

    if not company:

        show_companies(
            chat_id,
            message_id
        )

        return

    conn = database.get_connection()
    cursor = conn.cursor()

    try:

        cursor.execute(
            "BEGIN IMMEDIATE"
        )

        cursor.execute(
            """
            SELECT owner_user_id
            FROM international_companies
            WHERE company_id = ?
            """,
            (company_id,)
        )

        row = cursor.fetchone()

        if not row or row[0] is None:

            conn.rollback()

            show_company(
                chat_id,
                message_id,
                user_id,
                company_id
            )

            return

        if row[0] == user_id:

            conn.rollback()

            show_company(
                chat_id,
                message_id,
                user_id,
                company_id
            )

            return

        cursor.execute(
            """
            SELECT company_id
            FROM company_employees
            WHERE user_id = ?
            """,
            (user_id,)
        )

        if cursor.fetchone():

            conn.rollback()

            show_page(
                chat_id,
                message_id,
                "⚠️ تو در حال حاضر کارمند یک شرکت دیگر هستی.",
                keyboard([
                    back_button()
                ])
            )

            return

        cursor.execute(
            """
            SELECT COUNT(*)
            FROM company_employees
            WHERE company_id = ?
            """,
            (company_id,)
        )

        employee_count = cursor.fetchone()[0]

        if employee_count >= company["capacity"]:

            conn.rollback()

            show_page(
                chat_id,
                message_id,
                "❌ ظرفیت شرکت تکمیل شده است.",
                keyboard([
                    back_button()
                ])
            )

            return

        cursor.execute(
            """
            INSERT INTO company_employees
            (
                company_id,
                user_id,
                joined_at
            )
            VALUES (?, ?, ?)
            """,
            (
                company_id,
                user_id,
                datetime.now().isoformat()
            )
        )

        conn.commit()

    except sqlite3.IntegrityError:

        conn.rollback()

        show_page(
            chat_id,
            message_id,
            "❌ تو قبلاً کارمند یک شرکت هستی.",
            keyboard([
                back_button()
            ])
        )

        return

    except Exception:

        conn.rollback()

        raise

    finally:

        conn.close()

    show_company(
        chat_id,
        message_id,
        user_id,
        company_id
    )


# ==============================
# Leave Company
# ==============================

def leave_company(
    chat_id,
    message_id,
    user_id,
    company_id
):

    conn = database.get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        DELETE FROM company_employees
        WHERE company_id = ?
        AND user_id = ?
        """,
        (
            company_id,
            user_id
        )
    )

    conn.commit()
    conn.close()

    show_company(
        chat_id,
        message_id,
        user_id,
        company_id
    )


# ==============================
# Sell Confirmation
# ==============================

def show_sell_confirmation(
    chat_id,
    message_id,
    user_id,
    company_id
):

    company = get_company(company_id)

    if not company:

        show_companies(
            chat_id,
            message_id
        )

        return

    if not is_owner(
        user_id,
        company_id
    ):

        show_company(
            chat_id,
            message_id,
            user_id,
            company_id
        )

        return

    sale_price = company["price"] // 2

    text = (
        "💰 فروش شرکت\n\n"

        f"🏢 شرکت: {company['name']}\n"

        f"💵 قیمت خرید: "
        f"{money(company['price'])}\n"

        f"💰 مبلغ فروش: "
        f"{money(sale_price)}\n\n"

        "⚠️ با تأیید فروش، شرکت از مالکیت "
        "تو خارج می‌شود و مبلغ فروش به بودجه "
        "تو اضافه خواهد شد.\n\n"

        "آیا مطمئنی؟"
    )

    rows = [
        [
            button(
                "✅ تایید فروش",
                f"company_sell_confirm_{company_id}"
            )
        ],
        [
            button(
                "❌ لغو",
                f"company_view_{company_id}"
            )
        ]
    ]

    show_page(
        chat_id,
        message_id,
        text,
        keyboard(rows)
    )


# ==============================
# Sell Company
# ==============================

def sell_company(
    chat_id,
    message_id,
    user_id,
    company_id
):

    company = get_company(company_id)

    if not company:

        show_companies(
            chat_id,
            message_id
        )

        return

    sale_price = company["price"] // 2

    conn = database.get_connection()
    cursor = conn.cursor()

    try:

        cursor.execute(
            "BEGIN IMMEDIATE"
        )

        cursor.execute(
            """
            SELECT owner_user_id
            FROM international_companies
            WHERE company_id = ?
            """,
            (company_id,)
        )

        row = cursor.fetchone()

        if not row or row[0] != user_id:

            conn.rollback()

            show_company(
                chat_id,
                message_id,
                user_id,
                company_id
            )

            return

        cursor.execute(
            """
            UPDATE users
            SET budget = budget + ?
            WHERE user_id = ?
            """,
            (
                sale_price,
                user_id
            )
        )

        cursor.execute(
            """
            UPDATE international_companies
            SET owner_user_id = NULL
            WHERE company_id = ?
            AND owner_user_id = ?
            """,
            (
                company_id,
                user_id
            )
        )

        conn.commit()

    except Exception:

        conn.rollback()

        raise

    finally:

        conn.close()

    text = (
        "✅ شرکت با موفقیت فروخته شد.\n\n"

        f"🏢 {company['name']}\n"

        f"💰 مبلغ دریافتی: "
        f"{money(sale_price)}\n\n"

        "شرکت دوباره برای خرید در دسترس است."
    )

    show_page(
        chat_id,
        message_id,
        text,
        keyboard([
            [
                button(
                    "🌐 شرکت‌های بین‌المللی",
                    "international_companies"
                )
            ]
        ])
    )


# ==============================
# Company Income
# ==============================

def _get_company_income_cursor(
    cursor,
    user_id
):

    # مالک
    cursor.execute(
        """
        SELECT company_id
        FROM international_companies
        WHERE owner_user_id = ?
        LIMIT 1
        """,
        (user_id,)
    )

    owner_row = cursor.fetchone()

    if owner_row:

        company_id = owner_row[0]

        company = COMPANIES.get(
            company_id
        )

        if not company:

            return {
                "amount": 0,
                "role": None,
                "company_id": None
            }

        cursor.execute(
            """
            SELECT COUNT(*)
            FROM company_employees
            WHERE company_id = ?
            """,
            (company_id,)
        )

        employee_count = cursor.fetchone()[0]

        amount = (
            company["base_profit"]
            +
            employee_count
            *
            company["owner_employee_profit"]
        )

        return {
            "amount": amount,
            "role": "owner",
            "company_id": company_id
        }

    # کارمند
    cursor.execute(
        """
        SELECT company_id
        FROM company_employees
        WHERE user_id = ?
        LIMIT 1
        """,
        (user_id,)
    )

    employee_row = cursor.fetchone()

    if employee_row:

        company_id = employee_row[0]

        company = COMPANIES.get(
            company_id
        )

        if not company:

            return {
                "amount": 0,
                "role": None,
                "company_id": None
            }

        return {
            "amount": company["employee_income"],
            "role": "employee",
            "company_id": company_id
        }

    return {
        "amount": 0,
        "role": None,
        "company_id": None
    }


def get_daily_income_info(user_id):

    conn = database.get_connection()
    cursor = conn.cursor()

    try:

        result = _get_company_income_cursor(
            cursor,
            user_id
        )

        if result["company_id"]:

            company = COMPANIES.get(
                result["company_id"]
            )

            result["company_name"] = (
                company["name"]
                if company
                else "شرکت"
            )

        else:

            result["company_name"] = None

        return result

    finally:

        conn.close()


def get_company_daily_income(user_id):

    return get_daily_income_info(
        user_id
    )["amount"]


# ==============================
# Daily Payout
# ==============================

def payout_company_income(
    user_id,
    payout_date=None
):

    if payout_date is None:

        payout_date = today_iran()

    conn = database.get_connection()
    cursor = conn.cursor()

    try:

        cursor.execute(
            "BEGIN IMMEDIATE"
        )

        cursor.execute(
            """
            SELECT 1
            FROM company_daily_payouts
            WHERE payout_date = ?
            AND user_id = ?
            """,
            (
                payout_date,
                user_id
            )
        )

        if cursor.fetchone():

            conn.rollback()

            return 0

        income = _get_company_income_cursor(
            cursor,
            user_id
        )

        if (
            income["amount"] <= 0
            or not income["company_id"]
        ):

            conn.rollback()

            return 0

        cursor.execute(
            """
            UPDATE users
            SET budget = budget + ?
            WHERE user_id = ?
            """,
            (
                income["amount"],
                user_id
            )
        )

        if cursor.rowcount != 1:

            conn.rollback()

            return 0

        cursor.execute(
            """
            INSERT INTO company_daily_payouts
            (
                payout_date,
                user_id,
                company_id,
                role,
                amount,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                payout_date,
                user_id,
                income["company_id"],
                income["role"],
                income["amount"],
                datetime.now().isoformat()
            )
        )

        conn.commit()

        return income["amount"]

    except sqlite3.IntegrityError:

        conn.rollback()

        return 0

    except Exception:

        conn.rollback()

        raise

    finally:

        conn.close()


# ==============================
# Callback Handler
# ==============================

def handle_update(update):

    if not isinstance(
        update,
        dict
    ):

        return False

    callback = update.get(
        "callback_query"
    )

    if not callback:

        return False

    data = callback.get(
        "data"
    )

    if not data:

        return False

    message = callback.get(
        "message"
    ) or {}

    chat = message.get(
        "chat"
    ) or {}

    chat_id = chat.get(
        "id"
    )

    message_id = message.get(
        "message_id"
    )

    user = callback.get(
        "from"
    ) or {}

    user_id = user.get(
        "id"
    )

    if (
        chat_id is None
        or user_id is None
    ):

        return False

    # Main companies button
    if data in (
        "international_companies",
        "companies"
    ):

        init_company_tables()

        show_companies(
            chat_id,
            message_id
        )

        return True

    # Company details
    if data.startswith(
        "company_view_"
    ):

        company_id = data[
            len("company_view_"):
        ]

        show_company(
            chat_id,
            message_id,
            user_id,
            company_id
        )

        return True

    # Buy
    if data.startswith(
        "company_buy_"
    ):

        company_id = data[
            len("company_buy_"):
        ]

        buy_company(
            chat_id,
            message_id,
            user_id,
            company_id
        )

        return True

    # Join
    if data.startswith(
        "company_join_"
    ):

        company_id = data[
            len("company_join_"):
        ]

        join_company(
            chat_id,
            message_id,
            user_id,
            company_id
        )

        return True

    # Leave
    if data.startswith(
        "company_leave_"
    ):

        company_id = data[
            len("company_leave_"):
        ]

        leave_company(
            chat_id,
            message_id,
            user_id,
            company_id
        )

        return True

    # Sell confirmation
    if data.startswith(
        "company_sell_confirm_"
    ):

        company_id = data[
            len("company_sell_confirm_"):
        ]

        sell_company(
            chat_id,
            message_id,
            user_id,
            company_id
        )

        return True

    # Sell page
    if data.startswith(
        "company_sell_"
    ):

        company_id = data[
            len("company_sell_"):
        ]

        show_sell_confirmation(
            chat_id,
            message_id,
            user_id,
            company_id
        )

        return True

    return False


# ==============================
# Initialization
# ==============================

def initialize():

    init_company_tables()