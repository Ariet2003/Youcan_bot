import json

from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from aiogram import F, Router
from app.database import requests as rq
from aiogram.fsm.context import FSMContext
from app.users.user.scripts import is_valid_analogy, is_kyrgyz_words, is_kyrgyz_sentence, is_russian_words, \
    is_russian_sentence
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
#               Creating a analogy test in kg                #
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
        photo=utils.pictureForTheEditAnAnalogyKG,
        caption='Негизги жуптун берилишин жазыңыз.\nҮлгү: _Алма : Жемиш_',
        parse_mode=ParseMode.MARKDOWN
    )
    await state.set_state(st.CreatAnalogyQuestionsKG.create_question_kg)
    sent_message_add_screen_ids['bot_messages'].append(sent_message.message_id)


# Handler for entering analogy question text
@router.message(st.CreatAnalogyQuestionsKG.create_question_kg)
async def get_question_text(message: Message, state: FSMContext):
    question_text = message.text
    sent_message_add_screen_ids['user_messages'].append(message.message_id)
    await delete_previous_messages(message)

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
    sent_message_add_screen_ids['bot_messages'].append(sent_message.message_id)


# General handler for options A, B, V, and G
async def get_option_analogy_kg(message: Message, state: FSMContext, option_key: str, next_state):
    # Сохранение сообщения пользователя для удаления позже
    sent_message_add_screen_ids['user_messages'].append(message.message_id)
    await delete_previous_messages(message)
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

    # Сохранение отправленного ботом сообщения для удаления позже
    sent_message_add_screen_ids['bot_messages'].append(sent_message.message_id)


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
    sent_message_add_screen_ids['user_messages'].append(callback_query.message.message_id)
    await delete_previous_messages(callback_query.message)
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
    sent_message_add_screen_ids['bot_messages'].append(sent_message.message_id)




##############################################################
#              Creating a analogy test in ru                 #
##############################################################

# Handler for creating a question in ru
@router.callback_query(F.data == 'creat_test_ru')
async def create_question(callback_query: CallbackQuery, state: FSMContext):
    sent_message_add_screen_ids['user_messages'].append(callback_query.message.message_id)
    await delete_previous_messages(callback_query.message)
    sent_message = await callback_query.message.answer_photo(
        photo=utils.pictureForTheTestCreationScreenRU,
        caption='Из какого раздела вы хотите создать вопрос?',
        reply_markup=kb.subjects_ru
    )
    sent_message_add_screen_ids['bot_messages'].append(sent_message.message_id)


# Initial handler for entering question text
@router.callback_query(F.data == 'analogy_ru')
async def write_analogy_question_ru(callback_query: CallbackQuery, state: FSMContext):
    sent_message_add_screen_ids['user_messages'].append(callback_query.message.message_id)
    await delete_previous_messages(callback_query.message)

    sent_message = await callback_query.message.answer_photo(
        photo=utils.pictureForTheEditAnAnalogyRU,
        caption='Введите основную пару.\nПример: _Яблоко : Фрукт_',
        parse_mode=ParseMode.MARKDOWN
    )
    await state.set_state(st.CreatAnalogyQuestionsRU.create_question_ru)
    sent_message_add_screen_ids['bot_messages'].append(sent_message.message_id)


# Handler for entering analogy question text
@router.message(st.CreatAnalogyQuestionsRU.create_question_ru)
async def get_question_text(message: Message, state: FSMContext):
    question_text = message.text
    sent_message_add_screen_ids['user_messages'].append(message.message_id)
    await delete_previous_messages(message)

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

    sent_message_add_screen_ids['bot_messages'].append(sent_message.message_id)


# General handler for options A, B, V, and G in Russian
async def get_option_analogy_ru(message: Message, state: FSMContext, option_key: str, next_state):
    sent_message_add_screen_ids['user_messages'].append(message.message_id)
    await delete_previous_messages(message)
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

    sent_message_add_screen_ids['bot_messages'].append(sent_message.message_id)


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
    sent_message_add_screen_ids['user_messages'].append(callback_query.message.message_id)
    await delete_previous_messages(callback_query.message)

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
    sent_message_add_screen_ids['bot_messages'].append(sent_message.message_id)


##############################################################
#               Creating a grammar test in kg                #
##############################################################

