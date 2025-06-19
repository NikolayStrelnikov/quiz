from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import StateFilter
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from database.queries import (
    get_quiz_by_id,
    save_quiz_result,
    get_or_create_user
)
from keyboards.inline import (
    get_question_keyboard,
    get_quiz_result_keyboard
)
from services.quiz_processor import process_quiz
from states import QuizStates
from handlers.commands import cmd_run

router = Router()
logger = logging.getLogger(__name__)


async def show_question(
        message: Message,
        state: FSMContext,
        db: AsyncSession
) -> None:
    """Показывает текущий вопрос квиза"""
    try:
        data = await state.get_data()
        current_idx = data["current_question"]
        questions = data["questions"]

        if current_idx >= len(questions):
            await finish_quiz(message, state, db)
            return

        question = questions[current_idx]
        await message.answer(
            f"❓ Вопрос {current_idx + 1}/{len(questions)}:\n\n"
            f"{question['text']}",
            reply_markup=get_question_keyboard(question["options"])
        )

    except Exception as e:
        logger.error(f"Error showing question: {e}")
        await message.answer("⚠️ Произошла ошибка при загрузке вопроса")
        await state.clear()


async def finish_quiz(
        message: Message,
        state: FSMContext,
        db: AsyncSession
) -> None:
    """Завершает квиз и сохраняет результат"""
    try:
        data = await state.get_data()

        async with db.begin():
            user = await get_or_create_user(
                db,
                telegram_id=message.from_user.id,
                username=message.from_user.username,
                full_name=message.from_user.full_name
            )

            await save_quiz_result(
                db,
                user_id=user.id,
                quiz_id=data["quiz_id"],
                score=data["correct_answers"],
                total_questions=data["total_questions"]
            )

            percentage = (data["correct_answers"] / data["total_questions"]) * 100
            await message.answer(
                f"🏆 Квиз завершен!\n\n"
                f"Ваш результат: {data['correct_answers']}/{data['total_questions']}\n"
                f"Процент правильных ответов: {percentage:.1f}%",
                reply_markup=get_quiz_result_keyboard()
            )

            await state.clear()

    except Exception as e:
        logger.error(f"Error finishing quiz: {e}")
        await message.answer("⚠️ Ошибка при сохранении результатов")
        await state.clear()


@router.callback_query(F.data.startswith("quiz_"))
async def select_quiz_callback(
        callback: CallbackQuery,
        state: FSMContext,
        db: AsyncSession
) -> None:
    """Обработчик выбора квиза"""
    try:
        quiz_id = int(callback.data.split("_")[1])

        async with db.begin():
            quiz = await get_quiz_by_id(db, quiz_id)

            if not quiz:
                await callback.answer("⚠️ Квиз не найден!")
                return

            try:
                questions = process_quiz(quiz.content)
                if not questions or len(questions) < 1:
                    raise ValueError("Квиз не содержит вопросов")

                await state.update_data(
                    quiz_id=quiz.id,
                    questions=questions,
                    current_question=0,
                    correct_answers=0,
                    total_questions=len(questions)
                )

                await show_question(callback.message, state, db)
                await callback.answer()

            except ValueError as e:
                await callback.message.answer(f"❌ Ошибка: {str(e)}")
                await callback.answer()
                await state.clear()

    except Exception as e:
        logger.error(f"Error in select_quiz: {e}")
        await callback.answer("⚠️ Произошла ошибка")
        await state.clear()


@router.callback_query(F.data.startswith("answer_"), StateFilter(QuizStates.quiz_in_progress))
async def answer_callback(
        callback: CallbackQuery,
        state: FSMContext,
        db: AsyncSession
) -> None:
    """Обработчик ответа на вопрос"""
    try:
        selected_option = int(callback.data.split("_")[1])
        data = await state.get_data()
        current_idx = data["current_question"]
        questions = data["questions"]

        if current_idx >= len(questions):
            await callback.answer("Недопустимый вопрос!")
            return

        correct_answer = questions[current_idx]["correct_answer"]
        is_correct = selected_option == correct_answer

        await state.update_data(
            current_question=current_idx + 1,
            correct_answers=data["correct_answers"] + int(is_correct)
        )

        try:
            await callback.message.edit_text(
                f"{'✅ Правильно!' if is_correct else '❌ Неправильно!'}\n\n"
                f"Правильный ответ: {questions[current_idx]['options'][correct_answer]}",
                reply_markup=None
            )
        except TelegramBadRequest:
            await callback.answer()

        await show_question(callback.message, state, db)

    except Exception as e:
        logger.error(f"Error in answer callback: {e}")
        await callback.answer("⚠️ Ошибка обработки ответа")
        await state.clear()


@router.callback_query(F.data == "retry_quiz")
async def retry_quiz_callback(
        callback: CallbackQuery,
        state: FSMContext,
        db: AsyncSession
) -> None:
    """Обработчик повторного прохождения квиза"""
    try:
        await callback.message.delete()
        await cmd_run(callback.message, state, db)
    except Exception as e:
        logger.error(f"Error in retry quiz: {e}")
        await callback.answer("⚠️ Ошибка при запуске квиза")