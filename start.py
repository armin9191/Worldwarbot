# ==============================
# World War - Start Menu
# ==============================

import database
import keyboards
import config

# ارسال پیام از bot.py
send_message = None
edit_message = None
calculate_defense_power = None


def setup(
    send_message_function,
    edit_message_function,
    defense_power_function=None
):
    global send_message
    global edit_message
    global calculate_defense_power

    send_message = send_message_function
    edit_message = edit_message_function
    calculate_defense_power = defense_power_function


# =========================
# لیست کشورها
# =========================

COUNTRIES = {
    "country_iran": "ایران",
    "country_usa": "آمریکا",
    "country_israel": "اسرائیل",
    "country_russia": "روسیه",
    "country_japan": "ژاپن",
    "country_china": "چین",
    "country_uk": "انگلیس",
    "country_france": "فرانسه",
    "country_germany": "آلمان",
    "country_turkey": "ترکیه",
    "country_india": "هند",
    "country_south_korea": "کره جنوبی",
    "country_north_korea": "کره شمالی",
    "country_saudi_arabia": "عربستان",
    "country_uae": "امارات",
    "country_egypt": "مصر",
    "country_pakistan": "پاکستان",
    "country_ukraine": "اوکراین",
    "country_italy": "ایتالیا",
    "country_spain": "اسپانیا",
    "country_canada": "کانادا",
    "country_australia": "استرالیا",
    "country_brazil": "برزیل",
    "country_mexico": "مکزیک",
    "country_indonesia": "اندونزی",
    "country_vietnam": "ویتنام",
    "country_poland": "لهستان",
    "country_greece": "یونان",
    "country_iraq": "عراق",
    "country_qatar": "قطر"
}


# =========================
# صفحه انتخاب کشور
# =========================

def show_country_selection(chat_id, user_id):

    if send_message is None:
        return

    user = database.get_or_create_user(user_id)

    selected = database.get_selected_countries()

    selected_countries = {
        item["country"]
        for item in selected
    }

    user_country = user.get("country")

    send_message(
        chat_id,
        "🌍 فرمانده، ابتدا کشور خود را انتخاب کن:",
        keyboards.country_keyboard(
            selected_countries,
            user_country
        )
    )


# =========================
# منوی اصلی
# =========================

def show_main_menu(chat_id, user, message_id=None):

    if send_message is None:
        return

    is_admin = chat_id in getattr(config, "ADMINS", [])

    text = (
        "سلام فرمانده! 👋\n"
        "خوش برگشتی.\n\n"
        f"🌍 کشور: {user['country']}\n"
        f"💰 بودجه: {user['budget']:,}\n"
        f"❤️ HP: {user['hp']}%\n\n"
        "فرمانده، دستور بعدی را انتخاب کن:"
    )

    keyboard = keyboards.main_menu_keyboard(
        is_admin=is_admin
    )

    if message_id is not None and edit_message is not None:

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
# گرفتن تعداد آیتم
# =========================

def get_quantity(inventory, item_id):

    return inventory.get(
        item_id,
        0
    )


# =========================
# محاسبه درآمد روزانه معادن
# =========================

def calculate_mine_income(inventory):

    diamond = get_quantity(
        inventory,
        "diamond_mine"
    )

    gold = get_quantity(
        inventory,
        "gold_mine"
    )

    silver = get_quantity(
        inventory,
        "silver_mine"
    )

    diamond_income = diamond * 15000000
    gold_income = gold * 10000000
    silver_income = silver * 5000000

    return (
        diamond_income
        + gold_income
        + silver_income
    )


# =========================
# داشبورد کشور
# =========================

