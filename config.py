import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

# Ixtiyoriy: eski (faqat bitta kanalli) versiyadan saqlanib qolgan izohni
# yangi ko'p-kanalli tizimga bir martalik ko'chirish va o'sha kanalni
# avtomatik ro'yxatga olish uchun ishlatiladi. Yangi kanallar uchun bu
# o'zgaruvchini o'zgartirish shart emas.
LEGACY_CHANNEL_ID = int(os.getenv("CHANNEL_ID", "0")) or None

# Botning operatori (siz) — ochiq/omma uchun ishlaydigan botda bu ID'lar
# maxsus huquqqa ega emas, faqat: (1) /stats buyrug'ini ko'ra oladi,
# (2) eski, hali "egasi" biriktirilmagan kanallar shularga bog'lanadi
# (bir martalik migratsiya). Vergul bilan bir nechta ID kiritish mumkin.
OPERATOR_IDS = [int(x) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip()]

# Botdan foydalanish uchun majburiy obuna bo'linishi kerak bo'lgan kanal.
# Bot bu kanalda a'zolikni tekshira olishi uchun, shu kanalga ham
# (kamida oddiy a'zo sifatida, tavsiya etiladi — admin sifatida) qo'shilgan
# bo'lishi kerak, aks holda tekshiruv ishlamay qolishi mumkin.
REQUIRED_CHANNEL = os.getenv("REQUIRED_CHANNEL", "@namanganliklar_uz")