# Initial handler for entering question text
@router.callback_query(F.data == 'grammar_kg')
async def write_grammar_question_kg(callback_query: CallbackQuery, state: FSMContext):
    sent_message_add_screen_ids['user_messages'].append(callback_query.message.message_id)
    await delete_previous_messages(callback_query.message)

    sent_message = await callback_query.message.answer_photo(
        photo=utils.pictureForTheEditAnGrammerKG,
        caption='Грамматыкалык суроонун берилишин жазыңыз',
        parse_mode=ParseMode.MARKDOWN
    )
    await state.set_state(st.CreatGrammarQuestionsKG.create_question_kg)
    sent_message_add_screen_ids['bot_messages'].append(sent_message.message_id)


# Handler for entering grammar question text
@router.message(st.CreatGrammarQuestionsKG.create_question_kg)
async def get_question_text(message: Message, state: FSMContext):
    question_text = message.text
    sent_message_add_screen_ids['user_messages'].append(message.message_id)
    await delete_previous_messages(message)

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
        sent_message_add_screen_ids['bot_messages'].append(sent_message.message_id)
    else:
        err_sentences = await is_kyrgyz_sentence(question_text)
        sent_message = await message.answer_photo(
            photo=utils.pictureForTheEditAnGrammerKG,
            caption=f'_{err_sentences}._\nТууралап, суроонун берилишин кайра жазыңыз:',
            parse_mode=ParseMode.MARKDOWN
        )
        await state.set_state(st.CreatGrammarQuestionsKG.create_question_kg)
        sent_message_add_screen_ids['bot_messages'].append(sent_message.message_id)

# General handler for options A, B, V, and G
async def get_option_grammar_kg(message: Message, state: FSMContext, option_key: str, next_state):
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

    # Сохранение отправленного ботом сообщения для удаления позже
    sent_message_add_screen_ids['bot_messages'].append(sent_message.message_id)


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
    sent_message_add_screen_ids['user_messages'].append(callback_query.message.message_id)
    await delete_previous_messages(callback_query.message)

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
    sent_message_add_screen_ids['bot_messages'].append(sent_message.message_id)



##############################################################
#                Creating a grammar test in ru               #
##############################################################

# Initial handler for entering question text
@router.callback_query(F.data == 'grammar_ru')
async def write_grammar_question_ru(callback_query: CallbackQuery, state: FSMContext):
    sent_message_add_screen_ids['user_messages'].append(callback_query.message.message_id)
    await delete_previous_messages(callback_query.message)

    sent_message = await callback_query.message.answer_photo(
        photo=utils.pictureForTheEditAnGrammerRU,
        caption='Введите текст грамматического вопроса',
        parse_mode=ParseMode.MARKDOWN
    )
    await state.set_state(st.CreatGrammarQuestionsRU.create_question_ru)
    sent_message_add_screen_ids['bot_messages'].append(sent_message.message_id)


# Handler for entering grammar question text
@router.message(st.CreatGrammarQuestionsRU.create_question_ru)
async def get_question_text(message: Message, state: FSMContext):
    question_text = message.text
    await state.update_data(question_text=question_text, options={})

    if message.text == "/start":
        await user_account(message, state)
        return

    sent_message_add_screen_ids['user_messages'].append(message.message_id)
    await delete_previous_messages(message)

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
        sent_message_add_screen_ids['bot_messages'].append(sent_message.message_id)
    else:
        err_sentences = await is_russian_sentence(question_text)
        sent_message = await message.answer_photo(
            photo=utils.pictureForTheEditAnGrammerRU,
            caption=f'_{err_sentences}._\nПожалуйста, исправьте и напишите вопрос заново:',
            parse_mode=ParseMode.MARKDOWN
        )
        await state.set_state(st.CreatGrammarQuestionsRU.create_question_ru)
        sent_message_add_screen_ids['bot_messages'].append(sent_message.message_id)

# General handler for options A, B, V, and G
async def get_option_grammar_ru(message: Message, state: FSMContext, option_key: str, next_state):
    data = await state.get_data()
    options = data.get('options', {})
    options[option_key] = message.text
    await state.update_data(options=options)

    sent_message_add_screen_ids['user_messages'].append(message.message_id)
    await delete_previous_messages(message)

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

    sent_message_add_screen_ids['bot_messages'].append(sent_message.message_id)


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
    sent_message_add_screen_ids['user_messages'].append(callback_query.message.message_id)
    await delete_previous_messages(callback_query.message)

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
    sent_message_add_screen_ids['bot_messages'].append(sent_message.message_id)