def show_country_dashboard(
    chat_id,
    message_id
):

    user = database.get_or_create_user(
        chat_id
    )

    inventory = database.get_inventory(
        chat_id
    )

    country = user["country"]
    hp = user["hp"]
    budget = user["budget"]

    daily_mine_income = calculate_mine_income(
        inventory
    )

    daily_income = daily_mine_income

    # =========================
    # قدرت دفاعی کشور
    # =========================

    if calculate_defense_power is not None:
        defense_power = calculate_defense_power(
            chat_id
        )
    else:
        defense_power = 0

    text = (
        "━━━━━━━━━━━━━━━━━━━━\n"
        "🏛️ *داشبورد فرماندهی*\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"

        f"🌍 *{country}*\n"
        f"❤️ HP: `{hp}%`\n"
        f"💰 درآمد روزانه: `{daily_income:,}`\n"
        f"🏦 بودجه دولت: `{budget:,}`\n"
        f"🛡️ قدرت دفاعی: `{defense_power:,}`\n\n"

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

    edit_message(
        chat_id,
        message_id,
        text,
        keyboard
    )


# =========================
# نمایش دوباره انتخاب کشور
# =========================

def refresh_country_selection(
    chat_id,
    message_id,
    user_id,
    error_text=None
):

    user = database.get_or_create_user(user_id)

    selected = database.get_selected_countries()

    selected_countries = {
        item["country"]
        for item in selected
    }

    user_country = user.get("country")

    if error_text:
        text = (
            f"{error_text}\n\n"
            "🌍 کشور خود را انتخاب کن:"
        )
    else:
        text = "🌍 فرمانده، ابتدا کشور خود را انتخاب کن:"

    edit_message(
        chat_id,
        message_id,
        text,
        keyboards.country_keyboard(
            selected_countries,
            user_country
        )
    )


# =========================
# مدیریت آپدیت‌ها
# =========================

def handle_update(update):

    message = update.get("message")

    if message:

        chat = message.get(
            "chat",
            {}
        )

        chat_id = chat.get("id")

        text = message.get(
            "text",
            ""
        )

        if not chat_id:
            return

        if text == "/start":

            user = database.get_or_create_user(
                chat_id
            )

            if user["country"] is None:

                show_country_selection(
                    chat_id,
                    chat_id
                )

            else:

                show_main_menu(
                    chat_id,
                    user
                )

    # =========================
    # کلیک دکمه
    # =========================

    callback_query = update.get(
        "callback_query"
    )

    if callback_query:

        data = callback_query.get(
            "data"
        )

        message = callback_query.get(
            "message",
            {}
        )

        chat = message.get(
            "chat",
            {}
        )

        chat_id = chat.get(
            "id"
        )

        message_id = message.get(
            "message_id"
        )

        user_id = callback_query.get(
            "from",
            {}
        ).get(
            "id"
        )

        if not chat_id or not user_id:
            return

        # =========================
        # انتخاب کشور
        # =========================

        if data in COUNTRIES:

            country = COUNTRIES[data]

            database.get_or_create_user(
                user_id
            )

            result = database.set_country(
                user_id,
                country
            )

            # =========================
            # انتخاب موفق
            # =========================

            if result == "success":

                user = database.get_user(
                    user_id
                )

                show_main_menu(
                    chat_id,
                    user,
                    message_id
                )

                return

            # =========================
            # همین کشور قبلاً برای خود کاربر بوده
            # =========================

            if result == "already_owned":

                user = database.get_user(
                    user_id
                )

                show_main_menu(
                    chat_id,
                    user,
                    message_id
                )

                return

            # =========================
            # کشور توسط شخص دیگری گرفته شده
            # =========================

            if result == "occupied":

                refresh_country_selection(
                    chat_id,
                    message_id,
                    user_id,
                    "❌ این کشور قبلاً توسط یک کاربر انتخاب شده است."
                )

                return

            # =========================
            # کاربر از قبل کشور دارد
            # =========================

            if result == "has_country":

                user = database.get_user(
                    user_id
                )

                show_main_menu(
                    chat_id,
                    user,
                    message_id
                )

                return

            # =========================
            # خطای دیتابیس
            # =========================

            refresh_country_selection(
                chat_id,
                message_id,
                user_id,
                "❌ در انتخاب کشور مشکلی پیش آمد. دوباره تلاش کن."
            )

            return

        # =========================
        # کشور من
        # =========================

        if data == "my_country":

            show_country_dashboard(
                chat_id,
                message_id
            )

            return

        # =========================
        # برگشت به منوی اصلی
        # =========================

        if data == "back_main_menu":

            user = database.get_user(
                chat_id
            )

            if user and user["country"]:

                show_main_menu(
                    chat_id,
                    user,
                    message_id
                )

            return
