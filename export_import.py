# ==============================
# World War - Export / Import
# ==============================

import database
import keyboards


send_message = None
edit_message = None
get_shop_item = None


# ==============================
# اتصال به bot.py
# ==============================

def setup(
    send_message_function,
    edit_message_function,
    shop_item_function
):
    global send_message
    global edit_message
    global get_shop_item

    send_message = send_message_function
    edit_message = edit_message_function
    get_shop_item = shop_item_function


# ==============================
# سشن‌های صادرات
# ==============================

export_sessions = {}

# پیشنهادهای فعال
trade_offers = {}

# شماره پیشنهاد
next_offer_id = 1


# ==============================
# فرمت قیمت
# ==============================

def format_price(price):

    if price is None:
        return "نامشخص"

    if price == 0:
        return "رایگان"

    return f"{price:,}"


# ==============================
# ساخت سشن
# ==============================

def get_session(user_id):
    return export_sessions.get(user_id)


# ==============================
# حذف سشن
# ==============================

def clear_session(user_id):

    if user_id in export_sessions:
        del export_sessions[user_id]


# ==============================
# پیدا کردن کالا
# ==============================

def find_item(item_id):

    if get_shop_item is None:
        return None

    return get_shop_item(item_id)


# ==============================
# شروع صادرات / واردات
# ==============================

def show_trade_menu(chat_id, message_id):

    inventory = database.get_inventory(chat_id)

    available_items = []

    for item_id, quantity in inventory.items():

        if quantity <= 0:
            continue

        item = find_item(item_id)

        if item is None:
            continue

        available_items.append({
            "id": item_id,
            "name": item["name"],
            "price": item["price"],
            "quantity": quantity
        })

    if not available_items:

        edit_message(
            chat_id,
            message_id,
            (
                "📦 صادرات/واردات\n\n"
                "❌ شما هیچ کالایی برای صادرات ندارید.\n\n"
                "ابتدا از بازار تسلیحات کالا خریداری کنید."
            ),
            keyboards.trade_empty_keyboard()
        )

        return

    export_sessions[chat_id] = {
        "stage": "select_item"
    }

    edit_message(
        chat_id,
        message_id,
        (
            "📦 صادرات/واردات\n\n"
            "تجهیزاتی که می‌خواهی صادر کنی را انتخاب کن:"
        ),
        keyboards.trade_items_keyboard(
            available_items
        )
    )


# ==============================
# انتخاب کالا
# ==============================

def select_item(chat_id, message_id, item_id):

    item = find_item(item_id)

    if item is None:
        return

    quantity = database.get_inventory_item(
        chat_id,
        item_id
    )

    if quantity <= 0:

        edit_message(
            chat_id,
            message_id,
            "❌ این کالا دیگر در موجودی شما وجود ندارد.",
            keyboards.trade_back_keyboard()
        )

        return

    export_sessions[chat_id] = {
        "stage": "quantity",
        "item_id": item_id,
        "item_name": item["name"],
        "original_unit_price": item["price"],
        "inventory_quantity": quantity
    }

    edit_message(
        chat_id,
        message_id,
        (
            f"📦 نام کالا: {item['name']}\n\n"
            f"📊 تعدادی که کاربر دارد: {quantity:,}\n\n"
            "🔢 تعداد مورد نظر برای صادرات را وارد کن:"
        ),
        keyboards.trade_cancel_keyboard()
    )


# ==============================
# دریافت تعداد
# ==============================

def handle_quantity(chat_id, text):

    session = get_session(chat_id)

    if not session:
        return False

    if session.get("stage") != "quantity":
        return False

    try:
        quantity = int(text)

    except ValueError:

        send_message(
            chat_id,
            "❌ لطفاً فقط یک عدد صحیح وارد کن."
        )

        return True

    if quantity <= 0:

        send_message(
            chat_id,
            "❌ تعداد باید بیشتر از صفر باشد."
        )

        return True

    current_quantity = database.get_inventory_item(
        chat_id,
        session["item_id"]
    )

    if quantity > current_quantity:

        send_message(
            chat_id,
            (
                "❌ این تعداد از موجودی شما بیشتر است.\n\n"
                f"📦 موجودی فعلی: {current_quantity:,}"
            )
        )

        return True

    original_unit_price = session["original_unit_price"]

    original_total_price = (
        original_unit_price * quantity
    )

    session["quantity"] = quantity
    session["original_total_price"] = original_total_price
    session["stage"] = "price"

    return True


