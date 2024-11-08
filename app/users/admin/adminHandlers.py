import re

from aiogram.enums import ParseMode
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram import F, Router

from app.users.admin import adminKeyboards as kb
from app.users.admin import adminStates as st
from app import utils
from app.database import requests as rq
from aiogram.fsm.context import FSMContext

from app.users.admin.adminKeyboards import to_admin_account
from app.utils import sent_message_add_screen_ids, router


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

# Administrator's personal account
async def admin_account(message: Message, state: FSMContext):
    sent_message_add_screen_ids['user_messages'].append(message.message_id)
    await delete_previous_messages(message)
    user_tg_id = str(message.chat.id)
    name = await rq.get_user_name(user_tg_id)
    sent_message = await message.answer_photo(
        photo=utils.pictureOfAdminPersonalAccount,
        caption=f'Привет, {name}',
        reply_markup=kb.profile_button,
        parse_mode=ParseMode.HTML)
    sent_message_add_screen_ids['bot_messages'].append(sent_message.message_id)

# Back to personal account
@router.callback_query(F.data.in_('to_home_admin'))
async def go_home_admin(callback_query: CallbackQuery, state: FSMContext):
    sent_message_add_screen_ids['bot_messages'].append(callback_query.message.message_id)
    await admin_account(callback_query.message, state)

# Validate questions
@router.callback_query(F.data == 'validate_questions')
async def validate_questions(callback_query: CallbackQuery, state: FSMContext):
    sent_message_add_screen_ids['user_messages'].append(callback_query.message.message_id)
    await delete_previous_messages(callback_query.message)
    sent_message = await callback_query.message.answer_photo(
        photo=utils.pictureForValidationQuestions,
        caption=f'Выберите дисциплину, в которой вы хотите проверить вопросы.',
        reply_markup=kb.validate_questions,
        parse_mode=ParseMode.HTML)
    sent_message_add_screen_ids['bot_messages'].append(sent_message.message_id)


# Функция для экранирования символов, которые могут вызвать ошибку в Markdown
def escape_markdown(text: str) -> str:
    return re.sub(r'([.*+?^=!:${}()|\[\]\/\\])', r'\\\1', text)

# Handler for initializing grammar question check
@router.callback_query(F.data == 'validate_grammar_ru')
async def validate_grammar_ru(callback_query: CallbackQuery, state: FSMContext):
    sent_message_add_screen_ids['user_messages'].append(callback_query.message.message_id)
    await delete_previous_messages(callback_query.message)
    await state.update_data(subject_id=1)

    question_data = await rq.get_and_review_oldest_pending_question(subject_id=1)
    if question_data:
        question_text = escape_markdown(question_data['question_text'])
        option_a = escape_markdown(question_data['option_a'])
        option_b = escape_markdown(question_data['option_b'])
        option_v = escape_markdown(question_data['option_v'])
        option_g = escape_markdown(question_data['option_g'])

        await state.update_data(question_id=question_data['question_id'])
        sent_message = await callback_query.message.answer(
            text=f"Вопрос: _{question_text}_\n\n"
                 f"    *А\\)* {option_a}\n"
                 f"    *Б\\)* {option_b}\n"
                 f"    *В\\)* {option_v}\n"
                 f"    *Г\\)* {option_g}\n\n"
                 f"    *Правильный ответ:* ||{question_data['correct_option']}||",
            reply_markup=kb.verify_question,
            parse_mode=ParseMode.MARKDOWN_V2
        )

