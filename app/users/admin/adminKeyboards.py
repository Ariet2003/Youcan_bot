from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

profile_button = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="📜 Вопросы", callback_data='validate_questions'),
     InlineKeyboardButton(text="🌟 Добавить в VIP", callback_data='add_to_vip')],
    [InlineKeyboardButton(text="👥 Пользователи", callback_data='users'),
     InlineKeyboardButton(text="🔔 Уведомления", callback_data='send_notifications')],
    [InlineKeyboardButton(text="⚙️ Настройки", callback_data='admin_settings'),
     InlineKeyboardButton(text="📊 Статистика", callback_data='statistics')]
])

validate_questions = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🇰🇬 Аналогия", callback_data='validate_analogy_kg'),
     InlineKeyboardButton(text="🇷🇺 Аналогия", callback_data='validate_analogy_ru')],
    [InlineKeyboardButton(text="🇰🇬 Грамматика", callback_data='validate_grammar_kg'),
     InlineKeyboardButton(text="🇷🇺 Грамматика", callback_data='validate_grammar_ru')],
    [InlineKeyboardButton(text="⬅️ Назад", callback_data='to_home_admin')]
])

# To user account ru
to_admin_account = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="⬅️ Личный кабинет", callback_data='to_home_admin'),]
])

# Verify the question
verify_question = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="✅ Правильно", callback_data='correct_question'),
     InlineKeyboardButton(text="❌ Не правильно", callback_data='wrong_question')],
    [InlineKeyboardButton(text="⬅️ Личный кабинет", callback_data='to_home_admin_in_verify_question')]
])

send_notification = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="📤 Отправить всем пользователям", callback_data='send_notification_all'),
     InlineKeyboardButton(text="⬅️ Личный кабинет", callback_data='to_home_admin')]
])
