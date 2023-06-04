import logging
from copy import deepcopy

from aiogram import Router
from aiogram.types import Message
from database.database import user_dict_template, users_db
from lexicon.lexicon import LEXICON, LEXICON_MESSAGES, LEXICON_MESSAGES
from aiogram.filters import Command, CommandStart, Text, StateFilter, BaseFilter
from config_data.config import Config, load_config


class IsAdmin(BaseFilter):
    """
    Фильтр проверяет, относится ли текущий пользователь к админам, заявленных в конфиге
    """
    def __init__(self) -> None:
        config = load_config()
        self.admin_ids = config.tg_bot.admin_ids

    async def __call__(self, message: Message) -> bool:
        print(self.admin_ids)
        return message.from_user.id in self.admin_ids


# Этот роутер работает только для админов бота
router: Router = Router()

router.message.filter(IsAdmin())


@router.message(CommandStart())
async def process_start_command(message: Message) -> None:
    """
    Срабатывает на команду /start
    и отправляет ему приветственное сообщение.
    :type message: Message
    """
    logging.info(message.from_user.id)
    logging.info('admin is here')
    await message.answer(
        text=LEXICON_MESSAGES['admin_start'],
    )


@router.message()
async def send_default(message: Message):
    """
    Срабатывает на любые сообщения пользователя, не предусмотренные логикой работы бота
    :type message: Message
    """
    await message.answer(f'{LEXICON_MESSAGES["default"]}')
