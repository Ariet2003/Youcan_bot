from typing import Optional, List
from sqlalchemy.orm import selectinload
from sqlalchemy import or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.models import async_session
from app.database.models import User, Admin, Question, Notification, Duel, UserAnswer
from app.users.user import userKeyboards as kb
from sqlalchemy.exc import SQLAlchemyError
from bot_instance import bot
from sqlalchemy import select, delete
from datetime import datetime
from sqlalchemy import update
import random
from sqlalchemy import or_
from sqlalchemy.orm import aliased
import pytz
import json


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
async def write_question(telegram_id: str, subject_id: int, content: str, option_a: str, option_b: str, option_v: str, option_g: str, correct_option: str, status: str = "pending") -> bool:
    async with async_session() as session:
        async with session.begin():
            # Находим user_id по telegram_id
            result = await session.execute(
                select(User.user_id).where(User.telegram_id == telegram_id)
            )
            user_id = result.scalar_one_or_none()

            # Если user_id не найден, возвращаем False
            if user_id is None:
                print(f"Пользователь с telegram_id {telegram_id} не найден.")
                return False

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


# Request to get and review the oldest pending question for a specific subject_id (by smallest question_id)
async def get_and_review_oldest_pending_question(subject_id: int) -> Optional[dict]:
    async with async_session() as session:
        # Начинаем транзакцию
        async with session.begin():
            # Запрос для получения самого маленького question_id со статусом 'pending' и указанным subject_id
            result = await session.execute(
                select(Question)
                .filter(Question.status == 'pending', Question.subject_id == subject_id)
                .order_by(Question.question_id.asc())  # Сортировка по question_id в возрастающем порядке
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

# Функция для сброса статуса пользователя по Telegram ID
async def reset_user_subscription_status(telegram_id: str) -> bool:
    try:
        async with async_session() as session:  # async_session - ваша сессия SQLAlchemy
            async with session.begin():
                # Проверка наличия пользователя
                result = await session.execute(
                    select(User).where(User.telegram_id == telegram_id)
                )
                user = result.scalars().first()

                if not user:
                    return False  # Пользователь не найден

                # Обновление статуса пользователя на False
                await session.execute(
                    update(User)
                    .where(User.telegram_id == telegram_id)
                    .values(subscription_status=False)
                )
                await session.commit()
                return True  # Статус успешно сброшен

    except Exception as e:
        print(f"Ошибка при сбросе статуса пользователя: {e}")
        return False


# Функция для изменения языка пользователя на "ru" по Telegram ID
async def set_user_language_to_ru(telegram_id: str) -> bool:
    try:
        async with async_session() as session:  # async_session - ваша сессия SQLAlchemy
            async with session.begin():
                # Проверка наличия пользователя
                result = await session.execute(
                    select(User).where(User.telegram_id == telegram_id)
                )
                user = result.scalars().first()

                if not user:
                    return False  # Пользователь не найден

                # Обновление языка пользователя на "ru"
                await session.execute(
                    update(User)
                    .where(User.telegram_id == telegram_id)
                    .values(language="ru")
                )
                await session.commit()
                return True  # Язык успешно изменен на "ru"

    except Exception as e:
        print(f"Ошибка при изменении языка пользователя: {e}")
        return False


# Функция для изменения языка пользователя на "kg" по Telegram ID
async def set_user_language_to_kg(telegram_id: str) -> bool:
    try:
        async with async_session() as session:  # async_session - ваша сессия SQLAlchemy
            async with session.begin():
                # Проверка наличия пользователя
                result = await session.execute(
                    select(User).where(User.telegram_id == telegram_id)
                )
                user = result.scalars().first()

                if not user:
                    return False  # Пользователь не найден

                # Обновление языка пользователя на "kg"
                await session.execute(
                    update(User)
                    .where(User.telegram_id == telegram_id)
                    .values(language="kg")
                )
                await session.commit()
                return True  # Язык успешно изменен на "kg"

    except Exception as e:
        print(f"Ошибка при изменении языка пользователя: {e}")
        return False


# Функция для обновления номера телефона пользователя
async def update_user_phone_number(telegram_id: str, new_phone_number: str) -> bool:
    try:
        async with async_session() as session:
            async with session.begin():
                # Проверяем, существует ли пользователь
                result = await session.execute(
                    select(User).where(User.telegram_id == telegram_id)
                )
                user = result.scalars().first()

                if not user:
                    return False  # Пользователь не найден

                # Обновляем номер телефона
                await session.execute(
                    update(User)
                    .where(User.telegram_id == telegram_id)
                    .values(phone_number=new_phone_number)
                )
                await session.commit()
                return True  # Номер телефона успешно обновлен

    except Exception as e:
        print(f"Ошибка при обновлении номера телефона: {e}")
        return False


# Функция для получения статуса пользователя по Telegram ID
async def get_user_status_ru(telegram_id: str) -> str:
    try:
        async with async_session() as session:
            async with session.begin():
                # Извлекаем только subscription_status пользователя
                result = await session.execute(
                    select(User.subscription_status).where(User.telegram_id == telegram_id)
                )
                user_status = result.scalar()  # Получаем значение статуса

                if user_status is None:
                    return "Пользователь не найден"  # Если статус не найден

                # Возвращаем статус пользователя
                return "VIP" if user_status else "Обычный"  # Преобразуем статус в текст

    except Exception as e:
        print(f"Ошибка при получении статуса пользователя: {e}")
        return "Ошибка"  # В случае ошибки возвращаем "Ошибка"


# Функция для получения статуса пользователя по Telegram ID
async def get_user_status_kg(telegram_id: str) -> str:
    try:
        async with async_session() as session:
            async with session.begin():
                # Извлекаем только subscription_status пользователя
                result = await session.execute(
                    select(User.subscription_status).where(User.telegram_id == telegram_id)
                )
                user_status = result.scalar()  # Получаем значение статуса

                if user_status is None:
                    return "Колдонуучу табылган жок"  # Если статус не найден

                # Возвращаем статус пользователя
                return "VIP" if user_status else "Жөнөкөй"  # Преобразуем статус в текст

    except Exception as e:
        print(f"Ошибка при получении статуса пользователя: {e}")
        return "Ката!"  # В случае ошибки возвращаем "Ошибка"



# Функция для обновления ФИО пользователя
async def update_user_name(telegram_id: str, new_name: str) -> bool:
    try:
        async with async_session() as session:
            async with session.begin():
                # Проверяем, существует ли пользователь
                result = await session.execute(
                    select(User).where(User.telegram_id == telegram_id)
                )
                user = result.scalars().first()

                if not user:
                    return False  # Пользователь не найден

                # Обновляем ФИО
                await session.execute(
                    update(User)
                    .where(User.telegram_id == telegram_id)
                    .values(name=new_name)
                )
                await session.commit()
                return True  # ФИО успешно обновлено

    except Exception as e:
        print(f"Ошибка при обновлении ФИО пользователя: {e}")
        return False


# Функция для получения данных пользователя по Telegram ID
async def get_user_profile_data(telegram_id: str):
    try:
        async with async_session() as session:
            async with session.begin():
                # Извлекаем только нужные данные пользователя
                result = await session.execute(
                    select(
                        User.name,
                        User.phone_number,
                        User.rubies,
                        User.subscription_status,
                        User.created_at,
                        User.updated_at
                    ).where(User.telegram_id == telegram_id)
                )
                user_data = result.fetchone()  # Получаем данные в виде кортежа

                if not user_data:
                    return None  # Если данные не найдены, возвращаем None

                # Возвращаем данные пользователя в виде словаря
                return {
                    "name": user_data[0],
                    "phone_number": user_data[1],
                    "rubies": user_data[2],
                    "subscription_status": user_data[3],
                    "created_at": user_data[4],
                    "updated_at": user_data[5]
                }

    except Exception as e:
        print(f"Ошибка при получении данных пользователя: {e}")
        return None  # В случае ошибки возвращаем None


# Функция для получения рейтинга пользователей с учетом пагинации
async def get_users_ranking(page: int, page_size: int = 50):
    try:
        async with async_session() as session:
            async with session.begin():
                offset = (page - 1) * page_size  # Определяем отступ для текущей страницы

                # Извлекаем пользователей, сортируя по рубинам в порядке убывания
                result = await session.execute(
                    select(User.name, User.rubies)
                    .order_by(User.rubies.desc())
                    .offset(offset)
                    .limit(page_size)
                )

                # Получаем список пользователей с количеством рубинов
                users = result.all()
                return users  # Список пользователей для текущей страницы

    except Exception as e:
        print(f"Ошибка при получении рейтинга пользователей: {e}")
        return []

# Запрос для получения ранга пользователя по telegram_id
async def get_user_rank(telegram_id: str) -> Optional[int]:
    try:
        async with async_session() as session:
            async with session.begin():
                # Считаем количество пользователей с большим количеством рубинов
                rank_result = await session.execute(
                    select(func.count())
                    .where(User.rubies > (select(User.rubies).where(User.telegram_id == telegram_id).scalar_subquery()))
                )
                rank = rank_result.scalar() + 1  # Получаем текущий ранг пользователя
                return rank
    except Exception as e:
        print(f"Ошибка при получении ранга пользователя: {e}")
        return None


# _______________________________________________________________________________

# Запрос для получения индекса последнего сданного вопроса по telegram_id и subject_id
async def get_last_answered_question_index(telegram_id: str, subject_id: int) -> Optional[int]:
    try:
        async with async_session() as session:
            async with session.begin():
                # Подзапрос для получения user_id по telegram_id
                user_id_subquery = select(User.user_id).where(User.telegram_id == telegram_id).scalar_subquery()

                # Основной запрос для получения максимального question_id по subject_id для пользователя
                result = await session.execute(
                    select(func.max(UserAnswer.question_id))
                    .join(Question, Question.question_id == UserAnswer.question_id)
                    .where(
                        UserAnswer.user_id == user_id_subquery,
                        Question.subject_id == subject_id
                    )
                )
                last_answered_question_id = result.scalar()  # Получаем последний question_id
                return last_answered_question_id if last_answered_question_id is not None else 0
    except Exception as e:
        print(f"Ошибка при получении индекса последнего сданного вопроса: {e}")
        return None


async def get_next_question(last_answered_question_id: int, subject_id: int):
    try:
        async with async_session() as session:
            async with session.begin():
                # Получаем следующий вопрос по subject_id, начиная с вопроса после последнего сданного
                result = await session.execute(
                    select(Question)
                    .where(
                        Question.subject_id == subject_id,
                        Question.question_id > last_answered_question_id,
                        Question.status == "approved"  # Условие на статус
                    )
                    .order_by(Question.question_id)
                    .limit(1)
                )
                question = result.scalar_one_or_none()  # Получаем первый подходящий вопрос
                if question:
                    return {
                        'question_id': question.question_id,
                        'content': question.content,
                        'option_a': question.option_a,
                        'option_b': question.option_b,
                        'option_v': question.option_v,
                        'option_g': question.option_g,
                        'correct_option': question.correct_option
                    }
                return None
    except Exception as e:
        print(f"Ошибка при получении следующего вопроса: {e}")
        return None


async def check_answer(question_id: int, selected_option: str) -> bool:
    try:
        async with async_session() as session:
            async with session.begin():
                # Выполняем запрос, чтобы получить правильный ответ для заданного question_id
                result = await session.execute(
                    select(Question.correct_option)
                    .where(Question.question_id == question_id)
                )

                correct_option = result.scalar()  # Получаем правильный ответ

                if correct_option is None:
                    # Если вопрос не найден
                    return False

                # Проверяем, соответствует ли выбранный вариант правильному
                return selected_option == correct_option
    except Exception as e:
        print(f"Ошибка при проверке ответа: {e}")
        return False


# Запрос для получения вопроса, вариантов и правильного ответа по question_id
async def get_question_and_options(question_id: int) -> Optional[dict]:
    try:
        async with async_session() as session:
            async with session.begin():
                # Основной запрос для получения вопроса и вариантов
                result = await session.execute(
                    select(Question.content, Question.option_a, Question.option_b,
                           Question.option_v, Question.option_g, Question.correct_option)
                    .where(Question.question_id == question_id)
                )

                question_data = result.fetchone()

                if question_data:
                    question = {
                        "question": question_data[0],
                        "option_a": question_data[1],
                        "option_b": question_data[2],
                        "option_v": question_data[3],
                        "option_g": question_data[4],
                        "correct_option": question_data[5]
                    }
                    return question
                else:
                    return None
    except Exception as e:
        print(f"Ошибка при получении вопроса и вариантов: {e}")
        return None


# Запрос для обновления количества рубинов для пользователя по telegram_id
async def update_rubies(telegram_id: str, rubies_to_add: int) -> bool:
    try:
        async with async_session() as session:
            async with session.begin():
                # Запрос для получения пользователя по telegram_id
                result = await session.execute(
                    select(User).where(User.telegram_id == telegram_id)
                )

                user = result.scalar()

                if user:
                    # Обновляем количество рубинов
                    user.rubies += rubies_to_add

                    # Сохраняем изменения
                    await session.commit()
                    return True  # Успешно обновлено
                else:
                    return False  # Пользователь не найден
    except Exception as e:
        print(f"Ошибка при обновлении рубинов: {e}")
        return False  # Ошибка

# Запрос для обновления количества рубинов для пользователя по telegram_id (минус)
async def update_rubies_minus(telegram_id: str, rubies_to_add: int) -> bool:
    try:
        async with async_session() as session:
            async with session.begin():
                # Запрос для получения пользователя по telegram_id
                result = await session.execute(
                    select(User).where(User.telegram_id == telegram_id)
                )

                user = result.scalar()

                if user:
                    # Обновляем количество рубинов
                    user.rubies -= rubies_to_add

                    # Сохраняем изменения
                    await session.commit()
                    return True  # Успешно обновлено
                else:
                    return False  # Пользователь не найден
    except Exception as e:
        print(f"Ошибка при обновлении рубинов: {e}")
        return False  # Ошибка

# Запрос для записи ответа пользователя в таблицу user_answers
async def record_user_answer(user_id: int, question_id: int, chosen_option: str, is_correct: bool, rubies_earned: int) -> bool:
    try:
        async with async_session() as session:
            async with session.begin():
                # Создаем новый объект UserAnswer
                user_answer = UserAnswer(
                    user_id=user_id,
                    question_id=question_id,
                    chosen_option=chosen_option,
                    is_correct=is_correct,
                    rubies_earned=rubies_earned,
                    answered_at=get_current_time()
                )

                # Добавляем новый ответ в сессию
                session.add(user_answer)

                # Сохраняем изменения в базе данных
                await session.commit()
                return True  # Успешно добавлено
    except Exception as e:
        print(f"Ошибка при записи ответа пользователя: {e}")
        return False  # Ошибка


# Запрос для получения user_id по telegram_id
async def get_user_id_by_telegram_id(telegram_id: str) -> Optional[int]:
    try:
        async with async_session() as session:
            async with session.begin():
                # Запрос для получения user_id по telegram_id
                result = await session.execute(
                    select(User.user_id)
                    .where(User.telegram_id == telegram_id)
                )
                # Получаем результат
                user_id = result.scalar()  # Получаем скалярное значение (первый элемент результата)

                # Возвращаем user_id, если он найден, иначе None
                return user_id if user_id else None
    except Exception as e:
        print(f"Ошибка при получении user_id по telegram_id: {e}")
        return None


# Запрос для удаления всех пройденных вопросов пользователя по предмету из таблицы user_answers
async def delete_completed_questions(subject_id: int, telegram_id: str) -> bool:
    try:
        async with async_session() as session:
            async with session.begin():
                # Получаем user_id по telegram_id
                user_result = await session.execute(
                    select(User.user_id).where(User.telegram_id == telegram_id)
                )
                user = user_result.scalar_one_or_none()

                if user is None:
                    print(f"Пользователь с telegram_id {telegram_id} не найден.")
                    return False

                # Удаляем ответы пользователя по заданному предмету
                await session.execute(
                    delete(UserAnswer)
                    .where(
                        UserAnswer.user_id == user,
                        UserAnswer.question_id.in_(
                            select(Question.question_id).where(Question.subject_id == subject_id)
                        )
                    )
                )

                # Фиксируем изменения в базе данных
                await session.commit()
                return True  # Успешно удалено
    except Exception as e:
        print(f"Ошибка при удалении пройденных вопросов: {e}")
        return False  # Ошибка

# Функция для проверки наличия объяснения в вопросе
async def check_explanation_exists(question_id: int) -> bool:
    try:
        async with async_session() as session:
            async with session.begin():
                # Выполняем запрос для проверки поля explanation
                result = await session.execute(
                    select(Question.explanation)
                    .where(Question.question_id == question_id)
                )
                explanation = result.scalar_one_or_none()

                # Возвращаем False, если explanation пустое, иначе True
                return bool(explanation)
    except Exception as e:
        print(f"Ошибка при проверке наличия объяснения: {e}")
        return False

# Функция для получения объяснения по question_id
async def get_explanation_by_question_id(question_id: int) -> Optional[str]:
    try:
        async with async_session() as session:
            async with session.begin():
                # Выполняем запрос для получения поля explanation
                result = await session.execute(
                    select(Question.explanation)
                    .where(Question.question_id == question_id)
                )
                explanation = result.scalar_one_or_none()

                # Возвращаем значение explanation, если оно есть
                return explanation
    except Exception as e:
        print(f"Ошибка при получении объяснения: {e}")
        return None


# Функция для добавления значения в поле explanation по question_id
async def update_explanation_by_question_id(question_id: int, explanation_text: str):
    try:
        async with async_session() as session:
            async with session.begin():
                # Обновляем поле explanation для указанного question_id
                await session.execute(
                    update(Question)
                    .where(Question.question_id == question_id)
                    .values(explanation=explanation_text)
                )
                await session.commit()  # Сохраняем изменения
    except Exception as e:
        print(f"Ошибка при обновлении explanation: {e}")

# Функция для проверки, правильно ли пользователь ответил на вопрос по question_id и user_telegram_id
async def check_user_answer_correct(question_id: int, user_telegram_id: int) -> bool:
    try:
        async with async_session() as session:
            async with session.begin():
                # Находим user_id по user_telegram_id
                result = await session.execute(
                    select(User.user_id).where(User.telegram_id == user_telegram_id)
                )
                user_id = result.scalar_one_or_none()

                if user_id is None:
                    print("Пользователь не найден.")
                    return False

                # Проверяем, правильно ли ответил пользователь на указанный вопрос
                result = await session.execute(
                    select(UserAnswer.is_correct)
                    .where(UserAnswer.question_id == question_id, UserAnswer.user_id == user_id)
                )
                is_correct = result.scalar_one_or_none()

                # Возвращаем True, если ответ правильный, иначе False
                return bool(is_correct)
    except Exception as e:
        print(f"Ошибка при проверке правильности ответа пользователя: {e}")
        return False


# Функция для проверки наличия незавершенных дуэлей, где opponent_id пустой, creator_id не равен user_id, и язык совпадает
async def has_unfinished_duels(telegram_id: str) -> bool:
    try:
        async with async_session() as session:
            async with session.begin():
                # Находим user_id и язык по telegram_id
                result = await session.execute(
                    select(User.user_id, User.language).where(User.telegram_id == telegram_id)
                )
                user_data = result.one_or_none()

                if user_data is None:
                    print(f"Пользователь с telegram_id {telegram_id} не найден.")
                    return False

                user_id, user_language = user_data

                # Запрос на поиск хотя бы одной незавершенной дуэли, где opponent_id пустой, creator_id не равен user_id, и язык совпадает
                result = await session.execute(
                    select(Duel)
                    .join(User, Duel.creator_id == User.user_id)
                    .where(Duel.opponent_id == None, Duel.creator_id != user_id, User.language == user_language)
                    .limit(1)  # Ограничиваем результат одной строкой
                )

                # Проверяем, есть ли хотя бы одна подходящая незавершенная дуэль
                unfinished_duel_exists = result.fetchone() is not None

                return unfinished_duel_exists  # True, если есть незавершенные дуэли, иначе False
    except Exception as e:
        print(f"Ошибка при проверке наличия незавершенных дуэлей: {e}")
        return False






# Функция для получения 5 случайных question_id по двум subject_id
async def get_random_questions_by_subjects(subject_id1: int, subject_id2: int) -> list[int]:
    try:
        async with async_session() as session:
            async with session.begin():
                # Запрос для получения всех вопросов по двум subject_id
                result = await session.execute(
                    select(Question.question_id)
                    .where(or_(Question.subject_id == subject_id1, Question.subject_id == subject_id2))
                )

                # Извлекаем все question_id из результатов
                question_ids = [row[0] for row in result.fetchall()]

                # Возвращаем 5 случайных question_id, если доступно достаточно вопросов
                return random.sample(question_ids, min(5, len(question_ids)))
    except Exception as e:
        print(f"Ошибка при получении случайных вопросов: {e}")
        return []


# Функция для проверки, есть ли у пользователя хотя бы 10 рубинов
async def has_minimum_rubies(telegram_id: str) -> bool:
    try:
        async with async_session() as session:
            async with session.begin():
                # Находим пользователя по telegram_id
                result = await session.execute(
                    select(User.rubies).where(User.telegram_id == telegram_id)
                )
                rubies = result.scalar_one_or_none()

                # Проверяем, есть ли у пользователя хотя бы 10 рубинов
                if rubies is not None and rubies >= 10:
                    return True
                else:
                    print("Недостаточно рубинов или пользователь не найден.")
                    return False
    except Exception as e:
        print(f"Ошибка при проверке количества рубинов: {e}")
        return False


# Функция для записи данных о дуэли, используя telegram_id для получения creator_id
async def record_duel(telegram_id: str, questions: List[int], creator_score: int, creator_time: float) -> bool:
    try:
        async with async_session() as session:
            async with session.begin():
                # Находим creator_id по telegram_id
                result = await session.execute(
                    select(User.user_id).where(User.telegram_id == telegram_id)
                )
                creator_id = result.scalar_one_or_none()

                if creator_id is None:
                    print(f"Пользователь с telegram_id {telegram_id} не найден.")
                    return False

                # Сериализуем список вопросов в строку JSON
                questions_json = json.dumps(questions)

                # Создаём новый объект дуэли
                duel = Duel(
                    creator_id=creator_id,
                    questions=questions_json,  # сохраняем сериализованный список
                    creator_score=creator_score,
                    creator_time=creator_time,
                    created_at=get_current_time()
                )

                # Добавляем объект в сессию
                session.add(duel)

                # Сохраняем изменения в базе данных
                await session.commit()

                return True
    except Exception as e:
        print(f"Ошибка при записи дуэли: {e}")
        return False


# Функция для обновления opponent_id в самой старой дуэли с учетом языка
async def update_opponent_in_oldest_duel(telegram_id: str) -> Optional[int]:
    try:
        async with async_session() as session:
            async with session.begin():
                # Находим user_id и язык по telegram_id
                result = await session.execute(
                    select(User.user_id, User.language).where(User.telegram_id == telegram_id)
                )
                user_data = result.one_or_none()

                if user_data is None:
                    print(f"Пользователь с telegram_id {telegram_id} не найден.")
                    return None

                user_id, user_language = user_data

                # Находим самую старую дуэль, у которой opponent_id пустой,
                # creator_id не равен user_id, и язык создателя дуэли совпадает
                result = await session.execute(
                    select(Duel.duel_id, Duel.creator_id)
                    .join(User, Duel.creator_id == User.user_id)  # Присоединяем таблицу User для проверки языка
                    .where(Duel.opponent_id == None)
                    .where(Duel.creator_id != user_id)
                    .where(User.language == user_language)  # Условие на совпадение языков
                    .order_by(Duel.created_at.asc())
                    .limit(1)
                )
                duel = result.fetchone()  # Получаем результат как одну строку

                if duel is None:
                    print("Дуэли с пустым opponent_id и подходящим creator_id не найдены.")
                    return None

                duel_id, creator_id = duel  # Результат — кортеж с duel_id и creator_id

                # Обновляем opponent_id в найденной дуэли
                await session.execute(
                    update(Duel)
                    .where(Duel.duel_id == duel_id)
                    .values(opponent_id=user_id)
                )

                # Сохраняем изменения в базе данных
                await session.commit()

                # Возвращаем duel_id обновленной дуэли
                return duel_id
    except Exception as e:
        print(f"Ошибка при обновлении opponent_id: {e}")
        return None



# Функция для получения списка вопросов по duel_id
async def get_duel_questions(duel_id: int) -> List[int]:
    try:
        async with async_session() as session:
            async with session.begin():
                # Выполняем запрос для получения списка вопросов
                result = await session.execute(
                    select(Duel.questions).where(Duel.duel_id == duel_id)
                )
                questions = result.scalar_one_or_none()  # Извлекаем вопросы

                return questions  # Возвращаем список вопросов или None, если дуэль не найдена
    except Exception as e:
        print(f"Ошибка при получении списка вопросов для duel_id {duel_id}: {e}")
        return None

# Функция для получения creator_score, creator_time и telegram_id по duel_id
async def get_creator_score_time_and_telegram(duel_id: int) -> Optional[tuple[int, float, str]]:
    try:
        async with async_session() as session:
            async with session.begin():
                # Выполняем запрос для получения creator_score, creator_time и creator_id
                result = await session.execute(
                    select(Duel.creator_score, Duel.creator_time, Duel.creator_id).where(Duel.duel_id == duel_id)
                )
                duel_data = result.one_or_none()

                if duel_data is None:
                    print(f"Данные для duel_id {duel_id} не найдены.")
                    return None

                creator_score, creator_time, creator_id = duel_data

                # Выполняем запрос для получения telegram_id по creator_id
                result = await session.execute(
                    select(User.telegram_id).where(User.user_id == creator_id)
                )
                telegram_id = result.scalar_one_or_none()

                if telegram_id is None:
                    print(f"Telegram ID для creator_id {creator_id} не найден.")
                    return None

                # Возвращаем кортеж (creator_score, creator_time, telegram_id)
                return creator_score, creator_time, telegram_id
    except Exception as e:
        print(f"Ошибка при получении данных для duel_id {duel_id}: {e}")
        return None

# Функция для обновления opponent_score, opponent_time и winner_id по duel_id, где winner определяется по telegram_id
async def update_duel_with_opponent_results(duel_id: int, opponent_score: int, opponent_time: float, winner_telegram_id: str) -> bool:
    try:
        async with async_session() as session:
            async with session.begin():
                # Находим user_id по winner_telegram_id
                result = await session.execute(
                    select(User.user_id).where(User.telegram_id == winner_telegram_id)
                )
                winner_id = result.scalar_one_or_none()

                if winner_id is None:
                    print(f"Пользователь с telegram_id {winner_telegram_id} не найден.")
                    return False

                # Обновляем поля opponent_score, opponent_time и winner_id в записи дуэли
                await session.execute(
                    update(Duel)
                    .where(Duel.duel_id == duel_id)
                    .values(
                        opponent_score=opponent_score,
                        opponent_time=opponent_time,
                        winner_id=winner_id,
                        completed_at=get_current_time()
                    )
                )
                # Сохраняем изменения
                await session.commit()
                return True
    except Exception as e:
        print(f"Ошибка при обновлении данных дуэли: {e}")
        return False

# Функция для получения количества дуэлей, где пользователь - creator, а opponent_id пустой
async def count_duels_with_opponent_pending(telegram_id: str) -> Optional[int]:
    try:
        async with async_session() as session:
            async with session.begin():
                # Находим user_id по telegram_id
                result = await session.execute(
                    select(User.user_id).where(User.telegram_id == telegram_id)
                )
                user_id = result.scalar_one_or_none()

                if user_id is None:
                    print(f"Пользователь с telegram_id {telegram_id} не найден.")
                    return None

                # Запрос на подсчет дуэлей, где creator_id равен user_id и opponent_id пустой
                result = await session.execute(
                    select(func.count()).select_from(Duel)
                    .where(Duel.creator_id == user_id, Duel.opponent_id == None)
                )
                duel_count = result.scalar_one()  # Получаем количество дуэлей

                return duel_count
    except Exception as e:
        print(f"Ошибка при получении количества дуэлей: {e}")
        return None


# Функция для получения статистики дуэлей и списка последних 20 дуэлей
async def get_duel_results(telegram_id: str):
    try:
        async with async_session() as session:
            async with session.begin():
                # Находим user_id по telegram_id
                result = await session.execute(
                    select(User.user_id).where(User.telegram_id == telegram_id)
                )
                user_id = result.scalar_one_or_none()
                if user_id is None:
                    print(f"Пользователь с telegram_id {telegram_id} не найден.")
                    return None

                # Запрос на подсчет выигранных, проигранных и ожидающих дуэлей
                win_count = await session.execute(
                    select(func.count()).select_from(Duel)
                    .where(Duel.winner_id == user_id)
                )
                win_count = win_count.scalar_one()

                lose_count = await session.execute(
                    select(func.count()).select_from(Duel)
                    .where(Duel.opponent_id == user_id, Duel.winner_id != user_id)
                )
                lose_count = lose_count.scalar_one()

                pending_count = await session.execute(
                    select(func.count()).select_from(Duel)
                    .where(Duel.creator_id == user_id, Duel.opponent_id == None)
                )
                pending_count = pending_count.scalar_one()

                # Создаем псевдонимы для таблицы User
                creator_user = aliased(User)
                opponent_user = aliased(User)

                # Запрос для получения последних 20 дуэлей
                recent_duels = await session.execute(
                    select(
                        Duel.creator_score, Duel.creator_time, Duel.opponent_score, Duel.opponent_time,
                        Duel.completed_at, Duel.created_at,
                        creator_user.name.label("creator_name"),
                        opponent_user.name.label("opponent_name")
                    )
                    .join(creator_user, Duel.creator_id == creator_user.user_id)
                    .outerjoin(opponent_user, Duel.opponent_id == opponent_user.user_id)
                    .where((Duel.creator_id == user_id) | (Duel.opponent_id == user_id))
                    .order_by(Duel.created_at.desc())
                    .limit(10)
                )

                duel_list = []
                for duel in recent_duels:
                    duel_info = {
                        "creator_name": duel.creator_name if duel.creator_name else "Белгисиз",
                        "creator_score": duel.creator_score,
                        "creator_time": f"{duel.creator_time} сек.",
                        "opponent_name": duel.opponent_name if duel.opponent_name else " - ",
                        "opponent_score": duel.opponent_score if duel.opponent_score else " - ",
                        "opponent_time": f"{duel.opponent_time} сек." if duel.opponent_time else " - ",
                        "created_at": duel.created_at,  # Время создания дуэли
                        "completed_at": duel.completed_at if duel.completed_at else " - "# Время завершения дуэли
                    }
                    duel_list.append(duel_info)

                return {
                    "win_count": win_count,
                    "lose_count": lose_count,
                    "pending_count": pending_count,
                    "recent_duels": duel_list
                }

    except Exception as e:
        print(f"Ошибка при получении результатов дуэлей: {e}")
        return None


# Count the number of answered questions for specific subjects by a specific user
async def count_user_answered_questions(telegram_id: str, subject_id1: int, subject_id2: int) -> int:
    async with async_session() as session:
        async with session.begin():
            # Выполняем запрос для подсчета количества вопросов, отвеченных пользователем, по двум subject_id
            result = await session.execute(
                select(func.count(UserAnswer.answer_id))
                .join(Question, Question.question_id == UserAnswer.question_id)
                .join(User, User.user_id == UserAnswer.user_id)
                .filter(
                    User.telegram_id == telegram_id,
                    Question.subject_id.in_([subject_id1, subject_id2])
                )
            )
            # Получаем результат
            answered_count = result.scalar()

            return answered_count or 0

# Check if a user has VIP status
async def is_vip_user(telegram_id: str) -> bool:
    async with async_session() as session:
        async with session.begin():
            # Запрос для получения статуса подписки пользователя
            result = await session.execute(
                select(User.subscription_status)
                .where(User.telegram_id == telegram_id)
            )
            # Получаем статус подписки
            subscription_status = result.scalar()

            # Возвращаем True, если пользователь VIP, иначе False
            return subscription_status is True

# Get the number of rubies for a user
async def get_user_rubies(telegram_id: str) -> int:
    async with async_session() as session:
        async with session.begin():
            # Запрос для получения количества рубинов пользователя
            result = await session.execute(
                select(User.rubies)
                .where(User.telegram_id == telegram_id)
            )
            rubies = result.scalar()
            return rubies or 0  # Если рубины отсутствуют, вернуть 0
