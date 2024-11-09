from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from urllib.parse import quote

from app import utils

# User personal account buttons in Kyrgyz
profile_button_kg = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="✏️ Тест түзүү", callback_data='creat_test_kg'),
     InlineKeyboardButton(text="🚀 Тест тапшыруу", callback_data='take_test_kg')],
    [InlineKeyboardButton(text="🌟 Рейтинг", callback_data='rating_kg'),
     InlineKeyboardButton(text="⚔️ Дуэль", callback_data='duel_kg')],
    [InlineKeyboardButton(text="⚙️ Орнотуулар", callback_data='settings_kg'),
     InlineKeyboardButton(text="🎟️ VIPке кирүү", callback_data='vip_kg')]])

# User personal account buttons in Russian
profile_button_ru = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="✏️ Создать тест", callback_data='creat_test_ru'),
     InlineKeyboardButton(text="🚀 Пройти тест", callback_data='take_test_ru')],
    [InlineKeyboardButton(text="🌟 Рейтинг", callback_data='rating_ru'),
     InlineKeyboardButton(text="⚔️ Дуэль", callback_data='duel_ru')],
    [InlineKeyboardButton(text="⚙️ Настройки", callback_data='settings_ru'),
     InlineKeyboardButton(text="🎟️ Доступ к VIP", callback_data='vip_ru')]])

# Buttons for selecting an item in Russion
subjects_ru = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="📋 Аналогия", callback_data='analogy_ru'),
     InlineKeyboardButton(text="📜 Грамматика", callback_data='grammar_ru')],
    [InlineKeyboardButton(text="⬅️ Назад", callback_data='to_home_ru')]
])

# Buttons for selecting an item in Kyrgyz
subjects_kg = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="📋 Аналогия", callback_data='analogy_kg'),
     InlineKeyboardButton(text="📜 Грамматика", callback_data='grammar_kg')],
    [InlineKeyboardButton(text="⬅️ Артка", callback_data='to_home_kg')]
])

# Option buttons for creating an analogy in kg
option_buttons_for_creating_an_analogy_kg = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="A", callback_data='kg_creating_an_analogy_a'),
     InlineKeyboardButton(text="Б", callback_data='kg_creating_an_analogy_b')],
    [InlineKeyboardButton(text="В", callback_data='kg_creating_an_analogy_v'),
     InlineKeyboardButton(text="Г", callback_data='kg_creating_an_analogy_g')]
])

# Option buttons for creating an analogy in kg finish
option_buttons_for_creating_an_analogy_kg_finish = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="A", callback_data='kg_creating_an_analogy_a'),
     InlineKeyboardButton(text="Б", callback_data='kg_creating_an_analogy_b')],
    [InlineKeyboardButton(text="В", callback_data='kg_creating_an_analogy_v'),
     InlineKeyboardButton(text="Г", callback_data='kg_creating_an_analogy_g')],
    [InlineKeyboardButton(text="Жөнөтүү ➡️", callback_data='kg_send_an_analogy')]
])

# Option buttons for creating an analogy in ru
option_buttons_for_creating_an_analogy_ru = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="A", callback_data='ru_creating_an_analogy_a'),
     InlineKeyboardButton(text="Б", callback_data='ru_creating_an_analogy_b')],
    [InlineKeyboardButton(text="В", callback_data='ru_creating_an_analogy_v'),
     InlineKeyboardButton(text="Г", callback_data='ru_creating_an_analogy_g')]
])

# Option buttons for creating an analogy in ru finish
option_buttons_for_creating_an_analogy_ru_finish = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="A", callback_data='ru_creating_an_analogy_a'),
     InlineKeyboardButton(text="Б", callback_data='ru_creating_an_analogy_b')],
    [InlineKeyboardButton(text="В", callback_data='ru_creating_an_analogy_v'),
     InlineKeyboardButton(text="Г", callback_data='ru_creating_an_analogy_g')],
    [InlineKeyboardButton(text="Отправить ➡️", callback_data='ru_send_an_analogy')]
])

# Option buttons for creating a grammar in kg
option_buttons_for_creating_a_grammar_kg = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="A", callback_data='kg_creating_an_grammar_a'),
     InlineKeyboardButton(text="Б", callback_data='kg_creating_an_grammar_b')],
    [InlineKeyboardButton(text="В", callback_data='kg_creating_an_grammar_v'),
     InlineKeyboardButton(text="Г", callback_data='kg_creating_an_grammar_g')]
])

# Option buttons for creating a grammar in kg finish
option_buttons_for_creating_a_grammar_kg_finish = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="A", callback_data='kg_creating_an_grammar_a'),
     InlineKeyboardButton(text="Б", callback_data='kg_creating_an_grammar_b')],
    [InlineKeyboardButton(text="В", callback_data='kg_creating_an_grammar_v'),
     InlineKeyboardButton(text="Г", callback_data='kg_creating_an_grammar_g')],
    [InlineKeyboardButton(text="Жөнөтүү ➡️", callback_data='kg_send_an_grammar')]
])

