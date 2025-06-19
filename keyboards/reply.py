from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_main_menu_reply() -> ReplyKeyboardMarkup:
    """Главное меню с Reply-клавиатурой"""
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton('Создать квиз ✏️'))
    keyboard.add(KeyboardButton('Пройти квиз 🎮'))
    return keyboard

def get_cancel_keyboard() -> ReplyKeyboardMarkup:
    """Клавиатура с кнопкой отмены"""
    return ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton('Отмена ❌'))