import config
import database
import threading
import requests

from concurrent.futures import ThreadPoolExecutor, as_completed
from config import BOT_TOKEN, API_URL


send_message = None
edit_message = None

admin_sessions = {}

# =========================================================
# تنظیمات سرعت ارسال همگانی
# =========================================================

BROADCAST_WORKERS = 8


# =========================================================
# Session مستقل Broadcast
# =========================================================

BROADCAST_SESSION = requests.Session()

BROADCAST_SESSION.headers.update({
    "Content-Type": "application/json"
})


def setup(send_message_function, edit_message_function):

    global send_message
    global edit_message

    send_message = send_message_function
    edit_message = edit_message_function


def is_admin(user_id):

    return user_id in getattr(
        config,
        "ADMINS",
        []
    )


# =========================================================
# API مستقل Broadcast
# =========================================================

def broadcast_api_request(method, data=None):

    url = f"{API_URL}/{method}"

    try:

        response = BROADCAST_SESSION.post(
            url,
            json=data or {},
            timeout=(5, 35)
        )

        response.raise_for_status()

        return response.json()

    except Exception as error:

        print(
            f"Broadcast API Error [{method}]: {error}"
        )

        return None


# =========================================================
# گرفتن کاربران
# =========================================================

def get_all_users():

    try:

        connection = database.get_connection()

        cursor = connection.cursor()

        cursor.execute(
            "SELECT user_id FROM users"
        )

        rows = cursor.fetchall()

        connection.close()

        users = []

        for row in rows:

            if isinstance(row, dict):

                user_id = row.get(
                    "user_id"
                )

            else:

                user_id = row[0]

            if user_id is not None:

                users.append(
                    user_id
                )

        return users

    except Exception as error:

        print(
            f"Broadcast Database Error: {error}"
        )

        return []


# =========================================================
# ارسال متن
# =========================================================

def send_text_to_user(
    user_id,
    text
):

    return broadcast_api_request(
        "sendMessage",
        {
            "chat_id": user_id,
            "text": text
        }
    )


# =========================================================
# ارسال Forward
# =========================================================

def forward_message_to_user(
    user_id,
    from_chat_id,
    message_id
):

    return broadcast_api_request(
        "forwardMessage",
        {
            "chat_id": user_id,
            "from_chat_id": from_chat_id,
            "message_id": message_id
        }
    )


# =========================================================
# تشخیص Forward
# =========================================================

def is_forwarded_message(message):

    if not isinstance(
        message,
        dict
    ):

        return False

    forward_keys = [
        "forward_from",
        "forward_from_chat",
        "forward_from_message_id",
        "forward_date",
        "forward_origin"
    ]

    for key in forward_keys:

        if key in message:

            return True

    return False


# =========================================================
# ارسال یک کاربر
# =========================================================

def send_to_user(
    user_id,
    text,
    forwarded,
    from_chat_id,
    message_id
):

    try:

        # -------------------------------------------------
        # Forward
        # -------------------------------------------------

        if forwarded:

            result = forward_message_to_user(
                user_id,
                from_chat_id,
                message_id
            )

        # -------------------------------------------------
        # متن معمولی
        # -------------------------------------------------

        elif text is not None:

            result = send_text_to_user(
                user_id,
                text
            )

        # -------------------------------------------------
        # سایر پیام‌ها
        # -------------------------------------------------

        else:

            result = forward_message_to_user(
                user_id,
                from_chat_id,
                message_id
            )

        # -------------------------------------------------
        # نتیجه واقعی API
        # -------------------------------------------------

        if (
            isinstance(result, dict)
            and result.get("ok") is True
        ):

            return True

        return False

    except Exception as error:

        print(
            f"Broadcast user error "
            f"[{user_id}]: {error}"
        )

        return False


# =========================================================
# ارسال همگانی در Background
# =========================================================

def broadcast_worker(
    message,
    admin_chat_id,
    admin_message_id
):

    users = get_all_users()

    total_users = len(
        users
    )

    # =====================================================
    # بدون کاربر
    # =====================================================

    if not users:

        try:

            edit_message(
                admin_chat_id,
                admin_message_id,
                "📢 ارسال همگانی تمام شد\n\n"
                "👥 تعداد کاربران: ۰\n\n"
                "✅ ارسال موفق: ۰ کاربر\n"
                "❌ ارسال ناموفق: ۰ کاربر"
            )

        except Exception as error:

            print(
                f"Broadcast final edit error: {error}"
            )

        return


    # =====================================================
    # اطلاعات پیام
    # =====================================================

    text = message.get(
        "text"
    )

    message_chat = message.get(
        "chat",
        {}
    )

    from_chat_id = message_chat.get(
        "id"
    )

    message_id = message.get(
        "message_id"
    )

    forwarded = is_forwarded_message(
        message
    )


    # =====================================================
    # نمایش وضعیت
    # =====================================================

    try:

        edit_message(
            admin_chat_id,
            admin_message_id,
            "📢 پیام همگانی\n\n"
            f"📨 پیام برای {total_users:,} کاربر "
            "درحال ارسال می‌باشد..."
        )

    except Exception as error:

        print(
            f"Broadcast progress edit error: {error}"
        )


    # =====================================================
    # ارسال همزمان
    # =====================================================

    sent = 0
    failed = 0

    with ThreadPoolExecutor(
        max_workers=BROADCAST_WORKERS
    ) as executor:

        futures = []

        for user_id in users:

            future = executor.submit(
                send_to_user,
                user_id,
                text,
                forwarded,
                from_chat_id,
                message_id
            )

            futures.append(
                future
            )


        # =================================================
        # دریافت نتیجه‌ها
        # =================================================

        for future in as_completed(
            futures
        ):

            try:

                result = future.result()

                if result:

                    sent += 1

                else:

                    failed += 1

            except Exception as error:

                failed += 1

                print(
                    f"Broadcast worker error: "
                    f"{error}"
                )


    # =====================================================
    # پایان ارسال
    # =====================================================

    try:

        edit_message(
            admin_chat_id,
            admin_message_id,
            "📢 ارسال همگانی تمام شد\n\n"
            f"👥 تعداد کل کاربران: {total_users:,}\n\n"
            f"✅ ارسال موفق: {sent:,} کاربر\n"
            f"❌ ارسال ناموفق: {failed:,} کاربر"
        )

    except Exception as error:

        print(
            f"Broadcast final edit error: {error}"
        )


    print(
        f"Broadcast finished | "
        f"Total: {total_users} | "
        f"Sent: {sent} | "
        f"Failed: {failed}"
    )


