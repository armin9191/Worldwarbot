# ==============================
# World War - Attack System
# ==============================


import database
import keyboards
import reports
import time


# ==============================
# مدت محافظت کشورهای تازه‌تأسیس
# ==============================
# برای تست: ۱ دقیقه
PROTECTION_SECONDS = 60          # ۱ دقیقه

# وقتی خواستی برگردونی به ۵ ساعت، این خط رو بگذار:
# PROTECTION_SECONDS = 5 * 3600


# ==============================
# وزن قدرت حمله تجهیزات
# ==============================


ATTACK_WEIGHTS = {
    # Ground
    "commander": 8,
    "soldier": 2,
    "police": 1,
    "border_guard": 2,
    "bomb_disarmer": 1,
    "bomber": 4,
    "special_unit": 6,
    "mine_layer": 2,
    "mine_disarmer": 1,
    "spy": 1,
    "sniper": 5,
    "rpg": 4,

    # Air
    "f16": 50,
    "f18": 55,
    "f22": 70,
    "f35": 90,
    "b1": 60,
    "b2": 150,
    "b52": 130,

    # Navy
    "tanker": 0,
    "trade_ship": 0,
    "aircraft_carrier": 200,
    "war_boat": 15,
    "idaho_submarine": 40,
    "gerald_ford": 400,
    "abraham_lincoln": 600,

    # Missiles
    "precision_missile": 30,
    "cruise_missile": 45,
    "kheybershekan": 70,
    "khorramshahr4": 100,
    "df26": 130,

    # Drones
    "suicide_drone": 10,
    "precision_drone": 15,
    "recon_drone": 3,

    # Helicopters
    "crocodile_helicopter": 10,
    "apache": 20,
    "cobra": 15,
    "bell12": 8,

    # Tanks
    "zolfaghar": 12,
    "panther": 15,
    "karrar": 25,
}


# ==============================
# وزن دفاعی پدافندها
# ==============================


DEFENSE_WEIGHTS = {
    "patriot": 40,
    "phalanx": 35,
    "thaad": 60,
}


# ==============================
# محاسبه قدرت نظامی
# ==============================


def calculate_military_power(user_id):
    inventory = database.get_inventory(user_id)

    total_power = 0

    for item_id, quantity in inventory.items():
        weight = ATTACK_WEIGHTS.get(item_id, 0)
        total_power += quantity * weight

    return total_power


# ==============================
# محاسبه قدرت دفاعی
# ==============================


def calculate_defense_power(user_id):
    inventory = database.get_inventory(user_id)

    total_defense = 0

    for item_id, quantity in inventory.items():
        weight = DEFENSE_WEIGHTS.get(item_id, 0)
        total_defense += quantity * weight

    return total_defense


# ==============================
# محاسبه قدرت حمله بر اساس درصد
# ==============================


def calculate_attack_power(user_id, percent):
    military_power = calculate_military_power(user_id)

    if percent <= 0:
        return 0

    if percent > 100:
        percent = 100

    attack_power = military_power * percent / 100

    return int(attack_power)


# ==============================
# محاسبه نتیجه یک حمله
# ==============================


def calculate_attack_result(attacker_id, defender_id, percent):
    attack_power = calculate_attack_power(
        attacker_id,
        percent
    )

    defense_power = calculate_defense_power(
        defender_id
    )

    remaining_damage = attack_power - defense_power

    if remaining_damage < 0:
        remaining_damage = 0

    return {
        "attack_power": attack_power,
        "defense_power": defense_power,
        "damage": remaining_damage
    }


# ==============================
# مصرف تجهیزات هجومی
# ==============================


def consume_attack_equipment(user_id, percent):
    inventory = database.get_inventory(user_id)

    if percent <= 0:
        return {}

    if percent > 100:
        percent = 100

    consumed = {}

    for item_id, quantity in inventory.items():

        # فقط تجهیزات هجومی
        if item_id not in ATTACK_WEIGHTS:
            continue

        # تجهیزاتی که قدرت حمله ندارند مصرف نشوند
        if ATTACK_WEIGHTS[item_id] <= 0:
            continue

        amount = int(quantity * percent / 100)

        if amount <= 0:
            continue

        success = database.decrease_inventory(
            user_id,
            item_id,
            amount
        )

        if success:
            consumed[item_id] = amount

    return consumed


