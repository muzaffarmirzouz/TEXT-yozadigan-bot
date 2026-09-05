import asyncio
import logging

from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.types import Message

import db
from config import ADMIN_IDS, BOT_TOKEN, CHANNEL_ID

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher()

MAX_CAPTION_LEN = 1024  # Telegramning video/rasm caption limiti


def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS


# ---------- Admin buyruqlari (botning shaxsiy chatida) ----------

@dp.message(Command("start"), F.chat.type == "private")
async def cmd_start(message: Message):
    if not is_admin(message.from_user.id):
        await message.answer("Bu bot faqat administratorlar uchun.")
        return
    await message.answer(
        "Salom! Men kanalga tashlangan video/rasmlarga avtomatik izoh qo'shib boraman.\n\n"
        "Buyruqlar:\n"
        "/setcaption &lt;matn&gt; — avtomatik izohni belgilash\n"
        "/caption — joriy izohni ko'rish\n"
        "/clearcaption — avtomatik izoh qo'shishni to'xtatish\n\n"
        "Eslatma: bot kanalda admin bo'lishi va unda "
        "<b>\"Xabarlarni tahrirlash\" (Edit Messages)</b> huquqi yoqilgan bo'lishi shart."
    )


@dp.message(Command("setcaption"), F.chat.type == "private")
async def cmd_set_caption(message: Message):
    if not is_admin(message.from_user.id):
        return
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2 or not parts[1].strip():
        await message.answer(
            "Matnni ham yozing. Masalan:\n/setcaption Obuna bo'lish uchun: @kanal_nomi"
        )
        return
    caption = parts[1].strip()
    if len(caption) > MAX_CAPTION_LEN:
        await message.answer(
            f"Matn juda uzun ({len(caption)} belgi). Maksimum {MAX_CAPTION_LEN} belgi bo'lishi kerak."
        )
        return
    db.set_caption(caption)
    await message.answer(f"✅ Izoh saqlandi. Endi barcha yangi video/rasmlarga shu qo'shiladi:\n\n{caption}")


@dp.message(Command("caption"), F.chat.type == "private")
async def cmd_get_caption(message: Message):
    if not is_admin(message.from_user.id):
        return
    caption = db.get_caption()
    if caption:
        await message.answer(f"Joriy izoh:\n\n{caption}")
    else:
        await message.answer("Hozircha izoh belgilanmagan. /setcaption orqali qo'shing.")


@dp.message(Command("clearcaption"), F.chat.type == "private")
async def cmd_clear_caption(message: Message):
    if not is_admin(message.from_user.id):
        return
    db.clear_caption()
    await message.answer("✅ Avtomatik izoh o'chirildi. Endi yangi postlarga hech narsa qo'shilmaydi.")


# ---------- Kanal postlariga avtomatik izoh qo'shish ----------

@dp.channel_post(F.video | F.photo)
async def handle_channel_post(message: Message):
    if CHANNEL_ID and message.chat.id != CHANNEL_ID:
        return  # bu bizning kanalimiz emas — tegilmaymiz

    caption_text = db.get_caption()
    if not caption_text:
        return  # izoh sozlanmagan — hech narsa qilmaymiz

    old_caption = (message.caption or "").strip()
    new_caption = f"{old_caption}\n\n{caption_text}" if old_caption else caption_text

    if len(new_caption) > MAX_CAPTION_LEN:
        new_caption = new_caption[: MAX_CAPTION_LEN - 3] + "..."

    try:
        await bot.edit_message_caption(
            chat_id=message.chat.id,
            message_id=message.message_id,
            caption=new_caption,
        )
    except TelegramBadRequest as e:
        logging.error("Caption tahrirlashda xatolik: %s", e)


async def main():
    db.init_db()
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
