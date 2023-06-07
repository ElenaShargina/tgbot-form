import logging
from copy import deepcopy

from aiogram import Router
from aiogram.types import Message, CallbackQuery, FSInputFile
from lexicon.lexicon import LEXICON_MESSAGES, LEXICON_ADMIN_MENU
from aiogram.filters import Command, CommandStart,  BaseFilter
from config_data.config import load_config
from database.database import show_profiles, show_profile, update_profile_as_checked
from keyboards.admin_kb import (AdminListCF,
                                AdminCheckProfileCF,
                                create_admin_to_check_kb,
                                create_admin_checked_profiles_kb, create_admin_all_profiles_kb,
                                create_admin_not_checked_profiles_kb,
                                AdminAllPageCF, AdminNotCheckedPageCF, AdminCheckedPageCF)


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


# Этот роутер будет работать только для администраторов бота (их id перечислены в .env)
router: Router = Router()

router.message.filter(IsAdmin())


@router.message(CommandStart())
async def process_start_command(message: Message) -> None:
    """
    Срабатывает на команду /start
    и отправляет ему приветственное сообщение со списком всех анкет.
    :type message: Message
    """
    admin_menu = '\n\n'.join(f'{i} - {j}' for i,j in LEXICON_ADMIN_MENU.items())
    await message.answer(
        text=LEXICON_MESSAGES['admin_start']+'\n\n'+admin_menu,
    )

@router.message(Command(commands='all'))
async def process_all_command(message:Message) -> None:
    """
    Срабатывает на команду /all
    Показывает все анкеты, обработанные и нет
    :type message: Message
    """
    all_profiles = await show_profiles()
    await message.answer(text=LEXICON_MESSAGES['admin_show_all'],
                         reply_markup=create_admin_all_profiles_kb(all_profiles)
                         )

@router.message(Command(commands='checked'))
async def process_checked_command(message:Message) -> None:
    """
    Срабатывает на команду /checked
    Показывает все обработанные  анкеты
    :type message: Message
    """
    profiles = await show_profiles(status='checked')
    await message.answer(text=LEXICON_MESSAGES['admin_show_checked'],
                         reply_markup=create_admin_checked_profiles_kb(profiles)
                         )

@router.message(Command(commands='not_checked'))
async def process_not_checked_command(message:Message) -> None:
    """
    Срабатывает на команду /not_checked
    Показывает все необработанные  анкеты
    :type message: Message
    """
    profiles = await show_profiles(status='not_checked')
    await message.answer(text=LEXICON_MESSAGES['admin_show_not_checked'],
                         reply_markup=create_admin_not_checked_profiles_kb(profiles)
                         )

@router.callback_query(AdminCheckedPageCF.filter())
async def process_checked_page_press(callback: CallbackQuery, callback_data:AdminCheckProfileCF):
    """
    Срабатывает, если администратором была нажата кнопка со страницей в списке ОБРАБОТАННЫХ анкет
    """
    profiles = await show_profiles(status='checked')
    await callback.message.edit_text(text=LEXICON_MESSAGES['admin_show_checked'],
                                     reply_markup=create_admin_checked_profiles_kb(profiles,callback_data.id)
                                     )

@router.callback_query(AdminNotCheckedPageCF.filter())
async def process_unchecked_page_press(callback: CallbackQuery, callback_data:AdminNotCheckedPageCF):
    """
    Срабатывает, если администратором была нажата кнопка со страницей в списке НЕОБРАБОТАННЫХ анкет
    """
    profiles = await show_profiles(status='not_checked')
    await callback.message.edit_text(text=LEXICON_MESSAGES['admin_show_not_checked'],
                                     reply_markup=create_admin_not_checked_profiles_kb(profiles, callback_data.id)
                                     )

@router.callback_query(AdminAllPageCF.filter())
async def process_all_page_press(callback: CallbackQuery, callback_data:AdminAllPageCF):
    """
    Срабатывает, если администратором была нажата кнопка со страницей в списке ВСЕХ анкет
    """
    profiles = await show_profiles(status='all')
    await callback.message.edit_text(text=LEXICON_MESSAGES['admin_show_all'],
                                     reply_markup=create_admin_all_profiles_kb(profiles,callback_data.id)
                                     )


@router.callback_query(AdminListCF.filter())
async def process_profile_press(callback: CallbackQuery, callback_data:AdminListCF):
    """
    Срабатывает, если администратором нажата кнопка с анкетой
    Выводит анкету с фотографией
    """
    full_info = await show_profile(callback_data.id)
    my_config = load_config()
    photo = FSInputFile(my_config.photo_folder.folder+full_info['photo'])
    if full_info['checked']:
        full_info['checked'] = LEXICON_MESSAGES['checked_icon']
    else:
        full_info['checked'] = LEXICON_MESSAGES['not_checked_icon']
    await callback.message.answer_photo(caption=LEXICON_MESSAGES['data_for_admin'] % full_info,
                                        photo = photo,
                                        reply_markup=create_admin_to_check_kb(full_info))

@router.callback_query(AdminCheckProfileCF.filter())
async def process_checked_press(callback: CallbackQuery, callback_data:AdminCheckProfileCF):
    """
    Срабатывает, если администратором нажата кнопка "ОБРАБОТАНО" на анкете
    меняет в БД статус анкеты на "обработано"
    """
    updated_info = await update_profile_as_checked(callback_data.id)
    if updated_info['checked']:
        updated_info['checked'] = LEXICON_MESSAGES['checked_icon']
    else:
        updated_info['checked'] = LEXICON_MESSAGES['not_checked_icon']
    await callback.message.edit_caption(caption=LEXICON_MESSAGES['data_for_admin'] % updated_info, reply_markup=None)

@router.message(Command(commands='help'))
async def send_help(message: Message):
    """
    Срабатывает на команду \help
    :type message: Message
    """
    admin_menu = '\n\n'.join(f'{i} - {j}' for i, j in LEXICON_ADMIN_MENU.items())
    await message.answer(f'{LEXICON_MESSAGES["admin_help"]}\n\n{admin_menu}')

@router.message()
async def send_default(message: Message):
    """
    Срабатывает на любые сообщения пользователя, не предусмотренные логикой работы бота
    :type message: Message
    """
    admin_menu = '\n\n'.join(f'{i} - {j}' for i, j in LEXICON_ADMIN_MENU.items())
    await message.answer(f'{LEXICON_MESSAGES["admin_default"]}\n\n{admin_menu}')

