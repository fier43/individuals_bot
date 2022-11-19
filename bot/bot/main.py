#  + форма для создание анкет
#  + Понять где хранить анкеты девушек
#  - Создать дерево и цепочку действией
#  + Найти информацию как реализовать прова администратора
#  + Администратору добавить клавиши такие как:
# + (Добавить девушку)
# - (Удалить девушку)
# + (Показать всех)
# - добавить режими (админ, модератор, пользователь)
# - добавить кнопку для добавление (админа, модератора)
# - модератор меняет только свой статус

# - добавить кнопку добавить админа
# - при заполнении анкеты добавить сталбец с ID
# пользователем для определение его модератором
# - когда создаётся анкета на девушку данные отправятся
# в две таблицы одновременно таблица прав пользователя и таблица девушек
# - text_mention - ссылка на пользователя без username

# TODO: К изучению.
# * [x] env - переменные окружения (особенно для python)
# ? [ ] git - система контроля версий для сохранения и избежания потери файлов
# ? [ ] docker - система контейнеров для запуска любых приложений в том числе бота
# ? [ ] SQLAlchemy - библиотека для работы с базами данных
# ? [ ] mysql/mariadb - база данных
# ? [ ] postgresql - база данных

import re

from telebot import types, TeleBot
from telebot.custom_filters import StateFilter

# Статические (неизменяемые) переменные из файла constants.py
from .constants import *
from .db import *
from .filters import IsInAdminList
from time import sleep
import requests
import urllib.request

bot = TeleBot(BOT_API_KEY)

# Кастомные фильтры сообщений.
bot.add_custom_filter(StateFilter(bot))  # Состояния в сообщенях.
bot.add_custom_filter(IsInAdminList())  # Сообщения для админов.


# Добавление данных
# cur.execute("INSERT INTO articles VALUES ('Лера', 'Жаравина', 25, 'Свободна')")

# Удаление данных
# cur.execute("DELETE FROM articles WHERE Name = 'Лера'")

# Изменение данных
# cur.execute("UPDATE articles SET avtor = 'Admin', views = 1 WHERE title = 'Amazon is cool!'")

# Выборка данных
# cur.execute("SELECT rowid, * FROM articles WHERE rowid < 5 ORDER BY views")
# items = cur.fetchall()
# print(items)
# print(cur.fetchmany(1))
# print(cur.fetchone()[1])

# for el in items:
#     print(el[1] + "\n" + el[4])


@bot.message_handler(commands=["myid"], admins=ADMINS)  # Обработка команды для ID
def button_id(message):
    bot.send_message(message.chat.id, "{id}".format(id=message.chat.id))


# Обработка команды для старта
@bot.message_handler(commands=["go", "start"], admins=ADMINS)
def welcome(message):
    res = cur.execute("SELECT id, telegram_id, first_name, account_type FROM user")

    girls = res.fetchall()

    for girl in girls:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

        if girl[1] == message.from_user.id and girl[3] == ACCOUNT_TYPE_ADMIN:
            markup.add(
                types.KeyboardButton(ADD_ADMIN),
                types.KeyboardButton(ADD_GIRL),
                types.KeyboardButton(DELETE_GIRL),
                types.KeyboardButton(SHOW_ALL),
            )

            bot.send_message(
                message.chat.id,
                "<i>Добро пожаловать, {0.first_name}!\n\nты зашёл как Администратор.\n\n</i>".format(
                    message.from_user, bot.get_me()
                ),
                parse_mode="html",
                reply_markup=markup,
            )
            print("---\nAdmin\n" + str(message.from_user.id))
            break

        elif girl[1] == message.from_user.id and girl[3] == ACCOUNT_TYPE_GIRL:
            markup.add(
                types.KeyboardButton(BUSY),
                types.KeyboardButton(FREE),
            )

            bot.send_message(
                message.chat.id,
                "<i>Добро пожаловать, {2}!\n\nПоработаем?).\n\n</i>".format(*girl),
                parse_mode="html",
                reply_markup=markup,
            )
            print("---\nGirl\n" + str(message.from_user.id))
            break

    if girl[1] != message.from_user.id:
        user = "{username}, {id}".format(
            message=message.text,
            first=message.from_user.first_name,
            last=message.from_user.last_name,
            username=message.from_user.username,
            id=message.chat.id,
        )
        print("---\nUser\n" + user)
        # Вставляем картинку
        sti = open("media/girl_photo.png", "rb")
        bot.send_sticker(message.chat.id, sti)

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

        markup.add(
            types.KeyboardButton(SHOW_ALL),
            types.KeyboardButton(SHOW_FREE),
            types.KeyboardButton("О нас"),
        )

        bot.send_message(
            message.chat.id,
            "<i>Добро пожаловать, {0.first_name}!\n\nЯ - <b>{1.first_name}</b>, бот который поможет вам, "
            "определится с выбором, "
            "найти ту самую и сразу написать ей, "
            "договорится о услугах или же просто посмотреть кто работает.\n\n</i>".format(
                message.from_user, bot.get_me()
            ),
            parse_mode="html",
            reply_markup=markup,
        )


