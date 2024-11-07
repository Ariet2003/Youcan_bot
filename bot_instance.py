import os
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv

load_dotenv()
bot = Bot(os.getenv('API_TOKEN'))
dp = Dispatcher()
