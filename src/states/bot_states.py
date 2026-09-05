from aiogram.fsm.state import State, StatesGroup

class Registration(StatesGroup):
    waiting_for_channel = State()

class PostCreation(StatesGroup):
    waiting_for_text = State()
    holding_host = State()