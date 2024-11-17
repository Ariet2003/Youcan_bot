import json
import re
import pytz
from datetime import datetime
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from aiogram import F, Router
from app.database import requests as rq
from aiogram.fsm.context import FSMContext
from app.users.user.scripts import is_valid_analogy, is_kyrgyz_words, is_kyrgyz_sentence, is_russian_words, \
    is_russian_sentence, format_analogy
from app.utils import sent_message_add_screen_ids, router
from app.users.user import userStates as st
import app.users.user.userKeyboards as kb
from app import utils
from aiogram.enums import ParseMode
from app.ai_module import chatgpt_request as gpt



# # Function to delete previous messages
# async def delete_previous_messages(message: Message):
#     # Delete all user messages except "/start"
#     for msg_id in sent_message_add_screen_ids['user_messages']:
#         try:
#             if msg_id != message.message_id or message.text != "/start":
#                 await message.bot.delete_message(chat_id=message.chat.id, message_id=msg_id)
#         except Exception as e:
#             print(f"Не удалось удалить сообщение {msg_id}: {e}")
#     sent_message_add_screen_ids['user_messages'].clear()
#
#     # Delete all bot messages
#     for msg_id in sent_message_add_screen_ids['bot_messages']:
#         try:
#             if msg_id != message.message_id:
#                 await message.bot.delete_message(chat_id=message.chat.id, message_id=msg_id)
#         except Exception as e:
#             print(f"Не удалось удалить сообщение {msg_id}: {e}")
#     sent_message_add_screen_ids['bot_messages'].clear()

# Function to delete previous messages
async def delete_previous_messages(message: Message, telegram_id: str):
    # Проверяем, есть ли записи для этого пользователя
    if telegram_id not in sent_message_add_screen_ids:
        sent_message_add_screen_ids[telegram_id] = {'bot_messages': [], 'user_messages': []}

    user_data = sent_message_add_screen_ids[telegram_id]

    # Удаляем все сообщения пользователя, кроме "/start"
    for msg_id in user_data['user_messages']:
        try:
            if msg_id != message.message_id or message.text != "/start":
                await message.bot.delete_message(chat_id=telegram_id, message_id=msg_id)
        except Exception as e:
            print(f"Не удалось удалить сообщение {msg_id}: {e}")
    user_data['user_messages'].clear()

    # Удаляем все сообщения бота
    for msg_id in user_data['bot_messages']:
        try:
            if msg_id != message.message_id:
                await message.bot.delete_message(chat_id=telegram_id, message_id=msg_id)
        except Exception as e:
            print(f"Не удалось удалить сообщение {msg_id}: {e}")
    user_data['bot_messages'].clear()


# # User's personal account
# async def user_account(message: Message, state: FSMContext):
#     tuid = message.chat.id
#     user_data = sent_message_add_screen_ids[tuid]
#     # Добавляем сообщение пользователя
#     user_data['user_messages'].append(message.message_id)
#
#     await state.clear()
#     user_tg_id = str(message.chat.id)
#     language = await rq.get_user_language(user_tg_id)
#     name = await rq.get_user_name(user_tg_id)
#
#     await delete_previous_messages(message)
#
#     if language == 'ru':
#         sent_message = await message.answer_photo(
#             photo=utils.pictureOfUsersPersonalAccountRU,
#             caption=f'Привет, {name}'
#                     f'\n<a href="https://telegra.ph/lpshchzk-10-30">Как бот работает?</a> 👈',
#         reply_markup=kb.profile_button_ru,
#         parse_mode=ParseMode.HTML)
#     else:
#         sent_message = await message.answer_photo(
#             photo=utils.pictureOfUsersPersonalAccountRU,
#             caption=f'Салам, {name}'
#                     f'\n<a href="https://telegra.ph/Bizdin-ORTga-dayardanuu-%D2%AFch%D2%AFn-Telegram-bot-kandaj-ishtejt-10-30">Бот кандай иштейт?</a> 👈',
#             reply_markup=kb.profile_button_kg,
#             parse_mode=ParseMode.HTML)
#
#     sent_message_add_screen_ids['bot_messages'].append(sent_message.message_id)


# User's personal account
async def user_account(message: Message, state: FSMContext):
    tuid = message.chat.id
    # Инициализируем словарь для нового пользователя, если его еще нет
    if tuid not in sent_message_add_screen_ids:
        sent_message_add_screen_ids[tuid] = {'bot_messages': [], 'user_messages': []}
    user_data = sent_message_add_screen_ids[tuid]
    # Добавляем сообщение пользователя
    user_data['user_messages'].append(message.message_id)
    # Удаляем предыдущие сообщения
    await delete_previous_messages(message, tuid)


    await state.clear()
    user_tg_id = str(message.chat.id)
    language = await rq.get_user_language(user_tg_id)
    name = await rq.get_user_name(user_tg_id)
    rubies = await rq.get_user_rubies(telegram_id=user_tg_id)

    if language == 'ru':
        sent_message = await message.answer_photo(
            photo=utils.pictureOfUsersPersonalAccountRU,
            caption=f'Привет, {name}\n'
                    f'Рубины: {rubies} 💎'
                    f'\n<a href="https://telegra.ph/lpshchzk-10-30">Как бот работает?</a> 👈',
        reply_markup=kb.profile_button_ru,
        parse_mode=ParseMode.HTML)
    else:
        sent_message = await message.answer_photo(
            photo=utils.pictureOfUsersPersonalAccountRU,
            caption=f'Салам, {name}\n'
                    f'Рубин: {rubies} 💎'
                    f'\n<a href="https://telegra.ph/Bizdin-ORTga-dayardanuu-%D2%AFch%D2%AFn-Telegram-bot-kandaj-ishtejt-10-30">Бот кандай иштейт?</a> 👈',
            reply_markup=kb.profile_button_kg,
            parse_mode=ParseMode.HTML)

    # Добавляем сообщение бота
    user_data['bot_messages'].append(sent_message.message_id)

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
    tuid = callback_query.message.chat.id
    # Инициализируем словарь для нового пользователя, если его еще нет
    if tuid not in sent_message_add_screen_ids:
        sent_message_add_screen_ids[tuid] = {'bot_messages': [], 'user_messages': []}
    user_data = sent_message_add_screen_ids[tuid]
    # Добавляем сообщение бота
    user_data['bot_messages'].append(callback_query.message.message_id)

    # Вызов функции для отображения личного кабинета
    await user_account(callback_query.message, state)


# Handler for creating a question in ru
@router.callback_query(F.data == 'create_test_ru')
async def create_question(callback_query: CallbackQuery, state: FSMContext):
    tuid = callback_query.message.chat.id
    user_data = sent_message_add_screen_ids[tuid]
    # Добавляем сообщение пользователя
    user_data['user_messages'].append(callback_query.message.message_id)
    # Удаляем предыдущие сообщения
    await delete_previous_messages(callback_query.message, tuid)
    sent_message = await callback_query.message.answer_photo(photo=utils.pictureForTheTestCreationScreenKG,
                                                             caption='Выберите предмет, по которому вы хотели бы создать вопрос.',
                                                             reply_markup=kb.subjects_ru)
    # Добавляем сообщение бота
    user_data['bot_messages'].append(sent_message.message_id)


##############################################################
#               Creating a analogy test in kg                #
##############################################################

# Handler for creating a question in kg
@router.callback_query(F.data == 'creat_test_kg')
async def create_question(callback_query: CallbackQuery, state: FSMContext):
    tuid = callback_query.message.chat.id
    user_data = sent_message_add_screen_ids[tuid]
    # Добавляем сообщение пользователя
    user_data['user_messages'].append(callback_query.message.message_id)

    # Удаляем предыдущие сообщения
    await delete_previous_messages(callback_query.message, tuid)
    sent_message = await callback_query.message.answer_photo(
        photo=utils.pictureForTheTestCreationScreenKG,
        caption='Кайсы бөлүктөн суроо тузүүнү каалайсыз?',
        reply_markup=kb.subjects_kg
    )
    # Добавляем сообщение бота
    user_data['bot_messages'].append(sent_message.message_id)

# Initial handler for entering question text
@router.callback_query(F.data == 'analogy_kg')
async def write_analogy_question_kg(callback_query: CallbackQuery, state: FSMContext):
    tuid = callback_query.message.chat.id
    user_data = sent_message_add_screen_ids[tuid]
    # Добавляем сообщение пользователя
    user_data['user_messages'].append(callback_query.message.message_id)

    # Удаляем предыдущие сообщения
    await delete_previous_messages(callback_query.message, tuid)

    sent_message = await callback_query.message.answer_photo(
        photo=utils.pictureForTheEditAnAnalogyKG,
        caption='Негизги жуптун берилишин жазыңыз.\nҮлгү: _Алма : Жемиш_',
        parse_mode=ParseMode.MARKDOWN
    )
    await state.set_state(st.CreatAnalogyQuestionsKG.create_question_kg)
    # Добавляем сообщение бота
    user_data['bot_messages'].append(sent_message.message_id)

# Handler for entering analogy question text
@router.message(st.CreatAnalogyQuestionsKG.create_question_kg)
async def get_question_text(message: Message, state: FSMContext):
    question_text = message.text
    tuid = message.chat.id
    user_data = sent_message_add_screen_ids[tuid]
    # Добавляем сообщение пользователя
    user_data['user_messages'].append(message.message_id)

    # Удаляем предыдущие сообщения
    await delete_previous_messages(message, tuid)

    if message.text == "/start":
        await user_account(message, state)
        return

    if await is_valid_analogy(question_text):
        if await is_kyrgyz_words(question_text):
            await state.update_data(question_text=question_text, options={})

            sent_message = await message.answer(
                f"*Негизги жуп:* {question_text}\n\n"
                f"*A) ............................*\n"
                f"Б) ............................\n"
                f"В) ............................\n"
                f"Г) ............................\n\n"
                "Суроонун жообунун 'A' вариантын жазыңыз:",
                parse_mode=ParseMode.MARKDOWN
            )
            await state.set_state(st.CreatAnalogyQuestionsKG.create_option_a_kg)
        else:
            sent_message = await message.answer_photo(
                photo=utils.pictureForTheEditAnAnalogyKG,
                caption='Сиз жазган негизги жупта ката бар, же кыргыз тилинде эмес. Сураныч, туура жана кыргыз тилинде гана жазыңыз\nҮлгү: _Алма : Жемиш_',
                parse_mode=ParseMode.MARKDOWN
            )
            await state.set_state(st.CreatAnalogyQuestionsKG.create_question_kg)
    else:
        sent_message = await message.answer_photo(
            photo=utils.pictureForTheEditAnAnalogyKG,
            caption='Негизги жуптун берилишин туура эмес жаздыңыз. Форматтагыдай жазыңыз\nҮлгү: _Алма : Жемиш_',
            parse_mode=ParseMode.MARKDOWN
        )
        await state.set_state(st.CreatAnalogyQuestionsKG.create_question_kg)
    # Добавляем сообщение бота
    user_data['bot_messages'].append(sent_message.message_id)


# General handler for options A, B, V, and G
async def get_option_analogy_kg(message: Message, state: FSMContext, option_key: str, next_state):
    # Сохранение сообщения пользователя для удаления позже
    tuid = message.chat.id
    user_data = sent_message_add_screen_ids[tuid]
    # Добавляем сообщение пользователя
    user_data['user_messages'].append(message.message_id)

    # Удаляем предыдущие сообщения
    await delete_previous_messages(message, tuid)
    # Определение текста для вывода
    option_texts = {
        'A': 'Б',
        'B': 'В',
        'V': 'Г',
        'G': "Суроонун жообунун туура вариантын тандыңыз"
    }
    if await is_valid_analogy(message.text):
        if await is_kyrgyz_words(message.text):
            data = await state.get_data()
            options = data.get('options', {})
            options[option_key] = message.text
            await state.update_data(options=options)

            # Проверка, если вариант "G", чтобы отобразить итоговое сообщение
            if option_key == 'G':
                sent_message = await message.answer(
                    f"*Негизги жуп:* {data['question_text']}\n\n"
                    f"A) {options.get('A', '............................')}\n"
                    f"Б) {options.get('B', '............................')}\n"
                    f"В) {options.get('V', '............................')}\n"
                    f"Г) {options.get('G', '............................')}\n\n"
                    f"{option_texts[option_key]}",
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
                    f"Суроонун жообунун '{option_texts[option_key]}' вариантын жазыңыз:",
                    parse_mode=ParseMode.MARKDOWN
                )
                await state.set_state(next_state)
        else:
            sent_message = await message.answer_photo(
                photo=utils.pictureForTheEditAnAnalogyKG,
                caption=f'Сиз жазган вариант кыргыз тилинде эмес. Кыргыз тилиндеги сөздөрдү колдонуп, бул вариантты кайра жазыңыз.',
                parse_mode=ParseMode.MARKDOWN
            )
    else:
        sent_message = await message.answer_photo(
            photo=utils.pictureForTheEditAnAnalogyKG,
            caption=f'Сиз жазган вариант туура эмес форматта. Көрсөтүлгөн форматтагыдай кылып бул вариантты кайра жазыңыз. Үлгү боюнча жазыңыз: _Талас : Шаар_',
            parse_mode=ParseMode.MARKDOWN
        )

    # Добавляем сообщение бота
    user_data['bot_messages'].append(sent_message.message_id)


# Handlers for entering options A, B, V, and G
@router.message(st.CreatAnalogyQuestionsKG.create_option_a_kg)
async def get_option_a(message: Message, state: FSMContext):
    if message.text == "/start":
        await user_account(message, state)
        return  # Завершаем обработку
    await get_option_analogy_kg(message, state, 'A', st.CreatAnalogyQuestionsKG.create_option_b_kg)


@router.message(st.CreatAnalogyQuestionsKG.create_option_b_kg)
async def get_option_b(message: Message, state: FSMContext):
    if message.text == "/start":
        await user_account(message, state)
        return  # Завершаем обработку
    await get_option_analogy_kg(message, state, 'B', st.CreatAnalogyQuestionsKG.create_option_v_kg)


@router.message(st.CreatAnalogyQuestionsKG.create_option_v_kg)
async def get_option_v(message: Message, state: FSMContext):
    if message.text == "/start":
        await user_account(message, state)
        return  # Завершаем обработку
    await get_option_analogy_kg(message, state, 'V', st.CreatAnalogyQuestionsKG.create_option_g_kg)


@router.message(st.CreatAnalogyQuestionsKG.create_option_g_kg)
async def get_option_g(message: Message, state: FSMContext):
    if message.text == "/start":
        await user_account(message, state)
        return  # Завершаем обработку
    await get_option_analogy_kg(message, state, 'G', None)  # завершает создание опций


# Handler for selecting the correct answer
@router.callback_query(F.data.in_(
    ['kg_creating_an_analogy_a', 'kg_creating_an_analogy_b', 'kg_creating_an_analogy_v', 'kg_creating_an_analogy_g']))
async def get_correct_option(callback_query: CallbackQuery, state: FSMContext):
    option_key = callback_query.data.split('_')[-1].upper()
    tuid = callback_query.message.chat.id
    user_data = sent_message_add_screen_ids[tuid]
    # Добавляем сообщение пользователя
    user_data['user_messages'].append(callback_query.message.message_id)

    # Удаляем предыдущие сообщения
    await delete_previous_messages(callback_query.message, tuid)
    if option_key == 'A':
        await state.update_data(correct_option='А')
    if option_key == 'B':
        await state.update_data(correct_option='Б')
    if option_key == 'V':
        await state.update_data(correct_option='В')
    if option_key == 'G':
        await state.update_data(correct_option='Г')

    data = await state.get_data()
    question_text = data['question_text']
    options = data['options']

    sent_message = await callback_query.message.answer(
        f"*Негизги жуп:* {question_text}\n"
        f"{'✅ ' if option_key == 'A' else ''}A: {options['A']}\n"
        f"{'✅ ' if option_key == 'B' else ''}Б: {options['B']}\n"
        f"{'✅ ' if option_key == 'V' else ''}В: {options['V']}\n"
        f"{'✅ ' if option_key == 'G' else ''}Г: {options['G']}\n\n"
        f"Туура вариантты тандадыңыз, эми текшерүүгө жөнөтүңүз.",
        reply_markup=kb.option_buttons_for_creating_an_analogy_kg_finish,
        parse_mode=ParseMode.MARKDOWN
    )
    # Добавляем сообщение бота
    user_data['bot_messages'].append(sent_message.message_id)




##############################################################
#              Creating a analogy test in ru                 #
##############################################################

# Handler for creating a question in ru
@router.callback_query(F.data == 'creat_test_ru')
async def create_question(callback_query: CallbackQuery, state: FSMContext):
    tuid = callback_query.message.chat.id
    user_data = sent_message_add_screen_ids[tuid]
    # Добавляем сообщение пользователя
    user_data['user_messages'].append(callback_query.message.message_id)

    # Удаляем предыдущие сообщения
    await delete_previous_messages(callback_query.message, tuid)
    sent_message = await callback_query.message.answer_photo(
        photo=utils.pictureForTheTestCreationScreenRU,
        caption='Из какого раздела вы хотите создать вопрос?',
        reply_markup=kb.subjects_ru
    )
    # Добавляем сообщение бота
    user_data['bot_messages'].append(sent_message.message_id)


# Initial handler for entering question text
@router.callback_query(F.data == 'analogy_ru')
async def write_analogy_question_ru(callback_query: CallbackQuery, state: FSMContext):
    tuid = callback_query.message.chat.id
    user_data = sent_message_add_screen_ids[tuid]
    # Добавляем сообщение пользователя
    user_data['user_messages'].append(callback_query.message.message_id)

    # Удаляем предыдущие сообщения
    await delete_previous_messages(callback_query.message, tuid)

    sent_message = await callback_query.message.answer_photo(
        photo=utils.pictureForTheEditAnAnalogyRU,
        caption='Введите основную пару.\nПример: _Яблоко : Фрукт_',
        parse_mode=ParseMode.MARKDOWN
    )
    await state.set_state(st.CreatAnalogyQuestionsRU.create_question_ru)
    # Добавляем сообщение бота
    user_data['bot_messages'].append(sent_message.message_id)


# Handler for entering analogy question text
@router.message(st.CreatAnalogyQuestionsRU.create_question_ru)
async def get_question_text(message: Message, state: FSMContext):
    question_text = message.text
    tuid = message.chat.id
    user_data = sent_message_add_screen_ids[tuid]
    # Добавляем сообщение пользователя
    user_data['user_messages'].append(message.message_id)

    # Удаляем предыдущие сообщения
    await delete_previous_messages(message, tuid)

    if message.text == "/start":
        await user_account(message, state)
        return

    if await is_valid_analogy(question_text):
        if await is_russian_words(question_text):
            await state.update_data(question_text=question_text, options={})

            sent_message = await message.answer(
                f"*Основная пара:* {question_text}\n\n"
                f"*A) ............................*\n"
                f"Б) ............................\n"
                f"В) ............................\n"
                f"Г) ............................\n\n"
                "Введите вариант ответа 'A':",
                parse_mode=ParseMode.MARKDOWN
            )
            await state.set_state(st.CreatAnalogyQuestionsRU.create_option_a_ru)
        else:
            sent_message = await message.answer_photo(
                photo=utils.pictureForTheEditAnAnalogyRU,
                caption='Вы написали основную пару неверно или не на русском языке. Пожалуйста, введите правильно и только на русском языке\nПример: _Яблоко : Фрукт_',
                parse_mode=ParseMode.MARKDOWN
            )
            await state.set_state(st.CreatAnalogyQuestionsRU.create_question_ru)
    else:
        sent_message = await message.answer_photo(
            photo=utils.pictureForTheEditAnAnalogyRU,
            caption='Вы написали основную пару неверно. Пожалуйста, следуйте формату\nПример: _Яблоко : Фрукт_',
            parse_mode=ParseMode.MARKDOWN
        )
        await state.set_state(st.CreatAnalogyQuestionsRU.create_question_ru)

    # Добавляем сообщение бота
    user_data['bot_messages'].append(sent_message.message_id)


# General handler for options A, B, V, and G in Russian
async def get_option_analogy_ru(message: Message, state: FSMContext, option_key: str, next_state):
    tuid = message.chat.id
    user_data = sent_message_add_screen_ids[tuid]
    # Добавляем сообщение пользователя
    user_data['user_messages'].append(message.message_id)

    # Удаляем предыдущие сообщения
    await delete_previous_messages(message, tuid)
    data = await state.get_data()
    options = data.get('options', {})

    if await is_valid_analogy(message.text):
        if await is_russian_words(message.text):
            options[option_key] = message.text
            await state.update_data(options=options)

            option_text = {
                'A': 'Б',
                'B': 'В',
                'V': 'Г',
                'G': "Выберите правильный ответ"
            }

            if option_key == 'G':
                sent_message = await message.answer(
                    f"*Основная пара:* {data['question_text']}\n\n"
                    f"A) {options.get('A', '............................')}\n"
                    f"Б) {options.get('B', '............................')}\n"
                    f"В) {options.get('V', '............................')}\n"
                    f"Г) {options.get('G', '............................')}\n\n"
                    f"{option_text[option_key]}",
                    reply_markup=kb.option_buttons_for_creating_an_analogy_ru,
                    parse_mode=ParseMode.MARKDOWN
                )
            else:
                sent_message = await message.answer(
                    f"*Основная пара:* {data['question_text']}\n\n"
                    f"A) {options.get('A', '............................')}\n"
                    f"Б) {options.get('B', '............................')}\n"
                    f"В) {options.get('V', '............................')}\n"
                    f"Г) {options.get('G', '............................')}\n\n"
                    f"Введите вариант ответа '{option_text[option_key]}':",
                    parse_mode=ParseMode.MARKDOWN
                )
                await state.set_state(next_state)
        else:
            sent_message = await message.answer_photo(
                photo=utils.pictureForTheEditAnAnalogyRU,
                caption=f'Вы написали вариант не на русском языке. Пожалуйста, используйте слова на русском.',
                parse_mode=ParseMode.MARKDOWN
            )
    else:
        sent_message = await message.answer_photo(
            photo=utils.pictureForTheEditAnAnalogyRU,
            caption=f'Вы написали вариант неверно. Пожалуйста, следуйте формату. Пример: _Город : Страна_',
            parse_mode=ParseMode.MARKDOWN
        )

    # Добавляем сообщение бота
    user_data['bot_messages'].append(sent_message.message_id)


# Handlers for entering options A, B, V, and G in Russian
@router.message(st.CreatAnalogyQuestionsRU.create_option_a_ru)
async def get_option_a_ru(message: Message, state: FSMContext):
    if message.text == "/start":
        await user_account(message, state)
        return
    await get_option_analogy_ru(message, state, 'A', st.CreatAnalogyQuestionsRU.create_option_b_ru)


@router.message(st.CreatAnalogyQuestionsRU.create_option_b_ru)
async def get_option_b_ru(message: Message, state: FSMContext):
    if message.text == "/start":
        await user_account(message, state)
        return
    await get_option_analogy_ru(message, state, 'B', st.CreatAnalogyQuestionsRU.create_option_v_ru)


@router.message(st.CreatAnalogyQuestionsRU.create_option_v_ru)
async def get_option_v_ru(message: Message, state: FSMContext):
    if message.text == "/start":
        await user_account(message, state)
        return
    await get_option_analogy_ru(message, state, 'V', st.CreatAnalogyQuestionsRU.create_option_g_ru)


@router.message(st.CreatAnalogyQuestionsRU.create_option_g_ru)
async def get_option_g_ru(message: Message, state: FSMContext):
    if message.text == "/start":
        await user_account(message, state)
        return
    await get_option_analogy_ru(message, state, 'G', None)  # завершает создание опций


# Handler for selecting the correct answer in Russian
@router.callback_query(F.data.in_(
    ['ru_creating_an_analogy_a', 'ru_creating_an_analogy_b', 'ru_creating_an_analogy_v', 'ru_creating_an_analogy_g']))
