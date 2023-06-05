import logging
from copy import deepcopy

from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, Message, PhotoSize
from keyboards.form_kb import create_gender_kb
from lexicon.lexicon import LEXICON, LEXICON_MESSAGES, LEXICON_KEYBOARD_GENDER
from aiogram.filters import Command, CommandStart, Text, StateFilter
from aiogram.filters.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.fsm.storage.memory import MemoryStorage
from database.database import save_profile
from os.path import splitext
from config_data.config import load_config


# Cоздаем класс, наследуемый от StatesGroup, для группы состояний нашей FSM
class FSMFillForm(StatesGroup):
    """
    Класс для учета состояний этапов заполнения анкеты
    """
    fill_name = State()  # Состояние ожидания ввода имени
    fill_age = State()  # Состояние ожидания ввода возраста
    fill_gender = State()  # Состояние ожидания выбора пола
    fill_email = State() # Состояние ожидания ввода email
    upload_photo = State()  # Состояние ожидания загрузки фото


# Этот роутер работает для всех пользователей кроме админов
router: Router = Router()


@router.message(CommandStart(), StateFilter(default_state))
async def process_start_command(message: Message) -> None:
    """
    Срабатывает на команду /start
    Отправляет приветственное сообщение.
    :type message: Message
    """
    await message.answer(
        text=LEXICON[message.text],
    )


@router.message(Command(commands='cancel'), ~StateFilter(default_state))
async def process_cancel_command_state(message: Message, state: FSMContext):
    """
    Срабатывает на команду /cancel во всех состояниях кроме дефолтного
    и останавливает работу машины состояний
    :type message: Message
    :type state: FSMContext
    """
    await message.answer(text=LEXICON_MESSAGES['cancel_non_default_state'])
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
async def process_fill_command(message: Message, state: FSMContext ):
    """
    Срабатывает на команду /fill
    Устанавливает состояние fill_name
    :type message: Message
    """
    await message.answer(text='\n\n'.join([LEXICON_MESSAGES['fill_start'], LEXICON_MESSAGES['fill_name']]))
    await state.set_state(FSMFillForm.fill_name)

@router.message(StateFilter(FSMFillForm.fill_name), F.text.isalpha())
async def process_name_sent(message: Message, state: FSMContext):
    """
    Срабатывает при КОРРЕКТНОМ вводе имени.
    Сохраняет введенное значение.
    Просит ввести возраст.
    Устанавливает состояние fill_age
    :type message: Message
    :type state: FSMContext
    """
    await state.update_data(name=message.text)
    await message.answer(text='\n\n'.join([LEXICON_MESSAGES['fill_thank'],LEXICON_MESSAGES['fill_age']]))
    await state.set_state(FSMFillForm.fill_age)

@router.message(StateFilter(FSMFillForm.fill_name))
async def warning_name_sent(message: Message, state: FSMContext):
    """
    Срабатывает при НЕКОРРЕКТНОМ вводе имени.
    :type message: Message
    :type state: FSMContext
    """
    await state.update_data(name=message.text)
    await message.answer(text='\n\n'.join([LEXICON_MESSAGES['fill_name_error'],LEXICON_MESSAGES['cancel']]))

@router.message(StateFilter(FSMFillForm.fill_age),
            lambda x: x.text.isdigit() and 4 <= int(x.text) <= 120)
async def process_age_sent(message: Message, state: FSMContext):
    """
    Срабатывает, если КОРРЕКТНО введен возраст
    Сохраняет введенное значение
    Выводит запрос на пол
    Устанавливает состояние fill_gender
    :type message: Message
    :type state: FSMContext
    """
    await state.update_data(age=message.text)
    await message.answer(text='\n\n'.join([LEXICON_MESSAGES['fill_thank'],LEXICON_MESSAGES['fill_gender']]),
                         reply_markup=create_gender_kb())
    await state.set_state(FSMFillForm.fill_gender)


@router.message(StateFilter(FSMFillForm.fill_age))
async def warning_sent_age(message: Message):
    """
    Срабатывает, если НЕКОРРЕКТНО введен возраст
    :type message: Message
    """
    await message.answer(
        text='\n\n'.join([LEXICON_MESSAGES['fill_age_error'],LEXICON_MESSAGES['cancel']]))


@router.callback_query(StateFilter(FSMFillForm.fill_gender),
                   Text(text=['male', 'female', 'undefined_gender']))
