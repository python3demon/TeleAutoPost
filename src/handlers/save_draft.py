from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram import Router, F, Bot
from config import config_user, save_config
from states.bot_states import SaveDraft
from aiogram.exceptions import TelegramBadRequest

router = Router()

@router.message(F.text, SaveDraft.name_draft)
async def get_name_draft(message: Message, state: FSMContext, bot: Bot) -> None:
    name_draft = message.text
    if len(name_draft) > 12:
        await message.answer("Слишком длинное название")
        return
    
    data = await state.get_data()
    post = data.get("saved_post")
    group_photo = data.get("group_photo", [])
    group_msg_id = data.get("group_msg_id")
    first_msg_id = (data.get("first_msg_id")
        if not group_photo
        else group_msg_id
    )
    last_msg_id = message.message_id

    drafts = config_user["drafts"]
    drafts[name_draft] = {"post": post, "group_photo": group_photo}
    save_config()
    await state.clear()
    
    try:
        await bot.delete_messages(
            message.chat.id,
            message_ids=[id_msg for id_msg in range(
                first_msg_id, last_msg_id + 1
                )
            ]
        )
    except TelegramBadRequest:
        pass

    await message.answer("Пост успешно сохранен!")