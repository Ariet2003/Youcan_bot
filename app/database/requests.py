from typing import Optional
from sqlalchemy.orm import selectinload
from sqlalchemy import or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.models import async_session
from app.database.models import User, Admin, Question, Notification, Duel
from app.users.user import userKeyboards as kb
from bot_instance import bot
from sqlalchemy import select, delete
from datetime import datetime
from sqlalchemy import update
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
async def write_question(user_id: int, subject_id: int, content: str, option_a: str, option_b: str, option_v: str, option_g: str, correct_option: str, status: str = "pending") -> bool:
    async with async_session() as session:
        async with session.begin():
            # Проверка существования вопроса с такими же текстом и вариантами ответов
            existing_question = await session.execute(
                select(Question)
                .where(
                    Question.content == content,
                    Question.option_a == option_a,
                    Question.option_b == option_b,
                    Question.option_v == option_v,
                    Question.option_g == option_g
                )
            )
            # Если вопрос найден, возвращаем False
            if existing_question.scalars().first():
                return False

            # Создаем новый вопрос, так как аналогичного не найдено
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

            # Возвращаем True, чтобы показать, что вопрос был успешно добавлен
            return True

# Update the number of rubies the user has
async def add_rubies(telegram_id: str, rubies_amount: int):
    async with async_session() as session:
        async with session.begin():
            await session.execute(
                update(User)
                .where(User.telegram_id == telegram_id)
                .values(rubies=User.rubies + rubies_amount)
            )
            await session.commit()


# Request to get and review the oldest pending question for a specific subject_id (by largest question_id)
async def get_and_review_oldest_pending_question(subject_id: int) -> Optional[dict]:
    async with async_session() as session:
        # Начинаем транзакцию
        async with session.begin():
            # Запрос для получения самого большого question_id с статусом 'pending' и указанным subject_id
            result = await session.execute(
                select(Question)
                .filter(Question.status == 'pending', Question.subject_id == subject_id)
                .order_by(Question.question_id.desc())  # Сортировка по question_id в убывающем порядке
            )
            question = result.scalars().first()

            if question:
                # После завершения транзакции продолжаем выполнять запросы вне контекста транзакции
                async with async_session() as session:
                    # Обновляем статус вопроса на 'under review'
                    await session.execute(
                        update(Question)
                        .where(Question.question_id == question.question_id)
                        .values(status='under review')
                    )
                    await session.commit()

                return {
                    'question_id': question.question_id,
                    'question_text': question.content,
                    'option_a': question.option_a,
                    'option_b': question.option_b,
                    'option_v': question.option_v,
                    'option_g': question.option_g,
                    'correct_option': question.correct_option
                }

    return None  # Если нет вопросов со статусом 'pending' и указанным subject_id



# General function to update the status of a question
async def update_question_status(question_id: int, status: str) -> bool:
    try:
        async with async_session() as session:
            async with session.begin():
                await session.execute(
                    update(Question)
                    .where(Question.question_id == question_id)
                    .values(status=status)
                )
                await session.commit()
        return True
    except Exception as e:
        return False


# Update subscription_status to True, return False if already True
async def activate_subscription(telegram_id: str) -> bool:
    async with async_session() as session:
        async with session.begin():
            user = await session.execute(
                select(User).where(User.telegram_id == telegram_id)
            )
            user = user.scalars().first()

            if user and user.subscription_status:
                return False

            result = await session.execute(
                update(User)
                .where(User.telegram_id == telegram_id)
                .values(subscription_status=True)
            )
            await session.commit()
            return result.rowcount > 0


# Функция для отправки уведомлений всем пользователям, кроме администраторов
async def send_notification_to_all_users(text_notification: str, photo_id: str = None):
    notification = Notification(
        text=text_notification,
        photo_id=photo_id,
        total_users=0,
        sent_count=0,
        updated_at=get_current_time(),
        created_at=get_current_time()
    )

    async with async_session() as session:
        async with session.begin():
            user_result = await session.execute(select(User.telegram_id))
            all_users = set(user_result.scalars().all())

            admin_result = await session.execute(select(Admin.telegram_id))
            admins = set(admin_result.scalars().all())

            users_to_notify = all_users - admins

            notification.total_users = len(users_to_notify)

            session.add(notification)
            await session.flush()

            for telegram_id in users_to_notify:
                try:
                    await bot.send_photo(
                        chat_id=telegram_id,
                        photo=photo_id,
                        caption=text_notification,
                        reply_markup=kb.to_user_account_kb
                    )

                    notification.sent_count += 1
                except Exception as e:
                    print(f"Не удалось отправить сообщение пользователю {telegram_id}: {e}")

            session.add(notification)
            await session.commit()

