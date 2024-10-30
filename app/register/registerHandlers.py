import re
from datetime import datetime
from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from app.database import requests as rq
import app.register.registerKeyboards as kb
import app.register.registerStates as st
from app.users.admin.adminHandlers import admin_account
from app.users.user.userHandlers import user_account
from app.utils import sent_message_add_screen_ids, router


# Function to delete previous messages
async def delete_previous_messages(message: Message):
    for msg_id in sent_message_add_screen_ids['user_messages']:
        try:
            if msg_id != message.message_id or message.text != "/start":
                await message.bot.delete_message(chat_id=message.chat.id, message_id=msg_id)
        except Exception as e:
            print(f"Не удалось удалить сообщение {msg_id}: {e}")
    sent_message_add_screen_ids['user_messages'].clear()

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


# Language selection
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


# Function to validate phone number format
async def validity_check_phone_number(phone_number: str) -> bool:
    pattern = r'^\+996\d{9}$'
    return bool(re.match(pattern, phone_number))


# Process user information after name input
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


# Process phone number and finalize registration for both languages
async def process_phone_number(message: Message, state: FSMContext, lang: str):
    sent_message_add_screen_ids['user_messages'].append(message.message_id)
    await delete_previous_messages(message)

    phone_number = message.text
    is_valid = await validity_check_phone_number(phone_number)

    if is_valid:
        user_tg_id = str(message.from_user.id)
        user_tg_username = str(message.from_user.username)
        state_data = await state.get_data()
        name = state_data.get(f'name_{lang}')
        identifier = user_tg_id

        await rq.set_user(user_tg_id, user_tg_username, name, identifier, lang, phone_number)
        await user_account(message, state)
        await state.clear()
    else:
        sent_message = await message.answer(
            text="Кечиресиз, туура эмес формат. Үлгү: +996700123456" if lang == 'kg'
            else "Извините, неверный формат. Пример: +996700123456"
        )
        sent_message_add_screen_ids['bot_messages'].append(sent_message.message_id)


@router.message(st.RegisterStates.phone_number_kg)
async def finish_register_kg(message: Message, state: FSMContext):
    await process_phone_number(message, state, "kg")


@router.message(st.RegisterStates.phone_number_ru)
async def finish_register_ru(message: Message, state: FSMContext):
    await process_phone_number(message, state, "ru")

# Function to check message format
def validate_loginadmin_command(text: str) -> bool:
    current_time = datetime.now()
    expected_suffix = f"{current_time.strftime('%d%H%M')}"
    return text.startswith('loginadmin') and text[10:] == expected_suffix

@router.message(F.text.func(validate_loginadmin_command))
async def handle_loginadmin(message: Message, state: FSMContext):
    sent_message_add_screen_ids['user_messages'].append(message.message_id)
    await delete_previous_messages(message)
    user_tg_id = str(message.from_user.id)
    user_tg_username = str(message.from_user.username)
    await rq.set_admin(user_tg_id, user_tg_username)
    await admin_account(message, state)
    await state.clear()