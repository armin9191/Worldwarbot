# ==============================
# World War - Statement System
# ==============================

import config
import database


# ==============================
# اتصال به Bot
# ==============================

send_message = None
edit_message = None


def setup(send_func, edit_func):
    global send_message
    global edit_message

    send_message = send_func
    edit_message = edit_func


# ==============================
# وضعیت بیانیه کاربران
# ==============================

statement_sessions = {}


# ==============================
# کیبورد لغو
# ==============================

def cancel_keyboard():
    return {
        "inline_keyboard": [
            [
                {
                    "text": "❌ لغو",
                    "callback_data": "statement_cancel"
                }
            ]
        ]
    }


# ==============================
# کیبورد ادمین
# ==============================

def admin_statement_keyboard(user_id):
    return {
        "inline_keyboard": [
            [
                {
                    "text": "✅ تایید",
                    "callback_data": f"statement_approve_{user_id}"
                },
                {
                    "text": "❌ رد",
                    "callback_data": f"statement_reject_{user_id}"
                }
            ]
        ]
    }


# ==============================
# بررسی ادمین بودن کاربر
# ==============================

def is_admin(user_id):
    admins = getattr(
        config,
        "ADMINS",
        []
    )

    return user_id in admins


# ==============================
# شروع صدور بیانیه
# ==============================

def start_statement(chat_id, message_id, user_id):

    statement_sessions[user_id] = {
        "chat_id": chat_id,
        "message_id": message_id,
        "waiting_text": True
    }

    edit_message(
        chat_id,
        message_id,
        "📢 صدور بیانیه\n\n"
        "متن بیانیه خود را بنویسید.",
        cancel_keyboard()
    )


# ==============================
# ارسال بیانیه برای ادمین‌ها
# ==============================

def send_statement_to_admin(
    user_id,
    statement_text
):

    admins = getattr(
        config,
        "ADMINS",
        []
    )

    if not admins:
        print(
            "Statement Error: "
            "ADMINS is not configured."
        )
        return False

    success = False

    for admin_id in admins:

        result = send_message(
            admin_id,
            "📢 بیانیه جدید\n\n"
            f"👤 کاربر: {user_id}\n\n"
            "📝 متن بیانیه:\n"
            f"{statement_text}",
            admin_statement_keyboard(user_id)
        )

        if result and result.get("ok") is not False:
            success = True

    return success


# ==============================
# انتشار بیانیه
# ==============================

def publish_statement(
    user_id,
    statement_text
):

    channel_id = getattr(
        config,
        "STATEMENT_CHANNEL_ID",
        None
    )

    group_id = getattr(
        config,
        "STATEMENT_GROUP_ID",
        None
    )

    if channel_id is None:
        print(
            "Statement Error: "
            "STATEMENT_CHANNEL_ID is not configured."
        )
        return False

    if group_id is None:
        print(
            "Statement Error: "
            "STATEMENT_GROUP_ID is not configured."
        )
        return False

    # ==========================
    # گرفتن کشور کاربر
    # ==========================

    user = database.get_user(user_id)

    if user is None:
        print(
            "Statement Error: "
            "User not found."
        )
        return False

    country = user.get("country")

    if not country:
        country = "نامشخص"

    # ==========================
    # ساخت متن نهایی بیانیه
    # ==========================

    final_text = (
        "📢 بیانیه رسمی\n\n"
        f"کشور: {country}\n\n"
        f"{statement_text}\n\n"
        "این بیانیه توسط سازمان جهانی تایید شده است."
    )

    # ==========================
    # انتشار در کانال
    # ==========================

    channel_result = send_message(
        channel_id,
        final_text
    )

    if not channel_result:
        return False

    if channel_result.get("ok") is False:
        return False

    # ==========================
    # انتشار در گروه
    # ==========================

    group_result = send_message(
        group_id,
        final_text
    )

    if not group_result:
        return False

    if group_result.get("ok") is False:
        return False

    return True


# ==============================
# دریافت آپدیت‌ها
# ==============================

