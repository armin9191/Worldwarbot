# ==============================
# World War - Alliance
# ==============================

import json
import time

import database


# ==============================
# اتصال به bot.py
# ==============================

send_message = None
edit_message = None


# ==============================
# سشن‌های موقت
# ==============================

waiting = {}


# ==============================
# فروشگاه اتحاد
# ==============================

ALLIANCE_SHOP_ITEMS = {
    "kheybershekan": {
        "name": "⚡ موشک خیبرشکن",
        "price": 500000,
    },
    "f16": {
        "name": "✈️ جنگنده F-16",
        "price": 1000000,
    },
    "patriot": {
        "name": "🛡️ سامانه پاتریوت",
        "price": 100000,
    },
    "f22": {
        "name": "🛩️ جنگنده F-22",
        "price": 1500000,
    },
    "cruise_missile": {
        "name": "💨 موشک کروز",
        "price": 300000,
    },
    "thaad": {
        "name": "🔵 سامانه تاد",
        "price": 300000,
    },
}

SHOP_QTY_LIST = [1, 5, 10, 20]

# هزینه ساخت اتحاد
ALLIANCE_CREATE_COST = 500_000_000_000

CANCEL_TEXTS = {
    "لغو",
    "انصراف",
    "cancel",
    "/cancel",
}


# ==============================
# ابزارهای عمومی
# ==============================

def setup(send_message_function, edit_message_function):
    """اتصال ماژول اتحاد به توابع bot.py."""
    global send_message, edit_message

    send_message = send_message_function
    edit_message = edit_message_function

    init_alliance_tables()


def init_alliance_tables():
    """
    ساخت جداول موردنیاز اتحاد.

    این تابع مستقل از جداول کاربران است و فقط از database.get_connection()
    استفاده می‌کند تا معماری پروژه حفظ شود.
    """
    connection = database.get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("PRAGMA foreign_keys = ON")

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS alliances (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                tag TEXT,
                leader_id INTEGER NOT NULL,
                treasury INTEGER NOT NULL DEFAULT 0 CHECK(treasury >= 0),
                status TEXT NOT NULL DEFAULT 'active',
                created_at INTEGER NOT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS alliance_members (
                alliance_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                role TEXT NOT NULL DEFAULT 'member',
                joined_at INTEGER NOT NULL,
                PRIMARY KEY (alliance_id, user_id)
            )
        """)

        # هر بازیکن فقط می‌تواند عضو یک اتحاد باشد.
        cursor.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS idx_one_alliance_per_user
            ON alliance_members(user_id)
        """)

        # نام و تگ فقط بین اتحادهای فعال باید یکتا باشند.
        cursor.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS idx_active_alliance_name
            ON alliances(name)
            WHERE status = 'active'
        """)

        cursor.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS idx_active_alliance_tag
            ON alliances(tag)
            WHERE status = 'active' AND tag IS NOT NULL
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS alliance_warehouse (
                alliance_id INTEGER NOT NULL,
                item_id TEXT NOT NULL,
                quantity INTEGER NOT NULL DEFAULT 0 CHECK(quantity >= 0),
                PRIMARY KEY (alliance_id, item_id)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS alliance_transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                alliance_id INTEGER NOT NULL,
                user_id INTEGER,
                tx_type TEXT NOT NULL,
                amount INTEGER NOT NULL DEFAULT 0,
                item_id TEXT,
                quantity INTEGER NOT NULL DEFAULT 0,
                note TEXT,
                created_at INTEGER NOT NULL
            )
        """)

        connection.commit()

    except Exception as error:
        connection.rollback()
        print(f"Alliance Tables Error: {error}")
        raise

    finally:
        connection.close()


def now():
    return int(time.time())


def money(value):
    try:
        return f"{int(value):,}"
    except (TypeError, ValueError):
        return "0"


def persian_number(value):
    """تبدیل عدد انگلیسی به عدد فارسی برای متن دکمه‌ها و پیام‌ها."""
    return str(value).translate(str.maketrans(
        "0123456789",
        "۰۱۲۳۴۵۶۷۸۹"
    ))


def item_name(item_id):
    item = ALLIANCE_SHOP_ITEMS.get(item_id)
    return item["name"] if item else str(item_id)


def is_cancel_text(text):
    return str(text).strip().lower() in CANCEL_TEXTS


def parse_positive_int(text):
    raw = str(text).strip()
    raw = raw.replace(",", "").replace("،", "").replace("٬", "")

    persian = "۰۱۲۳۴۵۶۷۸۹"
    english = "0123456789"

    for p, e in zip(persian, english):
        raw = raw.replace(p, e)

    if not raw.isdigit():
        return None

    value = int(raw)

    if value <= 0:
        return None

    return value


def clean_name(text):
    return " ".join(str(text).strip().split())


def clean_tag(text):
    tag = str(text).strip().lstrip("#")
    return "".join(tag.split())


def valid_tag(tag):
    """
    تگ فقط با حروف/اعداد/زیرخط باشد.
    فارسی هم برای تگ مجاز است.
    """
    if not tag or not (2 <= len(tag) <= 16):
        return False

    for char in tag:
        if char.isalnum() or char == "_":
            continue
        return False

    return True


def clear_waiting(user_id):
    waiting.pop(user_id, None)


def set_waiting(user_id, action, message_id=None, extra=None):
    waiting[user_id] = {
        "action": action,
        "message_id": message_id,
        "extra": extra or {},
    }


def user_label(user_id):
    user = database.get_user(user_id)

    if user and user.get("country"):
        return user["country"]

    return f"بازیکن {user_id}"


# ==============================
# کیبورد
# ==============================

def inline(rows):
    return {"inline_keyboard": rows}


def btn(text, data):
    return {
        "text": str(text),
        "callback_data": str(data),
    }


def back_row():
    return [btn("🔙 بازگشت", "alliance")]


def cancel_keyboard():
    return inline([
        [btn("❌ لغو", "alliance_cancel")],
        back_row(),
    ])


def alliance_menu_keyboard(is_member=False, is_leader=False):
    rows = []

    if not is_member:
        rows.append([
            btn("🏰 ساخت اتحاد", "alliance_create"),
            btn("🤝 اتحاد من", "alliance_my"),
        ])
    else:
        rows.append([
            btn("🤝 اتحاد من", "alliance_my"),
        ])

    rows.append([
        btn("🔎 اتحادهای موجود", "alliance_list_0"),
    ])

    rows.append([
        btn("💰 خزانه اتحاد", "alliance_treasury"),
        btn("📦 انبار اتحاد", "alliance_warehouse"),
    ])

    if is_leader:
        rows.append([
            btn("🛒 فروشگاه اتحاد", "alliance_shop"),
        ])

    rows.append([
        btn("👥 اعضا و مدیریت", "alliance_manage"),
    ])

    rows.append([
        btn("🔙 بازگشت به منوی اصلی", "back_main_menu"),
    ])

    return inline(rows)


# ==============================
# توابع ارسال/ویرایش
# ==============================

def edit_or_send(chat_id, message_id, text, reply_markup=None):
    if message_id is not None and edit_message:
        edit_message(chat_id, message_id, text, reply_markup)
    elif send_message:
        send_message(chat_id, text, reply_markup)


def send_input_prompt(chat_id, text, placeholder=None):
    """پیام جدید با ForceReply برای ورودی‌های کاربر."""
    if not send_message:
        return None

    reply_markup = {
        "force_reply": True,
        "selective": True,
    }

    if placeholder:
        reply_markup["input_field_placeholder"] = str(placeholder)[:64]

    return send_message(chat_id, text, reply_markup)


def get_sent_message_id(result):
    """استخراج message_id از پاسخ ارسال پیام، بدون تغییر منطق اصلی."""
    if not isinstance(result, dict):
        return None

    message = result.get("result")

    if isinstance(message, dict):
        return message.get("message_id")

    return result.get("message_id")


def show_error(chat_id, message_id, text):
    edit_or_send(
        chat_id,
        message_id,
        f"❌ {text}",
        inline([back_row()]),
    )


# ==============================
# اطلاعات اتحاد
# ==============================

def get_user_alliance(user_id):
    connection = database.get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("""
            SELECT
                a.id,
                a.name,
                a.tag,
                a.leader_id,
                a.treasury,
                a.status,
                a.created_at,
                m.role
            FROM alliance_members m
            JOIN alliances a ON a.id = m.alliance_id
            WHERE m.user_id = ?
              AND a.status = 'active'
            LIMIT 1
        """, (user_id,))

        row = cursor.fetchone()

        if row is None:
            return None

        return {
            "id": row[0],
            "name": row[1],
            "tag": row[2],
            "leader_id": row[3],
            "treasury": row[4],
            "status": row[5],
            "created_at": row[6],
            "role": row[7],
        }

    finally:
        connection.close()


def get_alliance(alliance_id):
    connection = database.get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("""
            SELECT id, name, tag, leader_id, treasury, status, created_at
            FROM alliances
            WHERE id = ?
              AND status = 'active'
        """, (alliance_id,))

        row = cursor.fetchone()

        if row is None:
            return None

        return {
            "id": row[0],
            "name": row[1],
            "tag": row[2],
            "leader_id": row[3],
            "treasury": row[4],
            "status": row[5],
            "created_at": row[6],
        }

    finally:
        connection.close()


