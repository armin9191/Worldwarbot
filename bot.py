import requests
import time

from config import BOT_TOKEN, API_URL
import database

BASE_URL = API_URL

SESSION = requests.Session()
SESSION.headers.update({
    "Content-Type": "application/json"
})


JOIN_CACHE = {}
JOIN_CACHE_TTL = 60


def is_join_cached(user_id):
    cached_time = JOIN_CACHE.get(user_id)

    if cached_time is None:
        return False

    if time.monotonic() - cached_time < JOIN_CACHE_TTL:
        return True

    JOIN_CACHE.pop(user_id, None)

    return False


def cache_join(user_id):
    JOIN_CACHE[user_id] = time.monotonic()


def clear_join_cache(user_id):
    JOIN_CACHE.pop(user_id, None)


def api_request(method, data=None):

    url = f"{BASE_URL}/{method}"

    try:

        response = SESSION.post(
            url,
            json=data or {},
            timeout=(5, 35)
        )

        response.raise_for_status()

        return response.json()

    except requests.RequestException as error:

        print(f"API Error [{method}]: {error}")

        return None

    except ValueError:

        print(f"API JSON Error [{method}]")

        return None


def answer_callback(callback_id, text=None, show_alert=False):

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


def send_message(
    chat_id,
    text,
    reply_markup=None
):

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


def edit_message(
    chat_id,
    message_id,
    text,
    reply_markup=None
):

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
# Modules
# =========================================================

modules = []


def register_module(module):

    if module not in modules:
        modules.append(module)

    print(
        f"Module loaded: {module.__name__}"
    )


# =========================================================
# Start
# =========================================================

import military
import start

start.setup(
    send_message,
    edit_message,
    military.calculate_defense_power
)

register_module(start)


# =========================================================
# Reports
# =========================================================

import reports

reports.setup(
    send_message
)


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
    edit_message,
    start.show_main_menu
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
# Admin Panel
# =========================================================

import admin_panel

admin_panel.setup(
    send_message,
    edit_message
)


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
# Database Backup
# =========================================================

import backup

backup.setup(
    send_message
)

register_module(backup)


# =========================================================
# ذخیره اطلاعات کاربر
# =========================================================

def save_user_info(update):

    if "message" in update:

        message = update["message"]

        user = message.get(
            "from",
            {}
        )

        user_id = user.get("id")

        if user_id is None:
            return

        username = user.get("username")

        if username:
            username = username.strip()

        database.get_or_create_user(
            user_id
        )

        database.update_username(
            user_id,
            username
        )

        # ثبت آخرین فعالیت کاربر
        database.update_last_active(
            user_id
        )

        return

    if "callback_query" in update:

        callback = update["callback_query"]

        user = callback.get(
            "from",
            {}
        )

        user_id = user.get("id")

        if user_id is None:
            return

        username = user.get("username")

        if username:
            username = username.strip()

        database.get_or_create_user(
            user_id
        )

        database.update_username(
            user_id,
            username
        )

        # ثبت آخرین فعالیت کاربر
        database.update_last_active(
            user_id
        )


# =========================================================
# بررسی بن بودن کاربر
# =========================================================

def check_user_banned(update):

    if "message" not in update:
        return True

    message = update["message"]

    chat = message.get(
        "chat",
        {}
    )

    user = message.get(
        "from",
        {}
    )

    chat_id = chat.get("id")
    user_id = user.get("id")

    text = message.get(
        "text",
        ""
    ).strip()

    chat_type = chat.get("type")

    if chat_type != "private":
        return True

    # فقط هنگام ورود با /start بررسی می‌شود
    if text != "/start":
        return True

    ban_info = database.get_ban_info(
        user_id
    )

    if ban_info is None:
        return True

    reason = ban_info.get(
        "reason"
    ) or "دلیلی ثبت نشده است."

    send_message(
        chat_id,
        "🚫 شما از بازی بن شده‌اید.\n\n"
        "❌ دسترسی شما به بازی مسدود شده است.\n\n"
        f"📄 دلیل بن:\n{reason}"
    )

    return False


# =========================================================
# Join Required Check
# =========================================================

def check_join_required(update):

    if "message" in update:

        message = update["message"]

        chat = message.get(
            "chat",
            {}
        )

        user = message.get(
            "from",
            {}
        )

        chat_id = chat.get("id")
        user_id = user.get("id")

        text = message.get(
            "text",
            ""
        ).strip()

        chat_type = chat.get("type")

        if chat_type != "private":
            return True

        if text == "/start":

            clear_join_cache(
                user_id
            )

            allowed = join_required.handle_start(
                chat_id,
                user_id
            )

            if allowed:
                cache_join(
                    user_id
                )

            return allowed

        if is_join_cached(user_id):
            return True

        if not join_required.is_user_joined(
            user_id
        ):

            join_required.send_join_required(
                chat_id
            )

            return False

        cache_join(
            user_id
        )

        return True


    if "callback_query" in update:

        callback = update["callback_query"]

        callback_id = callback.get("id")

        user = callback.get(
            "from",
            {}
        )

        user_id = user.get("id")

        message = callback.get("message")

        answer_callback(
            callback_id
        )

        if message is None:
            return False

        chat = message.get(
            "chat",
            {}
        )

        chat_id = chat.get("id")

        chat_type = chat.get("type")

        if chat_type != "private":
            return True

        if is_join_cached(user_id):
            return True

        if not join_required.is_user_joined(
            user_id
        ):

            join_required.send_join_required(
                chat_id
            )

            return False

        cache_join(
            user_id
        )

        return True

    return True


# =========================================================
# Run Bot
# =========================================================

def run_bot():

    print("================================")
    print("World War Bot")
    print("Bot is starting...")
    print("================================")

    offset = None

    while True:

        try:

            result = get_updates(
                offset
            )

            try:

                mine_income.check_payout()

            except Exception as error:

                print(
                    f"Mine Income Error: {error}"
                )


            if not result:
                continue


            if not result.get("ok"):

                print(
                    "API Error:",
                    result
                )

                time.sleep(1)

                continue


            updates = result.get(
                "result",
                []
            )


            if not updates:
                continue


            for update in updates:

                offset = (
                    update["update_id"] + 1
                )


                try:

                    # =============================================
                    # ذخیره اطلاعات کاربر
                    # =============================================

                    save_user_info(
                        update
                    )

                    # =============================================
                    # بررسی بن بودن
                    # فقط برای /start
                    # =============================================

                    if not check_user_banned(
                        update
                    ):
                        continue

                    # =============================================
                    # بررسی عضویت
                    # =============================================

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
                # فقط پیوی
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
                # Admin Panel
                # =================================================

                if "callback_query" in update:

                    callback = update["callback_query"]

                    callback_data = callback.get(
                        "data",
                        ""
                    )

                    if callback_data == "admin_panel":

                        message = callback.get(
                            "message"
                        )

                        if message is not None:

                            chat_id = message.get(
                                "chat",
                                {}
                            ).get("id")

                            message_id = message.get(
                                "message_id"
                            )

                            admin_panel.handle_callback(
                                chat_id,
                                message_id,
                                callback_data
                            )

                        continue


                # =================================================
                # Send update to modules
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

            time.sleep(1)


# =========================================================
# Main
# =========================================================

if __name__ == "__main__":
    run_bot()
