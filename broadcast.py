import config

send_message = None
edit_message = None

# وضعیت موقت ادمین‌ها
admin_sessions = {}


def setup(send_message_function, edit_message_function):
    global send_message
    global edit_message

    send_message = send_message_function
    edit_message = edit_message_function


def is_admin(user_id):
    return user_id in getattr(config, "ADMINS", [])


# =========================================================
# شروع پیام همگانی
# =========================================================

def start_broadcast(chat_id, message_id):

    if not is_admin(chat_id):
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
# نمایش پیش‌نمایش
# =========================================================

def show_preview(chat_id, message):

    if not is_admin(chat_id):
        return

    session = admin_sessions.get(chat_id)

    if not session:
        return

    session["message"] = message
    session["state"] = "preview"

    # -----------------------------------------------------
    # پیام متنی
    # -----------------------------------------------------

    text = message.get("text")

    if text:

        preview_text = (
            "📢 پیش‌نمایش پیام\n\n"
            f"{text}\n\n"
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

        return

    # -----------------------------------------------------
    # پیام غیرمتنی / فورواردی
    # -----------------------------------------------------

    preview_text = (
        "📢 پیش‌نمایش پیام\n\n"
        "پیام دریافت شد.\n\n"
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

    # برای پیام‌های غیرمتنی فعلاً یک پیام متنی
    # برای پیش‌نمایش نشان داده می‌شود.
    edit_message(
        chat_id,
        session["message_id"],
        preview_text,
        keyboard
    )


# =========================================================
# دریافت پیام ادمین
# =========================================================

def handle_message(chat_id, message):

    if not is_admin(chat_id):
        return False

    session = admin_sessions.get(chat_id)

    if not session:
        return False

    if session.get("state") != "waiting_message":
        return False

    show_preview(
        chat_id,
        message
    )

    return True


# =========================================================
# مدیریت Callback
# =========================================================

def handle_callback(chat_id, message_id, callback_data):

    if not is_admin(chat_id):
        return False

    # -----------------------------------------------------
    # ورود به پیام همگانی
    # -----------------------------------------------------

    if callback_data == "admin_broadcast":

        start_broadcast(
            chat_id,
            message_id
        )

        return True

    # -----------------------------------------------------
    # لغو
    # -----------------------------------------------------

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

    # -----------------------------------------------------
    # ارسال
    # -----------------------------------------------------

    if callback_data == "broadcast_send":

        # فعلاً ارسال واقعی را فعال نمی‌کنیم.
        # در مرحله بعد سیستم ارسال سریع و Background اضافه می‌شود.

        return True

    return False
