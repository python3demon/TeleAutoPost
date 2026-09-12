from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from config import config_user
from keyboards.inline import build_list_draft
from aiogram.utils.media_group import MediaGroupBuilder

router = Router()

@router.message(F.text == "Мои черновики")
async def get_my_draft(message: Message):
    posts = config_user["drafts"]

    buttons_markup = await build_list_draft(posts)
    await message.answer("Ваши черновики", reply_markup=buttons_markup)

@router.callback_query(F.data.startswith("view_"))
async def cat_draft(callback: CallbackQuery):
    num_draft = callback.data.split("_")[-1]
    post_text = config_user["drafts"][num_draft]["post"]
    group_photo = config_user["drafts"][num_draft]["group_photo"]
    
    if not group_photo:
        await callback.message.edit_text(f"{post_text}\n\nВаш черновик*", reply_markup=None)
    else:
        builder = MediaGroupBuilder(caption=post_text)
        for photo_id in group_photo:
            builder.add_photo(media=photo_id)
        
        await callback.message.answer_media_group(media=builder.build())
