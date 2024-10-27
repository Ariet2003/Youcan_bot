from aiogram.fsm.state import StatesGroup, State

# Registration
class RegisterStates(StatesGroup):
    language = State()
    name_kg = State()
    name_ru = State()
    phone_number_kg = State()
    phone_number_ru = State()
