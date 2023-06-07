import asyncio
import logging
from copy import deepcopy
from typing import Literal

import sqlalchemy as sa
from sqlalchemy import MetaData, select, Column, Text, create_engine, insert, Integer, ForeignKey, Engine
from sqlalchemy.dialects import sqlite
from sqlalchemy.orm import DeclarativeBase, Session, Mapped, mapped_column, relationship
from config_data.config import load_config
import shutil

class Base(DeclarativeBase):
    pass


class Profile(Base):
    __tablename__ = 'profile'
    id = Column(Integer(), primary_key=True)
    name = Column(sqlite.TEXT)
    age = Column(sqlite.INTEGER)
    gender = Column(sqlite.TEXT)
    photo = Column(sqlite.TEXT)
    email = Column(sqlite.TEXT)
    checked = Column(sqlite.BOOLEAN, default=False)


def add_sample_data(engine:Engine, sample_dir: str) -> None:
    """
    Добавляет в БД тестовые данные
    :type engine: Engine
    :param sample_dir: путь до папки с тестовыми данными
    :type sample_dir: str
    """
    logging.info('ADDING TEST DATA')
    my_config = load_config()
    with open(sample_dir+'sample.txt', 'r') as f:
        profiles = []
        for line in f.readlines():
            data = line.split(';')
            # загружаем фото в общую папку для фото
            photo_filename = data[0]
            shutil.copy(sample_dir+photo_filename, my_config.photo_folder.folder+photo_filename)
            profiles.append(Profile(name=data[1],
                                  age=data[2],
                                  gender=data[3],
                                  photo=data[0],
                                  email=data[4])
                            )
        with Session(engine) as session:
            session.bulk_save_objects(profiles)
            session.commit()

async def save_profile(data: dict) -> None:
    """
    Сохраняет данные анкеты в БД
    :param data: словарь с полями name, age, gender, photo, email
    :type data: dict
    """
    with Session(engine) as session:
        new_profile = Profile(name=data['name'],
                              age=data['age'],
                              gender=data['gender'],
                              photo=data['photo'],
                              email=data['email'])
        session.add(new_profile)
        session.commit()

async def show_profiles(status: Literal['all','checked','not_checked'] = 'all') -> list[dict]:
    """
    Возвращает список заполненных анкет из БД
    :param status: 'all' - вывести все анкеты, 'checked' - только обработанные, 'not_checked' - только необработанные
    :type status: str
        defaults to 'all'
    :return: список словарей вида [{'name':'Tom', 'age':37, 'gender':'male', 'photo':'smth.jpg', 'email':'mail@nhg.ru'},{},...]
    :rtype: list[dict]
    """
    result = []
    with Session(engine) as session:
        if status == 'all':
            profiles = select(Profile)
        elif status == 'checked':
            profiles = select(Profile).where(Profile.checked == True)
        else:
            profiles = select(Profile).where(Profile.checked == False)

        for profile in session.scalars(profiles):
            result.append(profile.__dict__)
    return result


async def show_profile(id) -> dict:
    """
    Возвращает заполненную анкету из БД по заданному id
    :param id: id анкеты в БД
    :type id: str
    :return: список словарей вида [{'name':'Tom', 'age':37, 'gender':'male', 'photo':'smth.jpg'},{},...]
    :rtype: list[dict]
    """
    result = None
    with Session(engine) as session:
        one = select(Profile).where(Profile.id == int(id))
        result = session.scalar(one)
    if result:
        return result.__dict__
    else:
        return None


async def update_profile_as_checked(id) -> dict:
    """
    Помечает анкету из БД по заданному id как обработанную.
    Возвращает заполненную анкету из БД по заданному id с новым значением checked.
    :param id: id анкеты в БД
    :type id: str
    :return: словарь вида {'name':'Tom', 'age':37, 'gender':'male', 'photo':'smth.jpg'}
    :rtype: dict
    """
    result = None
    with Session(engine) as session:
        one = select(Profile).where(Profile.id == int(id))
        current_profile = session.scalar(one)
        current_profile.checked = True
        result = deepcopy(current_profile.__dict__)
        session.commit()
    return result


# Создаем БД, если нужно
engine = create_engine('sqlite:///database/db.db', echo=True)

my_metadata = MetaData()
# Проверка, существует ли таблица, создаем ее, если надо
inspector = sa.inspect(engine)

if not inspector.has_table('profile'):
    # Если таблицы не существует, создадим её
    Base.metadata.create_all(engine)
    add_sample_data(engine, 'database/sample/')

