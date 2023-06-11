from aiogram import Bot
from aiogram.types import BotCommand

from lexicon.lexicon import LEXICON_USER_MENU, LEXICON_ADMIN_MENU


async def set_main_menu_user(bot: Bot):
    """
    Настраивает главное меню бота для обычных пользователей
    :type bot: Bot
    """
    main_menu_commands = [BotCommand(
        command=command,
        description=description
    ) for command,
        description in LEXICON_USER_MENU.items()]
    await bot.set_my_commands(main_menu_commands)

async def set_main_menu_admin(bot: Bot):
    """
    Настраивает главное меню бота для администраторов
    :type bot: Bot
    """
    main_menu_commands = [BotCommand(
        command=command,
        description=description
    ) for command,
        description in LEXICON_ADMIN_MENU.items()]
    await bot.set_my_commands(main_menu_commands)