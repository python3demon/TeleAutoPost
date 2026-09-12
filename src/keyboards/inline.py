from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

kb_markup_post = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Отправить", callback_data="send_post")],
    [InlineKeyboardButton(text="Сохранить", callback_data="save_post")],
    [InlineKeyboardButton(text="Удалить", callback_data="delete_post")]
])

async def build_list_draft(drafts: dict):
    post_buttons = InlineKeyboardBuilder()
    
    for date_key in drafts:
        post_name = drafts[date_key]["post"][:6]
        post_buttons.add(
            InlineKeyboardButton(text=post_name, callback_data=date_key)
        )
    post_buttons.adjust(1)

    return post_buttons.as_markup()