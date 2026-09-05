import asyncio
import logging

from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message

import db
from config import ADMIN_IDS, BOT_TOKEN, CHANNEL_ID

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher(storage=MemoryStorage())

MAX_CAPTION_LEN = 1024  # Telegramning video/rasm caption limiti


class SetCaption(StatesGroup):
    waiting_for_text = State()


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
        "/setcaption — avtomatik izohni belgilash (formatlash va emojilar bilan)\n"
        "/caption — joriy izohni ko'rish\n"
        "/clearcaption — avtomatik izoh qo'shishni to'xtatish\n\n"
        "Eslatma: bot kanalda admin bo'lishi va unda "
        "<b>\"Xabarlarni tahrirlash\" (Edit Messages)</b> huquqi yoqilgan bo'lishi shart."
    )


@dp.message(Command("setcaption"), F.chat.type == "private")
async def cmd_set_caption(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    await state.set_state(SetCaption.waiting_for_text)
    await message.answer(
        "Endi izoh matnini yuboring — qalin/kursiv shrift, havolalar va premium "
        "(custom) emojilar bo'lsa, ular xuddi shu ko'rinishda saqlanadi.\n\n"
        "Bekor qilish uchun /cancel yozing."
    )


@dp.message(Command("cancel"), F.chat.type == "private")
async def cmd_cancel(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    await state.clear()
    await message.answer("Bekor qilindi.")


@dp.message(SetCaption.waiting_for_text, F.chat.type == "private")
async def process_new_caption(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return

    plain_text = message.text or message.caption or ""
    formatted_caption = message.html_text or plain_text

    if not plain_text.strip():
        await message.answer("Matn topilmadi. Qayta yuboring yoki /cancel bilan bekor qiling.")
        return

    if len(plain_text) > MAX_CAPTION_LEN:
        await message.answer(
            f"Matn juda uzun ({len(plain_text)} belgi). Maksimum {MAX_CAPTION_LEN} belgi bo'lishi kerak."
        )
        return

    db.set_caption(formatted_caption)
    await state.clear()
    await message.answer("✅ Izoh saqlandi. Namuna qanday ko'rinishda chiqishini pastda ko'rasiz 👇")
    await message.answer(formatted_caption)


@dp.message(Command("caption"), F.chat.type == "private")
async def cmd_get_caption(message: Message):
    if not is_admin(message.from_user.id):
        return
    caption = db.get_caption()
    if caption:
        await message.answer("Joriy izoh:")
        await message.answer(caption)
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

    # Videoning o'zidagi izoh formatini (qalin, emoji va h.k.) saqlab qolamiz
    old_caption_html = (message.html_text or "").strip()
    new_caption = f"{old_caption_html}\n\n{caption_text}" if old_caption_html else caption_text

    try:
        await bot.edit_message_caption(
            chat_id=message.chat.id,
            message_id=message.message_id,
            caption=new_caption,
        )
    except TelegramBadRequest as e:
        # Ehtimol umumiy uzunlik 1024 belgidan oshib ketgan — shunda faqat
        # o'zimizning izohimizni qo'yib ko'ramiz (eski izoh o'rniga)
        logging.error("Caption tahrirlashda xatolik (birinchi urinish): %s", e)
        try:
            await bot.edit_message_caption(
                chat_id=message.chat.id,
                message_id=message.message_id,
                caption=caption_text,
            )
        except TelegramBadRequest as e2:
            logging.error("Caption tahrirlashda xatolik (ikkinchi urinish): %s", e2)


async def main():
    db.init_db()
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
