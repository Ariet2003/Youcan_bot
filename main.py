from aiogram import Bot, Dispatcher
from dotenv import load_dotenv
from app.register.registerHandlers import router
from app.database.models import async_main # Если бд
import asyncio
import os

async def main():
    await async_main() # Если бд sqlite
    load_dotenv()
    bot = Bot(os.getenv('API_TOKEN'))
    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit')