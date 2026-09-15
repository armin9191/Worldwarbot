# ==============================
# World War - Arms Shop
# ==============================

import keyboards
import database
import reports


send_message = None
edit_message = None


def setup(send_message_function, edit_message_function):
    global send_message
    global edit_message

    send_message = send_message_function
    edit_message = edit_message_function


# =========================
# سبد خرید موقت کاربران
# =========================

carts = {}

# کاربرانی که منتظر تعداد دلخواه هستند
waiting_custom_quantity = {}


# =========================
# اطلاعات کالاها
# =========================

SHOP_ITEMS = {

    "ground": [
        {"id": "commander", "name": "🎖️ فرمانده", "price": 40000},
        {"id": "soldier", "name": "🪖 سرباز", "price": 20000},
        {"id": "police", "name": "👮‍♂️ پلیس", "price": 20000},
        {"id": "border_guard", "name": "🛡️ مرزبان", "price": 30000},
        {"id": "bomb_disarmer", "name": "🔧 خنثی‌کننده بمب", "price": 50000},
        {"id": "bomber", "name": "💣 بمب‌گذار", "price": 40000},
        {"id": "special_unit", "name": "🦅 یگان ویژه", "price": 30000},
        {"id": "mine_layer", "name": "🌋 مین‌گذار", "price": 25000},
        {"id": "mine_disarmer", "name": "🧹 خنثی‌کننده مین", "price": 30000},
        {"id": "spy", "name": "🕵️‍♂️ جاسوس", "price": 50000},
        {"id": "sniper", "name": "🎯 تک‌تیرانداز", "price": 20000},
        {"id": "rpg", "name": "💥 آرپی‌جی‌زن", "price": 20000}
    ],

    "air": [
        {"id": "f16", "name": "✈️ F-16", "price": 1000000},
        {"id": "f18", "name": "✈️ F-18", "price": 1200000},
        {"id": "f22", "name": "🛩️ F-22", "price": 1500000},
        {"id": "f35", "name": "✈️ F-35", "price": 12000000},
        {"id": "b1", "name": "💣 B-1", "price": 1000000},
        {"id": "b2", "name": "💣 B-2", "price": 40000000},
        {"id": "b52", "name": "💣 B-52", "price": 35000000}
    ],

    "navy": [
        {"id": "tanker", "name": "🛢️ نفتکش", "price": 1000000},
        {"id": "trade_ship", "name": "🚢 کشتی صادرات و واردات", "price": 1000000},
        {"id": "aircraft_carrier", "name": "🛳️ ناو هواپیمابر", "price": 5000000},
        {"id": "war_boat", "name": "🚤 قایق جنگی", "price": 200000},
        {"id": "idaho_submarine", "name": "🤿 زیردریایی ایداهو", "price": 500000},
        {"id": "gerald_ford", "name": "⚔️ ناو جرالد فورد", "price": 10000000}
    ],

    "missiles": [
        {"id": "precision_missile", "name": "🎯 موشک نقطه‌زن", "price": 200000},
        {"id": "cruise_missile", "name": "💨 موشک کروز", "price": 300000},
        {"id": "kheybershekan", "name": "⚡ موشک خیبرشکن", "price": 500000},
        {"id": "khorramshahr4", "name": "🔥 خرمشهر ۴", "price": 3000000},
        {"id": "df26", "name": "DF-26", "price": 5000000},
        {"id": "atomic_bomb", "name": "☢️ بمب اتم", "price": 1000000000}
    ],

    "drones": [
        {"id": "suicide_drone", "name": "💥 پهپاد انتحاری", "price": 100000},
        {"id": "precision_drone", "name": "🎯 پهپاد نقطه‌زن", "price": 200000},
        {"id": "recon_drone", "name": "👁️ پهپاد شناسایی", "price": 300000}
    ],

    "helicopters": [
        {"id": "crocodile_helicopter", "name": "🐊 بالگرد تمساح", "price": 50000},
        {"id": "apache", "name": "🦅 آپاچی", "price": 100000},
        {"id": "cobra", "name": "🐍 کبری", "price": 150000},
        {"id": "bell12", "name": "🔔 بل ۱۲", "price": 200000}
    ],

    "defense": [
        {"id": "patriot", "name": "🇺🇸 پاتریوت", "price": 100000},
        {"id": "phalanx", "name": "🌀 فلانکس", "price": 100000},
        {"id": "thaad", "name": "🔵 تاد", "price": 300000}
    ],

    "tanks": [
        {"id": "zolfaghar", "name": "⚔️ ذوالفقار", "price": 30000},
        {"id": "panther", "name": "🐆 پنتر", "price": 50000},
        {"id": "karrar", "name": "🦁 کرار", "price": 150000}
    ],

    "systems": [
        {"id": "asset_hack", "name": "🔓 هک دارایی", "price": 100000},
        {"id": "asset_anti_hack", "name": "🔒 ضد هک دارایی", "price": 200000},
        {"id": "military_hack", "name": "⚔️ هک نظامی", "price": 400000},
        {"id": "military_anti_hack", "name": "🛡️ ضد هک نظامی", "price": 600000}
    ],

    "civilian": [
        {"id": "supermarket", "name": "🛒 سوپرمارکت", "price": 30000},
        {"id": "school", "name": "🏫 مدرسه", "price": 100000},
        {"id": "kindergarten", "name": "🎒 مهدکودک", "price": 50000},
        {"id": "mall", "name": "🏬 پاساژ", "price": 500000},
        {"id": "shelter", "name": "⛺ پناهگاه", "price": 700000},
        {"id": "pool", "name": "🏊‍♂️ استخر", "price": 50000},
        {"id": "hotel", "name": "🏨 هتل", "price": 200000},
        {"id": "metro", "name": "🚇 مترو", "price": 5000000},
        {"id": "bus", "name": "🚌 اتوبوس", "price": 20000},
        {"id": "airplane", "name": "✈️ هواپیما", "price": 1000000},
        {"id": "amusement_park", "name": "🎡 شهربازی", "price": 300000}
    ],

    "mines": [
        {
            "id": "diamond_mine",
            "name": "💎 معدن الماس",
            "price": 30000000,
            "income": 15000000
        },
        {
            "id": "gold_mine",
            "name": "🥇 معدن طلا",
            "price": 20000000,
            "income": 10000000
        },
        {
            "id": "silver_mine",
            "name": "🥈 معدن نقره",
            "price": 10000000,
            "income": 5000000
        }
    ]
}


