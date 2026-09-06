import asyncio
import logging

from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.exceptions import TelegramAPIError, TelegramBadRequest
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (
    CallbackQuery,
    ChatMemberUpdated,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

import db
from config import ADMIN_IDS, BOT_TOKEN, LEGACY_CHANNEL_ID

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher(storage=MemoryStorage())

MAX_CAPTION_LEN = 1024  # Telegramning video/rasm caption limiti
ALBUM_DEBOUNCE = 1.5  # soniya — albomning barcha elementlari kelishini kutamiz

album_messages: dict[str, list[Message]] = {}
album_tasks: dict[str, asyncio.Task] = {}


class SetCaption(StatesGroup):
    waiting_for_text = State()


def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS


def channels_keyboard(prefix: str) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text=title, callback_data=f"{prefix}:{channel_id}")]
        for channel_id, title in db.list_channels()
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


# ---------- Kanal bot admin qilib qo'shilganda/olib tashlanganda ----------

@dp.my_chat_member()
async def on_my_chat_member(update: ChatMemberUpdated):
    if update.chat.type != "channel":
        return

    status = update.new_chat_member.status
    logging.info(
        "my_chat_member: chat_id=%s, title=%s, status=%s",
        update.chat.id, update.chat.title, status,
    )
    if status == "administrator":
        db.register_channel(update.chat.id, update.chat.title or str(update.chat.id))
        text = (
            f"✅ Yangi kanal ro'yxatga olindi: <b>{update.chat.title}</b>\n"
            "Endi /setcaption orqali shu kanal uchun ham izoh belgilashingiz mumkin."
        )
        for admin_id in ADMIN_IDS:
            try:
                await bot.send_message(admin_id, text)
            except TelegramBadRequest:
                pass
    elif status in ("left", "kicked", "member"):
        db.remove_channel(update.chat.id)


# ---------- Admin buyruqlari (botning shaxsiy chatida) ----------

@dp.message(Command("start"), F.chat.type == "private")
async def cmd_start(message: Message):
    if not is_admin(message.from_user.id):
        await message.answer("Bu bot faqat administratorlar uchun.")
        return
    await message.answer(
        "Salom! Men kanal(lar)ga tashlangan video/rasmlarga avtomatik izoh qo'shib boraman.\n\n"
        "Buyruqlar:\n"
        "/setcaption — kanal tanlab, izoh belgilash (formatlash va emojilar bilan)\n"
        "/caption — bir kanalning joriy izohini ko'rish\n"
        "/clearcaption — bir kanal uchun avtomatik izohni to'xtatish\n"
        "/channels — ro'yxatga olingan barcha kanallar\n\n"
        "Yangi kanal qo'shish uchun botni o'sha kanalga admin qilib qo'shing va "
        "<b>\"Xabarlarni tahrirlash\" (Edit Messages)</b> huquqini yoqing — bot "
        "avtomatik ravishda ro'yxatga olinadi."
    )


@dp.message(Command("channels"), F.chat.type == "private")
async def cmd_channels(message: Message):
    if not is_admin(message.from_user.id):
        return
    channels = db.list_channels()
    if not channels:
        await message.answer(
            "Hozircha hech qanday kanal ro'yxatga olinmagan. Botni kanalga admin "
            "qilib qo'shing (\"Xabarlarni tahrirlash\" huquqi bilan)."
        )
        return
    lines = []
    for channel_id, title in channels:
        has_caption = "✅ izoh bor" if db.get_caption(channel_id) else "— izoh yo'q"
        lines.append(f"• {title} ({has_caption})")
    await message.answer("Ro'yxatga olingan kanallar:\n" + "\n".join(lines))


@dp.message(Command("setcaption"), F.chat.type == "private")
async def cmd_set_caption(message: Message):
    if not is_admin(message.from_user.id):
        return
    if not db.list_channels():
        await message.answer(
            "Hozircha hech qanday kanal ro'yxatga olinmagan. Avval botni kanalga "
            "admin qilib qo'shing (\"Xabarlarni tahrirlash\" huquqi bilan)."
        )
        return
    await message.answer(
        "Qaysi kanal uchun izoh belgilaymiz?",
        reply_markup=channels_keyboard("setcap"),
    )