# ==============================
# نمایش صفحه قیمت
# ==============================

def show_price_page(chat_id, message_id):

    session = get_session(chat_id)

    if not session:
        return

    quantity = session.get("quantity")

    if quantity is None:
        return

    edit_message(
        chat_id,
        message_id,
        (
            "💰 قیمت کالا را وارد کن\n\n"
            f"📦 نام کالا: {session.get('item_name', 'نامشخص')}\n"
            f"🔢 تعداد: {quantity:,}\n\n"
            f"💵 قیمت اصلی هر ۱ دونه: "
            f"{format_price(session.get('original_unit_price'))}\n"
            f"💳 قیمت اصلی کل: "
            f"{format_price(session.get('original_total_price'))}\n\n"
            "💰 قیمت شما را وارد کنید:"
        ),
        keyboards.trade_price_keyboard()
    )


# ==============================
# دریافت قیمت
# ==============================

def handle_price(chat_id, text):

    session = get_session(chat_id)

    if not session:
        return False

    if session.get("stage") != "price":
        return False

    try:
        price = int(text)

    except ValueError:

        send_message(
            chat_id,
            "❌ لطفاً قیمت را فقط به صورت عدد وارد کن."
        )

        return True

    if price <= 0:

        send_message(
            chat_id,
            (
                "❌ قیمت باید بیشتر از صفر باشد.\n\n"
                "برای معامله رایگان از دکمه 🆓 ارسال رایگان استفاده کن."
            )
        )

        return True

    # اطمینان از وجود تعداد
    if session.get("quantity") is None:

        clear_session(chat_id)

        send_message(
            chat_id,
            "❌ اطلاعات معامله ناقص شد. لطفاً معامله را دوباره شروع کن."
        )

        return True

    session["price"] = price
    session["free"] = False
    session["stage"] = "countries"

    return True


# ==============================
# رایگان
# ==============================

def set_free_price(chat_id, message_id):

    session = get_session(chat_id)

    if not session:
        return

    if session.get("stage") != "price":
        return

    if session.get("quantity") is None:

        clear_session(chat_id)

        edit_message(
            chat_id,
            message_id,
            "❌ اطلاعات معامله ناقص شده است. لطفاً دوباره شروع کن.",
            keyboards.trade_main_menu_keyboard()
        )

        return

    session["price"] = 0
    session["free"] = True
    session["stage"] = "countries"

    show_countries(
        chat_id,
        message_id
    )


# ==============================
# نمایش کشورهای مقصد
# ==============================

def show_countries(chat_id, message_id):

    session = get_session(chat_id)

    if not session:
        return

    selected_countries = database.get_selected_countries()

    targets = []

    for country_data in selected_countries:

        target_user_id = country_data["user_id"]
        country = country_data["country"]

        if target_user_id == chat_id:
            continue

        targets.append({
            "user_id": target_user_id,
            "country": country
        })

    if not targets:

        edit_message(
            chat_id,
            message_id,
            (
                "🌍 انتخاب کشور مقصد\n\n"
                "❌ در حال حاضر کشور دیگری برای معامله وجود ندارد."
            ),
            keyboards.trade_back_keyboard()
        )

        return

    edit_message(
        chat_id,
        message_id,
        (
            "🌍 انتخاب کشور مقصد\n\n"
            "کشوری که می‌خواهی برای آن کالا صادر کنی را انتخاب کن:"
        ),
        keyboards.trade_countries_keyboard(
            targets
        )
    )


# ==============================
# انتخاب کشور
# ==============================

