# ==============================
# World War - Country Admin
# ==============================

import config
import database

send_message = None
edit_message = None

admin_sessions = {}


# =========================
# اتصال به bot.py
# =========================

def setup(send_message_function, edit_message_function):
    global send_message
    global edit_message

    send_message = send_message_function
    edit_message = edit_message_function


# =========================
# بررسی ادمین بودن
# =========================

def is_admin(user_id):
    return user_id in getattr(config, "ADMINS", [])


# =========================
# ایموجی کشورها
# =========================

COUNTRY_FLAGS = {
    "ایران": "🇮🇷",
    "آمریکا": "🇺🇸",
    "اسرائیل": "🇮🇱",
    "روسیه": "🇷🇺",
    "ژاپن": "🇯🇵",
    "چین": "🇨🇳",
    "انگلیس": "🇬🇧",
    "فرانسه": "🇫🇷",
    "آلمان": "🇩🇪",
    "ترکیه": "🇹🇷",
    "هند": "🇮🇳",
    "کره جنوبی": "🇰🇷",
    "کره شمالی": "🇰🇵",
    "عربستان": "🇸🇦",
    "امارات": "🇦🇪",
    "مصر": "🇪🇬",
    "پاکستان": "🇵🇰",
    "اوکراین": "🇺🇦",
    "ایتالیا": "🇮🇹",
    "اسپانیا": "🇪🇸",
    "کانادا": "🇨🇦",
    "استرالیا": "🇦🇺",
    "برزیل": "🇧🇷",
    "مکزیک": "🇲🇽",
    "اندونزی": "🇮🇩",
    "ویتنام": "🇻🇳",
    "لهستان": "🇵🇱",
    "یونان": "🇬🇷",
    "عراق": "🇮🇶",
    "قطر": "🇶🇦"
}


# =========================
# منوی مدیریت کشورها
# =========================

def admin_country_list_keyboard(countries):
    keyboard = []

    for item in countries:

        country = item["country"]
        flag = COUNTRY_FLAGS.get(country, "🌍")

        keyboard.append([
            {
                "text": f"{flag} {country}",
                "callback_data": f"admin_country_{item['user_id']}"
            }
        ])

    keyboard.append([
        {
            "text": "🔙 منوی اصلی",
            "callback_data": "back_main_menu"
        }
    ])

    return {
        "inline_keyboard": keyboard
    }


# =========================
# دکمه‌های مدیریت کشور
# =========================

def admin_manage_keyboard(user_id):
    return {
        "inline_keyboard": [
            [
                {
                    "text": "💸 کاهش پول",
                    "callback_data": f"admin_decrease_{user_id}"
                },
                {
                    "text": "💰 افزایش پول",
                    "callback_data": f"admin_increase_{user_id}"
                }
            ],
            [
                {
                    "text": "🔙 لیست کشورها",
                    "callback_data": "admin_countries"
                }
            ]
        ]
    }


# =========================
# گرفتن تعداد آیتم
# =========================

def get_quantity(inventory, item_id):
    return inventory.get(item_id, 0)


# =========================
# داشبورد کشور
# =========================

