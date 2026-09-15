import requests
import time

from config import BOT_TOKEN, API_URL

import database


# =========================================================
# تنظیمات اصلی ربات
# =========================================================

BASE_URL = API_URL

# =========================================================
# Session مشترک
# =========================================================
# به جای ساختن اتصال جدید برای هر درخواست،
# از یک Session مشترک استفاده می‌کنیم.
# این کار تعداد زیادی از درخواست‌های API را سریع‌تر می‌کند.

SESSION = requests.Session()

SESSION.headers.update({
    "Content-Type": "application/json"
})


# =========================================================
# Cache بررسی عضویت اجباری
# =========================================================

JOIN_CACHE = {}

# مدت اعتبار Cache عضویت
# کوتاه نگه داشته شده تا منطق فعلی تقریباً همان باقی بماند.
JOIN_CACHE_TTL = 60


def is_join_cached(user_id):
    """
    بررسی می‌کند آیا وضعیت عضویت کاربر
    اخیراً بررسی شده است یا خیر.
    """

    cached_time = JOIN_CACHE.get(user_id)

    if cached_time is None:
        return False

    if time.monotonic() - cached_time < JOIN_CACHE_TTL:
        return True

    JOIN_CACHE.pop(user_id, None)

    return False


def cache_join(user_id):
    """
    ذخیره موفقیت بررسی عضویت.
    """

    JOIN_CACHE[user_id] = time.monotonic()


def clear_join_cache(user_id):
    """
    حذف Cache عضویت کاربر.
    """

    JOIN_CACHE.pop(user_id, None)


# =========================================================
# درخواست API
# =========================================================

def api_request(method, data=None):
    """
    ارسال سریع درخواست به API بله.
    """

    url = f"{BASE_URL}/{method}"

    try:
        response = SESSION.post(
            url,
            json=data or {},
            timeout=(3, 10)
        )

        response.raise_for_status()

        return response.json()

    except requests.RequestException as error:
        print(f"API Error [{method}]: {error}")
        return None

    except ValueError:
        print(f"API JSON Error [{method}]")
        return None


# =========================================================
# پاسخ فوری به Callback
# =========================================================

def answer_callback(callback_id, text=None, show_alert=False):
    """
    پاسخ فوری به کلیک روی دکمه Inline.

    باعث می‌شود حالت Loading دکمه سریعاً بسته شود.
    """

    if not callback_id:
        return None

    data = {
        "callback_query_id": callback_id
    }

    if text:
        data["text"] = text

    if show_alert:
        data["show_alert"] = True

    return api_request(
        "answerCallbackQuery",
        data
    )


# =========================================================
# دریافت آپدیت‌ها
# =========================================================

def get_updates(offset=None):

    data = {
        "timeout": 25,
        "limit": 100,
        "allowed_updates": [
            "message",
            "callback_query"
        ]
    }

    if offset is not None:
        data["offset"] = offset

    return api_request(
        "getUpdates",
        data
    )


# =========================================================
# ارسال پیام
# =========================================================

def send_message(chat_id, text, reply_markup=None):

    data = {
        "chat_id": chat_id,
        "text": text
    }

    if reply_markup is not None:
        data["reply_markup"] = reply_markup

    return api_request(
        "sendMessage",
        data
    )


# =========================================================
# ویرایش پیام
# =========================================================

def edit_message(chat_id, message_id, text, reply_markup=None):

    data = {
        "chat_id": chat_id,
        "message_id": message_id,
        "text": text
    }

    if reply_markup is not None:
        data["reply_markup"] = reply_markup

    return api_request(
        "editMessageText",
        data
    )


# =========================================================
# سیستم اتصال فایل‌ها
# =========================================================

modules = []


def register_module(module):

    if module not in modules:
        modules.append(module)

    print(f"Module loaded: {module.__name__}")


# =========================================================
# Start
# =========================================================

import start

start.setup(
    send_message,
    edit_message
)

register_module(start)


# =========================================================
# Shop
# =========================================================

import shop

shop.setup(
    send_message,
    edit_message
)

register_module(shop)


# =========================================================
# Export / Import
# =========================================================

import export_import

export_import.setup(
    send_message,
    edit_message,
    shop.find_item
)

register_module(export_import)


# =========================================================
# Attack
# =========================================================

import attack

attack.setup(
    send_message,
    edit_message
)

register_module(attack)


# =========================================================
# Statement
# =========================================================

import statement

statement.setup(
    send_message,
    edit_message
)

register_module(statement)


# =========================================================
# Country Admin
# =========================================================

import country_admin

country_admin.setup(
    send_message,
    edit_message
)

register_module(country_admin)


# =========================================================
# Join Required
# =========================================================

import join_required

join_required.setup(
    send_message,
    edit_message,
    api_request
)

register_module(join_required)


# =========================================================
# Mine Income
# =========================================================

import mine_income

mine_income.setup(
    send_message
)

register_module(mine_income)


# =========================================================
# Alliance
# =========================================================

import alliance

alliance.setup(
    send_message,
    edit_message
)

register_module(alliance)


# =========================================================
# International Companies
# =========================================================

import companies

companies.setup(
    send_message,
    edit_message
)

register_module(companies)


