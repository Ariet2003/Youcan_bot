from aiogram.enums import ParseMode
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from aiogram import F, Router
from app.database import requests as rq
from aiogram.fsm.context import FSMContext
from app.utils import sent_message_add_screen_ids, router
import app.users.user.userKeyboards as kb
from app import utils


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
            if msg_id != message.message_id:
                await message.bot.delete_message(chat_id=message.chat.id, message_id=msg_id)
        except Exception as e:
            print(f"Не удалось удалить сообщение {msg_id}: {e}")
    sent_message_add_screen_ids['bot_messages'].clear()

# User's personal account
async def user_account(message: Message, state: FSMContext):
    sent_message_add_screen_ids['user_messages'].append(message.message_id)

    user_tg_id = str(message.chat.id)
    language = await rq.get_user_language(user_tg_id)
    name = await rq.get_user_name(user_tg_id)

    await delete_previous_messages(message)



    if language == 'ru':
        sent_message = await message.answer_photo(
            photo=utils.pictureOfUsersPersonalAccountRU,
            caption=f'Привет, {name}'
                    f'\n<a href="https://telegra.ph/lpshchzk-10-30">Как бот работает?</a> 👈',
        reply_markup=kb.profile_button_ru,
        parse_mode=ParseMode.HTML)
    else:
        sent_message = await message.answer_photo(
            photo=utils.pictureOfUsersPersonalAccountRU,
            caption=f'Салам, {name}'
                    f'\n<a href="https://telegra.ph/Bizdin-ORTga-dayardanuu-%D2%AFch%D2%AFn-Telegram-bot-kandaj-ishtejt-10-30">Бот кандай иштейт?</a> 👈',
            reply_markup=kb.profile_button_kg,
            parse_mode=ParseMode.HTML)

    sent_message_add_screen_ids['bot_messages'].append(sent_message.message_id)



# Хендлер для обработки команды "/photo"
@router.message(Command("photo"))
async def request_photo_handler(message: Message):
    await message.answer("Пожалуйста, отправьте фото, чтобы я мог получить его ID.")


# Хендлер для обработки фото от пользователя
@router.message(F.photo)
async def photo_handler(message: Message):
    # Берем фотографию в самом большом разрешении и получаем ее ID
    photo_id = message.photo[-1].file_id
    await message.answer(f"ID вашей картинки: {photo_id}")

# Handler for creating a question
@router.callback_query(F.data == 'creat_test_ru')
async def create_question(callback_query: CallbackQuery, state: FSMContext):
    sent_message_add_screen_ids['user_messages'].append(callback_query.message.message_id)
    await delete_previous_messages(callback_query.message)
    sent_message = await callback_query.message.answer(text="Выберите предмет, по которому вы хотели бы создать вопрос.",
                                                       reply_markup=kb.subjects_ru)
    sent_message_add_screen_ids['bot_messages'].append(sent_message.message_id)


@router.callback_query(F.data.in_(['to_home_ru', 'to_home_kg']))
async def go_home_handler(callback_query: CallbackQuery, state: FSMContext):
    # Добавление ID сообщения в список
    sent_message_add_screen_ids['bot_messages'].append(callback_query.message.message_id)

    # Вызов функции для отображения личного кабинета
    await user_account(callback_query.message, state)

