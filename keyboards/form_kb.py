from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from lexicon.lexicon import LEXICON_KEYBOARD_GENDER, LEXICON_KEYBOARD_ADMIN_DATA
from aiogram.filters.callback_data import CallbackData


def create_gender_kb() -> InlineKeyboardMarkup:
    """
    Создает клавиатуру для выбора пола
    :rtype: InlineKeyboardButton
    """
    male_button = InlineKeyboardButton(text=LEXICON_KEYBOARD_GENDER['male'],
                                       callback_data='male')
    female_button = InlineKeyboardButton(text=LEXICON_KEYBOARD_GENDER['female'],
                                         callback_data='female')
    undefined_button = InlineKeyboardButton(text=LEXICON_KEYBOARD_GENDER['undefined_gender'],
                                            callback_data='undefined_gender')
    keyboard: list[list[InlineKeyboardButton]] = [[male_button, female_button],
                                                  [undefined_button]]
    markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    return markup


class AdminListCallbackFactory(CallbackData, prefix='list'):
    id: str

class AdminCheckCallbackFactory(CallbackData, prefix='checked'):
    id: str

def create_admin_data_kb(data) -> InlineKeyboardMarkup:
    """
    Создает клавиатуру для просмотра администратором заполненных анкет
    :rtype: InlineKeyboardMarkup
    """
    kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
    for i in data:
        if i['checked']:
            i['checked'] = LEXICON_KEYBOARD_ADMIN_DATA['checked_icon']
        else:
            i['checked'] = LEXICON_KEYBOARD_ADMIN_DATA['not_checked_icon']
        kb_builder.row(InlineKeyboardButton(text=LEXICON_KEYBOARD_ADMIN_DATA['row'] % i,
                                            callback_data = AdminListCallbackFactory(id=i['id']).pack()
                                            )
                       )
    markup = kb_builder.as_markup()
    return markup

def create_admin_checked_kb(data) -> InlineKeyboardMarkup:
    """
    Создает клавиатуру для отметки администратором просмотренных анкет
    :rtype: InlineKeyboardMarkup
    """
    kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
    kb_builder.row(InlineKeyboardButton(
                                    text=LEXICON_KEYBOARD_ADMIN_DATA['mark_as_checked'],
                                    callback_data = AdminCheckCallbackFactory(id=data['id']).pack()
                                    )
                    )
    markup = kb_builder.as_markup()
    return markup