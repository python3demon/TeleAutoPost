from aiogram.fsm.state import State, StatesGroup

class Registration(StatesGroup):
    waiting_for_channel = State()

class PostCreation(StatesGroup):
    holding_host = State()

class SaveDraft(StatesGroup):
    name_draft = State()