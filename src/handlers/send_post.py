import logging
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, LinkPreviewOptions
from aiogram.fsm.context import FSMContext
from aiogram.utils.media_group import MediaGroupBuilder
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError

from config import config_user, save_config
from keyboards.inline import kb_markup_post
from keyboards.reply import skip_or_add_photo
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

async def send_preview(message: Message, bot: Bot, state: FSMContext) -> None:
    await state.set_state(PostCreation.holding_host)
    data = await state.get_data()
    post = data.get("post")
    group_photo = data.get("group_photo")

    try:
        if not group_photo:
            await message.answer(
                post,
                link_preview_options=LinkPreviewOptions(
                    is_disabled=config_user["settings"]["link_preview"]
                )
            )
            await message.answer("Выберите действие:", reply_markup=kb_markup_post)
        else:
            if len(post) > 1024:
                await message.answer("Текст слишком длинный. Лимит 1024 символов.")
                await state.clear()
                return
            group = MediaGroupBuilder(caption=post)
            for photo_id in group_photo:
                group.add_photo(media=photo_id)
            await bot.send_media_group(message.from_user.id, group.build())
            await message.answer("Выберите действие:", reply_markup=kb_markup_post)
    except TelegramBadRequest:
        await message.answer(
            "В HTML-разметке есть ошибки. Исправьте их и отправьте заново.",
            reply_markup=kb_start_reply
        )
        await state.clear()
    except Exception as e:
        logging.error(f"Ошибка при создании превью: {e}")
        await message.answer("Произошла неизвестная ошибка, повторите.")
        await state.clear()

@router.message(F.text == "Создать пост")
async def command_start_create_post(message: Message, state: FSMContext) -> None:
    await state.clear()
    await state.set_state(PostCreation.waiting_for_text)
    await message.answer("Отправьте текст поста: ")

@router.message(F.text, PostCreation.waiting_for_text)
async def command_create_post(message: Message, state: FSMContext) -> None:
    post = message.text
    await state.update_data(post=post)
    await message.answer("Добавьте фото/фотоальбом:", reply_markup=skip_or_add_photo)
    await state.set_state(PostCreation.waiting_for_photo)

@router.message(F.text == "Пропустить", PostCreation.waiting_for_photo)
async def skip_func(message: Message, state: FSMContext, bot: Bot):
    await send_preview(message, bot, state)

@router.message(F.photo, PostCreation.waiting_for_photo)
async def add_photo(message: Message, group_photo: list, state: FSMContext, bot: Bot) -> None:
    await state.update_data(group_photo=group_photo)
    await send_preview(message, bot, state)

@router.message(F.text, PostCreation.waiting_for_photo)
async def other_text_instead(message: Message):
    await message.answer("Отправьте изображение или нажмите на кнопку «Пропустить».")

@router.callback_query(F.data == "send_post", PostCreation.holding_host)
async def callback_answer_post(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    command = callback.data
    data = await state.get_data()
    post = data.get("post")
    group_photo = data.get("group_photo")
    last_msg_id = callback.message.message_id
    await callback.answer("Отправка...")
    send = False

    try:
        if not group_photo:
            await bot.send_message(
                chat_id=config_user["channel_link"],
                text=post,
                link_preview_options=LinkPreviewOptions(
                    is_disabled=config_user["settings"]["link_preview"]
                )
            )
        else:
            group = MediaGroupBuilder(caption=post)
            for photo_id in group_photo:
                group.add_photo(media=photo_id)
            await bot.send_media_group(config_user["channel_link"], group.build())
        send = True
    except TelegramForbiddenError:
        await callback.message.answer("❌ Ошибка публикации! Проверьте права администратора у бота.")
    except TelegramBadRequest:
        await callback.message.answer("❌ Ошибка запроса! Неверный юзернейм канала.")
    finally:
        await state.clear()
        if not send: return
    
    if not group_photo:
        await callback.message.edit_text("Пост успешно отправлен!")
    else:
        await callback.message.delete()
        await callback.message.answer("Пост успешно отправлен!")

@router.callback_query(F.data == "delete_post", PostCreation.holding_host)
async def command_delete_post(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    await state.clear()
    await callback.message.delete()
    await callback.answer()