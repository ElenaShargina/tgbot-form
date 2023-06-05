import asyncio
import sqlalchemy as sa
from sqlalchemy import MetaData, select, Column, Text, create_engine, insert, Integer
from sqlalchemy.dialects import sqlite
from sqlalchemy.orm import DeclarativeBase, Session


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer(), primary_key=True)
    name = Column(sqlite.TEXT)
    age = Column(sqlite.INTEGER)
    gender = Column(sqlite.TEXT)
    photo = Column(sqlite.TEXT)


# Создаем БД, если нужно
engine = create_engine('sqlite:///database/users.db', echo=True)
my_metadata = MetaData()
# Проверка, существует ли таблица, создаем ее, если надо
inspector = sa.inspect(engine)
if not inspector.has_table('user'):
    # Если таблицы не существует, создадим её
    Base.metadata.create_all(engine)


async def save_user(data: dict) -> None:
    """
    Сохраняет данные анкеты в БД
    :param data: словарь с полями name, age, gender, photo
    :type data: dict
    """
    with Session(engine) as session:
        new_user = User(name=data['name'],
                        age=data['age'],
                        gender=data['gender'],
                        photo=data['photo'])
        session.add(new_user)
        session.commit()


async def show_users() -> list[dict]:
    """
    Возвращает список заполненных анкет из БД
    :return: список словарей вида [{'name':'Tom', 'age':37, 'gender':'male', 'photo':'smth.jpg'},{},...]
    :rtype: list[dict]
    """
    result = []
    with Session(engine) as session:
        all = select(User)
        for user in session.scalars(all):
            result.append(user.__dict__)
    return result