# @bot.message_handler(content_types=["photo"])
# def handle_docs_audio(message):
#     photo_id = message.photo.file_id
#     file_info = bot.get_file(photo_id)
#     urllib.request.urlretrieve(
#         f"http://api.telegram.org/file/bot{config.token}/{file_info.file_path}",
#         file_info.file_path,
#     )


# @bot.message_handler(func=lambda msg: msg.text == "photo")
# def photo_output(message):
#     file = open("media/girl_photo.png", "rb")
#     bot.send_photo(message.chat.id, file)


@bot.message_handler(func=lambda msg: msg.text == ADD_ADMIN, admins=ADMINS)
def add_admin_button_handler(message):
    bot.set_state(message.from_user.id, "enter_id_admin")

    bot.send_message(message.from_user.id, "Напиши ID администратора")


@bot.message_handler(state="enter_id_admin", admins=ADMINS)
def admin_name_handler(message):
    if re.match(r"^\d+$", message.text):
        # Предварительное сохранение возраста.
        bot.add_data(message.from_user.id, admin_id=int(message.text))

        data = {}

        bot.set_state(message.from_user.id, "enter_name_admin")

        bot.send_message(message.from_user.id, "Напиши Имя")
    else:
        bot.send_message(
            message.from_user.id,
            (
                "Вы ввели неверно ID.\n"
                "Повторите ввод ID целым числом.\n\n"
                "Например: 123456789"
            ),
        )
        bot.send_message(message.from_user.id, "Ввидите ID администратора")


@bot.message_handler(state="enter_name_admin", admins=ADMINS)
def girl_name_handler(message):
    # Проверка введённого имени по шаблону.
    if re.match(r"^([А-Я]{1}[а-яё]{1,23}|[A-Z]{1}[a-z]{1,23})$", message.text):
        # Предварительное сохранение имени.
        bot.add_data(message.from_user.id, admin_name=message.text)

        data = {}

        with bot.retrieve_data(message.from_user.id) as state_data:
            data.update(state_data)

        try:
            cur.execute(
                "INSERT INTO user (telegram_id, first_name, account_type) VALUES (?, ?, ?)",
                (data["admin_id"], data["admin_name"], "1"),
            )
            bot.send_message(
                message.chat.id,
                "Oкей! Администратор добавлен\n".format(message.from_user),
            )
            bot.set_state(message.from_user.id, "Will_return")

        except Exception as error:
            print(error)

            # Оповещение пользователя об ошибке.
            bot.send_message(
                message.from_user.id,
                "Произошла ошибка при добавлении.",
            )

        con.commit()
    else:
        bot.send_message(
            message.from_user.id,
            (
                "Вы ввели неверное имя.\n"
                "Повторите ввод имени с заглавной буквы.\n\n"
                "Например: Ирина"
            ),
        )
        bot.send_message(message.from_user.id, "Напиши Имя")


@bot.message_handler(func=lambda msg: msg.text == ADD_GIRL, admins=ADMINS)
def add_girl_button_handler(message):
    bot.set_state(message.from_user.id, "enter_id")

    bot.send_message(message.from_user.id, "Напиши ID пользователя")


@bot.message_handler(state="enter_id", admins=ADMINS)
def girl_id_handler(message):
    if re.match(r"^\d+$", message.text):
        # Предварительное сохранение возраста.
        bot.add_data(message.from_user.id, girl_id=int(message.text))

        data = {}

        bot.set_state(message.from_user.id, "enter_name")

        bot.send_message(message.from_user.id, "Напиши Имя")
    else:
        bot.send_message(
            message.from_user.id,
            (
                "Вы ввели неверно ID.\n"
                "Повторите ввод ID целым числом.\n\n"
                "Например: 123456789"
            ),
        )
        bot.send_message(message.from_user.id, "Ввидите ID пользователя")