# =========================
# نام دسته‌ها
# =========================

CATEGORY_NAMES = {
    "ground": "⚔️ نیروی زمینی",
    "air": "✈️ نیروی هوایی",
    "navy": "⚓ نیروی دریایی",
    "missiles": "🚀 موشک",
    "drones": "🛬 پهپاد",
    "helicopters": "🚁 بالگرد",
    "defense": "🛡️ پدافند",
    "tanks": "🚜 تانک",
    "systems": "💻 سیستم",
    "civilian": "🏙️ امکانات مردمی",
    "mines": "⛏️ معادن"
}


# =========================
# پیدا کردن آیتم
# =========================

def find_item(item_id):

    for category_items in SHOP_ITEMS.values():

        for item in category_items:

            if item["id"] == item_id:
                return item

    return None


# =========================
# نمایش بازار
# =========================

def show_shop(chat_id, message_id=None):

    text = (
        "🔫 بازار تسلیحات\n\n"
        "فرمانده، دسته مورد نظر را انتخاب کن:"
    )

    if message_id is not None:

        edit_message(
            chat_id,
            message_id,
            text,
            keyboards.shop_keyboard()
        )

    else:

        send_message(
            chat_id,
            text,
            keyboards.shop_keyboard()
        )


# =========================
# نمایش دسته
# =========================

def show_category(chat_id, message_id, category):

    items = SHOP_ITEMS.get(category)

    if items is None:
        return

    category_name = CATEGORY_NAMES.get(
        category,
        "🔫 بازار"
    )

    if category == "mines":

        text = (
            f"{category_name}\n\n"
            "قیمت خرید و درآمد روزانه:"
        )

        keyboard = keyboards.mines_keyboard(items)

    else:

        text = (
            f"{category_name}\n\n"
            "آیتم مورد نظر را انتخاب کن:"
        )

        keyboard = keyboards.shop_items_keyboard(
            items
        )

    # =========================
    # دکمه خالی کردن سبد
    # =========================

    keyboard["inline_keyboard"].append(
        [
            {
                "text": "🗑️ خالی کردن سبد",
                "callback_data": "shop_clear_cart"
            }
        ]
    )

    edit_message(
        chat_id,
        message_id,
        text,
        keyboard
    )


# =========================
# نمایش صفحه خرید آیتم
# =========================

