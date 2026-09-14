import database
import attack


# ==============================
# کاربران آزمایشی
# ==============================

ATTACKER = 900001
DEFENDER = 900002


# ==============================
# ساخت کاربران
# ==============================

database.create_user(ATTACKER)
database.create_user(DEFENDER)


# ==============================
# آماده‌سازی تجهیزات
# ==============================

# مهاجم: 20 خِیبرشکن
database.add_inventory(
    ATTACKER,
    "kheybershekan",
    20
)

# مدافع: 10 تاد
database.add_inventory(
    DEFENDER,
    "thaad",
    10
)

# HP مدافع = 1000
database.update_hp(
    DEFENDER,
    1000
)


# ==============================
# اجرای حمله
# ==============================

result = attack.execute_attack(
    ATTACKER,
    DEFENDER,
    100
)


# ==============================
# نمایش نتیجه
# ==============================

print("\n========== ATTACK TEST ==========")

print("Attack Power:", result["attack_power"])
print("Defense Power:", result["defense_power"])
print("Damage:", result["damage"])
print("Old HP:", result["old_hp"])
print("New HP:", result["new_hp"])

print("Consumed Defense:")
print(result["consumed_defense"])

print("Consumed Attack:")
print(result["consumed_attack"])

print("=================================\n")