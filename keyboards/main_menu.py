from aiogram import Bot
from aiogram.types import BotCommand

from lexicon.lexicon import LEXICON_COMMANDS, LEXICON_COMMANDS_ADMIN


async def set_main_menu(bot: Bot):
    """
    Настраивает главное меню бота для обычных пользователей
    :type bot: Bot
    """
    main_menu_commands = [BotCommand(
        command=command,
        description=description
    ) for command,
        description in LEXICON_COMMANDS.items()]
    await bot.set_my_commands(main_menu_commands)

async def set_main_menu_admin(bot:Bot):
    """
    Настраивает главное меню бота для админов
    :type bot: Bot
    """
    main_menu_commands = [BotCommand(
        command=command,
        description=description
    ) for command,
        description in LEXICON_COMMANDS_ADMIN.items()]
    await bot.set_my_commands(main_menu_commands)