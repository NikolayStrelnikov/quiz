import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage  # Измененный путь

from config import BOT_TOKEN
from database import Base, engine
from handlers import register_all_handlers


async def main():
    # Создаем таблицы в БД
    Base.metadata.create_all(bind=engine)

    # Инициализация бота и диспетчера
    bot = Bot(token=BOT_TOKEN, parse_mode="HTML")
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)  # В aiogram 3.x Dispatcher создается иначе

    # Подключение базы данных к боту
    from database import get_db
    dp["db"] = next(get_db())

    # Регистрация всех обработчиков
    register_all_handlers(dp)

    # Запуск бота
    try:
        await dp.start_polling(bot)  # В aiogram 3.x бот передается явно
    finally:
        await storage.close()
        await bot.session.close()


if __name__ == '__main__':
    asyncio.run(main())