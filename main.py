import asyncio
import logging
import os
import sys
from aiogram import Bot, Dispatcher, html, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO, stream=sys.stdout)
TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_LINK = os.getenv("CHANNEL_LINK")
if not TOKEN:
    sys.exit("❌ Ошибка: Переменная BOT_TOKEN не найдена в файле .env!")

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer(
        f"🤖 Привет, {html.bold(message.from_user.full_name)}!\n\n"
        f"Добро пожаловать в {html.code('TeleAutoPost')} — бот для автоматической "
        f"отправки и планирования постов.\n\n"
        f"Используйте команду /help, чтобы увидеть список доступных функций."
    )

@dp.message(Command("help"))
async def command_help_handler(message: Message) -> None:
    await message.answer(
        f"📌 {html.bold('Справочное меню TeleAutoPost')}\n\n"
        f"Доступные команды на данный момент:\n"
        f"/start — Запустить бота и получить приветственное сообщение\n"
        f"/help — Показать эту справку по командам\n\n"
        f"Для отправки поста на канал проосто введите текст."
    )

@dp.message(F.text)
async def command_send_post(message: Message) -> None:
    post = message.text
    kb_markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Отправить", callback_data="send_post")],
        [InlineKeyboardButton(text="Удалить", callback_data="delete_post")]
    ])
    await message.answer(post + f"\n\n{'━'*15}\nДействия:", reply_markup=kb_markup)

@dp.callback_query(F.data.endswith("post"))
async def callback_answer_post(callback: CallbackQuery) -> None:
    command = callback.data
    post_usr = callback.message.text.replace(f"\n\n{'━'*15}\nДействия:", "")
    if callback.data == "send_post":
        await bot.send_message(chat_id=CHANNEL_LINK, text=post_usr)
        await callback.message.edit_text("Пост успешно отправлен!", reply_markup=None)
    else:
        await callback.message.delete()

    await callback.answer()

async def main() -> None:
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