# Handler for initializing grammar question check
@router.callback_query(F.data == 'validate_grammar_kg')
async def validate_grammar_kg(callback_query: CallbackQuery, state: FSMContext):
    sent_message_add_screen_ids['user_messages'].append(callback_query.message.message_id)
    await delete_previous_messages(callback_query.message)
    await state.update_data(subject_id=2)

    question_data = await rq.get_and_review_oldest_pending_question(subject_id=2)
    if question_data:
        question_text = escape_markdown(question_data['question_text'])
        option_a = escape_markdown(question_data['option_a'])
        option_b = escape_markdown(question_data['option_b'])
        option_v = escape_markdown(question_data['option_v'])
        option_g = escape_markdown(question_data['option_g'])

        await state.update_data(question_id=question_data['question_id'])
        sent_message = await callback_query.message.answer(
            text=f"Вопрос: _{question_text}_\n\n"
                 f"    *А\\)* {option_a}\n"
                 f"    *Б\\)* {option_b}\n"
                 f"    *В\\)* {option_v}\n"
                 f"    *Г\\)* {option_g}\n\n"
                 f"    *Правильный ответ:* ||{question_data['correct_option']}||",
            reply_markup=kb.verify_question,
            parse_mode=ParseMode.MARKDOWN_V2
        )

# Handler for initializing analogy question check
@router.callback_query(F.data == 'validate_analogy_ru')
async def validate_analogy_ru(callback_query: CallbackQuery, state: FSMContext):
    sent_message_add_screen_ids['user_messages'].append(callback_query.message.message_id)
    await delete_previous_messages(callback_query.message)
    await state.update_data(subject_id=3)

    question_data = await rq.get_and_review_oldest_pending_question(subject_id=3)
    if question_data:
        question_text = escape_markdown(question_data['question_text'])
        option_a = escape_markdown(question_data['option_a'])
        option_b = escape_markdown(question_data['option_b'])
        option_v = escape_markdown(question_data['option_v'])
        option_g = escape_markdown(question_data['option_g'])

        await state.update_data(question_id=question_data['question_id'])
        sent_message = await callback_query.message.answer(
            text=f"Aналогия: _{question_text}_\n\n"
                 f"    *А\\)* {option_a}\n"
                 f"    *Б\\)* {option_b}\n"
                 f"    *В\\)* {option_v}\n"
                 f"    *Г\\)* {option_g}\n\n"
                 f"    *Правильный ответ:* ||{question_data['correct_option']}||",
            reply_markup=kb.verify_question,
            parse_mode=ParseMode.MARKDOWN_V2
        )

    else:
        sent_message = await callback_query.message.answer(
            text=f'Нет доступных новых вопросов для проверки.',
            reply_markup=kb.to_admin_account,
            parse_mode=ParseMode.HTML)

    sent_message_add_screen_ids['bot_messages'].append(sent_message.message_id)

# Handler for initializing analogy question check
@router.callback_query(F.data == 'validate_analogy_kg')
async def validate_analogy_kg(callback_query: CallbackQuery, state: FSMContext):
    sent_message_add_screen_ids['user_messages'].append(callback_query.message.message_id)
    await delete_previous_messages(callback_query.message)
    await state.update_data(subject_id=4)

    question_data = await rq.get_and_review_oldest_pending_question(subject_id=4)
    if question_data:
        question_text = escape_markdown(question_data['question_text'])
        option_a = escape_markdown(question_data['option_a'])
        option_b = escape_markdown(question_data['option_b'])
        option_v = escape_markdown(question_data['option_v'])
        option_g = escape_markdown(question_data['option_g'])

        await state.update_data(question_id=question_data['question_id'])
        sent_message = await callback_query.message.answer(
            text=f"Aналогия: _{question_text}_\n\n"
                 f"    *А\\)* {option_a}\n"
                 f"    *Б\\)* {option_b}\n"
                 f"    *В\\)* {option_v}\n"
                 f"    *Г\\)* {option_g}\n\n"
                 f"    *Правильный ответ:* ||{question_data['correct_option']}||",
            reply_markup=kb.verify_question,
            parse_mode=ParseMode.MARKDOWN_V2
        )

    else:
        sent_message = await callback_query.message.answer(
            text=f'Нет доступных новых вопросов для проверки.',
            reply_markup=kb.to_admin_account,
            parse_mode=ParseMode.HTML)

    sent_message_add_screen_ids['bot_messages'].append(sent_message.message_id)

