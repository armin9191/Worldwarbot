import requests
import time

from config import BOT_TOKEN, API_URL

import database

# =========================
# تنظیمات اصلی ربات
# =========================

BASE_URL = API_URL


def api_request(method, data=None):
    """
    ارسال درخواست به API بله
    """
    url = f"{BASE_URL}/{method}"

    try:
        response = requests.post(
            url,
            json=data or {},
            timeout=30
        )

        return response.json()

    except requests.RequestException as error:
        print(f"API Error: {error}")
        return None

    except ValueError:
        print("API پاسخ معتبر JSON برنگرداند.")
        return None


# =========================
# دریافت آپدیت‌ها
# =========================

def get_updates(offset=None):
    data = {
        "timeout": 25
    }

    if offset is not None:
        data["offset"] = offset

    return api_request("getUpdates", data)


# =========================
# ارسال پیام
# =========================

def send_message(chat_id, text, reply_markup=None):
    data = {
        "chat_id": chat_id,
        "text": text
    }

    if reply_markup is not None:
        data["reply_markup"] = reply_markup

    return api_request("sendMessage", data)


# =========================
# ویرایش پیام
# =========================

def edit_message(chat_id, message_id, text, reply_markup=None):
    data = {
        "chat_id": chat_id,
        "message_id": message_id,
        "text": text
    }

    if reply_markup is not None:
        data["reply_markup"] = reply_markup

    return api_request("editMessageText", data)


# =========================
# سیستم اتصال فایل‌ها
# =========================

modules = []


def register_module(module):
    """
    ثبت یک فایل قابلیت در bot.py
    """
    if module not in modules:
        modules.append(module)

    print(f"Module loaded: {module.__name__}")


# =========================
# اتصال ماژول Start
# =========================

import start

start.setup(send_message, edit_message)
register_module(start)


# =========================
# اتصال ماژول Shop
# =========================

import shop

shop.setup(send_message, edit_message)
register_module(shop)

# =========================
# اتصال ماژول Export / Import
# =========================

import export_import

export_import.setup(
    send_message,
    edit_message,
    shop.find_item
)

register_module(export_import)

# =========================
# اتصال ماژول Attack
# =========================

import attack

attack.setup(send_message, edit_message)
register_module(attack)


# =========================
# اتصال ماژول Statement
# =========================

import statement

statement.setup(send_message, edit_message)
register_module(statement)


# =========================
# اتصال ماژول مدیریت کشورها
# =========================

import country_admin

country_admin.setup(
    send_message,
    edit_message
)

register_module(country_admin)


# =========================
# اتصال ماژول Join Required
# =========================

import join_required

join_required.setup(
    send_message,
    edit_message,
    api_request
)

register_module(join_required)


# =========================
# اتصال ماژول Mine Income
# =========================

import mine_income

mine_income.setup(send_message)
register_module(mine_income)

# =========================
# اتصال ماژول Alliance
# =========================

import alliance

alliance.setup(send_message, edit_message)
register_module(alliance)

# =========================
# اتصال ماژول International Companies
# =========================

import companies

companies.setup(
    send_message,
    edit_message
)

register_module(companies)


database.init_db()


# =========================
# بررسی جوین اجباری
# =========================

def check_join_required(update):

    # =========================
    # آپدیت پیام
    # =========================

    if "message" in update:

        message = update["message"]

        chat_id = message["chat"]["id"]
        user_id = message["from"]["id"]

        text = message.get("text", "").strip()

        # =========================
        # فقط PV
        # =========================

        chat_type = message["chat"].get("type")

        # اگر پیام داخل گروه یا کانال باشد
        # جوین اجباری بررسی نمی‌شود
        if chat_type != "private":
            return True

        # -------------------------
        # اگر /start بود
        # -------------------------

        if text == "/start":

            return join_required.handle_start(
                chat_id,
                user_id
            )

        # -------------------------
        # پیام‌های معمولی
        # -------------------------

        if not join_required.is_user_joined(user_id):

            join_required.send_join_required(
                chat_id
            )

            return False

        return True

    # =========================
    # آپدیت Callback
    # =========================

    if "callback_query" in update:

        callback = update["callback_query"]

        user_id = callback["from"]["id"]

        message = callback.get("message")

        if message is None:
            return False

        chat_id = message["chat"]["id"]

        # =========================
        # فقط Callback مربوط به PV
        # =========================

        chat_type = message["chat"].get("type")

        if chat_type != "private":
            return True

        # -------------------------
        # بررسی عضویت
        # -------------------------

        if not join_required.is_user_joined(user_id):

            join_required.send_join_required(
                chat_id
            )

            return False

        return True

    # =========================
    # آپدیت‌های دیگر
    # =========================

    return True


# =========================
# اجرای ربات
# =========================

def run_bot():
    print("================================")
    print("World War Bot")
    print("Bot is starting...")
    print("================================")

    offset = None

    while True:
        try:
            result = get_updates(offset)

            # =========================
            # بررسی درآمد روزانه معادن
            # =========================

            try:
                mine_income.check_payout()

            except Exception as error:
                print(
                    f"Mine Income Error: {error}"
                )

            if not result:
                time.sleep(2)
                continue

            if not result.get("ok"):
                print("API Error:", result)
                time.sleep(3)
                continue

            updates = result.get("result", [])

            for update in updates:
                offset = update["update_id"] + 1

                # =========================
                # بررسی جوین اجباری
                # =========================

                try:
                    allowed = check_join_required(update)

                    if not allowed:
                        continue

                except Exception as error:
                    print(
                        f"Join Required Error: {error}"
                    )

                    continue

                # =========================
                # جلوگیری از اجرای ربات
                # داخل گروه و کانال
                # =========================

                if "message" in update:

                    chat_type = update["message"]["chat"].get("type")

                    if chat_type != "private":
                        continue

                if "callback_query" in update:

                    callback_message = update["callback_query"].get("message")

                    if callback_message is not None:

                        chat_type = callback_message["chat"].get("type")

                        if chat_type != "private":
                            continue

                # =========================
                # اجرای ماژول‌ها
                # =========================

                for module in modules:
                    try:
                        module.handle_update(update)

                    except Exception as error:
                        print(
                            f"Error in {module.__name__}: {error}"
                        )

        except KeyboardInterrupt:
            print("\nBot stopped.")
            break

        except Exception as error:
            print(f"Main Error: {error}")
            time.sleep(5)