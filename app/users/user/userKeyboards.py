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
    [InlineKeyboardButton(text="Изменить ФИО", callback_data='change_nickname_ru'),
     InlineKeyboardButton(text="Мой профиль", callback_data='my_profile_ru')],
    [InlineKeyboardButton(text="⬅️ Личный кабинет", callback_data='to_home_ru')]
])

user_settings_kg = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Тил алмаштыруу", callback_data='change_language_kg'),
     InlineKeyboardButton(text="Номер алмаштыруу", callback_data='change_phone_number_kg')],
    [InlineKeyboardButton(text="Менин статусум", callback_data='current_status_kg'),
     InlineKeyboardButton(text="Колдоо кызматы", callback_data='helpdesk_kg')],
    [InlineKeyboardButton(text="ФИО алмаштыруу", callback_data='change_nickname_kg'),
     InlineKeyboardButton(text="Менин профилим", callback_data='my_profile_kg')],
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

# Клавиатура для первой страницы рейтинга
def rating_buttons_first_page_ru(page: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=" ", callback_data=f" "),
         InlineKeyboardButton(text="Гдя я?", callback_data=f"find_me_in_rating_ru"),
         InlineKeyboardButton(text="➡️", callback_data=f"rating_page_{page + 1}")],
        [InlineKeyboardButton(text="⬅️ Личный кабинет", callback_data='to_home_ru')]
    ])

# Клавиатура для всех других страниц рейтинга
def rating_buttons_other_pages_ru(page: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️", callback_data=f"rating_page_{page - 1}"),
         InlineKeyboardButton(text="Гдя я?", callback_data=f"find_me_in_rating_ru"),
         InlineKeyboardButton(text="➡️", callback_data=f"rating_page_{page + 1}")],
        [InlineKeyboardButton(text="⬅️ Личный кабинет", callback_data='to_home_ru')]
    ])

# Клавиатура для всех других страниц рейтинга
def rating_buttons_last_page_ru(page: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️", callback_data=f"rating_page_{page - 1}"),
         InlineKeyboardButton(text="Гдя я?", callback_data=f"find_me_in_rating_ru"),
         InlineKeyboardButton(text=" ", callback_data=f" ")],
        [InlineKeyboardButton(text="⬅️ Личный кабинет", callback_data='to_home_ru')]
    ])

# Клавиатура для первой страницы рейтинга
def rating_buttons_first_page_kg(page: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=" ", callback_data=f" "),
         InlineKeyboardButton(text="Мени тап", callback_data=f"find_me_in_rating_kg"),
         InlineKeyboardButton(text="➡️", callback_data=f"kg_rating_page_{page + 1}")],
        [InlineKeyboardButton(text="⬅️ Өздүк бөлмөгө", callback_data='to_home_kg')]
    ])

# Клавиатура для всех других страниц рейтинга
def rating_buttons_other_pages_kg(page: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️", callback_data=f"kg_rating_page_{page - 1}"),
         InlineKeyboardButton(text="Мени тап", callback_data=f"find_me_in_rating_kg"),
         InlineKeyboardButton(text="➡️", callback_data=f"kg_rating_page_{page + 1}")],
        [InlineKeyboardButton(text="⬅️ Өздүк бөлмөгө", callback_data='to_home_kg')]
    ])

# Клавиатура для всех других страниц рейтинга
def rating_buttons_last_page_kg(page: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️", callback_data=f"kg_rating_page_{page - 1}"),
         InlineKeyboardButton(text="Мени тап", callback_data=f"find_me_in_rating_kg"),
         InlineKeyboardButton(text=" ", callback_data=f" ")],
        [InlineKeyboardButton(text="⬅️ Өздүк бөлмөгө", callback_data='to_home_kg')]
    ])

# _______________________________________________________________________________

select_subject_ru = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="📋 Аналогия", callback_data='take_analogy_ru'),
     InlineKeyboardButton(text="📜 Грамматика", callback_data='take_grammar_ru')],
    [InlineKeyboardButton(text="⬅️ Личный кабинет", callback_data='to_home_ru')]
])