# Handler for the "Correct" button - status 'approved'
@router.callback_query(F.data == 'correct_question')
async def approve_question(callback_query: CallbackQuery, state: FSMContext):
    question_data = await state.get_data()
    question_id = question_data.get("question_id")
    subject_id = question_data.get("subject_id", 2)

    if question_id is not None:
        success = await rq.update_question_status(question_id, 'approved')
        if success:
            if subject_id == 2:
                await validate_grammar_kg(callback_query, state)
            else:
                await validate_analogy_kg(callback_query, state)
        else:
            await callback_query.message.answer(text="Произошла ошибка при обновлении статуса вопроса.",
                                                reply_markup=kb.to_admin_account)
    else:
        await callback_query.message.answer(text="ID вопроса не найден в состоянии.",
                                            reply_markup=kb.to_admin_account)

# Handler for the "Incorrect" button - status 'rejected'
@router.callback_query(F.data == 'wrong_question')
async def reject_question(callback_query: CallbackQuery, state: FSMContext):
    question_data = await state.get_data()
    question_id = question_data.get("question_id")
    subject_id = question_data.get("subject_id", 2)

    if question_id is not None:
        success = await rq.update_question_status(question_id, 'rejected')
        if success:
            if subject_id == 2:
                await validate_grammar_kg(callback_query, state)
            else:
                await validate_analogy_kg(callback_query, state)
        else:
            await callback_query.message.answer(text="Произошла ошибка при обновлении статуса вопроса.",
                                                reply_markup=kb.to_admin_account)
    else:
        await callback_query.message.answer(text="ID вопроса не найден в состоянии.",
                                            reply_markup=kb.to_admin_account)

# Handler for the "Personal Account" button - return status 'pending'
@router.callback_query(F.data == 'to_home_admin_in_verify_question')
async def return_to_pending(callback_query: CallbackQuery, state: FSMContext):
    question_data = await state.get_data()
    question_id = question_data.get("question_id")

    if question_id is not None:
        success = await rq.update_question_status(question_id, 'pending')
        if success:
            await admin_account(callback_query.message, state)
        else:
            await callback_query.message.answer(text="Произошла ошибка при обновлении статуса вопроса.",
                                                reply_markup=kb.to_admin_account)
    else:
        await callback_query.message.answer(text="ID вопроса не найден в состоянии.",
                                            reply_markup=kb.to_admin_account)
    await state.clear()

@router.callback_query(F.data == 'add_to_vip')
async def add_to_vip(callback_query: CallbackQuery, state: FSMContext):
    sent_message_add_screen_ids['user_messages'].append(callback_query.message.message_id)
    await delete_previous_messages(callback_query.message)
    sent_message = await callback_query.message.answer_photo(
        photo=utils.pictureForAddUserVIP,
        caption="Отправьте Telegram ID пользователя",
        reply_markup=kb.to_admin_account
    )
    await state.set_state(st.AddVIPUser.write_tg_id)
    sent_message_add_screen_ids['bot_messages'].append(sent_message.message_id)

@router.message(st.AddVIPUser.write_tg_id)
async def add_to_vip_finish(message: Message, state: FSMContext):
    sent_message_add_screen_ids['user_messages'].append(message.message_id)
    await delete_previous_messages(message)
    user_tg_id = message.text

    is_added = await rq.activate_subscription(telegram_id=user_tg_id)

    if is_added:
        sent_message = await message.answer_photo(
            photo=utils.pictureSuccessProces,
            caption="Пользователь успешно добавлен!",
            reply_markup=kb.to_admin_account
        )
        sent_message_add_screen_ids['bot_messages'].append(sent_message.message_id)
    else:
        sent_message = await message.answer_photo(
            photo=utils.pictureErrorProcess,
            caption="Произошла ошибка при добавлении пользователя!"
                    "\nМожет быть уже добавлен в VIP или нету такого пользователя.",
            reply_markup=kb.to_admin_account
        )
        sent_message_add_screen_ids['bot_messages'].append(sent_message.message_id)
    await state.clear()

