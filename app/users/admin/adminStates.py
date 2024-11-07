from aiogram.fsm.state import StatesGroup, State

# Add VIP user
class AddVIPUser(StatesGroup):
    write_tg_id = State()