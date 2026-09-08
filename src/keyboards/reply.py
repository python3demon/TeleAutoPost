from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

kb_start_reply = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Создать пост")]
    ],
    resize_keyboard=True
)

skip_or_add_photo = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Пропустить")],
    ],
    resize_keyboard=True
)