def select_country(
    chat_id,
    message_id,
    target_user_id
):

    session = get_session(chat_id)

    if not session:
        return

    if target_user_id == chat_id:
        return

    target_user = database.get_user(
        target_user_id
    )

    if not target_user or not target_user["country"]:

        edit_message(
            chat_id,
            message_id,
            "❌ کشور مقصد دیگر در دسترس نیست.",
            keyboards.trade_back_keyboard()
        )

        return

    # اطلاعات ضروری باید وجود داشته باشند
    item_id = session.get("item_id")
    quantity = session.get("quantity")

    if not item_id or quantity is None:

        clear_session(chat_id)

        edit_message(
            chat_id,
            message_id,
            "❌ اطلاعات معامله ناقص شده است. لطفاً دوباره شروع کن.",
            keyboards.trade_main_menu_keyboard()
        )

        return

    current_quantity = database.get_inventory_item(
        chat_id,
        item_id
    )

    if current_quantity < quantity:

        clear_session(chat_id)

        edit_message(
            chat_id,
            message_id,
            (
                "❌ موجودی شما برای این معامله کافی نیست.\n\n"
                f"📦 موجودی فعلی: {current_quantity:,}"
            ),
            keyboards.trade_back_keyboard()
        )

        return

    session["target_user_id"] = target_user_id
    session["target_country"] = target_user["country"]
    session["stage"] = "confirm"

    trade_value = (
        "رایگان"
        if session.get("free")
        else format_price(session.get("price"))
    )

    edit_message(
        chat_id,
        message_id,
        (
            "⚠️ آیا مطمئن هستید از این معامله؟\n\n"
            f"🌍 کشور مقصد: {session['target_country']}\n"
            f"📦 تعداد کالا: {quantity:,}\n"
            f"📦 نام کالا: {session.get('item_name', 'نامشخص')}\n"
            f"💰 ارزش معامله: {trade_value}"
        ),
        keyboards.trade_confirm_keyboard()
    )


# ==============================
# تأیید صادرکننده
# ==============================

def confirm_export(chat_id, message_id):

    global next_offer_id

    session = get_session(chat_id)

    if not session:
        return

    if session.get("stage") != "confirm":
        return

    # ==============================
    # دریافت اطلاعات قبل از پاک شدن سشن
    # ==============================

    target_user_id = session.get("target_user_id")
    target_country = session.get("target_country")

    item_id = session.get("item_id")
    item_name = session.get("item_name")
    quantity = session.get("quantity")
    price = session.get("price")
    free = session.get("free", False)

    # ==============================
    # بررسی اطلاعات
    # ==============================

    if not target_user_id:
        return

    if not item_id or not item_name:
        edit_message(
            chat_id,
            message_id,
            "❌ اطلاعات کالا ناقص است.",
            keyboards.trade_main_menu_keyboard()
        )
        clear_session(chat_id)
        return

    if quantity is None or quantity <= 0:
        edit_message(
            chat_id,
            message_id,
            "❌ تعداد کالا در این معامله معتبر نیست.",
            keyboards.trade_main_menu_keyboard()
        )
        clear_session(chat_id)
        return

    if not free and (price is None or price <= 0):
        edit_message(
            chat_id,
            message_id,
            "❌ قیمت معامله معتبر نیست.",
            keyboards.trade_main_menu_keyboard()
        )
        clear_session(chat_id)
        return

    # ==============================
    # بررسی موجودی
    # ==============================

    current_quantity = database.get_inventory_item(
        chat_id,
        item_id
    )

    if current_quantity < quantity:

        clear_session(chat_id)

        edit_message(
            chat_id,
            message_id,
            "❌ موجودی شما برای انجام این معامله کافی نیست.",
            keyboards.trade_back_keyboard()
        )

        return

    # ==============================
    # جلوگیری از تأیید دوباره
    # ==============================

    if session.get("offer_created"):
        return

    # ==============================
    # ساخت پیشنهاد
    # ==============================

    offer_id = next_offer_id
    next_offer_id += 1

    offer = {
        "id": offer_id,
        "seller_id": chat_id,
        "buyer_id": target_user_id,
        "item_id": item_id,
        "item_name": item_name,
        "quantity": quantity,
        "price": price,
        "free": free,
        "target_country": target_country,
        "status": "pending"
    }

    trade_offers[offer_id] = offer

    # ==============================
    # پاک کردن سشن
    # ==============================

    clear_session(chat_id)

    trade_value = (
        "رایگان"
        if offer["free"]
        else format_price(offer["price"])
    )

    # ==============================
    # پیام صادرکننده
    # ==============================

    edit_message(
        chat_id,
        message_id,
        (
            "📦 پیشنهاد صادراتی ارسال شد.\n\n"
            f"🌍 کشور مقصد: {target_country}\n"
            f"📦 نام کالا: {item_name}\n"
            f"🔢 تعداد: {quantity:,}\n"
            f"💰 ارزش معامله: {trade_value}\n\n"
            "⏳ منتظر پاسخ کشور مقصد باشید."
        ),
        keyboards.trade_main_menu_keyboard()
    )

    # ==============================
    # ارسال پیشنهاد به خریدار
    # ==============================

    result = send_message(
        target_user_id,
        (
            "📦 پیشنهاد صادراتی جدید دارید!\n\n"
            f"💰 قیمت کالا: {trade_value}\n"
            f"🔢 تعداد: {quantity:,}\n"
            f"📦 نام کالا: {item_name}\n\n"
            "آیا این پیشنهاد را تأیید و خریداری می‌کنید؟"
        ),
        keyboards.trade_buyer_keyboard(
            offer_id
        )
    )

    # اگر ارسال پیام با خطا مواجه شد
    if not result or not result.get("ok", False):

        trade_offers.pop(
            offer_id,
            None
        )

        edit_message(
            chat_id,
            message_id,
            (
                "❌ ارسال پیشنهاد به کشور مقصد انجام نشد.\n\n"
                "لطفاً دوباره تلاش کن."
            ),
            keyboards.trade_main_menu_keyboard()
        )


