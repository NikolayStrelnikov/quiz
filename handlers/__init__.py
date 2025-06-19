from aiogram import Dispatcher

from .callbacks import router as callbacks_router
from .commands import router as commands_router
from .messages import router as messages_router


def register_all_handlers(dp: Dispatcher) -> None:
    """
    Регистрирует все обработчики в диспетчере
    Порядок регистрации важен - первые роутеры имеют приоритет
    """
    dp.include_router(commands_router)
    dp.include_router(callbacks_router)
    dp.include_router(messages_router)
