from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

# Languages
languages = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🇰🇬 Кыргызча", callback_data='kg'),
     InlineKeyboardButton(text="🇷🇺 Русский", callback_data='ru')]])