async def get_last_50_notifications():
    try:
        async with async_session() as session:
            # Получаем последние 50 уведомлений
            result = await session.execute(
                select(Notification)
                .order_by(Notification.created_at.desc())  # Сортируем по дате создания
                .limit(50)  # Ограничиваем 50 последними записями
            )

            # Извлекаем уведомления
            notifications = result.scalars().all()

            # Формируем красивое отображение уведомлений с эмодзи
            formatted_notifications = ""
            for notification in notifications:
                # Обрезаем текст уведомления до 40 символов
                text_preview = notification.text[:40] + "..." if len(notification.text) > 40 else notification.text

                formatted_notifications += f"📩: {text_preview}\n"
                formatted_notifications += f"👥: {notification.total_users} | ✅: {notification.sent_count} | ⏰: {notification.created_at.strftime('%Y-%m-%d %H:%M:%S')}\n"
                formatted_notifications += "-" * 65 + "\n"

            return formatted_notifications

    except Exception as e:
        print(f"Ошибка при получении уведомлений: {e}")
        return None


# Function for getting general statistics
async def get_all_statistics() -> str:
    try:
        async with async_session() as session:
            async with session.begin():
                # Counting the total number of users
                total_users = await session.scalar(select(func.count(User.user_id)))

                # Counting the number of VIP (paid) users
                total_vip_users = await session.scalar(
                    select(func.count(User.user_id)).where(User.subscription_status == True)
                )

                # Counting the total number of questions
                total_questions = await session.scalar(select(func.count(Question.question_id)))

                # Counting the number of questions by category (subject_id)
                kyrgyz_analogy_questions = await session.scalar(
                    select(func.count(Question.question_id)).where(Question.subject_id == 4)
                )
                russian_analogy_questions = await session.scalar(
                    select(func.count(Question.question_id)).where(Question.subject_id == 3)
                )
                kyrgyz_grammar_questions = await session.scalar(
                    select(func.count(Question.question_id)).where(Question.subject_id == 2)
                )
                russian_grammar_questions = await session.scalar(
                    select(func.count(Question.question_id)).where(Question.subject_id == 1)
                )

                # Counting the number of questions by status
                approved_questions = await session.scalar(
                    select(func.count(Question.question_id)).where(Question.status == "approved")
                )
                rejected_questions = await session.scalar(
                    select(func.count(Question.question_id)).where(Question.status == "rejected")
                )
                pending_questions = await session.scalar(
                    select(func.count(Question.question_id)).where(Question.status == "pending")
                )

                # Counting the total number of duels and the number of pending duels
                total_duels = await session.scalar(select(func.count(Duel.duel_id)))
                pending_duels = await session.scalar(
                    select(func.count(Duel.duel_id)).where(Duel.opponent_id == None)
                )

                # Formatting statistics
                statistics = (
                    f"Общая статистика:\n"
                    f"👥 Всего пользователей: {total_users}\n"
                    f"👑 VIP (платные) пользователи: {total_vip_users}\n\n"
                    f"📄 Всего вопросов: {total_questions}\n"
                    f"🇰🇬 Кыргызская аналогия: {kyrgyz_analogy_questions}\n"
                    f"🇷🇺 Русская аналогия: {russian_analogy_questions}\n"
                    f"🇰🇬 Кыргызская грамматика: {kyrgyz_grammar_questions}\n"
                    f"🇷🇺 Русская грамматика: {russian_grammar_questions}\n\n"
                    f"✅ Подтверждено: {approved_questions}\n"
                    f"❌ Отклонено: {rejected_questions}\n"
                    f"⏳ В ожидании: {pending_questions}\n\n"
                    f"⚔️ Всего дуэлей: {total_duels}\n"
                    f"⏳ Дуэли в ожидании: {pending_duels}"
                )

                return statistics

    except Exception as e:
        return f"Ошибка при получении статистики: {e}"


