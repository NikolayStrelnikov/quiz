from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship
from . import Base

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(Integer, unique=True, index=True)
    username = Column(String, nullable=True)
    full_name = Column(String, nullable=True)

    quiz_results = relationship("QuizResult", back_populates="user")


class Quiz(Base):
    __tablename__ = 'quizzes'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(Text)
    content = Column(Text)  # JSON или текстовое представление
    is_active = Column(Boolean, default=True)
    creator_id = Column(Integer, ForeignKey('users.id'))
    created_at = Column(DateTime, index=True)
    updated_at = Column(DateTime, index=True)

    results = relationship("QuizResult", back_populates="quiz")


class QuizResult(Base):
    __tablename__ = 'quiz_results'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    quiz_id = Column(Integer, ForeignKey('quizzes.id'))
    score = Column(Integer)
    total_questions = Column(Integer)
    completed_at = Column(String)  # Можно использовать DateTime при наличии timezone

    user = relationship("User", back_populates="quiz_results")
    quiz = relationship("Quiz", back_populates="results")