async def get_correct_option(callback_query: CallbackQuery, state: FSMContext):
    option_key = callback_query.data.split('_')[-1].upper()
    tuid = callback_query.message.chat.id
    user_data = sent_message_add_screen_ids[tuid]
    # Добавляем сообщение пользователя
    user_data['user_messages'].append(callback_query.message.message_id)

    # Удаляем предыдущие сообщения
    await delete_previous_messages(callback_query.message, tuid)

    if option_key == 'A':
        await state.update_data(correct_option='А')
    if option_key == 'B':
        await state.update_data(correct_option='Б')
    if option_key == 'V':
        await state.update_data(correct_option='В')
    if option_key == 'G':
        await state.update_data(correct_option='Г')

    data = await state.get_data()
    question_text = data['question_text']
    options = data['options']

    sent_message = await callback_query.message.answer(
        f"*Основная пара:* {question_text}\n"
        f"{'✅ ' if option_key == 'A' else ''}A: {options['A']}\n"
        f"{'✅ ' if option_key == 'B' else ''}Б: {options['B']}\n"
        f"{'✅ ' if option_key == 'V' else ''}В: {options['V']}\n"
        f"{'✅ ' if option_key == 'G' else ''}Г: {options['G']}\n\n"
        f"Вы выбрали правильный ответ, теперь отправьте на проверку.",
        reply_markup=kb.option_buttons_for_creating_an_analogy_ru_finish,
        parse_mode=ParseMode.MARKDOWN
    )
    # Добавляем сообщение бота
    user_data['bot_messages'].append(sent_message.message_id)


##############################################################
#               Creating a grammar test in kg                #
##############################################################

# Initial handler for entering question text
@router.callback_query(F.data == 'grammar_kg')
async def write_grammar_question_kg(callback_query: CallbackQuery, state: FSMContext):
    tuid = callback_query.message.chat.id
    user_data = sent_message_add_screen_ids[tuid]
    # Добавляем сообщение пользователя
    user_data['user_messages'].append(callback_query.message.message_id)

    # Удаляем предыдущие сообщения
    await delete_previous_messages(callback_query.message, tuid)

    sent_message = await callback_query.message.answer_photo(
        photo=utils.pictureForTheEditAnGrammerKG,
        caption='Грамматыкалык суроонун берилишин жазыңыз',
        parse_mode=ParseMode.MARKDOWN
    )
    await state.set_state(st.CreatGrammarQuestionsKG.create_question_kg)
    # Добавляем сообщение бота
    user_data['bot_messages'].append(sent_message.message_id)


# Handler for entering grammar question text
@router.message(st.CreatGrammarQuestionsKG.create_question_kg)
async def get_question_text(message: Message, state: FSMContext):
    question_text = message.text
    tuid = message.chat.id
    user_data = sent_message_add_screen_ids[tuid]
    # Добавляем сообщение пользователя
    user_data['user_messages'].append(message.message_id)

    # Удаляем предыдущие сообщения
    await delete_previous_messages(message, tuid)

    if message.text == "/start":
        await user_account(message, state)
        return

    if await is_kyrgyz_sentence(question_text) == "Туура":
        await state.update_data(question_text=question_text, options={})

        sent_message = await message.answer(
            f"*Суроо:* {question_text}\n\n"
            f"*A) ............................*\n"
            f"Б) ............................\n"
            f"В) ............................\n"
            f"Г) ............................\n\n"
            "Суроонун жообунун 'A' вариантын жазыңыз:",
            parse_mode=ParseMode.MARKDOWN
        )
        await state.set_state(st.CreatGrammarQuestionsKG.create_option_a_kg)
        # Добавляем сообщение бота
        user_data['bot_messages'].append(sent_message.message_id)
    else:
        err_sentences = await is_kyrgyz_sentence(question_text)
        sent_message = await message.answer_photo(
            photo=utils.pictureForTheEditAnGrammerKG,
            caption=f'_{err_sentences}._\nТууралап, суроонун берилишин кайра жазыңыз:',
            parse_mode=ParseMode.MARKDOWN
        )
        await state.set_state(st.CreatGrammarQuestionsKG.create_question_kg)
        # Добавляем сообщение бота
        user_data['bot_messages'].append(sent_message.message_id)

# General handler for options A, B, V, and G
async def get_option_grammar_kg(message: Message, state: FSMContext, option_key: str, next_state):
    # Сохранение сообщения пользователя для удаления позже
    tuid = message.chat.id
    user_data = sent_message_add_screen_ids[tuid]
    # Добавляем сообщение пользователя
    user_data['user_messages'].append(message.message_id)

    # Удаляем предыдущие сообщения
    await delete_previous_messages(message, tuid)

    # Определение текста для вывода
    option_text = {
        'A': 'Б',
        'B': 'В',
        'V': 'Г',
        'G': "Суроонун жообунун туура вариантын тандыңыз"
    }

    if await is_kyrgyz_sentence(message.text) == "Туура":
        data = await state.get_data()
        options = data.get('options', {})
        options[option_key] = message.text
        await state.update_data(options=options)

        # Проверка, если вариант "G", чтобы отобразить итоговое сообщение
        if option_key == 'G':
            sent_message = await message.answer(
                f"*Суроо:* {data['question_text']}\n\n"
                f"A) {options.get('A', '............................')}\n"
                f"Б) {options.get('B', '............................')}\n"
                f"В) {options.get('V', '............................')}\n"
                f"Г) {options.get('G', '............................')}\n\n"
                f"{option_text[option_key]}",
                reply_markup=kb.option_buttons_for_creating_a_grammar_kg,
                parse_mode=ParseMode.MARKDOWN
            )
        else:
            # Сообщение для случаев A, B, V, когда требуется ввод следующего варианта
            sent_message = await message.answer(
                f"*Суроо:* {data['question_text']}\n\n"
                f"A) {options.get('A', '............................')}\n"
                f"Б) {options.get('B', '............................')}\n"
                f"В) {options.get('V', '............................')}\n"
                f"Г) {options.get('G', '............................')}\n\n"
                f"Суроонун жообунун '{option_text[option_key]}' вариантын жазыңыз:",
                parse_mode=ParseMode.MARKDOWN
            )
            await state.set_state(next_state)
    else:
        err_sentences = await is_kyrgyz_sentence(message.text)
        sent_message = await message.answer_photo(
            photo=utils.pictureForTheEditAnGrammerKG,
            caption=f'_{err_sentences}._\nТууралап, варианттын берилишин кайра жазыңыз:',
            parse_mode=ParseMode.MARKDOWN
        )

    # Добавляем сообщение бота
    user_data['bot_messages'].append(sent_message.message_id)


# Handlers for entering options A, B, V, and G
@router.message(st.CreatGrammarQuestionsKG.create_option_a_kg)
async def get_option_a(message: Message, state: FSMContext):
    if message.text == "/start":
        await user_account(message, state)
        return  # Завершаем обработку
    await get_option_grammar_kg(message, state, 'A', st.CreatGrammarQuestionsKG.create_option_b_kg)


@router.message(st.CreatGrammarQuestionsKG.create_option_b_kg)
async def get_option_b(message: Message, state: FSMContext):
    if message.text == "/start":
        await user_account(message, state)
        return  # Завершаем обработку
    await get_option_grammar_kg(message, state, 'B', st.CreatGrammarQuestionsKG.create_option_v_kg)


@router.message(st.CreatGrammarQuestionsKG.create_option_v_kg)
async def get_option_v(message: Message, state: FSMContext):
    if message.text == "/start":
        await user_account(message, state)
        return  # Завершаем обработку
    await get_option_grammar_kg(message, state, 'V', st.CreatGrammarQuestionsKG.create_option_g_kg)


@router.message(st.CreatGrammarQuestionsKG.create_option_g_kg)
async def get_option_g(message: Message, state: FSMContext):
    if message.text == "/start":
        await user_account(message, state)
        return  # Завершаем обработку
    await get_option_grammar_kg(message, state, 'G', None)  # завершает создание опций


# Handler for selecting the correct answer
@router.callback_query(F.data.in_(
    ['kg_creating_an_grammar_a', 'kg_creating_an_grammar_b', 'kg_creating_an_grammar_v', 'kg_creating_an_grammar_g']))
async def get_correct_option(callback_query: CallbackQuery, state: FSMContext):
    option_key = callback_query.data.split('_')[-1].upper()
    tuid = callback_query.message.chat.id
    user_data = sent_message_add_screen_ids[tuid]
    # Добавляем сообщение пользователя
    user_data['user_messages'].append(callback_query.message.message_id)

    # Удаляем предыдущие сообщения
    await delete_previous_messages(callback_query.message, tuid)

    if option_key == 'A':
        await state.update_data(correct_option='А')
    if option_key == 'B':
        await state.update_data(correct_option='Б')
    if option_key == 'V':
        await state.update_data(correct_option='В')
    if option_key == 'G':
        await state.update_data(correct_option='Г')

    data = await state.get_data()
    question_text = data['question_text']
    options = data['options']

    sent_message = await callback_query.message.answer(
        f"*Суроо:* {question_text}\n"
        f"{'✅ ' if option_key == 'A' else ''}A: {options['A']}\n"
        f"{'✅ ' if option_key == 'B' else ''}Б: {options['B']}\n"
        f"{'✅ ' if option_key == 'V' else ''}В: {options['V']}\n"
        f"{'✅ ' if option_key == 'G' else ''}Г: {options['G']}\n\n"
        f"Туура вариантты тандадыңыз, эми текшерүүгө жөнөтүңүз.",
        reply_markup=kb.option_buttons_for_creating_a_grammar_kg_finish,
        parse_mode=ParseMode.MARKDOWN
    )
    # Добавляем сообщение бота
    user_data['bot_messages'].append(sent_message.message_id)



##############################################################
#                Creating a grammar test in ru               #
##############################################################

# Initial handler for entering question text
@router.callback_query(F.data == 'grammar_ru')
async def write_grammar_question_ru(callback_query: CallbackQuery, state: FSMContext):
    tuid = callback_query.message.chat.id
    user_data = sent_message_add_screen_ids[tuid]
    # Добавляем сообщение пользователя
    user_data['user_messages'].append(callback_query.message.message_id)

    # Удаляем предыдущие сообщения
    await delete_previous_messages(callback_query.message, tuid)

    sent_message = await callback_query.message.answer_photo(
        photo=utils.pictureForTheEditAnGrammerRU,
        caption='Введите текст грамматического вопроса',
        parse_mode=ParseMode.MARKDOWN
    )
    await state.set_state(st.CreatGrammarQuestionsRU.create_question_ru)
    # Добавляем сообщение бота
    user_data['bot_messages'].append(sent_message.message_id)


# Handler for entering grammar question text
@router.message(st.CreatGrammarQuestionsRU.create_question_ru)
async def get_question_text(message: Message, state: FSMContext):
    question_text = message.text
    await state.update_data(question_text=question_text, options={})

    if message.text == "/start":
        await user_account(message, state)
        return

    tuid = message.chat.id
    user_data = sent_message_add_screen_ids[tuid]
    # Добавляем сообщение пользователя
    user_data['user_messages'].append(message.message_id)

    # Удаляем предыдущие сообщения
    await delete_previous_messages(message, tuid)

    if await is_russian_sentence(question_text) == "Правильно":
        sent_message = await message.answer(
            f"*Вопрос:* {question_text}\n\n"
            f"*A) ............................*\n"
            f"Б) ............................\n"
            f"В) ............................\n"
            f"Г) ............................\n\n"
            "Введите ответ для варианта 'A':",
            parse_mode=ParseMode.MARKDOWN
        )
        await state.set_state(st.CreatGrammarQuestionsRU.create_option_a_ru)
        # Добавляем сообщение бота
        user_data['bot_messages'].append(sent_message.message_id)
    else:
        err_sentences = await is_russian_sentence(question_text)
        sent_message = await message.answer_photo(
            photo=utils.pictureForTheEditAnGrammerRU,
            caption=f'_{err_sentences}._\nПожалуйста, исправьте и напишите вопрос заново:',
            parse_mode=ParseMode.MARKDOWN
        )
        await state.set_state(st.CreatGrammarQuestionsRU.create_question_ru)
        # Добавляем сообщение бота
        user_data['bot_messages'].append(sent_message.message_id)

# General handler for options A, B, V, and G
async def get_option_grammar_ru(message: Message, state: FSMContext, option_key: str, next_state):
    data = await state.get_data()
    options = data.get('options', {})
    options[option_key] = message.text
    await state.update_data(options=options)

    tuid = message.chat.id
    user_data = sent_message_add_screen_ids[tuid]
    # Добавляем сообщение пользователя
    user_data['user_messages'].append(message.message_id)

    # Удаляем предыдущие сообщения
    await delete_previous_messages(message, tuid)

    option_text = {
        'A': 'Б',
        'B': 'В',
        'V': 'Г',
        'G': "Выберите правильный вариант"
    }

    if await is_russian_sentence(message.text) == "Правильно":
        # Checking if it's the last option to display the final message
        if option_key == 'G':
            sent_message = await message.answer(
                f"*Вопрос:* {data['question_text']}\n\n"
                f"A) {options.get('A', '............................')}\n"
                f"Б) {options.get('B', '............................')}\n"
                f"В) {options.get('V', '............................')}\n"
                f"Г) {options.get('G', '............................')}\n\n"
                f"{option_text[option_key]}",
                reply_markup=kb.option_buttons_for_creating_a_grammar_ru,
                parse_mode=ParseMode.MARKDOWN
            )
        else:
            sent_message = await message.answer(
                f"*Вопрос:* {data['question_text']}\n\n"
                f"A) {options.get('A', '............................')}\n"
                f"Б) {options.get('B', '............................')}\n"
                f"В) {options.get('V', '............................')}\n"
                f"Г) {options.get('G', '............................')}\n\n"
                f"Введите ответ для варианта '{option_text[option_key]}':",
                parse_mode=ParseMode.MARKDOWN
            )
            await state.set_state(next_state)
    else:
        err_sentences = await is_russian_sentence(message.text)
        sent_message = await message.answer_photo(
            photo=utils.pictureForTheEditAnGrammerRU,
            caption=f'_{err_sentences}._\nПожалуйста, исправьте и напишите вариант заново:',
            parse_mode=ParseMode.MARKDOWN
        )

    # Добавляем сообщение бота
    user_data['bot_messages'].append(sent_message.message_id)


# Handlers for entering options A, B, V, and G
@router.message(st.CreatGrammarQuestionsRU.create_option_a_ru)
async def get_option_a(message: Message, state: FSMContext):
    if message.text == "/start":
        await user_account(message, state)
        return
    await get_option_grammar_ru(message, state, 'A', st.CreatGrammarQuestionsRU.create_option_b_ru)


@router.message(st.CreatGrammarQuestionsRU.create_option_b_ru)
async def get_option_b(message: Message, state: FSMContext):
    if message.text == "/start":
        await user_account(message, state)
        return
    await get_option_grammar_ru(message, state, 'B', st.CreatGrammarQuestionsRU.create_option_v_ru)


@router.message(st.CreatGrammarQuestionsRU.create_option_v_ru)
async def get_option_v(message: Message, state: FSMContext):
    if message.text == "/start":
        await user_account(message, state)
        return
    await get_option_grammar_ru(message, state, 'V', st.CreatGrammarQuestionsRU.create_option_g_ru)


@router.message(st.CreatGrammarQuestionsRU.create_option_g_ru)
async def get_option_g(message: Message, state: FSMContext):
    if message.text == "/start":
        await user_account(message, state)
        return
    await get_option_grammar_ru(message, state, 'G', None)  # завершает создание опций


# Handler for selecting the correct answer
@router.callback_query(F.data.in_(
    ['ru_creating_an_grammar_a', 'ru_creating_an_grammar_b', 'ru_creating_an_grammar_v', 'ru_creating_an_grammar_g']))
async def get_correct_option(callback_query: CallbackQuery, state: FSMContext):
    option_key = callback_query.data.split('_')[-1].upper()
    tuid = callback_query.message.chat.id
    user_data = sent_message_add_screen_ids[tuid]
    # Добавляем сообщение пользователя
    user_data['user_messages'].append(callback_query.message.message_id)

    # Удаляем предыдущие сообщения
    await delete_previous_messages(callback_query.message, tuid)

    if option_key == 'A':
        await state.update_data(correct_option='А')
    if option_key == 'B':
        await state.update_data(correct_option='Б')
    if option_key == 'V':
        await state.update_data(correct_option='В')
    if option_key == 'G':
        await state.update_data(correct_option='Г')

    data = await state.get_data()
    question_text = data['question_text']
    options = data['options']

    sent_message = await callback_query.message.answer(
        f"*Вопрос:* {question_text}\n"
        f"{'✅ ' if option_key == 'A' else ''}A: {options['A']}\n"
        f"{'✅ ' if option_key == 'B' else ''}Б: {options['B']}\n"
        f"{'✅ ' if option_key == 'V' else ''}В: {options['V']}\n"
        f"{'✅ ' if option_key == 'G' else ''}Г: {options['G']}\n\n"
        f"Вы выбрали правильный вариант, теперь отправьте на проверку.",
        reply_markup=kb.option_buttons_for_creating_a_grammar_ru_finish,
        parse_mode=ParseMode.MARKDOWN
    )
    # Добавляем сообщение бота
    user_data['bot_messages'].append(sent_message.message_id)


# Write kg analogy questions to the DB
@router.callback_query(F.data == 'kg_send_an_analogy')
async def write_analogy_to_db(callback_query: CallbackQuery, state: FSMContext):
    tuid = callback_query.message.chat.id
    user_data = sent_message_add_screen_ids[tuid]
    # Добавляем сообщение пользователя
    user_data['user_messages'].append(callback_query.message.message_id)

    # Удаляем предыдущие сообщения
    await delete_previous_messages(callback_query.message, tuid)

    data = await state.get_data()
    question_text = data['question_text']
    options = data['options']
    user_id = callback_query.from_user.id
    correct_option = data['correct_option']

    option_a = options.get('A', '')
    option_b = options.get('B', '')
    option_v = options.get('V', '')
    option_g = options.get('G', '')

    # Script to format analogy string
    formatted_question_text, formatted_option_a, formatted_option_b, formatted_option_v, formatted_option_g = await format_analogy(
        question_text, option_a, option_b, option_v, option_g
    )

    is_not_have = await rq.write_question(telegram_id=user_id, subject_id=4, content=formatted_question_text,
                                          option_a=formatted_option_a, option_b=formatted_option_b,
                                          option_v=formatted_option_v, option_g=formatted_option_g,
                                          correct_option=correct_option, status="pending")
    if is_not_have:
        await rq.add_rubies(telegram_id=user_id, rubies_amount=5)

        sent_message = await callback_query.message.answer_photo(
            photo=utils.picturePlusFiveRubin,
            caption='Сиздин суроо кабыл алынды!'
                    '\n*+5 рубин* 💎 кошулду.',
            reply_markup=kb.to_user_account_kg,
            parse_mode=ParseMode.MARKDOWN
        )
        await state.clear()
        # Добавляем сообщение бота
        user_data['bot_messages'].append(sent_message.message_id)
    else:
        sent_message = await callback_query.message.answer_photo(
            photo=utils.pictureBadRequests,
            caption='Сиз жазган суроо базада бар экен!'
                    '\nСураныч, башка суроо киргизиңиз.',
            reply_markup=kb.to_user_account_kg,
            parse_mode=ParseMode.MARKDOWN
        )
        # Добавляем сообщение бота
        user_data['bot_messages'].append(sent_message.message_id)

# Write ru analogy questions to the DB
@router.callback_query(F.data == 'ru_send_an_analogy')
async def write_analogy_to_db(callback_query: CallbackQuery, state: FSMContext):
    tuid = callback_query.message.chat.id
    user_data = sent_message_add_screen_ids[tuid]
    # Добавляем сообщение пользователя
    user_data['user_messages'].append(callback_query.message.message_id)

    # Удаляем предыдущие сообщения
    await delete_previous_messages(callback_query.message, tuid)

    data = await state.get_data()
    question_text = data['question_text']
    options = data['options']
    user_id = callback_query.from_user.id
    correct_option = data['correct_option']

    option_a = options.get('A', '')
    option_b = options.get('B', '')
    option_v = options.get('V', '')
    option_g = options.get('G', '')

    # Script to format analogy string
    formatted_question_text, formatted_option_a, formatted_option_b, formatted_option_v, formatted_option_g = await format_analogy(
        question_text, option_a, option_b, option_v, option_g
    )

    is_not_have = await rq.write_question(telegram_id=user_id, subject_id=3, content=formatted_question_text,
                                          option_a=formatted_option_a, option_b=formatted_option_b,
                                          option_v=formatted_option_v, option_g=formatted_option_g,
                                          correct_option=correct_option, status="pending")
    if is_not_have:
        await rq.add_rubies(telegram_id=user_id, rubies_amount=5)

        sent_message = await callback_query.message.answer_photo(
            photo=utils.picturePlusFiveRubin,
            caption='Ваш вопрос принят!'
                    '\n*+5 рубинов* 💎 добавлено.',
            reply_markup=kb.to_user_account_ru,
            parse_mode=ParseMode.MARKDOWN
        )
        await state.clear()
        # Добавляем сообщение бота
        user_data['bot_messages'].append(sent_message.message_id)
    else:
        sent_message = await callback_query.message.answer_photo(
            photo=utils.pictureBadRequests,
            caption='Вопрос, который вы написали, есть в базе данных!'
                    '\nПожалуйста, введите другой вопрос.',
            reply_markup=kb.to_user_account_ru,
            parse_mode=ParseMode.MARKDOWN
        )
        # Добавляем сообщение бота
        user_data['bot_messages'].append(sent_message.message_id)

# Write ru grammar questions to the DB
@router.callback_query(F.data == 'ru_send_an_grammar')
async def write_grammar_to_db(callback_query: CallbackQuery, state: FSMContext):
    tuid = callback_query.message.chat.id
    user_data = sent_message_add_screen_ids[tuid]
    # Добавляем сообщение пользователя
    user_data['user_messages'].append(callback_query.message.message_id)

    # Удаляем предыдущие сообщения
    await delete_previous_messages(callback_query.message, tuid)

    data = await state.get_data()
    question_text = data['question_text']
    options = data['options']
    user_id = callback_query.from_user.id
    correct_option = data['correct_option']

    option_a = options.get('A', '')
    option_b = options.get('B', '')
    option_v = options.get('V', '')
    option_g = options.get('G', '')

    # Записываем вопрос в БД
    is_not_have = await rq.write_question(telegram_id=user_id, subject_id=1, content=question_text, option_a=option_a,
                                          option_b=option_b,
                                          option_v=option_v, option_g=option_g, correct_option=correct_option,
                                          status="pending")
    if is_not_have:
        await rq.add_rubies(telegram_id=user_id, rubies_amount=5)

        sent_message = await callback_query.message.answer_photo(
            photo=utils.picturePlusFiveRubin,
            caption='Ваш вопрос принят!'
                    '\n*+5 рубинов* 💎 добавлено.',
            reply_markup=kb.to_user_account_ru,
            parse_mode=ParseMode.MARKDOWN
        )
        await state.clear()
        # Добавляем сообщение бота
        user_data['bot_messages'].append(sent_message.message_id)
    else:
        sent_message = await callback_query.message.answer_photo(
            photo=utils.pictureBadRequests,
            caption='Вопрос, который вы написали, есть в базе данных!'
                    '\nПожалуйста, введите другой вопрос.',
            reply_markup=kb.to_user_account_ru,
            parse_mode=ParseMode.MARKDOWN
        )
        # Добавляем сообщение бота
        user_data['bot_messages'].append(sent_message.message_id)

# Write kg grammar questions to the DB
@router.callback_query(F.data == 'kg_send_an_grammar')
async def write_grammar_to_db(callback_query: CallbackQuery, state: FSMContext):
    tuid = callback_query.message.chat.id
    user_data = sent_message_add_screen_ids[tuid]
    # Добавляем сообщение пользователя
    user_data['user_messages'].append(callback_query.message.message_id)

    # Удаляем предыдущие сообщения
    await delete_previous_messages(callback_query.message, tuid)

    data = await state.get_data()
    question_text = data['question_text']
    options = data['options']
    user_id = callback_query.from_user.id
    correct_option = data['correct_option']

    option_a = options.get('A', '')
    option_b = options.get('B', '')
    option_v = options.get('V', '')
    option_g = options.get('G', '')

    # Записываем вопрос в БД
    is_not_have = await rq.write_question(telegram_id=user_id, subject_id=2, content=question_text, option_a=option_a, option_b=option_b,
                            option_v=option_v, option_g=option_g, correct_option=correct_option, status="pending")
    if is_not_have:
        await rq.add_rubies(telegram_id=user_id, rubies_amount=5)

        sent_message = await callback_query.message.answer_photo(
            photo=utils.picturePlusFiveRubin,
            caption='Сиздин суроо кабыл алынды!'
                    '\n*+5 рубин* 💎 кошулду.',
            reply_markup=kb.to_user_account_kg,
            parse_mode=ParseMode.MARKDOWN
        )
        await state.clear()
        # Добавляем сообщение бота
        user_data['bot_messages'].append(sent_message.message_id)
    else:
        sent_message = await callback_query.message.answer_photo(
            photo=utils.pictureBadRequests,
            caption='Сиз жазган суроо базада бар экен!'
                    '\nСураныч, башка суроо киргизиңиз.',
            reply_markup=kb.to_user_account_kg,
            parse_mode=ParseMode.MARKDOWN
        )
        # Добавляем сообщение бота
        user_data['bot_messages'].append(sent_message.message_id)


