import os

from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_IDS = list(map(int, os.getenv('ADMIN_IDS', '').split(',')))
DATABASE_URL = "sqlite+aiosqlite:///database/quiz_bot.db"

QUIZ_TEMPLATE = """Название квиза: {quiz_name}
Описание: {quiz_description}

Вопрос 1: {question1}
1. {option1_1}
2. {option1_2}
3. {option1_3}
4. {option1_4}
Правильный ответ: {correct_answer1}

Вопрос 2: {question2}
1. {option2_1}
2. {option2_2}
3. {option2_3}
4. {option2_4}
Правильный ответ: {correct_answer2}
"""
