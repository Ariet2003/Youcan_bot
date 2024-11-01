from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from aiogram import F, Router
from app.database import requests as rq
from aiogram.fsm.context import FSMContext
from app.utils import sent_message_add_screen_ids, router
from app.users.user import userStates as st
import app.users.user.userKeyboards as kb
from app import utils
from aiogram.enums import ParseMode



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

# Back to personal account
@router.callback_query(F.data.in_(['to_home_ru', 'to_home_kg']))
async def go_home_handler(callback_query: CallbackQuery, state: FSMContext):
    # Добавление ID сообщения в список
    sent_message_add_screen_ids['bot_messages'].append(callback_query.message.message_id)

    # Вызов функции для отображения личного кабинета
    await user_account(callback_query.message, state)


# Handler for creating a question in ru
@router.callback_query(F.data == 'create_test_ru')
async def create_question(callback_query: CallbackQuery, state: FSMContext):
    sent_message_add_screen_ids['user_messages'].append(callback_query.message.message_id)
    await delete_previous_messages(callback_query.message)
    sent_message = await callback_query.message.answer_photo(photo=utils.pictureForTheTestCreationScreenKG,
                                                             caption='Выберите предмет, по которому вы хотели бы создать вопрос.',
                                                             reply_markup=kb.subjects_ru)
    sent_message_add_screen_ids['bot_messages'].append(sent_message.message_id)


##############################################################
#                    Creating a test in kg                   #
##############################################################

# Handler for creating a question in kg
@router.callback_query(F.data == 'creat_test_kg')
async def create_question(callback_query: CallbackQuery, state: FSMContext):
    sent_message_add_screen_ids['user_messages'].append(callback_query.message.message_id)
    await delete_previous_messages(callback_query.message)
    sent_message = await callback_query.message.answer_photo(
        photo=utils.pictureForTheTestCreationScreenKG,
        caption='Кайсы бөлүктөн суроо тузүүнү каалайсыз?',
        reply_markup=kb.subjects_kg
    )
    sent_message_add_screen_ids['bot_messages'].append(sent_message.message_id)


# Initial handler for entering question text
@router.callback_query(F.data == 'analogy_kg')
async def write_analogy_question_kg(callback_query: CallbackQuery, state: FSMContext):
    sent_message_add_screen_ids['user_messages'].append(callback_query.message.message_id)
    await delete_previous_messages(callback_query.message)

    sent_message = await callback_query.message.answer_photo(
        photo=utils.pictureForTheTestCreationScreenKG,
        caption='Негизги жуптун берилишин жазыңыз.\nҮлгү: _Алма : Жемиш_',
        parse_mode=ParseMode.MARKDOWN
    )
    await state.set_state(st.CreatQuestionsKG.create_question_kg)
    sent_message_add_screen_ids['bot_messages'].append(sent_message.message_id)


# Handler for entering analogy question text
@router.message(st.CreatQuestionsKG.create_question_kg)
async def get_question_text(message: Message, state: FSMContext):
    question_text = message.text
    await state.update_data(question_text=question_text, options={})

    sent_message_add_screen_ids['user_messages'].append(message.message_id)
    await delete_previous_messages(message)

    sent_message = await message.answer(
        f"*Негизги жуп:* {question_text}\n\n"
        f"*A) ............................*\n"
        f"Б) ............................\n"
        f"В) ............................\n"
        f"Г) ............................\n\n"
        "Суроонун жообунун 'A' вариантын жазыңыз:",
        parse_mode=ParseMode.MARKDOWN
    )
    await state.set_state(st.CreatQuestionsKG.create_option_a_kg)
    sent_message_add_screen_ids['bot_messages'].append(sent_message.message_id)


