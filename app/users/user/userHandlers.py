from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram import F, Router
from app.database import requests as rq
from aiogram.fsm.context import FSMContext
from app.utils import sent_message_add_screen_ids

router = Router()



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
            await message.bot.delete_message(chat_id=message.chat.id, message_id=msg_id)
        except Exception as e:
            print(f"Не удалось удалить сообщение {msg_id}: {e}")
    sent_message_add_screen_ids['bot_messages'].clear()

async def user_account(message: Message, state: FSMContext):
    sent_message_add_screen_ids['user_messages'].append(message.message_id)
    await delete_previous_messages(message)
    sent_message = await message.answer(text="Личный кабинет пользователя")
    sent_message_add_screen_ids['bot_messages'].append(sent_message.message_id)