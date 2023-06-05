import logging
from copy import deepcopy

from aiogram import Router
from aiogram.types import Message, CallbackQuery, FSInputFile
from lexicon.lexicon import LEXICON, LEXICON_MESSAGES, LEXICON_MESSAGES
from aiogram.filters import Command, CommandStart, Text, StateFilter, BaseFilter
from config_data.config import Config, load_config
from database.database import show_users, show_user, update_user_as_checked
from keyboards.form_kb import create_admin_data_kb, AdminListCallbackFactory,AdminCheckCallbackFactory, create_admin_checked_kb


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
    stat = await show_users()
    await message.answer(
        text=LEXICON_MESSAGES['admin_start'],
        reply_markup=create_admin_data_kb(stat)
    )

@router.callback_query(AdminListCallbackFactory.filter())
async def process_user_press(callback: CallbackQuery, callback_data:AdminListCallbackFactory):
    """
    Срабатывает, если администратором нажата кнопка с заполненной анкетой
    Выводит анкету с фотографией
    """
    full_info = await show_user(callback_data.id)
    my_config = load_config()
    photo = FSInputFile(my_config.photo_folder.folder+full_info['photo'])
    if full_info['checked']:
        full_info['checked'] = LEXICON_MESSAGES['checked_icon']
    else:
        full_info['checked'] = LEXICON_MESSAGES['not_checked_icon']
    await callback.message.answer_photo(caption=LEXICON_MESSAGES['data_for_admin'] % full_info,
                                        photo = photo,
                                        reply_markup=create_admin_checked_kb(full_info))

@router.callback_query(AdminCheckCallbackFactory.filter())
async def process_checked_press(callback: CallbackQuery, callback_data:AdminCheckCallbackFactory):
    """
    Срабатывает, если администратором нажата кнопка "ОБРАБОТАНО" на анкете
    меняет в БД статус анкеты на "обработано"
    """
    await update_user_as_checked(callback_data.id)
    await callback.message.edit_caption(caption='ОБРАБОТАНО', reply_markup=None)

@router.message()
async def send_default(message: Message):
    """
    Срабатывает на любые сообщения пользователя, не предусмотренные логикой работы бота
    :type message: Message
    """
    await message.answer(f'{LEXICON_MESSAGES["default"]}')

