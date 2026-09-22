import config

send_message = None
edit_message = None


# ==============================
# اتصال به bot.py
# ==============================

def setup(send_message_function, edit_message_function):
    global send_message
    global edit_message

    send_message = send_message_function
    edit_message = edit_message_function


# ==============================
# بررسی ادمین بودن
# ==============================

def is_admin(user_id):
    return user_id in getattr(config, "ADMINS", [])


# ==============================
# نمایش پنل مدیریت
# ==============================

def show_admin_panel(chat_id, message_id):
    if not is_admin(chat_id):
        return

    text = (
        "⚙️ پنل مدیریت\n\n"
        "یکی از گزینه‌های زیر را انتخاب کنید:"
    )

    keyboard = [
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

    edit_message(
        chat_id,
        message_id,
        text,
        keyboard
    )


# ==============================
# مدیریت Callback پنل
# ==============================

def handle_callback(chat_id, message_id, callback_data):
    if callback_data == "admin_panel":
        show_admin_panel(chat_id, message_id)
        return True

    return False
