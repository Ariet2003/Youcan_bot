from typing import Optional
from sqlalchemy.orm import selectinload
from sqlalchemy import or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.models import async_session
from app.database.models import User, Admin
from sqlalchemy import select, delete
from datetime import datetime
import pytz

# We get the current time in the required time zone
def get_current_time():
    tz = pytz.timezone('Asia/Bishkek')
    return datetime.now(tz)

# Request to check if a user is in the database
async def set_user(telegram_id: str, username: str, name: str, identifier: str, language: str, phone_number: str) -> None:
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.telegram_id == telegram_id))

        if not user:
            session.add(User(
                telegram_id=telegram_id,
                username=username,
                name=name,
                identifier=identifier,
                language=language,
                phone_number=phone_number,
                created_at=get_current_time(),  # Используем текущее время
                updated_at=get_current_time()   # Используем текущее время
            ))
            await session.commit()


# Request to check if you are an administrator
async def check_admin(telegram_id: str) -> bool:
    async with async_session() as session:
        result = await session.execute(
            select(Admin).where(Admin.telegram_id == telegram_id)
        )
        admin = result.scalar_one_or_none()

        return admin is not None

# Request to check if you are a user
async def check_user(telegram_id: str) -> bool:
    async with async_session() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = result.scalar_one_or_none()

        return user is not None