select_subject_kg = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="📋 Аналогия", callback_data='take_analogy_kg'),
     InlineKeyboardButton(text="📜 Грамматика", callback_data='take_grammar_kg')],
    [InlineKeyboardButton(text="⬅️ Өздүк бөлмөгө", callback_data='to_home_kg')]
])

def generate_answer_keyboard_ru(question_id: int, option_a: str, option_b: str, option_v: str, option_g: str) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"{option_a}", callback_data=f"question_{question_id}_A"),
         InlineKeyboardButton(text=f"{option_b}", callback_data=f"question_{question_id}_B")],
        [InlineKeyboardButton(text=f"{option_v}", callback_data=f"question_{question_id}_V"),
         InlineKeyboardButton(text=f"{option_g}", callback_data=f"question_{question_id}_G")],
        [InlineKeyboardButton(text="⬅️ Личный кабинет", callback_data='to_home_ru')]
    ])
    return keyboard

def next_analogy_question_button(question_id: int):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✨ Разбор вопроса", callback_data=f'analysis_of_the_issue_ru_analogy_{question_id}'),
         InlineKeyboardButton(text="Следующий ➡️", callback_data='next_analogy_question')],
        [InlineKeyboardButton(text="⬅️ Личный кабинет", callback_data='to_home_ru')]
    ])
    return keyboard

def generate_answer_keyboard_ru_grammar(question_id: int, option_a: str, option_b: str, option_v: str, option_g: str) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"{option_a}", callback_data=f"ru_grammar_question_{question_id}_A"),
         InlineKeyboardButton(text=f"{option_b}", callback_data=f"ru_grammar_question_{question_id}_B")],
        [InlineKeyboardButton(text=f"{option_v}", callback_data=f"ru_grammar_question_{question_id}_V"),
         InlineKeyboardButton(text=f"{option_g}", callback_data=f"ru_grammar_question_{question_id}_G")],
        [InlineKeyboardButton(text="⬅️ Личный кабинет", callback_data='to_home_ru')]
    ])
    return keyboard

def next_analogy_grammar_button(question_id: int):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✨ Разбор вопроса", callback_data=f'analysis_of_the_issue_ru_grammar_{question_id}'),
         InlineKeyboardButton(text="Следующий ➡️", callback_data='next_grammar_question')],
        [InlineKeyboardButton(text="⬅️ Личный кабинет", callback_data='to_home_ru')]
    ])
    return keyboard

def generate_answer_keyboard_kg_analogy(question_id: int, option_a: str, option_b: str, option_v: str, option_g: str) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"{option_a}", callback_data=f"kg_analogy_question_{question_id}_A"),
         InlineKeyboardButton(text=f"{option_b}", callback_data=f"kg_analogy_question_{question_id}_B")],
        [InlineKeyboardButton(text=f"{option_v}", callback_data=f"kg_analogy_question_{question_id}_V"),
         InlineKeyboardButton(text=f"{option_g}", callback_data=f"kg_analogy_question_{question_id}_G")],
        [InlineKeyboardButton(text="⬅️ Өздүк бөлмөгө", callback_data='to_home_kg')]
    ])
    return keyboard

def next_analogy_question_kg_button(question_id: int):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✨ Суроону талдоо", callback_data=f'analysis_of_the_issue_kg_analogy_{question_id}'),
         InlineKeyboardButton(text="Кийинки ➡️", callback_data='next_analogy_kg_question')],
        [InlineKeyboardButton(text="⬅️ Өздүк бөлмөгө", callback_data='to_home_kg')]
    ])
    return keyboard

