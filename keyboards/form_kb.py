from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from lexicon.lexicon import LEXICON_KEYBOARD


def create_start_form_kb() -> InlineKeyboardMarkup:
    """
    Генерирует клавиатуру для начала заполнения анкеты
    :rtype: InlineKeyboardMarkup
    """
    # Инициализируем билдер
    kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
    # Добавляем в билдер ряд с кнопками
    kb_builder.add(
        InlineKeyboardButton(
            text=LEXICON_KEYBOARD['start_form'],
            callback_data='fill'
        )
    )
    # Возвращаем объект инлайн-клавиатуры
    return kb_builder.as_markup()