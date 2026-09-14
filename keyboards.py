# ==============================
# World War - Keyboards
# ==============================


# =========================
# دکمه‌های انتخاب کشور
# =========================

def country_keyboard(selected_countries=None, user_country=None):

    selected_countries = selected_countries or set()

    countries = [
        ("🇮🇷", "ایران", "country_iran"),
        ("🇺🇸", "آمریکا", "country_usa"),
        ("🇮🇱", "اسرائیل", "country_israel"),

        ("🇷🇺", "روسیه", "country_russia"),
        ("🇯🇵", "ژاپن", "country_japan"),
        ("🇨🇳", "چین", "country_china"),

        ("🇬🇧", "انگلیس", "country_uk"),
        ("🇫🇷", "فرانسه", "country_france"),
        ("🇩🇪", "آلمان", "country_germany"),

        ("🇹🇷", "ترکیه", "country_turkey"),
        ("🇮🇳", "هند", "country_india"),
        ("🇰🇷", "کره جنوبی", "country_south_korea"),

        ("🇰🇵", "کره شمالی", "country_north_korea"),
        ("🇸🇦", "عربستان", "country_saudi_arabia"),
        ("🇦🇪", "امارات", "country_uae"),

        ("🇪🇬", "مصر", "country_egypt"),
        ("🇵🇰", "پاکستان", "country_pakistan"),
        ("🇺🇦", "اوکراین", "country_ukraine"),

        ("🇮🇹", "ایتالیا", "country_italy"),
        ("🇪🇸", "اسپانیا", "country_spain"),
        ("🇨🇦", "کانادا", "country_canada"),

        ("🇦🇺", "استرالیا", "country_australia"),
        ("🇧🇷", "برزیل", "country_brazil"),
        ("🇲🇽", "مکزیک", "country_mexico"),

        ("🇮🇩", "اندونزی", "country_indonesia"),
        ("🇻🇳", "ویتنام", "country_vietnam"),
        ("🇵🇱", "لهستان", "country_poland"),

        ("🇬🇷", "یونان", "country_greece"),
        ("🇮🇶", "عراق", "country_iraq"),
        ("🇶🇦", "قطر", "country_qatar")
    ]

    keyboard = []
    row = []

    for flag, name, callback in countries:

        if name == user_country:
            text = f"{flag} {name} ✅"
        elif name in selected_countries:
            text = f"{flag} {name} 🔒"
        else:
            text = f"{flag} {name}"

        row.append({
            "text": text,
            "callback_data": callback
        })

        if len(row) == 3:
            keyboard.append(row)
            row = []

    if row:
        keyboard.append(row)

    return {
        "inline_keyboard": keyboard
    }


# =========================
# منوی اصلی
# =========================

def main_menu_keyboard(is_admin=False):

    keyboard = [
        [
            {"text": "🌍 کشور من", "callback_data": "my_country"},
            {"text": "🔫 بازار تسلیحات", "callback_data": "arms_market"}
        ],
        [
            {"text": "🏢 شرکت‌های بین‌المللی", "callback_data": "international_companies"}
        ],
        [
            {"text": "📦 صادرات/واردات", "callback_data": "trade"}
        ],
        [
            {"text": "🏰 اتحاد", "callback_data": "alliance"}
        ],
        [
            {"text": "📢 صدور بیانیه", "callback_data": "statement"}
        ],
        [
            {"text": "⚔️ قوانین جنگ", "callback_data": "war_rules"}
        ],
        [
            {"text": "💥 حمله نظامی", "callback_data": "attack"}
        ]
    ]

    # فقط برای ادمین
    if is_admin:
        keyboard.append([
            {
                "text": "👑 مدیریت کشورها",
                "callback_data": "admin_countries"
            }
        ])

    return {
        "inline_keyboard": keyboard
    }


# =========================
# منوی شرکت‌های بین‌المللی
# =========================

def international_companies_keyboard(companies):

    keyboard = []

    for company in companies:
        keyboard.append([
            {
                "text": (
                    f"{company['emoji']} "
                    f"{company['name']}"
                ),
                "callback_data": f"company_view_{company['id']}"
            }
        ])

    keyboard.append([
        {
            "text": "🔙 بازگشت",
            "callback_data": "back_main_menu"
        }
    ])

    return {
        "inline_keyboard": keyboard
    }


# =========================
# صفحه شرکت
# =========================