async def process_gender_press(callback: CallbackQuery, state: FSMContext):
    """
    Срабатывает, если КОРРЕКТНО введен пол
    Сохраняет введенное значение
    Выводит запрос на фото
    Устанавливает состояние fill_email
    :type message: Message
    :type state: FSMContext
    """
    await state.update_data(gender=callback.data)
    # редактируем предыдущее сообщение - убираем клавиатуру, выводис сообщение о том, какой пол был выбран
    await callback.message.edit_text(text=LEXICON_MESSAGES['fill_gender_result'] + LEXICON_KEYBOARD_GENDER[callback.data],reply_markup=None)
    await callback.message.answer(text='\n\n'.join([LEXICON_MESSAGES['fill_thank'],LEXICON_MESSAGES['fill_email']]))
    await state.set_state(FSMFillForm.fill_email)


@router.message(StateFilter(FSMFillForm.fill_gender))
async def warning_gender_press(message: Message):
    """
    Срабатывает, если НЕКОРРЕКТНО введен пол
    :type message: Message
    """
    await message.answer(text='\n\n'.join([LEXICON_MESSAGES['fill_gender_error'],LEXICON_MESSAGES['cancel']]))


@router.message(StateFilter(FSMFillForm.fill_email),
            F.text.contains('@'))
async def process_email_sent(message: Message, state: FSMContext):
    """
    Срабатывает, если КОРРЕКТНО введен email
    Сохраняет введенное значение
    Выводит запрос на фото
    Устанавливает состояние upload_photo
    :type message: Message
    :type state: FSMContext
    """
    await state.update_data(email=message.text)
    await message.answer(text='\n\n'.join([LEXICON_MESSAGES['fill_thank'],LEXICON_MESSAGES['fill_photo']]),
                         reply_markup=None)
    await state.set_state(FSMFillForm.upload_photo)


@router.message(StateFilter(FSMFillForm.fill_email))
async def warning_email_sent(message: Message):
    """
    Срабатывает, если НЕКОРРЕКТНО введено email
    :type message: Message
    """
    await message.answer(
        text='\n\n'.join([LEXICON_MESSAGES['fill_email_error'],LEXICON_MESSAGES['cancel']]))

@router.message(StateFilter(FSMFillForm.upload_photo), F.photo[-1].as_('largest_photo'))
async def process_photo_sent(message: Message,
                             state: FSMContext,
                             largest_photo: PhotoSize):
    """
    Срабатывает, если КОРРЕКТНО отправлено фото
    Сохраняет фото на диске
    Сохраняет введенное значение в State
    СОХРАНЯЕТ ВСЕ ДАННЫЕ В БД
    Выводит сообщение с благодарностью
    Выводит сообщение с результатами заполнения анкеты
    :type message: Message
    :type state: FSMContext
    """
    # сохраняем фото на диске
    my_config = load_config()
    file_info = await state.bot.get_file(message.photo[-1].file_id)
    filename, file_extension = splitext(file_info.file_path)
    saved_filename = message.photo[-1].file_unique_id + file_extension
    with open(my_config.photo_folder.folder + saved_filename, mode='wb') as f:
        d = await state.bot.download(file=file_info, destination=f)

    await state.update_data(photo=saved_filename)

    await message.answer(text='\n\n'.join([LEXICON_MESSAGES['final'], LEXICON_MESSAGES['show_data']]))
    data = await state.get_data()
    await save_profile({'name':data['name'],'age':int(data['age']),'gender':data['gender'],'email':data['email'],'photo':data['photo']})
    await message.answer_photo(
            photo=largest_photo.file_id,
            caption=LEXICON_MESSAGES['data'] % (data['name'], data['age'], LEXICON_KEYBOARD_GENDER[data['gender']], data['email']))
    # Устанавливаем дефолтное состояние
    await state.clear()


@router.message(StateFilter(FSMFillForm.upload_photo))
async def warning_not_photo(message: Message):
    """
    Срабатывает, если НЕКОРРЕКТНО отправлено фото
    :type message: Message
    """
    await message.answer(text='\n\n'.join([LEXICON_MESSAGES['fill_photo_error'], LEXICON_MESSAGES['cancel']]))

@router.message()
async def send_default(message: Message):
    """
    Срабатывает на любые сообщения пользователя, не предусмотренные логикой работы бота
    :type message: Message
    """
    await message.answer(LEXICON_MESSAGES["default"])