@router.callback_query(F.data == "back_to_account")
async def back_to_account(callback_query: CallbackQuery, state: FSMContext):
    # Удаляем сообщение с уведомлением
    await callback_query.message.delete()


@router.callback_query(F.data == 'vip_ru')
async def vip_ru(callback_query: CallbackQuery, state: FSMContext):
    tuid = callback_query.message.chat.id
    user_data = sent_message_add_screen_ids[tuid]
    # Добавляем сообщение пользователя
    user_data['user_messages'].append(callback_query.message.message_id)

    # Удаляем предыдущие сообщения
    await delete_previous_messages(callback_query.message, tuid)

    # Получаем Telegram ID пользователя
    telegram_id = callback_query.from_user.id

    sent_message = await callback_query.message.answer_photo(
        photo=utils.pictureForGoToVIPRU,
        caption=(
            f'<a href="https://telegra.ph/Telegram-bot-dlya-podgotovki-k-ORT-Obychnye-i-VIP-polzovateli-11-16">'
            f"Каковы преимущества статуса VIP-пользователя?</a> 👈\n\n"
            f"Если вы хотите стать VIP-пользователем или у вас есть вопросы, нажмите кнопку ниже👇"
        ),
        reply_markup=kb.whatsapp_button_ru(telegram_id=telegram_id),
        parse_mode=ParseMode.HTML
    )
    # Добавляем сообщение бота
    user_data['bot_messages'].append(sent_message.message_id)


@router.callback_query(F.data == 'vip_kg')
async def vip_kg(callback_query: CallbackQuery, state: FSMContext):
    tuid = callback_query.message.chat.id
    user_data = sent_message_add_screen_ids[tuid]
    # Добавляем сообщение пользователя
    user_data['user_messages'].append(callback_query.message.message_id)

    # Удаляем предыдущие сообщения
    await delete_previous_messages(callback_query.message, tuid)

    # Получаем Telegram ID пользователя
    telegram_id = callback_query.from_user.id

    sent_message = await callback_query.message.answer_photo(
        photo=utils.pictureForGoToVIPKG,
        caption=(
            f'<a href="https://telegra.ph/ZHRT-Dayardoo-Telegram-Botunda-ZH%D3%A9n%D3%A9k%D3%A9j-zhana-VIP-Koldonuuchular-11-16">'
            f"VIP колдонуучунун кандай артыкчылыктары бар?</a> 👈\n\n"
            f"Эгер VIP колдонуучуга өтүүнү кааласаңыз же суроолоруңуз болсо төмөндөнү баскычты басаңыз👇"
        ),
        reply_markup=kb.whatsapp_button_kg(telegram_id=telegram_id),
        parse_mode=ParseMode.HTML
    )
    # Добавляем сообщение бота
    user_data['bot_messages'].append(sent_message.message_id)

@router.callback_query(F.data == 'settings_ru')
async def setting_user_ru(callback_query: CallbackQuery, state: FSMContext):
    tuid = callback_query.message.chat.id
    user_data = sent_message_add_screen_ids[tuid]
    # Добавляем сообщение пользователя
    user_data['user_messages'].append(callback_query.message.message_id)

    # Удаляем предыдущие сообщения
    await delete_previous_messages(callback_query.message, tuid)

    sent_message = await callback_query.message.answer_photo(
        photo=utils.PictureForUserSettingsRU,
        caption="Выберите нужную вам команду",
        reply_markup=kb.user_settings_ru
    )

    # Добавляем сообщение бота
    user_data['bot_messages'].append(sent_message.message_id)

@router.callback_query(F.data == 'settings_kg')
async def setting_user_ru(callback_query: CallbackQuery, state: FSMContext):
    tuid = callback_query.message.chat.id
    user_data = sent_message_add_screen_ids[tuid]
    # Добавляем сообщение пользователя
    user_data['user_messages'].append(callback_query.message.message_id)

    # Удаляем предыдущие сообщения
    await delete_previous_messages(callback_query.message, tuid)

    sent_message = await callback_query.message.answer_photo(
        photo=utils.PictureForUserSettingsKG,
        caption="Сизге керек команданы тандаңыз",
        reply_markup=kb.user_settings_kg
    )

    # Добавляем сообщение бота
    user_data['bot_messages'].append(sent_message.message_id)

@router.callback_query(F.data == 'change_language_kg')
async def change_language_kg(callback_query: CallbackQuery, state: FSMContext):
    tuid = callback_query.message.chat.id
    user_data = sent_message_add_screen_ids[tuid]
    # Добавляем сообщение пользователя
    user_data['user_messages'].append(callback_query.message.message_id)

    # Удаляем предыдущие сообщения
    await delete_previous_messages(callback_query.message, tuid)
    sent_message = await callback_query.message.answer_photo(
        photo=utils.PictureForChangeLanguaageKG,
        caption="Сиз чындап тилди орус тилине алмаштырууну каалайсызбы?\n"
                "Эгер кааласаңыз 'ru' деп жазыңыз, каалабасаңыз артка кайтууну басыңыз.",
        reply_markup=kb.to_user_account_kg
    )
    await state.set_state(st.ChangeLanguageKG.write_ru)
    # Добавляем сообщение бота
    user_data['bot_messages'].append(sent_message.message_id)

@router.message(st.ChangeLanguageKG.write_ru)
async def change_language_kg_write_ru(message: Message, state: FSMContext):
    tuid = message.chat.id
    user_data = sent_message_add_screen_ids[tuid]
    # Добавляем сообщение пользователя
    user_data['user_messages'].append(message.message_id)

    # Удаляем предыдущие сообщения
    await delete_previous_messages(message, tuid)
    user_telegram_id = message.from_user.id
    input_user = message.text

    if input_user == 'ru':
        is_changed = await rq.set_user_language_to_ru(telegram_id=user_telegram_id)
        if is_changed:
            sent_message = await message.answer(
                text="Сиздин тил орус тилине алмашылды.",
                reply_markup=kb.to_user_account_ru
            )
            # Добавляем сообщение бота
            user_data['bot_messages'].append(sent_message.message_id)
        else:
            sent_message = await message.answer(
                text="Тилди алмаштырууда ката чыкты!",
                reply_markup=kb.to_user_account_kg
            )
            # Добавляем сообщение бота
            user_data['bot_messages'].append(sent_message.message_id)
    else:
        sent_message = await message.answer(
            text="Сиз сөздү туура эмес жаздыңыз!",
            reply_markup=kb.to_user_account_kg
        )
        # Добавляем сообщение бота
        user_data['bot_messages'].append(sent_message.message_id)
    await state.clear()


@router.callback_query(F.data == 'change_language_ru')
async def change_language_ru(callback_query: CallbackQuery, state: FSMContext):
    tuid = callback_query.message.chat.id
    user_data = sent_message_add_screen_ids[tuid]
    # Добавляем сообщение пользователя
    user_data['user_messages'].append(callback_query.message.message_id)

    # Удаляем предыдущие сообщения
    await delete_previous_messages(callback_query.message, tuid)
    sent_message = await callback_query.message.answer_photo(
        photo=utils.PictureForChangeLanguaageRU,
        caption="Вы уверены, что хотите сменить язык на кыргызский?\n"
                "Если хотите, введите «kg», если нет, нажмите «Назад».",
        reply_markup=kb.to_user_account_kg
    )
    await state.set_state(st.ChangeLanguageRU.write_kg)
    # Добавляем сообщение бота
    user_data['bot_messages'].append(sent_message.message_id)

@router.message(st.ChangeLanguageRU.write_kg)
async def change_language_ru_write_kg(message: Message, state: FSMContext):
    tuid = message.chat.id
    user_data = sent_message_add_screen_ids[tuid]
    # Добавляем сообщение пользователя
    user_data['user_messages'].append(message.message_id)

    # Удаляем предыдущие сообщения
    await delete_previous_messages(message, tuid)
    user_telegram_id = message.from_user.id
    input_user = message.text

    if input_user == 'kg':
        is_changed = await rq.set_user_language_to_kg(telegram_id=user_telegram_id)
        if is_changed:
            sent_message = await message.answer(
                text="Ваш язык изменен на кыргызский.",
                reply_markup=kb.to_user_account_kg
            )
            # Добавляем сообщение бота
            user_data['bot_messages'].append(sent_message.message_id)
        else:
            sent_message = await message.answer(
                text="Произошла ошибка при смене языка!",
                reply_markup=kb.to_user_account_ru
            )
            # Добавляем сообщение бота
            user_data['bot_messages'].append(sent_message.message_id)
    else:
        sent_message = await message.answer(
            text="Вы неправильно написали слово!",
            reply_markup=kb.to_user_account_ru
        )
        # Добавляем сообщение бота
        user_data['bot_messages'].append(sent_message.message_id)
    await state.clear()


@router.callback_query(F.data == 'change_phone_number_ru')
async def prompt_change_phone_number_ru(callback_query: CallbackQuery, state: FSMContext):
    tuid = callback_query.message.chat.id
    user_data = sent_message_add_screen_ids[tuid]
    # Добавляем сообщение пользователя
    user_data['user_messages'].append(callback_query.message.message_id)

    # Удаляем предыдущие сообщения
    await delete_previous_messages(callback_query.message, tuid)

    # Отправляем сообщение с просьбой ввести новый номер телефона
    sent_message = await callback_query.message.answer_photo(
        photo=utils.PictureForChangePhoneNumberRU,
        caption="Пожалуйста, введите ваш новый номер телефона:",
        reply_markup=kb.to_user_account_ru
    )

    # Переходим в состояние ввода номера телефона
    await state.set_state(st.ChangePhoneNumberRU.enter_phone_ru)
    # Добавляем сообщение бота
    user_data['bot_messages'].append(sent_message.message_id)


@router.message(st.ChangePhoneNumberRU.enter_phone_ru)
async def change_phone_number(message: Message, state: FSMContext):
    tuid = message.chat.id
    user_data = sent_message_add_screen_ids[tuid]
    # Добавляем сообщение пользователя
    user_data['user_messages'].append(message.message_id)

    # Удаляем предыдущие сообщения
    await delete_previous_messages(message, tuid)
    new_phone_number = message.text.strip()

    # Проверяем формат номера телефона
    if not re.match(r"^\+996\d{9}$", new_phone_number):
        sent_message = await message.answer(
            text="Некорректный номер телефона. Пожалуйста, введите номер в формате +996XXXXXXXXX.",
            reply_markup=kb.to_user_account_ru)
        # Добавляем сообщение бота
        user_data['bot_messages'].append(sent_message.message_id)
    else:
        telegram_id = message.from_user.id

        is_updated = await rq.update_user_phone_number(telegram_id, new_phone_number)

        if is_updated:
            sent_message = await message.answer(
                text="Ваш номер телефона успешно обновлен.",
                reply_markup=kb.to_user_account_ru)
            # Добавляем сообщение бота
            user_data['bot_messages'].append(sent_message.message_id)
        else:
            sent_message = await message.answer(
                text="Не удалось обновить номер телефона. Попробуйте позже.",
                reply_markup=kb.to_user_account_ru)
            # Добавляем сообщение бота
            user_data['bot_messages'].append(sent_message.message_id)

    await state.clear()


@router.callback_query(F.data == 'change_phone_number_kg')
async def prompt_change_phone_number_kg(callback_query: CallbackQuery, state: FSMContext):
    tuid = callback_query.message.chat.id
    user_data = sent_message_add_screen_ids[tuid]
    # Добавляем сообщение пользователя
    user_data['user_messages'].append(callback_query.message.message_id)

    # Удаляем предыдущие сообщения
    await delete_previous_messages(callback_query.message, tuid)

    # Отправляем сообщение с просьбой ввести новый номер телефона
    sent_message = await callback_query.message.answer_photo(
        photo=utils.PictureForChangePhoneNumberKG,
        caption="Сураныч, жаңы телефон номериңизди киргизиңиз:",
        reply_markup=kb.to_user_account_kg
    )

    # Переходим в состояние ввода номера телефона
    await state.set_state(st.ChangePhoneNumberKG.enter_phone_kg)
    # Добавляем сообщение бота
    user_data['bot_messages'].append(sent_message.message_id)


@router.message(st.ChangePhoneNumberKG.enter_phone_kg)
async def change_phone_number(message: Message, state: FSMContext):
    tuid = message.chat.id
    user_data = sent_message_add_screen_ids[tuid]
    # Добавляем сообщение пользователя
    user_data['user_messages'].append(message.message_id)

    # Удаляем предыдущие сообщения
    await delete_previous_messages(message, tuid)
    new_phone_number = message.text.strip()

    # Проверяем формат номера телефона
    if not re.match(r"^\+996\d{9}$", new_phone_number):
        sent_message = await message.answer(
            text="Жараксыз телефон номери. Номерди +996ХХХХХХХХ форматында киргизиңиз.",
            reply_markup=kb.to_user_account_kg)
        # Добавляем сообщение бота
        user_data['bot_messages'].append(sent_message.message_id)
    else:
        telegram_id = message.from_user.id

        is_updated = await rq.update_user_phone_number(telegram_id, new_phone_number)

        if is_updated:
            sent_message = await message.answer(
                text="Телефон номериңиз ийгиликтүү жаңыртылды.",
                reply_markup=kb.to_user_account_kg)
            # Добавляем сообщение бота
            user_data['bot_messages'].append(sent_message.message_id)
        else:
            sent_message = await message.answer(
                text="Телефон номери жаңыртылган жок. Кийинчерээк кайра аракет кылыңыз.",
                reply_markup=kb.to_user_account_kg)
            # Добавляем сообщение бота
            user_data['bot_messages'].append(sent_message.message_id)

    await state.clear()


# Обработчик для кнопки "Текущий статус"
@router.callback_query(F.data == 'current_status_ru')
async def current_status_ru(callback_query: CallbackQuery):
    tuid = callback_query.message.chat.id
    user_data = sent_message_add_screen_ids[tuid]
    # Добавляем сообщение пользователя
    user_data['user_messages'].append(callback_query.message.message_id)

    # Удаляем предыдущие сообщения
    await delete_previous_messages(callback_query.message, tuid)
    telegram_id = callback_query.from_user.id

    # Получаем текущий статус пользователя из базы данных
    user_status = await rq.get_user_status_ru(telegram_id)

    # Проверяем статус и отправляем соответствующее сообщение
    if user_status == "VIP":
        status_message = (
            f"Ваш текущий статус: VIP.\n"
        )
    elif user_status != "VIP":
        status_message = (
            f"Ваш текущий статус: Обычный.\n"
        )
    else:
        status_message = "Статус не найден. Возможно, вы не зарегистрированы."

    sent_message = await callback_query.message.answer_photo(
        photo=utils.PictureForMyStatusRU,
        caption=status_message,
        reply_markup=kb.to_user_account_ru
    )
    # Добавляем сообщение бота
    user_data['bot_messages'].append(sent_message.message_id)

# Обработчик для кнопки "Текущий статус"
@router.callback_query(F.data == 'current_status_kg')
async def current_status_kg(callback_query: CallbackQuery):
    tuid = callback_query.message.chat.id
    user_data = sent_message_add_screen_ids[tuid]
    # Добавляем сообщение пользователя
    user_data['user_messages'].append(callback_query.message.message_id)

    # Удаляем предыдущие сообщения
    await delete_previous_messages(callback_query.message, tuid)
    telegram_id = callback_query.from_user.id

    # Получаем текущий статус пользователя из базы данных
    user_status = await rq.get_user_status_kg(telegram_id)

    # Проверяем статус и отправляем соответствующее сообщение
    if user_status == "VIP":
        status_message = (
            f"Сиздин статус: VIP.\n"
        )
    elif user_status != "VIP":
        status_message = (
            f"Сиздин статус: Жөнөкөй.\n"
        )
    else:
        status_message = "Статус белгисиз. Балким, сиз регистрация болгон эмессиз."

    sent_message = await callback_query.message.answer_photo(
        photo=utils.PictureForMyStatusKG,
        caption=status_message,
        reply_markup=kb.to_user_account_kg
    )
    # Добавляем сообщение бота
    user_data['bot_messages'].append(sent_message.message_id)

@router.callback_query(F.data == 'helpdesk_kg')
async def helpdesk_kg(callback_query: CallbackQuery, state: FSMContext):
    tuid = callback_query.message.chat.id
    user_data = sent_message_add_screen_ids[tuid]
    # Добавляем сообщение пользователя
    user_data['user_messages'].append(callback_query.message.message_id)

    # Удаляем предыдущие сообщения
    await delete_previous_messages(callback_query.message, tuid)
    sent_message = await callback_query.message.answer_photo(
        photo=utils.PictureForFAQKG,
        caption="Бот боюнча кандайдыр бир суроолор бар болсо төмөндөгү баскычты бас.",
        reply_markup=kb.whatsapp_button_without_text_kg
    )
    # Добавляем сообщение бота
    user_data['bot_messages'].append(sent_message.message_id)

@router.callback_query(F.data == 'helpdesk_ru')
async def helpdesk_ru(callback_query: CallbackQuery, state: FSMContext):
    tuid = callback_query.message.chat.id
    user_data = sent_message_add_screen_ids[tuid]
    # Добавляем сообщение пользователя
    user_data['user_messages'].append(callback_query.message.message_id)

    # Удаляем предыдущие сообщения
    await delete_previous_messages(callback_query.message, tuid)
    sent_message = await callback_query.message.answer_photo(
        photo=utils.PictureForFAQRU,
        caption="Если у вас есть вопросы по боту, нажмите кнопку ниже.",
        reply_markup=kb.whatsapp_button_without_text_ru
    )
    # Добавляем сообщение бота
    user_data['bot_messages'].append(sent_message.message_id)

# Хендлер для кнопки "Изменить никнейм/ФИО"
@router.callback_query(F.data == 'change_nickname_ru')
async def change_nickname_ru(callback_query: CallbackQuery, state: FSMContext):
    tuid = callback_query.message.chat.id
    user_data = sent_message_add_screen_ids[tuid]
    # Добавляем сообщение пользователя
    user_data['user_messages'].append(callback_query.message.message_id)

    # Удаляем предыдущие сообщения
    await delete_previous_messages(callback_query.message, tuid)
    sent_message = await callback_query.message.answer_photo(
        photo=utils.PictureForChangeNicknameRU,
        caption="Введите ваш новый никнейм или ФИО, чтобы обновить.",
        reply_markup=kb.to_user_account_ru
    )
    await state.set_state(st.ChangeNicknameRU.enter_nickname_ru)
    # Добавляем сообщение бота
    user_data['bot_messages'].append(sent_message.message_id)

@router.message(st.ChangeNicknameRU.enter_nickname_ru)
async def change_nickname_ru_finish(message: Message, state: FSMContext):
    tuid = message.chat.id
    user_data = sent_message_add_screen_ids[tuid]
    # Добавляем сообщение пользователя
    user_data['user_messages'].append(message.message_id)

    # Удаляем предыдущие сообщения
    await delete_previous_messages(message, tuid)
    user_telegram_id = message.from_user.id
    new_name = message.text
    is_changed = await rq.update_user_name(telegram_id=user_telegram_id, new_name=new_name)

    if is_changed:
        sent_message = await message.answer(
            text="Ваше ФИО было успешно изменено!",
            reply_markup=kb.to_user_account_ru
        )
        # Добавляем сообщение бота
        user_data['bot_messages'].append(sent_message.message_id)
    else:
        sent_message = await message.answer(
            text="Произошла ошибка при изменении ФИО!",
            reply_markup=kb.to_user_account_ru
        )
        # Добавляем сообщение бота
        user_data['bot_messages'].append(sent_message.message_id)

    await state.clear()


# Хендлер для кнопки "Изменить никнейм/ФИО"
@router.callback_query(F.data == 'change_nickname_kg')
async def change_nickname_kg(callback_query: CallbackQuery, state: FSMContext):
    tuid = callback_query.message.chat.id
    user_data = sent_message_add_screen_ids[tuid]
    # Добавляем сообщение пользователя
    user_data['user_messages'].append(callback_query.message.message_id)

    # Удаляем предыдущие сообщения
    await delete_previous_messages(callback_query.message, tuid)
    sent_message = await callback_query.message.answer_photo(
        photo=utils.PictureForChangeNicknameKG,
        caption="Жаңы ФИО жазыңыз.",
        reply_markup=kb.to_user_account_kg
    )
    await state.set_state(st.ChangeNicknameKG.enter_nickname_kg)
    # Добавляем сообщение бота
    user_data['bot_messages'].append(sent_message.message_id)

@router.message(st.ChangeNicknameKG.enter_nickname_kg)
async def change_nickname_kg_finish(message: Message, state: FSMContext):
    tuid = message.chat.id
    user_data = sent_message_add_screen_ids[tuid]
    # Добавляем сообщение пользователя
    user_data['user_messages'].append(message.message_id)

    # Удаляем предыдущие сообщения
    await delete_previous_messages(message, tuid)
    user_telegram_id = message.from_user.id
    new_name = message.text
    is_changed = await rq.update_user_name(telegram_id=user_telegram_id, new_name=new_name)

    if is_changed:
        sent_message = await message.answer(
            text="ФИО ийгиликтүү алмаштырылды!",
            reply_markup=kb.to_user_account_kg
        )
        # Добавляем сообщение бота
        user_data['bot_messages'].append(sent_message.message_id)
    else:
        sent_message = await message.answer(
            text="ФИО алмаштырууда ката кетти!",
            reply_markup=kb.to_user_account_kg
        )
        # Добавляем сообщение бота
        user_data['bot_messages'].append(sent_message.message_id)

    await state.clear()


@router.callback_query(F.data == 'my_profile_ru')
async def my_profile(callback_query: CallbackQuery):
    tuid = callback_query.message.chat.id
    user_data = sent_message_add_screen_ids[tuid]
    # Добавляем сообщение пользователя
    user_data['user_messages'].append(callback_query.message.message_id)

    # Удаляем предыдущие сообщения
    await delete_previous_messages(callback_query.message, tuid)
    telegram_id = callback_query.from_user.id

    # Получаем данные пользователя из базы данных
    user_profile = await rq.get_user_profile_data(telegram_id)

    # Формируем красивое сообщение с данными пользователя
    profile_message = (
        f"🌟 *Мой профиль* 🌟\n\n"
        f"🆔 *Telegram ID:* {telegram_id}\n"
        f"👤 *ФИО:* {user_profile['name']}\n"
        f"📱 *Номер телефона:* {user_profile['phone_number']}\n"
        f"💎 *Рубины:* {user_profile['rubies']}\n"
        f"💼 *Статус подписки:* {'VIP' if user_profile['subscription_status'] else 'Обычный'}\n"
        f"🗓️ *Дата регистрации:* {user_profile['created_at'].strftime('%d-%m-%Y')}\n"
    )

    sent_message = await callback_query.message.answer(
        text=profile_message,
        reply_markup=kb.to_user_account_ru,
        parse_mode=ParseMode.MARKDOWN
    )
    # Добавляем сообщение бота
    user_data['bot_messages'].append(sent_message.message_id)


