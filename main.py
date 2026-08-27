import asyncio
import logging
import os
import json
import sys
from aiogram import Bot, Dispatcher, html, F, Router, BaseMiddleware
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.utils.media_group import MediaGroupBuilder
from dotenv import load_dotenv
from aiogram.filters.callback_data import CallbackData
from aiogram.types import (
    Message,
    InlineKeyboardMarkup, InlineKeyboardButton, 
    CallbackQuery, LinkPreviewOptions
)

load_dotenv()
logging.basicConfig(level=logging.INFO, stream=sys.stdout)

FILE_CONFIG = "config.json"
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    sys.exit("❌ Ошибка: Переменная BOT_TOKEN не найдена в файле .env!")

config_user = {
    "id": -1,
    "channel_link": "",
    "settings": {
        "link_preview": True,
    }
}

cache_user = {
    "post_text": ""
}

kb_markup_post = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Отправить", callback_data="send_post")],
    [InlineKeyboardButton(text="Удалить", callback_data="delete_post")]
])

class Registration(StatesGroup):
    waiting_for_channel = State()

try:
    with open(FILE_CONFIG, "r") as config:
        config_user = json.load(config)
except FileNotFoundError:
    pass

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()
router = Router()

@dp.message(CommandStart())
async def command_start_handler(message: Message, state: FSMContext) -> None:
    if config_user["id"] != -1:
        await message.answer(
            f"🤖 Привет, {html.bold(message.from_user.full_name)}!\n\n"
            f"Добро пожаловать в {html.code('TeleAutoPost')} — бот для автоматической "
            f"отправки и планирования постов.\n\n"
            f"Используйте команду /help, чтобы увидеть список доступных функций."
        )
    else:
        config_user["id"] = message.from_user.id
        await message.answer(
            f"Привет, {html.bold(message.from_user.full_name)}!\n"
            f"Для начала работы необходимо пройти регистрацию.\n\n"
            f"Пожалуйста, отправьте юзернейм вашего канала (например, {html.code('@my_channel')}):"
        )
        await state.set_state(Registration.waiting_for_channel)

@dp.message(Registration.waiting_for_channel, F.text)
async def process_channel_registration(message: Message, state: FSMContext) -> None:
    channel_link = message.text.strip()
    if not channel_link.startswith("@"):
        await message.answer("❌ Юзернейм канала должен начинаться с символа @. Попробуйте еще раз:")
        return
    config_user["channel_link"] = channel_link
    with open(FILE_CONFIG, "w") as config:
        json.dump(config_user, config, indent=4)

    await message.answer(
        f"✅ Регистрация успешно завершена!\n"
        f"Бот привязан к каналу: {html.bold(channel_link)}\n\n"
        f"Теперь вы можете присылать тексты для публикации."
    )
    await state.clear()
    

@dp.message(Command("help"))
async def command_help_handler(message: Message) -> None:
    await message.answer(
        f"📌 {html.bold('Справочное меню TeleAutoPost')}\n\n"
        f"Доступные команды на данный момент:\n"
        f"/start — Запустить бота и получить приветственное сообщение\n"
        f"/help — Показать эту справку по командам.\n\n"
        f"Для отправки поста на канал просто введите текст.",
    )

@dp.message(F.text)
async def command_send_post(message: Message) -> None:
    post = message.text
    cache_user["post_text"] = post
    try:
        await message.answer(
            post + f"\n\n{'━'*15}\nДействия:",
            reply_markup=kb_markup_post,
            link_preview_options=LinkPreviewOptions(
                is_disabled=config_user["settings"]["link_preview"]
            )
        )
    except TelegramBadRequest:
        await message.answer("В HTML-разметке есть ошибки. Исправьте их и отправьте сообщение снова.")
    except Exception as e:
        logging.error(f"Ошибка при создании превью: {e}")
        await message.answer("Произошла неизвестная ошибка, повторите.")

class GroupPhotoMiddleware(BaseMiddleware):
    def __init__(self, latency: float = 0.5):
        # {media_group: [media], ...}
        self.cache: [str, list] = {}
        self.latency = latency
    
    async def __call__(self, handler, event, data):
        if not event.photo:
            return await handler(event, data)
        if not event.media_group_id:
            data["group_photo"] = [event.photo[-1].file_id]
            return await handler(event, data)
        
        try:
            self.cache[event.media_group_id].append(event)

        except KeyError:
            self.cache[event.media_group_id] = [event]
            await asyncio.sleep(self.latency)
            msgs = self.cache.pop(event.media_group_id)
            data["group_photo"] = [msg.photo[-2].file_id for msg in msgs]
            result = await handler(event, data)

@router.message(F.photo)
async def command_send_post_with_photo(message: Message, group_photo) -> None:
    post = message.caption
    if post is None:
        await message.answer("Добавьте подпись к фото!")
        return
    
    try:
        group = MediaGroupBuilder(caption=post)
        for photo_id in group_photo:
            group.add_photo(media=photo_id)
        await bot.send_media_group(
            message.from_user.id,
            group.build(),
        )
    except TelegramBadRequest:
        await message.answer("В HTML-разметке есть ошибки. Исправьте их и отправьте сообщение снова.")

@dp.callback_query(F.data.endswith("post"))
async def callback_answer_post(callback: CallbackQuery) -> None:
    command = callback.data
    post = cache_user["post_text"]
    await callback.answer()

    if command == "send_post":
        try:
            if callback.message.photo:
                photo_id = callback.message.photo[-2].file_id
                await bot.send_photo(
                    chat_id=config_user["channel_link"],
                    photo=photo_id,
                    caption=post
                )
            else:
                await bot.send_message(
                    chat_id=config_user["channel_link"],
                    text=post,
                    link_preview_options=LinkPreviewOptions(
                        is_disabled=config_user["settings"]["link_preview"]
                    )
            )
        except TelegramForbiddenError:
            await callback.message.answer(
                "❌ Ошибка публикации!\n"
                "У бота нет прав на отправку сообщений в этот канал. "
                "Убедитесь, что бот добавлен в канал в качестве **Администратора** "
                "и ему разрешено публиковать посты."
            )
            return
        except TelegramBadRequest:
            await callback.message.answer(
                f"❌ Ошибка запроса!\n"
                f"Telegram не смог отправить сообщение. Возможно, указан неверный юзернейм канала."
            )
        await callback.message.delete()
        await callback.message.answer("Пост успешно отправлен!", reply_markup=None)
    else:
        await callback.message.delete()

async def main() -> None:
    dp.include_router(router)
    dp.message.outer_middleware(GroupPhotoMiddleware())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
