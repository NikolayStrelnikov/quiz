import html
import re
from dataclasses import dataclass
from typing import List, Dict


class QuizValidationError(ValueError):
    """Кастомное исключение для ошибок валидации квизов"""
    pass


@dataclass
class QuizQuestion:
    text: str
    options: List[str]
    correct_answer: int  # 0-based индекс


def parse_quiz_text(raw_text: str) -> Dict:
    """
    Парсит текст квиза и возвращает структурированные данные
    Формат:
    Название: Название квиза
    Описание: Описание квиза

    Вопрос 1: Текст вопроса
    1. Вариант 1
    2. Вариант 2
    3. Вариант 3
    Правильный ответ: 1

    Вопрос 2: ...
    """
    try:
        # Предварительная очистка и проверка
        text = _sanitize_input(raw_text)
        if not text:
            raise QuizValidationError("Текст квиза пуст")

        lines = [line.strip() for line in text.split('\n') if line.strip()]
        if len(lines) < 5:
            raise QuizValidationError("Текст слишком короткий для квиза")

        quiz_data = {
            'title': '',
            'description': '',
            'questions': []
        }
        current_question = None

        for line in lines:
            # Обработка заголовков
            if _is_header_line(line, "Название"):
                quiz_data['title'] = _parse_header(line, "Название")
            elif _is_header_line(line, "Описание"):
                quiz_data['description'] = _parse_header(line, "Описание")

            # Обработка вопросов
            elif line.startswith(('Вопрос', 'Question')):
                if current_question:
                    _validate_question(current_question)
                    quiz_data['questions'].append(current_question)

                question_text = _parse_question_line(line)
                current_question = {
                    'text': question_text,
                    'options': [],
                    'correct_answer': None
                }

            # Обработка вариантов ответа
            elif re.match(r'^\d+\.', line):
                if not current_question:
                    raise QuizValidationError("Вариант ответа без вопроса")

                option_text = _parse_option_line(line)
                current_question['options'].append(option_text)

            # Обработка правильного ответа
            elif line.startswith(('Правильный ответ', 'Correct answer')):
                if not current_question:
                    raise QuizValidationError("Ответ без вопроса")

                current_question['correct_answer'] = _parse_correct_answer(line)

        # Добавляем последний вопрос
        if current_question:
            _validate_question(current_question)
            quiz_data['questions'].append(current_question)

        # Финальная валидация
        _validate_quiz_structure(quiz_data)
        return quiz_data

    except Exception as e:
        raise QuizValidationError(str(e))


def _sanitize_input(text: str) -> str:
    """Очистка и подготовка входного текста"""
    # Удаляем BOM и лишние пробелы
    text = text.lstrip('\ufeff').strip()
    # Экранируем HTML/XML теги
    return html.escape(text)


def _is_header_line(line: str, prefix: str) -> bool:
    """Проверяет, является ли строка заголовком"""
    return line.startswith((f"{prefix}:", f"{prefix} квиза:"))


def _parse_header(line: str, prefix: str) -> str:
    """Извлекает значение заголовка после указанного префикса

    Args:
        line: Строка для парсинга (например, "Название: Мой квиз")
        prefix: Ожидаемый префикс (например, "Название")

    Returns:
        Значение после двоеточия, очищенное от пробелов

    Raises:
        QuizValidationError: Если формат строки не соответствует ожидаемому
    """
    try:
        parts = line.split(':', 1)
        if len(parts) != 2:
            raise ValueError
        return parts[1].strip()
    except (ValueError, IndexError):
        raise QuizValidationError(f"Неверный формат заголовка {prefix}. Ожидается '{prefix}: значение'")


def _parse_question_line(line: str) -> str:
    """Парсит строку с вопросом"""
    return line.split(':', 1)[1].strip()


def _parse_option_line(line: str) -> str:
    """Парсит вариант ответа"""
    return line.split('.', 1)[1].strip()


def _parse_correct_answer(line: str) -> int:
    """Парсит и проверяет правильный ответ"""
    try:
        answer = int(line.split(':', 1)[1].strip()) - 1  # Конвертируем в 0-based
        if answer < 0:
            raise ValueError("Номер ответа должен быть положительным")
        return answer
    except (ValueError, IndexError):
        raise QuizValidationError("Неверный формат правильного ответа")


def _validate_question(question: Dict) -> None:
    """Валидация отдельного вопроса"""
    if not question['text']:
        raise QuizValidationError("Текст вопроса не может быть пустым")

    if len(question['options']) < 2:
        raise QuizValidationError("Должно быть минимум 2 варианта ответа")

    if question['correct_answer'] is None:
        raise QuizValidationError("Не указан правильный ответ")

    if question['correct_answer'] >= len(question['options']):
        raise QuizValidationError(
            f"Номер правильного ответа ({question['correct_answer'] + 1}) "
            f"превышает количество вариантов ({len(question['options'])})"
        )


def _validate_quiz_structure(quiz_data: Dict) -> None:
    """Финальная валидация всей структуры квиза"""
    if not quiz_data['title']:
        raise QuizValidationError("Не указано название квиза")

    if not quiz_data['questions']:
        raise QuizValidationError("Квиз должен содержать хотя бы один вопрос")

    max_questions = 50
    if len(quiz_data['questions']) > max_questions:
        raise QuizValidationError(f"Максимум {max_questions} вопросов в квизе")

    for i, question in enumerate(quiz_data['questions'], 1):
        try:
            _validate_question(question)
        except QuizValidationError as e:
            raise QuizValidationError(f"Вопрос {i}: {str(e)}")
