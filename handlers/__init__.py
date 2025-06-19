from aiogram import Dispatcher


def register_all_handlers(dp: Dispatcher) -> None:
    from .commands import register_commands
    from .callbacks import register_callbacks
    from .messages import register_messages

    register_commands(dp)
    register_callbacks(dp)
    register_messages(dp)