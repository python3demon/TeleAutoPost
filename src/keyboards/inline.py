from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

kb_markup_post = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="Отправить", callback_data="send_post"),
        InlineKeyboardButton(text="Удалить", callback_data="delete_post")
    ],
    [InlineKeyboardButton(text="Сохранить", callback_data="save_draft")]
])