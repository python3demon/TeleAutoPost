import asyncio
import logging
import os
import sys
from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO, stream=sys.stdout)
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    sys.exit("❌ Ошибка: Переменная BOT_TOKEN не найдена в файле .env!")

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
        f"⏳ {html.italic('Разработка функций отправки постов начнется в v0.2.0-alpha')}"
    )

async def main() -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