@router.callback_query(F.data == 'my_profile_kg')
async def my_profile(callback_query: CallbackQuery):
    tuid = callback_query.message.chat.id
    user_data = sent_message_add_screen_ids[tuid]
    # Добавляем сообщение пользователя
    user_data['user_messages'].append(callback_query.message.message_id)

    # Удаляем предыдущие сообщения
    await delete_previous_messages(callback_query.message, tuid)
    telegram_id = callback_query.from_user.id

    # Получаем данные пользователя из базы данных
    user_profile = await rq.get_user_profile_data(telegram_id)

    # Формируем красивое сообщение с данными пользователя
    profile_message = (
        f"🌟 *Менин профилим* 🌟\n\n"
        f"🆔 *Telegram ID:* {telegram_id}\n"
        f"👤 *ФИО:* {user_profile['name']}\n"
        f"📱 *Телефон номер:* {user_profile['phone_number']}\n"
        f"💎 *Рубин:* {user_profile['rubies']}\n"
        f"💼 *Статус:* {'VIP' if user_profile['subscription_status'] else 'Обычный'}\n"
        f"🗓️ *Катталган дата:* {user_profile['created_at'].strftime('%d-%m-%Y')}\n"
    )

    sent_message = await callback_query.message.answer(
        text=profile_message,
        reply_markup=kb.to_user_account_kg,
        parse_mode=ParseMode.MARKDOWN
    )
    # Добавляем сообщение бота
    user_data['bot_messages'].append(sent_message.message_id)


# Хендлер для показа первой страницы рейтинга
@router.callback_query(F.data == 'rating_ru')
async def show_user_ranking(callback_query: CallbackQuery):
    await display_ranking_page(callback_query, page=1)

# Функция для отображения страницы рейтинга
async def display_ranking_page(callback_query: CallbackQuery, page: int):
    tuid = callback_query.message.chat.id
    user_data = sent_message_add_screen_ids[tuid]
    # Добавляем сообщение пользователя
    user_data['user_messages'].append(callback_query.message.message_id)

    # Удаляем предыдущие сообщения
    await delete_previous_messages(callback_query.message, tuid)

    page_size = 50
    users = await rq.get_users_ranking(page, page_size)

    if not users:
        if page == 1:
            keyboard = kb.rating_buttons_last_page_ru(page)
            sent_message = await callback_query.message.answer(
                text="Вы дошли до последней страницы.",
                reply_markup=keyboard)
            # Добавляем сообщение бота
            user_data['bot_messages'].append(sent_message.message_id)
        else:
            keyboard = kb.rating_buttons_last_page_ru(page)
            sent_message = await callback_query.message.answer(
                text="Вы дошли до последней страницы.",
                reply_markup=keyboard)
            # Добавляем сообщение бота
            user_data['bot_messages'].append(sent_message.message_id)
    else:
        # Формируем текст для вывода рейтинга
        ranking_text = f"🌟 *РЕЙТИНГ ПОЛЬЗОВАТЕЛЕЙ* 🌟\n\nСтраница: {page}\n\n"
        for idx, (name, rubies) in enumerate(users, start=(page - 1) * page_size + 1):
            ranking_text += f"{idx}. _{name}_ : {rubies} 💎\n"

        # Определяем, какую клавиатуру использовать в зависимости от страницы
        if page == 1:
            keyboard = kb.rating_buttons_first_page_ru(page)
        else:
            keyboard = kb.rating_buttons_other_pages_ru(page)

        # Отправляем или обновляем сообщение с рейтингом
        sent_message = await callback_query.message.answer(text=ranking_text, reply_markup=keyboard, parse_mode="Markdown")
        # Добавляем сообщение бота
        user_data['bot_messages'].append(sent_message.message_id)

# Хендлер для кнопок перехода по страницам
@router.callback_query(lambda c: c.data and c.data.startswith("rating_page_"))
async def handle_pagination(callback_query: CallbackQuery):
    page = int(callback_query.data.split("_")[2])  # Извлекаем номер страницы из callback_data
    await display_ranking_page(callback_query, page)

# Хендлер для кнопки "Найти меня"
@router.callback_query(F.data == 'find_me_in_rating_ru')
async def find_user_in_ranking(callback_query: CallbackQuery):
    telegram_id = callback_query.from_user.id
    rank = await rq.get_user_rank(telegram_id)

    if rank is None:
        await callback_query.message.answer(
            text="Не удалось найти ваш рейтинг.",
            reply_markup=kb.to_user_account_ru)
    else:
        # Рассчитываем страницу пользователя
        page_size = 50
        user_page = (rank - 1) // page_size + 1

        # Переходим на страницу пользователя в рейтинге
        await display_ranking_page(callback_query, page=user_page)


# Хендлер для показа первой страницы рейтинга
@router.callback_query(F.data == 'rating_kg')
async def show_user_ranking_kg(callback_query: CallbackQuery):
    await display_ranking_page_kg(callback_query, page=1)

# Функция для отображения страницы рейтинга
async def display_ranking_page_kg(callback_query: CallbackQuery, page: int):
    tuid = callback_query.message.chat.id
    user_data = sent_message_add_screen_ids[tuid]
    # Добавляем сообщение пользователя
    user_data['user_messages'].append(callback_query.message.message_id)

    # Удаляем предыдущие сообщения
    await delete_previous_messages(callback_query.message, tuid)

    page_size = 50
    users = await rq.get_users_ranking(page, page_size)

    if not users:
        if page == 1:
            keyboard = kb.rating_buttons_last_page_kg(page)
            sent_message = await callback_query.message.answer(
                text="Cиз акыркы бетке келдиңиз.",
                reply_markup=keyboard)
            # Добавляем сообщение бота
            user_data['bot_messages'].append(sent_message.message_id)
        else:
            keyboard = kb.rating_buttons_last_page_kg(page)
            sent_message = await callback_query.message.answer(
                text="Cиз акыркы бетке келдиңиз.",
                reply_markup=keyboard)
            # Добавляем сообщение бота
            user_data['bot_messages'].append(sent_message.message_id)
    else:
        # Формируем текст для вывода рейтинга
        ranking_text = f"🌟 *КОЛДОНУУЧУЛАР РЕЙТИНГИ* 🌟\n\nБет: {page}\n\n"
        for idx, (name, rubies) in enumerate(users, start=(page - 1) * page_size + 1):
            ranking_text += f"{idx}. _{name}_ : {rubies} 💎\n"

        # Определяем, какую клавиатуру использовать в зависимости от страницы
        if page == 1:
            keyboard = kb.rating_buttons_first_page_kg(page)
        else:
            keyboard = kb.rating_buttons_other_pages_kg(page)

        # Отправляем или обновляем сообщение с рейтингом
        sent_message = await callback_query.message.answer(text=ranking_text, reply_markup=keyboard, parse_mode="Markdown")
        # Добавляем сообщение бота
        user_data['bot_messages'].append(sent_message.message_id)

# Хендлер для кнопок перехода по страницам
@router.callback_query(lambda c: c.data and c.data.startswith("kg_rating_page_"))
async def handle_pagination(callback_query: CallbackQuery):
    page = int(callback_query.data.split("_")[3])  # Извлекаем номер страницы из callback_data
    await display_ranking_page_kg(callback_query, page)

# Хендлер для кнопки "Найти меня"
@router.callback_query(F.data == 'find_me_in_rating_kg')
async def find_user_in_ranking_kg(callback_query: CallbackQuery):
    telegram_id = callback_query.from_user.id
    rank = await rq.get_user_rank(telegram_id)

    if rank is None:
        await callback_query.message.answer(
            text="Сиздин рейтингиңиз табылган жок.",
            reply_markup=kb.to_user_account_kg)
    else:
        # Рассчитываем страницу пользователя
        page_size = 50
        user_page = (rank - 1) // page_size + 1

        # Переходим на страницу пользователя в рейтинге
        await display_ranking_page_kg(callback_query, page=user_page)


#################################################################################
#                  Passing the test in Russian                                  #
#################################################################################
@router.callback_query(F.data == 'take_test_ru')
async def take_test_ru(callback_query: CallbackQuery):
    tuid = callback_query.message.chat.id
    user_data = sent_message_add_screen_ids[tuid]
    # Добавляем сообщение пользователя
    user_data['user_messages'].append(callback_query.message.message_id)

    # Удаляем предыдущие сообщения
    await delete_previous_messages(callback_query.message, tuid)
    sent_message = await callback_query.message.answer_photo(
        photo=utils.PictureForTakeTheTestRU,
        caption="Выберите категорию, по которой вы хотите пройти тест.",
        reply_markup=kb.select_subject_ru
    )
    # Добавляем сообщение бота
    user_data['bot_messages'].append(sent_message.message_id)


# Passing the analogy test in Russian
@router.callback_query(F.data == 'take_analogy_ru')
async def start_analogy_test(callback_query: CallbackQuery):
    tuid = callback_query.message.chat.id
    user_data = sent_message_add_screen_ids[tuid]
    # Добавляем сообщение пользователя
    user_data['user_messages'].append(callback_query.message.message_id)

    # Удаляем предыдущие сообщения
    await delete_previous_messages(callback_query.message, tuid)
    telegram_id = callback_query.from_user.id

    count_passed_questions = await rq.count_user_answered_questions(telegram_id=telegram_id, subject_id1=1, subject_id2=3)
    if count_passed_questions >= 50:
        is_vip = await rq.is_vip_user(telegram_id=telegram_id)

        if is_vip:
            # Получаем индекс последнего сданного вопроса
            last_question_index = await rq.get_last_answered_question_index(telegram_id=telegram_id, subject_id=3)

            # Получаем следующий вопрос, основываясь на последнем сданном
            next_question = await rq.get_next_question(last_answered_question_id=last_question_index, subject_id=3)

            if next_question:
                # Если следующий вопрос существует, создаем текст вопроса и вариант ответов
                question_text = f"*Пара:* {next_question['content']}\n"

                # Генерируем клавиатуру с вариантами ответов
                keyboard = kb.generate_answer_keyboard_ru(
                    question_id=next_question['question_id'],
                    option_a=next_question['option_a'],
                    option_b=next_question['option_b'],
                    option_v=next_question['option_v'],
                    option_g=next_question['option_g']
                )

                sent_message = await callback_query.message.answer_photo(
                    photo=utils.PictureForTakeAnalogyQuestionRU,
                    caption=question_text,
                    reply_markup=keyboard, # Отправляем сообщение с клавиатурой
                    parse_mode=ParseMode.MARKDOWN
                )
            else:
                # Если нет следующего вопроса, сообщаем пользователю
                sent_message = await callback_query.message.answer_photo(
                    photo=utils.PictureForTakeAnalogyQuestionRU,
                    caption="Вы прошли все тесты! Вы можете вернуться позже или начать тест заново. Обратите внимание, "
                            "что при повторном прохождении все данные о ваших пройденных вопросах будут сброшены, "
                            "и вам нужно будет пройти тест заново. Однако количество рубинов останется неизменным.",
                    reply_markup=kb.take_the_test_again_analogy_ru
                )

            # Добавляем сообщение бота
            user_data['bot_messages'].append(sent_message.message_id)
        else:
            sent_message = await callback_query.message.answer_photo(
                photo=utils.PictureForTakeAnalogyQuestionKG,
                caption="Вы достигли лимита 50 вопросов. Чтобы получить доступ к больше чем 4000 вопросам, вы должны "
                        "получить статус VIP. Для этого в личном кабинете выберите кнопку VIP и свяжитесь с админом.",
                reply_markup=kb.to_user_account_ru
            )
            # Добавляем сообщение бота
            user_data['bot_messages'].append(sent_message.message_id)
    else:
        # Получаем индекс последнего сданного вопроса
        last_question_index = await rq.get_last_answered_question_index(telegram_id=telegram_id, subject_id=3)

        # Получаем следующий вопрос, основываясь на последнем сданном
        next_question = await rq.get_next_question(last_answered_question_id=last_question_index, subject_id=3)

        if next_question:
            # Если следующий вопрос существует, создаем текст вопроса и вариант ответов
            question_text = f"*Пара:* {next_question['content']}\n"

            # Генерируем клавиатуру с вариантами ответов
            keyboard = kb.generate_answer_keyboard_ru(
                question_id=next_question['question_id'],
                option_a=next_question['option_a'],
                option_b=next_question['option_b'],
                option_v=next_question['option_v'],
                option_g=next_question['option_g']
            )

            sent_message = await callback_query.message.answer_photo(
                photo=utils.PictureForTakeAnalogyQuestionRU,
                caption=question_text,
                reply_markup=keyboard,  # Отправляем сообщение с клавиатурой
                parse_mode=ParseMode.MARKDOWN
            )
        else:
            # Если нет следующего вопроса, сообщаем пользователю
            sent_message = await callback_query.message.answer_photo(
                photo=utils.PictureForTakeAnalogyQuestionRU,
                caption="Вы прошли все тесты! Вы можете вернуться позже или начать тест заново. Обратите внимание, "
                        "что при повторном прохождении все данные о ваших пройденных вопросах будут сброшены, "
                        "и вам нужно будет пройти тест заново. Однако количество рубинов останется неизменным.",
                reply_markup=kb.take_the_test_again_analogy_ru
            )

        # Добавляем сообщение бота
        user_data['bot_messages'].append(sent_message.message_id)



@router.callback_query(lambda c: c.data.startswith("question_"))
async def check_the_correctness(callback_query: CallbackQuery):
    # Добавление ID сообщения пользователя в список
    tuid = callback_query.message.chat.id
    user_data = sent_message_add_screen_ids[tuid]
    # Добавляем сообщение пользователя
    user_data['user_messages'].append(callback_query.message.message_id)


    # Удаление предыдущих сообщений
    # Удаляем предыдущие сообщения
    await delete_previous_messages(callback_query.message, tuid)

    # Извлекаем данные из callback_data, например, 'question_123_A'
    callback_data = callback_query.data
    parts = callback_data.split('_')  # Разделяем строку по символу '_'

    if len(parts) >= 3:
        question_id = int(parts[1])  # Вторая часть после 'question'
        selected_option = parts[2]  # Третья часть (A, B, C, D)

        # Преобразуем английские буквы в кириллические
        if selected_option == "A":
            selected_option = "А"
        elif selected_option == "B":
            selected_option = "Б"
        elif selected_option == "V":
            selected_option = "В"
        elif selected_option == "G":
            selected_option = "Г"

        # Получаем вопрос и варианты из БД
        question_data = await rq.get_question_and_options(question_id)

        if question_data:
            # Проверяем правильность ответа
            is_correct = await rq.check_answer(question_id, selected_option)

            # Формируем текст для отображения правильности ответа
            if is_correct:
                is_update_rubin = await rq.update_rubies(telegram_id=callback_query.from_user.id, rubies_to_add=1)

                if is_update_rubin:
                    user_id = await rq.get_user_id_by_telegram_id(callback_query.from_user.id)
                    is_update_user_answer = await rq.record_user_answer(
                        user_id=user_id,
                        question_id=question_id,
                        chosen_option=selected_option,
                        is_correct=is_correct,
                        rubies_earned=1)
                    if is_update_user_answer:
                        feedback_text = (f"Ваш ответ ({question_data['correct_option']}) правильный!\n"
                                         f"Вам зачислено +1 💎 рубинов.")
                        photo = utils.PictureForCorrectAnswer
                    else:
                        feedback_text = (
                            f"Произошла ошибка при обновлении истории. Пожалуйста, выйдите из теста и войдите в него снова.")
                else:
                    feedback_text = (f"Произошла ошибка при добавлении рубинов. Пожалуйста, выйдите из теста и войдите в него снова.")
            else:
                user_id = await rq.get_user_id_by_telegram_id(callback_query.from_user.id)
                is_update_user_answer = await rq.record_user_answer(
                    user_id=user_id,
                    question_id=question_id,
                    chosen_option=selected_option,
                    is_correct=is_correct,
                    rubies_earned=0)
                if is_update_user_answer:
                    feedback_text = f"Ваш ответ неправильный! Правильный ответ: {question_data['correct_option']}"
                    photo = utils.PictureForWrongAnswer
                else:
                    feedback_text = (
                        f"Произошла ошибка при обновлении истории. Пожалуйста, выйдите из теста и войдите в него снова.")

            # Формируем текст вопроса и вариантов
            question_text = f"Пара: {question_data['question']}\n" \
                            f"А) {question_data['option_a']}\n" \
                            f"Б) {question_data['option_b']}\n" \
                            f"В) {question_data['option_v']}\n" \
                            f"Г) {question_data['option_g']}\n"

            # Отправляем ответ с результатом и вопросом
            sent_message = await callback_query.message.answer_photo(
                photo=photo,
                caption=f"{question_text}\n_{feedback_text}_",
                reply_markup=kb.next_analogy_question_button(question_id=question_id),
                parse_mode=ParseMode.MARKDOWN
            )
            # Добавляем сообщение бота
            user_data['bot_messages'].append(sent_message.message_id)


@router.callback_query(F.data == 'next_analogy_question')
async def next_analogy_question(callback_query: CallbackQuery):
    await start_analogy_test(callback_query)

#________________________________________________________________________________________

@router.callback_query(F.data == 'take_grammar_ru')
async def start_grammar_test(callback_query: CallbackQuery):
    tuid = callback_query.message.chat.id
    user_data = sent_message_add_screen_ids[tuid]
    # Добавляем сообщение пользователя
    user_data['user_messages'].append(callback_query.message.message_id)

    # Удаляем предыдущие сообщения
    await delete_previous_messages(callback_query.message, tuid)
    telegram_id = callback_query.from_user.id

    count_passed_questions = await rq.count_user_answered_questions(telegram_id=telegram_id, subject_id1=1, subject_id2=3)
    if count_passed_questions >= 50:
        is_vip = await rq.is_vip_user(telegram_id=telegram_id)

        if is_vip:
            # Получаем индекс последнего сданного вопроса
            last_question_index = await rq.get_last_answered_question_index(telegram_id=telegram_id, subject_id=1)

            # Получаем следующий вопрос, основываясь на последнем сданном
            next_question = await rq.get_next_question(last_answered_question_id=last_question_index, subject_id=1)

            if next_question:
                # Если следующий вопрос существует, создаем текст вопроса и вариант ответов
                question_text = (f"*Вопрос:* {next_question['content']}\n\n"
                                 f"_А) {next_question['option_a']}_\n"
                                 f"_Б) {next_question['option_b']}_\n"
                                 f"_В) {next_question['option_v']}_\n"
                                 f"_Г) {next_question['option_g']}_\n")

                # Генерируем клавиатуру с вариантами ответов
                keyboard = kb.generate_answer_keyboard_ru_grammar(
                    question_id=next_question['question_id'],
                    option_a="А",
                    option_b="Б",
                    option_v="В",
                    option_g="Г"
                )

                sent_message = await callback_query.message.answer_photo(
                    photo=utils.PictureForTakeGrammarQuestionRU,
                    caption=question_text,
                    reply_markup=keyboard, # Отправляем сообщение с клавиатурой
                    parse_mode=ParseMode.MARKDOWN
                )
            else:
                # Если нет следующего вопроса, сообщаем пользователю
                sent_message = await callback_query.message.answer_photo(
                    photo=utils.PictureForTakeGrammarQuestionRU,
                    caption="Вы прошли все тесты! Вы можете вернуться позже или начать тест заново. Обратите внимание, "
                            "что при повторном прохождении все данные о ваших пройденных вопросах будут сброшены, "
                            "и вам нужно будет пройти тест заново. Однако количество рубинов останется неизменным.",
                    reply_markup=kb.take_the_test_again_grammar_ru
                )

            # Добавляем сообщение бота
            user_data['bot_messages'].append(sent_message.message_id)
        else:
            sent_message = await callback_query.message.answer_photo(
                photo=utils.PictureForTakeAnalogyQuestionKG,
                caption="Вы достигли лимита 50 вопросов. Чтобы получить доступ к больше чем 4000 вопросам, вы должны "
                        "получить статус VIP. Для этого в личном кабинете выберите кнопку VIP и свяжитесь с админом.",
                reply_markup=kb.to_user_account_ru
            )
            # Добавляем сообщение бота
            user_data['bot_messages'].append(sent_message.message_id)
    else:
        # Получаем индекс последнего сданного вопроса
        last_question_index = await rq.get_last_answered_question_index(telegram_id=telegram_id, subject_id=1)

        # Получаем следующий вопрос, основываясь на последнем сданном
        next_question = await rq.get_next_question(last_answered_question_id=last_question_index, subject_id=1)

        if next_question:
            # Если следующий вопрос существует, создаем текст вопроса и вариант ответов
            question_text = (f"*Вопрос:* {next_question['content']}\n\n"
                             f"_А) {next_question['option_a']}_\n"
                             f"_Б) {next_question['option_b']}_\n"
                             f"_В) {next_question['option_v']}_\n"
                             f"_Г) {next_question['option_g']}_\n")

            # Генерируем клавиатуру с вариантами ответов
            keyboard = kb.generate_answer_keyboard_ru_grammar(
                question_id=next_question['question_id'],
                option_a="А",
                option_b="Б",
                option_v="В",
                option_g="Г"
            )

            sent_message = await callback_query.message.answer_photo(
                photo=utils.PictureForTakeGrammarQuestionRU,
                caption=question_text,
                reply_markup=keyboard,  # Отправляем сообщение с клавиатурой
                parse_mode=ParseMode.MARKDOWN
            )
        else:
            # Если нет следующего вопроса, сообщаем пользователю
            sent_message = await callback_query.message.answer_photo(
                photo=utils.PictureForTakeGrammarQuestionRU,
                caption="Вы прошли все тесты! Вы можете вернуться позже или начать тест заново. Обратите внимание, "
                        "что при повторном прохождении все данные о ваших пройденных вопросах будут сброшены, "
                        "и вам нужно будет пройти тест заново. Однако количество рубинов останется неизменным.",
                reply_markup=kb.take_the_test_again_grammar_ru
            )

        # Добавляем сообщение бота
        user_data['bot_messages'].append(sent_message.message_id)

@router.callback_query(lambda c: c.data.startswith("ru_grammar_question_"))
async def check_the_correctness(callback_query: CallbackQuery):
    # Добавление ID сообщения пользователя в список
    tuid = callback_query.message.chat.id
    user_data = sent_message_add_screen_ids[tuid]
    # Добавляем сообщение пользователя
    user_data['user_messages'].append(callback_query.message.message_id)

    # Удаляем предыдущие сообщения
    await delete_previous_messages(callback_query.message, tuid)

    # Извлекаем данные из callback_data, например, 'question_123_A'
    callback_data = callback_query.data
    parts = callback_data.split('_')  # Разделяем строку по символу '_'

    if len(parts) >= 3:
        question_id = int(parts[3])  # Вторая часть после 'question'
        selected_option = parts[4]  # Третья часть (A, B, C, D)

        # Преобразуем английские буквы в кириллические
        if selected_option == "A":
            selected_option = "А"
        elif selected_option == "B":
            selected_option = "Б"
        elif selected_option == "V":
            selected_option = "В"
        elif selected_option == "G":
            selected_option = "Г"

        # Получаем вопрос и варианты из БД
        question_data = await rq.get_question_and_options(question_id)

        if question_data:
            # Проверяем правильность ответа
            is_correct = await rq.check_answer(question_id, selected_option)

            # Формируем текст для отображения правильности ответа
            if is_correct:
                is_update_rubin = await rq.update_rubies(telegram_id=callback_query.from_user.id, rubies_to_add=1)

                if is_update_rubin:
                    user_id = await rq.get_user_id_by_telegram_id(callback_query.from_user.id)
                    is_update_user_answer = await rq.record_user_answer(
                        user_id=user_id,
                        question_id=question_id,
                        chosen_option=selected_option,
                        is_correct=is_correct,
                        rubies_earned=1)
                    if is_update_user_answer:
                        feedback_text = (f"Ваш ответ ({question_data['correct_option']}) правильный!\n"
                                         f"Вам зачислено +1 💎 рубинов.")
                        photo = utils.PictureForCorrectAnswer
                    else:
                        feedback_text = (
                            f"Произошла ошибка при обновлении истории. Пожалуйста, выйдите из теста и войдите в него снова.")
                else:
                    feedback_text = (f"Произошла ошибка при добавлении рубинов. Пожалуйста, выйдите из теста и войдите в него снова.")
            else:
                user_id = await rq.get_user_id_by_telegram_id(callback_query.from_user.id)
                is_update_user_answer = await rq.record_user_answer(
                    user_id=user_id,
                    question_id=question_id,
                    chosen_option=selected_option,
                    is_correct=is_correct,
                    rubies_earned=0)
                if is_update_user_answer:
                    feedback_text = f"Ваш ответ неправильный! Правильный ответ: {question_data['correct_option']}"
                    photo = utils.PictureForWrongAnswer
                else:
                    feedback_text = (
                        f"Произошла ошибка при обновлении истории. Пожалуйста, выйдите из теста и войдите в него снова.")

            # Формируем текст вопроса и вариантов
            question_text = f"Вопрос: {question_data['question']}\n" \
                            f"А) {question_data['option_a']}\n" \
                            f"Б) {question_data['option_b']}\n" \
                            f"В) {question_data['option_v']}\n" \
                            f"Г) {question_data['option_g']}\n"

            # Отправляем ответ с результатом и вопросом
            sent_message = await callback_query.message.answer_photo(
                photo=photo,
                caption=f"{question_text}\n_{feedback_text}_",
                reply_markup=kb.next_analogy_grammar_button(question_id=question_id),
                parse_mode=ParseMode.MARKDOWN
            )
            # Добавляем сообщение бота
            user_data['bot_messages'].append(sent_message.message_id)