@dp.callback_query(F.data.startswith("setcap:"))
async def cb_choose_setcaption(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer()
        return
    channel_id = int(callback.data.split(":", 1)[1])
    title = db.get_channel_title(channel_id) or str(channel_id)
    await state.set_state(SetCaption.waiting_for_text)
    await state.update_data(channel_id=channel_id)
    await callback.message.edit_text(
        f"«{title}» uchun izoh matnini yuboring — qalin/kursiv shrift, havolalar "
        f"va premium emojilar saqlanadi.\nBekor qilish uchun /cancel."
    )
    await callback.answer()


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

    data = await state.get_data()
    channel_id = data.get("channel_id")
    if not channel_id:
        await state.clear()
        await message.answer("Nimadir noto'g'ri ketdi, /setcaption bilan qayta boshlang.")
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

    db.set_caption(channel_id, formatted_caption)
    await state.clear()
    title = db.get_channel_title(channel_id) or str(channel_id)
    await message.answer(f"✅ «{title}» uchun izoh saqlandi. Namuna qanday chiqishini pastda ko'rasiz 👇")
    await message.answer(formatted_caption)


@dp.message(Command("caption"), F.chat.type == "private")
async def cmd_get_caption(message: Message):
    if not is_admin(message.from_user.id):
        return
    if not db.list_channels():
        await message.answer("Hozircha hech qanday kanal ro'yxatga olinmagan.")
        return
    await message.answer(
        "Qaysi kanalning izohini ko'rmoqchisiz?",
        reply_markup=channels_keyboard("getcap"),
    )


@dp.callback_query(F.data.startswith("getcap:"))
async def cb_get_caption(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer()
        return
    channel_id = int(callback.data.split(":", 1)[1])
    title = db.get_channel_title(channel_id) or str(channel_id)
    caption = db.get_caption(channel_id)
    await callback.answer()
    if caption:
        await callback.message.answer(f"«{title}» uchun joriy izoh:")
        await callback.message.answer(caption)
    else:
        await callback.message.answer(f"«{title}» uchun izoh hali belgilanmagan.")


@dp.message(Command("clearcaption"), F.chat.type == "private")
async def cmd_clear_caption(message: Message):
    if not is_admin(message.from_user.id):
        return
    if not db.list_channels():
        await message.answer("Hozircha hech qanday kanal ro'yxatga olinmagan.")
        return
    await message.answer(
        "Qaysi kanalning avtomatik izohini o'chiramiz?",
        reply_markup=channels_keyboard("clrcap"),
    )


@dp.callback_query(F.data.startswith("clrcap:"))
async def cb_clear_caption(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer()
        return
    channel_id = int(callback.data.split(":", 1)[1])
    title = db.get_channel_title(channel_id) or str(channel_id)
    db.clear_caption(channel_id)
    await callback.answer("O'chirildi")
    await callback.message.edit_text(f"✅ «{title}» uchun avtomatik izoh o'chirildi.")


# ---------- Kanal postlariga avtomatik izoh qo'shish ----------

async def apply_caption(chat_id: int, message_id: int, base_html: str, caption_text: str) -> None:
    old = base_html.strip()
    new_caption = f"{old}\n\n{caption_text}" if old else caption_text
    try:
        await bot.edit_message_caption(chat_id=chat_id, message_id=message_id, caption=new_caption)
        logging.info("Caption yangilandi: chat_id=%s, message_id=%s", chat_id, message_id)
    except TelegramAPIError as e:
        logging.error(
            "Caption tahrirlashda xatolik (birinchi urinish): chat_id=%s, message_id=%s, xato=%s",
            chat_id, message_id, e,
        )
        try:
            await bot.edit_message_caption(chat_id=chat_id, message_id=message_id, caption=caption_text)
            logging.info("Caption (zaxira variant) yangilandi: chat_id=%s, message_id=%s", chat_id, message_id)
        except TelegramAPIError as e2:
            logging.error(
                "Caption tahrirlashda xatolik (ikkinchi urinish): chat_id=%s, message_id=%s, xato=%s",
                chat_id, message_id, e2,
            )


@dp.channel_post(~F.media_group_id, F.video | F.photo)
async def handle_channel_post(message: Message):
    """Yakka (albom bo'lmagan) video/rasm postlari."""
    logging.info("Yakka post keldi: chat_id=%s, title=%s", message.chat.id, message.chat.title)
    caption_text = db.get_caption(message.chat.id)
    if not caption_text:
        logging.info("chat_id=%s uchun izoh topilmadi — tegilmaymiz.", message.chat.id)
        return
    await apply_caption(message.chat.id, message.message_id, message.html_text or "", caption_text)


@dp.channel_post(F.media_group_id, F.video | F.photo)
async def handle_album_item(message: Message):
    """Albom (bir vaqtda yuborilgan bir nechta video/rasm) postlari."""
    group_id = message.media_group_id
    album_messages.setdefault(group_id, []).append(message)

    if group_id in album_tasks:
        album_tasks[group_id].cancel()
    album_tasks[group_id] = asyncio.create_task(process_album(group_id))


async def process_album(group_id: str) -> None:
    await asyncio.sleep(ALBUM_DEBOUNCE)
    messages = album_messages.pop(group_id, [])
    album_tasks.pop(group_id, None)
    if not messages:
        return

    first = min(messages, key=lambda m: m.message_id)
    logging.info("Albom keldi: chat_id=%s, title=%s, elementlar=%s", first.chat.id, first.chat.title, len(messages))
    caption_text = db.get_caption(first.chat.id)
    if not caption_text:
        logging.info("chat_id=%s uchun izoh topilmadi — tegilmaymiz.", first.chat.id)
        return

    # Telegram butun albom uchun faqat BITTA elementning (birinchisining)
    # izohini ko'rsatadi — shu sabab faqat o'shanga yozamiz
    await apply_caption(first.chat.id, first.message_id, first.html_text or "", caption_text)


async def main():
    db.init_db()
    if LEGACY_CHANNEL_ID:
        try:
            chat = await bot.get_chat(LEGACY_CHANNEL_ID)
            db.register_channel(chat.id, chat.title or str(chat.id))
        except Exception as e:
            logging.warning("Eski CHANNEL_ID uchun ma'lumot olinmadi: %s", e)
        db.migrate_legacy_caption(LEGACY_CHANNEL_ID)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
