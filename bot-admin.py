import asyncio
import logging

from aiogram import Bot, Dispatcher
from config_data.config import Config, load_config
from handlers import admin_handlers
from keyboards.main_menu import set_main_menu

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
    config: Config = load_config('admin.env')

    # Инициализация бота и диспетчера
    bot: Bot = Bot(token=config.tg_bot.token,
                   parse_mode='HTML')
    dp: Dispatcher = Dispatcher()

    # Настройка главного меню бота
    await set_main_menu(bot)

    # Регистрация роутеров для пользователей и администраторов в диспетчере
    dp.include_router(admin_handlers.router)
    # dp.include_router(user_handlers.router)

    # Пропуск накопившиеся апдейты и запуск polling
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())