# ==============================
# مصرف پدافند دشمن
# ==============================


def consume_defense_equipment(user_id, attack_power):
    inventory = database.get_inventory(user_id)

    remaining_power = attack_power
    consumed = {}

    defense_items = [
        "patriot",
        "phalanx",
        "thaad"
    ]

    for item_id in defense_items:

        if remaining_power <= 0:
            break

        quantity = inventory.get(item_id, 0)

        if quantity <= 0:
            continue

        weight = DEFENSE_WEIGHTS[item_id]

        # تعداد پدافند لازم برای جذب حمله
        # اگر حتی بخشی از یک پدافند لازم باشد،
        # کل همان یک پدافند مصرف می‌شود.
        needed = (remaining_power + weight - 1) // weight

        amount = min(quantity, needed)

        if amount <= 0:
            continue

        success = database.decrease_inventory(
            user_id,
            item_id,
            amount
        )

        if success:
            consumed[item_id] = amount

            # کل قدرت پدافندهای مصرف‌شده جذب می‌شود
            absorbed = amount * weight
            remaining_power -= absorbed

    return {
        "consumed": consumed,
        "remaining_power": max(remaining_power, 0)
    }


# ==============================
# اجرای کامل حمله
# ==============================


def execute_attack(attacker_id, defender_id, percent):

    # قدرت حمله
    attack_power = calculate_attack_power(
        attacker_id,
        percent
    )

    # مصرف پدافند و محاسبه قدرت باقی مانده
    defense_result = consume_defense_equipment(
        defender_id,
        attack_power
    )

    remaining_damage = defense_result["remaining_power"]

    # اطلاعات مدافع
    defender = database.get_user(defender_id)

    if defender is None:
        return None

    old_hp = defender["hp"]

    # ==============================
    # ذخیره بودجه مدافع قبل از تغییر
    # ==============================

    defender_budget = defender["budget"]

    # کم شدن آسیب باقی مانده از HP
    new_hp = old_hp - remaining_damage

    if new_hp < 0:
        new_hp = 0

    # ذخیره HP جدید
    database.update_hp(
        defender_id,
        new_hp
    )

    # مصرف تجهیزات مهاجم
    consumed_attack = consume_attack_equipment(
        attacker_id,
        percent
    )

    # ==================================
    # محاسبه غرامت
    # ==================================

    if new_hp <= 0:

        # اگر کشور کاملاً نابود شده باشد،
        # کل بودجه باقی مانده مدافع منتقل می‌شود.
        compensation = defender_budget

    else:

        # در حمله عادی، 10 درصد بودجه مدافع منتقل می‌شود.
        compensation = int(
            defender_budget * 10 / 100
        )

    # ==================================
    # انتقال واقعی غرامت
    # ==================================

    if compensation > 0:

        database.update_budget(
            defender_id,
            defender_budget - compensation
        )

        attacker = database.get_user(attacker_id)

        if attacker is not None:

            database.update_budget(
                attacker_id,
                attacker["budget"] + compensation
            )

    # ==================================
    # اگر کشور کاملاً نابود شده باشد
    # بازیکن کاملاً از صفر شروع می‌کند
    # ==================================

    if new_hp <= 0:
        database.reset_player_after_defeat(
            defender_id
        )

    return {
        "attack_power": attack_power,
        "defense_power": attack_power - remaining_damage,
        "damage": remaining_damage,
        "old_hp": old_hp,
        "new_hp": new_hp,
        "compensation": compensation,
        "consumed_defense": defense_result["consumed"],
        "consumed_attack": consumed_attack
    }


# ==============================
# دریافت کشورهای قابل حمله
# ==============================


def get_attack_targets(attacker_id):
    selected_countries = database.get_selected_countries()

    attacker = database.get_user(attacker_id)

    if attacker is None:
        return [], 0

    targets = []
    protected_count = 0

    current_time = time.time()

    for player in selected_countries:

        # کشور خود بازیکن نمایش داده نشود
        if player["user_id"] == attacker_id:
            continue

        # بررسی محافظت تازه‌تأسیس بودن
        selected_at = player.get("country_selected_at")

        if selected_at is not None:
            age = current_time - selected_at
            if age < PROTECTION_SECONDS:
                protected_count += 1
                continue  # مخفی کردن

        targets.append(player)

    return targets, protected_count