@router.callback_query(F.data == 'send_notifications')
async def send_notifications(callback_query: CallbackQuery, state: FSMContext):
    sent_message_add_screen_ids['user_messages'].append(callback_query.message.message_id)
    await delete_previous_messages(callback_query.message)
    sent_message = await callback_query.message.answer_photo(
        photo=utils.pictureForNotification,
        caption="Отправьте фотографию для прикрепления к уведомлению.",
        reply_markup=kb.to_admin_account
    )
    await state.set_state(st.SendNotification.add_photo)
    sent_message_add_screen_ids['bot_messages'].append(sent_message.message_id)

@router.message(st.SendNotification.add_photo)
async def send_notifications_write_text(message: Message, state: FSMContext):
    sent_message_add_screen_ids['user_messages'].append(message.message_id)
    await delete_previous_messages(message)
    photo_id = message.photo[-1].file_id
    await state.update_data(photo_id=photo_id)
    sent_message = await message.answer_photo(
        photo=utils.pictureForNotification,
        caption="Напишите текст для уведомления.",
        reply_markup=kb.to_admin_account
    )
    await state.set_state(st.SendNotification.add_text)
    sent_message_add_screen_ids['bot_messages'].append(sent_message.message_id)

@router.message(st.SendNotification.add_text)
async def send_notifications_finish(message: Message, state: FSMContext):
    sent_message_add_screen_ids['user_messages'].append(message.message_id)
    await delete_previous_messages(message)
    text_notification = message.text
    await state.update_data(text_notification=text_notification)
    data_notification = await state.get_data()
    photo_id = data_notification.get("photo_id")
    sent_message = await message.answer_photo(
        photo=photo_id,
        caption=str(text_notification),
        reply_markup=kb.send_notification
    )
    await state.set_state(st.SendNotification.add_text)
    sent_message_add_screen_ids['bot_messages'].append(sent_message.message_id)

@router.callback_query(F.data == 'send_notification_all')
async def send_notification_all(callback_query: CallbackQuery, state: FSMContext):
    sent_message_add_screen_ids['user_messages'].append(callback_query.message.message_id)
    await delete_previous_messages(callback_query.message)
    data_notification = await state.get_data()
    photo_id = data_notification.get("photo_id")
    text_notification = data_notification.get("text_notification")

    # Проверка, был ли передан photo_id и текст, и отправка уведомлений всем пользователям
    sent_message = await callback_query.message.answer("Уведомления отправляются всем пользователям...",
                                                            reply_markup=kb.to_admin_account)
    sent_message_add_screen_ids['bot_messages'].append(sent_message.message_id)

    # Отправка уведомлений всем пользователям
    await rq.send_notification_to_all_users(text_notification, photo_id)

# Statistics
@router.callback_query(F.data == 'statistics')
async def statistics(callback_query: CallbackQuery, state: FSMContext):
    sent_message_add_screen_ids['user_messages'].append(callback_query.message.message_id)
    await delete_previous_messages(callback_query.message)
    sent_message = await callback_query.message.answer_photo(
        photo=utils.pictureForStatistics,
        caption="Выберите раздел для просмотра статистики",
        reply_markup=kb.statistic
    )
    sent_message_add_screen_ids['bot_messages'].append(sent_message.message_id)


@router.callback_query(F.data == 'notification_statistics')
async def notification_statistics(callback_query: CallbackQuery, state: FSMContext):
    sent_message_add_screen_ids['user_messages'].append(callback_query.message.message_id)
    await delete_previous_messages(callback_query.message)

    formatted_notifications = await rq.get_last_50_notifications()

    if formatted_notifications:
        sent_message = await callback_query.message.answer(text=formatted_notifications,
                                            reply_markup=kb.to_admin_account)
        sent_message_add_screen_ids['bot_messages'].append(sent_message.message_id)
    else:
        sent_message = await callback_query.message.answer(text="Не удалось получить данные о уведомлениях.",
                                            reply_markup=kb.to_admin_account)
        sent_message_add_screen_ids['bot_messages'].append(sent_message.message_id)

