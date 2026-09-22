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


def handle_callback(chat_id, message_id, callback_data):
    if not is_admin(chat_id):
        return False

    if callback_data == "admin_broadcast":
        start_broadcast(chat_id, message_id)
        return True

    if callback_data == "broadcast_cancel":
        admin_sessions.pop(chat_id, None)
        return True

    return False


def handle_message(chat_id, message):
    if not is_admin(chat_id):
        return False

    session = admin_sessions.get(chat_id)

    if not session:
        return False

    if session.get("state") != "waiting_message":
        return False

    # فعلاً فقط پیام را ذخیره می‌کنیم.
    # مرحله بعد، تشخیص متن / فوروارد و پیش‌نمایش را اضافه می‌کنیم.
    session["message"] = message
    session["state"] = "preview"

    return True