def generate_answer_keyboard_kg_grammar(question_id: int, option_a: str, option_b: str, option_v: str, option_g: str) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"{option_a}", callback_data=f"kg_grammar_question_{question_id}_A"),
         InlineKeyboardButton(text=f"{option_b}", callback_data=f"kg_grammar_question_{question_id}_B")],
        [InlineKeyboardButton(text=f"{option_v}", callback_data=f"kg_grammar_question_{question_id}_V"),
         InlineKeyboardButton(text=f"{option_g}", callback_data=f"kg_grammar_question_{question_id}_G")],
        [InlineKeyboardButton(text="⬅️ Өздүк бөлмөгө", callback_data='to_home_kg')]
    ])
    return keyboard

def next_grammar_kg_button(question_id: int):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✨ Суроону талдоо", callback_data=f'analysis_of_the_issue_kg_grammar_{question_id}'),
         InlineKeyboardButton(text="Кийинки ➡️", callback_data='next_grammar_question_kg')],
        [InlineKeyboardButton(text="⬅️ Өздүк бөлмөгө", callback_data='to_home_kg')]
    ])
    return keyboard

take_the_test_again_analogy_ru = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="↪️ Пройти тест заново", callback_data='take_the_test_again_analogy_ru')],
    [InlineKeyboardButton(text="⬅️ Личный кабинет", callback_data='to_home_ru')]
])

take_the_test_again_grammar_ru = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="↪️ Пройти тест заново", callback_data='take_the_test_again_grammar_ru')],
    [InlineKeyboardButton(text="⬅️ Личный кабинет", callback_data='to_home_ru')]
])

take_the_test_again_analogy_kg = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="↪️ Тестти кайрадан баштоо", callback_data='take_the_test_again_analogy_kg')],
    [InlineKeyboardButton(text="⬅️ Өздүк бөлмөгө", callback_data='to_home_kg')]
])

take_the_test_again_grammar_kg = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="↪️ Тестти кайрадан баштоо", callback_data='take_the_test_again_grammar_kg')],
    [InlineKeyboardButton(text="⬅️ Өздүк бөлмөгө", callback_data='to_home_kg')]
])

def go_to_question_result(question_id: int, question_type: str, question_lenguage: str) -> InlineKeyboardMarkup:
    if question_lenguage == 'kg':
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⬅️ Суроого кайтуу", callback_data=f'go_to_question_result_{question_type}_{question_lenguage}_{question_id}')],
            [InlineKeyboardButton(text="⬅️ Өздүк бөлмөгө", callback_data='to_home_kg')]
        ])
    else:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⬅️ Вернутся к вопросу",callback_data=f'go_to_question_result_{question_type}_{question_lenguage}_{question_id}')],
            [InlineKeyboardButton(text="⬅️ Личный кабинет", callback_data='to_home_ru')]
        ])
    return keyboard

duel_menu_kg = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🗡️ Баштаа", callback_data='duel_with_random_kg')],
    [InlineKeyboardButton(text="⬅️ Өздүк бөлмөгө", callback_data='to_home_kg')]
])

duel_menu_ru = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🗡️ Начать", callback_data='duel_with_random_ru')],
    [InlineKeyboardButton(text="⬅️ Личный кабинет", callback_data='to_home_ru')]
])

def duel_question_keyboard_kg(question_id: int, numerator: int) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="А", callback_data=f'duel_question_kg_{numerator}_{question_id}_a'),
         InlineKeyboardButton(text="Б", callback_data=f'duel_question_kg_{numerator}_{question_id}_b')],
        [InlineKeyboardButton(text="В", callback_data=f'duel_question_kg_{numerator}_{question_id}_v'),
         InlineKeyboardButton(text="Г", callback_data=f'duel_question_kg_{numerator}_{question_id}_g')]
    ])
    return keyboard

def duel_question_keyboard_ru(question_id: int, numerator: int) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="А", callback_data=f'duel_question_ru_{numerator}_{question_id}_a'),
         InlineKeyboardButton(text="Б", callback_data=f'duel_question_ru_{numerator}_{question_id}_b')],
        [InlineKeyboardButton(text="В", callback_data=f'duel_question_ru_{numerator}_{question_id}_v'),
         InlineKeyboardButton(text="Г", callback_data=f'duel_question_ru_{numerator}_{question_id}_g')]
    ])
    return keyboard