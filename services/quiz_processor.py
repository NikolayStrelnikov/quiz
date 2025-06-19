from typing import Dict, List


def process_quiz(quiz_content: str) -> List[Dict]:
    """Обрабатывает контент квиза и возвращает структурированные данные"""
    questions = []
    current_question = None

    for line in quiz_content.split('\n'):
        line = line.strip()
        if not line:
            continue

        if line.startswith('Вопрос'):
            if current_question:
                questions.append(current_question)
            current_question = {
                'text': line.split(':', 1)[1].strip(),
                'options': [],
                'correct_answer': None
            }
        elif line[0].isdigit() and line[1] == '.':
            if current_question:
                current_question['options'].append(line.split('.', 1)[1].strip())
        elif line.startswith('Правильный ответ:'):
            if current_question:
                current_question['correct_answer'] = int(line.split(':')[1].strip()) - 1

    if current_question:
        questions.append(current_question)

    return questions