@bot.message_handler(state="enter_name", admins=ADMINS)
def girl_name_handler(message):
    # Проверка введённого имени по шаблону.
    if re.match(r"^([А-Я]{1}[а-яё]{1,23}|[A-Z]{1}[a-z]{1,23})$", message.text):
        # Предварительное сохранение имени.
        bot.add_data(message.from_user.id, girl_name=message.text)

        # Переход к следующему состоянию (шагу).
        bot.set_state(message.from_user.id, "enter_age")

        bot.send_message(message.from_user.id, "А теперь ввидите возраст")
    else:
        bot.send_message(
            message.from_user.id,
            (
                "Вы ввели неверное имя.\n"
                "Повторите ввод имени с заглавной буквы.\n\n"
                "Например: Ирина"
            ),
        )
        bot.send_message(message.from_user.id, "Напиши Имя")


@bot.message_handler(state="enter_age", admins=ADMINS)
def girl_age_handler(message):
    # Проверка введённого возраста по шаблону.
    if re.match(r"^\d+$", message.text):
        # Предварительное сохранение возраста.
        bot.add_data(message.from_user.id, girl_age=int(message.text))

        data = {}

        with bot.retrieve_data(message.from_user.id) as state_data:
            data.update(state_data)

        try:
            cur.execute(
                "INSERT INTO girls (telegram_id, first_name, age, status) VALUES (?, ?, ?, ?)",
                (data["girl_id"], data["girl_name"], data["girl_age"], "Свободна"),
            )

            # Вставляем картинку
            sti1 = open("media/pngegg.png", "rb")
            bot.send_sticker(message.chat.id, sti1)

            bot.set_state(message.from_user.id, "Will_return")

        except Exception as error:
            print(error)

            # Оповещение пользователя об ошибке.
            bot.send_message(
                message.from_user.id,
                "Произошла ошибка при добавлении.",
            )

        con.commit()

        try:
            cur.execute(
                "INSERT INTO user (telegram_id, first_name, account_type) VALUES (?, ?, ?)",
                (data["girl_id"], data["girl_name"], "2"),
            )
            bot.send_message(
                message.chat.id,
                "Oкей! Девушка добавлен\n".format(message.from_user),
            )
            bot.set_state(message.from_user.id, "Will_return")

        except Exception as error:
            print(error)

            # Оповещение пользователя об ошибке.
            bot.send_message(
                message.from_user.id,
                "Произошла ошибка при добавлении.",
            )

        con.commit()

    else:
        bot.send_message(
            message.from_user.id,
            (
                "Вы ввели неверно возраст.\n"
                "Повторите ввод возраста целым числом.\n\n"
                "Например: 26"
            ),
        )
        bot.send_message(message.from_user.id, "Ввидите возраст")


@bot.message_handler(func=lambda msg: msg.text == SHOW_ALL, admins=ADMINS)
def add_girl_button_handler(message):
    bot.set_state(message.from_user.id, "show_all")

    res = cur.execute("SELECT telegram_id, first_name, age, status FROM girls")

    girls = res.fetchall()

    for girl in girls:
        bot.send_message(
            message.from_user.id,
            "ID: {0}\nИмя: {1}\nВозраст: {2}\nСтатус: {3}".format(*girl),
        )


@bot.message_handler(func=lambda msg: msg.text == SHOW_FREE, admins=ADMINS)
def add_girl_button_handler(message):
    bot.set_state(message.from_user.id, "show_free")

    res = cur.execute("SELECT telegram_id, first_name, age, status FROM girls")

    girls = res.fetchall()

    for girl in girls:
        if girl[3] == "Свободна":
            bot.send_message(
                message.from_user.id,
                "ID: {0}\nИмя: {1}\nВозраст: {2}\nСтатус: {3}".format(*girl),
            )


@bot.message_handler(func=lambda msg: msg.text == DELETE_GIRL, admins=ADMINS)
def delete_girl_button_handler(message):
    bot.set_state(message.from_user.id, "delete_enter_name")

    bot.send_message(message.from_user.id, "Напиши Имя кого хочешь удалить")