# =========================================================
# Database
# =========================================================

database.init_db()


# =========================================================
# بررسی جوین اجباری
# =========================================================

def check_join_required(update):

    # =====================================================
    # Message
    # =====================================================

    if "message" in update:

        message = update["message"]

        chat = message.get("chat", {})
        user = message.get("from", {})

        chat_id = chat.get("id")
        user_id = user.get("id")

        text = message.get(
            "text",
            ""
        ).strip()

        chat_type = chat.get("type")

        # فقط PV
        if chat_type != "private":
            return True

        # =================================================
        # /start
        # =================================================

        if text == "/start":

            # برای /start بررسی واقعی انجام می‌شود
            # تا کاربر بتواند عضویت خود را تأیید کند.

            clear_join_cache(user_id)

            allowed = join_required.handle_start(
                chat_id,
                user_id
            )

            if allowed:
                cache_join(user_id)

            return allowed

        # =================================================
        # پیام معمولی
        # =================================================

        # اگر اخیراً عضویت تأیید شده،
        # دوباره API نزن.

        if is_join_cached(user_id):
            return True

        # بررسی واقعی عضویت

        if not join_required.is_user_joined(user_id):

            join_required.send_join_required(
                chat_id
            )

            return False

        # عضویت تأیید شد
        cache_join(user_id)

        return True

    # =====================================================
    # Callback Query
    # =====================================================

    if "callback_query" in update:

        callback = update["callback_query"]

        callback_id = callback.get(
            "id"
        )

        user = callback.get(
            "from",
            {}
        )

        user_id = user.get(
            "id"
        )

        message = callback.get(
            "message"
        )

        # =================================================
        # پاسخ فوری به کلیک
        # =================================================

        answer_callback(
            callback_id
        )

        if message is None:
            return False

        chat = message.get(
            "chat",
            {}
        )

        chat_id = chat.get(
            "id"
        )

        chat_type = chat.get(
            "type"
        )

        # فقط PV
        if chat_type != "private":
            return True

        # =================================================
        # Cache
        # =================================================

        if is_join_cached(user_id):
            return True

        # =================================================
        # بررسی عضویت واقعی
        # =================================================

        if not join_required.is_user_joined(user_id):

            join_required.send_join_required(
                chat_id
            )

            return False

        # =================================================
        # ذخیره Cache
        # =================================================

        cache_join(user_id)

        return True

    # =====================================================
    # سایر آپدیت‌ها
    # =====================================================

    return True


# =========================================================
# اجرای ربات
# =========================================================

def run_bot():

    print("================================")
    print("World War Bot")
    print("Bot is starting...")
    print("================================")

    offset = None

    while True:

        try:

            # =================================================
            # دریافت آپدیت
            # =================================================

            result = get_updates(
                offset
            )

            # =================================================
            # بررسی درآمد روزانه
            # =================================================

            try:

                mine_income.check_payout()

            except Exception as error:

                print(
                    f"Mine Income Error: {error}"
                )

            # =================================================
            # اگر پاسخ خالی بود
            # =================================================

            if not result:

                # قبلاً اینجا 2 ثانیه sleep داشتیم.
                # حذف شد تا بعد از timeout تأخیر اضافه نداشته باشیم.

                continue

            # =================================================
            # API Error
            # =================================================

            if not result.get("ok"):

                print(
                    "API Error:",
                    result
                )

                # تأخیر فقط در صورت خطای واقعی API
                time.sleep(1)

                continue

            # =================================================
            # Updates
            # =================================================

            updates = result.get(
                "result",
                []
            )

            if not updates:
                continue

            # =================================================
            # پردازش آپدیت‌ها
            # =================================================

            for update in updates:

                offset = (
                    update["update_id"] + 1
                )

                # =================================================
                # بررسی Join
                # =================================================

                try:

                    allowed = check_join_required(
                        update
                    )

                    if not allowed:
                        continue

                except Exception as error:

                    print(
                        f"Join Required Error: {error}"
                    )

                    continue

                # =================================================
                # جلوگیری از اجرای ربات
                # داخل گروه و کانال
                # =================================================

                if "message" in update:

                    chat_type = (
                        update["message"]
                        .get("chat", {})
                        .get("type")
                    )

                    if chat_type != "private":
                        continue

                if "callback_query" in update:

                    callback_message = (
                        update["callback_query"]
                        .get("message")
                    )

                    if callback_message is not None:

                        chat_type = (
                            callback_message
                            .get("chat", {})
                            .get("type")
                        )

                        if chat_type != "private":
                            continue

                # =================================================
                # اجرای ماژول‌ها
                # =================================================

                for module in modules:

                    try:

                        module.handle_update(
                            update
                        )

                    except Exception as error:

                        print(
                            f"Error in "
                            f"{module.__name__}: "
                            f"{error}"
                        )


        except KeyboardInterrupt:

            print(
                "\nBot stopped."
            )

            break


        except Exception as error:

            print(
                f"Main Error: {error}"
            )

            # فقط در خطای غیرمنتظره
            # یک ثانیه صبر می‌کنیم.

            time.sleep(1)


# =========================================================
# Start Bot
# =========================================================

if __name__ == "__main__":
    run_bot()
