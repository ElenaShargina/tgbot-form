import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from config_data.config import Config, load_config
from handlers import user_handlers
from keyboards.main_menu import set_main_menu_user
from database.database import db_init

# Инициализация логгера
logger = logging.getLogger(__name__)

async def main():
    """
    Функция конфигурации и запуска бота
    """
    # Настройка логгирования
    logging.basicConfig(
        level=logging.INFO,
        format='%(filename)s:%(lineno)d #%(levelname)-8s '
               '[%(asctime)s] - %(name)s - %(message)s')

    # Вывод в лог информацию о начале запуска бота
    logger.info('Starting bot')

    # Загрузка конфига в переменную config
    config: Config = load_config(os.path.join(os.path.dirname(__file__),'user.env'))

    # Инициализация базы данных - если нужно, создание семпловой
    db_init(config)

    # Инициализация бота и диспетчера
    bot: Bot = Bot(token=config.tg_bot.token,
                   parse_mode='HTML')
    dp: Dispatcher = Dispatcher()

    # Настройка главного меню бота
    await set_main_menu_user(bot)

    # Регистрация роутеров для пользователей  диспетчере
    # dp.include_router(admin_handlers.router)
    dp.include_router(user_handlers.router)

    # Пропуск накопившиеся апдейты и запуск polling
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())