@bot.message_handler(state="delete_enter_name", admins=ADMINS)
def delete_girl_handler(message):
    # Проверка введённого имени по шаблону.
    if re.match(r"^([А-Я]{1}[а-яё]{1,23}|[A-Z]{1}[a-z]{1,23})$", message.text):
        # Предварительное сохранение имени.
        bot.add_data(message.from_user.id, delete_girl_name=message.text)

        # Переход к следующему состоянию (шагу).
        # bot.set_state(message.from_user.id, "delete_girl")

        print("Происходит удаление")
        data = {}

        with bot.retrieve_data(message.from_user.id) as state_data:
            data.update(state_data)

        try:
            # Удаление девушки из таблицы girls
            cur.execute(
                "DELETE FROM user WHERE first_name = (?)",
                (data["delete_girl_name"],),
            )

            sti2 = open("media/pngegg.png", "rb")
            bot.send_sticker(message.chat.id, sti2)

            bot.set_state(message.from_user.id, "Will_return")

        except Exception as error:
            print(error)

            # Оповещение пользователя об ошибке.
            bot.send_message(
                message.from_user.id,
                "Произошла ошибка при удалении.",
            )

        con.commit()

        try:
            # Удаление девушки из таблицы user
            cur.execute(
                "DELETE FROM girls WHERE first_name = (?)",
                (data["delete_girl_name"],),
            )

            bot.send_message(
                message.chat.id,
                "Oкей, девушка удалена\n".format(message.from_user),
            )
            bot.set_state(message.from_user.id, "Will_return")

        except Exception as error:
            print(error)

            # Оповещение пользователя об ошибке.
            bot.send_message(
                message.from_user.id,
                "Произошла ошибка при удалении.",
            )

        con.commit()

    else:
        bot.send_message(
            message.from_user.id,
            (
                "Вы ввели неверное имя.\n"
                "Повторите ввод имени с заглавной буквы.\n\n"
                "Например: Ирина"
            ),
        )
        bot.send_message(message.from_user.id, "Напиши Имя")


@bot.message_handler(func=lambda msg: msg.text == BUSY, admins=ADMINS)
def chenge_status_busy(message):

    try:
        # изменяем статус
        girls_id = "{id}".format(id=message.chat.id)
        cur.execute(
            "UPDATE girls SET status = 'Занята' WHERE telegram_id = (?)",
            [girls_id],
        )

        # cur.execute(
        #     "INSERT INTO girls (first_name, age, status) VALUES (?, ?, ?)",
        #     (data["girl_name"], data["girl_age"], "Свободна"),
        # )
        bot.send_message(
            message.chat.id,
            "Удачной работы!)\n".format(message.from_user),
        )
        bot.set_state(message.from_user.id, "Will_return")

    except Exception as error:
        print(error)

        # Оповещение пользователя об ошибке.
        bot.send_message(
            message.from_user.id,
            "Произошла ошибка.",
        )

    con.commit()


@bot.message_handler(func=lambda msg: msg.text == FREE, admins=ADMINS)
def chenge_status_free(message):

    try:
        # изменяем статус
        girls_id = "{id}".format(id=message.chat.id)
        cur.execute(
            "UPDATE girls SET status = 'Свободна' WHERE telegram_id = (?)",
            [girls_id],
        )

        # cur.execute(
        #     "INSERT INTO girls (first_name, age, status) VALUES (?, ?, ?)",
        #     (data["girl_name"], data["girl_age"], "Свободна"),
        # )
        bot.send_message(
            message.chat.id,
            "Статус изменён\n".format(message.from_user),
        )
        bot.set_state(message.from_user.id, "Will_return")

    except Exception as error:
        print(error)

        # Оповещение пользователя об ошибке.
        bot.send_message(
            message.from_user.id,
            "Произошла ошибка.",
        )

    con.commit()


def start():
    while True:
        try:
            bot.polling(none_stop=True, interval=0)
        except requests.exceptions.ConnectionError as _ex:
            print(_ex)
            sleep(15)


# RUN
if __name__ == "__main__":
    try:
        start()
        # bot.polling(none_stop=True)
    except ConnectionError as e:
        print("Ошибка соединения: ", e)
    except Exception as r:
        print("Непридвиденная ошибка: ", r)
    finally:
        print("Здесь всё закончилось")
