from dataclasses import dataclass
from environs import Env


@dataclass
class TgBot:
    token: str            # Токен для доступа к телеграм-боту

@dataclass
class PhotoFolder:
    folder: str            # папка для хранения загруженных пользователями фото

@dataclass
class Config:
    tg_bot: TgBot
    photo_folder: PhotoFolder


def load_config(path: str | None = None) -> Config:
    """
    Читает файл .env и возвращает экземпляр класса Config с заполненными полями token
    :param path: путь до файла .env
    :type path: str
    :return: экземпляр Config
    :rtype: Config
    """
    env = Env()
    env.read_env(path)
    return Config(tg_bot=TgBot(env('BOT_TOKEN')),
                photo_folder=PhotoFolder('database/photos/')
                )