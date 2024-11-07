from aiogram.fsm.state import StatesGroup, State

# Add VIP user
class AddVIPUser(StatesGroup):
    write_tg_id = State()

class SendNotification(StatesGroup):
    add_photo = State()
    add_text = State()