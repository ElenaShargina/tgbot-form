import logging
from copy import deepcopy

from aiogram import Router
from aiogram.types import CallbackQuery, Message
from database.database import user_dict_template, users_db, get_today
from keyboards.form_kb import create_start_form_kb
from lexicon.lexicon import LEXICON, LEXICON_MESSAGES
from aiogram.filters import Command, CommandStart, Text, StateFilter
from aiogram.filters.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.fsm.storage.memory import MemoryStorage


# Cоздаем класс, наследуемый от StatesGroup, для группы состояний нашей FSM
class FSMFillForm(StatesGroup):
    """
    Класс для учета состояний этапов заполнения анкеты
    """
    fill_name = State()  # Состояние ожидания ввода имени
    fill_age = State()  # Состояние ожидания ввода возраста
    fill_gender = State()  # Состояние ожидания выбора пола
    upload_photo = State()  # Состояние ожидания загрузки фото


# Этот роутер работает для всех пользователей кроме админов
router: Router = Router()


@router.message(CommandStart(), StateFilter(default_state))
async def process_start_command(message: Message) -> None:
    """
    Срабатывает на команду /start
    и добавляет пользователя в БД, если его там еще не было,
    и отправляет ему приветственное сообщение.
    :type message: Message
    """
    logging.info('id= ' + str(message.from_user.id))
    await message.answer(
        text=LEXICON[message.text],
        reply_markup=create_start_form_kb()
    )


@router.message(Command(commands='cancel'), ~StateFilter(default_state))
async def process_cancel_command_state(message: Message, state: FSMContext):
    """
    Срабатывает на команду /cancel во всех состояниях кроме дефолтного
    и останавливает работу машины состояний
    :type message: Message
    :type state: FSMContext
    """
    await message.answer(text='cancel_non_default_state')
    # Сбрасываем состояние
    await state.clear()


@router.message(Command(commands='cancel'), StateFilter(default_state))
async def process_cancel_command(message: Message):
    """
    Срабатывает на команду /cancel в дефолтном состоянии и сообщает,
    что она доступна только в процессе заполнения анкеты
    :type message: Message
    :type state: FSMContext
    """
    await message.answer(text=LEXICON_MESSAGES['cancel_default_state'])


@router.message(Command(commands='help'))
async def process_help_command(message: Message):
    """
    Срабатывает на команду /help
    и отправляет пользователю сообщение со списком доступных команд в боте
    :type message: Message
    """
    await message.answer(LEXICON[message.text],
                         )

@router.message(Command(commands='fill'), StateFilter(default_state))
@router.callback_query(Text(text='fill'), StateFilter(default_state))
async def process_fill_command(message: Message, state: FSMContext, callback:CallbackQuery=None, ):
    """
    Срабатывает на команду /fill
    :type message: Message
    """
    if getattr(message, 'data'):
        print(message.data)
        await callback.message.answer(LEXICON_MESSAGES['fill_start'] + LEXICON_MESSAGES['fill_name'])
    else:
        print('usual')
        await message.answer(LEXICON_MESSAGES['fill_start'] + LEXICON_MESSAGES['fill_name'])

    await state.set_state(FSMFillForm.fill_name)

# @router.callback_query(Text(text='fill'), StateFilter(default_state))
# async def process_fill_callback(callback: CallbackQuery, state: FSMContext):
#     """
#     Срабатывает на нажатие инлайн-кнопки fill
#     :type message: Message
#     """
#     await callback.message.answer(LEXICON_MESSAGES['fill_start'] + LEXICON_MESSAGES['fill_name'])
#     await state.set_state(FSMFillForm.fill_name)

@router.message()
async def send_default(message: Message):
    """
    Срабатывает на любые сообщения пользователя, не предусмотренные логикой работы бота
    :type message: Message
    """
    await message.answer(LEXICON_MESSAGES["default"])
