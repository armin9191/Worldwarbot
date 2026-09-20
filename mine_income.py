# ==============================
# World War - Mine Income
# ==============================

from datetime import datetime, timedelta

import database


# ==============================
# درآمد هر معدن در روز
# ==============================

MINE_RATES = {
    "diamond_mine": 15_000_000,
    "gold_mine": 10_000_000,
    "silver_mine": 5_000_000,
}


# ==============================
# ساعت واریز
# ==============================

PAYOUT_HOUR = 0
PAYOUT_MINUTE = 0


# ==============================
# اختلاف ساعت ایران با UTC
# ==============================

IRAN_UTC_OFFSET = timedelta(hours=3, minutes=30)


_send_message = None


# ==============================
# اتصال به bot.py
# ==============================

def setup(send_message):
    global _send_message
    _send_message = send_message


# ==============================
# زمان ایران
# ==============================

def get_iran_time():

    utc_now = datetime.utcnow()

    return utc_now + IRAN_UTC_OFFSET


# ==============================
# محاسبه درآمد معادن
# ==============================

def calculate_income(user_id):

    inventory = database.get_inventory(user_id)

    total_income = 0

    for item_id, rate in MINE_RATES.items():

        quantity = inventory.get(item_id, 0)

        total_income += quantity * rate

    return total_income


# ==============================
# دریافت درآمد شرکت
# ==============================

def get_company_income(user_id, today):

    """
    این بخش کاملاً جدا از درآمد معدن است.

    اگر companies.py خراب باشد،
    درآمد معدن همچنان بدون مشکل کار می‌کند.
    """

    try:

        import companies

        income = companies.payout_company_income(
            user_id,
            today
        )

        if income is None:
            return 0

        return int(income)

    except Exception as error:

        print(
            f"Company Income Error "
            f"for user {user_id}: {error}"
        )

        return 0


# ==============================
# پرداخت درآمد روزانه
# ==============================

def check_payout():

    now = get_iran_time()


    # ==============================
    # فقط ساعت مشخص
    # ==============================

    if (
        now.hour != PAYOUT_HOUR
        or now.minute != PAYOUT_MINUTE
    ):
        return


    today = now.strftime("%Y-%m-%d")


    # ==============================
    # جلوگیری از پرداخت دوباره
    # ==============================

    if database.get_last_mine_payout_date() == today:
        return


    # ==============================
    # دریافت رنکینگ
    # ==============================

    ranking_text = None

    try:

        import ranking

        ranking_text = ranking.get_ranking_text()

    except Exception as error:

        print(
            f"Ranking Error: {error}"
        )

        ranking_text = None


    # ==============================
    # دریافت کشورها
    # ==============================

    countries = database.get_selected_countries()


    # ==============================
    # پرداخت به کشورها
    # ==============================

    for country_data in countries:

        user_id = country_data["user_id"]
        country = country_data["country"]


        # ==============================
        # درآمد معدن
        # ==============================

        mine_income = 0

        try:

            mine_income = calculate_income(
                user_id
            )

            if mine_income < 0:
                mine_income = 0

        except Exception as error:

            print(
                f"Mine Income Error "
                f"for user {user_id}: {error}"
            )

            mine_income = 0


        # ==============================
        # واریز معدن
        # ==============================

        if mine_income > 0:

            try:

                database.add_budget(
                    user_id,
                    mine_income
                )

            except Exception as error:

                print(
                    f"Mine Payment Error "
                    f"for user {user_id}: {error}"
                )

                # اگر واریز معدن شکست خورد،
                # مبلغ معدن را درآمد موفق حساب نمی‌کنیم.

                mine_income = 0


        # ==============================
        # درآمد شرکت
        # ==============================

        company_income = get_company_income(
            user_id,
            today
        )


        # ==============================
        # مجموع درآمد
        # ==============================

        total_income = (
            mine_income +
            company_income
        )


        # ==============================
        # کاربر
        # ==============================

        user = database.get_user(user_id)

        if user is None:

            continue


        # ==============================
        # اگر هیچ درآمدی وجود ندارد
        # ==============================

        if total_income <= 0:

            continue


        # ==============================
        # پیام درآمد
        # ==============================

        message = (
            "💰 درآمد روزانه کشور شما\n\n"

            f"🌍 {country}\n\n"

            "⛏️ درآمد معدن:\n"
            f"{mine_income:,} دلار\n\n"

            "🏢 درآمد شرکت:\n"
            f"{company_income:,} دلار\n\n"

            "💵 مجموع درآمد امروز:\n"
            f"{total_income:,} دلار\n\n"

            "💳 بودجه جدید کشور شما:\n"
            f"{user['budget']:,} دلار\n\n"

            "⏰ زمان واریز: 05:57\n\n"

            "⚔️ فرمانده، کشور شما هر روز بر اساس "
            "منابع، معادن و شرکت‌های خود درآمد کسب می‌کند."
        )


        # ==============================
        # رنکینگ
        # ==============================

        if ranking_text:

            message += (
                "\n\n"
                "━━━━━━━━━━━━━━━━━━\n\n"
                f"{ranking_text}"
            )


        # ==============================
        # ارسال پیام
        # ==============================

        if _send_message is not None:

            try:

                _send_message(
                    user_id,
                    message
                )

            except Exception as error:

                print(
                    f"Send Income Message Error "
                    f"for user {user_id}: {error}"
                )


    # ==============================
    # ثبت پرداخت روزانه
    # ==============================

    database.set_last_mine_payout_date(
        today
    )


# ==============================
# Handle Update
# ==============================

def handle_update(update):

    # این Feature نیازی به پیام یا Callback ندارد.

    pass