@router.callback_query(F.data == 'next_grammar_question')
async def next_grammar_question(callback_query: CallbackQuery):
    await start_grammar_test(callback_query)



#################################################################################
#                     Passing the test in Kyrgyz                                #
#################################################################################

@router.callback_query(F.data == 'take_test_kg')
async def take_test_kg(callback_query: CallbackQuery):
    tuid = callback_query.message.chat.id
    user_data = sent_message_add_screen_ids[tuid]
    # Добавляем сообщение пользователя
    user_data['user_messages'].append(callback_query.message.message_id)

    # Удаляем предыдущие сообщения
    await delete_previous_messages(callback_query.message, tuid)
    sent_message = await callback_query.message.answer_photo(
        photo=utils.PictureForTakeTheTestKG,
        caption="Кайсы категориядан тест өтөсүз?",
        reply_markup=kb.select_subject_kg
    )
    # Добавляем сообщение бота
    user_data['bot_messages'].append(sent_message.message_id)

# Passing the analogy test in Kyrgyz
@router.callback_query(F.data == 'take_analogy_kg')
async def start_analogy_test_kg(callback_query: CallbackQuery):
    tuid = callback_query.message.chat.id
    user_data = sent_message_add_screen_ids[tuid]
    # Добавляем сообщение пользователя
    user_data['user_messages'].append(callback_query.message.message_id)

    # Удаляем предыдущие сообщения
    await delete_previous_messages(callback_query.message, tuid)
    telegram_id = callback_query.from_user.id

    count_passed_questions = await rq.count_user_answered_questions(telegram_id=telegram_id, subject_id1=2, subject_id2=4)
    if count_passed_questions >= 50:
        is_vip = await rq.is_vip_user(telegram_id=telegram_id)

        if is_vip:
            # Получаем индекс последнего сданного вопроса
            last_question_index = await rq.get_last_answered_question_index(telegram_id=telegram_id, subject_id=4)

            # Получаем следующий вопрос, основываясь на последнем сданном
            next_question = await rq.get_next_question(last_answered_question_id=last_question_index, subject_id=4)

            if next_question:
                # Если следующий вопрос существует, создаем текст вопроса и вариант ответов
                question_text = f"*Жуп:* {next_question['content']}\n"

                # Генерируем клавиатуру с вариантами ответов
                keyboard = kb.generate_answer_keyboard_kg_analogy(
                    question_id=next_question['question_id'],
                    option_a=next_question['option_a'],
                    option_b=next_question['option_b'],
                    option_v=next_question['option_v'],
                    option_g=next_question['option_g']
                )

                sent_message = await callback_query.message.answer_photo(
                    photo=utils.PictureForTakeAnalogyQuestionKG,
                    caption=question_text,
                    reply_markup=keyboard, # Отправляем сообщение с клавиатурой
                    parse_mode=ParseMode.MARKDOWN
                )
            else:
                # Если нет следующего вопроса, сообщаем пользователю
                sent_message = await callback_query.message.answer_photo(
                    photo=utils.PictureForTakeAnalogyQuestionKG,
                    caption="Сиз бардык тесттерди өттүңүз! Кийинчерээк кайталап кирсеңиз болот же тестти кайра баштай аласыз. "
                            "Эскертүү: тестти кайра өткөн учурда, бардык өткөн суроолор боюнча маалыматтар жоголот жана сизге "
                            "тестти кайрадан өтүү керек болот. Бирок рубиндердин саны өзгөрбөйт.",
                    reply_markup=kb.take_the_test_again_analogy_kg
                )

            # Добавляем сообщение бота
            user_data['bot_messages'].append(sent_message.message_id)
        else:
            sent_message = await callback_query.message.answer_photo(
                photo=utils.PictureForTakeAnalogyQuestionKG,
                caption="Сиз 50 суроо тапшырып бүттүңүз. 4000+ суроону тапшырууга мүмкүнчүлүк алуу үчүн VIP колдонуучу "
                        "статусун алыңыз. Алуу үчүн өздүк бөлмөгө кирип, VIP баскычын басып, администрацияга жазыңыз",
                reply_markup=kb.to_user_account_kg
            )
            # Добавляем сообщение бота
            user_data['bot_messages'].append(sent_message.message_id)
    else:
        # Получаем индекс последнего сданного вопроса
        last_question_index = await rq.get_last_answered_question_index(telegram_id=telegram_id, subject_id=4)

        # Получаем следующий вопрос, основываясь на последнем сданном
        next_question = await rq.get_next_question(last_answered_question_id=last_question_index, subject_id=4)

        if next_question:
            # Если следующий вопрос существует, создаем текст вопроса и вариант ответов
            question_text = f"*Жуп:* {next_question['content']}\n"

            # Генерируем клавиатуру с вариантами ответов
            keyboard = kb.generate_answer_keyboard_kg_analogy(
                question_id=next_question['question_id'],
                option_a=next_question['option_a'],
                option_b=next_question['option_b'],
                option_v=next_question['option_v'],
                option_g=next_question['option_g']
            )

            sent_message = await callback_query.message.answer_photo(
                photo=utils.PictureForTakeAnalogyQuestionKG,
                caption=question_text,
                reply_markup=keyboard,  # Отправляем сообщение с клавиатурой
                parse_mode=ParseMode.MARKDOWN
            )
        else:
            # Если нет следующего вопроса, сообщаем пользователю
            sent_message = await callback_query.message.answer_photo(
                photo=utils.PictureForTakeAnalogyQuestionKG,
                caption="Сиз бардык тесттерди өттүңүз! Кийинчерээк кайталап кирсеңиз болот же тестти кайра баштай аласыз. "
                        "Эскертүү: тестти кайра өткөн учурда, бардык өткөн суроолор боюнча маалыматтар жоголот жана сизге "
                        "тестти кайрадан өтүү керек болот. Бирок рубиндердин саны өзгөрбөйт.",
                reply_markup=kb.take_the_test_again_analogy_kg
            )

        # Добавляем сообщение бота
        user_data['bot_messages'].append(sent_message.message_id)


@router.callback_query(lambda c: c.data.startswith("kg_analogy_question_"))
async def check_the_correctness(callback_query: CallbackQuery):
    # Добавление ID сообщения пользователя в список
    tuid = callback_query.message.chat.id
    user_data = sent_message_add_screen_ids[tuid]
    # Добавляем сообщение пользователя
    user_data['user_messages'].append(callback_query.message.message_id)


    # Удаление предыдущих сообщений
    # Удаляем предыдущие сообщения
    await delete_previous_messages(callback_query.message, tuid)

    # Извлекаем данные из callback_data, например, 'question_123_A'
    callback_data = callback_query.data
    parts = callback_data.split('_')  # Разделяем строку по символу '_'

    if len(parts) >= 3:
        question_id = int(parts[3])  # Вторая часть после 'question'
        selected_option = parts[4]  # Третья часть (A, B, C, D)

        # Преобразуем английские буквы в кириллические
        if selected_option == "A":
            selected_option = "А"
        elif selected_option == "B":
            selected_option = "Б"
        elif selected_option == "V":
            selected_option = "В"
        elif selected_option == "G":
            selected_option = "Г"

        # Получаем вопрос и варианты из БД
        question_data = await rq.get_question_and_options(question_id)

        if question_data:
            # Проверяем правильность ответа
            is_correct = await rq.check_answer(question_id, selected_option)

            # Формируем текст для отображения правильности ответа
            if is_correct:
                is_update_rubin = await rq.update_rubies(telegram_id=callback_query.from_user.id, rubies_to_add=1)

                if is_update_rubin:
                    user_id = await rq.get_user_id_by_telegram_id(callback_query.from_user.id)
                    is_update_user_answer = await rq.record_user_answer(
                        user_id=user_id,
                        question_id=question_id,
                        chosen_option=selected_option,
                        is_correct=is_correct,
                        rubies_earned=1)
                    if is_update_user_answer:
                        feedback_text = (f"Сиздин жооп ({question_data['correct_option']}) туура!\n"
                                         f"Сизге +1 💎 рубин кошулду.")
                        photo = utils.PictureForCorrectAnswer
                    else:
                        feedback_text = (
                            f"Тарыхчаны жаңыртууда ката кетти. Сураныч, тесттен чыгып, ага кайрадан кириңиз.")
                else:
                    feedback_text = (f"Рубиндерди кошууда ката кетти. Сураныч, тесттен чыгып, ага кайрадан кириңиз.")
            else:
                user_id = await rq.get_user_id_by_telegram_id(callback_query.from_user.id)
                is_update_user_answer = await rq.record_user_answer(
                    user_id=user_id,
                    question_id=question_id,
                    chosen_option=selected_option,
                    is_correct=is_correct,
                    rubies_earned=0)
                if is_update_user_answer:
                    feedback_text = f"Сиздин жооп туура эмес! Туура жооп: {question_data['correct_option']}"
                    photo = utils.PictureForWrongAnswer
                else:
                    feedback_text = (
                        f"Тарыхчаны жаңыртууда ката кетти. Сураныч, тесттен чыгып, ага кайрадан кириңиз.")

            # Формируем текст вопроса и вариантов
            question_text = f"Жуп: {question_data['question']}\n" \
                            f"А) {question_data['option_a']}\n" \
                            f"Б) {question_data['option_b']}\n" \
                            f"В) {question_data['option_v']}\n" \
                            f"Г) {question_data['option_g']}\n"

            # Отправляем ответ с результатом и вопросом
            sent_message = await callback_query.message.answer_photo(
                photo=photo,
                caption=f"{question_text}\n_{feedback_text}_",
                reply_markup=kb.next_analogy_question_kg_button(question_id=question_id),
                parse_mode=ParseMode.MARKDOWN
            )
            # Добавляем сообщение бота
            user_data['bot_messages'].append(sent_message.message_id)

@router.callback_query(F.data == 'next_analogy_kg_question')
async def next_analogy_kg_question(callback_query: CallbackQuery):
    await start_analogy_test_kg(callback_query)


@router.callback_query(F.data == 'take_grammar_kg')
async def start_grammar_test_kg(callback_query: CallbackQuery):
    tuid = callback_query.message.chat.id
    user_data = sent_message_add_screen_ids[tuid]
    # Добавляем сообщение пользователя
    user_data['user_messages'].append(callback_query.message.message_id)

    # Удаляем предыдущие сообщения
    await delete_previous_messages(callback_query.message, tuid)
    telegram_id = callback_query.from_user.id

    count_passed_questions = await rq.count_user_answered_questions(telegram_id=telegram_id, subject_id1=2, subject_id2=4)
    if count_passed_questions >= 50:
        is_vip = await rq.is_vip_user(telegram_id=telegram_id)

        if is_vip:
            # Получаем индекс последнего сданного вопроса
            last_question_index = await rq.get_last_answered_question_index(telegram_id=telegram_id, subject_id=2)

            # Получаем следующий вопрос, основываясь на последнем сданном
            next_question = await rq.get_next_question(last_answered_question_id=last_question_index, subject_id=2)

            if next_question:
                # Если следующий вопрос существует, создаем текст вопроса и вариант ответов
                question_text = (f"*Суроо:* {next_question['content']}\n\n"
                                 f"_А) {next_question['option_a']}_\n"
                                 f"_Б) {next_question['option_b']}_\n"
                                 f"_В) {next_question['option_v']}_\n"
                                 f"_Г) {next_question['option_g']}_\n")

                # Генерируем клавиатуру с вариантами ответов
                keyboard = kb.generate_answer_keyboard_kg_grammar(
                    question_id=next_question['question_id'],
                    option_a="А",
                    option_b="Б",
                    option_v="В",
                    option_g="Г"
                )

                sent_message = await callback_query.message.answer_photo(
                    photo=utils.PictureForTakeGrammarQuestionKG,
                    caption=question_text,
                    reply_markup=keyboard, # Отправляем сообщение с клавиатурой
                    parse_mode=ParseMode.MARKDOWN
                )
            else:
                # Если нет следующего вопроса, сообщаем пользователю
                sent_message = await callback_query.message.answer_photo(
                    photo=utils.PictureForTakeGrammarQuestionKG,
                    caption="Сиз бардык тесттерди өттүңүз! Кийинчерээк кайталап кирсеңиз болот же тестти кайра баштай аласыз. "
                            "Эскертүү: тестти кайра өткөн учурда, бардык өткөн суроолор боюнча маалыматтар жоголот жана сизге "
                            "тестти кайрадан өтүү керек болот. Бирок рубиндердин саны өзгөрбөйт.",
                    reply_markup=kb.take_the_test_again_grammar_kg
                )

            # Добавляем сообщение бота
            user_data['bot_messages'].append(sent_message.message_id)
        else:
            sent_message = await callback_query.message.answer_photo(
                photo=utils.PictureForTakeAnalogyQuestionKG,
                caption="Сиз 50 суроо тапшырып бүттүңүз. 4000+ суроону тапшырууга мүмкүнчүлүк алуу үчүн VIP колдонуучу "
                        "статусун алыңыз. Алуу үчүн өздүк бөлмөгө кирип, VIP баскычын басып, администрацияга жазыңыз",
                reply_markup=kb.to_user_account_kg
            )
            # Добавляем сообщение бота
            user_data['bot_messages'].append(sent_message.message_id)
    else:
        # Получаем индекс последнего сданного вопроса
        last_question_index = await rq.get_last_answered_question_index(telegram_id=telegram_id, subject_id=2)

        # Получаем следующий вопрос, основываясь на последнем сданном
        next_question = await rq.get_next_question(last_answered_question_id=last_question_index, subject_id=2)

        if next_question:
            # Если следующий вопрос существует, создаем текст вопроса и вариант ответов
            question_text = (f"*Суроо:* {next_question['content']}\n\n"
                             f"_А) {next_question['option_a']}_\n"
                             f"_Б) {next_question['option_b']}_\n"
                             f"_В) {next_question['option_v']}_\n"
                             f"_Г) {next_question['option_g']}_\n")

            # Генерируем клавиатуру с вариантами ответов
            keyboard = kb.generate_answer_keyboard_kg_grammar(
                question_id=next_question['question_id'],
                option_a="А",
                option_b="Б",
                option_v="В",
                option_g="Г"
            )

            sent_message = await callback_query.message.answer_photo(
                photo=utils.PictureForTakeGrammarQuestionKG,
                caption=question_text,
                reply_markup=keyboard,  # Отправляем сообщение с клавиатурой
                parse_mode=ParseMode.MARKDOWN
            )
        else:
            # Если нет следующего вопроса, сообщаем пользователю
            sent_message = await callback_query.message.answer_photo(
                photo=utils.PictureForTakeGrammarQuestionKG,
                caption="Сиз бардык тесттерди өттүңүз! Кийинчерээк кайталап кирсеңиз болот же тестти кайра баштай аласыз. "
                        "Эскертүү: тестти кайра өткөн учурда, бардык өткөн суроолор боюнча маалыматтар жоголот жана сизге "
                        "тестти кайрадан өтүү керек болот. Бирок рубиндердин саны өзгөрбөйт.",
                reply_markup=kb.take_the_test_again_grammar_kg
            )

        # Добавляем сообщение бота
        user_data['bot_messages'].append(sent_message.message_id)



@router.callback_query(lambda c: c.data.startswith("kg_grammar_question_"))
async def check_the_correctness(callback_query: CallbackQuery):
    # Добавление ID сообщения пользователя в список
    tuid = callback_query.message.chat.id
    user_data = sent_message_add_screen_ids[tuid]
    # Добавляем сообщение пользователя
    user_data['user_messages'].append(callback_query.message.message_id)

    # Удаляем предыдущие сообщения
    await delete_previous_messages(callback_query.message, tuid)

    # Извлекаем данные из callback_data, например, 'question_123_A'
    callback_data = callback_query.data
    parts = callback_data.split('_')  # Разделяем строку по символу '_'

    if len(parts) >= 3:
        question_id = int(parts[3])  # Вторая часть после 'question'
        selected_option = parts[4]  # Третья часть (A, B, C, D)

        # Преобразуем английские буквы в кириллические
        if selected_option == "A":
            selected_option = "А"
        elif selected_option == "B":
            selected_option = "Б"
        elif selected_option == "V":
            selected_option = "В"
        elif selected_option == "G":
            selected_option = "Г"

        # Получаем вопрос и варианты из БД
        question_data = await rq.get_question_and_options(question_id)

        if question_data:
            # Проверяем правильность ответа
            is_correct = await rq.check_answer(question_id, selected_option)

            # Формируем текст для отображения правильности ответа
            if is_correct:
                is_update_rubin = await rq.update_rubies(telegram_id=callback_query.from_user.id, rubies_to_add=1)

                if is_update_rubin:
                    user_id = await rq.get_user_id_by_telegram_id(callback_query.from_user.id)
                    is_update_user_answer = await rq.record_user_answer(
                        user_id=user_id,
                        question_id=question_id,
                        chosen_option=selected_option,
                        is_correct=is_correct,
                        rubies_earned=1)
                    if is_update_user_answer:
                        feedback_text = (f"Сиздин жооп ({question_data['correct_option']}) туура!\n"
                                         f"Сизге +1 💎 рубин кошулду.")
                        photo = utils.PictureForCorrectAnswer
                    else:
                        feedback_text = (
                            f"Тарыхчаны жаңыртууда ката кетти. Сураныч, тесттен чыгып, ага кайрадан кириңиз.")
                else:
                    feedback_text = (f"Рубиндерди кошууда ката кетти. Сураныч, тесттен чыгып, ага кайрадан кириңиз.")
            else:
                user_id = await rq.get_user_id_by_telegram_id(callback_query.from_user.id)
                is_update_user_answer = await rq.record_user_answer(
                    user_id=user_id,
                    question_id=question_id,
                    chosen_option=selected_option,
                    is_correct=is_correct,
                    rubies_earned=0)
                if is_update_user_answer:
                    feedback_text = f"Сиздин жооп туура эмес! Туура жооп: {question_data['correct_option']}"
                    photo = utils.PictureForWrongAnswer
                else:
                    feedback_text = (
                        f"Тарыхчаны жаңыртууда ката кетти. Сураныч, тесттен чыгып, ага кайрадан кириңиз.")

            # Формируем текст вопроса и вариантов
            question_text = f"Суроо: {question_data['question']}\n" \
                            f"А) {question_data['option_a']}\n" \
                            f"Б) {question_data['option_b']}\n" \
                            f"В) {question_data['option_v']}\n" \
                            f"Г) {question_data['option_g']}\n"

            # Отправляем ответ с результатом и вопросом
            sent_message = await callback_query.message.answer_photo(
                photo=photo,
                caption=f"{question_text}\n_{feedback_text}_",
                reply_markup=kb.next_grammar_kg_button(question_id=question_id),
                parse_mode=ParseMode.MARKDOWN
            )
            # Добавляем сообщение бота
            user_data['bot_messages'].append(sent_message.message_id)

@router.callback_query(F.data == 'next_grammar_question_kg')
async def next_grammar_question_kg(callback_query: CallbackQuery):
    await start_grammar_test_kg(callback_query)

# Take the russian analogy test again
@router.callback_query(F.data == 'take_the_test_again_analogy_ru')
async def take_the_test_analogy_ru(callback_query: CallbackQuery, state: FSMContext):
    tuid = callback_query.message.chat.id
    user_data = sent_message_add_screen_ids[tuid]
    # Добавляем сообщение пользователя
    user_data['user_messages'].append(callback_query.message.message_id)

    # Удаляем предыдущие сообщения
    await delete_previous_messages(callback_query.message, tuid)
    sent_message = await callback_query.message.answer(
        text="Если вы действительно хотите сбросить прогресс и начать тест заново, "
             "введите текущее время в формате чч:мм, например, 12:34.",
        reply_markup=kb.to_user_account_ru
    )

    await state.set_state(st.TakeTheRussianAnalogyTestAgain.enter_time)
    # Добавляем сообщение бота
    user_data['bot_messages'].append(sent_message.message_id)

@router.message(st.TakeTheRussianAnalogyTestAgain.enter_time)
async def take_the_test_analogy_ru_finish(message: Message, state: FSMContext):
    tuid = message.chat.id
    user_data = sent_message_add_screen_ids[tuid]
    # Добавляем сообщение пользователя
    user_data['user_messages'].append(message.message_id)

    # Удаляем предыдущие сообщения
    await delete_previous_messages(message, tuid)
    user_input = message.text

    current_time = datetime.now()
    current_hour = current_time.strftime('%H')
    current_minute = current_time.strftime('%M')
    expected_time = f"{current_hour}:{current_minute}"
    user_telegram_id = message.from_user.id

    # Проверка времени
    if user_input == expected_time:
        is_deleted_data = await rq.delete_completed_questions(subject_id=3, telegram_id=user_telegram_id)
        if is_deleted_data:
            sent_message = await message.answer(
                text="Ваши данные о прохождении теста сброшены. Вы можете начать тест заново.",
                reply_markup=kb.to_user_account_ru
            )
            # Добавляем сообщение бота
            user_data['bot_messages'].append(sent_message.message_id)
        else:
            sent_message = await message.answer(
                text="Произошла ошибка при сбросе данных о прохождении теста. Пожалуйста, попробуйте снова.",
                reply_markup=kb.to_user_account_ru
            )
            # Добавляем сообщение бота
            user_data['bot_messages'].append(sent_message.message_id)
    else:
        sent_message = await message.answer(
            text="Неверное время. Сброс теста отменен.",
            reply_markup=kb.to_user_account_ru
        )
        # Добавляем сообщение бота
        user_data['bot_messages'].append(sent_message.message_id)
    await state.clear()


# Take the russian grammar test again
@router.callback_query(F.data == 'take_the_test_again_grammar_ru')
async def take_the_test_grammar_ru(callback_query: CallbackQuery, state: FSMContext):
    tuid = callback_query.message.chat.id
    user_data = sent_message_add_screen_ids[tuid]
    # Добавляем сообщение пользователя
    user_data['user_messages'].append(callback_query.message.message_id)

    # Удаляем предыдущие сообщения
    await delete_previous_messages(callback_query.message, tuid)
    sent_message = await callback_query.message.answer(
        text="Если вы действительно хотите сбросить прогресс и начать тест заново, "
             "введите текущее время в формате чч:мм, например, 12:34.",
        reply_markup=kb.to_user_account_ru
    )

    await state.set_state(st.TakeTheRussianGrammarTestAgain.enter_time)
    # Добавляем сообщение бота
    user_data['bot_messages'].append(sent_message.message_id)

@router.message(st.TakeTheRussianGrammarTestAgain.enter_time)
async def take_the_test_grammar_ru_finish(message: Message, state: FSMContext):
    tuid = message.chat.id
    user_data = sent_message_add_screen_ids[tuid]
    # Добавляем сообщение пользователя
    user_data['user_messages'].append(message.message_id)

    # Удаляем предыдущие сообщения
    await delete_previous_messages(message, tuid)
    user_input = message.text

    current_time = datetime.now()
    current_hour = current_time.strftime('%H')
    current_minute = current_time.strftime('%M')
    expected_time = f"{current_hour}:{current_minute}"
    user_telegram_id = message.from_user.id

    # Проверка времени
    if user_input == expected_time:
        is_deleted_data = await rq.delete_completed_questions(subject_id=1, telegram_id=user_telegram_id)
        if is_deleted_data:
            sent_message = await message.answer(
                text="Ваши данные о прохождении теста сброшены. Вы можете начать тест заново.",
                reply_markup=kb.to_user_account_ru
            )
            # Добавляем сообщение бота
            user_data['bot_messages'].append(sent_message.message_id)
        else:
            sent_message = await message.answer(
                text="Произошла ошибка при сбросе данных о прохождении теста. Пожалуйста, попробуйте снова.",
                reply_markup=kb.to_user_account_ru
            )
            # Добавляем сообщение бота
            user_data['bot_messages'].append(sent_message.message_id)
    else:
        sent_message = await message.answer(
            text="Неверное время. Сброс теста отменен.",
            reply_markup=kb.to_user_account_ru
        )
        # Добавляем сообщение бота
        user_data['bot_messages'].append(sent_message.message_id)
    await state.clear()

