import asyncio
import logging
import os
import json
import sys
from aiogram import Bot, Dispatcher, html, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO, stream=sys.stdout)

FILE_CONFIG = "config.json"
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    sys.exit("❌ Ошибка: Переменная BOT_TOKEN не найдена в файле .env!")

config_user = {
    "id": -1,
    "channel_link": ""
}

class Registration(StatesGroup):
    waiting_for_channel = State()

try:
    with open(FILE_CONFIG, "r") as config:
        config_user = json.load(config)
except FileNotFoundError:
    pass

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

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
    kb_markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Отправить", callback_data="send_post")],
        [InlineKeyboardButton(text="Удалить", callback_data="delete_post")]
    ])
    try:
        await message.answer(post + f"\n\n{'━'*15}\nДействия:", reply_markup=kb_markup)
    except TelegramBadRequest:
        await message.answer("В HTML-разметке есть ошибки. Исправьте их и отправьте сообщение снова.")
    except:
        await message.answer("Произошла неизвестная ошибка, повторите.")

@dp.callback_query(F.data.endswith("post"))
async def callback_answer_post(callback: CallbackQuery) -> None:
    command = callback.data
    post_usr = callback.message.html_text.replace(f"\n\n{'━'*15}\nДействия:", "")
    await callback.answer()

    if command == "send_post":
        try:
            await bot.send_message(chat_id=config_user["channel_link"], text=post_usr)
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
        await callback.message.edit_text("Пост успешно отправлен!", reply_markup=None)
    else:
        await callback.message.delete()

async def main() -> None:
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
