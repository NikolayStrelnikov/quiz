from datetime import datetime
from typing import Optional, List

from sqlalchemy import ForeignKey, String, Boolean, Text, DateTime, Integer
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(AsyncAttrs, DeclarativeBase):
    """Базовый класс моделей с поддержкой асинхронных атрибутов"""
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int] = mapped_column(unique=True, index=True)
    username: Mapped[Optional[str]] = mapped_column(String(64))
    full_name: Mapped[Optional[str]] = mapped_column(String(128))
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    quiz_results: Mapped[List["QuizResult"]] = relationship(back_populates="user")


class Quiz(Base):
    __tablename__ = "quizzes"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100), index=True)
    description: Mapped[str] = mapped_column(Text)
    content: Mapped[str] = mapped_column(Text)  # JSON или текстовое представление
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    creator_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    results: Mapped[List["QuizResult"]] = relationship(back_populates="quiz")
    creator: Mapped["User"] = relationship(back_populates="created_quizzes")


class QuizResult(Base):
    __tablename__ = "quiz_results"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    quiz_id: Mapped[int] = mapped_column(ForeignKey("quizzes.id"))
    score: Mapped[int] = mapped_column(Integer)
    total_questions: Mapped[int] = mapped_column(Integer)
    completed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    user: Mapped["User"] = relationship(back_populates="quiz_results")
    quiz: Mapped["Quiz"] = relationship(back_populates="results")
