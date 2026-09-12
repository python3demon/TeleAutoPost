from aiogram import Router, F, Bot
from aiogram.types import Message
from config import config_user
from keyboards.inline import build_list_draft

router = Router()

@router.message(F.text == "Мои черновики")
async def get_my_draft(message: Message):
    posts = config_user["drafts"]

    buttons_markup = await build_list_draft(posts)
    await message.answer("Ваши черновики", reply_markup=buttons_markup)