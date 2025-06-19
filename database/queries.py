import logging
from datetime import datetime
from typing import List, Optional

from sqlalchemy import select, func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from .models import User, Quiz, QuizResult

logger = logging.getLogger(__name__)


async def get_or_create_user(
        db: AsyncSession,
        telegram_id: int,
        username: Optional[str] = None,
        full_name: Optional[str] = None
) -> User:
    """Безопасное получение или создание пользователя"""
    try:
        async with db.begin():
            stmt = select(User).where(User.telegram_id == telegram_id)
            result = await db.execute(stmt)
            user = result.scalar_one_or_none()

            if user:
                # Обновляем данные, если они изменились
                if username and user.username != username:
                    user.username = username
                if full_name and user.full_name != full_name:
                    user.full_name = full_name
                await db.commit()
            else:
                user = User(
                    telegram_id=telegram_id,
                    username=username,
                    full_name=full_name
                )
                db.add(user)
                await db.commit()
                await db.refresh(user)

            return user

    except SQLAlchemyError as e:
        logger.error(f"Error in get_or_create_user: {e}")
        await db.rollback()
        raise ValueError("Ошибка при работе с пользователем")


async def create_quiz(
        db: AsyncSession,
        title: str,
        description: str,
        content: str,
        creator_id: int
) -> Quiz:
    """Создание квиза с транзакцией"""
    try:
        async with db.begin():
            quiz = Quiz(
                title=title,
                description=description,
                content=content,
                creator_id=creator_id
            )
            db.add(quiz)
            await db.commit()
            await db.refresh(quiz)
            return quiz

    except SQLAlchemyError as e:
        logger.error(f"Error creating quiz: {e}")
        await db.rollback()
        raise ValueError("Ошибка при создании квиза")


async def get_active_quizzes(db: AsyncSession) -> List[Quiz]:
    """Безопасное получение активных квизов"""
    try:
        async with db.begin():
            stmt = (
                select(Quiz)
                .where(Quiz.is_active == True)
                .options(selectinload(Quiz.creator))
            )
            result = await db.execute(stmt)
            return list(result.scalars().all())

    except SQLAlchemyError as e:
        logger.error(f"Error fetching active quizzes: {e}")
        await db.rollback()
        raise ValueError("Ошибка при получении квизов")


async def get_quiz_by_id(db: AsyncSession, quiz_id: int) -> Optional[Quiz]:
    """Получение квиза по ID с проверкой"""
    try:
        async with db.begin():
            stmt = (
                select(Quiz)
                .where(Quiz.id == quiz_id)
                .options(selectinload(Quiz.creator))
            )
            result = await db.execute(stmt)
            return result.scalar_one_or_none()

    except SQLAlchemyError as e:
        logger.error(f"Error fetching quiz {quiz_id}: {e}")
        await db.rollback()
        raise ValueError("Ошибка при поиске квиза")


async def save_quiz_result(
        db: AsyncSession,
        user_id: int,
        quiz_id: int,
        score: int,
        total_questions: int
) -> QuizResult:
    """Сохранение результата с транзакцией"""
    try:
        async with db.begin():
            result = QuizResult(
                user_id=user_id,
                quiz_id=quiz_id,
                score=score,
                total_questions=total_questions,
                completed_at=datetime.now()
            )
            db.add(result)
            await db.commit()
            await db.refresh(result)
            return result

    except SQLAlchemyError as e:
        logger.error(f"Error saving quiz result: {e}")
        await db.rollback()
        raise ValueError("Ошибка сохранения результата")


async def update_quiz_activity(
        db: AsyncSession,
        quiz_id: int,
        is_active: bool
) -> bool:
    """Обновление статуса квиза с гарантированным возвратом bool"""
    try:
        async with db.begin():
            # Самый надежный вариант - отдельный запрос на проверку
            quiz = await db.get(Quiz, quiz_id)
            if not quiz:
                return False

            quiz.is_active = is_active
            await db.commit()
            return True

    except SQLAlchemyError as e:
        logger.error(f"Error updating quiz {quiz_id}: {e}")
        await db.rollback()
        raise ValueError("Ошибка обновления квиза")


async def get_user_results(
        db: AsyncSession,
        user_id: int
) -> List[QuizResult]:
    """Получение результатов пользователя"""
    try:
        async with db.begin():
            stmt = (
                select(QuizResult)
                .join(Quiz)
                .where(QuizResult.user_id == user_id)
                .options(selectinload(QuizResult.quiz))
                .order_by(QuizResult.completed_at.desc())
            )
            result = await db.execute(stmt)
            return list(result.scalars().all())

    except SQLAlchemyError as e:
        logger.error(f"Error fetching results for user {user_id}: {e}")
        await db.rollback()
        raise ValueError("Ошибка получения результатов")


async def get_quiz_stats(db: AsyncSession, quiz_id: int) -> dict:
    """Получение статистики квиза"""
    try:
        async with db.begin():
            stmt = select(
                func.count(QuizResult.id).label("total_attempts"),
                func.avg(QuizResult.score).label("average_score")
            ).where(QuizResult.quiz_id == quiz_id)

            result = await db.execute(stmt)
            stats = result.first()

            return {
                "total_attempts": stats.total_attempts or 0,
                "average_score": float(stats.average_score or 0)
            }

    except SQLAlchemyError as e:
        logger.error(f"Error fetching stats for quiz {quiz_id}: {e}")
        await db.rollback()
        raise ValueError("Ошибка получения статистики")