@router.callback_query(F.data == 'all_statistics')
async def all_statistics(callback_query: CallbackQuery, state: FSMContext):
    sent_message_add_screen_ids['user_messages'].append(callback_query.message.message_id)
    await delete_previous_messages(callback_query.message)

    all_statistics = await rq.get_all_statistics()

    if all_statistics:
        sent_message = await callback_query.message.answer(text=all_statistics,
                                                           reply_markup=kb.to_admin_account)
        sent_message_add_screen_ids['bot_messages'].append(sent_message.message_id)
    else:
        sent_message = await callback_query.message.answer(text="Не удалось получить данные о статистике.",
                                                           reply_markup=kb.to_admin_account)
        sent_message_add_screen_ids['bot_messages'].append(sent_message.message_id)

# Обработчик для отображения списка пользователей
@router.callback_query(F.data == 'show_users')
async def show_users(callback_query: CallbackQuery, state: FSMContext):
    sent_message_add_screen_ids['user_messages'].append(callback_query.message.message_id)
    await delete_previous_messages(callback_query.message)
    data = await state.get_data()
    offset = data.get('offset', 0)
    limit = 50

    # Получаем список пользователей с учетом текущего смещения
    users_list = await rq.get_users_list(offset=offset, limit=limit)

    # Формируем текст сообщения
    if users_list == "⚠️ Пользователи не найдены.":
        message = users_list
    else:
        message = (
            f"📋 Список пользователей (показаны {offset + 1}-{offset + limit}):\n\n{users_list}"
        )

    sent_message = await callback_query.message.answer(
        message,
        parse_mode="Markdown",
        reply_markup=kb.edit_users,
        disable_web_page_preview=True
    )
    # Сохранение текущего смещения в состоянии для навигации
    await state.update_data(offset=offset)
    sent_message_add_screen_ids['bot_messages'].append(sent_message.message_id)

# Обработчики для навигации между страницами пользователей
@router.callback_query(F.data == 'show_users_next')
async def show_users_next(callback_query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    offset = data.get('offset', 0) + 50
    await state.update_data(offset=offset)
    await show_users(callback_query, state)

@router.callback_query(F.data == 'show_users_prev')
async def show_users_prev(callback_query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    offset = max(0, data.get('offset', 0) - 50)
    await state.update_data(offset=offset)
    await show_users(callback_query, state)

@router.callback_query(F.data == 'list_users')
async def list_users(callback_query: CallbackQuery, state: FSMContext):
    sent_message_add_screen_ids['user_messages'].append(callback_query.message.message_id)
    await delete_previous_messages(callback_query.message)
    sent_message = await callback_query.message.answer_photo(
        photo=utils.pictureForListUsers,
        caption="Выберите нужную вам кнопку.",
        reply_markup=kb.list_users
    )

    sent_message_add_screen_ids['bot_messages'].append(sent_message.message_id)


@router.callback_query(F.data == 'delete_user')
async def delete_user(callback_query: CallbackQuery, state: FSMContext):
    sent_message_add_screen_ids['user_messages'].append(callback_query.message.message_id)
    await delete_previous_messages(callback_query.message)

    sent_message = await callback_query.message.answer_photo(
        photo=utils.pictureForListUsers,
        caption="Введите Telegram ID пользователя.",
        reply_markup=kb.to_admin_account
    )

    await state.set_state(st.DeleteUser.write_tg_id)

    sent_message_add_screen_ids['bot_messages'].append(sent_message.message_id)


@router.message(st.DeleteUser.write_tg_id)
async def delete_user_yes_no(message: Message, state: FSMContext):
    user_tg_id = message.text.strip()  # Получаем Telegram ID пользователя

    # Убираем старые сообщения
    sent_message_add_screen_ids['user_messages'].append(message.message_id)
    await delete_previous_messages(message)

    # Попытка удаления пользователя
    is_deleted = await rq.delete_user_by_id(user_tg_id)

    if is_deleted:
        sent_message = await message.answer(
            f"Пользователь с ID {user_tg_id} был удален.",
            reply_markup=kb.to_admin_account
        )
    else:
        sent_message = await message.answer(
            "Не удалось удалить пользователя. Он может не существовать.",
            reply_markup=kb.to_admin_account
        )

    sent_message_add_screen_ids['bot_messages'].append(sent_message.message_id)
    await state.clear()  # Закрываем состояние после обработки