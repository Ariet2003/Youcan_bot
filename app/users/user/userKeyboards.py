from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

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
     InlineKeyboardButton(text="Г", callback_data='kg_creating_an_analogy_g')],
    [InlineKeyboardButton(text="Жөнөтүү ➡️", callback_data='kg_send_an_analogy')]
])

# Option buttons for creating an analogy in ru
option_buttons_for_creating_an_analogy_ru = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="A", callback_data='ru_creating_an_analogy_a'),
     InlineKeyboardButton(text="Б", callback_data='ru_creating_an_analogy_b')],
    [InlineKeyboardButton(text="В", callback_data='ru_creating_an_analogy_v'),
     InlineKeyboardButton(text="Г", callback_data='ru_creating_an_analogy_g')],
    [InlineKeyboardButton(text="Отправить ➡️", callback_data='ru_send_an_analogy')]
])

# Buttons for selecting part of an analogy question for editing
buttons_for_selecting_part_of_an_analogy_question_for_editing_kg = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Суроо", callback_data='edit_analogy_question_kg')],
    [InlineKeyboardButton(text="А", callback_data='edit_analogy_a_kg'),
     InlineKeyboardButton(text="Б", callback_data='edit_analogy_b_kg')],
    [InlineKeyboardButton(text="В", callback_data='edit_analogy_v_kg'),
     InlineKeyboardButton(text="Г", callback_data='edit_analogy_g_kg')],
    [InlineKeyboardButton(text="Оңдоп бүттүм", callback_data='finish_edit_analogy_kg')]
])