def show_item(chat_id, message_id, item, quantity=1):

    user = database.get_or_create_user(chat_id)

    total_price = item["price"] * quantity

    if user["budget"] >= total_price:
        budget_status = "✅ بودجه کافی است"
    else:
        budget_status = "❌ بودجه کافی نیست"

    text = (
        f"{item['name']}\n\n"
        f"💰 بودجه شما: {user['budget']:,}\n"
        f"📦 تعداد: {quantity:,}\n"
        f"💵 قیمت واحد: {item['price']:,}\n"
        f"💳 قیمت کل: {total_price:,}\n\n"
        f"{budget_status}"
    )

    edit_message(
        chat_id,
        message_id,
        text,
        keyboards.shop_item_keyboard(item["id"])
    )


# =========================
# اضافه کردن به سبد
# =========================

def add_to_cart(user_id, item_id, quantity):

    item = find_item(item_id)

    if item is None:
        return

    if user_id not in carts:
        carts[user_id] = {}

    if item_id not in carts[user_id]:

        carts[user_id][item_id] = {
            "id": item_id,
            "name": item["name"],
            "price": item["price"],
            "quantity": 0
        }

    carts[user_id][item_id]["quantity"] += quantity


# =========================
# تعداد فعلی آیتم
# =========================

def get_cart_quantity(user_id, item_id):

    if user_id not in carts:
        return 0

    if item_id not in carts[user_id]:
        return 0

    return carts[user_id][item_id]["quantity"]


# =========================
# نمایش سبد خرید
# =========================

def show_cart(chat_id, message_id):

    user = database.get_or_create_user(chat_id)

    cart = carts.get(chat_id, {})

    if not cart:

        text = (
            "🛒 سبد خرید\n\n"
            "سبد خرید شما خالی است."
        )

        edit_message(
            chat_id,
            message_id,
            text,
            {
                "inline_keyboard": [
                    [
                        {
                            "text": "🛍️ ادامه خرید",
                            "callback_data": "shop_menu"
                        }
                    ]
                ]
            }
        )

        return

    total_price = 0
    cart_items = []

    for item in cart.values():

        item_total = (
            item["price"] *
            item["quantity"]
        )

        total_price += item_total

        cart_items.append(item)

    if user["budget"] >= total_price:
        budget_status = "✅ بودجه کافی است"
    else:
        budget_status = "❌ بودجه کافی نیست"

    text = (
        "🛒 سبد خرید\n\n"
        f"💰 بودجه شما: {user['budget']:,}\n"
        f"💳 قیمت کل خرید: {total_price:,}\n\n"
        f"{budget_status}\n\n"
        "برای حذف یک آیتم، روی دکمه همان آیتم بزن:"
    )

    cart_keyboard = keyboards.cart_keyboard(cart_items)

    cart_keyboard["inline_keyboard"].append(
        [
            {
                "text": "🗑️ خالی کردن سبد",
                "callback_data": "shop_clear_cart"
            }
        ]
    )

    edit_message(
        chat_id,
        message_id,
        text,
        cart_keyboard
    )


# =========================
# حذف آیتم از سبد
# =========================

def remove_from_cart(user_id, item_id):

    if user_id not in carts:
        return

    if item_id in carts[user_id]:

        del carts[user_id][item_id]

    if not carts[user_id]:

        del carts[user_id]


# =========================
# لغو خرید
# =========================

def cancel_cart(user_id):

    if user_id in carts:
        del carts[user_id]

    if user_id in waiting_custom_quantity:
        del waiting_custom_quantity[user_id]


# =========================
# تسویه خرید
# =========================

