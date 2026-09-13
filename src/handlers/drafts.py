from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from config import config_user, save_config
from keyboards.inline import build_list_draft
from aiogram.utils.media_group import MediaGroupBuilder

router = Router()

async def send_drafts(message: Message):
    posts = config_user["drafts"]
    buttons_markup = await build_list_draft(posts)
    await message.answer("Ваши черновики", reply_markup=buttons_markup)

@router.message(F.text == "Мои черновики")
async def get_my_draft(message: Message):
    await send_drafts(message)

@router.callback_query(F.data.startswith("view_"))
async def cat_draft(callback: CallbackQuery):
    num_draft = callback.data.split("_")[-1]
    post_text = config_user["drafts"][num_draft]["post"]
    group_photo = config_user["drafts"][num_draft]["group_photo"]
    await callback.message.delete()
    
    if not group_photo:
        await callback.message.answer(f"{post_text}\n\nВаш черновик*")
    else:
        builder = MediaGroupBuilder(caption=post_text)
        for photo_id in group_photo:
            builder.add_photo(media=photo_id)
        
        await callback.message.answer_media_group(media=builder.build())
    
    draft_edit = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Назад", callback_data="back")],
        [InlineKeyboardButton(text="Удалить", callback_data=f"del_{num_draft}")],
        [InlineKeyboardButton(text="Отправить", callback_data=f"send_{num_draft}")]
    ])

    await callback.message.answer(f"Ваши действия?", reply_markup=draft_edit)
    await callback.answer()

@router.callback_query(F.data == "back")
async def get_back_drafts(callback: CallbackQuery):
    await callback.message.delete()
    await send_drafts(callback.message)
    
    await callback.answer()

@router.callback_query(F.data.startswith("del_"))
async def del_draft(callback: CallbackQuery):
    id_draft = callback.data.split("_")[-1]
    
    if id_draft not in config_user["drafts"]:
        await callback.answer("Уже удален")
        return
    
    del config_user["drafts"][id_draft]
    save_config()
    await callback.answer("Черновик успешно удален!")

@router.callback_query(F.data.startswith("send_"))
async def send_draft(callback: CallbackQuery, bot: Bot):
    num_draft = callback.data.split("_")[-1]
    post = config_user["drafts"].get(num_draft)
    if not post:
        await callback.answer("Нет такого поста!")
        return
    post_text = post["post"]
    group_photo = config_user["drafts"][num_draft]["group_photo"]
    await callback.message.delete()
    
    if not group_photo:
        await bot.send_message(chat_id=config_user["channel_link"], text=post_text) 
    else:
        builder = MediaGroupBuilder(caption=post_text)
        for photo_id in group_photo:
            builder.add_photo(media=photo_id)
        
        await bot.send_media_group(chat_id=config_user["channel_link"], media=builder.build())
    
    del config_user["drafts"][num_draft]
    save_config()
    
    await callback.answer("Пост успешно отправлен!")