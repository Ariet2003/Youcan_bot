from typing import Optional
from sqlalchemy.orm import selectinload
from sqlalchemy import or_, func


from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import async_session
from app.database.models import User, Admin
from sqlalchemy import select, delete

async def set_user(tg_id: str) -> None:
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))

        if not user:
            session.add(User(tg_id=tg_id))
            await session.commit()