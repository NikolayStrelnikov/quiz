from datetime import datetime
from typing import List, Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from .models import User, Quiz, QuizResult


async def get_or_create_user(
        db: AsyncSession,
        telegram_id: int,
        username: Optional[str] = None,
        full_name: Optional[str] = None
) -> User:
    """Получает или создает пользователя"""
    stmt = select(User).where(User.telegram_id == telegram_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if user:
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


async def create_quiz(
        db: AsyncSession,
        title: str,
        description: str,
        content: str,
        creator_id: int
) -> Quiz:
    """Создает новый квиз"""
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


async def get_active_quizzes(db: AsyncSession) -> List[Quiz]:
    """Возвращает активные квизы"""
    stmt = (
        select(Quiz)
        .where(Quiz.is_active == True)
        .options(selectinload(Quiz.creator))
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_quiz_by_id(db: AsyncSession, quiz_id: int) -> Optional[Quiz]:
    """Находит квиз по ID"""
    stmt = (
        select(Quiz)
        .where(Quiz.id == quiz_id)
        .options(selectinload(Quiz.creator))
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def save_quiz_result(
        db: AsyncSession,
        user_id: int,
        quiz_id: int,
        score: int,
        total_questions: int
) -> QuizResult:
    """Сохраняет результат квиза"""
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


async def update_quiz_activity(
        db: AsyncSession,
        quiz_id: int,
        is_active: bool
) -> bool:
    """Активирует/деактивирует квиз"""
    quiz = await db.get(Quiz, quiz_id)
    if not quiz:
        return False
    quiz.is_active = is_active
    await db.commit()
    return True


async def get_user_results(db: AsyncSession, user_id: int) -> List[QuizResult]:
    """Возвращает результаты пользователя"""
    stmt = (
        select(QuizResult)
        .join(Quiz)
        .where(QuizResult.user_id == user_id)
        .options(selectinload(QuizResult.quiz))
        .order_by(QuizResult.completed_at.desc())
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_quiz_stats(db: AsyncSession, quiz_id: int) -> dict:
    """Возвращает статистику квиза"""
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
