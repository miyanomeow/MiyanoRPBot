import asyncio
import logging
from aiogram import Bot, Dispatcher
from config import config
from handlers import inline

async def main():
    # Настройка логирования
    logging.basicConfig(level=logging.INFO)

    bot = Bot(token=config.bot_token.get_secret_value())
    dp = Dispatcher()

    # Регистрация роутеров
    dp.include_router(inline.router)

    # Пропускаем накопившиеся апдейты и запускаем поллинг
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())