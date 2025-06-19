from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
import logging
from sqlalchemy import delete
from config import ADMIN_IDS
from database.queries import create_quiz
from services.quiz_parser import parse_quiz_text, QuizValidationError
from states import QuizStates
from keyboards.inline import get_main_menu_keyboard
from keyboards.reply import get_cancel_keyboard

router = Router()
logger = logging.getLogger(__name__)


@router.message(QuizStates.waiting_for_quiz)
async def process_quiz_text(
        message: Message,
        state: FSMContext,
        db: AsyncSession
) -> None:
    """
    Обработчик текста квиза с полной валидацией и транзакциями
    """
    try:
        # Парсинг с валидацией
        quiz_data = parse_quiz_text(message.text)

        # Транзакция для создания квиза
        async with db.begin():
            quiz = await create_quiz(
                db,
                title=quiz_data['title'],
                description=quiz_data['description'],
                content=message.text,  # Сохраняем оригинальный текст
                creator_id=message.from_user.id
            )

            await message.answer(
                f"✅ Квиз <b>{quiz.title}</b> успешно создан!\n"
                f"Вопросов: {len(quiz_data['questions'])}",
                reply_markup=get_main_menu_keyboard(),
                parse_mode="HTML"
            )
            await state.clear()

    except QuizValidationError as e:
        logger.warning(f"Validation error: {e}")
        await message.answer(
            f"❌ Ошибка в формате квиза:\n{e}\n\n"
            "Исправьте и отправьте текст снова или нажмите /cancel",
            reply_markup=get_cancel_keyboard()
        )

    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        await message.answer(
            "⚠️ Произошла непредвиденная ошибка. Попробуйте позже.",
            reply_markup=get_main_menu_keyboard()
        )
        await state.clear()


@router.message(F.text.lower().in_(["отмена", "cancel"]))
async def cancel_operation(
        message: Message,
        state: FSMContext
) -> None:
    """
    Обработчик отмены действий с очисткой состояния
    """
    current_state = await state.get_state()
    if not current_state:
        return

    try:
        await state.clear()
        await message.answer(
            "❌ Действие отменено",
            reply_markup=get_main_menu_keyboard()
        )
    except Exception as e:
        logger.error(f"Error clearing state: {e}")
        await message.answer(
            "⚠️ Ошибка при отмене операции",
            reply_markup=get_main_menu_keyboard()
        )


@router.message(F.text == "/cleanup")
async def cleanup_database(
        message: Message,
        db: AsyncSession
) -> None:
    """
    Админская команда для очистки тестовых данных
    """
    try:
        # Проверка прав администратора
        if message.from_user.id not in ADMIN_IDS:
            await message.answer("⛔ Доступ запрещен")
            return

        async with db.begin():
            # Пример очистки - адаптируйте под свои модели
            from database.models import Quiz, QuizResult
            await db.execute(delete(QuizResult))
            await db.execute(delete(Quiz))
            await message.answer("🗑️ База данных очищена")

    except Exception as e:
        logger.error(f"Cleanup error: {e}")
        await message.answer("⚠️ Ошибка при очистке БД")