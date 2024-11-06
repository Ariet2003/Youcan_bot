from typing import Optional
from sqlalchemy.orm import selectinload
from sqlalchemy import or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.models import async_session
from app.database.models import User, Admin, Question
from sqlalchemy import select, delete
from datetime import datetime
import pytz

# We get the current time in the required time zone
def get_current_time():
    tz = pytz.timezone('Asia/Bishkek')
    return datetime.now(tz)

# Request to check if a user is in the database, if not, then add
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
                created_at=get_current_time(),
                updated_at=get_current_time()
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

# Request to check if an admin is in the database, if not, then add
async def set_admin(telegram_id: str, username: str) -> None:
    async with async_session() as session:
        admin = await session.scalar(select(Admin).where(Admin.telegram_id == telegram_id))

        if not admin:
            new_admin = Admin(
                telegram_id=telegram_id,
                username=username,
                created_at=get_current_time(),
                updated_at=get_current_time()
            )
            session.add(new_admin)
            await session.commit()

# Request to get user language
async def get_user_language(telegram_id: str) -> Optional[str]:
    async with async_session() as session:
        result = await session.execute(
            select(User.language).where(User.telegram_id == telegram_id)
        )
        language = result.scalar_one_or_none()

        return language

# Request to get user name
async def get_user_name(telegram_id: str) -> Optional[str]:
    async with async_session() as session:
        result = await session.execute(
            select(User.name).where(User.telegram_id == telegram_id)
        )
        name = result.scalar_one_or_none()

        return name

# Write analogy questions to the DB
async def write_analogy(user_id: int, subject_id: int, content: str, option_a: str, option_b: str, option_v: str, option_g: str, correct_option: str, status: str = "pending"):
    async with async_session() as session:
        async with session.begin():
            new_question = Question(
                user_id=user_id,
                subject_id=subject_id,
                content=content,
                option_a=option_a,
                option_b=option_b,
                option_v=option_v,
                option_g=option_g,
                correct_option=correct_option,
                status=status,
                created_at=get_current_time()
            )
            session.add(new_question)
            await session.commit()
