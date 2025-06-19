import asyncio

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from config import BOT_TOKEN, DATABASE_URL
from database.models import Base
from handlers import register_all_handlers


async def setup_database():
    """Настройка подключения к базе данных"""
    engine = create_async_engine(DATABASE_URL, echo=True)

    # Создаем таблицы (в продакшене лучше использовать миграции)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    return async_sessionmaker(engine, expire_on_commit=False)


async def main():
    # Инициализация бота и хранилища состояний
    bot = Bot(token=BOT_TOKEN, parse_mode="HTML")
    dp = Dispatcher(storage=MemoryStorage())

    # Настройка сессий БД
    session_maker = await setup_database()

    # Middleware для инъекции сессий
    @dp.update.outer_middleware()
    async def db_session_middleware(handler, event, data):
        async with session_maker() as session:
            data["db"] = session
            try:
                return await handler(event, data)
            except Exception as e:
                await session.rollback()
                raise e
            finally:
                await session.close()

    # Регистрация обработчиков
    register_all_handlers(dp)

    # Запуск бота
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
