# ==============================
# World War - Reports System
# ==============================

import config


# =========================================================
# اتصال ارسال پیام
# =========================================================

send_message = None


def setup(send_message_function):
    global send_message

    send_message = send_message_function


# =========================================================
# نام تجهیزات
# =========================================================

ITEM_NAMES = {
    "kheybershekan": "خیبرشکن",
    "thaad": "تاد",
    "patriot": "پاتریوت",
    "phalanx": "فالانکس",

    "commander": "فرمانده",
    "soldier": "نیروی زمینی",
    "police": "پلیس",
    "border_guard": "مرزبانی",

    "f16": "F-16",
    "f18": "F-18",
    "f22": "F-22",
    "f35": "F-35",

    "b1": "B-1",
    "b2": "B-2",
    "b52": "B-52",

    "aircraft_carrier": "ناو هواپیمابر",
    "war_boat": "قایق جنگی",
    "idaho_submarine": "زیردریایی آیداهو",

    "gerald_ford": "ناو جرالد فورد",
    "abraham_lincoln": "ناو آبراهام لینکلن",

    "precision_missile": "موشک دقیق",
    "cruise_missile": "موشک کروز",

    "suicide_drone": "پهپاد انتحاری",
    "precision_drone": "پهپاد دقیق",
    "recon_drone": "پهپاد شناسایی",

    "crocodile_helicopter": "بالگرد کروکودیل",
    "apache": "آپچی",
    "cobra": "کبرا",
    "bell12": "بل ۱۲",

    "zolfaghar": "ذوالفقار",
    "panther": "پانتر",
    "karrar": "کرار",

    "diamond_mine": "معدن الماس",
    "gold_mine": "معدن طلا",
    "silver_mine": "معدن نقره",
}


# =========================================================
# پرچم کشورها
# =========================================================

COUNTRY_FLAGS = {
    "ایران": "🇮🇷",
    "آمریکا": "🇺🇸",
    "اسرائیل": "🇮🇱",
    "روسیه": "🇷🇺",
    "ژاپن": "🇯🇵",
    "چین": "🇨🇳",
    "آلمان": "🇩🇪",
    "فرانسه": "🇫🇷",
    "انگلیس": "🇬🇧",
    "ایتالیا": "🇮🇹",
    "اسپانیا": "🇪🇸",
    "ترکیه": "🇹🇷",
    "عراق": "🇮🇶",
    "عربستان": "🇸🇦",
    "امارات": "🇦🇪",
    "قطر": "🇶🇦",
    "هند": "🇮🇳",
    "پاکستان": "🇵🇰",
    "کره جنوبی": "🇰🇷",
    "کره شمالی": "🇰🇵",
    "اوکراین": "🇺🇦",
    "کانادا": "🇨🇦",
    "استرالیا": "🇦🇺",
    "برزیل": "🇧🇷",
    "مکزیک": "🇲🇽",
    "مصر": "🇪🇬",
    "آفریقای جنوبی": "🇿🇦",
    "یونان": "🇬🇷",
    "سوئد": "🇸🇪",
    "هلند": "🇳🇱",
}


# =========================================================
# ارسال گزارش خرید
# =========================================================

def send_purchase_report(
    country,
    items,
    total_price
):

    if send_message is None:
        return

    flag = COUNTRY_FLAGS.get(
        country,
        "🌍"
    )

    lines = []

    for item_id, quantity in items.items():

        if quantity <= 0:
            continue

        item_name = ITEM_NAMES.get(
            item_id,
            item_id
        )

        lines.append(
            f"• {item_name} × {quantity:,}"
        )

    if not lines:
        return

    text = (
        "🛒 *خرید تسلیحاتی جدید!*\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"🌍 کشور: {flag} *{country}*\n\n"
        "📦 *تجهیزات خریداری‌شده:*\n"
        + "\n".join(lines)
        + "\n\n"
        f"💰 قیمت کل: `{total_price:,}`\n"
        "━━━━━━━━━━━━━━━━━━━━"
    )

    send_message(
        config.STATEMENT_CHANNEL_ID,
        text
    )


# =========================================================
# ارسال گزارش حمله
# =========================================================

def send_attack_report(
    attacker_country,
    defender_country,
    percent,
    attack_power,
    defense_power,
    damage_percent,
    winner,
    destroyed=False,
    compensation=0
):

    if send_message is None:
        return

    attacker_flag = COUNTRY_FLAGS.get(
        attacker_country,
        "🌍"
    )

    defender_flag = COUNTRY_FLAGS.get(
        defender_country,
        "🌍"
    )

    if winner == "attack":

        winner_text = (
            f"🏆 *برنده: حمله*\n"
            f"💥 کشور {defender_flag} *{defender_country}* "
        )

        if destroyed:
            winner_text += (
                "کاملاً نابود و حذف شد!"
            )
        else:
            winner_text += (
                "در این حمله شکست خورد."
            )

    else:

        winner_text = (
            f"🏆 *برنده: دفاع*\n"
            f"🛡 کشور {defender_flag} *{defender_country}* "
            "در برابر حمله دفاع کرد."
        )

    text = (
        "⚔️ *گزارش حمله نظامی*\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"🗡 حمله‌کننده: {attacker_flag} "
        f"*{attacker_country}*\n"
        f"🛡 دفاع‌کننده: {defender_flag} "
        f"*{defender_country}*\n\n"
        f"{winner_text}\n\n"
        f"📦 درصد تجهیزات استفاده‌شده: `{percent}%`\n"
        f"💪 قدرت حمله: `{attack_power:,}`\n"
        f"🛡 قدرت دفاع: `{defense_power:,}`\n"
        f"📊 درصد آسیب: `{damage_percent:.2f}%`\n"
    )

    if destroyed:
        text += (
            "\n☢️ این کشور الان آزاده و "
            "کس دیگه‌ای می‌تونه انتخابش کنه.\n"
        )

    if compensation > 0:
        text += (
            f"\n💸 غرامت دریافتی: `{compensation:,}`\n"
        )

    text += (
        "━━━━━━━━━━━━━━━━━━━━"
    )

    send_message(
        config.STATEMENT_CHANNEL_ID,
        text
)