# ==============================
# اتصال Attack به Bot
# ==============================


send_message = None
edit_message = None


def setup(send_func, edit_func):
    global send_message
    global edit_message

    send_message = send_func
    edit_message = edit_func


# ==============================
# نمایش منوی حمله
# ==============================


def show_attack_menu(chat_id, message_id, user_id):

    targets, protected_count = get_attack_targets(user_id)

    if not targets and protected_count == 0:
        edit_message(
            chat_id,
            message_id,
            "💥 حمله نظامی\n\n"
            "❌ در حال حاضر هیچ کشور دیگری برای حمله وجود ندارد."
        )
        return

    text = "💥 انتخاب کشور برای حمله:"

    if protected_count > 0:
        text += f"\n\n🔒 {protected_count} کشور تازه‌تأسیس دیده نمی‌شود (مخفی است)"

    if not targets:
        edit_message(
            chat_id,
            message_id,
            text + "\n\n❌ هیچ کشور قابل حمله‌ای وجود ندارد."
        )
        return

    edit_message(
        chat_id,
        message_id,
        text,
        keyboards.attack_targets_keyboard(targets)
    )


# ==============================
# وضعیت حمله کاربران
# ==============================


attack_sessions = {}


# ==============================
# دریافت آپدیت‌های حمله
# ==============================


