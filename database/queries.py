from datetime import datetime

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from .models import User, Quiz, QuizResult


def get_or_create_user(db: Session, telegram_id: int, username: str = None, full_name: str = None) -> User:
    """Получает или создает пользователя"""
    stmt = select(User).where(User.telegram_id == telegram_id)
    user = db.scalars(stmt).first()

    if not user:
        user = User(
            telegram_id=telegram_id,
            username=username,
            full_name=full_name
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    return user


def create_quiz(db: Session, title: str, description: str, content: str, creator_id: int) -> Quiz:
    """Создает новый квиз"""
    quiz = Quiz(
        title=title,
        description=description,
        content=content,
        creator_id=creator_id,
        created_at=datetime.now()
    )
    db.add(quiz)
    db.commit()
    db.refresh(quiz)
    return quiz


def get_active_quizzes(db: Session) -> list[Quiz]:
    """Возвращает список активных квизов"""
    stmt = select(Quiz).where(Quiz.is_active == True)
    return db.scalars(stmt).all()


def get_quiz_by_id(db: Session, quiz_id: int) -> Quiz | None:
    """Находит квиз по ID"""
    stmt = select(Quiz).where(Quiz.id == quiz_id)
    return db.scalars(stmt).first()


def save_quiz_result(
        db: Session,
        user_id: int,
        quiz_id: int,
        score: int,
        total_questions: int
) -> QuizResult:
    """Сохраняет результат прохождения квиза"""
    result = QuizResult(
        user_id=user_id,
        quiz_id=quiz_id,
        score=score,
        total_questions=total_questions,
        completed_at=datetime.now()
    )
    db.add(result)
    db.commit()
    db.refresh(result)
    return result


def update_quiz_activity(db: Session, quiz_id: int, is_active: bool) -> bool:
    """Активирует/деактивирует квиз"""
    stmt = (
        update(Quiz)
        .where(Quiz.id == quiz_id)
        .values(is_active=is_active)
    )
    result = db.execute(stmt)
    db.commit()
    return result.rowcount > 0


def get_user_results(db: Session, user_id: int) -> list[QuizResult]:
    """Возвращает результаты пользователя"""
    stmt = (
        select(QuizResult)
        .join(Quiz)
        .where(QuizResult.user_id == user_id)
        .order_by(QuizResult.completed_at.desc())
    )
    return db.scalars(stmt).all()