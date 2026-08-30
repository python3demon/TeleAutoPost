from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, LinkPreviewOptions
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError
from aiogram.utils.media_group import MediaGroupBuilder
from config import config_user
from states.bot_states import PostCreation, SaveDraft

router = Router()

@router.callback_query(F.data.endswith("post"), PostCreation.holding_host)
async def callback_answer_post(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    command = callback.data
    data = await state.get_data()
    post = data.get("saved_post")
    group_photo = data.get("saved_group", [])
    group_msg_id = data.get("group_msg_id")
    last_msg_id = callback.message.message_id
    await callback.answer()

    if command == "send_post":
        try:
            if group_photo:
                group = MediaGroupBuilder(caption=post)
                for photo_id in group_photo:
                    group.add_photo(media=photo_id)
                await bot.send_media_group(config_user["channel_link"], group.build())
            else:
                await bot.send_message(
                    chat_id=config_user["channel_link"],
                    text=post,
                    link_preview_options=LinkPreviewOptions(
                        is_disabled=config_user["settings"]["link_preview"]
                    )
                )
        except TelegramForbiddenError:
            await callback.message.answer("❌ Ошибка публикации! Проверьте права администратора у бота.")
            return
        except TelegramBadRequest:
            await callback.message.answer("❌ Ошибка запроса! Неверный юзернейм канала.")
            return

        if group_photo:
            try:
                await bot.delete_messages(
                    callback.message.chat.id,
                    message_ids=[id_msg for id_msg in range(group_msg_id, last_msg_id + 1)]
                )
            except TelegramBadRequest:
                pass
            await callback.message.answer("Пост успешно отправлен!")
        else:
            await callback.message.edit_text("Пост успешно отправлен!")
    else:
        if group_photo:
            try:
                await bot.delete_messages(
                    callback.message.chat.id,
                    message_ids=[id_msg for id_msg in range(
                        group_msg_id, last_msg_id + 1
                        )
                    ]
                )
            except TelegramBadRequest:
                pass
        else:
            await callback.message.delete()
    await state.clear()

@router.callback_query(F.data == "save_draft", PostCreation.holding_host)
async def callback_save_draft(callback: CallbackQuery, state: FSMContext, bot: Bot):
    data = await state.get_data()
    post = data.get("saved_post")
    group_photo = data.get("saved_group", [])
    group_msg_id = data.get("group_msg_id")

    if group_msg_id:
        first_msg_id = group_msg_id - 1
    else:
        first_msg_id = callback.message.message_id

    await state.update_data(first_msg_id=first_msg_id)
    await state.set_state(SaveDraft.name_draft)
    await callback.answer()
    
    await callback.message.answer("Какое название для черновика поставить?")

