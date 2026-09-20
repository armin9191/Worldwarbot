# ==============================
# World War Bot - Configuration
# ==============================

import os

# توکن ربات بله
BOT_TOKEN = "685363715:pYL2jAvDbj5SWa7wT1Mgbw5lXP6ZL_tTcPM"

# آیدی عددی ادمین‌ها
ADMINS = [
    595450272,
]

# آدرس API بله
API_URL = f"https://tapi.bale.ai/bot{BOT_TOKEN}"

# تنظیمات عمومی
BOT_NAME = "World War"

# ==============================
# تنظیمات دیتابیس (پایدار روی Railway)
# ==============================
# اگر متغیر محیطی DATABASE_PATH وجود داشت از اون استفاده می‌کنه
# در غیر این صورت از مسیر /data/world_war.db استفاده می‌کنه
DATABASE_NAME = os.environ.get("DATABASE_PATH", "/data/world_war.db")

# ==============================
# تنظیمات صدور بیانیه
# ==============================

# یوزرنیم کانال انتشار بیانیه
STATEMENT_CHANNEL_ID = "@jang_jahani_b"

# یوزرنیم گروه انتشار بیانیه
STATEMENT_GROUP_ID = "@jang_jahani_bb"

# تایید خودکار بیانیه‌ها
# True  = مستقیم منتشر شود
# False = برای تایید ادمین ارسال شود
AUTO_APPROVE_STATEMENTS = False

# ==============================
# تنظیمات جوین اجباری
# ==============================

REQUIRED_CHANNEL = "@jang_jahani_b"
REQUIRED_GROUP = "@jang_jahani_bb"
