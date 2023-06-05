import asyncio
import sqlalchemy as sa
from sqlalchemy import MetaData, select, Column, Text, create_engine, insert, Integer, ForeignKey
from sqlalchemy.dialects import sqlite
from sqlalchemy.orm import DeclarativeBase, Session, Mapped, mapped_column, relationship


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

# Создаем БД, если нужно
engine = create_engine('sqlite:///database/db.db', echo=True)
my_metadata = MetaData()
# Проверка, существует ли таблица, создаем ее, если надо
inspector = sa.inspect(engine)
if not inspector.has_table('profile'):
    # Если таблицы не существует, создадим её
    Base.metadata.create_all(engine)


async def save_profile(data: dict) -> None:
    """
    Сохраняет данные анкеты в БД
    :param data: словарь с полями name, age, gender, photo, email
    :type data: dict
    """
    with Session(engine) as session:
        new_profile = Profile(name = data['name'],
                             age = data['age'],
                             gender = data['gender'],
                             photo = data['photo'],
                             email = data['email'])
        session.add(new_profile)
        session.commit()


async def show_profiles() -> list[dict]:
    """
    Возвращает список заполненных анкет из БД
    :return: список словарей вида [{'name':'Tom', 'age':37, 'gender':'male', 'photo':'smth.jpg', 'email':'mail@nhg.ru'},{},...]
    :rtype: list[dict]
    """
    result = []
    with Session(engine) as session:
        all = select(Profile)
        for profile in session.scalars(all):
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

async def update_profile_as_checked(id):
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
        result = current_profile.__dict__
        session.commit()
    return result