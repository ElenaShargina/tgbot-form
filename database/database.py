# Создаем шаблон заполнения словаря с пользователями
from datetime import datetime
def get_today():
    return datetime.now().strftime("%Y-%m-%d")


user_dict_template: dict = {'water': {get_today():0} }

# Инициализируем "базу данных"
users_db: dict = {}