# Take the kyrgyz analogy test again
@router.callback_query(F.data == 'take_the_test_again_analogy_kg')
async def take_the_test_analogy_kg(callback_query: CallbackQuery, state: FSMContext):
    tuid = callback_query.message.chat.id
    user_data = sent_message_add_screen_ids[tuid]
    # Добавляем сообщение пользователя
    user_data['user_messages'].append(callback_query.message.message_id)

    # Удаляем предыдущие сообщения
    await delete_previous_messages(callback_query.message, tuid)
    sent_message = await callback_query.message.answer(
        text="Эгерде сиз чын эле прогрессти өчүрүп, тестти кайра баштагыңыз келсе, "
             "анда учурдагы убакытты саат:мүнөт форматында жазыңыз, мисалы, 12:34.",
        reply_markup=kb.to_user_account_kg
    )

    await state.set_state(st.TakeTheKyrgyzAnalogyTestAgain.enter_time)
    # Добавляем сообщение бота
    user_data['bot_messages'].append(sent_message.message_id)

@router.message(st.TakeTheKyrgyzAnalogyTestAgain.enter_time)
async def take_the_test_analogy_kg_finish(message: Message, state: FSMContext):
    tuid = message.chat.id
    user_data = sent_message_add_screen_ids[tuid]
    # Добавляем сообщение пользователя
    user_data['user_messages'].append(message.message_id)

    # Удаляем предыдущие сообщения
    await delete_previous_messages(message, tuid)
    user_input = message.text

    current_time = datetime.now()
    current_hour = current_time.strftime('%H')
    current_minute = current_time.strftime('%M')
    expected_time = f"{current_hour}:{current_minute}"
    user_telegram_id = message.from_user.id

    # Проверка времени
    if user_input == expected_time:
        is_deleted_data = await rq.delete_completed_questions(subject_id=4, telegram_id=user_telegram_id)
        if is_deleted_data:
            sent_message = await message.answer(
                text="Сиздин өткөн тесттер тууралуу маалыматыңыз өчүрүлдү. Сиз тестти кайра баштасаңыз болот.",
                reply_markup=kb.to_user_account_kg
            )
            # Добавляем сообщение бота
            user_data['bot_messages'].append(sent_message.message_id)
        else:
            sent_message = await message.answer(
                text="Сиздин өткөн тесттер тууралуу маалыматты өчүрүүдө ката кетти. Кайрадан аракет кылып көрүңүз.",
                reply_markup=kb.to_user_account_kg
            )
            # Добавляем сообщение бота
            user_data['bot_messages'].append(sent_message.message_id)
    else:
        sent_message = await message.answer(
            text="Убакытты туура эмес жаздыңыз, өткөн тесттер тууралуу маалымат өчүрүлгөн жок.",
            reply_markup=kb.to_user_account_kg
        )
        # Добавляем сообщение бота
        user_data['bot_messages'].append(sent_message.message_id)
    await state.clear()


# Take the kyrgyz grammar test again
@router.callback_query(F.data == 'take_the_test_again_grammar_kg')
async def take_the_test_grammar_kg(callback_query: CallbackQuery, state: FSMContext):
    tuid = callback_query.message.chat.id
    user_data = sent_message_add_screen_ids[tuid]
    # Добавляем сообщение пользователя
    user_data['user_messages'].append(callback_query.message.message_id)

    # Удаляем предыдущие сообщения
    await delete_previous_messages(callback_query.message, tuid)
    sent_message = await callback_query.message.answer(
        text="Эгерде сиз чын эле прогрессти өчүрүп, тестти кайра баштагыңыз келсе, "
             "анда учурдагы убакытты саат:мүнөт форматында жазыңыз, мисалы, 12:34.",
        reply_markup=kb.to_user_account_kg
    )

    await state.set_state(st.TakeTheKyrgyzGrammarTestAgain.enter_time)
    # Добавляем сообщение бота
    user_data['bot_messages'].append(sent_message.message_id)

@router.message(st.TakeTheKyrgyzGrammarTestAgain.enter_time)
async def take_the_test_grammar_kg_finish(message: Message, state: FSMContext):
    tuid = message.chat.id
    user_data = sent_message_add_screen_ids[tuid]
    # Добавляем сообщение пользователя
    user_data['user_messages'].append(message.message_id)

    # Удаляем предыдущие сообщения
    await delete_previous_messages(message, tuid)
    user_input = message.text

    current_time = datetime.now()
    current_hour = current_time.strftime('%H')
    current_minute = current_time.strftime('%M')
    expected_time = f"{current_hour}:{current_minute}"
    user_telegram_id = message.from_user.id

    # Проверка времени
    if user_input == expected_time:
        is_deleted_data = await rq.delete_completed_questions(subject_id=2, telegram_id=user_telegram_id)
        if is_deleted_data:
            sent_message = await message.answer(
                text="Сиздин өткөн тесттер тууралуу маалыматыңыз өчүрүлдү. Сиз тестти кайра баштасаңыз болот.",
                reply_markup=kb.to_user_account_kg
            )
            # Добавляем сообщение бота
            user_data['bot_messages'].append(sent_message.message_id)
        else:
            sent_message = await message.answer(
                text="Сиздин өткөн тесттер тууралуу маалыматты өчүрүүдө ката кетти. Кайрадан аракет кылып көрүңүз.",
                reply_markup=kb.to_user_account_kg
            )
            # Добавляем сообщение бота
            user_data['bot_messages'].append(sent_message.message_id)
    else:
        sent_message = await message.answer(
            text="Убакытты туура эмес жаздыңыз, өткөн тесттер тууралуу маалымат өчүрүлгөн жок.",
            reply_markup=kb.to_user_account_kg
        )
        # Добавляем сообщение бота
        user_data['bot_messages'].append(sent_message.message_id)
    await state.clear()

@router.callback_query(lambda c: c.data.startswith("analysis_of_the_issue_"))
async def analysis_of_the_issue(callback_query: CallbackQuery):
    # take_the_test_again_analogy_kg_3
    tuid = callback_query.message.chat.id
    user_data = sent_message_add_screen_ids[tuid]
    # Добавляем сообщение пользователя
    user_data['user_messages'].append(callback_query.message.message_id)


    callback_data = callback_query.data
    parts = callback_data.split('_')
    question_id = int(parts[6])
    question_type = parts[5]
    question_language = parts[4]
    explanation_text_for_user = ""

    is_explanation = await rq.check_explanation_exists(question_id=question_id)

    if not is_explanation:
        if question_language == "kg":
            question_data = await rq.get_question_and_options(question_id)
            if question_type == "analogy":
                if question_data:
                    question_text = f"Негизги жуп: {question_data['question']}\n" \
                                    f"А) {question_data['option_a']}\n" \
                                    f"Б) {question_data['option_b']}\n" \
                                    f"В) {question_data['option_v']}\n" \
                                    f"Г) {question_data['option_g']}\n\n"\
                                    f"Туура жооп: {question_data['correct_option']}"
                    explanation_text_for_user += question_text
                    prompt_for_gpt = (f"{utils.PromptForChatGPTForKyrgyzAnalogyQuestion}\n\n"
                                      f"{question_text}\n\n"
                                      f"{utils.PromptForChatGPTForKyrgyzAnalogyQuestionEnd}")

                    response = await gpt.get_chatgpt_response(prompt_for_gpt)
                    if response == "Произошла ошибка при получении ответа от ChatGPT.":
                        explanation_text_for_user += "\n\n" + ("Жооптун түшүндүрмөсүн алууда ката кетти. Артка чыгып, "
                                                               "кайра кирип көрүңүз. Эгер, анда дагы болбосо, админге "
                                                               "жазыңыз.")
                    else:
                        explanation_text_for_user += "\n\n" + response
                        await rq.update_explanation_by_question_id(question_id=question_id, explanation_text=response)
            elif question_type == "grammar":
                if question_data:
                    question_text = f"Суроо: {question_data['question']}\n" \
                                    f"А) {question_data['option_a']}\n" \
                                    f"Б) {question_data['option_b']}\n" \
                                    f"В) {question_data['option_v']}\n" \
                                    f"Г) {question_data['option_g']}\n\n" \
                                    f"Туура жооп: {question_data['correct_option']}"
                    explanation_text_for_user += question_text
                    prompt_for_gpt = (f"{utils.PromptForChatGPTForKyrgyzGrammarQuestion}\n\n"
                                      f"{question_text}\n\n"
                                      f"{utils.PromptForChatGPTForKyrgyzGrammarQuestionEnd}")

                    response = await gpt.get_chatgpt_response(prompt_for_gpt)
                    if response == "Произошла ошибка при получении ответа от ChatGPT.":
                        explanation_text_for_user += "\n\n" + ("Жооптун түшүндүрмөсүн алууда ката кетти. Артка чыгып, "
                                                               "кайра кирип көрүңүз. Эгер, анда дагы болбосо, админге "
                                                               "жазыңыз.")
                    else:
                        explanation_text_for_user += "\n\n" + response
                        await rq.update_explanation_by_question_id(question_id=question_id, explanation_text=response)
        elif question_language == "ru":
            question_data = await rq.get_question_and_options(question_id)
            if question_type == "analogy":
                if question_data:
                    question_text = f"Основная пара: {question_data['question']}\n" \
                                    f"А) {question_data['option_a']}\n" \
                                    f"Б) {question_data['option_b']}\n" \
                                    f"В) {question_data['option_v']}\n" \
                                    f"Г) {question_data['option_g']}\n\n"\
                                    f"Правильный ответ: {question_data['correct_option']}"
                    explanation_text_for_user += question_text
                    prompt_for_gpt = (f"{utils.PromptForChatGPTForRussianAnalogyQuestion}\n\n"
                                      f"{question_text}\n\n"
                                      f"{utils.PromptForChatGPTForRussianAnalogyQuestionEnd}")

                    response = await gpt.get_chatgpt_response(prompt_for_gpt)
                    if response == "Произошла ошибка при получении ответа от ChatGPT.":
                        explanation_text_for_user += "\n\n" + ("Произошла ошибка при получении объяснения ответа. "
                                                               "Вернитесь к вопросу и попробуйте войти еще раз. "
                                                               "Если нет, напишите администратору.")
                    else:
                        explanation_text_for_user += "\n\n" + response
                        await rq.update_explanation_by_question_id(question_id=question_id, explanation_text=response)
            elif question_type == "grammar":
                if question_data:
                    question_text = f"Вопрос: {question_data['question']}\n" \
                                    f"А) {question_data['option_a']}\n" \
                                    f"Б) {question_data['option_b']}\n" \
                                    f"В) {question_data['option_v']}\n" \
                                    f"Г) {question_data['option_g']}\n\n" \
                                    f"Правильный ответ: {question_data['correct_option']}"
                    explanation_text_for_user += question_text
                    prompt_for_gpt = (f"{utils.PromptForChatGPTForRussianGrammarQuestion}\n\n"
                                      f"{question_text}\n\n"
                                      f"{utils.PromptForChatGPTForRussianGrammarQuestionEnd}")

                    response = await gpt.get_chatgpt_response(prompt_for_gpt)
                    if response == "Произошла ошибка при получении ответа от ChatGPT.":
                        explanation_text_for_user += "\n\n" + ("Произошла ошибка при получении объяснения ответа. "
                                                               "Вернитесь к вопросу и попробуйте войти еще раз. "
                                                               "Если нет, напишите администратору.")
                    else:
                        explanation_text_for_user += "\n\n" + response
                        await rq.update_explanation_by_question_id(question_id=question_id, explanation_text=response)
        # Удаляем предыдущие сообщения
        await delete_previous_messages(callback_query.message, tuid)
        sent_message = await callback_query.message.answer(
            text=explanation_text_for_user,
            reply_markup=kb.go_to_question_result(question_id=question_id, question_type=question_type,
                                                  question_lenguage=question_language)
        )
        # Добавляем сообщение бота
        user_data['bot_messages'].append(sent_message.message_id)
    else:
        explanation = await rq.get_explanation_by_question_id(question_id=question_id)
        if question_language == "kg":
            question_data = await rq.get_question_and_options(question_id)
            if question_type == "analogy":
                if question_data:
                    question_text = f"Негизги жуп: {question_data['question']}\n" \
                                    f"А) {question_data['option_a']}\n" \
                                    f"Б) {question_data['option_b']}\n" \
                                    f"В) {question_data['option_v']}\n" \
                                    f"Г) {question_data['option_g']}\n\n" \
                                    f"Туура жооп: {question_data['correct_option']}"
                    explanation_text_for_user += question_text
                    explanation_text_for_user += "\n\n" + explanation
            elif question_type == "grammar":
                if question_data:
                    question_text = f"Суроо: {question_data['question']}\n" \
                                    f"А) {question_data['option_a']}\n" \
                                    f"Б) {question_data['option_b']}\n" \
                                    f"В) {question_data['option_v']}\n" \
                                    f"Г) {question_data['option_g']}\n\n" \
                                    f"Туура жооп: {question_data['correct_option']}"
                    explanation_text_for_user += question_text
                    explanation_text_for_user += "\n\n" + explanation

        elif question_language == "ru":
            question_data = await rq.get_question_and_options(question_id)
            if question_type == "analogy":
                if question_data:
                    question_text = f"Основная пара: {question_data['question']}\n" \
                                    f"А) {question_data['option_a']}\n" \
                                    f"Б) {question_data['option_b']}\n" \
                                    f"В) {question_data['option_v']}\n" \
                                    f"Г) {question_data['option_g']}\n\n" \
                                    f"Правильный ответ: {question_data['correct_option']}"
                    explanation_text_for_user += question_text
                    explanation_text_for_user += "\n\n" + explanation
            elif question_type == "grammar":
                if question_data:
                    question_text = f"Вопрос: {question_data['question']}\n" \
                                    f"А) {question_data['option_a']}\n" \
                                    f"Б) {question_data['option_b']}\n" \
                                    f"В) {question_data['option_v']}\n" \
                                    f"Г) {question_data['option_g']}\n\n" \
                                    f"Правильный ответ: {question_data['correct_option']}"
                    explanation_text_for_user += question_text
                    explanation_text_for_user += "\n\n" + explanation
        # Удаляем предыдущие сообщения
        await delete_previous_messages(callback_query.message, tuid)
        sent_message = await callback_query.message.answer(
            text=explanation_text_for_user,
            reply_markup=kb.go_to_question_result(question_id=question_id, question_type=question_type,
                                                  question_lenguage=question_language)
        )
        # Добавляем сообщение бота
        user_data['bot_messages'].append(sent_message.message_id)


@router.callback_query(lambda c: c.data.startswith("go_to_question_result_"))
async def go_to_question_result(callback_query: CallbackQuery):
    tuid = callback_query.message.chat.id
    user_data = sent_message_add_screen_ids[tuid]
    # Добавляем сообщение пользователя
    user_data['user_messages'].append(callback_query.message.message_id)

    # Удаляем предыдущие сообщения
    await delete_previous_messages(callback_query.message, tuid)
    telegram_id = callback_query.from_user.id
    # go_to_question_result_analogy_kg_12
    callback_data = callback_query.data
    parts = callback_data.split('_')
    question_id = int(parts[6])
    question_type = parts[4]
    question_language = parts[5]

    question_data = await rq.get_question_and_options(question_id)
    is_correct = await rq.check_user_answer_correct(question_id=question_id, user_telegram_id=telegram_id)

    if question_language == 'kg':
        if question_type == 'analogy':
            question_text = f"Жуп: {question_data['question']}\n" \
                            f"А) {question_data['option_a']}\n" \
                            f"Б) {question_data['option_b']}\n" \
                            f"В) {question_data['option_v']}\n" \
                            f"Г) {question_data['option_g']}\n"
            if is_correct:
                feedback_text = (f"Сиздин жооп ({question_data['correct_option']}) туура!\n"
                                 f"Сизге +1 💎 рубин кошулду.")
                photo = utils.PictureForCorrectAnswer
            else:
                feedback_text = f"Сиздин жооп туура эмес! Туура жооп: {question_data['correct_option']}"
                photo = utils.PictureForWrongAnswer
            sent_message = await callback_query.message.answer_photo(
                photo=photo,
                caption=f"{question_text}\n_{feedback_text}_",
                reply_markup=kb.next_analogy_question_kg_button(question_id=question_id),
                parse_mode=ParseMode.MARKDOWN
            )
            # Добавляем сообщение бота
            user_data['bot_messages'].append(sent_message.message_id)
        elif question_type == 'grammar':
            question_text = f"Суроо: {question_data['question']}\n" \
                            f"А) {question_data['option_a']}\n" \
                            f"Б) {question_data['option_b']}\n" \
                            f"В) {question_data['option_v']}\n" \
                            f"Г) {question_data['option_g']}\n"
            if is_correct:
                feedback_text = (f"Сиздин жооп ({question_data['correct_option']}) туура!\n"
                                 f"Сизге +1 💎 рубин кошулду.")
                photo = utils.PictureForCorrectAnswer
            else:
                feedback_text = f"Сиздин жооп туура эмес! Туура жооп: {question_data['correct_option']}"
                photo = utils.PictureForWrongAnswer
            sent_message = await callback_query.message.answer_photo(
                photo=photo,
                caption=f"{question_text}\n_{feedback_text}_",
                reply_markup=kb.next_grammar_kg_button(question_id=question_id),
                parse_mode=ParseMode.MARKDOWN
            )
            # Добавляем сообщение бота
            user_data['bot_messages'].append(sent_message.message_id)
    elif question_language == 'ru':
        if question_type == 'analogy':
            question_text = f"Пара: {question_data['question']}\n" \
                            f"А) {question_data['option_a']}\n" \
                            f"Б) {question_data['option_b']}\n" \
                            f"В) {question_data['option_v']}\n" \
                            f"Г) {question_data['option_g']}\n"
            if is_correct:
                feedback_text = (f"Ваш ответ ({question_data['correct_option']}) правильный!\n"
                                 f"Вам зачислено +1 💎 рубинов.")
                photo = utils.PictureForCorrectAnswer
            else:
                feedback_text = f"Ваш ответ неправильный! Правильный ответ: {question_data['correct_option']}"
                photo = utils.PictureForWrongAnswer
            sent_message = await callback_query.message.answer_photo(
                photo=photo,
                caption=f"{question_text}\n_{feedback_text}_",
                reply_markup=kb.next_analogy_question_button(question_id=question_id),
                parse_mode=ParseMode.MARKDOWN
            )
            # Добавляем сообщение бота
            user_data['bot_messages'].append(sent_message.message_id)
        elif question_type == 'grammar':
            question_text = f"Вопрос: {question_data['question']}\n" \
                            f"А) {question_data['option_a']}\n" \
                            f"Б) {question_data['option_b']}\n" \
                            f"В) {question_data['option_v']}\n" \
                            f"Г) {question_data['option_g']}\n"
            if is_correct:
                feedback_text = (f"Ваш ответ ({question_data['correct_option']}) правильный!\n"
                                 f"Вам зачислено +1 💎 рубинов.")
                photo = utils.PictureForCorrectAnswer
            else:
                feedback_text = f"Ваш ответ неправильный! Правильный ответ: {question_data['correct_option']}"
                photo = utils.PictureForWrongAnswer
            sent_message = await callback_query.message.answer_photo(
                photo=photo,
                caption=f"{question_text}\n_{feedback_text}_",
                reply_markup=kb.next_analogy_grammar_button(question_id=question_id),
                parse_mode=ParseMode.MARKDOWN
            )
            # Добавляем сообщение бота
            user_data['bot_messages'].append(sent_message.message_id)

# We get the current time in the required time zone
def get_current_time():
    tz = pytz.timezone('Asia/Bishkek')
    return datetime.now(tz)

def calculate_time_difference(start: datetime, finish: datetime) -> float:
    # Вычисляем разницу между финишем и стартом
    time_difference = finish - start
    # Возвращаем результат в секундах с микросекундами
    return time_difference.total_seconds()

#################################################################################
#                        Duel in kyrgyz language                                #
#################################################################################

@router.callback_query(F.data == 'duel_kg')
async def duel_kg(callback_query: CallbackQuery):
    tuid = callback_query.message.chat.id
    user_data = sent_message_add_screen_ids[tuid]
    # Добавляем сообщение пользователя
    user_data['user_messages'].append(callback_query.message.message_id)

    # Удаляем предыдущие сообщения
    await delete_previous_messages(callback_query.message, tuid)

    sent_message = await callback_query.message.answer_photo(
        photo=utils.PictureForDuel,
        caption=f'\n<a href="https://telegra.ph/Bottogu-Duehl-funkciyasy-Rubinder-%D2%AFch%D2%AFn-zharyshy%D2%A3yz-zhana-eh%D2%A3-mykty-ehkeni%D2%A3izdi-k%D3%A9rs%D3%A9t%D2%AF%D2%A3%D2%AFz-11-14">Дуэль деген эмне?</a> 👈',
        reply_markup=kb.duel_menu_kg,
        parse_mode=ParseMode.HTML
    )

    # Добавляем сообщение бота
    user_data['bot_messages'].append(sent_message.message_id)


@router.callback_query(F.data == 'duel_with_random_kg')
async def duel_with_random_kg(callback_query: CallbackQuery, state: FSMContext):
    tuid = callback_query.message.chat.id
    user_data = sent_message_add_screen_ids[tuid]
    # Добавляем сообщение пользователя
    user_data['user_messages'].append(callback_query.message.message_id)

    # Удаляем предыдущие сообщения
    await delete_previous_messages(callback_query.message, tuid)
    telegram_id = callback_query.from_user.id

    is_vip = await rq.is_vip_user(telegram_id=telegram_id)

    if is_vip:
        has_rubies = await rq.has_minimum_rubies(telegram_id=telegram_id)

        if has_rubies:
            is_duel = await rq.has_unfinished_duels(telegram_id=telegram_id)

            if not is_duel:
                count_duels_with_opponent = await rq.count_duels_with_opponent_pending(telegram_id=telegram_id)
                if count_duels_with_opponent <= 4:
                    await state.update_data(user_type="creator")
                    question_ids = await rq.get_random_questions_by_subjects(subject_id1=2, subject_id2=4)
                    await duel_first_question_kg(callback_query, question_ids, state)
                else:
                    sent_message = await callback_query.message.answer_photo(
                        photo=utils.PictureForDuel,
                        caption="Сиз 5 дуэль ачып койдуңуз, аларды эч ким өтө элек.\n"
                                "_Жок дегенде бирөөн башка бирөө өткөн соң дуэль ача аласыз._",
                        reply_markup=kb.to_user_account_kg,
                            parse_mode=ParseMode.MARKDOWN
                    )
                    # Добавляем сообщение бота
                    user_data['bot_messages'].append(sent_message.message_id)
            else:
                duel_id = await rq.update_opponent_in_oldest_duel(telegram_id=telegram_id)
                if duel_id:
                    question_ids = await rq.get_duel_questions(duel_id=duel_id)
                    if question_ids is None:
                        sent_message = await callback_query.message.answer_photo(
                            photo=utils.PictureForDuel,
                            caption="Дуэлдин суроолорун алууда ката кетти.\n"
                                    "Башынан кирип көрүңүз.",
                            reply_markup=kb.to_user_account_kg
                        )
                        # Добавляем сообщение бота
                        user_data['bot_messages'].append(sent_message.message_id)
                    else:
                        await state.update_data(user_type="opponent", duel_id=duel_id)
                        # Проверка и преобразование в list[int] при необходимости
                        if isinstance(question_ids, str):
                            question_ids = json.loads(question_ids)
                        await duel_first_question_kg(callback_query, question_ids, state)
                else:
                    count_duels_with_opponent = await rq.count_duels_with_opponent_pending(telegram_id=telegram_id)
                    if count_duels_with_opponent <= 4:
                        await state.update_data(user_type="creator")
                        question_ids = await rq.get_random_questions_by_subjects(subject_id1=2, subject_id2=4)
                        await duel_first_question_kg(callback_query, question_ids, state)
                    else:
                        sent_message = await callback_query.message.answer_photo(
                            photo=utils.PictureForDuel,
                            caption="Сиз 5 дуэль ачып койдуңуз, аларды эч ким өтө элек.\n"
                                    "_Жок дегенде бирөөн башка бирөө өткөн соң дуэль ача аласыз._",
                            reply_markup=kb.to_user_account_kg,
                            parse_mode=ParseMode.MARKDOWN
                        )
                        # Добавляем сообщение бота
                        user_data['bot_messages'].append(sent_message.message_id)
        else:
            sent_message = await callback_query.message.answer_photo(
                photo=utils.PictureForDuel,
                caption="Сизде дуэлге катышуу үчүн рубин жетишсиз\n"
                        "Жок дегенде 10 рубин болуу керек.",
                reply_markup=kb.to_user_account_kg
            )
            # Добавляем сообщение бота
            user_data['bot_messages'].append(sent_message.message_id)
    else:
        sent_message = await callback_query.message.answer_photo(
            photo=utils.PictureForDuel,
            caption="Боттун башка колдонуучулары менен дуэлде атаандашып, ойноо үчүн сизге VIP статус керек. "
                    "VIP статусту алуу үчүн өздүк бөлмөгө кирип, VIP баскычын басып, админге жазыңыз.",
            reply_markup=kb.to_user_account_kg
        )
        # Добавляем сообщение бота
        user_data['bot_messages'].append(sent_message.message_id)

