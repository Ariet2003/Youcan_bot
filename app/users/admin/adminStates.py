from aiogram.fsm.state import StatesGroup, State

# Add VIP user
class AddVIPUser(StatesGroup):
    write_tg_id = State()

class SendNotification(StatesGroup):
    add_photo = State()
    add_text = State()

class DeleteUser(StatesGroup):
    write_tg_id = State()

class SearchUser(StatesGroup):
    user_search_input = State()