# Write kg analogy questions to the DB
@router.callback_query(F.data == 'kg_send_an_analogy')
async def write_analogy_to_db(callback_query: CallbackQuery, state: FSMContext):
    sent_message_add_screen_ids['user_messages'].append(callback_query.message.message_id)
    await delete_previous_messages(callback_query.message)

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
    is_not_have = await rq.write_question(user_id=user_id, subject_id=4, content=question_text, option_a=option_a,
                                          option_b=option_b,
                                          option_v=option_v, option_g=option_g, correct_option=correct_option,
                                          status="pending")
    if is_not_have:
        await rq.add_rubies(telegram_id=user_id, rubies_amount=5)

        sent_message = await callback_query.message.answer_photo(
            photo=utils.picturePlusFiveRubin,
            caption='Сиздин суроо кабыл алынды!'
                    '\n*+5 рубин* 💎 кошулду.',
            reply_markup=kb.to_user_account_kg,
            parse_mode=ParseMode.MARKDOWN
        )
        sent_message_add_screen_ids['bot_messages'].append(sent_message.message_id)
    else:
        sent_message = await callback_query.message.answer_photo(
            photo=utils.pictureBadRequests,
            caption='Сиз жазган суроо базада бар экен!'
                    '\nСураныч, башка суроо киргизиңиз.',
            reply_markup=kb.to_user_account_kg,
            parse_mode=ParseMode.MARKDOWN
        )
        sent_message_add_screen_ids['bot_messages'].append(sent_message.message_id)

# Write ru analogy questions to the DB
@router.callback_query(F.data == 'ru_send_an_analogy')
async def write_analogy_to_db(callback_query: CallbackQuery, state: FSMContext):
    sent_message_add_screen_ids['user_messages'].append(callback_query.message.message_id)
    await delete_previous_messages(callback_query.message)

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
    is_not_have = await rq.write_question(user_id=user_id, subject_id=3, content=question_text, option_a=option_a,
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
        sent_message_add_screen_ids['bot_messages'].append(sent_message.message_id)
    else:
        sent_message = await callback_query.message.answer_photo(
            photo=utils.pictureBadRequests,
            caption='Вопрос, который вы написали, есть в базе данных!'
                    '\nПожалуйста, введите другой вопрос.',
            reply_markup=kb.to_user_account_ru,
            parse_mode=ParseMode.MARKDOWN
        )
        sent_message_add_screen_ids['bot_messages'].append(sent_message.message_id)

# Write ru grammar questions to the DB
@router.callback_query(F.data == 'ru_send_an_grammar')
async def write_grammar_to_db(callback_query: CallbackQuery, state: FSMContext):
    sent_message_add_screen_ids['user_messages'].append(callback_query.message.message_id)
    await delete_previous_messages(callback_query.message)

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
    is_not_have = await rq.write_question(user_id=user_id, subject_id=1, content=question_text, option_a=option_a,
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
        sent_message_add_screen_ids['bot_messages'].append(sent_message.message_id)
    else:
        sent_message = await callback_query.message.answer_photo(
            photo=utils.pictureBadRequests,
            caption='Вопрос, который вы написали, есть в базе данных!'
                    '\nПожалуйста, введите другой вопрос.',
            reply_markup=kb.to_user_account_ru,
            parse_mode=ParseMode.MARKDOWN
        )
        sent_message_add_screen_ids['bot_messages'].append(sent_message.message_id)

# Write kg grammar questions to the DB
@router.callback_query(F.data == 'kg_send_an_grammar')
async def write_grammar_to_db(callback_query: CallbackQuery, state: FSMContext):
    sent_message_add_screen_ids['user_messages'].append(callback_query.message.message_id)
    await delete_previous_messages(callback_query.message)

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
    is_not_have = await rq.write_question(user_id=user_id, subject_id=2, content=question_text, option_a=option_a, option_b=option_b,
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
        sent_message_add_screen_ids['bot_messages'].append(sent_message.message_id)
    else:
        sent_message = await callback_query.message.answer_photo(
            photo=utils.pictureBadRequests,
            caption='Сиз жазган суроо базада бар экен!'
                    '\nСураныч, башка суроо киргизиңиз.',
            reply_markup=kb.to_user_account_kg,
            parse_mode=ParseMode.MARKDOWN
        )
        sent_message_add_screen_ids['bot_messages'].append(sent_message.message_id)