def build_country_dashboard(user):

    user_id = user["user_id"]

    inventory = database.get_inventory(user_id)

    country = user["country"]
    hp = user["hp"]
    budget = user["budget"]

    diamond = get_quantity(inventory, "diamond_mine")
    gold = get_quantity(inventory, "gold_mine")
    silver = get_quantity(inventory, "silver_mine")

    daily_income = (
        diamond * 15000000
        + gold * 10000000
        + silver * 5000000
    )

    text = (
        "━━━━━━━━━━━━━━━━━━━━\n"
        "🏛️ *داشبورد فرماندهی*\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"

        f"🌍 *{country}*\n"
        f"👤 شناسه فرمانده: `{user_id}`\n"
        f"❤️ HP: `{hp}%`\n"
        f"💰 درآمد روزانه: `{daily_income:,}`\n"
        f"🏦 بودجه دولت: `{budget:,}`\n\n"

        "🛢️ درآمد نفتی روزانه: `0`\n"
        "🛢️ ذخایر نفت: `0`\n"
        "😍 رضایت مردمی: `100٪`\n"
        "🤝 اتحاد: عضو هیچ اتحادی نیستی\n\n"

        "──────────────────\n"
        "⚔️ *نیروی زمینی*\n"
        "──────────────────\n"

        f"🎖️ فرمانده: `{get_quantity(inventory, 'commander')}`   "
        f"🪖 سرباز: `{get_quantity(inventory, 'soldier')}`\n"

        f"👮 پلیس: `{get_quantity(inventory, 'police')}`   "
        f"🛡️ مرزبان: `{get_quantity(inventory, 'border_guard')}`\n"

        f"🕵️ جاسوس: `{get_quantity(inventory, 'spy')}`   "
        f"🦅 یگان ویژه: `{get_quantity(inventory, 'special_unit')}`\n"

        f"🎯 تک‌تیرانداز: `{get_quantity(inventory, 'sniper')}`   "
        f"💥 ار پی جی: `{get_quantity(inventory, 'rpg')}`\n"

        f"💣 بمب‌گذار: `{get_quantity(inventory, 'bomber')}`   "
        f"🔧 خنثی‌کننده: `{get_quantity(inventory, 'bomb_disarmer')}`\n"

        f"🌋 مین‌گذار: `{get_quantity(inventory, 'mine_layer')}`   "
        f"🧹 خنثی‌کننده مین: `{get_quantity(inventory, 'mine_disarmer')}`\n\n"

        "──────────────────\n"
        "✈️ *نیروی هوایی*\n"
        "──────────────────\n"

        f"F-16: `{get_quantity(inventory, 'f16')}`  "
        f"F-18: `{get_quantity(inventory, 'f18')}`  "
        f"F-22: `{get_quantity(inventory, 'f22')}`\n"

        f"F-35: `{get_quantity(inventory, 'f35')}`  "
        f"B-1: `{get_quantity(inventory, 'b1')}`  "
        f"B-2: `{get_quantity(inventory, 'b2')}`  "
        f"B-52: `{get_quantity(inventory, 'b52')}`\n\n"

        "──────────────────\n"
        "⚓ *نیروی دریایی*\n"
        "──────────────────\n"

        f"🛢️ نفت‌کش: `{get_quantity(inventory, 'tanker')}`   "
        f"🚢 کشتی: `{get_quantity(inventory, 'trade_ship')}`\n"

        f"🛳️ ناو هواپیمابر: `{get_quantity(inventory, 'aircraft_carrier')}`   "
        f"⛵ قایق: `{get_quantity(inventory, 'war_boat')}`\n"

        f"🤿 زیردریایی: `{get_quantity(inventory, 'idaho_submarine')}`   "
        f"⚔️ ناو جرالد فورد: `{get_quantity(inventory, 'gerald_ford')}`\n"

        "👑 ناو ابراهام لینکن: `0`\n\n"

        "──────────────────\n"
        "🚀 *زرادخانه موشکی*\n"
        "──────────────────\n"

        f"🎯 نقطه‌زن: `{get_quantity(inventory, 'precision_missile')}`   "
        f"💨 کروز: `{get_quantity(inventory, 'cruise_missile')}`\n"

        f"⚡ خیبرشکن: `{get_quantity(inventory, 'kheybershekan')}`   "
        f"🔥 خرمشهر ۴: `{get_quantity(inventory, 'khorramshahr4')}`\n"

        f"🌐 DF-26: `{get_quantity(inventory, 'df26')}`   "
        f"☢️ بمب اتم: `{get_quantity(inventory, 'atomic_bomb')}`\n\n"

        "──────────────────\n"
        "🛬 *پهپاد*\n"
        "──────────────────\n"

        f"💥 انتحاری: `{get_quantity(inventory, 'suicide_drone')}`   "
        f"🎯 نقطه‌زن: `{get_quantity(inventory, 'precision_drone')}`   "
        f"👁️ شناسایی: `{get_quantity(inventory, 'recon_drone')}`\n\n"

        "──────────────────\n"
        "🚁 *بالگرد*\n"
        "──────────────────\n"

        f"🐊 تمساح: `{get_quantity(inventory, 'crocodile_helicopter')}`   "
        f"🦅 آپاچی: `{get_quantity(inventory, 'apache')}`   "
        f"🐍 کبری: `{get_quantity(inventory, 'cobra')}`   "
        f"🔔 بل ۱۲: `{get_quantity(inventory, 'bell12')}`\n\n"

        "──────────────────\n"
        "🛡️ *پدافند*\n"
        "──────────────────\n"

        f"🇺🇸 پاتریوت: `{get_quantity(inventory, 'patriot')}`   "
        f"🌀 فلانکس: `{get_quantity(inventory, 'phalanx')}`   "
        f"🔵 تاد: `{get_quantity(inventory, 'thaad')}`\n\n"

        "──────────────────\n"
        "🚜 *زرهپوش و تانک*\n"
        "──────────────────\n"

        f"⚔️ ذوالفقار: `{get_quantity(inventory, 'zolfaghar')}`   "
        f"🐆 پنتر: `{get_quantity(inventory, 'panther')}`   "
        f"🦁 کرار: `{get_quantity(inventory, 'karrar')}`\n\n"

        "──────────────────\n"
        "💻 *جنگ سایبری*\n"
        "──────────────────\n"

        f"🔓 هک دارایی: `{get_quantity(inventory, 'asset_hack')}`   "
        f"🔒 ضد هک: `{get_quantity(inventory, 'asset_anti_hack')}`\n"

        f"⚔️ هک نظامی: `{get_quantity(inventory, 'military_hack')}`   "
        f"🛡️ ضد هک نظامی: `{get_quantity(inventory, 'military_anti_hack')}`\n\n"

        "──────────────────\n"
        "🏙️ *زیرساخت مردمی*\n"
        "──────────────────\n"

        f"🛒 سوپرمارکت: `{get_quantity(inventory, 'supermarket')}`   "
        f"🏫 مدرسه: `{get_quantity(inventory, 'school')}`   "
        f"🎒 مهد کودک: `{get_quantity(inventory, 'kindergarten')}`\n"

        f"🏬 پاساژ: `{get_quantity(inventory, 'mall')}`   "
        f"⛺ پناهگاه: `{get_quantity(inventory, 'shelter')}`   "
        f"🏊 استخر: `{get_quantity(inventory, 'pool')}`\n"

        f"🏨 هتل: `{get_quantity(inventory, 'hotel')}`   "
        f"🚇 مترو: `{get_quantity(inventory, 'metro')}`   "
        f"🚌 اتوبوس: `{get_quantity(inventory, 'bus')}`\n"

        f"✈️ هواپیما: `{get_quantity(inventory, 'airplane')}`   "
        f"🎡 شهربازی: `{get_quantity(inventory, 'amusement_park')}`\n\n"

        "──────────────────\n"
        "⛏️ *معادن*\n"
        "──────────────────\n"

        f"💎 الماس: `{get_quantity(inventory, 'diamond_mine')}`   "
        f"🥇 طلا: `{get_quantity(inventory, 'gold_mine')}`   "
        f"🥈 نقره: `{get_quantity(inventory, 'silver_mine')}`\n"

        "━━━━━━━━━━━━━━━━━━━━"
    )

    return text