async def duel_first_question_kg(callback_query, question_ids: list[int], state: FSMContext):
    tuid = callback_query.message.chat.id
    user_data = sent_message_add_screen_ids[tuid]
    question_id = question_ids[0]
    start_time = get_current_time()
    question_data = await rq.get_question_and_options(question_id=question_id)
    await state.update_data(question_ids=question_ids, score=0, start_time=start_time)

    question_text = f"Суроо 1: *{question_data['question']}*\n" \
                    f"А) {question_data['option_a']}\n" \
                    f"Б) {question_data['option_b']}\n" \
                    f"В) {question_data['option_v']}\n" \
                    f"Г) {question_data['option_g']}\n"

    sent_message = await callback_query.message.answer_photo(
        photo=utils.PictureForDuel,
        caption=question_text,
        reply_markup=kb.duel_question_keyboard_kg(question_id=question_id, numerator=1),
        parse_mode=ParseMode.MARKDOWN
    )
    # Добавляем сообщение бота
    user_data['bot_messages'].append(sent_message.message_id)


@router.callback_query(lambda c: c.data and c.data.startswith("duel_question_kg_1_"))
async def duel_second_question_kg(callback_query: CallbackQuery, state: FSMContext):
    tuid = callback_query.message.chat.id
    user_data = sent_message_add_screen_ids[tuid]
    # Добавляем сообщение пользователя
    user_data['user_messages'].append(callback_query.message.message_id)

    # Удаляем предыдущие сообщения
    await delete_previous_messages(callback_query.message, tuid)
    # duel_question_kg_1_12_a
    callback_data = callback_query.data
    parts = callback_data.split('_')
    question_id = int(parts[4])
    selected_option = parts[5]

    if selected_option == "a":
        selected_option = "А"
    elif selected_option == "b":
        selected_option = "Б"
    elif selected_option == "v":
        selected_option = "В"
    elif selected_option == "g":
        selected_option = "Г"


    is_correct = await rq.check_answer(question_id, selected_option)

    data = await state.get_data()

    if is_correct:
        score = data['score']
        score = score + 1
        await state.update_data(score=score)

    next_question_ids = data['question_ids']
    next_question_id = next_question_ids[1]


    question_data = await rq.get_question_and_options(question_id=next_question_id)

    question_text = f"Суроо 2: *{question_data['question']}*\n" \
                    f"А) {question_data['option_a']}\n" \
                    f"Б) {question_data['option_b']}\n" \
                    f"В) {question_data['option_v']}\n" \
                    f"Г) {question_data['option_g']}\n"

    sent_message = await callback_query.message.answer_photo(
        photo=utils.PictureForDuel,
        caption=question_text,
        reply_markup=kb.duel_question_keyboard_kg(question_id=next_question_id, numerator=2),
        parse_mode=ParseMode.MARKDOWN
    )
    # Добавляем сообщение бота
    user_data['bot_messages'].append(sent_message.message_id)


@router.callback_query(lambda c: c.data and c.data.startswith("duel_question_kg_2_"))
async def duel_third_question_kg(callback_query: CallbackQuery, state: FSMContext):
    tuid = callback_query.message.chat.id
    user_data = sent_message_add_screen_ids[tuid]
    # Добавляем сообщение пользователя
    user_data['user_messages'].append(callback_query.message.message_id)

    # Удаляем предыдущие сообщения
    await delete_previous_messages(callback_query.message, tuid)
    # duel_question_kg_1_12_a
    callback_data = callback_query.data
    parts = callback_data.split('_')
    question_id = int(parts[4])
    selected_option = parts[5]


    if selected_option == "a":
        selected_option = "А"
    elif selected_option == "b":
        selected_option = "Б"
    elif selected_option == "v":
        selected_option = "В"
    elif selected_option == "g":
        selected_option = "Г"

    is_correct = await rq.check_answer(question_id, selected_option)

    data = await state.get_data()

    if is_correct:
        score = data['score']
        score = score + 1
        await state.update_data(score=score)

    next_question_ids = data['question_ids']
    next_question_id = next_question_ids[2]


    question_data = await rq.get_question_and_options(question_id=next_question_id)

    question_text = f"Суроо 3: *{question_data['question']}*\n" \
                    f"А) {question_data['option_a']}\n" \
                    f"Б) {question_data['option_b']}\n" \
                    f"В) {question_data['option_v']}\n" \
                    f"Г) {question_data['option_g']}\n"

    sent_message = await callback_query.message.answer_photo(
        photo=utils.PictureForDuel,
        caption=question_text,
        reply_markup=kb.duel_question_keyboard_kg(question_id=next_question_id, numerator=3),
        parse_mode=ParseMode.MARKDOWN
    )
    # Добавляем сообщение бота
    user_data['bot_messages'].append(sent_message.message_id)

@router.callback_query(lambda c: c.data and c.data.startswith("duel_question_kg_3_"))
async def duel_fourth_question_kg(callback_query: CallbackQuery, state: FSMContext):
    tuid = callback_query.message.chat.id
    user_data = sent_message_add_screen_ids[tuid]
    # Добавляем сообщение пользователя
    user_data['user_messages'].append(callback_query.message.message_id)

    # Удаляем предыдущие сообщения
    await delete_previous_messages(callback_query.message, tuid)
    # duel_question_kg_1_12_a
    callback_data = callback_query.data
    parts = callback_data.split('_')
    question_id = int(parts[4])
    selected_option = parts[5]


    if selected_option == "a":
        selected_option = "А"
    elif selected_option == "b":
        selected_option = "Б"
    elif selected_option == "v":
        selected_option = "В"
    elif selected_option == "g":
        selected_option = "Г"



    is_correct = await rq.check_answer(question_id, selected_option)

    data = await state.get_data()

    if is_correct:
        score = data['score']
        score = score + 1
        await state.update_data(score=score)

    next_question_ids = data['question_ids']
    next_question_id = next_question_ids[3]


    question_data = await rq.get_question_and_options(question_id=next_question_id)

    question_text = f"Суроо 4: *{question_data['question']}*\n" \
                    f"А) {question_data['option_a']}\n" \
                    f"Б) {question_data['option_b']}\n" \
                    f"В) {question_data['option_v']}\n" \
                    f"Г) {question_data['option_g']}\n"

    sent_message = await callback_query.message.answer_photo(
        photo=utils.PictureForDuel,
        caption=question_text,
        reply_markup=kb.duel_question_keyboard_kg(question_id=next_question_id, numerator=4),
        parse_mode=ParseMode.MARKDOWN
    )
    # Добавляем сообщение бота
    user_data['bot_messages'].append(sent_message.message_id)


@router.callback_query(lambda c: c.data and c.data.startswith("duel_question_kg_4_"))
async def duel_fifth_question_kg(callback_query: CallbackQuery, state: FSMContext):
    tuid = callback_query.message.chat.id
    user_data = sent_message_add_screen_ids[tuid]
    # Добавляем сообщение пользователя
    user_data['user_messages'].append(callback_query.message.message_id)

    # Удаляем предыдущие сообщения
    await delete_previous_messages(callback_query.message, tuid)
    # duel_question_kg_1_12_a
    callback_data = callback_query.data
    parts = callback_data.split('_')
    question_id = int(parts[4])
    selected_option = parts[5]


    if selected_option == "a":
        selected_option = "А"
    elif selected_option == "b":
        selected_option = "Б"
    elif selected_option == "v":
        selected_option = "В"
    elif selected_option == "g":
        selected_option = "Г"


    is_correct = await rq.check_answer(question_id, selected_option)

    data = await state.get_data()

    if is_correct:
        score = data['score']
        score = score + 1
        await state.update_data(score=score)

    next_question_ids = data['question_ids']
    next_question_id = next_question_ids[4]


    question_data = await rq.get_question_and_options(question_id=next_question_id)

    question_text = f"Суроо 5: *{question_data['question']}*\n" \
                    f"А) {question_data['option_a']}\n" \
                    f"Б) {question_data['option_b']}\n" \
                    f"В) {question_data['option_v']}\n" \
                    f"Г) {question_data['option_g']}\n"

    sent_message = await callback_query.message.answer_photo(
        photo=utils.PictureForDuel,
        caption=question_text,
        reply_markup=kb.duel_question_keyboard_kg(question_id=next_question_id, numerator=5),
        parse_mode=ParseMode.MARKDOWN
    )
    # Добавляем сообщение бота
    user_data['bot_messages'].append(sent_message.message_id)



@router.callback_query(lambda c: c.data and c.data.startswith("duel_question_kg_5_"))
async def duel_fifth_question_kg(callback_query: CallbackQuery, state: FSMContext):
    tuid = callback_query.message.chat.id
    user_data = sent_message_add_screen_ids[tuid]
    # Добавляем сообщение пользователя
    user_data['user_messages'].append(callback_query.message.message_id)

    # Удаляем предыдущие сообщения
    await delete_previous_messages(callback_query.message, tuid)
    # duel_question_kg_1_12_a
    callback_data = callback_query.data
    parts = callback_data.split('_')
    question_id = int(parts[4])
    selected_option = parts[5]
    telegram_id = callback_query.from_user.id
    finish_time = get_current_time()


    if selected_option == "a":
        selected_option = "А"
    elif selected_option == "b":
        selected_option = "Б"
    elif selected_option == "v":
        selected_option = "В"
    elif selected_option == "g":
        selected_option = "Г"


    is_correct = await rq.check_answer(question_id, selected_option)

    data = await state.get_data()

    if is_correct:
        score = data['score']
        score = score + 1
        await state.update_data(score=score)

    data = await state.get_data()
    score = data['score']
    start_time = data['start_time']
    question_ids = data['question_ids']
    user_type = data['user_type']

    time_difference = calculate_time_difference(start_time, finish_time)

    if user_type == "creator":
        is_added_db = await rq.record_duel(
            telegram_id=telegram_id,
            questions=question_ids,
            creator_score=score,
            creator_time=time_difference
        )

        if is_added_db:
            sent_message = await callback_query.message.answer_photo(
                photo=utils.PictureForDuel,
                caption=f"🎖️ *Сиздин балл:* _{score}_\n"
                        f"⏱️ *Кеткен убакыт:* _{time_difference} секунд_\n\n"
                        f"_Сизге атаандаш табылып, ал суроолорго жооп берип бүткөндөн кийин сизге жыйынтык_ "
                        f"_'Жыйынтыктар' баскычына түшөт. Сиз ал баскычты басып, текшерип турсаңыз болот._",
                reply_markup=kb.to_user_account_kg,
                parse_mode=ParseMode.MARKDOWN
            )
            await state.clear()
            # Добавляем сообщение бота
            user_data['bot_messages'].append(sent_message.message_id)
        else:
            sent_message = await callback_query.message.answer_photo(
                photo=utils.PictureForDuel,
                caption=f"_Сиздин жыйынтыкты базага киргизип жатканда ката чыкты, кайра башынан өтүп көрүңүз._",
                reply_markup=kb.to_user_account_kg,
                parse_mode=ParseMode.MARKDOWN
            )
            await state.clear()
            # Добавляем сообщение бота
            user_data['bot_messages'].append(sent_message.message_id)
    elif user_type == "opponent":
        duel_id = data['duel_id']
        creator_data = await rq.get_creator_score_time_and_telegram(duel_id)
        if creator_data is not None:
            creator_score, creator_time, creator_telegram_id = creator_data

            if creator_score > score:
                await rq.update_rubies(telegram_id=creator_telegram_id, rubies_to_add=30)
                await rq.update_rubies_minus(telegram_id=telegram_id, rubies_to_add=10)
                is_update = await rq.update_duel_with_opponent_results(
                    duel_id=duel_id,
                    opponent_score=score,
                    opponent_time=time_difference,
                    winner_telegram_id=creator_telegram_id
                )
                if is_update:
                    sent_message = await callback_query.message.answer_photo(
                        photo=utils.PictureForDuel,
                        caption=f"🎖️ *Сиздин балл:* _{score}_\n"
                                f"⏱️ *Кеткен убакыт:* _{time_difference} секунд_\n\n"
                                f"_Дуэлдин жыйынтыгын 'Жыйынтыктар' баскычынан азыр кирип көрсөңүз болот_",
                        reply_markup=kb.to_user_account_kg,
                        parse_mode=ParseMode.MARKDOWN
                    )
                    await state.clear()
                    # Добавляем сообщение бота
                    user_data['bot_messages'].append(sent_message.message_id)
                else:
                    sent_message = await callback_query.message.answer_photo(
                        photo=utils.PictureForDuel,
                        caption=f"Дуэлдин жыйынтыгын базага киргизип жатканда ката чыкты, кайра башынан өтүп көрүңүз._",
                        reply_markup=kb.to_user_account_kg,
                        parse_mode=ParseMode.MARKDOWN
                    )
                    await state.clear()
                    # Добавляем сообщение бота
                    user_data['bot_messages'].append(sent_message.message_id)
            elif creator_score < score:
                await rq.update_rubies(telegram_id=telegram_id, rubies_to_add=30)
                await rq.update_rubies_minus(telegram_id=creator_telegram_id, rubies_to_add=10)
                is_update = await rq.update_duel_with_opponent_results(
                    duel_id=duel_id,
                    opponent_score=score,
                    opponent_time=time_difference,
                    winner_telegram_id=telegram_id
                )
                if is_update:
                    sent_message = await callback_query.message.answer_photo(
                        photo=utils.PictureForDuel,
                        caption=f"🎖️ *Сиздин балл:* _{score}_\n"
                                f"⏱️ *Кеткен убакыт:* _{time_difference} секунд_\n\n"
                                f"_Дуэлдин жыйынтыгын 'Жыйынтыктар' баскычынан азыр кирип көрсөңүз болот_",
                        reply_markup=kb.to_user_account_kg,
                        parse_mode=ParseMode.MARKDOWN
                    )
                    await state.clear()
                    # Добавляем сообщение бота
                    user_data['bot_messages'].append(sent_message.message_id)
                else:
                    sent_message = await callback_query.message.answer_photo(
                        photo=utils.PictureForDuel,
                        caption=f"Дуэлдин жыйынтыгын базага киргизип жатканда ката чыкты, кайра башынан өтүп көрүңүз._",
                        reply_markup=kb.to_user_account_kg,
                        parse_mode=ParseMode.MARKDOWN
                    )
                    await state.clear()
                    # Добавляем сообщение бота
                    user_data['bot_messages'].append(sent_message.message_id)
            elif creator_score == score:
                if creator_time < time_difference:
                    await rq.update_rubies(telegram_id=creator_telegram_id, rubies_to_add=30)
                    await rq.update_rubies_minus(telegram_id=telegram_id, rubies_to_add=10)
                    is_update = await rq.update_duel_with_opponent_results(
                        duel_id=duel_id,
                        opponent_score=score,
                        opponent_time=time_difference,
                        winner_telegram_id=creator_telegram_id
                    )
                    if is_update:
                        sent_message = await callback_query.message.answer_photo(
                            photo=utils.PictureForDuel,
                            caption=f"🎖️ *Сиздин балл:* _{score}_\n"
                                    f"⏱️ *Кеткен убакыт:* _{time_difference} секунд_\n\n"
                                    f"_Дуэлдин жыйынтыгын 'Жыйынтыктар' баскычынан азыр кирип көрсөңүз болот_",
                            reply_markup=kb.to_user_account_kg,
                            parse_mode=ParseMode.MARKDOWN
                        )
                        await state.clear()
                        # Добавляем сообщение бота
                        user_data['bot_messages'].append(sent_message.message_id)
                    else:
                        sent_message = await callback_query.message.answer_photo(
                            photo=utils.PictureForDuel,
                            caption=f"Дуэлдин жыйынтыгын базага киргизип жатканда ката чыкты, кайра башынан өтүп көрүңүз._",
                            reply_markup=kb.to_user_account_kg,
                            parse_mode=ParseMode.MARKDOWN
                        )
                        await state.clear()
                        # Добавляем сообщение бота
                        user_data['bot_messages'].append(sent_message.message_id)
                elif creator_time > time_difference:
                    await rq.update_rubies(telegram_id=telegram_id, rubies_to_add=30)
                    await rq.update_rubies_minus(telegram_id=creator_telegram_id, rubies_to_add=10)
                    is_update = await rq.update_duel_with_opponent_results(
                        duel_id=duel_id,
                        opponent_score=score,
                        opponent_time=time_difference,
                        winner_telegram_id=telegram_id
                    )
                    if is_update:
                        sent_message = await callback_query.message.answer_photo(
                            photo=utils.PictureForDuel,
                            caption=f"🎖️ *Сиздин балл:* _{score}_\n"
                                    f"⏱️ *Кеткен убакыт:* _{time_difference} секунд_\n\n"
                                    f"_Дуэлдин жыйынтыгын 'Жыйынтыктар' баскычынан азыр кирип көрсөңүз болот_",
                            reply_markup=kb.to_user_account_kg,
                            parse_mode=ParseMode.MARKDOWN
                        )
                        await state.clear()
                        # Добавляем сообщение бота
                        user_data['bot_messages'].append(sent_message.message_id)
                    else:
                        sent_message = await callback_query.message.answer_photo(
                            photo=utils.PictureForDuel,
                            caption=f"Дуэлдин жыйынтыгын базага киргизип жатканда ката чыкты, кайра башынан өтүп көрүңүз._",
                            reply_markup=kb.to_user_account_kg,
                            parse_mode=ParseMode.MARKDOWN
                        )
                        await state.clear()
                        # Добавляем сообщение бота
                        user_data['bot_messages'].append(sent_message.message_id)
                elif creator_time == time_difference:
                    await rq.update_rubies(telegram_id=telegram_id, rubies_to_add=30)
                    await rq.update_rubies(telegram_id=creator_telegram_id, rubies_to_add=30)
                    is_update = await rq.update_duel_with_opponent_results(
                        duel_id=duel_id,
                        opponent_score=score,
                        opponent_time=time_difference,
                        winner_telegram_id="Draw"
                    )
                    if is_update:
                        sent_message = await callback_query.message.answer_photo(
                            photo=utils.PictureForDuel,
                            caption=f"🎖️ *Сиздин балл:* _{score}_\n"
                                    f"⏱️ *Кеткен убакыт:* _{time_difference} секунд_\n\n"
                                    f"_Дуэлдин жыйынтыгын 'Жыйынтыктар' баскычынан азыр кирип көрсөңүз болот_",
                            reply_markup=kb.to_user_account_kg,
                            parse_mode=ParseMode.MARKDOWN
                        )
                        await state.clear()
                        # Добавляем сообщение бота
                        user_data['bot_messages'].append(sent_message.message_id)
                    else:
                        sent_message = await callback_query.message.answer_photo(
                            photo=utils.PictureForDuel,
                            caption=f"Дуэлдин жыйынтыгын базага киргизип жатканда ката чыкты, кайра башынан өтүп көрүңүз._",
                            reply_markup=kb.to_user_account_kg,
                            parse_mode=ParseMode.MARKDOWN
                        )
                        await state.clear()
                        # Добавляем сообщение бота
                        user_data['bot_messages'].append(sent_message.message_id)

        else:
            sent_message = await callback_query.message.answer_photo(
                photo=utils.PictureForDuel,
                caption=f"_Сиздин жыйынтыкты базага киргизип жатканда ката чыкты, кайра башынан өтүп көрүңүз._",
                reply_markup=kb.to_user_account_kg,
                parse_mode=ParseMode.MARKDOWN
            )
            await state.clear()
            # Добавляем сообщение бота
            user_data['bot_messages'].append(sent_message.message_id)

@router.callback_query(F.data == 'duel_results_kg')
async def duel_results_kg(callback_query: CallbackQuery):
    tuid = callback_query.message.chat.id
    user_data = sent_message_add_screen_ids[tuid]
    # Добавляем сообщение пользователя
    user_data['user_messages'].append(callback_query.message.message_id)

    # Удаляем предыдущие сообщения
    await delete_previous_messages(callback_query.message, tuid)

    telegram_id = callback_query.message.chat.id

    duel_results = await rq.get_duel_results(telegram_id)

    if duel_results:
        # Формируем текст с результатами
        response_text = (
            f"*ДУЭЛЬ ЖЫЙЫНТЫКТАРЫ:*\n\n"
            f"🏆 Жеңиштер: {duel_results['win_count']}\n"
            f"📉 Жеңилүүлөр: {duel_results['lose_count']}\n"
            f"⏳ Атаандаш табыла элек: {duel_results['pending_count']}\n\n"
            f"*АКЫРКЫ 10 ДУЭЛЬ:*\n\n"
        )

        # Добавляем информацию о последних 20 дуэлях
        for idx, duel in enumerate(duel_results['recent_duels'], start=1):
            response_text += (
                f"{idx}. *Түзгөн:* _{duel['creator_name']}:_\n"
                f"🎖️: _{duel['creator_score']}_\n"
                f"⏱️: _{duel['creator_time']}_\n"
                f"*Атаандаш:* _{duel['opponent_name']}_\n"
                f"🎖️: _{duel['opponent_score']}_\n"
                f"⏱️: _{duel['opponent_time']}_\n"
                f"*Түзүлгөн убакыт:* _{str(duel['created_at'])[:16]}_\n"
                f"*Аяктаган убакыт:* _{str(duel['completed_at'])[:16]}_\n\n"
            )

        await callback_query.message.answer(
            text=response_text,
            reply_markup=kb.to_user_account_kg,
            parse_mode=ParseMode.MARKDOWN
        )
    else:
        await callback_query.message.answer(
            text="Дуэлдер боюнча маалымат алууда ката кетти.",
            reply_markup=kb.to_user_account_kg
        )


#################################################################################
#                        Duel in russian language                               #
#################################################################################

@router.callback_query(F.data == 'duel_ru')
async def duel_ru(callback_query: CallbackQuery):
    tuid = callback_query.message.chat.id
    user_data = sent_message_add_screen_ids[tuid]
    # Добавляем сообщение пользователя
    user_data['user_messages'].append(callback_query.message.message_id)

    # Удаляем предыдущие сообщения
    await delete_previous_messages(callback_query.message, tuid)

    sent_message = await callback_query.message.answer_photo(
        photo=utils.PictureForDuel,
        caption=f'\n<a href="https://telegra.ph/Funkciya-Duehl-v-nashem-bote-Srazites-za-rubiny-i-pokazhite-kto-luchshij-11-14">Что такое дуэль?</a> 👈',
        reply_markup=kb.duel_menu_ru,
        parse_mode=ParseMode.HTML
    )

    # Добавляем сообщение бота
    user_data['bot_messages'].append(sent_message.message_id)