# ==============================
# لغو معامله توسط صادرکننده
# ==============================

def cancel_export(chat_id, message_id):

    clear_session(chat_id)

    edit_message(
        chat_id,
        message_id,
        "❌ معامله لغو شد.",
        keyboards.trade_main_menu_keyboard()
    )


# ==============================
# انجام معامله
# ==============================

def complete_trade(
    offer_id,
    buyer_id,
    message_id
):

    offer = trade_offers.get(offer_id)

    if not offer:

        edit_message(
            buyer_id,
            message_id,
            "❌ این پیشنهاد دیگر معتبر نیست.",
            keyboards.trade_main_menu_keyboard()
        )

        return

    if offer["status"] != "pending":

        edit_message(
            buyer_id,
            message_id,
            "❌ این پیشنهاد قبلاً بررسی شده است.",
            keyboards.trade_main_menu_keyboard()
        )

        return

    if offer["buyer_id"] != buyer_id:
        return

    seller_id = offer["seller_id"]

    buyer = database.get_user(
        buyer_id
    )

    seller = database.get_user(
        seller_id
    )

    if not buyer or not seller:

        offer["status"] = "failed"

        edit_message(
            buyer_id,
            message_id,
            "❌ اطلاعات معامله معتبر نیست.",
            keyboards.trade_main_menu_keyboard()
        )

        return

    if not buyer["country"] or not seller["country"]:

        offer["status"] = "failed"

        edit_message(
            buyer_id,
            message_id,
            "❌ کشور یکی از طرفین دیگر فعال نیست.",
            keyboards.trade_main_menu_keyboard()
        )

        return

    seller_quantity = database.get_inventory_item(
        seller_id,
        offer["item_id"]
    )

    if seller_quantity < offer["quantity"]:

        offer["status"] = "failed"

        edit_message(
            buyer_id,
            message_id,
            (
                "❌ معامله انجام نشد.\n\n"
                "فروشنده دیگر این مقدار کالا را در موجودی ندارد."
            ),
            keyboards.trade_main_menu_keyboard()
        )

        return

    if not offer["free"]:

        if buyer["budget"] < offer["price"]:

            edit_message(
                buyer_id,
                message_id,
                (
                    "❌ معامله انجام نشد.\n\n"
                    "💰 بودجه شما برای خرید این کالا کافی نیست."
                ),
                keyboards.trade_main_menu_keyboard()
            )

            return

    inventory_removed = database.decrease_inventory(
        seller_id,
        offer["item_id"],
        offer["quantity"]
    )

    if not inventory_removed:

        offer["status"] = "failed"

        edit_message(
            buyer_id,
            message_id,
            "❌ انتقال کالا انجام نشد.",
            keyboards.trade_main_menu_keyboard()
        )

        return

    if not offer["free"]:

        money_transferred = database.transfer_budget(
            buyer_id,
            seller_id,
            offer["price"]
        )

        if not money_transferred:

            database.add_inventory(
                seller_id,
                offer["item_id"],
                offer["quantity"]
            )

            edit_message(
                buyer_id,
                message_id,
                (
                    "❌ معامله انجام نشد.\n\n"
                    "انتقال پول با مشکل مواجه شد."
                ),
                keyboards.trade_main_menu_keyboard()
            )

            return

    database.add_inventory(
        buyer_id,
        offer["item_id"],
        offer["quantity"]
    )

    offer["status"] = "completed"
    
        # ==============================
    # اطلاع‌رسانی به صادرکننده
    # ==============================

    if offer["free"]:

        send_message(
            seller_id,
            (
                "✅ کشور "
                f"{buyer['country']} پیشنهاد شما را قبول کرد!\n\n"
                f"📦 مقدار و نام کالا: "
                f"{offer['quantity']:,} عدد {offer['item_name']}\n"
                f"🌍 به کشور {buyer['country']} فرستاده شد."
            )
        )

    else:

        send_message(
            seller_id,
            (
                "✅ کشور "
                f"{buyer['country']} پیشنهاد شما را قبول کرد!\n\n"
                f"📦 مقدار و نام کالا: "
                f"{offer['quantity']:,} عدد {offer['item_name']}\n"
                f"🌍 به کشور {buyer['country']} فرستاده شد.\n\n"
                f"💰 مبلغ {format_price(offer['price'])} "
                "به کشور شما پرداخت شد."
            )
        )

    edit_message(
        buyer_id,
        message_id,
        (
            "✅ معامله با موفقیت انجام شد!\n\n"
            f"کشور شما {offer['quantity']:,} عدد "
            f"{offer['item_name']} دریافت کرد."
        ),
        keyboards.trade_main_menu_keyboard()
    )