# Функция для получения списка пользователей с учетом пагинации
async def get_users_list(offset: int = 0, limit: int = 50):
    try:
        async with async_session() as session:
            async with session.begin():
                # Запрос пользователей с учетом лимита и смещения
                result = await session.execute(
                    select(User)
                    .offset(offset)
                    .limit(limit)
                )
                users = result.scalars().all()

                # Проверка наличия пользователей
                if not users:
                    return "⚠️ Пользователи не найдены."

                # Форматирование пользователей
                users_list = []
                for index, user in enumerate(users, start=offset + 1):
                    subscription_status = "VIP" if user.subscription_status else " - "

                    # Скрытая ссылка на WhatsApp
                    whatsapp_link = f"[WhatsApp](https://wa.me/{user.phone_number})" if user.phone_number else "N/A"

                    # Замена кода языка на флаг
                    language_flag = "🇷🇺" if user.language == "ru" else "🇰🇬" if user.language == "kg" else "N/A"

                    # Информация о пользователе с добавлением скрытой ссылки на WhatsApp и флага языка
                    user_info = (
                        f"{index}. [{user.name}](tg://user?id={user.telegram_id}) ● {user.telegram_id} ● "
                        f"{user.rubies} 💎 ● {subscription_status} ● {language_flag} ● {whatsapp_link}"
                    )
                    users_list.append(user_info)

                return "\n".join(users_list)

    except Exception as e:
        return f"Ошибка при получении списка пользователей: {e}"

# Функция для удаления пользователя по ID
async def delete_user_by_id(telegram_id: str) -> bool:
    try:
        async with async_session() as session:
            async with session.begin():
                user = await session.execute(
                    select(User).where(User.telegram_id == telegram_id)
                )
                user = user.scalars().first()

                if not user:
                    return False  # Пользователь не найден

                result = await session.execute(
                    delete(User).where(User.telegram_id == telegram_id)
                )
                await session.commit()
                return result.rowcount > 0  # Если удалено хотя бы 1 запись, вернем True

    except Exception as e:
        print(f"Ошибка при удалении пользователя: {e}")
        return False


# Функция для поиска пользователей по ФИО, tg_id или номеру телефона
async def search_users(search_query: str) -> list:
    try:
        async with async_session() as session:
            async with session.begin():
                # Поиск по ФИО, telegram_id или телефону
                search_results = await session.execute(
                    select(User).where(
                        (User.name.ilike(f"%{search_query}%")) |
                        (User.telegram_id.ilike(f"%{search_query}%")) |
                        (User.phone_number.ilike(f"%{search_query}%"))
                    )
                )
                users = search_results.scalars().all()

                # Если результаты найдены, форматируем список пользователей
                if users:
                    user_list = []
                    for user in users:
                        subscription_status = "VIP" if user.subscription_status else " - "
                        whatsapp_link = f"[WhatsApp](https://wa.me/{user.phone_number})" if user.phone_number else "N/A"
                        language_flag = "🇷🇺" if user.language == "ru" else "🇰🇬" if user.language == "kg" else "N/A"

                        user_info = (
                            f"🔹 [{user.name}](tg://user?id={user.telegram_id}) | {user.telegram_id} | "
                            f"{user.rubies} 💎 | {subscription_status} | {language_flag} | {whatsapp_link}"
                        )
                        user_list.append(user_info)
                    return user_list
                else:
                    return []  # Если пользователей не найдено

    except Exception as e:
        print(f"Ошибка при поиске пользователей: {e}")
        return []


# Функция для сброса VIP-статусов в БД
async def reset_all_users_to_regular():
    try:
        async with async_session() as session:
            async with session.begin():
                await session.execute(
                    update(User)
                    .where(User.subscription_status == True)
                    .values(subscription_status=False)
                )
                await session.commit()
    except Exception as e:
        print(f"Ошибка при сбросе VIP-статусов: {e}")


# Функция для удаления администратора по Telegram ID
async def delete_admin_by_tg_id(telegram_id: str) -> bool:
    try:
        async with async_session() as session:  # async_session - ваша сессия SQLAlchemy
            async with session.begin():
                # Проверка наличия администратора
                result = await session.execute(
                    select(Admin).where(Admin.telegram_id == telegram_id)
                )
                admin = result.scalars().first()

                if not admin:
                    return False  # Администратор не найден

                # Удаление администратора
                await session.execute(
                    delete(Admin).where(Admin.telegram_id == telegram_id)
                )
                await session.commit()
                return True  # Администратор успешно удален

    except Exception as e:
        print(f"Ошибка при удалении администратора: {e}")
        return False