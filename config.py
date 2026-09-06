import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

# Ixtiyoriy: eski (faqat bitta kanalli) versiyadan saqlanib qolgan izohni
# yangi ko'p-kanalli tizimga bir martalik ko'chirish va o'sha kanalni
# avtomatik ro'yxatga olish uchun ishlatiladi. Yangi kanallar uchun bu
# o'zgaruvchini o'zgartirish shart emas — ular admin qo'shilganda o'zi
# ro'yxatga olinadi.
LEGACY_CHANNEL_ID = int(os.getenv("CHANNEL_ID", "0")) or None

# Botni boshqara oladigan adminlarning Telegram user ID'lari, vergul bilan ajratilgan.
ADMIN_IDS = [int(x) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip()]