def handle_update(update):

    # ==================================
    # پیام متنی کاربر
    # برای درصد دلخواه
    # ==================================

    if "message" in update:

        message = update["message"]

        chat_id = message["chat"]["id"]
        user_id = message["from"]["id"]
        message_id = message["message_id"]

        text = message.get("text", "").strip()

        session = attack_sessions.get(user_id)

        if session is None:
            return

        # فقط وقتی منتظر درصد دلخواه هستیم
        if session.get("waiting_percent"):

            try:
                percent = int(text)
            except ValueError:
                edit_message(
                    session["chat_id"],
                    session["message_id"],
                    "❌ درصد وارد شده معتبر نیست.\n\n"
                    "لطفاً یک عدد بین 1 تا 100 وارد کنید."
                )
                return

            if percent < 1 or percent > 100:
                edit_message(
                    session["chat_id"],
                    session["message_id"],
                    "❌ درصد باید بین 1 تا 100 باشد."
                )
                return

            session["percent"] = percent
            session["waiting_percent"] = False

            defender_id = session["defender_id"]

            defender = database.get_user(defender_id)

            if defender is None:
                edit_message(
                    chat_id,
                    message_id,
                    "❌ کشور حریف دیگر وجود ندارد."
                )
                attack_sessions.pop(user_id, None)
                return

            military_power = calculate_military_power(user_id)

            attack_power = int(
                military_power * percent / 100
            )

            defense_power = calculate_defense_power(
                defender_id
            )

            damage = attack_power - defense_power

            if damage < 0:
                damage = 0

            warning = ""

            if damage >= defender["hp"]:
                warning = "\n\n⚠️ کشور حریف کاملاً نابود می‌شود!"

            text_result = (
                "⚔️ آماده حمله\n\n"
                f"🌍 کشور حریف: {defender['country']}\n"
                f"🛡️ قدرت دفاعی کشور حریف: {defense_power:,}\n"
                f"⚔️ قدرت حمله ما: {attack_power:,}\n"
                f"📊 درصد انتخاب شده: {percent}%"
                f"{warning}"
            )

            edit_message(
                session["chat_id"],
                session["message_id"],
                text_result,
                keyboards.attack_percent_keyboard()
            )

        return

    # ==================================
    # فقط Callback Query
    # ==================================

    if "callback_query" not in update:
        return

    callback = update["callback_query"]

    data = callback.get("data")

    message = callback.get("message")

    if message is None:
        return

    chat_id = message["chat"]["id"]
    message_id = message["message_id"]
    user_id = callback["from"]["id"]

    # ==================================
    # دکمه حمله نظامی
    # ==================================

    if data == "attack":

        attack_sessions.pop(user_id, None)

        show_attack_menu(
            chat_id,
            message_id,
            user_id
        )

        return

    # ==================================
    # انتخاب کشور حریف
    # ==================================

    if data.startswith("attack_target_"):

        try:
            defender_id = int(
                data.replace(
                    "attack_target_",
                    ""
                )
            )
        except ValueError:
            return

        # کشور حریف
        defender = database.get_user(
            defender_id
        )

        if defender is None:
            edit_message(
                chat_id,
                message_id,
                "❌ این کشور دیگر در دسترس نیست."
            )
            return

        # جلوگیری از حمله به خود
        if defender_id == user_id:
            edit_message(
                chat_id,
                message_id,
                "❌ نمی‌توانی به کشور خودت حمله کنی."
            )
            return
        
        # ==================================
        # بررسی داشتن تجهیزات نظامی
        # ==================================

        military_power = calculate_military_power(user_id)

        if military_power <= 0:
            shop_keyboard = {
                "inline_keyboard": [
                    [
                        {
                            "text": "🛒 رفتن به شاپ",
                            "callback_data": "shop_menu"
                        }
                    ]
                ]
            }

            edit_message(
                chat_id,
                message_id,
                "⚠️ شما تجهیزات نظامی ندارید.\n\n"
                "برای خرید تجهیزات بزنید روی «رفتن به شاپ».",
                shop_keyboard
            )
            return

        # بررسی اینکه هنوز کشور در اختیار بازیکن است
        targets, _ = get_attack_targets(user_id)

        valid_target = False

        for target in targets:
            if target["user_id"] == defender_id:
                valid_target = True
                break

        if not valid_target:
            edit_message(
                chat_id,
                message_id,
                "❌ این کشور دیگر قابل حمله نیست."
            )
            return
        
        # ذخیره وضعیت حمله
        attack_sessions[user_id] = {
            "chat_id": chat_id,
            "message_id": message_id,
            "defender_id": defender_id,
            "percent": None,
            "waiting_percent": False
        }

        military_power = calculate_military_power(
            user_id
        )

        defense_power = calculate_defense_power(
            defender_id
        )

        text = (
            "⚔️ آماده حمله\n\n"
            f"🌍 کشور حریف: {defender['country']}\n"
            f"🛡️ قدرت دفاعی کشور حریف: {defense_power:,}\n"
            f"⚔️ قدرت نظامی کشور ما: {military_power:,}\n\n"
            "📊 درصد قدرت نظامی را انتخاب کنید:"
        )

        edit_message(
            chat_id,
            message_id,
            text,
            keyboards.attack_percent_keyboard()
        )

        return

    # ==================================
    # انتخاب درصد
    # ==================================

    if data.startswith("attack_percent_"):

        session = attack_sessions.get(user_id)

        if session is None:
            return

        try:
            percent = int(
                data.replace(
                    "attack_percent_",
                    ""
                )
            )
        except ValueError:
            return

        session["percent"] = percent
        session["waiting_percent"] = False

        defender_id = session["defender_id"]

        defender = database.get_user(
            defender_id
        )

        if defender is None:
            edit_message(
                chat_id,
                message_id,
                "❌ کشور حریف دیگر وجود ندارد."
            )
            attack_sessions.pop(user_id, None)
            return

        military_power = calculate_military_power(
            user_id
        )

        attack_power = int(
            military_power * percent / 100
        )

        defense_power = calculate_defense_power(
            defender_id
        )

        damage = attack_power - defense_power

        if damage < 0:
            damage = 0

        warning = ""

        if damage >= defender["hp"]:
            warning = "\n\n⚠️ کشور حریف کاملاً نابود می‌شود!"

        text = (
            "⚔️ آماده حمله\n\n"
            f"🌍 کشور حریف: {defender['country']}\n"
            f"🛡️ قدرت دفاعی کشور حریف: {defense_power:,}\n"
            f"⚔️ قدرت حمله ما: {attack_power:,}\n"
            f"📊 درصد انتخاب شده: {percent}%"
            f"{warning}"
        )

        edit_message(
            chat_id,
            message_id,
            text,
            keyboards.attack_percent_keyboard()
        )

        return

    # ==================================
    # تایپ درصد دلخواه
    # ==================================

    if data == "attack_custom_percent":

        session = attack_sessions.get(user_id)

        if session is None:
            return

        session["waiting_percent"] = True

        edit_message(
            chat_id,
            message_id,
            "🔢 درصد قدرت نظامی موردنظر را وارد کنید.\n\n"
            "مثلاً:\n"
            "25\n"
            "40\n"
            "80\n"
            "100"
        )

        return

    # ==================================
    # اجرای حمله
    # ==================================

    if data == "attack_execute":

        session = attack_sessions.get(user_id)

        if session is None:
            return

        percent = session.get("percent")

        if percent is None:
            edit_message(
                chat_id,
                message_id,
                "❌ ابتدا درصد قدرت نظامی را انتخاب کنید."
            )
            return

        defender_id = session["defender_id"]

        defender = database.get_user(
            defender_id
        )

        if defender is None:
            edit_message(
                chat_id,
                message_id,
                "❌ کشور حریف دیگر وجود ندارد."
            )
            attack_sessions.pop(user_id, None)
            return

        attacker = database.get_user(
            user_id
        )

        if attacker is None:
            return

        # ذخیره نام کشور مهاجم
        # چون بعداً کشور مدافع ممکن است ریست شود
        attacker_country = attacker["country"]

        # ==================================
        # ذخیره اطلاعات دفاع قبل از حمله
        # ==================================

        defense_power_before = calculate_defense_power(
            defender_id
        )

        result = execute_attack(
            user_id,
            defender_id,
            percent
        )

        if result is None:
            edit_message(
                chat_id,
                message_id,
                "❌ اجرای حمله با خطا مواجه شد."
            )
            return

        # ==================================
        # گزارش حمله
        # فقط بعد از اجرای موفق کامل حمله
        # ==================================

        damage_percent = 0

        if result["old_hp"] > 0:

            damage_percent = (
                result["damage"] /
                result["old_hp"]
            ) * 100

        if damage_percent > 100:
            damage_percent = 100

        destroyed = result["new_hp"] <= 0

        if destroyed:
            winner = "attack"
        else:
            winner = "defense"

        reports.send_attack_report(
            attacker_country=attacker_country,
            defender_country=defender["country"],
            percent=percent,
            attack_power=result["attack_power"],
            defense_power=defense_power_before,
            damage_percent=damage_percent,
            winner=winner,
            destroyed=destroyed,
            compensation=result["compensation"]
        )

        # ==================================
        # ارسال گزارش حمله به مدافع
        # ==================================

        send_message(
            defender_id,
            "🚨به کشور شما حمله شده!\n"
            f"آسیب وارد شده: {percent}%\n"
            f"کشور حمله کننده: {attacker_country}\n"
            f"غرامت دریافتی: {result['compensation']:,}"
        )

        # ==================================
        # کشور حریف نابود شده
        # ==================================

        if result["new_hp"] <= 0:

            # حذف وضعیت حمله احتمالی مدافع
            attack_sessions.pop(
                defender_id,
                None
            )

            # باز کردن دوباره صفحه انتخاب کشور
            send_message(
                defender_id,
                "💀 کشور شما کاملاً نابود شد!\n\n"
                "🌍 شما باید یک کشور جدید انتخاب کنید.",
                keyboards.country_keyboard()
            )

            text = (
                "⚔️ حمله با موفقیت انجام شد!\n\n"
                f"💥 درصد آسیب وارد شده: {percent}%\n"
                f"🏆 برنده: کشور {attacker_country}\n\n"
                f"💰 غرامت دریافتی: {result['compensation']:,}"
            )

        # ==================================
        # مدافع برنده شده
        # ==================================

        else:

            defender_after = database.get_user(
                defender_id
            )

            text = (
                "⚔️ حمله با موفقیت انجام شد!\n\n"
                f"🏆 برنده: کشور {defender_after['country']}\n"
                f"💥 درصد آسیب وارد شده: {percent}%\n\n"
                f"💰 غرامت دریافتی: {result['compensation']:,}"
            )

        edit_message(
            chat_id,
            message_id,
            text
        )

        attack_sessions.pop(user_id, None)

        return

    # ==================================
    # لغو حمله
    # ==================================

    if data == "attack_cancel":

        attack_sessions.pop(user_id, None)

        edit_message(
            chat_id,
            message_id,
            "🏠 منوی اصلی"
        )

        return
