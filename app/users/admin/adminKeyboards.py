from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

profile_button = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="📜 Вопросы", callback_data='validate_questions'),
     InlineKeyboardButton(text="🌟 Добавить в VIP", callback_data='add_to_vip')],
    [InlineKeyboardButton(text="👥 Пользователи", callback_data='list_users'),
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
    [InlineKeyboardButton(text="📤 Отправить всем пользователям", callback_data='send_notification_all')],
    [InlineKeyboardButton(text="⬅️ Личный кабинет", callback_data='to_home_admin')]
])

statistic = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🔔 Статистика уведомлений", callback_data='notification_statistics')],
    [InlineKeyboardButton(text="📈 Статистика данных", callback_data='all_statistics')],
    [InlineKeyboardButton(text="⬅️ Личный кабинет", callback_data='to_home_admin')]
])

list_users = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="📜 Список пользователей", callback_data="show_users"),
     InlineKeyboardButton(text="🗑️ Удалить пользователя", callback_data="delete_user")],
    [InlineKeyboardButton(text="🔍 Поиск пользователя", callback_data='user_search')],
    [InlineKeyboardButton(text="⬅️ Личный кабинет", callback_data='to_home_admin')]
])

edit_users = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="⬅️ Предыдущая", callback_data="show_users_prev"),
     InlineKeyboardButton(text="Следующая ➡️", callback_data="show_users_next")],
    [InlineKeyboardButton(text="⬅️ Личный кабинет", callback_data='to_home_admin')]
])

admin_seeting = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="👥 Сбросить все VIP", callback_data='reset_all_vip_statuses'),
     InlineKeyboardButton(text="👤 Удалить VIP", callback_data='reset_vip_status')],
    [InlineKeyboardButton(text="🚪 Выйти из админки", callback_data='exit_admin_panel')],
    [InlineKeyboardButton(text="⬅️ Личный кабинет", callback_data='to_home_admin')]
])