def company_keyboard(company_id, is_owner=False, is_employee=False):

    keyboard = []

    if not is_owner and not is_employee:
        keyboard.append([
            {
                "text": "💰 خرید شرکت",
                "callback_data": f"company_buy_{company_id}"
            }
        ])

        keyboard.append([
            {
                "text": "👷 استخدام در شرکت",
                "callback_data": f"company_join_{company_id}"
            }
        ])

    if is_employee:
        keyboard.append([
            {
                "text": "🚪 ترک شرکت",
                "callback_data": f"company_leave_{company_id}"
            }
        ])

    if is_owner:
        keyboard.append([
            {
                "text": "💰 فروش شرکت",
                "callback_data": f"company_sell_confirm_{company_id}"
            }
        ])

    keyboard.append([
        {
            "text": "🔙 بازگشت",
            "callback_data": "international_companies"
        }
    ])

    return {
        "inline_keyboard": keyboard
    }


# =========================
# تأیید فروش شرکت
# =========================

def company_sell_confirm_keyboard(company_id):

    return {
        "inline_keyboard": [
            [
                {
                    "text": "✅ بله، بفروش",
                    "callback_data": f"company_sell_{company_id}"
                },
                {
                    "text": "❌ لغو",
                    "callback_data": f"company_view_{company_id}"
                }
            ]
        ]
    }


# =========================
# منوی بازار تسلیحات
# =========================

def shop_keyboard():
    return {
        "inline_keyboard": [
            [
                {"text": "⚔️ نیروی زمینی", "callback_data": "shop_ground"}
            ],
            [
                {"text": "✈️ نیروی هوایی", "callback_data": "shop_air"}
            ],
            [
                {"text": "⚓ نیروی دریایی", "callback_data": "shop_navy"}
            ],
            [
                {"text": "🚀 موشک", "callback_data": "shop_missiles"}
            ],
            [
                {"text": "🛬 پهپاد", "callback_data": "shop_drones"}
            ],
            [
                {"text": "🚁 بالگرد", "callback_data": "shop_helicopters"}
            ],
            [
                {"text": "🛡️ پدافند", "callback_data": "shop_defense"}
            ],
            [
                {"text": "🚜 تانک", "callback_data": "shop_tanks"}
            ],
            [
                {"text": "💻 سیستم", "callback_data": "shop_systems"}
            ],
            [
                {"text": "🏙️ امکانات مردمی", "callback_data": "shop_civilian"}
            ],
            [
                {"text": "⛏️ معادن", "callback_data": "shop_mines"}
            ],
            [
                {"text": "🔙 بازگشت", "callback_data": "back_main_menu"}
            ]
        ]
    }


# =========================
# ساخت دکمه‌های آیتم‌ها
# =========================

def shop_items_keyboard(items, back_callback="shop_menu"):
    keyboard = []

    for item in items:
        keyboard.append([
            {
                "text": f"{item['name']} | 💰 {item['price']:,}",
                "callback_data": f"shop_item_{item['id']}"
            }
        ])

    keyboard.append([
        {"text": "🔙 بازگشت", "callback_data": back_callback}
    ])

    return {
        "inline_keyboard": keyboard
    }


# =========================
# دکمه‌های معادن
# =========================

def mines_keyboard(items):
    keyboard = []

    for item in items:
        keyboard.append([
            {
                "text": (
                    f"{item['name']} | "
                    f"💰 {item['price']:,} | "
                    f"📈 {item['income']:,}/روز"
                ),
                "callback_data": f"shop_item_{item['id']}"
            }
        ])

    keyboard.append([
        {"text": "🔙 بازگشت", "callback_data": "shop_menu"}
    ])

    return {
        "inline_keyboard": keyboard
    }


# =========================
# صفحه خرید آیتم
# =========================

def shop_item_keyboard(item_id):
    return {
        "inline_keyboard": [
            [
                {"text": "➕ ۱+", "callback_data": f"shop_add_1_{item_id}"},
                {"text": "➕ ۱۰+", "callback_data": f"shop_add_10_{item_id}"}
            ],
            [
                {"text": "➕ ۱۰۰+", "callback_data": f"shop_add_100_{item_id}"},
                {"text": "➕ ۱۰۰۰+", "callback_data": f"shop_add_1000_{item_id}"}
            ],
            [
                {"text": "🔢 تعداد دلخواه", "callback_data": f"shop_custom_{item_id}"}
            ],
            [
                {"text": "🛒 سبد خرید", "callback_data": "shop_cart"}
            ],
            [
                {"text": "🛍️ ادامه خرید", "callback_data": "shop_menu"}
            ]
        ]
    }


# =========================
# سبد خرید
# =========================

def cart_keyboard(cart_items):
    keyboard = []

    for item in cart_items:
        keyboard.append([
            {
                "text": f"❌ {item['name']} × {item['quantity']}",
                "callback_data": f"shop_remove_{item['id']}"
            }
        ])

    keyboard.append([
        {"text": "💳 تسویه خرید", "callback_data": "shop_checkout"}
    ])

    keyboard.append([
        {"text": "🛍️ ادامه خرید", "callback_data": "shop_menu"}
    ])

    keyboard.append([
        {"text": "❌ لغو", "callback_data": "shop_cancel"}
    ])

    return {
        "inline_keyboard": keyboard
    }