@router.callback_query(F.data == 'duel_with_random_ru')
async def duel_with_random_ru(callback_query: CallbackQuery, state: FSMContext):
    tuid = callback_query.message.chat.id
    user_data = sent_message_add_screen_ids[tuid]
    # Добавляем сообщение пользователя
    user_data['user_messages'].append(callback_query.message.message_id)

    # Удаляем предыдущие сообщения
    await delete_previous_messages(callback_query.message, tuid)
    telegram_id = callback_query.from_user.id

    is_vip = await rq.is_vip_user(telegram_id=telegram_id)

    if is_vip:
        has_rubies = await rq.has_minimum_rubies(telegram_id=telegram_id)

        if has_rubies:
            is_duel = await rq.has_unfinished_duels(telegram_id=telegram_id)

            if not is_duel:
                count_duels_with_opponent = await rq.count_duels_with_opponent_pending(telegram_id=telegram_id)
                if count_duels_with_opponent <= 4:
                    await state.update_data(user_type="creator")
                    question_ids = await rq.get_random_questions_by_subjects(subject_id1=1, subject_id2=3)
                    await duel_first_question_ru(callback_query, question_ids, state)
                else:
                    sent_message = await callback_query.message.answer_photo(
                        photo=utils.PictureForDuel,
                        caption="Вы открыли 5 дуэлей, которые никто не завершил.\n"
                                "_По крайней мере, вы можете сразиться с кем-то после того, как кто-то другой прошел._",
                        reply_markup=kb.to_user_account_ru,
                            parse_mode=ParseMode.MARKDOWN
                    )
                    # Добавляем сообщение бота
                    user_data['bot_messages'].append(sent_message.message_id)
            else:
                duel_id = await rq.update_opponent_in_oldest_duel(telegram_id=telegram_id)
                if duel_id:
                    question_ids = await rq.get_duel_questions(duel_id=duel_id)
                    if question_ids is None:
                        sent_message = await callback_query.message.answer_photo(
                            photo=utils.PictureForDuel,
                            caption="Ошибка при получении дуэльных вопросов.\n"
                                    "Попробуйте войти с самого начала.",
                            reply_markup=kb.to_user_account_ru
                        )
                        # Добавляем сообщение бота
                        user_data['bot_messages'].append(sent_message.message_id)
                    else:
                        await state.update_data(user_type="opponent", duel_id=duel_id)
                        # Проверка и преобразование в list[int] при необходимости
                        if isinstance(question_ids, str):
                            question_ids = json.loads(question_ids)
                        await duel_first_question_ru(callback_query, question_ids, state)
                else:
                    count_duels_with_opponent = await rq.count_duels_with_opponent_pending(telegram_id=telegram_id)
                    if count_duels_with_opponent <= 4:
                        await state.update_data(user_type="creator")
                        question_ids = await rq.get_random_questions_by_subjects(subject_id1=1, subject_id2=3)
                        await duel_first_question_ru(callback_query, question_ids, state)
                    else:
                        sent_message = await callback_query.message.answer_photo(
                            photo=utils.PictureForDuel,
                            caption="Вы открыли 5 дуэлей, которые никто еще не прошел.\n"
                                    "_По крайней мере, вы можете начать дуэль после того, как кто-то другой пройдет._",
                            reply_markup=kb.to_user_account_ru,
                            parse_mode=ParseMode.MARKDOWN
                        )
                        # Добавляем сообщение бота
                        user_data['bot_messages'].append(sent_message.message_id)
        else:
            sent_message = await callback_query.message.answer_photo(
                photo=utils.PictureForDuel,
                caption="У вас недостаточно рубина, чтобы участвовать в дуэли\n"
                        "Должно быть не менее 10 рубинов.",
                reply_markup=kb.to_user_account_ru
            )
            # Добавляем сообщение бота
            user_data['bot_messages'].append(sent_message.message_id)
    else:
        sent_message = await callback_query.message.answer_photo(
            photo=utils.PictureForDuel,
            caption="Чтобы посоревноваться с друзями в дуэле вам надо VIP подписка. Для этого в личном кабинете выберите "
                    "кнопку VIP и свяжитесь с админом.",
            reply_markup=kb.to_user_account_ru
        )
        # Добавляем сообщение бота
        user_data['bot_messages'].append(sent_message.message_id)

async def duel_first_question_ru(callback_query, question_ids: list[int], state: FSMContext):
    tuid = callback_query.message.chat.id
    user_data = sent_message_add_screen_ids[tuid]
    question_id = question_ids[0]
    start_time = get_current_time()
    question_data = await rq.get_question_and_options(question_id=question_id)
    await state.update_data(question_ids=question_ids, score=0, start_time=start_time)

    question_text = f"Вопрос 1: *{question_data['question']}*\n" \
                    f"А) {question_data['option_a']}\n" \
                    f"Б) {question_data['option_b']}\n" \
                    f"В) {question_data['option_v']}\n" \
                    f"Г) {question_data['option_g']}\n"

    sent_message = await callback_query.message.answer_photo(
        photo=utils.PictureForDuel,
        caption=question_text,
        reply_markup=kb.duel_question_keyboard_ru(question_id=question_id, numerator=1),
        parse_mode=ParseMode.MARKDOWN
    )
    # Добавляем сообщение бота
    user_data['bot_messages'].append(sent_message.message_id)


@router.callback_query(lambda c: c.data and c.data.startswith("duel_question_ru_1_"))
async def duel_second_question_ru(callback_query: CallbackQuery, state: FSMContext):
    tuid = callback_query.message.chat.id
    user_data = sent_message_add_screen_ids[tuid]
    # Добавляем сообщение пользователя
    user_data['user_messages'].append(callback_query.message.message_id)

    # Удаляем предыдущие сообщения
    await delete_previous_messages(callback_query.message, tuid)
    # duel_question_ru_1_12_a
    callback_data = callback_query.data
    parts = callback_data.split('_')
    question_id = int(parts[4])
    selected_option = parts[5]

    if selected_option == "a":
        selected_option = "А"
    elif selected_option == "b":
        selected_option = "Б"
    elif selected_option == "v":
        selected_option = "В"
    elif selected_option == "g":
        selected_option = "Г"


    is_correct = await rq.check_answer(question_id, selected_option)

    data = await state.get_data()

    if is_correct:
        score = data['score']
        score = score + 1
        await state.update_data(score=score)

    next_question_ids = data['question_ids']
    next_question_id = next_question_ids[1]


    question_data = await rq.get_question_and_options(question_id=next_question_id)

    question_text = f"Вопрос 2: *{question_data['question']}*\n" \
                    f"А) {question_data['option_a']}\n" \
                    f"Б) {question_data['option_b']}\n" \
                    f"В) {question_data['option_v']}\n" \
                    f"Г) {question_data['option_g']}\n"

    sent_message = await callback_query.message.answer_photo(
        photo=utils.PictureForDuel,
        caption=question_text,
        reply_markup=kb.duel_question_keyboard_ru(question_id=next_question_id, numerator=2),
        parse_mode=ParseMode.MARKDOWN
    )
    # Добавляем сообщение бота
    user_data['bot_messages'].append(sent_message.message_id)

@router.callback_query(lambda c: c.data and c.data.startswith("duel_question_ru_2_"))
async def duel_third_question_ru(callback_query: CallbackQuery, state: FSMContext):
    tuid = callback_query.message.chat.id
    user_data = sent_message_add_screen_ids[tuid]
    # Добавляем сообщение пользователя
    user_data['user_messages'].append(callback_query.message.message_id)

    # Удаляем предыдущие сообщения
    await delete_previous_messages(callback_query.message, tuid)
    # duel_question_ru_1_12_a
    callback_data = callback_query.data
    parts = callback_data.split('_')
    question_id = int(parts[4])
    selected_option = parts[5]


    if selected_option == "a":
        selected_option = "А"
    elif selected_option == "b":
        selected_option = "Б"
    elif selected_option == "v":
        selected_option = "В"
    elif selected_option == "g":
        selected_option = "Г"

    is_correct = await rq.check_answer(question_id, selected_option)

    data = await state.get_data()

    if is_correct:
        score = data['score']
        score = score + 1
        await state.update_data(score=score)

    next_question_ids = data['question_ids']
    next_question_id = next_question_ids[2]


    question_data = await rq.get_question_and_options(question_id=next_question_id)

    question_text = f"Вопрос 3: *{question_data['question']}*\n" \
                    f"А) {question_data['option_a']}\n" \
                    f"Б) {question_data['option_b']}\n" \
                    f"В) {question_data['option_v']}\n" \
                    f"Г) {question_data['option_g']}\n"

    sent_message = await callback_query.message.answer_photo(
        photo=utils.PictureForDuel,
        caption=question_text,
        reply_markup=kb.duel_question_keyboard_ru(question_id=next_question_id, numerator=3),
        parse_mode=ParseMode.MARKDOWN
    )
    # Добавляем сообщение бота
    user_data['bot_messages'].append(sent_message.message_id)


@router.callback_query(lambda c: c.data and c.data.startswith("duel_question_ru_3_"))
async def duel_fourth_question_ru(callback_query: CallbackQuery, state: FSMContext):
    tuid = callback_query.message.chat.id
    user_data = sent_message_add_screen_ids[tuid]
    # Добавляем сообщение пользователя
    user_data['user_messages'].append(callback_query.message.message_id)

    # Удаляем предыдущие сообщения
    await delete_previous_messages(callback_query.message, tuid)
    # duel_question_ru_1_12_a
    callback_data = callback_query.data
    parts = callback_data.split('_')
    question_id = int(parts[4])
    selected_option = parts[5]


    if selected_option == "a":
        selected_option = "А"
    elif selected_option == "b":
        selected_option = "Б"
    elif selected_option == "v":
        selected_option = "В"
    elif selected_option == "g":
        selected_option = "Г"



    is_correct = await rq.check_answer(question_id, selected_option)

    data = await state.get_data()

    if is_correct:
        score = data['score']
        score = score + 1
        await state.update_data(score=score)

    next_question_ids = data['question_ids']
    next_question_id = next_question_ids[3]


    question_data = await rq.get_question_and_options(question_id=next_question_id)

    question_text = f"Вопрос 4: *{question_data['question']}*\n" \
                    f"А) {question_data['option_a']}\n" \
                    f"Б) {question_data['option_b']}\n" \
                    f"В) {question_data['option_v']}\n" \
                    f"Г) {question_data['option_g']}\n"

    sent_message = await callback_query.message.answer_photo(
        photo=utils.PictureForDuel,
        caption=question_text,
        reply_markup=kb.duel_question_keyboard_ru(question_id=next_question_id, numerator=4),
        parse_mode=ParseMode.MARKDOWN
    )
    # Добавляем сообщение бота
    user_data['bot_messages'].append(sent_message.message_id)


@router.callback_query(lambda c: c.data and c.data.startswith("duel_question_ru_4_"))
async def duel_fifth_question_ru(callback_query: CallbackQuery, state: FSMContext):
    tuid = callback_query.message.chat.id
    user_data = sent_message_add_screen_ids[tuid]
    # Добавляем сообщение пользователя
    user_data['user_messages'].append(callback_query.message.message_id)

    # Удаляем предыдущие сообщения
    await delete_previous_messages(callback_query.message, tuid)
    # duel_question_ru_1_12_a
    callback_data = callback_query.data
    parts = callback_data.split('_')
    question_id = int(parts[4])
    selected_option = parts[5]


    if selected_option == "a":
        selected_option = "А"
    elif selected_option == "b":
        selected_option = "Б"
    elif selected_option == "v":
        selected_option = "В"
    elif selected_option == "g":
        selected_option = "Г"


    is_correct = await rq.check_answer(question_id, selected_option)

    data = await state.get_data()

    if is_correct:
        score = data['score']
        score = score + 1
        await state.update_data(score=score)

    next_question_ids = data['question_ids']
    next_question_id = next_question_ids[4]


    question_data = await rq.get_question_and_options(question_id=next_question_id)

    question_text = f"Вопрос 5: *{question_data['question']}*\n" \
                    f"А) {question_data['option_a']}\n" \
                    f"Б) {question_data['option_b']}\n" \
                    f"В) {question_data['option_v']}\n" \
                    f"Г) {question_data['option_g']}\n"

    sent_message = await callback_query.message.answer_photo(
        photo=utils.PictureForDuel,
        caption=question_text,
        reply_markup=kb.duel_question_keyboard_ru(question_id=next_question_id, numerator=5),
        parse_mode=ParseMode.MARKDOWN
    )
    # Добавляем сообщение бота
    user_data['bot_messages'].append(sent_message.message_id)

@router.callback_query(lambda c: c.data and c.data.startswith("duel_question_ru_5_"))
async def duel_fifth_question_ru(callback_query: CallbackQuery, state: FSMContext):
    tuid = callback_query.message.chat.id
    user_data = sent_message_add_screen_ids[tuid]
    # Добавляем сообщение пользователя
    user_data['user_messages'].append(callback_query.message.message_id)

    # Удаляем предыдущие сообщения
    await delete_previous_messages(callback_query.message, tuid)
    # duel_question_ru_1_12_a
    callback_data = callback_query.data
    parts = callback_data.split('_')
    question_id = int(parts[4])
    selected_option = parts[5]
    telegram_id = callback_query.from_user.id
    finish_time = get_current_time()


    if selected_option == "a":
        selected_option = "А"
    elif selected_option == "b":
        selected_option = "Б"
    elif selected_option == "v":
        selected_option = "В"
    elif selected_option == "g":
        selected_option = "Г"


    is_correct = await rq.check_answer(question_id, selected_option)

    data = await state.get_data()

    if is_correct:
        score = data['score']
        score = score + 1
        await state.update_data(score=score)

    data = await state.get_data()
    score = data['score']
    start_time = data['start_time']
    question_ids = data['question_ids']
    user_type = data['user_type']

    time_difference = calculate_time_difference(start_time, finish_time)

    if user_type == "creator":
        is_added_db = await rq.record_duel(
            telegram_id=telegram_id,
            questions=question_ids,
            creator_score=score,
            creator_time=time_difference
        )

        if is_added_db:
            sent_message = await callback_query.message.answer_photo(
                photo=utils.PictureForDuel,
                caption=f"🎖️ *Ваш результат:* _{score}_\n"
                        f"⏱️ *Время:* _{time_difference} секунд_\n\n"
                        f"_После того как будет найден соперник и он ответит на вопросы, вы сможете увидеть результаты,_ "
                        f"_нажав на кнопку 'Результаты'._",
                reply_markup=kb.to_user_account_ru,
                parse_mode=ParseMode.MARKDOWN
            )
            await state.clear()
            # Добавляем сообщение бота
            user_data['bot_messages'].append(sent_message.message_id)
        else:
            sent_message = await callback_query.message.answer_photo(
                photo=utils.PictureForDuel,
                caption=f"_Ошибка возникла при вводе результатов в базу данных, попробуйте пройти еще раз._",
                reply_markup=kb.to_user_account_ru,
                parse_mode=ParseMode.MARKDOWN
            )
            await state.clear()
            # Добавляем сообщение бота
            user_data['bot_messages'].append(sent_message.message_id)
    elif user_type == "opponent":
        duel_id = data['duel_id']
        creator_data = await rq.get_creator_score_time_and_telegram(duel_id)
        if creator_data is not None:
            creator_score, creator_time, creator_telegram_id = creator_data

            if creator_score > score:
                await rq.update_rubies(telegram_id=creator_telegram_id, rubies_to_add=30)
                await rq.update_rubies_minus(telegram_id=telegram_id, rubies_to_add=10)
                is_update = await rq.update_duel_with_opponent_results(
                    duel_id=duel_id,
                    opponent_score=score,
                    opponent_time=time_difference,
                    winner_telegram_id=creator_telegram_id
                )
                if is_update:
                    sent_message = await callback_query.message.answer_photo(
                        photo=utils.PictureForDuel,
                        caption=f"🎖️ *Ваш результат:* _{score}_\n"
                                f"⏱️ *Время:* _{time_difference} секунд_\n\n"
                                f"_Вы можете увидеть результаты дуэли, войдя в систему прямо сейчас с помощью кнопки 'Результаты'._",
                        reply_markup=kb.to_user_account_ru,
                        parse_mode=ParseMode.MARKDOWN
                    )
                    await state.clear()
                    # Добавляем сообщение бота
                    user_data['bot_messages'].append(sent_message.message_id)
                else:
                    sent_message = await callback_query.message.answer_photo(
                        photo=utils.PictureForDuel,
                        caption=f"Ошибка возникла при вводе результатов в базу данных, попробуйте пройти еще раз._",
                        reply_markup=kb.to_user_account_ru,
                        parse_mode=ParseMode.MARKDOWN
                    )
                    await state.clear()
                    # Добавляем сообщение бота
                    user_data['bot_messages'].append(sent_message.message_id)
            elif creator_score < score:
                await rq.update_rubies(telegram_id=telegram_id, rubies_to_add=30)
                await rq.update_rubies_minus(telegram_id=creator_telegram_id, rubies_to_add=10)
                is_update = await rq.update_duel_with_opponent_results(
                    duel_id=duel_id,
                    opponent_score=score,
                    opponent_time=time_difference,
                    winner_telegram_id=telegram_id
                )
                if is_update:
                    sent_message = await callback_query.message.answer_photo(
                        photo=utils.PictureForDuel,
                        caption=f"🎖️ *Ваш результат:* _{score}_\n"
                                f"⏱️ *Время:* _{time_difference} секунд_\n\n"
                                f"_Вы можете увидеть результаты дуэли, войдя в систему прямо сейчас с помощью кнопки 'Результаты'._",
                        reply_markup=kb.to_user_account_ru,
                        parse_mode=ParseMode.MARKDOWN
                    )
                    await state.clear()
                    # Добавляем сообщение бота
                    user_data['bot_messages'].append(sent_message.message_id)
                else:
                    sent_message = await callback_query.message.answer_photo(
                        photo=utils.PictureForDuel,
                        caption=f"Ошибка возникла при вводе результатов в базу данных, попробуйте пройти еще раз._",
                        reply_markup=kb.to_user_account_ru,
                        parse_mode=ParseMode.MARKDOWN
                    )
                    await state.clear()
                    # Добавляем сообщение бота
                    user_data['bot_messages'].append(sent_message.message_id)
            elif creator_score == score:
                if creator_time < time_difference:
                    await rq.update_rubies(telegram_id=creator_telegram_id, rubies_to_add=30)
                    await rq.update_rubies_minus(telegram_id=telegram_id, rubies_to_add=10)
                    is_update = await rq.update_duel_with_opponent_results(
                        duel_id=duel_id,
                        opponent_score=score,
                        opponent_time=time_difference,
                        winner_telegram_id=creator_telegram_id
                    )
                    if is_update:
                        sent_message = await callback_query.message.answer_photo(
                            photo=utils.PictureForDuel,
                            caption=f"🎖️ *Ваш результат:* _{score}_\n"
                                    f"⏱️ *Время:* _{time_difference} секунд_\n\n"
                                    f"_Вы можете увидеть результаты дуэли, войдя в систему прямо сейчас с помощью кнопки 'Результаты'._",
                            reply_markup=kb.to_user_account_ru,
                            parse_mode=ParseMode.MARKDOWN
                        )
                        await state.clear()
                        # Добавляем сообщение бота
                        user_data['bot_messages'].append(sent_message.message_id)
                    else:
                        sent_message = await callback_query.message.answer_photo(
                            photo=utils.PictureForDuel,
                            caption=f"Ошибка возникла при вводе результатов в базу данных, попробуйте пройти еще раз._",
                            reply_markup=kb.to_user_account_ru,
                            parse_mode=ParseMode.MARKDOWN
                        )
                        await state.clear()
                        # Добавляем сообщение бота
                        user_data['bot_messages'].append(sent_message.message_id)
                elif creator_time > time_difference:
                    await rq.update_rubies(telegram_id=telegram_id, rubies_to_add=30)
                    await rq.update_rubies_minus(telegram_id=creator_telegram_id, rubies_to_add=10)
                    is_update = await rq.update_duel_with_opponent_results(
                        duel_id=duel_id,
                        opponent_score=score,
                        opponent_time=time_difference,
                        winner_telegram_id=telegram_id
                    )
                    if is_update:
                        sent_message = await callback_query.message.answer_photo(
                            photo=utils.PictureForDuel,
                            caption=f"🎖️ *Ваш результат:* _{score}_\n"
                                    f"⏱️ *Время:* _{time_difference} секунд_\n\n"
                                    f"_Вы можете увидеть результаты дуэли, войдя в систему прямо сейчас с помощью кнопки 'Результаты'._",
                            reply_markup=kb.to_user_account_ru,
                            parse_mode=ParseMode.MARKDOWN
                        )
                        await state.clear()
                        # Добавляем сообщение бота
                        user_data['bot_messages'].append(sent_message.message_id)
                    else:
                        sent_message = await callback_query.message.answer_photo(
                            photo=utils.PictureForDuel,
                            caption=f"Ошибка возникла при вводе результатов в базу данных, попробуйте пройти еще раз._",
                            reply_markup=kb.to_user_account_ru,
                            parse_mode=ParseMode.MARKDOWN
                        )
                        await state.clear()
                        # Добавляем сообщение бота
                        user_data['bot_messages'].append(sent_message.message_id)
                elif creator_time == time_difference:
                    await rq.update_rubies(telegram_id=telegram_id, rubies_to_add=30)
                    await rq.update_rubies(telegram_id=creator_telegram_id, rubies_to_add=30)
                    is_update = await rq.update_duel_with_opponent_results(
                        duel_id=duel_id,
                        opponent_score=score,
                        opponent_time=time_difference,
                        winner_telegram_id="Draw"
                    )
                    if is_update:
                        sent_message = await callback_query.message.answer_photo(
                            photo=utils.PictureForDuel,
                            caption=f"🎖️ *Ваш результат:* _{score}_\n"
                                    f"⏱️ *Время:* _{time_difference} секунд_\n\n"
                                    f"_Вы можете увидеть результаты дуэли, войдя в систему прямо сейчас с помощью кнопки 'Результаты'._",
                            reply_markup=kb.to_user_account_ru,
                            parse_mode=ParseMode.MARKDOWN
                        )
                        await state.clear()
                        # Добавляем сообщение бота
                        user_data['bot_messages'].append(sent_message.message_id)
                    else:
                        sent_message = await callback_query.message.answer_photo(
                            photo=utils.PictureForDuel,
                            caption=f"Ошибка возникла при вводе результатов в базу данных, попробуйте пройти еще раз._",
                            reply_markup=kb.to_user_account_ru,
                            parse_mode=ParseMode.MARKDOWN
                        )
                        await state.clear()
                        # Добавляем сообщение бота
                        user_data['bot_messages'].append(sent_message.message_id)

        else:
            sent_message = await callback_query.message.answer_photo(
                photo=utils.PictureForDuel,
                caption=f"_Ошибка возникла при вводе результатов в базу данных, попробуйте пройти еще раз._",
                reply_markup=kb.to_user_account_ru,
                parse_mode=ParseMode.MARKDOWN
            )
            await state.clear()
            # Добавляем сообщение бота
            user_data['bot_messages'].append(sent_message.message_id)

@router.callback_query(F.data == 'duel_results_ru')
async def duel_results_ru(callback_query: CallbackQuery):
    tuid = callback_query.message.chat.id
    user_data = sent_message_add_screen_ids[tuid]
    # Добавляем сообщение пользователя
    user_data['user_messages'].append(callback_query.message.message_id)

    # Удаляем предыдущие сообщения
    await delete_previous_messages(callback_query.message, tuid)

    telegram_id = callback_query.message.chat.id

    duel_results = await rq.get_duel_results(telegram_id)

    if duel_results:
        # Формируем текст с результатами
        response_text = (
            f"*РЕЗУЛЬТАТЫ ДУЭЛЕЙ:*\n\n"
            f"🏆 Победы: {duel_results['win_count']}\n"
            f"📉 Поражения: {duel_results['lose_count']}\n"
            f"⏳ В ожидании соперника: {duel_results['pending_count']}\n\n"
            f"*ПОСЛЕДНИЕ 10 ДУЭЛЕЙ:*\n\n"
        )

        # Добавляем информацию о последних 20 дуэлях
        for idx, duel in enumerate(duel_results['recent_duels'], start=1):
            response_text += (
                f"{idx}. *Создатель:* _{duel['creator_name']}:_\n"
                f"🎖️: _{duel['creator_score']}_\n"
                f"⏱️: _{duel['creator_time']}_\n"
                f"*Соперник:* _{duel['opponent_name']}_\n"
                f"🎖️: _{duel['opponent_score']}_\n"
                f"⏱️: _{duel['opponent_time']}_\n"
                f"*Время создания:* _{str(duel['created_at'])[:16]}_\n"
                f"*Время завершения:* _{str(duel['completed_at'])[:16]}_\n\n"
            )

        await callback_query.message.answer(
            text=response_text,
            reply_markup=kb.to_user_account_ru,
            parse_mode=ParseMode.MARKDOWN
        )
    else:
        await callback_query.message.answer(
            text="Произошла ошибка при получении информации о дуэлях.",
            reply_markup=kb.to_user_account_ru
        )