def handle_update(update):

    # ==================================
    # پیام متنی کاربر
    # ==================================

    if "message" in update:

        message = update["message"]

        chat_id = message["chat"]["id"]
        user_id = message["from"]["id"]
        message_id = message["message_id"]

        text = message.get("text", "").strip()

        session = statement_sessions.get(user_id)

        if session is None:
            return

        # فقط زمانی که منتظر متن بیانیه هستیم
        if session.get("waiting_text"):

            if not text:

                edit_message(
                    session["chat_id"],
                    session["message_id"],
                    "❌ متن بیانیه نمی‌تواند خالی باشد.\n\n"
                    "لطفاً متن بیانیه خود را بنویسید.",
                    cancel_keyboard()
                )

                return

            statement_text = text

            # دیگر منتظر متن نیستیم
            session["waiting_text"] = False

            # ذخیره متن بیانیه
            session["statement_text"] = statement_text

            # ==================================
            # حالت انتشار خودکار
            # ==================================

            auto_approve = getattr(
                config,
                "AUTO_APPROVE_STATEMENTS",
                False
            )

            if auto_approve:

                # انتشار مستقیم در کانال و گروه
                published = publish_statement(
                    user_id,
                    statement_text
                )

                if not published:

                    statement_sessions.pop(
                        user_id,
                        None
                    )

                    edit_message(
                        session["chat_id"],
                        session["message_id"],
                        "❌ انتشار بیانیه با خطا مواجه شد.\n\n"
                        "لطفاً دوباره تلاش کنید."
                    )

                    return

                # اطلاع به کاربر
                edit_message(
                    session["chat_id"],
                    session["message_id"],
                    "✅ بیانیه شما با موفقیت منتشر شد.\n\n"
                    "📢 بیانیه در کانال و گروه منتشر شد."
                )

                # پاک کردن وضعیت
                statement_sessions.pop(
                    user_id,
                    None
                )

                return

            # ==================================
            # حالت تأیید دستی
            # ==================================

            # ارسال برای ادمین‌ها
            success = send_statement_to_admin(
                user_id,
                statement_text
            )

            if not success:

                statement_sessions.pop(
                    user_id,
                    None
                )

                edit_message(
                    session["chat_id"],
                    session["message_id"],
                    "❌ ارسال بیانیه با خطا مواجه شد.\n\n"
                    "لطفاً دوباره تلاش کنید."
                )

                return

            # اطلاع به کاربر
            edit_message(
                session["chat_id"],
                session["message_id"],
                "📢 بیانیه شما برای بررسی ارسال شد.\n\n"
                "⏳ لطفاً منتظر تایید ادمین باشید."
            )

        return

    # ==================================
    # فقط Callback Query
    # ==================================

    if "callback_query" not in update:
        return

    callback = update["callback_query"]

    data = callback.get("data")

    message = callback.get("message")

    if message is None:
        return

    chat_id = message["chat"]["id"]
    message_id = message["message_id"]
    user_id = callback["from"]["id"]

    # ==================================
    # شروع صدور بیانیه
    # ==================================

    if data == "statement":

        statement_sessions.pop(
            user_id,
            None
        )

        start_statement(
            chat_id,
            message_id,
            user_id
        )

        return

    # ==================================
    # لغو بیانیه
    # ==================================

    if data == "statement_cancel":

        statement_sessions.pop(
            user_id,
            None
        )

        edit_message(
            chat_id,
            message_id,
            "🏠 منوی اصلی"
        )

        return

    # ==================================
    # تایید بیانیه
    # ==================================

    if data.startswith("statement_approve_"):

        # فقط ادمین‌ها
        if not is_admin(user_id):
            return

        try:
            target_user_id = int(
                data.replace(
                    "statement_approve_",
                    ""
                )
            )

        except ValueError:
            return

        session = statement_sessions.get(
            target_user_id
        )

        if session is None:

            edit_message(
                chat_id,
                message_id,
                "❌ این بیانیه دیگر در انتظار بررسی نیست."
            )

            return

        statement_text = session.get(
            "statement_text"
        )

        if not statement_text:

            edit_message(
                chat_id,
                message_id,
                "❌ متن بیانیه پیدا نشد."
            )

            return

        # انتشار در کانال و گروه
        published = publish_statement(
            target_user_id,
            statement_text
        )

        if not published:

            edit_message(
                chat_id,
                message_id,
                "❌ انتشار بیانیه با خطا مواجه شد.\n\n"
                "بیانیه منتشر نشد."
            )

            return

        # تغییر پیام ادمین
        edit_message(
            chat_id,
            message_id,
            "✅ بیانیه تایید و منتشر شد."
        )

        # اطلاع به کاربر
        edit_message(
            session["chat_id"],
            session["message_id"],
            "✅ بیانیه شما تایید شد.\n\n"
            "📢 بیانیه در کانال و گروه منتشر شد."
        )

        # پاک کردن وضعیت
        statement_sessions.pop(
            target_user_id,
            None
        )

        return

    # ==================================
    # رد بیانیه
    # ==================================

    if data.startswith("statement_reject_"):

        # فقط ادمین‌ها
        if not is_admin(user_id):
            return

        try:
            target_user_id = int(
                data.replace(
                    "statement_reject_",
                    ""
                )
            )

        except ValueError:
            return

        session = statement_sessions.get(
            target_user_id
        )

        if session is None:

            edit_message(
                chat_id,
                message_id,
                "❌ این بیانیه دیگر در انتظار بررسی نیست."
            )

            return

        # تغییر پیام ادمین
        edit_message(
            chat_id,
            message_id,
            "❌ بیانیه رد شد."
        )

        # اطلاع به کاربر
        edit_message(
            session["chat_id"],
            session["message_id"],
            "❌ بیانیه شما رد شد.\n\n"
            "این بیانیه منتشر نخواهد شد."
        )

        # پاک کردن وضعیت
        statement_sessions.pop(
            target_user_id,
            None
        )

        return