# =========================================================
# شروع پیام همگانی
# =========================================================

def start_broadcast(
    chat_id,
    message_id
):

    if not is_admin(
        chat_id
    ):

        return


    admin_sessions[chat_id] = {

        "state": "waiting_message",

        "message_id": message_id

    }


    text = (

        "📢 پیام همگانی\n\n"

        "پیام موردنظر برای ارسال به کاربران را بفرستید.\n\n"

        "می‌توانید متن معمولی یا یک پیام فورواردشده ارسال کنید."

    )


    keyboard = [

        [

            {

                "text": "🔙 برگشت",

                "callback_data": "back_admin_panel"

            }

        ]

    ]


    edit_message(
        chat_id,
        message_id,
        text,
        keyboard
    )


# =========================================================
# پیش‌نمایش
# =========================================================

def show_preview(
    chat_id,
    message
):

    if not is_admin(
        chat_id
    ):

        return


    session = admin_sessions.get(
        chat_id
    )


    if not session:

        return


    session["message"] = message

    session["state"] = "preview"


    text = message.get(
        "text"
    )


    if (
        text
        and not is_forwarded_message(message)
    ):

        preview_text = (

            "📢 پیش‌نمایش پیام\n\n"

            f"{text}\n\n"

            "آیا پیام برای همه کاربران ارسال شود؟"

        )

    else:

        preview_text = (

            "📢 پیش‌نمایش پیام\n\n"

            "📨 پیام فورواردی دریافت شد.\n\n"

            "آیا پیام برای همه کاربران ارسال شود؟"

        )


    keyboard = [

        [

            {

                "text": "✅ ارسال",

                "callback_data": "broadcast_send"

            },

            {

                "text": "❌ لغو",

                "callback_data": "broadcast_cancel"

            }

        ]

    ]


    edit_message(
        chat_id,
        session["message_id"],
        preview_text,
        keyboard
    )


# =========================================================
# دریافت پیام
# =========================================================

def handle_message(
    chat_id,
    message
):

    if not is_admin(
        chat_id
    ):

        return False


    session = admin_sessions.get(
        chat_id
    )


    if not session:

        return False


    if session.get(
        "state"
    ) != "waiting_message":

        return False


    show_preview(
        chat_id,
        message
    )


    return True


# =========================================================
# Callback
# =========================================================

def handle_callback(
    chat_id,
    message_id,
    callback_data
):

    if not is_admin(
        chat_id
    ):

        return False


    # =====================================================
    # ورود
    # =====================================================

    if callback_data == "admin_broadcast":

        start_broadcast(
            chat_id,
            message_id
        )

        return True


    # =====================================================
    # لغو
    # =====================================================

    if callback_data == "broadcast_cancel":

        admin_sessions.pop(
            chat_id,
            None
        )


        edit_message(
            chat_id,
            message_id,
            "⚙️ پنل مدیریت\n\n"
            "یکی از گزینه‌های زیر را انتخاب کنید:",
            [

                [

                    {

                        "text": "📊 آمار ربات",

                        "callback_data": "admin_stats"

                    }

                ],

                [

                    {

                        "text": "📢 پیام همگانی",

                        "callback_data": "admin_broadcast"

                    }

                ],

                [

                    {

                        "text": "👥 کاربران ربات",

                        "callback_data": "admin_users"

                    }

                ],

                [

                    {

                        "text": "🚷 کاربران بن شده",

                        "callback_data": "admin_banned"

                    }

                ],

                [

                    {

                        "text": "👑 مدیریت ادمین‌ها",

                        "callback_data": "admin_admins"

                    }

                ],

                [

                    {

                        "text": "⚙️ تنظیمات ربات",

                        "callback_data": "admin_settings"

                    }

                ],

                [

                    {

                        "text": "🔙 برگشت",

                        "callback_data": "back_main_menu"

                    }

                ]

            ]
        )


        return True


    # =====================================================
    # ارسال
    # =====================================================

    if callback_data == "broadcast_send":

        session = admin_sessions.get(
            chat_id
        )


        if not session:

            return True


        message = session.get(
            "message"
        )


        if not message:

            return True


        session["state"] = "sending"


        # شناسه پیام ادمین
        admin_message_id = message_id


        # تعداد کاربران
        users = get_all_users()

        total_users = len(
            users
        )


        edit_message(
            chat_id,
            message_id,
            "📢 پیام همگانی\n\n"
            f"📨 پیام برای {total_users:,} کاربر "
            "درحال ارسال می‌باشد..."
        )


        admin_sessions.pop(
            chat_id,
            None
        )


        # =================================================
        # Background Thread
        # =================================================

        worker = threading.Thread(

            target=broadcast_worker,

            args=(

                message,

                chat_id,

                admin_message_id

            ),

            daemon=True

        )


        worker.start()


        return True


    return False
