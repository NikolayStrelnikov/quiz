from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from database.queries import create_quiz
from keyboards.inline import get_main_menu_keyboard
from keyboards.reply import get_cancel_keyboard
from services.quiz_parser import parse_quiz_text
from states import QuizStates

router = Router()


@router.message(QuizStates.waiting_for_quiz)
async def process_quiz_text(
        message: Message,
        state: FSMContext,
        db: AsyncSession
):
    try:
        # Парсим текст квиза
        quiz_data = parse_quiz_text(message.text)

        # Создаем квиз в базе данных
        quiz = await create_quiz(
            db,
            title=quiz_data['title'],
            description=quiz_data['description'],
            content=message.text,
            creator_id=message.from_user.id
        )

        await message.answer(
            f"✅ Квиз <b>{quiz.title}</b> успешно создан!",
            reply_markup=get_main_menu_keyboard(),
            parse_mode="HTML"
        )
        await state.clear()

    except ValueError as e:
        await message.answer(
            f"❌ Ошибка в формате квиза:\n{e}\n\n"
            "Пожалуйста, исправьте и отправьте текст снова\n"
            "Или нажмите /cancel для отмены",
            reply_markup=get_cancel_keyboard()
        )
    except Exception as e:
        await message.answer(
            "⚠️ Произошла непредвиденная ошибка. Попробуйте позже.",
            reply_markup=get_main_menu_keyboard()
        )
        await state.clear()
        raise e


@router.message(F.text.lower() == "отмена")
async def cancel_quiz_creation(
        message: Message,
        state: FSMContext
):
    await state.clear()
    await message.answer(
        "Создание квиза отменено",
        reply_markup=get_main_menu_keyboard()
    )
