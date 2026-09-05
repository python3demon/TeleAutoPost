import logging
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, LinkPreviewOptions
from aiogram.fsm.context import FSMContext
from aiogram.utils.media_group import MediaGroupBuilder
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError

from config import config_user, save_config
from keyboards.inline import kb_markup_post
from states.bot_states import Registration, PostCreation

router = Router()

@router.message(Registration.waiting_for_channel, F.text)
async def process_channel_registration(message: Message, state: FSMContext) -> None:
    channel_link = message.text.strip()
    if not channel_link.startswith("@"):
        await message.answer("❌ Юзернейм канала должен начинаться с символа @. Попробуйте еще раз:")
        return
    config_user["channel_link"] = channel_link
    save_config()

    await message.answer(
        f"✅ Регистрация успешно завершена!\n"
        f"Бот привязан к каналу: {html.bold(channel_link)}\n\n"
        f"Теперь вы можете присылать тексты для публикации."
    )
    await state.clear()

@router.message(F.text == "Создать пост")
async def command_start_create_post(message: Message, state: FSMContext) -> None:
    await state.clear()
    await state.set_state(PostCreation.waiting_for_text)
    await message.answer("Отправьте текст поста: ")

@router.message(F.text, PostCreation.waiting_for_text)
async def command_create_post(message: Message, state: FSMContext) -> None:
    post = message.text
    await state.update_data(saved_post=post)
    await state.set_state(PostCreation.holding_host)
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

#@router.message(F.photo) Фича будет доступна в следьющих версиях
async def command_send_post_with_photo(message: Message, group_photo: list, post: str, state: FSMContext, bot: Bot) -> None:
    if not post:
        await message.answer("Добавьте подпись к фото!")
        return

    group = MediaGroupBuilder(caption=post)
    for photo_id in group_photo:
        group.add_photo(media=photo_id)

    await state.update_data(saved_post=post, saved_group=group_photo)
    await state.set_state(PostCreation.holding_host)

    try:
        group_msg = await bot.send_media_group(message.from_user.id, group.build())
        await message.answer("Выберите действие:", reply_markup=kb_markup_post)
        await state.update_data(group_msg_id=group_msg[0].message_id)
    except TelegramBadRequest as e:
        logging.error(e)
        await message.answer("В HTML-разметке есть ошибки. Исправьте их и отправьте сообщение снова.")

@router.callback_query(F.data == "send_post", PostCreation.holding_host)
async def callback_answer_post(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    command = callback.data
    data = await state.get_data()
    post = data.get("saved_post")
    last_msg_id = callback.message.message_id
    await callback.answer("Отправка...")

    try:
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

    await state.clear()
    await callback.message.edit_text("Пост успешно отправлен!")

@router.callback_query(F.data == "delete_post", PostCreation.holding_host)
async def command_delete_post(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    await state.clear()
    await callback.message.delete()
