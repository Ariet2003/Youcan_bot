from aiogram.enums import ParseMode
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram import F, Router
from app.database import requests as rq
from aiogram.fsm.context import FSMContext
import app.keyboards as kb
import app.states as st

router = Router()

# Dictionary for storing message IDs
sent_message_add_screen_ids = {
    'bot_messages': [],
    'user_messages': []
}

# Function to delete previous messages
async def delete_previous_messages(message: Message):
    # Delete all user messages except "/start"
    for msg_id in sent_message_add_screen_ids['user_messages']:
        try:
            if msg_id != message.message_id or message.text != "/start":
                await message.bot.delete_message(chat_id=message.chat.id, message_id=msg_id)
        except Exception as e:
            print(f"Не удалось удалить сообщение {msg_id}: {e}")
    sent_message_add_screen_ids['user_messages'].clear()

    # Delete all bot messages
    for msg_id in sent_message_add_screen_ids['bot_messages']:
        try:
            await message.bot.delete_message(chat_id=message.chat.id, message_id=msg_id)
        except Exception as e:
            print(f"Не удалось удалить сообщение {msg_id}: {e}")
    sent_message_add_screen_ids['bot_messages'].clear()

# Start
@router.message(CommandStart())
async def start(message: Message, state: FSMContext):
    user_tg_id = str(message.from_user.id)

    # Check if user is an administrator
    is_admin = await rq.check_admin(user_tg_id)

    if is_admin:
        await admin_account(message, state)
    else:
        is_user = await rq.check_user(user_tg_id)

        if is_user:
            await user_account(message, state)
        else:
            sent_message = await message.answer(
                text="Выберите язык для подготовки к тесту! Тестке даярданууга тилди тандаңыз!",
                reply_markup=kb.languages
            )
            await state.set_state(st.RegisterStates.language)
            sent_message_add_screen_ids['bot_messages'].append(sent_message.message_id)

@router.callback_query(F.data == 'kg')
async def get_name_kg(callback_query: CallbackQuery, state: FSMContext):
    sent_message_add_screen_ids['user_messages'].append(callback_query.message.message_id)
    await delete_previous_messages(callback_query.message)
    sent_message = await callback_query.message.answer(text="Аты-жөнүңүздү жазыңыз(ФИО)")
    await state.set_state(st.RegisterStates.name_kg)
    sent_message_add_screen_ids['bot_messages'].append(sent_message.message_id)

@router.callback_query(F.data == 'ru')
async def get_name_ru(callback_query: CallbackQuery, state: FSMContext):
    sent_message_add_screen_ids['user_messages'].append(callback_query.message.message_id)
    await delete_previous_messages(callback_query.message)
    sent_message = await callback_query.message.answer(text="Напишите ваше имя и фамилию (ФИО).")
    await state.set_state(st.RegisterStates.name_ru)
    sent_message_add_screen_ids['bot_messages'].append(sent_message.message_id)

@router.message(st.RegisterStates.phone_number_kg)
async def finish_register_kg(message: Message, state: FSMContext):
    sent_message_add_screen_ids['user_messages'].append(message.message_id)
    await delete_previous_messages(message)
    user_tg_id = str(message.from_user.id)
    user_tg_username = str(message.from_user.username)

    state_data = await state.get_data()
    name = state_data.get('name_kg')

    phone_number = message.text
    identifier = user_tg_id

    await rq.set_user(user_tg_id, user_tg_username, name, identifier, "kg", phone_number)

    await user_account(message, state)
    await state.clear()

@router.message(st.RegisterStates.phone_number_ru)
async def finish_register_ru(message: Message, state: FSMContext):
    sent_message_add_screen_ids['user_messages'].append(message.message_id)
    await delete_previous_messages(message)
    user_tg_id = str(message.from_user.id)
    user_tg_username = str(message.from_user.username)

    state_data = await state.get_data()
    name = state_data.get('name_ru')

    phone_number = message.text
    identifier = user_tg_id

    await rq.set_user(user_tg_id, user_tg_username, name, identifier, "ru", phone_number)

    await user_account(message, state)
    await state.clear()

@router.message(st.RegisterStates.name_kg)
async def get_number_kg(message: Message, state: FSMContext):
    sent_message_add_screen_ids['user_messages'].append(message.message_id)
    await delete_previous_messages(message)
    name = message.text
    await state.update_data(name_kg=name)
    sent_message = await message.answer(text="Телефон номериңизди жөнөтүңүз. Үлгү: +996700123456")
    await state.set_state(st.RegisterStates.phone_number_kg)
    sent_message_add_screen_ids['bot_messages'].append(sent_message.message_id)

@router.message(st.RegisterStates.name_ru)
async def get_number_ru(message: Message, state: FSMContext):
    sent_message_add_screen_ids['user_messages'].append(message.message_id)
    await delete_previous_messages(message)
    name = message.text
    await state.update_data(name_ru=name)
    sent_message = await message.answer(text="Отправьте ваш номер телефона. Пример: +996700123456")
    await state.set_state(st.RegisterStates.phone_number_ru)
    sent_message_add_screen_ids['bot_messages'].append(sent_message.message_id)

async def user_account(message: Message, state: FSMContext):
    sent_message_add_screen_ids['user_messages'].append(message.message_id)
    await delete_previous_messages(message)
    sent_message = await message.answer(text="Личный кабинет пользователя")
    sent_message_add_screen_ids['bot_messages'].append(sent_message.message_id)

async def admin_account(message: Message, state: FSMContext):
    sent_message_add_screen_ids['user_messages'].append(message.message_id)
    await delete_previous_messages(message)
    sent_message = await message.answer(text="Личный кабинет админа")
    sent_message_add_screen_ids['bot_messages'].append(sent_message.message_id)