# ==============================
# رد پیشنهاد توسط خریدار
# ==============================

def reject_trade(
    offer_id,
    buyer_id,
    message_id
):

    offer = trade_offers.get(offer_id)

    if not offer:

        edit_message(
            buyer_id,
            message_id,
            "❌ این پیشنهاد دیگر معتبر نیست.",
            keyboards.trade_main_menu_keyboard()
        )

        return

    if offer["buyer_id"] != buyer_id:
        return

    if offer["status"] != "pending":

        edit_message(
            buyer_id,
            message_id,
            "❌ این پیشنهاد قبلاً بررسی شده است.",
            keyboards.trade_main_menu_keyboard()
        )

        return

    offer["status"] = "rejected"

    edit_message(
        buyer_id,
        message_id,
        "❌ پیشنهاد صادراتی رد شد.",
        keyboards.trade_main_menu_keyboard()
    )


# ==============================
# پیام‌های متنی
# ==============================

def handle_message(message):

    chat = message.get(
        "chat",
        {}
    )

    chat_id = chat.get("id")

    if not chat_id:
        return

    text = message.get(
        "text",
        ""
    ).strip()

    session = get_session(chat_id)

    if not session:
        return

    # ==============================
    # تعداد
    # ==============================

    if session.get("stage") == "quantity":

        handled = handle_quantity(
            chat_id,
            text
        )

        if handled:

            # صفحه قیمت را در یک پیام جدید نشان می‌دهیم
            # چون message_id پیام تایپی کاربر است.

            show_price_page_after_quantity(
                chat_id
            )

        return

    # ==============================
    # قیمت
    # ==============================

    if session.get("stage") == "price":

        handled = handle_price(
            chat_id,
            text
        )

        if handled and get_session(chat_id):

            show_countries_after_price(
                chat_id
            )

        return


# ==============================
# نمایش صفحه قیمت بعد از تعداد
# ==============================