# ==============================
# دکمه‌های کشورهای قابل حمله
# ==============================

def attack_targets_keyboard(targets):
    keyboard = []

    for target in targets:
        keyboard.append([
            {
                "text": target["country"],
                "callback_data": f"attack_target_{target['user_id']}"
            }
        ])

    keyboard.append([
        {
            "text": "🔙 بازگشت",
            "callback_data": "back_main_menu"
        }
    ])

    return {
        "inline_keyboard": keyboard
    }


# ==============================
# دکمه‌های درصد حمله
# ==============================

def attack_percent_keyboard():
    return {
        "inline_keyboard": [
            [
                {
                    "text": "25%",
                    "callback_data": "attack_percent_25"
                },
                {
                    "text": "50%",
                    "callback_data": "attack_percent_50"
                }
            ],
            [
                {
                    "text": "75%",
                    "callback_data": "attack_percent_75"
                },
                {
                    "text": "100%",
                    "callback_data": "attack_percent_100"
                }
            ],
            [
                {
                    "text": "🔢 تایپ درصد دلخواه",
                    "callback_data": "attack_custom_percent"
                }
            ],
            [
                {
                    "text": "⚔️ حمله",
                    "callback_data": "attack_execute"
                }
            ],
            [
                {
                    "text": "❌ لغو",
                    "callback_data": "attack_cancel"
                }
            ]
        ]
    }


# ==============================
# دکمه‌های صادرات / واردات
# ==============================

def trade_items_keyboard(items):

    keyboard = []

    for item in items:

        keyboard.append([
            {
                "text": (
                    f"{item['name']} | "
                    f"📦 {item['quantity']:,}"
                ),
                "callback_data": f"trade_item_{item['id']}"
            }
        ])

    keyboard.append([
        {
            "text": "🔙 بازگشت",
            "callback_data": "trade_main_menu"
        }
    ])

    return {
        "inline_keyboard": keyboard
    }


# ==============================
# وقتی کالایی وجود ندارد
# ==============================

def trade_empty_keyboard():

    return {
        "inline_keyboard": [
            [
                {
                    "text": "🛍️ بازار تسلیحات",
                    "callback_data": "arms_market"
                }
            ],
            [
                {
                    "text": "🔙 بازگشت",
                    "callback_data": "trade_main_menu"
                }
            ]
        ]
    }


# ==============================
# لغو
# ==============================

def trade_cancel_keyboard():

    return {
        "inline_keyboard": [
            [
                {
                    "text": "❌ لغو",
                    "callback_data": "trade_cancel"
                }
            ]
        ]
    }


# ==============================
# قیمت
# ==============================

def trade_price_keyboard():

    return {
        "inline_keyboard": [
            [
                {
                    "text": "🆓 ارسال رایگان",
                    "callback_data": "trade_free"
                }
            ],
            [
                {
                    "text": "❌ لغو",
                    "callback_data": "trade_cancel"
                }
            ]
        ]
    }


# ==============================
# کشورهای مقصد
# ==============================

def trade_countries_keyboard(targets):

    keyboard = []

    for target in targets:

        keyboard.append([
            {
                "text": f"🌍 {target['country']}",
                "callback_data": (
                    f"trade_country_{target['user_id']}"
                )
            }
        ])

    keyboard.append([
        {
            "text": "❌ لغو",
            "callback_data": "trade_cancel"
        }
    ])

    return {
        "inline_keyboard": keyboard
    }


# ==============================
# تأیید معامله
# ==============================

def trade_confirm_keyboard():

    return {
        "inline_keyboard": [
            [
                {
                    "text": "✅ تایید",
                    "callback_data": "trade_confirm"
                },
                {
                    "text": "❌ لغو",
                    "callback_data": "trade_cancel"
                }
            ]
        ]
    }


# ==============================
# پیشنهاد برای خریدار
# ==============================

def trade_buyer_keyboard(offer_id):

    return {
        "inline_keyboard": [
            [
                {
                    "text": "✅ تایید و خرید",
                    "callback_data": f"trade_buy_{offer_id}"
                }
            ],
            [
                {
                    "text": "❌ خیر",
                    "callback_data": f"trade_reject_{offer_id}"
                }
            ]
        ]
    }


# ==============================
# بازگشت
# ==============================

def trade_back_keyboard():

    return {
        "inline_keyboard": [
            [
                {
                    "text": "🔙 بازگشت",
                    "callback_data": "trade_main_menu"
                }
            ]
        ]
    }


# ==============================
# منوی اصلی تجارت
# ==============================

def trade_main_menu_keyboard():

    return {
        "inline_keyboard": [
            [
                {
                    "text": "🔙 بازگشت به منوی اصلی",
                    "callback_data": "trade_main_menu"
                }
            ]
        ]
    }