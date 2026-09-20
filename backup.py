# ==============================
# World War - Database Backup
# ==============================

import os
import requests

from config import DATABASE_NAME, ADMINS, API_URL


send_message = None


def setup(send_message_function):
    global send_message
    send_message = send_message_function


def send_database_backup(user_id: int) -> bool:

    # فقط ادمین
    if user_id not in ADMINS:
        return False

    possible_paths = [
        DATABASE_NAME,
        f"/data/{DATABASE_NAME}",
        "/data/world_war.db",
    ]

    db_path = None

    for path in possible_paths:
        if os.path.exists(path):
            db_path = path
            break

    if not db_path:
        print("Backup Error: Database file not found")
        return False

    try:
        with open(db_path, "rb") as f:

            files = {
                "document": (
                    "world_war.db",
                    f,
                    "application/octet-stream"
                )
            }

            data = {
                "chat_id": user_id
            }

            response = requests.post(
                f"{API_URL}/sendDocument",
                data=data,
                files=files,
                timeout=60
            )

            if response.status_code == 200:
                print("Database backup sent successfully.")
                return True

            print(
                "Backup Error:",
                response.status_code,
                response.text
            )

            return False

    except Exception as e:
        print(f"[BACKUP ERROR] {e}")
        return False


def handle_update(update):

    if "message" not in update:
        return

    message = update["message"]

    chat = message.get("chat", {})
    chat_type = chat.get("type")

    # فقط پیوی
    if chat_type != "private":
        return

    user = message.get("from", {})
    user_id = user.get("id")

    text = message.get("text", "").strip()

    # دستور بکاپ
    if text != "/backup":
        return

    # فقط ادمین
    if user_id not in ADMINS:
        return

    if send_message:
        send_message(
            user_id,
            "⏳ در حال تهیه بکاپ دیتابیس..."
        )

    success = send_database_backup(user_id)

    if not success:
        if send_message:
            send_message(
                user_id,
                "❌ تهیه بکاپ انجام نشد."
              )