def get_members(alliance_id):
    connection = database.get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("""
            SELECT user_id, role, joined_at
            FROM alliance_members
            WHERE alliance_id = ?
            ORDER BY
                CASE WHEN role = 'leader' THEN 0 ELSE 1 END,
                joined_at ASC
        """, (alliance_id,))

        rows = cursor.fetchall()

        return [
            {
                "user_id": row[0],
                "role": row[1],
                "joined_at": row[2],
            }
            for row in rows
        ]

    finally:
        connection.close()


def member_count(alliance_id):
    connection = database.get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("""
            SELECT COUNT(*)
            FROM alliance_members
            WHERE alliance_id = ?
        """, (alliance_id,))

        return cursor.fetchone()[0]

    finally:
        connection.close()


def is_leader(user_id):
    alliance = get_user_alliance(user_id)

    if alliance is None:
        return False

    return (
        alliance["leader_id"] == user_id
        and alliance["role"] == "leader"
    )


# ==============================
# انبار اتحاد
# ==============================

def get_warehouse(alliance_id):
    connection = database.get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("""
            SELECT item_id, quantity
            FROM alliance_warehouse
            WHERE alliance_id = ?
              AND quantity > 0
            ORDER BY item_id
        """, (alliance_id,))

        rows = cursor.fetchall()

        return {
            item_id: quantity
            for item_id, quantity in rows
        }

    finally:
        connection.close()


def warehouse_qty(alliance_id, item_id):
    connection = database.get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("""
            SELECT quantity
            FROM alliance_warehouse
            WHERE alliance_id = ?
              AND item_id = ?
        """, (alliance_id, item_id))

        row = cursor.fetchone()
        return row[0] if row else 0

    finally:
        connection.close()


def warehouse_text(stock):
    if not stock:
        return "خالی است."

    lines = []

    for item_id, quantity in stock.items():
        lines.append(
            f"• {item_name(item_id)} × {money(quantity)}"
        )

    return "\n".join(lines)


# ==============================
# تراکنش‌های اتحاد
# ==============================