# =========================
# نمایش لیست کشورها
# =========================

def show_country_list(chat_id, message_id=None):

    countries = database.get_selected_countries()

    if not countries:

        text = "👑 مدیریت کشورها\n\n❌ در حال حاضر هیچ کشوری بازیکن ندارد."

        keyboard = {
            "inline_keyboard": [
                [
                    {
                        "text": "🔙 منوی اصلی",
                        "callback_data": "back_main_menu"
                    }
                ]
            ]
        }

    else:

        text = (
            "👑 مدیریت کشورها\n\n"
            "کشور دارای بازیکن را انتخاب کنید:"
        )

        keyboard = admin_country_list_keyboard(countries)

    if message_id is not None:
        edit_message(
            chat_id,
            message_id,
            text,
            keyboard
        )
    else:
        send_message(
            chat_id,
            text,
            keyboard
        )


# =========================
# نمایش کشور انتخاب شده
# =========================

def show_country(chat_id, message_id, target_user_id):

    user = database.get_user(target_user_id)

    if user is None or not user["country"]:

        edit_message(
            chat_id,
            message_id,
            "❌ این کشور دیگر بازیکن ندارد."
        )

        return

    text = build_country_dashboard(user)

    edit_message(
        chat_id,
        message_id,
        text,
        admin_manage_keyboard(target_user_id)
    )


# =========================
# شروع افزایش پول
# =========================

def start_increase(chat_id, message_id, admin_id, target_user_id):

    admin_sessions[admin_id] = {
        "action": "increase",
        "target_user_id": target_user_id,
        "message_id": message_id
    }

    edit_message(
        chat_id,
        message_id,
        "💰 افزایش پول\n\n"
        "مبلغ دلخواه را به صورت عدد وارد کنید.\n\n"
        "مثال:\n"
        "5000000\n\n"
        "❌ برای لغو، /cancel را بفرستید."
    )


# =========================
# شروع کاهش پول
# =========================

