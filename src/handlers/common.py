from aiogram import Router, html, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from config import config_user
from states.bot_states import Registration

router = Router()

@router.message(CommandStart())
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

@router.message(Command("help"))
async def command_help_handler(message: Message) -> None:
    await message.answer(
        f"📌 {html.bold('Справочное меню TeleAutoPost')}\n\n"
        f"Доступные команды на данный момент:\n"
        f"/start — Запустить бота и получить приветственное сообщение\n"
        f"/help — Показать эту справку по командам.\n\n"
        f"Для отправки поста на канал просто введите текст.",
    )