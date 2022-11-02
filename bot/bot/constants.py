import os

from dotenv import load_dotenv
from pathlib import Path

load_dotenv(dotenv_path=Path(".env"))  # Переменные (пароли, ИД) из файла .env


ADMINS = os.environ.get("ADMINS").split(",")
BOT_API_KEY = os.environ.get("BOT_API_KEY")

SHOW_FREE = "Показать свободных"
SHOW_ALL = "Показать всех"

ADD_GIRL = "Добавить девушку"
DELETE_GIRL = "Удалить девушку"
ADD_ADMIN = "Добавить администратора"

BUSY = "Занята"
FREE = "Свободная"

ACCOUNT_TYPE_ADMIN = 1
ACCOUNT_TYPE_GIRL = 2

# При указании * чтобы передавались только эти переменные
__all__ = (
    "ADMINS",
    "BOT_API_KEY",
    "SHOW_FREE",
    "SHOW_ALL",
    "ADD_GIRL",
    "DELETE_GIRL",
    "ADD_ADMIN",
    "BUSY",
    "FREE",
    "ACCOUNT_TYPE_ADMIN",
    "ACCOUNT_TYPE_GIRL",
)
