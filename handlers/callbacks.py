from aiogram import Router, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from database.queries import (
    get_quiz_by_id,
    save_quiz_result,
    get_or_create_user
)
from handlers.commands import cmd_run
from keyboards.inline import (
    get_question_keyboard,
    get_quiz_result_keyboard
)
from services.quiz_processor import process_quiz
from states import QuizStates

router = Router()


async def show_question(
        message: Message,
        state: FSMContext,
        db: AsyncSession
):
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


async def finish_quiz(
        message: Message,
        state: FSMContext,
        db: AsyncSession
):
    data = await state.get_data()

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


@router.callback_query(F.data.startswith("quiz_"))
async def select_quiz_callback(
        callback: CallbackQuery,
        state: FSMContext,
        db: AsyncSession
):
    quiz_id = int(callback.data.split("_")[1])
    quiz = await get_quiz_by_id(db, quiz_id)

    if not quiz:
        await callback.answer("⚠️ Квиз не найден!")
        return

    try:
        questions = process_quiz(quiz.content)
        if not questions:
            raise ValueError("Не удалось обработать вопросы квиза")

        await state.update_data(
            quiz_id=quiz.id,
            questions=questions,
            current_question=0,
            correct_answers=0,
            total_questions=len(questions)
        )

        await show_question(callback.message, state, db)
        await callback.answer()

    except Exception as e:
        await callback.message.answer(f"❌ Ошибка загрузки квиза: {str(e)}")
        await callback.answer()
        await state.clear()


@router.callback_query(F.data.startswith("answer_"), StateFilter(QuizStates.quiz_in_progress))
async def answer_callback(
        callback: CallbackQuery,
        state: FSMContext,
        db: AsyncSession
):
    selected_option = int(callback.data.split("_")[1])
    data = await state.get_data()
    current_idx = data["current_question"]
    questions = data["questions"]

    correct_answer = questions[current_idx]["correct_answer"]
    is_correct = selected_option == correct_answer

    new_data = {
        "current_question": current_idx + 1,
        "correct_answers": data["correct_answers"] + int(is_correct)
    }
    await state.update_data(**new_data)

    try:
        await callback.message.edit_text(
            f"{'✅ Правильно!' if is_correct else '❌ Неправильно!'}\n\n"
            f"Правильный ответ: {questions[current_idx]['options'][correct_answer]}",
            reply_markup=None
        )
    except TelegramBadRequest:
        await callback.answer()

    await show_question(callback.message, state, db)


@router.callback_query(F.data == "retry_quiz")
async def retry_quiz_callback(
        callback: CallbackQuery,
        state: FSMContext,
        db: AsyncSession
):
    await callback.message.delete()
    # Правильный порядок аргументов: message, state, db
    await cmd_run(callback.message, state, db)
