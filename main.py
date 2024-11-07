# main.py
from aiogram import Dispatcher
from app.register.registerHandlers import router
from app.database.models import async_main
from bot_instance import bot, dp  # Импортируем bot и dp
import asyncio

async def main():
    await async_main()  # Если бд sqlite
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit')
