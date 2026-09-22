import config
import database


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
# نمایش آمار ربات
# ==============================

def show_admin_stats(chat_id, message_id):
    if not is_admin(chat_id):
        return

    stats = database.get_bot_stats()

    text = (
        "📊 آمار ربات\n\n"

        "👥 کاربران\n"
        f"├ کل کاربران: {stats['total_users']:,}\n"
        f"├ امروز: {stats['users_today']:,}\n"
        f"├ ۷ روز اخیر: {stats['users_7_days']:,}\n"
        f"└ ۳۰ روز اخیر: {stats['users_30_days']:,}\n\n"

        "🌍 کشورها\n"
        f"├ کشورهای انتخاب‌شده: {stats['selected_countries']:,}\n"
        f"├ بدون کشور: {stats['users_without_country']:,}\n"
        f"└ انتخاب کشور در ۲۴ ساعت اخیر: "
        f"{stats['countries_selected_24h']:,}\n\n"

        "📈 وضعیت کاربران\n"
        f"├ دارای کشور: {stats['selected_countries']:,}\n"
        f"└ بدون کشور: {stats['users_without_country']:,}\n\n"

        "👤 کاربران فعال\n"
        f"├ امروز: {stats['active_today']:,}\n"
        f"└ ۷ روز گذشته: {stats['active_7_days']:,}\n\n"

        "🕐 آخرین بروزرسانی:\n"
        "همین الان"
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


# ==============================
# پیام همگانی
# ==============================

def show_admin_broadcast(chat_id, message_id):
    if not is_admin(chat_id):
        return

    text = (
        "📢 پیام همگانی\n\n"
        "این بخش برای ارسال پیام به کاربران ربات است."
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


# ==============================
# کاربران ربات
# ==============================

def show_admin_users(chat_id, message_id):
    if not is_admin(chat_id):
        return

    stats = database.get_bot_stats()

    text = (
        "👥 کاربران ربات\n\n"
        f"کل کاربران: {stats['total_users']:,}\n"
        f"دارای کشور: {stats['selected_countries']:,}\n"
        f"بدون کشور: {stats['users_without_country']:,}\n\n"
        "برای مدیریت کاربران از بخش‌های مربوطه استفاده کنید."
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


# ==============================
# کاربران بن شده
# ==============================

def show_admin_banned(chat_id, message_id):
    if not is_admin(chat_id):
        return

    text = (
        "🚷 کاربران بن شده\n\n"
        "مدیریت کاربران بن شده در این بخش انجام می‌شود."
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


# ==============================
# مدیریت ادمین‌ها
# ==============================

def show_admin_admins(chat_id, message_id):
    if not is_admin(chat_id):
        return

    admins = getattr(config, "ADMINS", [])

    text = (
        "👑 مدیریت ادمین‌ها\n\n"
        f"تعداد ادمین‌ها: {len(admins)}\n\n"
        "ادمین‌های فعلی:\n"
    )

    for admin_id in admins:
        text += f"• {admin_id}\n"

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


# ==============================
# تنظیمات ربات
# ==============================

def show_admin_settings(chat_id, message_id):
    if not is_admin(chat_id):
        return

    text = (
        "⚙️ تنظیمات ربات\n\n"
        "بخش تنظیمات ربات آماده مدیریت است."
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


# ==============================
# مدیریت Callback پنل
# ==============================

def handle_callback(chat_id, message_id, callback_data):

    if not is_admin(chat_id):
        return False

    # پنل اصلی
    if callback_data == "admin_panel":
        show_admin_panel(chat_id, message_id)
        return True

    # آمار
    if callback_data == "admin_stats":
        show_admin_stats(chat_id, message_id)
        return True

    # پیام همگانی
    if callback_data == "admin_broadcast":
        show_admin_broadcast(chat_id, message_id)
        return True

    # کاربران
    if callback_data == "admin_users":
        show_admin_users(chat_id, message_id)
        return True

    # کاربران بن شده
    if callback_data == "admin_banned":
        show_admin_banned(chat_id, message_id)
        return True

    # مدیریت ادمین‌ها
    if callback_data == "admin_admins":
        show_admin_admins(chat_id, message_id)
        return True

    # تنظیمات
    if callback_data == "admin_settings":
        show_admin_settings(chat_id, message_id)
        return True

    # برگشت از بخش‌های پنل به پنل اصلی
    if callback_data == "back_admin_panel":
        show_admin_panel(chat_id, message_id)
        return True

    return False
