from typing import Optional, List
from sqlalchemy import (
    BigInteger, Integer, String, Boolean, ForeignKey, JSON, DECIMAL, TIMESTAMP, func
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from dotenv import load_dotenv
import os

load_dotenv()
engine = create_async_engine(url=os.getenv('SQLITE_URL'))
async_session = async_sessionmaker(engine)

class Base(AsyncAttrs, DeclarativeBase):
    pass

class User(Base):
    __tablename__ = 'users'
    user_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    telegram_id: Mapped[str] = mapped_column(String(200))
    username: Mapped[Optional[str]] = mapped_column(String(150))
    rubies: Mapped[int] = mapped_column(default=0)
    identifier: Mapped[str] = mapped_column(String(6), unique=True)
    subscription_status: Mapped[bool] = mapped_column(Boolean, default=False)
    questions_answered: Mapped[int] = mapped_column(default=0)
    language: Mapped[str] = mapped_column(String(5))  # "ru" или "en"
    created_at: Mapped[TIMESTAMP] = mapped_column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at: Mapped[TIMESTAMP] = mapped_column(TIMESTAMP, onupdate=func.current_timestamp())

class Subject(Base):
    __tablename__ = 'subjects'
    subject_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100))
    language: Mapped[str] = mapped_column(String(5))  # "ru" или "kg"

class Question(Base):
    __tablename__ = 'questions'
    question_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.user_id', ondelete='CASCADE'))
    subject_id: Mapped[int] = mapped_column(ForeignKey('subjects.subject_id', ondelete='CASCADE'))
    content: Mapped[str] = mapped_column(String(1000))
    options: Mapped[dict] = mapped_column(JSON)
    correct_option: Mapped[str] = mapped_column(String(5))
    explanation: Mapped[Optional[str]] = mapped_column(String(4400), nullable=True)
    created_at: Mapped[TIMESTAMP] = mapped_column(TIMESTAMP, server_default=func.current_timestamp())

class UserAnswer(Base):
    __tablename__ = 'user_answers'
    answer_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.user_id', ondelete='CASCADE'))
    question_id: Mapped[int] = mapped_column(ForeignKey('questions.question_id', ondelete='CASCADE'))
    chosen_option: Mapped[str] = mapped_column(String(5))
    is_correct: Mapped[bool] = mapped_column(Boolean)
    rubies_earned: Mapped[int] = mapped_column(default=0)
    answered_at: Mapped[TIMESTAMP] = mapped_column(TIMESTAMP, server_default=func.current_timestamp())

class Duel(Base):
    __tablename__ = 'duels'
    duel_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    creator_id: Mapped[int] = mapped_column(ForeignKey('users.user_id', ondelete='CASCADE'))
    opponent_id: Mapped[Optional[int]] = mapped_column(ForeignKey('users.user_id', ondelete='SET NULL'), nullable=True)
    questions: Mapped[List[int]] = mapped_column(JSON)  # Список идентификаторов вопросов
    creator_score: Mapped[int] = mapped_column(default=0)
    creator_time: Mapped[int] = mapped_column(Integer)  # Время в секундах
    opponent_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    opponent_time: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # Время в секундах
    winner_id: Mapped[Optional[int]] = mapped_column(ForeignKey('users.user_id'), nullable=True)
    created_at: Mapped[TIMESTAMP] = mapped_column(TIMESTAMP, server_default=func.current_timestamp())
    completed_at: Mapped[Optional[TIMESTAMP]] = mapped_column(TIMESTAMP, nullable=True)

class Payment(Base):
    __tablename__ = 'payments'
    payment_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.user_id', ondelete='CASCADE'))
    amount: Mapped[float] = mapped_column(DECIMAL)
    status: Mapped[str] = mapped_column(String(50), default="pending")
    receipt: Mapped[str] = mapped_column(String(500))
    created_at: Mapped[TIMESTAMP] = mapped_column(TIMESTAMP, server_default=func.current_timestamp())
    verified_at: Mapped[Optional[TIMESTAMP]] = mapped_column(TIMESTAMP, nullable=True)

class Feedback(Base):
    __tablename__ = 'feedback'
    feedback_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.user_id', ondelete='CASCADE'))
    message: Mapped[str] = mapped_column(String(1000))
    response: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="pending")
    created_at: Mapped[TIMESTAMP] = mapped_column(TIMESTAMP, server_default=func.current_timestamp())
    responded_at: Mapped[Optional[TIMESTAMP]] = mapped_column(TIMESTAMP, nullable=True)

class Admin(Base):
    __tablename__ = 'admins'
    admin_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    telegram_id: Mapped[str] = mapped_column(String(200))
    username: Mapped[str] = mapped_column(String(150))
    created_at: Mapped[TIMESTAMP] = mapped_column(TIMESTAMP, server_default=func.current_timestamp())

class Statistic(Base):
    __tablename__ = 'statistics'
    stat_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    total_users: Mapped[int] = mapped_column(default=0)
    total_questions: Mapped[int] = mapped_column(default=0)
    total_duels: Mapped[int] = mapped_column(default=0)
    total_rubies_earned: Mapped[int] = mapped_column(default=0)
    total_payments: Mapped[int] = mapped_column(default=0)
    updated_at: Mapped[TIMESTAMP] = mapped_column(TIMESTAMP, server_default=func.current_timestamp())

async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