# General handler for options A, B, V, and G
async def get_option(message: Message, state: FSMContext, option_key: str, next_state):
    data = await state.get_data()
    options = data.get('options', {})
    options[option_key] = message.text
    await state.update_data(options=options)

    # Сохранение сообщения пользователя для удаления позже
    sent_message_add_screen_ids['user_messages'].append(message.message_id)
    await delete_previous_messages(message)

    # Определение текста для вывода
    option_text = {
        'A': 'Б',
        'B': 'В',
        'V': 'Г',
        'G': "Суроонун жообунун туура вариантын тандыңыз"
    }

    # Проверка, если вариант "G", чтобы отобразить итоговое сообщение
    if option_key == 'G':
        sent_message = await message.answer(
            f"*Негизги жуп:* {data['question_text']}\n\n"
            f"A) {options.get('A', '............................')}\n"
            f"Б) {options.get('B', '............................')}\n"
            f"В) {options.get('V', '............................')}\n"
            f"Г) {options.get('G', '............................')}\n\n"
            f"{option_text[option_key]}",
            reply_markup=kb.option_buttons_for_creating_an_analogy_kg,
            parse_mode=ParseMode.MARKDOWN
        )
    else:
        # Сообщение для случаев A, B, V, когда требуется ввод следующего варианта
        sent_message = await message.answer(
            f"*Негизги жуп:* {data['question_text']}\n\n"
            f"A) {options.get('A', '............................')}\n"
            f"Б) {options.get('B', '............................')}\n"
            f"В) {options.get('V', '............................')}\n"
            f"Г) {options.get('G', '............................')}\n\n"
            f"Суроонун жообунун '{option_text[option_key]}' вариантын жазыңыз:",
            parse_mode=ParseMode.MARKDOWN
        )
        await state.set_state(next_state)

    # Сохранение отправленного ботом сообщения для удаления позже
    sent_message_add_screen_ids['bot_messages'].append(sent_message.message_id)


# Handlers for entering options A, B, V, and G
@router.message(st.CreatQuestionsKG.create_option_a_kg)
async def get_option_a(message: Message, state: FSMContext):
    if message.text == "/start":
        await user_account(message, state)
        return  # Завершаем обработку
    await get_option(message, state, 'A', st.CreatQuestionsKG.create_option_b_kg)


@router.message(st.CreatQuestionsKG.create_option_b_kg)
async def get_option_b(message: Message, state: FSMContext):
    if message.text == "/start":
        await user_account(message, state)
        return  # Завершаем обработку
    await get_option(message, state, 'B', st.CreatQuestionsKG.create_option_v_kg)


@router.message(st.CreatQuestionsKG.create_option_v_kg)
async def get_option_v(message: Message, state: FSMContext):
    if message.text == "/start":
        await user_account(message, state)
        return  # Завершаем обработку
    await get_option(message, state, 'V', st.CreatQuestionsKG.create_option_g_kg)


@router.message(st.CreatQuestionsKG.create_option_g_kg)
async def get_option_g(message: Message, state: FSMContext):
    if message.text == "/start":
        await user_account(message, state)
        return  # Завершаем обработку
    await get_option(message, state, 'G', None)  # завершает создание опций


# Handler for selecting the correct answer
@router.callback_query(F.data.in_(
    ['kg_creating_an_analogy_a', 'kg_creating_an_analogy_b', 'kg_creating_an_analogy_v', 'kg_creating_an_analogy_g']))
async def get_correct_option(callback_query: CallbackQuery, state: FSMContext):
    option_key = callback_query.data.split('_')[-1].upper()
    sent_message_add_screen_ids['user_messages'].append(callback_query.message.message_id)
    await delete_previous_messages(callback_query.message)

    data = await state.get_data()
    question_text = data['question_text']
    options = data['options']

    sent_message = await callback_query.message.answer(
        f"*Негизги жуп:* {question_text}\n"
        f"{'✅ ' if option_key == 'A' else ''}A: {options['A']}\n"
        f"{'✅ ' if option_key == 'B' else ''}Б: {options['B']}\n"
        f"{'✅ ' if option_key == 'V' else ''}В: {options['V']}\n"
        f"{'✅ ' if option_key == 'G' else ''}Г: {options['G']}\n\n"
        f"Туура вариантты тандыңыз, андан соң текшерүүгө жөнөтүңүз.",
        reply_markup=kb.option_buttons_for_creating_an_analogy_kg,
        parse_mode=ParseMode.MARKDOWN
    )
    sent_message_add_screen_ids['bot_messages'].append(sent_message.message_id)

