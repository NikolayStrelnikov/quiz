from aiogram import Dispatcher
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from database.queries import get_or_create_user, get_active_quizzes
from keyboards.inline import get_quizzes_keyboard, get_main_menu_keyboard
from states import QuizStates

router = Router()


def register_commands(dp: Dispatcher):
    dp.include_router(router)


@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()

    # Регистрируем/получаем пользователя
    db = message.bot.get("db")
    user = get_or_create_user(
        db,
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        full_name=message.from_user.full_name
    )

    await message.answer(
        "Добро пожаловать в QuizBot!\n\n"
        "Вы можете:\n"
        "- Создать новый квиз командой /create\n"
        "- Пройти доступные квизы командой /run",
        reply_markup=get_main_menu_keyboard()
    )


@router.message(Command("create"))
async def cmd_create(message: Message, state: FSMContext):
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
        "Вопрос 2: Текст вопроса\n"
        "... (и так далее)\n\n"
        "Пример вы можете получить по команде /template"
    )
    await state.set_state(QuizStates.waiting_for_quiz)


@router.message(Command("template"))
async def cmd_template(message: Message):
    await message.answer(
        "Пример квиза:\n\n"
        "Название квиза: Основы Python\n"
        "Описание: Тест по базовому синтаксису Python\n\n"
        "Вопрос 1: Как объявить список?\n"
        "1. list = {}\n"
        "2. list = []\n"
        "3. list = ()\n"
        "4. list = <>\n"
        "Правильный ответ: 2\n\n"
        "Вопрос 2: Какой оператор используется для возведения в степень?\n"
        "1. ^\n"
        "2. **\n"
        "3. *\n"
        "4. !\n"
        "Правильный ответ: 2"
    )


@router.message(Command("run"))
async def cmd_run(message: Message, state: FSMContext):
    await state.clear()
    db = message.bot.get("db")
    quizzes = get_active_quizzes(db)

    if not quizzes:
        await message.answer("❌ Нет доступных квизов для прохождения.")
        return

    await message.answer(
        "📋 Выберите квиз для прохождения:",
        reply_markup=get_quizzes_keyboard(quizzes)
    )


@router.callback_query(F.data == "main_menu")
async def main_menu_callback(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        "Главное меню:",
        reply_markup=get_main_menu_keyboard()
    )
    await callback.answer()