def add_tx(
    cursor,
    alliance_id,
    user_id,
    tx_type,
    amount=0,
    item_id=None,
    quantity=0,
    note="",
):
    cursor.execute("""
        INSERT INTO alliance_transactions
        (
            alliance_id,
            user_id,
            tx_type,
            amount,
            item_id,
            quantity,
            note,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        alliance_id,
        user_id,
        tx_type,
        amount,
        item_id,
        quantity,
        note,
        now(),
    ))


# ==============================
# لیست اتحادها
# ==============================

def list_alliances(page=0, per_page=5):
    try:
        page = max(0, int(page))
        per_page = max(1, min(int(per_page), 20))
    except (TypeError, ValueError):
        page = 0
        per_page = 5

    connection = database.get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("""
            SELECT COUNT(*)
            FROM alliances
            WHERE status = 'active'
        """)

        total = cursor.fetchone()[0]

        cursor.execute("""
            SELECT
                a.id,
                a.name,
                a.tag,
                a.leader_id,
                a.treasury,
                (
                    SELECT COUNT(*)
                    FROM alliance_members m
                    WHERE m.alliance_id = a.id
                ) AS members_count
            FROM alliances a
            WHERE a.status = 'active'
            ORDER BY a.created_at DESC
            LIMIT ? OFFSET ?
        """, (per_page, page * per_page))

        rows = cursor.fetchall()

        items = [
            {
                "id": row[0],
                "name": row[1],
                "tag": row[2],
                "leader_id": row[3],
                "treasury": row[4],
                "members_count": row[5],
            }
            for row in rows
        ]

        return items, total

    finally:
        connection.close()


def alliance_detail_text(alliance):
    members = get_members(alliance["id"])
    stock = get_warehouse(alliance["id"])

    tag = f"#{alliance['tag']}" if alliance.get("tag") else "بدون تگ"

    return (
        f"🏰 {alliance['name']}\n\n"
        f"🏷 تگ: {tag}\n"
        f"👑 رهبر: {user_label(alliance['leader_id'])}\n"
        f"👥 تعداد اعضا: {len(members)}\n"
        f"💰 خزانه: {money(alliance['treasury'])}\n\n"
        f"📦 انبار اتحاد:\n{warehouse_text(stock)}"
    )


# ==============================
# منوی اصلی اتحاد
# ==============================

def show_alliance_menu(chat_id, user_id, message_id=None):
    clear_waiting(user_id)
    database.get_or_create_user(user_id)

    alliance = get_user_alliance(user_id)

    text = "🏰 منوی اتحاد\n\n"

    if alliance:
        role = "رهبر" if alliance["role"] == "leader" else "عضو"
        tag = f"#{alliance['tag']}" if alliance["tag"] else "بدون تگ"

        text += (
            f"اتحاد فعلی: {alliance['name']}\n"
            f"🏷 تگ: {tag}\n"
            f"👤 نقش شما: {role}\n"
            f"💰 خزانه: {money(alliance['treasury'])}\n\n"
        )
    else:
        text += "شما فعلاً عضو هیچ اتحادی نیستید.\n\n"

    text += "یک گزینه را انتخاب کنید:"

    edit_or_send(
        chat_id,
        message_id,
        text,
        alliance_menu_keyboard(
            is_member=bool(alliance),
            is_leader=bool(alliance and alliance["role"] == "leader"),
        ),
    )


# ==============================
# ساخت اتحاد
# ==============================

def start_create(chat_id, user_id, message_id):
    if get_user_alliance(user_id):
        show_error(
            chat_id,
            message_id,
            "شما از قبل عضو یک اتحاد هستید و نمی‌توانید اتحاد جدید بسازید.",
        )
        return

    sent = send_input_prompt(
        chat_id,
        "🏰 ساخت اتحاد\n\n"
        "نام اتحاد را در پاسخ به این پیام ارسال کنید.\n"
        "حداقل ۳ و حداکثر ۳۲ کاراکتر.\n\n"
        "برای انصراف، بنویسید: لغو",
        "نام اتحاد",
    )

    # از اینجا به بعد، همان پیام جدیدِ ForceReply باید ویرایش شود.
    prompt_message_id = get_sent_message_id(sent) or message_id
    set_waiting(user_id, "create_name", prompt_message_id)


def show_create_confirmation(
    chat_id,
    user_id,
    message_id,
    name,
    tag=None,
):
    user = database.get_or_create_user(user_id)
    budget = user["budget"] if user else 0

    tag_text = f"#{tag}" if tag else "بدون تگ"

    edit_or_send(
        chat_id,
        message_id,
        "🛡️ تأیید ساخت اتحاد\n\n"
        f"🏰 نام اتحاد: «{name}»\n"
        f"🏷 تگ: {tag_text}\n\n"
        f"💰 هزینه ساخت: {money(ALLIANCE_CREATE_COST)} دلار\n"
        f"💳 بودجه فعلی شما: {money(budget)} دلار\n\n"
        "آیا از ساخت این اتحاد مطمئن هستید؟",
        inline([
            [
                btn("✅ تأیید و پرداخت", "alliance_create_confirm"),
                btn("❌ لغو", "alliance_cancel"),
            ],
            back_row(),
        ]),
    )


def create_alliance(user_id, name, tag=None):
    name = clean_name(name)

    if len(name) < 3:
        return False, "نام اتحاد باید حداقل ۳ کاراکتر باشد."

    if len(name) > 32:
        return False, "نام اتحاد نباید بیشتر از ۳۲ کاراکتر باشد."

    if tag:
        tag = clean_tag(tag)

        if not valid_tag(tag):
            return False, (
                "تگ نامعتبر است.\n"
                "تگ باید بین ۲ تا ۱۶ کاراکتر و فقط شامل "
                "حروف، عدد یا _ باشد."
            )
    else:
        tag = None

    connection = database.get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("BEGIN IMMEDIATE")

        cursor.execute("""
            SELECT alliance_id
            FROM alliance_members
            WHERE user_id = ?
            LIMIT 1
        """, (user_id,))

        if cursor.fetchone():
            connection.rollback()
            return False, "شما از قبل عضو یک اتحاد هستید."

        # ==============================
        # بررسی بودجه و پرداخت هزینه ساخت
        # ==============================

        cursor.execute("""
            SELECT budget
            FROM users
            WHERE user_id = ?
            LIMIT 1
        """, (user_id,))

        user_row = cursor.fetchone()

        if user_row is None:
            connection.rollback()
            return False, "کاربر پیدا نشد."

        budget = user_row[0]

        if budget < ALLIANCE_CREATE_COST:
            connection.rollback()
            return False, (
                "بودجه شما برای ساخت اتحاد کافی نیست.\n\n"
                f"💰 هزینه ساخت: {money(ALLIANCE_CREATE_COST)} دلار\n"
                f"💳 بودجه فعلی: {money(budget)} دلار"
            )

        cursor.execute("""
            UPDATE users
            SET budget = budget - ?
            WHERE user_id = ?
              AND budget >= ?
        """, (
            ALLIANCE_CREATE_COST,
            user_id,
            ALLIANCE_CREATE_COST,
        ))

        if cursor.rowcount == 0:
            connection.rollback()
            return False, "پرداخت هزینه ساخت اتحاد انجام نشد."

        # ==============================
        # بررسی نام اتحاد
        # ==============================

        cursor.execute("""
            SELECT id
            FROM alliances
            WHERE name = ?
              AND status = 'active'
            LIMIT 1
        """, (name,))

        if cursor.fetchone():
            connection.rollback()
            return False, "این نام اتحاد قبلاً استفاده شده است."

        # ==============================
        # بررسی تگ
        # ==============================

        if tag:
            cursor.execute("""
                SELECT id
                FROM alliances
                WHERE tag = ?
                  AND status = 'active'
                LIMIT 1
            """, (tag,))

            if cursor.fetchone():
                connection.rollback()
                return False, "این تگ قبلاً استفاده شده است."

        created_at = now()

        cursor.execute("""
            INSERT INTO alliances
            (
                name,
                tag,
                leader_id,
                treasury,
                status,
                created_at
            )
            VALUES (?, ?, ?, 0, 'active', ?)
        """, (
            name,
            tag,
            user_id,
            created_at,
        ))

        alliance_id = cursor.lastrowid

        cursor.execute("""
            INSERT INTO alliance_members
            (
                alliance_id,
                user_id,
                role,
                joined_at
            )
            VALUES (?, ?, 'leader', ?)
        """, (
            alliance_id,
            user_id,
            created_at,
        ))

        add_tx(
            cursor,
            alliance_id,
            user_id,
            "create",
            note="ایجاد اتحاد",
        )

        connection.commit()

        return True, name

    except Exception as error:
        connection.rollback()
        print(f"Create Alliance Error: {error}")
        return False, "ساخت اتحاد انجام نشد."

    finally:
        connection.close()


# ==============================
# ورود به اتحاد
# ==============================

def join_alliance(user_id, alliance_id):
    database.get_or_create_user(user_id)

    connection = database.get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("BEGIN IMMEDIATE")

        cursor.execute("""
            SELECT a.id, a.name
            FROM alliance_members m
            JOIN alliances a ON a.id = m.alliance_id
            WHERE m.user_id = ?
              AND a.status = 'active'
            LIMIT 1
        """, (user_id,))

        current = cursor.fetchone()

        if current:
            connection.rollback()
            return False, f"شما هم‌اکنون عضو اتحاد «{current[1]}» هستید."

        cursor.execute("""
            SELECT id, name
            FROM alliances
            WHERE id = ?
              AND status = 'active'
        """, (alliance_id,))

        alliance = cursor.fetchone()

        if alliance is None:
            connection.rollback()
            return False, "این اتحاد وجود ندارد یا منحل شده است."

        joined_at = now()

        cursor.execute("""
            INSERT INTO alliance_members
            (
                alliance_id,
                user_id,
                role,
                joined_at
            )
            VALUES (?, ?, 'member', ?)
        """, (
            alliance_id,
            user_id,
            joined_at,
        ))

        add_tx(
            cursor,
            alliance_id,
            user_id,
            "join",
            note="عضویت",
        )

        connection.commit()

        return True, alliance[1]

    except Exception as error:
        connection.rollback()
        print(f"Join Alliance Error: {error}")
        return False, "ورود به اتحاد انجام نشد."

    finally:
        connection.close()


# ==============================
# خروج از اتحاد
# ==============================

def leave_alliance(user_id):
    alliance = get_user_alliance(user_id)

    if alliance is None:
        return False, "شما عضو هیچ اتحادی نیستید."

    if is_leader(user_id):
        count = member_count(alliance["id"])

        if count > 1:
            return False, (
                "رهبر نمی‌تواند اتحاد را ترک کند.\n"
                "ابتدا رهبری را به یکی از اعضا منتقل کنید."
            )

        return False, (
            "اگر تنها عضو اتحاد هستید، "
            "از گزینه «منحل کردن اتحاد» استفاده کنید."
        )

    connection = database.get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("BEGIN IMMEDIATE")

        cursor.execute("""
            DELETE FROM alliance_members
            WHERE alliance_id = ?
              AND user_id = ?
        """, (
            alliance["id"],
            user_id,
        ))

        if cursor.rowcount == 0:
            connection.rollback()
            return False, "عضویت شما در اتحاد پیدا نشد."

        add_tx(
            cursor,
            alliance["id"],
            user_id,
            "leave",
            note="خروج از اتحاد",
        )

        connection.commit()

        return True, alliance["name"]

    except Exception as error:
        connection.rollback()
        print(f"Leave Alliance Error: {error}")
        return False, "خروج از اتحاد انجام نشد."

    finally:
        connection.close()


# ==============================
# انحلال اتحاد
# ==============================

def disband_alliance(user_id):
    alliance = get_user_alliance(user_id)

    if alliance is None:
        return False, "شما عضو هیچ اتحادی نیستید."

    if not is_leader(user_id):
        return False, "فقط رهبر می‌تواند اتحاد را منحل کند."

    if member_count(alliance["id"]) > 1:
        return False, "تا وقتی عضو دیگری در اتحاد هست، نمی‌توان آن را منحل کرد."

    connection = database.get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("BEGIN IMMEDIATE")

        cursor.execute("""
            SELECT status, treasury
            FROM alliances
            WHERE id = ?
        """, (alliance["id"],))

        row = cursor.fetchone()

        if row is None or row[0] != "active":
            connection.rollback()
            return False, "این اتحاد دیگر فعال نیست."

        # تراکنش انحلال قبل از حذف عضو ثبت می‌شود.
        add_tx(
            cursor,
            alliance["id"],
            user_id,
            "disband",
            amount=row[1],
            note="انحلال اتحاد",
        )

        cursor.execute("""
            UPDATE alliances
            SET status = 'disbanded'
            WHERE id = ?
              AND status = 'active'
        """, (alliance["id"],))

        if cursor.rowcount == 0:
            connection.rollback()
            return False, "انحلال اتحاد انجام نشد."

        cursor.execute("""
            DELETE FROM alliance_members
            WHERE alliance_id = ?
        """, (alliance["id"],))

        connection.commit()

        return True, alliance["name"]

    except Exception as error:
        connection.rollback()
        print(f"Disband Alliance Error: {error}")
        return False, "انحلال اتحاد انجام نشد."

    finally:
        connection.close()


# ==============================
# انتقال رهبری
# ==============================

def transfer_leadership(leader_id, new_leader_id):
    if leader_id == new_leader_id:
        return False, "نمی‌توانید رهبری را به خودتان منتقل کنید."

    alliance = get_user_alliance(leader_id)

    if alliance is None:
        return False, "شما عضو هیچ اتحادی نیستید."

    if not is_leader(leader_id):
        return False, "فقط رهبر می‌تواند رهبری را منتقل کند."

    connection = database.get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("BEGIN IMMEDIATE")

        cursor.execute("""
            SELECT 1
            FROM alliance_members
            WHERE alliance_id = ?
              AND user_id = ?
            LIMIT 1
        """, (
            alliance["id"],
            new_leader_id,
        ))

        if cursor.fetchone() is None:
            connection.rollback()
            return False, "این بازیکن عضو اتحاد شما نیست."

        cursor.execute("""
            UPDATE alliances
            SET leader_id = ?
            WHERE id = ?
              AND status = 'active'
        """, (
            new_leader_id,
            alliance["id"],
        ))

        if cursor.rowcount == 0:
            connection.rollback()
            return False, "انتقال رهبری انجام نشد."

        cursor.execute("""
            UPDATE alliance_members
            SET role = 'member'
            WHERE alliance_id = ?
        """, (alliance["id"],))

        cursor.execute("""
            UPDATE alliance_members
            SET role = 'leader'
            WHERE alliance_id = ?
              AND user_id = ?
        """, (
            alliance["id"],
            new_leader_id,
        ))

        add_tx(
            cursor,
            alliance["id"],
            leader_id,
            "transfer_leader",
            note=str(new_leader_id),
        )

        connection.commit()

        return True, alliance["name"]

    except Exception as error:
        connection.rollback()
        print(f"Transfer Leadership Error: {error}")
        return False, "انتقال رهبری انجام نشد."

    finally:
        connection.close()


def notify_alliance_members(alliance_id, text):
    """ارسال پیام اطلاع‌رسانی به تمام اعضای فعلی اتحاد."""
    if not send_message:
        return

    for member in get_members(alliance_id):
        try:
            send_message(
                member["user_id"],
                text,
                None,
            )
        except Exception as error:
            print(
                f"Alliance Notification Error "
                f"(user={member['user_id']}): {error}"
            )


# ==============================
# خزانه اتحاد
# ==============================

def donate_to_treasury(user_id, amount):
    if amount <= 0:
        return False, "مبلغ باید بیشتر از صفر باشد."

    alliance = get_user_alliance(user_id)

    if alliance is None:
        return False, "برای اهدا باید عضو یک اتحاد باشید."

    connection = database.get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("BEGIN IMMEDIATE")

        cursor.execute("""
            SELECT budget
            FROM users
            WHERE user_id = ?
        """, (user_id,))

        user_row = cursor.fetchone()

        if user_row is None:
            connection.rollback()
            return False, "کاربر پیدا نشد."

        budget = user_row[0]

        if budget < amount:
            connection.rollback()
            return False, (
                "موجودی شما کافی نیست.\n"
                f"موجودی فعلی: {money(budget)}\n"
                f"مبلغ درخواستی: {money(amount)}"
            )

        cursor.execute("""
            UPDATE users
            SET budget = budget - ?
            WHERE user_id = ?
              AND budget >= ?
        """, (
            amount,
            user_id,
            amount,
        ))

        if cursor.rowcount == 0:
            connection.rollback()
            return False, "موجودی شما کافی نیست."

        cursor.execute("""
            UPDATE alliances
            SET treasury = treasury + ?
            WHERE id = ?
              AND status = 'active'
        """, (
            amount,
            alliance["id"],
        ))

        if cursor.rowcount == 0:
            connection.rollback()
            return False, "اتحاد پیدا نشد یا دیگر فعال نیست."

        add_tx(
            cursor,
            alliance["id"],
            user_id,
            "donate",
            amount=amount,
            note="اهدا به خزانه",
        )

        cursor.execute("""
            SELECT treasury
            FROM alliances
            WHERE id = ?
        """, (alliance["id"],))

        treasury = cursor.fetchone()[0]

        connection.commit()

        notify_alliance_members(
            alliance["id"],
            f"💰 کمک مالی به خزانه اتحاد\n\n"
            f"🌍 کشور «{user_label(user_id)}» مبلغ {money(amount)} "
            f"به خزانه اتحاد «{alliance['name']}» کمک مالی کرد.\n\n"
            f"💰 موجودی جدید خزانه: {money(treasury)}",
        )

        return True, {
            "name": alliance["name"],
            "amount": amount,
            "treasury": treasury,
        }

    except Exception as error:
        connection.rollback()
        print(f"Donate Error: {error}")
        return False, "اهدا انجام نشد."

    finally:
        connection.close()


# ==============================
# فروشگاه اتحاد
# ==============================

def buy_alliance_item(user_id, item_id, quantity):
    if quantity <= 0:
        return False, "تعداد باید بیشتر از صفر باشد."

    item = ALLIANCE_SHOP_ITEMS.get(item_id)

    if item is None:
        return False, "این آیتم در فروشگاه اتحاد وجود ندارد."

    alliance = get_user_alliance(user_id)

    if alliance is None:
        return False, "شما عضو هیچ اتحادی نیستید."

    if not is_leader(user_id):
        return False, "فقط رهبر می‌تواند از فروشگاه اتحاد خرید کند."

    cost = item["price"] * quantity

    connection = database.get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("BEGIN IMMEDIATE")

        cursor.execute("""
            SELECT treasury
            FROM alliances
            WHERE id = ?
              AND status = 'active'
        """, (alliance["id"],))

        row = cursor.fetchone()

        if row is None:
            connection.rollback()
            return False, "اتحاد پیدا نشد."

        treasury = row[0]

        if treasury < cost:
            connection.rollback()
            return False, (
                "موجودی خزانه کافی نیست.\n"
                f"هزینه: {money(cost)}\n"
                f"خزانه: {money(treasury)}"
            )

        cursor.execute("""
            UPDATE alliances
            SET treasury = treasury - ?
            WHERE id = ?
              AND status = 'active'
              AND treasury >= ?
        """, (
            cost,
            alliance["id"],
            cost,
        ))

        if cursor.rowcount == 0:
            connection.rollback()
            return False, "خرید انجام نشد."

        cursor.execute("""
            INSERT INTO alliance_warehouse
            (
                alliance_id,
                item_id,
                quantity
            )
            VALUES (?, ?, ?)
            ON CONFLICT(alliance_id, item_id)
            DO UPDATE SET
                quantity = quantity + excluded.quantity
        """, (
            alliance["id"],
            item_id,
            quantity,
        ))

        add_tx(
            cursor,
            alliance["id"],
            user_id,
            "shop_buy",
            amount=cost,
            item_id=item_id,
            quantity=quantity,
            note="خرید از فروشگاه اتحاد",
        )

        cursor.execute("""
            SELECT treasury
            FROM alliances
            WHERE id = ?
        """, (alliance["id"],))

        new_treasury = cursor.fetchone()[0]

        connection.commit()

        notify_alliance_members(
            alliance["id"],
            f"🎁 تجهیزات جدید برای اتحاد\n\n"
            f"👑 رهبر اتحاد «{alliance['name']}»، کشور «{user_label(user_id)}»، "
            f"برای اعضای اتحاد تجهیزات تهیه کرد.\n\n"
            f"📦 {item['name']} × {money(quantity)}\n"
            f"این تجهیزات به انبار اتحاد اضافه شد و برای توزیع بین اعضا آماده است.",
        )

        return True, {
            "name": item["name"],
            "quantity": quantity,
            "treasury": new_treasury,
        }

    except Exception as error:
        connection.rollback()
        print(f"Alliance Shop Error: {error}")
        return False, "خرید از فروشگاه اتحاد انجام نشد."

    finally:
        connection.close()


# ==============================
# توزیع تجهیزات
# ==============================

def split_items(member_ids, quantity):
    count = len(member_ids)

    if count <= 0:
        return None, "عضوی برای توزیع وجود ندارد."

    if quantity < count:
        return None, (
            "تعداد تجهیزات نمی‌تواند کمتر از تعداد اعضای اتحاد باشد."
        )

    base = quantity // count
    remain = quantity % count

    shares = {}

    for index, member_id in enumerate(member_ids):
        shares[member_id] = base + (1 if index < remain else 0)

    return shares, None


def distribute_items(leader_id, item_id, quantity):
    if quantity <= 0:
        return False, "تعداد باید بیشتر از صفر باشد."

    if item_id not in ALLIANCE_SHOP_ITEMS:
        return False, "آیتم نامعتبر است."

    alliance = get_user_alliance(leader_id)

    if alliance is None:
        return False, "شما عضو هیچ اتحادی نیستید."

    if not is_leader(leader_id):
        return False, "فقط رهبر می‌تواند انبار را مدیریت کند."

    connection = database.get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("BEGIN IMMEDIATE")

        cursor.execute("""
            SELECT user_id
            FROM alliance_members
            WHERE alliance_id = ?
            ORDER BY
                CASE WHEN role = 'leader' THEN 0 ELSE 1 END,
                joined_at ASC
        """, (alliance["id"],))

        member_ids = [row[0] for row in cursor.fetchall()]

        shares, error = split_items(member_ids, quantity)

        if error:
            connection.rollback()
            return False, error

        cursor.execute("""
            SELECT quantity
            FROM alliance_warehouse
            WHERE alliance_id = ?
              AND item_id = ?
        """, (
            alliance["id"],
            item_id,
        ))

        row = cursor.fetchone()
        available = row[0] if row else 0

        if available < quantity:
            connection.rollback()
            return False, (
                "موجودی انبار کافی نیست.\n"
                f"موجود: {money(available)}\n"
                f"درخواستی: {money(quantity)}"
            )

        cursor.execute("""
            UPDATE alliance_warehouse
            SET quantity = quantity - ?
            WHERE alliance_id = ?
              AND item_id = ?
              AND quantity >= ?
        """, (
            quantity,
            alliance["id"],
            item_id,
            quantity,
        ))

        if cursor.rowcount == 0:
            connection.rollback()
            return False, "کاهش موجودی انبار انجام نشد."

        for member_id, share in shares.items():
            if share <= 0:
                continue

            cursor.execute("""
                INSERT INTO inventory
                (
                    user_id,
                    item_id,
                    quantity
                )
                VALUES (?, ?, ?)
                ON CONFLICT(user_id, item_id)
                DO UPDATE SET
                    quantity = quantity + excluded.quantity
            """, (
                member_id,
                item_id,
                share,
            ))

        add_tx(
            cursor,
            alliance["id"],
            leader_id,
            "distribute",
            item_id=item_id,
            quantity=quantity,
            note=json.dumps(
                {str(k): v for k, v in shares.items()},
                ensure_ascii=False,
            ),
        )

        # ردیف‌های صفر را پاک می‌کنیم.
        cursor.execute("""
            DELETE FROM alliance_warehouse
            WHERE alliance_id = ?
              AND quantity <= 0
        """, (alliance["id"],))

        connection.commit()

        return True, shares

    except Exception as error:
        connection.rollback()
        print(f"Distribute Error: {error}")
        return False, "توزیع انجام نشد و موجودی انبار تغییر نکرد."

    finally:
        connection.close()


# ==============================
# نمایش اتحاد من
# ==============================

def show_my_alliance(chat_id, user_id, message_id):
    alliance = get_user_alliance(user_id)

    if alliance is None:
        edit_or_send(
            chat_id,
            message_id,
            "شما عضو هیچ اتحادی نیستید.",
            inline([
                [btn("🔎 اتحادهای موجود", "alliance_list_0")],
                [btn("🏰 ساخت اتحاد", "alliance_create")],
                back_row(),
            ]),
        )
        return

    text = "🤝 اتحاد من\n\n" + alliance_detail_text(alliance)

    buttons = []

    if is_leader(user_id):
        buttons.append([
            btn("👑 انتقال رهبری", "alliance_transfer_list")
        ])
        buttons.append([
            btn("💥 منحل کردن اتحاد", "alliance_disband_ask")
        ])
    else:
        buttons.append([
            btn("🚪 خروج از اتحاد", "alliance_leave_ask")
        ])

    buttons.append(back_row())

    edit_or_send(
        chat_id,
        message_id,
        text,
        inline(buttons),
    )


# ==============================
# لیست اتحادها
# ==============================

def show_alliance_list(chat_id, user_id, message_id, page=0):
    try:
        page = max(0, int(page))
    except (TypeError, ValueError):
        page = 0

    per_page = 5
    items, total = list_alliances(page, per_page)

    if total == 0:
        edit_or_send(
            chat_id,
            message_id,
            "هنوز هیچ اتحاد فعالی ساخته نشده است.",
            inline([
                [btn("🏰 ساخت اتحاد", "alliance_create")],
                back_row(),
            ]),
        )
        return

    pages = max(1, (total + per_page - 1) // per_page)

    if page >= pages:
        page = pages - 1
        items, total = list_alliances(page, per_page)

    text = (
        f"🔎 اتحادهای موجود\n"
        f"صفحه {persian_number(page + 1)} از {persian_number(pages)}\n\n"
    )

    buttons = []

    for item in items:
        tag = f" #{item['tag']}" if item["tag"] else ""

        text += (
            f"🏰 {item['name']}{tag}\n"
            f"👑 رهبر: {user_label(item['leader_id'])}\n"
            f"👥 اعضا: {persian_number(item['members_count'])}\n"
            f"💰 خزانه: {money(item['treasury'])}\n\n"
        )

        buttons.append([
            btn(
                f"🔎 مشاهده «{item['name']}»",
                f"alliance_view_{item['id']}",
            )
        ])

    navigation = []

    if page > 0:
        navigation.append(
            btn("◀️ قبلی", f"alliance_list_{page - 1}")
        )

    if page + 1 < pages:
        navigation.append(
            btn("بعدی ▶️", f"alliance_list_{page + 1}")
        )

    if navigation:
        buttons.append(navigation)

    buttons.append(back_row())

    edit_or_send(
        chat_id,
        message_id,
        text,
        inline(buttons),
    )


def show_alliance_view(chat_id, user_id, message_id, alliance_id):
    alliance = get_alliance(alliance_id)

    if alliance is None:
        show_error(chat_id, message_id, "این اتحاد پیدا نشد.")
        return

    mine = get_user_alliance(user_id)

    if mine and mine["id"] == alliance["id"]:
        buttons = [[
            btn("✅ شما عضو این اتحاد هستید", "alliance_my")
        ]]
    elif mine:
        buttons = [[
            btn("ℹ️ شما عضو اتحاد دیگری هستید", "alliance_my")
        ]]
    else:
        buttons = [[
            btn(
                f"🤝 پیوستن به «{alliance['name']}»",
                f"alliance_join_{alliance['id']}",
            )
        ]]

    buttons.append([
        btn("🔙 بازگشت به اتحادهای موجود", "alliance_list_0")
    ])

    edit_or_send(
        chat_id,
        message_id,
        alliance_detail_text(alliance),
        inline(buttons),
    )


# ==============================
# خزانه و تاریخچه
# ==============================

def show_treasury(chat_id, user_id, message_id):
    alliance = get_user_alliance(user_id)

    if alliance is None:
        show_error(
            chat_id,
            message_id,
            "برای دیدن خزانه باید عضو یک اتحاد باشید.",
        )
        return

    user = database.get_or_create_user(user_id)

    connection = database.get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("""
            SELECT user_id, tx_type, amount, item_id, quantity
            FROM alliance_transactions
            WHERE alliance_id = ?
              AND tx_type IN ('donate', 'shop_buy')
            ORDER BY id DESC
            LIMIT 8
        """, (alliance["id"],))

        rows = cursor.fetchall()

    finally:
        connection.close()

    text = (
        f"💰 خزانه اتحاد «{alliance['name']}»\n\n"
        f"موجودی خزانه: {money(alliance['treasury'])}\n"
        f"پول شخصی شما: {money(user['budget'])}\n\n"
        "آخرین تراکنش‌ها:\n"
    )

    if not rows:
        text += "موردی ثبت نشده است."
    else:
        for row in rows:
            who = user_label(row[0]) if row[0] else "سیستم"

            if row[1] == "donate":
                text += (
                    f"➕ اهدا {money(row[2])} توسط {who}\n"
                )
            else:
                text += (
                    f"🛒 خرید {item_name(row[3])} × {row[4]}\n"
                    f"   مبلغ: {money(row[2])} | توسط: {who}\n"
                )

    edit_or_send(
        chat_id,
        message_id,
        text,
        inline([
            [btn("💸 اهدا به خزانه", "alliance_donate")],
            [btn("📜 تاریخچه کامل", "alliance_history")],
            back_row(),
        ]),
    )


def show_history(chat_id, user_id, message_id):
    alliance = get_user_alliance(user_id)

    if alliance is None:
        show_error(chat_id, message_id, "شما عضو هیچ اتحادی نیستید.")
        return

    connection = database.get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("""
            SELECT user_id, tx_type, amount, item_id, quantity
            FROM alliance_transactions
            WHERE alliance_id = ?
            ORDER BY id DESC
            LIMIT 20
        """, (alliance["id"],))

        rows = cursor.fetchall()

    finally:
        connection.close()

    labels = {
        "donate": "اهدا به خزانه",
        "shop_buy": "خرید از فروشگاه",
        "distribute": "توزیع تجهیزات",
        "join": "عضویت",
        "leave": "خروج",
        "create": "ایجاد اتحاد",
        "disband": "انحلال اتحاد",
        "transfer_leader": "انتقال رهبری",
    }

    text = f"📜 تاریخچه اتحاد «{alliance['name']}»\n\n"

    if not rows:
        text += "تاریخچه‌ای وجود ندارد."
    else:
        for row in rows:
            who = user_label(row[0]) if row[0] else "سیستم"
            label = labels.get(row[1], row[1])

            extra = []

            if row[2]:
                extra.append(f"مبلغ: {money(row[2])}")

            if row[3]:
                extra.append(
                    f"{item_name(row[3])} × {money(row[4])}"
                )

            suffix = " | ".join(extra)

            if suffix:
                text += f"• {label} — {who} | {suffix}\n"
            else:
                text += f"• {label} — {who}\n"

    edit_or_send(
        chat_id,
        message_id,
        text,
        inline([
            [btn("🔙 بازگشت به خزانه", "alliance_treasury")]
        ]),
    )


def start_donate(chat_id, user_id, message_id):
    alliance = get_user_alliance(user_id)

    if alliance is None:
        show_error(
            chat_id,
            message_id,
            "برای اهدا باید عضو یک اتحاد باشید.",
        )
        return

    user = database.get_or_create_user(user_id)

    set_waiting(user_id, "donate", message_id)

    send_input_prompt(
        chat_id,
        f"💸 اهدا به خزانه «{alliance['name']}»\n\n"
        f"پول شخصی شما: {money(user['budget'])}\n"
        f"موجودی خزانه: {money(alliance['treasury'])}\n\n"
        "مبلغ را در پاسخ به این پیام ارسال کنید.\n"
        "مثال: 500000\n\n"
        "برای انصراف: لغو",
        "مبلغ اهدا",
    )


# ==============================
# فروشگاه اتحاد
# ==============================

def show_shop(chat_id, user_id, message_id):
    alliance = get_user_alliance(user_id)

    if alliance is None:
        show_error(
            chat_id,
            message_id,
            "برای استفاده از فروشگاه اتحاد باید عضو یک اتحاد باشید.",
        )
        return

    if not is_leader(user_id):
        edit_or_send(
            chat_id,
            message_id,
            f"🛒 فروشگاه اتحاد «{alliance['name']}»\n\n"
            f"خزانه: {money(alliance['treasury'])}\n\n"
            "فقط رهبر می‌تواند از خزانه اتحاد خرید کند.",
            inline([back_row()]),
        )
        return

    text = (
        f"🛒 فروشگاه اتحاد «{alliance['name']}»\n\n"
        f"خزانه: {money(alliance['treasury'])}\n\n"
        "تجهیزات خریداری‌شده مستقیماً وارد انبار اتحاد می‌شود.\n\n"
        "یک مورد را انتخاب کنید:"
    )

    buttons = []

    for item_id, item in ALLIANCE_SHOP_ITEMS.items():
        buttons.append([
            btn(
                f"{item['name']} — {money(item['price'])}",
                f"alliance_shop_item_{item_id}",
            )
        ])

    buttons.append(back_row())

    edit_or_send(
        chat_id,
        message_id,
        text,
        inline(buttons),
    )


def show_shop_item(chat_id, user_id, message_id, item_id):
    item = ALLIANCE_SHOP_ITEMS.get(item_id)

    if item is None:
        show_error(chat_id, message_id, "آیتم نامعتبر است.")
        return

    alliance = get_user_alliance(user_id)

    if alliance is None:
        show_error(chat_id, message_id, "شما عضو هیچ اتحادی نیستید.")
        return

    if not is_leader(user_id):
        show_error(
            chat_id,
            message_id,
            "فقط رهبر می‌تواند خرید کند.",
        )
        return

    text = (
        f"🛒 خرید {item['name']}\n\n"
        f"قیمت هر واحد: {money(item['price'])}\n"
        f"خزانه: {money(alliance['treasury'])}\n\n"
        "تعداد را انتخاب کنید:"
    )

    qty_buttons = [
        btn(
            persian_number(qty),
            f"alliance_shop_buy_{item_id}_{qty}",
        )
        for qty in SHOP_QTY_LIST
    ]

    edit_or_send(
        chat_id,
        message_id,
        text,
        inline([
            qty_buttons[:2],
            qty_buttons[2:],
            [
                btn(
                    "✍️ تعداد دلخواه",
                    f"alliance_shop_custom_{item_id}",
                )
            ],
            [btn("🔙 بازگشت به فروشگاه", "alliance_shop")],
        ]),
    )


# ==============================
# انبار اتحاد
# ==============================

def show_warehouse(chat_id, user_id, message_id):
    alliance = get_user_alliance(user_id)

    if alliance is None:
        show_error(
            chat_id,
            message_id,
            "برای دیدن انبار باید عضو یک اتحاد باشید.",
        )
        return

    stock = get_warehouse(alliance["id"])
    count = member_count(alliance["id"])

    text = (
        f"📦 انبار اتحاد «{alliance['name']}»\n"
        f"👥 تعداد اعضا: {persian_number(count)}\n\n"
        f"{warehouse_text(stock)}\n\n"
    )

    buttons = []

    if is_leader(user_id):
        if stock:
            text += "یک تجهیزات را برای توزیع انتخاب کنید:"

            for item_id, quantity in stock.items():
                buttons.append([
                    btn(
                        f"{item_name(item_id)} × {money(quantity)}",
                        f"alliance_wh_item_{item_id}",
                    )
                ])
        else:
            text += "انبار خالی است."

            buttons.append([
                btn(
                    "🛒 رفتن به فروشگاه اتحاد",
                    "alliance_shop",
                )
            ])
    else:
        text += "فقط رهبر می‌تواند انبار را مدیریت کند."

    buttons.append(back_row())

    edit_or_send(
        chat_id,
        message_id,
        text,
        inline(buttons),
    )


def show_warehouse_item(chat_id, user_id, message_id, item_id):
    alliance = get_user_alliance(user_id)

    if alliance is None:
        show_error(chat_id, message_id, "شما عضو هیچ اتحادی نیستید.")
        return

    if not is_leader(user_id):
        show_error(
            chat_id,
            message_id,
            "فقط رهبر می‌تواند انبار را مدیریت کند.",
        )
        return

    if item_id not in ALLIANCE_SHOP_ITEMS:
        show_error(chat_id, message_id, "آیتم نامعتبر است.")
        return

    quantity = warehouse_qty(alliance["id"], item_id)
    count = member_count(alliance["id"])

    if quantity <= 0:
        show_error(chat_id, message_id, "این تجهیزات در انبار نیست.")
        return

    edit_or_send(
        chat_id,
        message_id,
        f"{item_name(item_id)} × {money(quantity)}\n\n"
        f"تعداد اعضای اتحاد: {persian_number(count)}\n"
        "تعداد تجهیزات برای توزیع باید حداقل به اندازه "
        "تعداد اعضای اتحاد باشد.",
        inline([
            [
                btn(
                    "📤 توزیع بین اعضا",
                    f"alliance_distribute_{item_id}",
                )
            ],
            [btn("🔙 بازگشت به انبار", "alliance_warehouse")],
        ]),
    )


def start_distribute(chat_id, user_id, message_id, item_id):
    alliance = get_user_alliance(user_id)

    if alliance is None:
        show_error(chat_id, message_id, "شما عضو هیچ اتحادی نیستید.")
        return

    if not is_leader(user_id):
        show_error(
            chat_id,
            message_id,
            "فقط رهبر می‌تواند توزیع کند.",
        )
        return

    if item_id not in ALLIANCE_SHOP_ITEMS:
        show_error(chat_id, message_id, "آیتم نامعتبر است.")
        return

    quantity = warehouse_qty(alliance["id"], item_id)
    count = member_count(alliance["id"])

    if quantity < count:
        edit_or_send(
            chat_id,
            message_id,
            "تعداد تجهیزات برای توزیع کافی نیست.\n"
            f"موجودی: {money(quantity)}\n"
            f"تعداد اعضا: {persian_number(count)}",
            inline([
                [btn("🔙 بازگشت به انبار", "alliance_warehouse")]
            ]),
        )
        return

    set_waiting(
        user_id,
        "distribute",
        message_id,
        {"item_id": item_id},
    )

    send_input_prompt(
        chat_id,
        f"📤 توزیع {item_name(item_id)}\n\n"
        f"موجودی انبار: {money(quantity)}\n"
        f"تعداد اعضا: {persian_number(count)}\n\n"
        "تعداد موردنظر را در پاسخ به این پیام ارسال کنید.\n"
        "تجهیزات تا حد ممکن مساوی تقسیم می‌شود.\n"
        "باقیمانده به اعضای اول می‌رسد.\n\n"
        "برای انصراف: لغو",
        "تعداد توزیع",
    )


# ==============================
# مدیریت اعضا
# ==============================

def show_manage(chat_id, user_id, message_id):
    alliance = get_user_alliance(user_id)

    if alliance is None:
        show_error(chat_id, message_id, "شما عضو هیچ اتحادی نیستید.")
        return

    members = get_members(alliance["id"])

    text = (
        f"👥 مدیریت اعضای اتحاد «{alliance['name']}»\n\n"
    )

    for member in members:
        if member["role"] == "leader":
            role = "👑 رهبر"
        else:
            role = "👤 عضو"

        text += (
            f"{role} — {user_label(member['user_id'])}\n"
        )

    buttons = []

    if is_leader(user_id):
        buttons.append([
            btn("👑 انتقال رهبری", "alliance_transfer_list")
        ])
        buttons.append([
            btn("💥 منحل کردن اتحاد", "alliance_disband_ask")
        ])
    else:
        buttons.append([
            btn("🚪 خروج از اتحاد", "alliance_leave_ask")
        ])

    buttons.append(back_row())

    edit_or_send(
        chat_id,
        message_id,
        text,
        inline(buttons),
    )


def show_transfer_list(chat_id, user_id, message_id):
    alliance = get_user_alliance(user_id)

    if alliance is None:
        show_error(chat_id, message_id, "شما عضو هیچ اتحادی نیستید.")
        return

    if not is_leader(user_id):
        show_error(
            chat_id,
            message_id,
            "فقط رهبر می‌تواند رهبری را منتقل کند.",
        )
        return

    members = [
        member
        for member in get_members(alliance["id"])
        if member["user_id"] != user_id
    ]

    if not members:
        edit_or_send(
            chat_id,
            message_id,
            "عضو دیگری برای انتقال رهبری وجود ندارد.\n"
            "اگر تنها عضو هستید، می‌توانید اتحاد را منحل کنید.",
            inline([
                [btn("💥 منحل کردن اتحاد", "alliance_disband_ask")],
                [btn("🔙 مدیریت اعضا", "alliance_manage")],
            ]),
        )
        return

    buttons = []

    for member in members:
        buttons.append([
            btn(
                f"👑 انتخاب {user_label(member['user_id'])}",
                f"alliance_transfer_{member['user_id']}",
            )
        ])

    buttons.append([
        btn("🔙 بازگشت به مدیریت", "alliance_manage")
    ])

    edit_or_send(
        chat_id,
        message_id,
        "👑 عضو جدید برای رهبری را انتخاب کنید:",
        inline(buttons),
    )


# ==============================
# مدیریت ورودی متنی
# ==============================

def handle_waiting_text(chat_id, user_id, text, message_id=None):
    session = waiting.get(user_id)

    if session is None:
        return False

    action = session.get("action")
    old_message_id = session.get("message_id")
    extra = session.get("extra") or {}

    if is_cancel_text(text):
        clear_waiting(user_id)

        show_alliance_menu(
            chat_id,
            user_id,
            old_message_id or message_id,
        )

        return True

    # ==============================
    # نام اتحاد
    # ==============================

    if action == "create_name":
        name = clean_name(text)

        if len(name) < 3:
            sent = send_input_prompt(
                chat_id,
                "❌ نام اتحاد باید حداقل ۳ کاراکتر باشد.\n"
                "نام جدید را در پاسخ به این پیام ارسال کنید.\n\n"
                "برای انصراف: لغو",
                "نام اتحاد",
            )

            prompt_message_id = get_sent_message_id(sent)

            if prompt_message_id:
                set_waiting(
                    user_id,
                    "create_name",
                    prompt_message_id,
                )

            return True

        if len(name) > 32:
            sent = send_input_prompt(
                chat_id,
                "❌ نام اتحاد نباید بیشتر از ۳۲ کاراکتر باشد.\n"
                "نام جدید را در پاسخ به این پیام ارسال کنید.\n\n"
                "برای انصراف: لغو",
                "نام اتحاد",
            )

            prompt_message_id = get_sent_message_id(sent)

            if prompt_message_id:
                set_waiting(
                    user_id,
                    "create_name",
                    prompt_message_id,
                )

            return True

        set_waiting(
            user_id,
            "create_tag",
            old_message_id,
            {"name": name},
        )

        edit_or_send(
            chat_id,
            old_message_id,
            f"🏰 نام اتحاد: «{name}»\n\n"
            "اگر تگ می‌خواهید، آن را ارسال کنید.\n"
            "اگر تگ نمی‌خواهید، روی «بدون تگ» بزنید.",
            inline([
                [btn("بدون تگ", "alliance_create_notag")],
                [btn("❌ لغو", "alliance_cancel")],
                back_row(),
            ]),
        )

        return True

    # ==============================
    # تگ اتحاد
    # ==============================

    if action == "create_tag":
        name = extra.get("name")

        if not name:
            clear_waiting(user_id)

            show_error(
                chat_id,
                old_message_id,
                "جلسه ساخت اتحاد نامعتبر است. دوباره تلاش کنید.",
            )

            return True

        tag = clean_tag(text)

        if not valid_tag(tag):
            edit_or_send(
                chat_id,
                old_message_id,
                "❌ تگ نامعتبر است.\n\n"
                "تگ باید بین ۲ تا ۱۶ کاراکتر و فقط شامل "
                "حروف، عدد یا _ باشد.\n\n"
                "تگ را دوباره ارسال کنید.",
                inline([
                    [btn("بدون تگ", "alliance_create_notag")],
                    [btn("❌ لغو", "alliance_cancel")],
                    back_row(),
                ]),
            )

            return True

        set_waiting(
            user_id,
            "create_confirm",
            old_message_id,
            {
                "name": name,
                "tag": tag,
            },
        )

        show_create_confirmation(
            chat_id,
            user_id,
            old_message_id,
            name,
            tag,
        )

        return True

    # ==============================
    # اهدا به خزانه
    # ==============================

    if action == "donate":
        amount = parse_positive_int(text)

        if amount is None:
            send_input_prompt(
                chat_id,
                "❌ مبلغ نامعتبر است.\n"
                "یک عدد بزرگ‌تر از صفر را در پاسخ به این پیام ارسال کنید.\n\n"
                "برای انصراف: لغو",
                "مبلغ اهدا",
            )

            return True

        ok, result = donate_to_treasury(
            user_id,
            amount,
        )

        if not ok:
            send_input_prompt(
                chat_id,
                f"❌ {result}\n\n"
                "مبلغ دیگری را در پاسخ به این پیام ارسال کنید.\n\n"
                "برای انصراف: لغو",
                "مبلغ اهدا",
            )

            return True

        clear_waiting(user_id)

        edit_or_send(
            chat_id,
            old_message_id,
            f"✅ مبلغ {money(result['amount'])} به خزانه "
            f"اتحاد «{result['name']}» اضافه شد.\n\n"
            f"💰 موجودی جدید خزانه: {money(result['treasury'])}",
            inline([
                [btn("💰 خزانه اتحاد", "alliance_treasury")],
                back_row(),
            ]),
        )

        return True

    # ==============================
    # خرید فروشگاه
    # ==============================

    if action == "shop_qty":
        quantity = parse_positive_int(text)
        item_id = extra.get("item_id")

        if quantity is None:
            send_input_prompt(
                chat_id,
                "❌ تعداد نامعتبر است.\n"
                "یک عدد بزرگ‌تر از صفر را در پاسخ به این پیام ارسال کنید.\n\n"
                "برای انصراف: لغو",
                "تعداد",
            )

            return True

        ok, result = buy_alliance_item(
            user_id,
            item_id,
            quantity,
        )

        if not ok:
            send_input_prompt(
                chat_id,
                f"❌ {result}\n\n"
                "تعداد دیگری را در پاسخ به این پیام ارسال کنید.\n\n"
                "برای انصراف: لغو",
                "تعداد",
            )

            return True

        clear_waiting(user_id)

        edit_or_send(
            chat_id,
            old_message_id,
            f"✅ {result['name']} × {money(result['quantity'])} "
            "خریداری شد و وارد انبار اتحاد شد.\n\n"
            f"💰 خزانه باقیمانده: {money(result['treasury'])}",
            inline([
                [btn("📦 انبار اتحاد", "alliance_warehouse")],
                [btn("🛒 فروشگاه اتحاد", "alliance_shop")],
                back_row(),
            ]),
        )

        return True

    # ==============================
    # توزیع
    # ==============================

    if action == "distribute":
        quantity = parse_positive_int(text)
        item_id = extra.get("item_id")

        if quantity is None:
            send_input_prompt(
                chat_id,
                "❌ تعداد نامعتبر است.\n"
                "یک عدد بزرگ‌تر از صفر را در پاسخ به این پیام ارسال کنید.\n\n"
                "برای انصراف: لغو",
                "تعداد توزیع",
            )

            return True

        ok, result = distribute_items(
            user_id,
            item_id,
            quantity,
        )

        if not ok:
            send_input_prompt(
                chat_id,
                f"❌ {result}\n\n"
                "تعداد دیگری را در پاسخ به این پیام ارسال کنید.\n\n"
                "برای انصراف: لغو",
                "تعداد توزیع",
            )

            return True

        clear_waiting(user_id)

        # اطلاعات اتحاد رهبر برای ارسال اعلان
        alliance = get_user_alliance(user_id)
        leader_id = user_id

        notify_alliance_members(
            alliance["id"],
            f"🎁 توزیع تجهیزات اتحاد\n\n"
            f"👑 رهبر اتحاد «{alliance['name']}»، کشور «{user_label(leader_id)}»، "
            f"به تمام کشورهای اتحاد تجهیزات اهدا کرد.\n\n"
            f"📦 {item_name(item_id)} × {money(quantity)}\n"
            "تجهیزات بین اعضای اتحاد توزیع شد."
        )

        text_out = (
            f"✅ توزیع {item_name(item_id)} انجام شد.\n"
            f"📦 مجموع: {money(quantity)}\n\n"
            "سهم اعضا:\n"
        )

        for member_id, share in result.items():
            text_out += (
                f"• {user_label(member_id)} → {money(share)}\n"
            )

        edit_or_send(
            chat_id,
            old_message_id,
            text_out,
            inline([
                [btn("📦 انبار اتحاد", "alliance_warehouse")],
                back_row(),
            ]),
        )

        return True

    return False


# ==============================
# پردازش Callback
# ==============================

def safe_int(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def handle_update(update):
    if not isinstance(update, dict):
        return

    # --------------------------
    # پیام متنی
    # --------------------------

    message = update.get("message")

    if message:
        chat = message.get("chat") or {}
        from_user = message.get("from") or {}

        chat_id = chat.get("id")
        user_id = from_user.get("id") or chat_id
        text = message.get("text")

        if chat_id and user_id and text:
            handle_waiting_text(
                chat_id,
                user_id,
                text,
                message.get("message_id"),
            )

    # --------------------------
    # Callback
    # --------------------------

    callback_query = update.get("callback_query")

    if not callback_query:
        return

    data = callback_query.get("data")

    if not data:
        return

    if data != "alliance" and not data.startswith("alliance_"):
        return

    message = callback_query.get("message") or {}
    chat = message.get("chat") or {}
    from_user = callback_query.get("from") or {}

    chat_id = chat.get("id")
    message_id = message.get("message_id")
    user_id = from_user.get("id") or chat_id

    if not chat_id or not message_id or not user_id:
        return

    # --------------------------
    # منوی اتحاد
    # --------------------------

    if data == "alliance":
        show_alliance_menu(
            chat_id,
            user_id,
            message_id,
        )
        return

    # --------------------------
    # لغو
    # --------------------------

    if data == "alliance_cancel":
        clear_waiting(user_id)

        show_alliance_menu(
            chat_id,
            user_id,
            message_id,
        )

        return

    # --------------------------
    # ساخت اتحاد
    # --------------------------

    if data == "alliance_create":
        start_create(
            chat_id,
            user_id,
            message_id,
        )
        return

    # --------------------------
    # ساخت اتحاد بدون تگ
    # --------------------------

    if data == "alliance_create_notag":
        session = waiting.get(user_id)

        if not session or session.get("action") != "create_tag":
            show_error(
                chat_id,
                message_id,
                "جلسه ساخت اتحاد تمام شده است.",
            )
            return

        name = (session.get("extra") or {}).get("name")

        if not name:
            clear_waiting(user_id)

            show_error(
                chat_id,
                message_id,
                "جلسه ساخت اتحاد نامعتبر است. دوباره تلاش کنید.",
            )

            return

        set_waiting(
            user_id,
            "create_confirm",
            message_id,
            {
                "name": name,
                "tag": None,
            },
        )

        show_create_confirmation(
            chat_id,
            user_id,
            message_id,
            name,
            None,
        )

        return

    # --------------------------
    # تأیید ساخت اتحاد و پرداخت
    # --------------------------

    if data == "alliance_create_confirm":
        session = waiting.get(user_id)

        if not session or session.get("action") != "create_confirm":
            show_error(
                chat_id,
                message_id,
                "جلسه ساخت اتحاد تمام شده است. دوباره تلاش کنید.",
            )
            return

        extra = session.get("extra") or {}

        name = extra.get("name")
        tag = extra.get("tag")

        if not name:
            clear_waiting(user_id)

            show_error(
                chat_id,
                message_id,
                "اطلاعات ساخت اتحاد ناقص است.",
            )

            return

        ok, result = create_alliance(
            user_id,
            name,
            tag,
        )

        if not ok:
            clear_waiting(user_id)

            edit_or_send(
                chat_id,
                message_id,
                f"❌ ساخت اتحاد انجام نشد.\n\n{result}",
                inline([
                    [btn("🏰 ساخت اتحاد دوباره", "alliance_create")],
                    back_row(),
                ]),
            )

            return

        clear_waiting(user_id)

        edit_or_send(
            chat_id,
            message_id,
            f"✅ اتحاد «{result}» با موفقیت ساخته شد.\n\n"
            f"💰 مبلغ {money(ALLIANCE_CREATE_COST)} دلار از بودجه شما کسر شد.\n"
            "👑 شما رهبر اتحاد هستید.",
            alliance_menu_keyboard(
                is_member=True,
                is_leader=True,
            ),
        )

        return

    # --------------------------
    # اتحاد من
    # --------------------------

    if data == "alliance_my":
        show_my_alliance(
            chat_id,
            user_id,
            message_id,
        )
        return

    # --------------------------
    # لیست اتحادها
    # --------------------------

    if data.startswith("alliance_list_"):
        page = safe_int(
            data[len("alliance_list_"):]
        )

        if page is None:
            show_error(
                chat_id,
                message_id,
                "صفحه نامعتبر است.",
            )
            return

        show_alliance_list(
            chat_id,
            user_id,
            message_id,
            page,
        )
        return

    # --------------------------
    # مشاهده اتحاد
    # --------------------------

    if data.startswith("alliance_view_"):
        alliance_id = safe_int(
            data[len("alliance_view_"):]
        )

        if alliance_id is None:
            show_error(
                chat_id,
                message_id,
                "شناسه اتحاد نامعتبر است.",
            )
            return

        show_alliance_view(
            chat_id,
            user_id,
            message_id,
            alliance_id,
        )
        return

    # --------------------------
    # ورود به اتحاد
    # --------------------------

    if data.startswith("alliance_join_"):
        alliance_id = safe_int(
            data[len("alliance_join_"):]
        )

        if alliance_id is None:
            show_error(
                chat_id,
                message_id,
                "شناسه اتحاد نامعتبر است.",
            )
            return

        ok, result = join_alliance(
            user_id,
            alliance_id,
        )

        if not ok:
            show_error(
                chat_id,
                message_id,
                result,
            )
            return

        edit_or_send(
            chat_id,
            message_id,
            f"✅ شما با موفقیت وارد اتحاد «{result}» شدید.",
            inline([
                [btn("🤝 اتحاد من", "alliance_my")],
                back_row(),
            ]),
        )
        return

    # --------------------------
    # خروج از اتحاد
    # --------------------------

    if data == "alliance_leave_ask":
        if get_user_alliance(user_id) is None:
            show_error(
                chat_id,
                message_id,
                "شما عضو هیچ اتحادی نیستید.",
            )
            return

        edit_or_send(
            chat_id,
            message_id,
            "⚠️ آیا مطمئن هستید که می‌خواهید از اتحاد خارج شوید؟",
            inline([
                [btn("✅ بله، خارج می‌شوم", "alliance_leave")],
                [btn("🔙 انصراف", "alliance_my")],
            ]),
        )
        return

    if data == "alliance_leave":
        ok, result = leave_alliance(user_id)

        if not ok:
            show_error(
                chat_id,
                message_id,
                result,
            )
            return

        edit_or_send(
            chat_id,
            message_id,
            f"✅ شما از اتحاد «{result}» خارج شدید.",
            alliance_menu_keyboard(
                is_member=False,
                is_leader=False,
            ),
        )
        return

    # --------------------------
    # انحلال اتحاد
    # --------------------------

    if data == "alliance_disband_ask":
        if not is_leader(user_id):
            show_error(
                chat_id,
                message_id,
                "فقط رهبر می‌تواند اتحاد را منحل کند.",
            )
            return

        edit_or_send(
            chat_id,
            message_id,
            "⚠️ آیا مطمئن هستید اتحاد منحل شود?\n"
            "این کار قابل برگشت نیست.",
            inline([
                [btn("💥 بله، منحل شود", "alliance_disband")],
                [btn("🔙 انصراف", "alliance_manage")],
            ]),
        )
        return

    if data == "alliance_disband":
        ok, result = disband_alliance(user_id)

        if not ok:
            show_error(
                chat_id,
                message_id,
                result,
            )
            return

        edit_or_send(
            chat_id,
            message_id,
            f"✅ اتحاد «{result}» منحل شد.",
            alliance_menu_keyboard(
                is_member=False,
                is_leader=False,
            ),
        )
        return

    # --------------------------
    # انتقال رهبری
    # --------------------------

    if data == "alliance_transfer_list":
        show_transfer_list(
            chat_id,
            user_id,
            message_id,
        )
        return

    if data.startswith("alliance_transfer_"):
        new_leader_id = safe_int(
            data[len("alliance_transfer_"):]
        )

        if new_leader_id is None:
            show_error(
                chat_id,
                message_id,
                "شناسه بازیکن نامعتبر است.",
            )
            return

        ok, result = transfer_leadership(
            user_id,
            new_leader_id,
        )

        if not ok:
            show_error(
                chat_id,
                message_id,
                result,
            )
            return

        edit_or_send(
            chat_id,
            message_id,
            f"✅ رهبری اتحاد «{result}» به "
            f"{user_label(new_leader_id)} منتقل شد.",
            inline([
                [btn("🤝 اتحاد من", "alliance_my")],
                back_row(),
            ]),
        )
        return

    # --------------------------
    # خزانه
    # --------------------------

    if data == "alliance_treasury":
        show_treasury(
            chat_id,
            user_id,
            message_id,
        )
        return

    if data == "alliance_history":
        show_history(
            chat_id,
            user_id,
            message_id,
        )
        return

    if data == "alliance_donate":
        start_donate(
            chat_id,
            user_id,
            message_id,
        )
        return

    # --------------------------
    # فروشگاه
    # --------------------------

    if data == "alliance_shop":
        show_shop(
            chat_id,
            user_id,
            message_id,
        )
        return

    if data.startswith("alliance_shop_item_"):
        item_id = data[len("alliance_shop_item_"):]

        show_shop_item(
            chat_id,
            user_id,
            message_id,
            item_id,
        )
        return

    if data.startswith("alliance_shop_custom_"):
        item_id = data[len("alliance_shop_custom_"):]

        if item_id not in ALLIANCE_SHOP_ITEMS:
            show_error(
                chat_id,
                message_id,
                "آیتم نامعتبر است.",
            )
            return

        if not is_leader(user_id):
            show_error(
                chat_id,
                message_id,
                "فقط رهبر می‌تواند خرید کند.",
            )
            return

        set_waiting(
            user_id,
            "shop_qty",
            message_id,
            {"item_id": item_id},
        )

        send_input_prompt(
            chat_id,
            f"✍️ تعداد خرید {item_name(item_id)} را "
            "در پاسخ به این پیام ارسال کنید.\n\n"
            "برای انصراف: لغو",
            "تعداد خرید",
        )
        return

    if data.startswith("alliance_shop_buy_"):
        rest = data[len("alliance_shop_buy_"):]

        if "_" not in rest:
            show_error(
                chat_id,
                message_id,
                "درخواست خرید نامعتبر است.",
            )
            return

        item_id, quantity_text = rest.rsplit("_", 1)
        quantity = safe_int(quantity_text)

        if quantity is None:
            show_error(
                chat_id,
                message_id,
                "تعداد خرید نامعتبر است.",
            )
            return

        ok, result = buy_alliance_item(
            user_id,
            item_id,
            quantity,
        )

        if not ok:
            show_error(
                chat_id,
                message_id,
                result,
            )
            return

        edit_or_send(
            chat_id,
            message_id,
            f"✅ {result['name']} × {money(result['quantity'])} "
            "خریداری شد و وارد انبار اتحاد شد.\n\n"
            f"💰 خزانه باقیمانده: {money(result['treasury'])}",
            inline([
                [btn("📦 انبار اتحاد", "alliance_warehouse")],
                [btn("🛒 فروشگاه اتحاد", "alliance_shop")],
                back_row(),
            ]),
        )
        return

    # --------------------------
    # انبار
    # --------------------------

    if data == "alliance_warehouse":
        show_warehouse(
            chat_id,
            user_id,
            message_id,
        )
        return

    if data.startswith("alliance_wh_item_"):
        item_id = data[len("alliance_wh_item_"):]

        show_warehouse_item(
            chat_id,
            user_id,
            message_id,
            item_id,
        )
        return

    if data.startswith("alliance_distribute_"):
        item_id = data[len("alliance_distribute_"):]

        start_distribute(
            chat_id,
            user_id,
            message_id,
            item_id,
        )
        return

    # --------------------------
    # مدیریت اعضا
    # --------------------------

    if data == "alliance_manage":
        show_manage(
            chat_id,
            user_id,
            message_id,
        )
        return
