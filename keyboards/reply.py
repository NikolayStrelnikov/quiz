from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def get_main_menu_keyboard() -> ReplyKeyboardMarkup:
    """Главное меню с reply-кнопками"""
    builder = ReplyKeyboardBuilder()

    builder.row(
        KeyboardButton(text="📝 Создать квиз"),
        KeyboardButton(text="🎮 Пройти квиз")
    )
    builder.row(
        KeyboardButton(text="ℹ️ Помощь"),
        KeyboardButton(text="📊 Моя статистика")
    )

    return builder.as_markup(
        resize_keyboard=True,
        input_field_placeholder="Выберите действие"
    )


def get_cancel_keyboard() -> ReplyKeyboardMarkup:
    """Клавиатура с кнопкой отмены"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="❌ Отменить создание")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )


def get_quiz_actions_keyboard() -> ReplyKeyboardMarkup:
    """Клавиатура действий с квизом"""
    builder = ReplyKeyboardBuilder()

    builder.row(
        KeyboardButton(text="✅ Сохранить квиз"),
        KeyboardButton(text="✏️ Редактировать")
    )
    builder.row(KeyboardButton(text="❌ Удалить квиз"))

    return builder.as_markup(
        resize_keyboard=True,
        selective=True
    )


def get_confirmation_keyboard() -> ReplyKeyboardMarkup:
    """Клавиатура подтверждения действий"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="✅ Да"),
                KeyboardButton(text="❌ Нет")
            ]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
