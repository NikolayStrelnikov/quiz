import re


def parse_quiz_text(text: str):
    lines = [line.strip() for line in text.split('\n') if line.strip()]

    quiz_data = {
        'title': '',
        'description': '',
        'questions': []
    }

    current_question = None

    for line in lines:
        if line.startswith('Название квиза:'):
            quiz_data['title'] = line.split(':', 1)[1].strip()
        elif line.startswith('Описание:'):
            quiz_data['description'] = line.split(':', 1)[1].strip()
        elif line.startswith('Вопрос'):
            if current_question:
                quiz_data['questions'].append(current_question)

            question_num = re.search(r'Вопрос (\d+):', line)
            if not question_num:
                raise ValueError("Неверный формат вопроса")

            current_question = {
                'text': line.split(':', 1)[1].strip(),
                'options': [],
                'correct_answer': None
            }
        elif re.match(r'^\d+\.', line):
            if not current_question:
                raise ValueError("Вариант ответа без вопроса")

            option = line.split('.', 1)[1].strip()
            current_question['options'].append(option)
        elif line.startswith('Правильный ответ:'):
            if not current_question:
                raise ValueError("Правильный ответ без вопроса")

            answer = line.split(':', 1)[1].strip()
            try:
                current_question['correct_answer'] = int(answer) - 1  # Приводим к 0-based индексу
            except ValueError:
                raise ValueError("Правильный ответ должен быть числом")

    if current_question:
        quiz_data['questions'].append(current_question)

    # Валидация
    if not quiz_data['title']:
        raise ValueError("Не указано название квиза")

    if not quiz_data['questions']:
        raise ValueError("Квиз должен содержать хотя бы один вопрос")

    for i, question in enumerate(quiz_data['questions'], start=1):
        if len(question['options']) < 2:
            raise ValueError(f"Вопрос {i} должен иметь хотя бы 2 варианта ответа")
        if question['correct_answer'] is None:
            raise ValueError(f"Не указан правильный ответ для вопроса {i}")
        if question['correct_answer'] >= len(question['options']):
            raise ValueError(f"Правильный ответ для вопроса {i} выходит за пределы количества вариантов")

    return quiz_data