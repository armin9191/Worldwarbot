# ==============================
# World War - Military System
# ==============================

import database


# ==============================
# وزن دفاعی پدافندها
# ==============================

DEFENSE_WEIGHTS = {
    "patriot": 40,
    "phalanx": 35,
    "thaad": 60,
}


# ==============================
# محاسبه قدرت دفاعی
# ==============================

def calculate_defense_power(user_id):

    inventory = database.get_inventory(user_id)

    total_defense = 0

    for item_id, quantity in inventory.items():

        weight = DEFENSE_WEIGHTS.get(
            item_id,
            0
        )

        total_defense += quantity * weight

    return total_defense
