from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram import Router
from database.queries import create_quiz, get_or_create_user
from services.quiz_parser import parse_quiz_text
from states import QuizStates
from aiogram import Dispatcher

router = Router()

def register_messages(dp: Dispatcher):
    dp.include_router(router)

async def process_quiz_text(message: types.Message, state: FSMContext):
    try:
        quiz_data = parse_quiz_text(message.text)
    except ValueError as e:
        await message.answer(f"Ошибка при разборе квиза: {str(e)}\nПожалуйста, проверьте формат и попробуйте снова.")
        return

    db = message.bot.get('db')
    user = get_or_create_user(
        db,
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        full_name=message.from_user.full_name
    )

    quiz = create_quiz(
        db,
        title=quiz_data['title'],
        description=quiz_data['description'],
        content=message.text,  # Или можно сохранять quiz_data в JSON
        creator_id=user.id
    )

    await message.answer(
        f"Квиз '{quiz.title}' успешно создан и добавлен в список доступных для прохождения!"
    )
    await state.finish()


def register_messages(dp):
    dp.register_message_handler(process_quiz_text, state=QuizStates.waiting_for_quiz)