def show_price_page_after_quantity(chat_id):

    session = get_session(chat_id)

    if not session:
        return

    quantity = session.get("quantity")

    if quantity is None:
        return

    send_message(
        chat_id,
        (
            "💰 قیمت کالا را وارد کن\n\n"
            f"📦 نام کالا: {session.get('item_name', 'نامشخص')}\n"
            f"🔢 تعداد: {quantity:,}\n\n"
            f"💵 قیمت اصلی هر ۱ دونه: "
            f"{format_price(session.get('original_unit_price'))}\n"
            f"💳 قیمت اصلی کل: "
            f"{format_price(session.get('original_total_price'))}\n\n"
            "💰 قیمت شما را وارد کنید:"
        ),
        keyboards.trade_price_keyboard()
    )


# ==============================
# نمایش کشورها بعد از قیمت
# ==============================

def show_countries_after_price(chat_id):

    session = get_session(chat_id)

    if not session:
        return

    if session.get("quantity") is None:
        return

    selected_countries = database.get_selected_countries()

    targets = []

    for country_data in selected_countries:

        if country_data["user_id"] == chat_id:
            continue

        targets.append({
            "user_id": country_data["user_id"],
            "country": country_data["country"]
        })

    if not targets:

        send_message(
            chat_id,
            (
                "🌍 انتخاب کشور مقصد\n\n"
                "❌ کشور دیگری برای معامله وجود ندارد."
            ),
            keyboards.trade_back_keyboard()
        )

        return

    session["stage"] = "countries"

    send_message(
        chat_id,
        (
            "🌍 انتخاب کشور مقصد\n\n"
            "کشوری که می‌خواهی برای آن کالا صادر کنی را انتخاب کن:"
        ),
        keyboards.trade_countries_keyboard(
            targets
        )
    )


# ==============================
# مدیریت Callback
# ==============================

def handle_update(update):

    message = update.get("message")

    if message:
        handle_message(message)

    callback_query = update.get(
        "callback_query"
    )

    if not callback_query:
        return

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

    chat_id = chat.get("id")

    message_id = message.get(
        "message_id"
    )

    if not chat_id or not message_id:
        return

    # ==============================
    # ورود به صادرات / واردات
    # ==============================

    if data == "trade":

        show_trade_menu(
            chat_id,
            message_id
        )

        return

    # ==============================
    # انتخاب کالا
    # ==============================

    if data.startswith("trade_item_"):

        item_id = data.replace(
            "trade_item_",
            ""
        )

        select_item(
            chat_id,
            message_id,
            item_id
        )

        return

    # ==============================
    # ارسال رایگان
    # ==============================

    if data == "trade_free":

        set_free_price(
            chat_id,
            message_id
        )

        return

    # ==============================
    # انتخاب کشور
    # ==============================

    if data.startswith("trade_country_"):

        try:
            target_user_id = int(
                data.replace(
                    "trade_country_",
                    ""
                )
            )

        except ValueError:
            return

        select_country(
            chat_id,
            message_id,
            target_user_id
        )

        return

    # ==============================
    # تأیید صادرکننده
    # ==============================

    if data == "trade_confirm":

        confirm_export(
            chat_id,
            message_id
        )

        return

    # ==============================
    # لغو صادرکننده
    # ==============================

    if data == "trade_cancel":

        cancel_export(
            chat_id,
            message_id
        )

        return

    # ==============================
    # تأیید خریدار
    # ==============================

    if data.startswith("trade_buy_"):

        try:
            offer_id = int(
                data.replace(
                    "trade_buy_",
                    ""
                )
            )

        except ValueError:
            return

        complete_trade(
            offer_id,
            chat_id,
            message_id
        )

        return

    # ==============================
    # رد خریدار
    # ==============================

    if data.startswith("trade_reject_"):

        try:
            offer_id = int(
                data.replace(
                    "trade_reject_",
                    ""
                )
            )

        except ValueError:
            return

        reject_trade(
            offer_id,
            chat_id,
            message_id
        )

        return

    # ==============================
    # برگشت منوی اصلی
    # ==============================

    if data == "trade_main_menu":

        clear_session(chat_id)

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
                f"Trade Back Error: {error}"
            )

        return