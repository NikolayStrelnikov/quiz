from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    """Главное меню с основными действиями"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="📝 Создать квиз", callback_data="create_quiz"),
        InlineKeyboardButton(text="🎮 Пройти квиз", callback_data="run_quiz")
    )
    return builder.as_markup()


def get_quizzes_keyboard(quizzes: list) -> InlineKeyboardMarkup:
    """Клавиатура со списком доступных квизов"""
    builder = InlineKeyboardBuilder()

    for quiz in quizzes:
        builder.row(
            InlineKeyboardButton(
                text=f"📌 {quiz.title}",
                callback_data=f"quiz_{quiz.id}"
            )
        )

    builder.row(
        InlineKeyboardButton(
            text="🔙 Назад",
            callback_data="main_menu"
        )
    )
    return builder.as_markup()


def get_question_keyboard(options: list[str]) -> InlineKeyboardMarkup:
    """Клавиатура с вариантами ответа на вопрос"""
    builder = InlineKeyboardBuilder()

    for index, option in enumerate(options):
        builder.row(
            InlineKeyboardButton(
                text=f"{index + 1}. {option}",
                callback_data=f"answer_{index}"
            )
        )

    return builder.as_markup()


def get_quiz_result_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура после завершения квиза"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="🔄 Пройти еще раз",
            callback_data="retry_quiz"
        ),
        InlineKeyboardButton(
            text="📋 К списку квизов",
            callback_data="run_quiz"
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="🏠 В главное меню",
            callback_data="main_menu"
        )
    )
    return builder.as_markup()


def get_cancel_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для отмены действия"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="❌ Отменить",
            callback_data="cancel_action"
        )
    )
    return builder.as_markup()


def get_confirmation_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура подтверждения создания квиза"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="✅ Подтвердить",
            callback_data="confirm_quiz"
        ),
        InlineKeyboardButton(
            text="✏️ Редактировать",
            callback_data="edit_quiz"
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="❌ Отменить",
            callback_data="cancel_quiz"
        )
    )
    return builder.as_markup()
