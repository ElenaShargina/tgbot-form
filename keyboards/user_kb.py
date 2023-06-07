from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from lexicon.lexicon import LEXICON_KEYBOARD_GENDER



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
