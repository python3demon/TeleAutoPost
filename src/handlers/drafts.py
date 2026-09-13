from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from config import config_user
from keyboards.inline import build_list_draft, draft_edit
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
    
    await callback.message.answer(f"Ваши действия?", reply_markup=draft_edit)
    
    await callback.answer()

@router.callback_query(F.data == "back")
async def get_back_drafts(callback: CallbackQuery):
    await callback.message.delete()
    await send_drafts(callback.message)
    
    await callback.answer()