def checkout(chat_id, message_id):

    user = database.get_or_create_user(chat_id)

    cart = carts.get(chat_id, {})

    if not cart:

        show_cart(
            chat_id,
            message_id
        )

        return

    total_price = 0

    for item in cart.values():

        total_price += (
            item["price"] *
            item["quantity"]
        )

    # =========================
    # بررسی بودجه
    # =========================

    if user["budget"] < total_price:

        text = (
            "🛒 سبد خرید\n\n"
            f"💰 بودجه شما: {user['budget']:,}\n"
            f"💳 قیمت کل خرید: {total_price:,}\n\n"
            "❌ بودجه کافی نیست!\n"
            "خرید انجام نشد."
        )

        edit_message(
            chat_id,
            message_id,
            text,
            keyboards.cart_keyboard(
                list(cart.values())
            )
        )

        return

    # =========================
    # کم کردن پول
    # =========================

    success = database.decrease_budget(
        chat_id,
        total_price
    )

    if not success:

        text = (
            "❌ خرید انجام نشد.\n\n"
            "بودجه کافی نیست."
        )

        edit_message(
            chat_id,
            message_id,
            text,
            {
                "inline_keyboard": [
                    [
                        {
                            "text": "🛒 سبد خرید",
                            "callback_data": "shop_cart"
                        }
                    ],
                    [
                        {
                            "text": "🛍️ ادامه خرید",
                            "callback_data": "shop_menu"
                        }
                    ]
                ]
            }
        )

        return

    # =========================
    # اضافه کردن خرید به موجودی
    # =========================

    for item in cart.values():

        database.add_inventory(
            chat_id,
            item["id"],
            item["quantity"]
        )

    # =========================
    # خرید انجام شد
    # =========================

    new_user = database.get_user(chat_id)

    # =========================
    # گزارش خرید
    # =========================

    purchase_items = {}

    for item in cart.values():

        purchase_items[item["id"]] = item["quantity"]

    reports.send_purchase_report(
        user["country"],
        purchase_items,
        total_price
    )

    cancel_cart(chat_id)

    text = (
        "✅ خرید با موفقیت انجام شد!\n\n"
        f"💳 مبلغ خرید: {total_price:,}\n"
        f"💰 بودجه باقی‌مانده: {new_user['budget']:,}\n\n"
        "📦 آیتم‌های خریداری‌شده به موجودی شما اضافه شدند."
    )

    edit_message(
        chat_id,
        message_id,
        text,
        {
            "inline_keyboard": [
                [
                    {
                        "text": "🛍️ ادامه خرید",
                        "callback_data": "shop_menu"
                    }
                ],
                [
                    {
                        "text": "🌍 کشور من",
                        "callback_data": "my_country"
                    }
                ]
            ]
        }
    )


# =========================
# مدیریت پیام‌ها
# =========================

def handle_message(message):

    chat = message.get("chat", {})

    chat_id = chat.get("id")

    text = message.get("text", "")

    if not chat_id:
        return

    # آیا کاربر منتظر تعداد دلخواه است؟
    if chat_id in waiting_custom_quantity:

        item_id = waiting_custom_quantity[chat_id]

        try:
            quantity = int(text)

        except ValueError:

            send_message(
                chat_id,
                "❌ لطفاً فقط یک عدد صحیح وارد کن."
            )

            return

        if quantity <= 0:

            send_message(
                chat_id,
                "❌ تعداد باید بیشتر از صفر باشد."
            )

            return

        add_to_cart(
            chat_id,
            item_id,
            quantity
        )

        del waiting_custom_quantity[chat_id]

        item = find_item(item_id)

        # پیام جدید می‌فرستیم چون message_id نداریم
        send_message(
            chat_id,
            (
                f"✅ تعداد {quantity:,} عدد "
                f"{item['name']} به سبد خرید اضافه شد.\n\n"
                "🛒 از دکمه سبد خرید وارد سبد شو."
            ),
            {
                "inline_keyboard": [
                    [
                        {
                            "text": "🛒 سبد خرید",
                            "callback_data": "shop_cart"
                        }
                    ],
                    [
                        {
                            "text": "🛍️ ادامه خرید",
                            "callback_data": "shop_menu"
                        }
                    ]
                ]
            }
        )

        return


# =========================
# مدیریت کلیک‌ها
# =========================