def start_decrease(chat_id, message_id, admin_id, target_user_id):

    admin_sessions[admin_id] = {
        "action": "decrease",
        "target_user_id": target_user_id,
        "message_id": message_id
    }

    edit_message(
        chat_id,
        message_id,
        "💸 کاهش پول\n\n"
        "مبلغ دلخواه را به صورت عدد وارد کنید.\n\n"
        "مثال:\n"
        "2000000\n\n"
        "❌ برای لغو، /cancel را بفرستید."
    )


# =========================
# پردازش مبلغ
# =========================

def process_amount(chat_id, admin_id, text):

    session = admin_sessions.get(admin_id)

    if session is None:
        return False

    if text.lower() == "/cancel":

        admin_sessions.pop(admin_id, None)

        send_message(
            chat_id,
            "❌ عملیات لغو شد."
        )

        return True

    try:
        clean_text = text.replace(",", "").replace("٬", "").strip()

        amount = int(clean_text)

    except ValueError:

        send_message(
            chat_id,
            "❌ مبلغ نامعتبر است.\n\n"
            "لطفاً فقط عدد وارد کنید."
        )

        return True

    if amount <= 0:

        send_message(
            chat_id,
            "❌ مبلغ باید بیشتر از صفر باشد."
        )

        return True

    target_user_id = session["target_user_id"]
    action = session["action"]

    target_user = database.get_user(target_user_id)

    if target_user is None or not target_user["country"]:

        admin_sessions.pop(admin_id, None)

        send_message(
            chat_id,
            "❌ این کشور دیگر بازیکن ندارد."
        )

        return True

    country = target_user["country"]

    # =========================
    # افزایش
    # =========================

    if action == "increase":

        new_budget = target_user["budget"] + amount

        database.update_budget(
            target_user_id,
            new_budget
        )

        send_message(
            target_user_id,
            f"💰 مبلغ {amount:,} به کشور شما اضافه شد!"
        )

        send_message(
            chat_id,
            f"✅ مبلغ {amount:,} به کشور «{country}» اضافه شد."
        )

    # =========================
    # کاهش
    # =========================

    elif action == "decrease":

        if target_user["budget"] < amount:

            send_message(
                chat_id,
                "❌ موجودی این کشور برای این مقدار کافی نیست.\n\n"
                f"💰 موجودی فعلی: {target_user['budget']:,}"
            )

            return True

        new_budget = target_user["budget"] - amount

        database.update_budget(
            target_user_id,
            new_budget
        )

        send_message(
            target_user_id,
            f"💸 مبلغ {amount:,} از کشور شما کم شد!"
        )

        send_message(
            chat_id,
            f"✅ مبلغ {amount:,} از کشور «{country}» کم شد."
        )

    admin_sessions.pop(admin_id, None)

    return True


# =========================
# مدیریت آپدیت‌ها
# =========================

def handle_update(update):

    # =========================
    # پیام متنی
    # =========================

    if "message" in update:

        message = update["message"]

        chat_id = message["chat"]["id"]
        user_id = message["from"]["id"]

        text = message.get("text", "").strip()

        if not is_admin(user_id):
            return

        if user_id in admin_sessions:

            process_amount(
                chat_id,
                user_id,
                text
            )

            return

        return

    # =========================
    # Callback
    # =========================

    if "callback_query" not in update:
        return

    callback = update["callback_query"]

    admin_id = callback["from"]["id"]

    if not is_admin(admin_id):
        return

    data = callback.get("data")

    message = callback.get("message")

    if message is None:
        return

    chat_id = message["chat"]["id"]
    message_id = message["message_id"]

    # =========================
    # مدیریت کشورها
    # =========================

    if data == "admin_countries":

        admin_sessions.pop(admin_id, None)

        show_country_list(
            chat_id,
            message_id
        )

        return

    # =========================
    # انتخاب کشور
    # =========================

    if data.startswith("admin_country_"):

        try:
            target_user_id = int(
                data.replace("admin_country_", "")
            )
        except ValueError:
            return

        admin_sessions.pop(admin_id, None)

        show_country(
            chat_id,
            message_id,
            target_user_id
        )

        return

    # =========================
    # افزایش پول
    # =========================

    if data.startswith("admin_increase_"):

        try:
            target_user_id = int(
                data.replace("admin_increase_", "")
            )
        except ValueError:
            return

        start_increase(
            chat_id,
            message_id,
            admin_id,
            target_user_id
        )

        return

    # =========================
    # کاهش پول
    # =========================

    if data.startswith("admin_decrease_"):

        try:
            target_user_id = int(
                data.replace("admin_decrease_", "")
            )
        except ValueError:
            return

        start_decrease(
            chat_id,
            message_id,
            admin_id,
            target_user_id
        )

        return