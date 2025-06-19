from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from database.queries import (
    get_or_create_user,
    get_active_quizzes,
    create_quiz
)
from keyboards.inline import (
    get_quizzes_keyboard,
    get_main_menu_keyboard
)
from services.quiz_parser import parse_quiz_text
from states import QuizStates

router = Router()


@router.message(Command("start"))
async def cmd_start(
        message: types.Message,
        db: AsyncSession,
        state: FSMContext
):
    await state.clear()

    # Создаем/получаем пользователя и используем его данные
    user = await get_or_create_user(
        db,
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        full_name=message.from_user.full_name
    )

    greeting_name = user.full_name or user.username or "пользователь"

    await message.answer(
        f"Добро пожаловать в QuizBot, {greeting_name}!\n\n"
        "Вы можете:\n"
        "- Создать новый квиз: /create\n"
        "- Пройти квизы: /run\n"
        "- Посмотреть пример: /template",
        reply_markup=get_main_menu_keyboard()
    )


@router.message(Command("create"))
async def cmd_create(
        message: types.Message,
        state: FSMContext
):
    await state.clear()
    await message.answer(
        "📝 Отправьте текст квиза в следующем формате:\n\n"
        "Название квиза: Название\n"
        "Описание: Описание квиза\n\n"
        "Вопрос 1: Текст вопроса\n"
        "1. Вариант 1\n"
        "2. Вариант 2\n"
        "3. Вариант 3\n"
        "4. Вариант 4\n"
        "Правильный ответ: 1\n\n"
        "Пример: /template",
        parse_mode="Markdown"
    )
    await state.set_state(QuizStates.waiting_for_quiz)


@router.message(Command("template"))
async def cmd_template(message: types.Message):
    await message.answer(
        "```\n"
        "Название квиза: Основы Python\n"
        "Описание: Тест по базовому синтаксису Python\n\n"
        "Вопрос 1: Как объявить список?\n"
        "1. list = {}\n"
        "2. list = []\n"
        "3. list = ()\n"
        "4. list = <>\n"
        "Правильный ответ: 2\n\n"
        "Вопрос 2: Какой оператор для возведения в степень?\n"
        "1. ^\n"
        "2. **\n"
        "3. *\n"
        "4. !\n"
        "Правильный ответ: 2\n"
        "```",
        parse_mode="Markdown"
    )


@router.message(Command("run"))
async def cmd_run(
        message: types.Message,
        state: FSMContext,
        db: AsyncSession
):
    await state.clear()

    quizzes = await get_active_quizzes(db)

    if not quizzes:
        await message.answer("❌ Нет доступных квизов для прохождения.")
        return

    await message.answer(
        "📋 Доступные квизы:",
        reply_markup=get_quizzes_keyboard(quizzes)
    )


@router.message(QuizStates.waiting_for_quiz)
async def process_quiz_text(
        message: types.Message,
        db: AsyncSession,
        state: FSMContext
):
    try:
        quiz_data = parse_quiz_text(message.text)

        await create_quiz(
            db,
            title=quiz_data['title'],
            description=quiz_data['description'],
            content=message.text,
            creator_id=message.from_user.id
        )

        await message.answer(
            "✅ Квиз успешно создан и добавлен в список!",
            reply_markup=get_main_menu_keyboard()
        )
        await state.clear()

    except ValueError as e:
        await message.answer(
            f"❌ Ошибка в формате квиза:\n{e}\n\n"
            "Исправьте и отправьте текст снова или посмотрите пример: /template"
        )
    except Exception as e:
        await message.answer(
            "❌ Произошла непредвиденная ошибка при создании квиза. Попробуйте позже."
        )
        await state.clear()
        raise e
