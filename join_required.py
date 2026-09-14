# ==============================
# World War - Join Required
# ==============================

import config


# ==============================
# اتصال به Bot
# ==============================

send_message = None
edit_message = None
api_request = None


def setup(send_func, edit_func, api_func):
    global send_message
    global edit_message
    global api_request

    send_message = send_func
    edit_message = edit_func
    api_request = api_func


# ==============================
# کیبورد جوین اجباری
# ==============================

def join_keyboard():
    return {
        "inline_keyboard": [
            [
                {
                    "text": "📢 کانال بات",
                    "url": f"https://ble.ir/{config.REQUIRED_CHANNEL.lstrip('@')}"
                }
            ],
            [
                {
                    "text": "👥 گروه بات",
                    "url": f"https://ble.ir/{config.REQUIRED_GROUP.lstrip('@')}"
                }
            ]
        ]
    }


# ==============================
# بررسی عضویت کاربر
# ==============================

def check_member(chat_id, user_id):

    result = api_request(
        "getChatMember",
        {
            "chat_id": chat_id,
            "user_id": user_id
        }
    )

    if not result:
        print(
            f"Join Check Error: "
            f"no response | chat={chat_id} | user={user_id}"
        )
        return False

    if result.get("ok") is not True:
        print(
            f"Join Check Error: "
            f"API failed | chat={chat_id} | "
            f"user={user_id} | result={result}"
        )
        return False

    member = result.get("result")

    if not member:
        print(
            f"Join Check Error: "
            f"member data not found | chat={chat_id} | "
            f"user={user_id}"
        )
        return False

    status = member.get("status")

    # ==============================
    # وضعیت‌های قابل قبول
    # ==============================

    if status in [
        "creator",
        "administrator",
        "member"
    ]:
        return True

    # ==============================
    # کاربر Restricted ولی عضو است
    # ==============================

    if status == "restricted":

        if member.get("is_member") is True:
            return True

        return False

    # ==============================
    # کاربر عضو نیست
    # ==============================

    return False


# ==============================
# بررسی عضویت در کانال و گروه
# ==============================

def is_user_joined(user_id):

    channel = getattr(
        config,
        "REQUIRED_CHANNEL",
        None
    )

    group = getattr(
        config,
        "REQUIRED_GROUP",
        None
    )

    # ==============================
    # بررسی تنظیمات
    # ==============================

    if not channel or not group:

        print(
            "Join Required Error: "
            "REQUIRED_CHANNEL or REQUIRED_GROUP "
            "is not configured."
        )

        return False

    # ==============================
    # بررسی کانال
    # ==============================

    channel_joined = check_member(
        channel,
        user_id
    )

    # اگر کانال عضو نیست، نیازی به بررسی گروه نیست
    if not channel_joined:
        return False

    # ==============================
    # بررسی گروه
    # ==============================

    group_joined = check_member(
        group,
        user_id
    )

    if not group_joined:
        return False

    # ==============================
    # هر دو عضو هستند
    # ==============================

    return True


# ==============================
# پیام جوین اجباری
# ==============================

def send_join_required(chat_id):

    send_message(
        chat_id,
        "🔒 دسترسی به ربات\n\n"
        "برای استفاده از ربات باید در کانال و گروه بات عضو شوید.\n\n"
        "📢 کانال بات\n"
        "👥 گروه بات\n\n"
        "بعد از عضویت، برای تایید عضویت دوباره /start را بزنید.",
        join_keyboard()
    )


# ==============================
# بررسی Start
# ==============================

def handle_start(chat_id, user_id):

    # ==============================
    # کاربر عضو هر دو است
    # ==============================

    if is_user_joined(user_id):
        return True

    # ==============================
    # کاربر عضو نیست
    # ==============================

    send_join_required(chat_id)

    return False


# ==============================
# دریافت آپدیت‌ها
# ==============================

def handle_update(update):

    # فقط پیام‌ها
    if "message" not in update:
        return

    message = update["message"]

    chat_id = message["chat"]["id"]
    user_id = message["from"]["id"]

    text = message.get("text", "").strip()

    # ==============================
    # فقط /start
    # ==============================

    if text == "/start":

        handle_start(
            chat_id,
            user_id
        )