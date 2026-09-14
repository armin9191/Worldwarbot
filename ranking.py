# ==============================
# World War - Military Ranking
# ==============================

import database
from attack import ATTACK_WEIGHTS


# ==============================
# محاسبه قدرت نظامی یک کشور
# ==============================

def calculate_military_power(user_id):

    try:
        inventory = database.get_inventory(user_id)

    except Exception as error:
        print(f"Ranking Inventory Error ({user_id}): {error}")
        return 0

    if not isinstance(inventory, dict):
        return 0

    total_power = 0

    for item_id, quantity in inventory.items():

        try:
            quantity = int(quantity)

        except (TypeError, ValueError):
            continue

        # موجودی منفی حساب نشود
        if quantity <= 0:
            continue

        weight = ATTACK_WEIGHTS.get(item_id, 0)

        try:
            weight = int(weight)

        except (TypeError, ValueError):
            continue

        # تجهیزات بدون قدرت هجومی حساب نشوند
        if weight <= 0:
            continue

        total_power += quantity * weight

    return total_power


# ==============================
# دریافت رنکینگ کشورها
# ==============================

def get_ranking():

    ranking = []

    try:
        selected_countries = database.get_selected_countries()

    except Exception as error:
        print(f"Ranking Countries Error: {error}")
        return ranking

    if not selected_countries:
        return ranking

    for country_data in selected_countries:

        try:
            user_id = country_data.get("user_id")
            country = country_data.get("country")

            if not user_id or not country:
                continue

            power = calculate_military_power(user_id)

            ranking.append({
                "user_id": user_id,
                "country": country,
                "power": power
            })

        except Exception as error:
            print(f"Ranking Country Error: {error}")
            continue

    # بیشترین قدرت = رتبه اول
    ranking.sort(
        key=lambda item: item["power"],
        reverse=True
    )

    # تعیین رتبه
    for index, item in enumerate(ranking, start=1):
        item["rank"] = index

    return ranking


# ==============================
# ساخت متن رنکینگ
# ==============================

def get_ranking_text():

    try:
        ranking = get_ranking()

    except Exception as error:
        print(f"Ranking Text Error: {error}")

        return None

    if not ranking:

        return (
            "🏆 رنکینگ قدرت نظامی\n\n"
            "❌ در حال حاضر هیچ کشوری توسط بازیکنان "
            "انتخاب نشده است."
        )

    text = "🏆 رنکینگ قدرت نظامی\n\n"

    for item in ranking:

        try:
            rank = item["rank"]
            country = item["country"]
            power = item["power"]

            if rank == 1:
                rank_text = "🥇"

            elif rank == 2:
                rank_text = "🥈"

            elif rank == 3:
                rank_text = "🥉"

            else:
                rank_text = f"{rank}."

            text += (
                f"{rank_text} {country} — "
                f"{power:,} قدرت نظامی\n"
            )

        except Exception as error:
            print(f"Ranking Format Error: {error}")
            continue

    return text