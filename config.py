import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

# Bot faqat shu kanaldagi postlarga ishlov beradi.
# Kanal ID odatda -100 bilan boshlanadi (masalan: -1001234567890).
CHANNEL_ID = int(os.getenv("CHANNEL_ID", "0"))

# Botni boshqara oladigan adminlarning Telegram user ID'lari, vergul bilan ajratilgan.
ADMIN_IDS = [int(x) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip()]