# Option buttons for creating a grammar in kg
option_buttons_for_creating_a_grammar_ru = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="A", callback_data='ru_creating_an_grammar_a'),
     InlineKeyboardButton(text="Б", callback_data='ru_creating_an_grammar_b')],
    [InlineKeyboardButton(text="В", callback_data='ru_creating_an_grammar_v'),
     InlineKeyboardButton(text="Г", callback_data='ru_creating_an_grammar_g')]
])

# Option buttons for creating a grammar in kg finish
option_buttons_for_creating_a_grammar_ru_finish = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="A", callback_data='ru_creating_an_grammar_a'),
     InlineKeyboardButton(text="Б", callback_data='ru_creating_an_grammar_b')],
    [InlineKeyboardButton(text="В", callback_data='ru_creating_an_grammar_v'),
     InlineKeyboardButton(text="Г", callback_data='ru_creating_an_grammar_g')],
    [InlineKeyboardButton(text="Отправить ➡️", callback_data='ru_send_an_grammar')]
])

# To user account kg
to_user_account_kg = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="⬅️ Өздүк бөлмөгө", callback_data='to_home_kg')]
])

# To user account ru
to_user_account_ru = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="⬅️ Личный кабинет", callback_data='to_home_ru')]
])

to_user_account_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="⬅️ Артка/Назад", callback_data="back_to_account")]
])


# Формируем сообщение для передачи в WhatsApp
def get_whatsapp_link_ru(telegram_id: str):
    phone_number = utils.PhoneNumberAdmin
    message = f"Здравствуйте! Хочу приобрести VIP статус. Мой Telegram ID: {telegram_id}"
    encoded_message = quote(message)  # Кодируем сообщение для URL
    return f"https://wa.me/{phone_number}?text={encoded_message}"

# Клавиатура с кнопкой для перехода в WhatsApp
def whatsapp_button_ru(telegram_id: str):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Whatsapp", url=get_whatsapp_link_ru(telegram_id))],
        [InlineKeyboardButton(text="⬅️ Личный кабинет", callback_data='to_home_ru')]
    ])

# Формируем сообщение для передачи в WhatsApp
def get_whatsapp_link_kg(telegram_id: str):
    phone_number = utils.PhoneNumberAdmin
    message = f"Саламатсызбы! Мен VIP статусун сатып алгым келет. Менин Telegram ID: {telegram_id}"
    encoded_message = quote(message)  # Кодируем сообщение для URL
    return f"https://wa.me/{phone_number}?text={encoded_message}"

# Клавиатура с кнопкой для перехода в WhatsApp
def whatsapp_button_kg(telegram_id: str):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Whatsapp", url=get_whatsapp_link_kg(telegram_id))],
        [InlineKeyboardButton(text="⬅️ Өздүк бөлмөгө", callback_data='to_home_kg')]
    ])

user_settings_ru = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Изменить язык", callback_data='change_language_ru'),
     InlineKeyboardButton(text="Изменить номер", callback_data='change_phone_number_ru')],
    [InlineKeyboardButton(text="Текущий статус", callback_data='current_status_ru'),
     InlineKeyboardButton(text="Поддержка", callback_data='helpdesk_ru')],
    [InlineKeyboardButton(text="Изменить никнейм/ФИО", callback_data='change_nickname_ru')],
    [InlineKeyboardButton(text="⬅️ Личный кабинет", callback_data='to_home_ru')]
])

user_settings_kg = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Тил алмаштыруу", callback_data='change_language_kg'),
     InlineKeyboardButton(text="Номер алмаштыруу", callback_data='change_phone_number_kg')],
    [InlineKeyboardButton(text="Менин статусум", callback_data='current_status_kg'),
     InlineKeyboardButton(text="Колдоо кызматы", callback_data='helpdesk_kg')],
    [InlineKeyboardButton(text="ФИО алмаштыруу", callback_data='change_nickname_kg')],
    [InlineKeyboardButton(text="⬅️ Өздүк бөлмөгө", callback_data='to_home_kg')]
])

whatsapp_button_without_text_kg = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Whatsapp", url=f"https://wa.me/{utils.PhoneNumberAdmin}")],
    [InlineKeyboardButton(text="⬅️ Өздүк бөлмөгө", callback_data='to_home_kg')]
])

whatsapp_button_without_text_ru = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Whatsapp", url=f"https://wa.me/{utils.PhoneNumberAdmin}")],
    [InlineKeyboardButton(text="⬅️ Личный кабинет", callback_data='to_home_ru')]
])