def handle_update(update):

    # =========================
    # پیام
    # =========================

    message = update.get("message")

    if message:

        handle_message(message)

    # =========================
    # کلیک دکمه
    # =========================

    callback_query = update.get("callback_query")

    if not callback_query:
        return

    data = callback_query.get("data")

    message = callback_query.get(
        "message",
        {}
    )

    chat = message.get(
        "chat",
        {}
    )

    chat_id = chat.get("id")

    message_id = message.get(
        "message_id"
    )

    if not chat_id or not message_id:
        return

    # =========================
    # ورود به بازار
    # =========================

    if data == "arms_market":

        show_shop(
            chat_id,
            message_id
        )

        return

    # =========================
    # برگشت به منوی اصلی
    # =========================

    if data == "back_main_menu":

        try:

            import start

            user = database.get_user(
                chat_id
            )

            if user and user["country"]:

                start.show_main_menu(
                    chat_id,
                    user,
                    message_id
                )

        except Exception as error:

            print(
                f"Shop Back Error: {error}"
            )

        return

    # =========================
    # برگشت به بازار
    # =========================

    if data == "shop_menu":

        show_shop(
            chat_id,
            message_id
        )

        return

    # =========================
    # سبد خرید
    # =========================

    if data == "shop_cart":

        show_cart(
            chat_id,
            message_id
        )

        return

    # =========================
    # خالی کردن کامل سبد
    # =========================

    if data == "shop_clear_cart":

        cancel_cart(chat_id)

        text = (
            "🗑️ سبد خرید خالی شد."
        )

        edit_message(
            chat_id,
            message_id,
            text,
            {
                "inline_keyboard": [
                    [
                        {
                            "text": "🛍️ برگشت به بازار",
                            "callback_data": "shop_menu"
                        }
                    ],
                    [
                        {
                            "text": "🌍 منوی اصلی",
                            "callback_data": "back_main_menu"
                        }
                    ]
                ]
            }
        )

        return

    # =========================
    # لغو خرید
    # =========================

    if data == "shop_cancel":

        cancel_cart(chat_id)

        text = (
            "❌ خرید لغو شد.\n\n"
            "سبد خرید شما خالی شد."
        )

        edit_message(
            chat_id,
            message_id,
            text,
            {
                "inline_keyboard": [
                    [
                        {
                            "text": "🛍️ ادامه خرید",
                            "callback_data": "shop_menu"
                        }
                    ]
                ]
            }
        )

        return

    # =========================
    # تسویه خرید
    # =========================

    if data == "shop_checkout":

        checkout(
            chat_id,
            message_id
        )

        return

    # =========================
    # حذف آیتم
    # =========================

    if data.startswith("shop_remove_"):

        item_id = data.replace(
            "shop_remove_",
            ""
        )

        remove_from_cart(
            chat_id,
            item_id
        )

        show_cart(
            chat_id,
            message_id
        )

        return

    # =========================
    # تعداد دلخواه
    # =========================

    if data.startswith("shop_custom_"):

        item_id = data.replace(
            "shop_custom_",
            ""
        )

        item = find_item(item_id)

        if item is None:
            return

        waiting_custom_quantity[chat_id] = item_id

        edit_message(
            chat_id,
            message_id,
            (
                f"{item['name']}\n\n"
                "🔢 تعداد دلخواه را ارسال کن:\n\n"
                "مثلاً:\n"
                "250"
            ),
            {
                "inline_keyboard": [
                    [
                        {
                            "text": "❌ لغو",
                            "callback_data": "shop_cancel"
                        }
                    ]
                ]
            }
        )

        return

    # =========================
    # اضافه کردن تعداد
    # =========================

    if data.startswith("shop_add_"):

        parts = data.split("_")

        if len(parts) < 4:
            return

        amount = parts[2]
        item_id = "_".join(parts[3:])

        try:
            amount = int(amount)

        except ValueError:
            return

        item = find_item(item_id)

        if item is None:
            return

        add_to_cart(
            chat_id,
            item_id,
            amount
        )

        quantity = get_cart_quantity(
            chat_id,
            item_id
        )

        show_item(
            chat_id,
            message_id,
            item,
            quantity
        )

        return

    # =========================
    # کلیک روی آیتم
    # =========================

    if data.startswith("shop_item_"):

        item_id = data.replace(
            "shop_item_",
            ""
        )

        item = find_item(item_id)

        if item is None:
            return

        quantity = get_cart_quantity(
            chat_id,
            item_id
        )

        if quantity <= 0:
            quantity = 1

        show_item(
            chat_id,
            message_id,
            item,
            quantity
        )

        return

    # =========================
    # دسته‌ها
    # =========================

    category_map = {
        "shop_ground": "ground",
        "shop_air": "air",
        "shop_navy": "navy",
        "shop_missiles": "missiles",
        "shop_drones": "drones",
        "shop_helicopters": "helicopters",
        "shop_defense": "defense",
        "shop_tanks": "tanks",
        "shop_systems": "systems",
        "shop_civilian": "civilian",
        "shop_mines": "mines"
    }

    if data in category_map:

        category = category_map[data]

        show_category(
            chat_id,
            message_id,
            category
        )

        return

این نسخه فقط داخل "show_category" دکمه رو اضافه کرده؛ هندلر "shop_clear_cart" همون قبلیه و تغییر دیگه‌ای نداره.

یه نکته: الان این دکمه در صفحه‌ای دیده میشه که مثلاً وارد «🚀 موشک» یا «✈️ نیروی هوایی» میشی و لیست آیتم‌ها رو می‌بینی.
