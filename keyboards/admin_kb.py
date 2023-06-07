from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from lexicon.lexicon import LEXICON_KEYBOARD_ADMIN_DATA
from aiogram.filters.callback_data import CallbackData

class AdminListCF(CallbackData, prefix='list'):
    id: str

class AdminCheckProfileCF(CallbackData, prefix='checked'):
    id: str

class AdminAllPageCF(CallbackData, prefix='all_page'):
    id: int

class AdminCheckedPageCF(CallbackData, prefix='checked_page'):
    id: int

class AdminNotCheckedPageCF(CallbackData, prefix='not_checked_page'):
    id: int

def create_admin_all_profiles_kb(data, page=0):
    """
    Создает клавиатуру с выводом всех анкет.
    """
    return create_pages_kb(data, page, callback_factory=AdminAllPageCF)

def create_admin_checked_profiles_kb(data, page=0):
    """
    Создает клавиатуру с выводом всех обработанных анкет.
    """
    return create_pages_kb(data, page, callback_factory=AdminCheckedPageCF)

def create_admin_not_checked_profiles_kb(data, page=0):
    """
    Создает клавиатуру с выводом всех необработанных анкет.
    """
    return create_pages_kb(data, page, callback_factory=AdminNotCheckedPageCF)

def create_pages_kb(data, page=0, callback_factory = AdminAllPageCF) -> InlineKeyboardMarkup:
    """
    Создает клавиатуру для просмотра администратором анкет.
    Выводит по 5 анкет + паджинатор для остальных в нижнем ряду

    :param data: список выводимых данных
    :type data: list[dict]
    :param page: текущая страницы
    :type page: int
    :rtype: InlineKeyboardMarkup
    """
    # количество записей на одной странице
    n = 5
    kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()

    # вычисляем границы списка показываемых записей - зависит от текущей страницы
    start = page * n
    # в случае, если запрашивается последняя страница записей, но она будет не полной
    if len(data) >= page * n and len(data) < (page + 1) * n:
        finish = len(data)
    else:
        finish = (page + 1) * n
    show_data = data[start:finish]

    # показываем анкеты в виде кнопок
    for i in show_data:
        if i['checked']:
            i['checked'] = LEXICON_KEYBOARD_ADMIN_DATA['checked_icon']
        else:
            i['checked'] = LEXICON_KEYBOARD_ADMIN_DATA['not_checked_icon']
        kb_builder.row(InlineKeyboardButton(text=LEXICON_KEYBOARD_ADMIN_DATA['row'] % i,
                                            callback_data=AdminListCF(id=i['id']).pack()
                                            )
                       )

    # показываем паджинатор. Страницы выводятся не 0,1,2, а 1,2,3 - то есть прибавляем к ним +1
    paginator = []
    current = page + 1
    total = len(data) // 5 if len(data) % 5 == 0 else len(data) // 5 + 1
    # кнопка предыдущей страницы, если есть
    if current > 1:
        paginator.append(
            InlineKeyboardButton(text=f'{LEXICON_KEYBOARD_ADMIN_DATA["previous_page"]} {current-1}', callback_data=callback_factory(id=page-1).pack()))
    # кнопка с текущей страницей
    paginator.append(
        InlineKeyboardButton(text=f'{current}/{total}', callback_data=callback_factory(id=page).pack())
    )

    # кнопка следующей страницы, если есть
    if current < total:
        paginator.append(
            InlineKeyboardButton(text=f'{current+1} {LEXICON_KEYBOARD_ADMIN_DATA["next_page"]}', callback_data=callback_factory(id=page+1).pack()))

    kb_builder.row(*paginator)
    markup = kb_builder.as_markup()
    return markup


def create_admin_to_check_kb(data) -> InlineKeyboardMarkup or None:
    """
    Создает клавиатуру для отметки администратором анкет как обработанных
    (только если анкета еще не обработана)
    :rtype: InlineKeyboardMarkup
    """
    markup = None
    if data['checked'] == LEXICON_KEYBOARD_ADMIN_DATA['not_checked_icon']:
        kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
        kb_builder.row(InlineKeyboardButton(
            text=LEXICON_KEYBOARD_ADMIN_DATA['mark_as_checked'],
            callback_data=AdminCheckProfileCF(id=data['id']).pack()
            )
        )
        markup = kb_builder.as_markup()
    return markup
