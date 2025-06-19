from aiogram.fsm.state import State, StatesGroup


class QuizStates(StatesGroup):
    """
    Группа состояний для работы с квизами
    """
    # Состояния создания квиза
    waiting_for_quiz = State()  # Ожидание текста квиза от пользователя
    quiz_validation = State()  # Проверка валидности квиза
    quiz_confirmation = State()  # Подтверждение перед сохранением

    # Состояния прохождения квиза
    quiz_selection = State()  # Выбор квиза из списка
    quiz_in_progress = State()  # Процесс прохождения квиза
    waiting_for_answer = State()  # Ожидание ответа на текущий вопрос

    # Состояния редактирования
    editing_quiz_title = State()  # Редактирование названия квиза
    editing_quiz_description = State()  # Редактирование описания
    editing_question = State()  # Редактирование вопроса
    editing_options = State()  # Редактирование вариантов ответа
    editing_correct_answer = State()  # Изменение правильного ответа

    # Административные состояния
    quiz_management = State()  # Управление квизами (активация/деактивация)
    user_stats_view = State()  # Просмотр статистики пользователей


class AdminStates(StatesGroup):
    """
    Группа состояний для административных функций
    """
    waiting_for_admin_command = State()  # Ожидание команды администрирования
    user_management = State()  # Управление пользователями
    broadcast_message = State()  # Рассылка сообщений


class UserProfileStates(StatesGroup):
    """
    Группа состояний для работы с профилем пользователя
    """
    editing_profile = State()  # Редактирование профиля
    viewing_history = State()  # Просмотр истории прохождений
    stats_selection = State()  # Выбор типа статистики
