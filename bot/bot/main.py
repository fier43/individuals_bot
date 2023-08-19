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
from bot.constants import *
from bot.db import *
from bot.filters import IsInAdminList
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
    res = cur.execute("SELECT telegram_id, first_name, account_type FROM admins")

    admins = res.fetchall()

    for admin in admins:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

        if admin[0] == message.from_user.id and admin[2] == ACCOUNT_TYPE_ADMIN:
            markup.add(
                types.KeyboardButton(ADD_ADMIN),
                types.KeyboardButton(ADD_GIRL),
                types.KeyboardButton(DELETE_GIRL),
                types.KeyboardButton(SHOW_ALL),
            )

            bot.send_message(
                message.chat.id,
                "<i>Добро пожаловать, {0.first_name}!\n\nкакие планы?).\n\n</i>".format(
                    message.from_user, bot.get_me()
                ),
                parse_mode="html",
                reply_markup=markup,
            )
            print("---\nAdmin\n" + str(message.from_user.id))
            break

        elif admin[0] == message.from_user.id and admin[2] == ACCOUNT_TYPE_GIRL:
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

    if admin[0] != message.from_user.id:
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
            types.KeyboardButton(SHOW_FREE),
            types.KeyboardButton(ABOUT_MY),
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


@bot.message_handler(func=lambda msg: msg.text == "photo")
def photo_output(message):
    file = open("media/girl_photo.png", "rb")
    bot.send_photo(message.chat.id, file)


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
                "INSERT INTO admins (telegram_id, first_name, account_type) VALUES (?, ?, ?)",
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
    bot.set_state(message.from_user.id, "enter_data")

    bot.send_message(message.from_user.id, "На какое число будем записывать?")


@bot.message_handler(state="enter_data", admins=ADMINS)
def girl_id_handler(message):
    if re.match(r"\d\d.\d\d", message.text):
        # Предварительное сохранение ID.
        bot.add_data(message.from_user.id, data=message.text)

        bot.set_state(message.from_user.id, "enter_time")

        bot.send_message(message.from_user.id, "Введите время записи.\nНапример 13:00")
    else:
        bot.send_message(
            message.from_user.id,
            (
                "Вы ввели неверно дату.\n"
                "Повторите ввод даты целым числом.\n\n"
                "Например: 22.12"
            ),
        )
        bot.send_message(message.from_user.id, "Ввидите дату записи")


@bot.message_handler(state="enter_time", admins=ADMINS)
def girl_name_handler(message):
    # Проверка введённого имени по шаблону.
    if re.match(r"\d\d.\d\d", message.text):
        # Предварительное сохранение имени.
        bot.add_data(message.from_user.id, time=message.text)

        # Переход к следующему состоянию (шагу).
        bot.set_state(message.from_user.id, "enter_phone")

        bot.send_message(message.from_user.id, "Какое средство связи?")
    else:
        bot.send_message(
            message.from_user.id,
            (
                "Вы ввели неверное время.\n"
                "Повторите ввод времени.\n\n"
                "Например: 09:00"
            ),
        )
        bot.send_message(message.from_user.id, "Напиши время")


@bot.message_handler(state="enter_phone", admins=ADMINS)
def girl_name_handler(message):

    # Предварительное сохранение имени.
    bot.add_data(message.from_user.id, phone=message.text)

    # Переход к следующему состоянию (шагу).
    bot.set_state(message.from_user.id, "enter_name")

    bot.send_message(message.from_user.id, "А теперь ввидите Имя с Фамилией")


# ^([А-Я]{1}[а-яё]{1,23}|[A-Z]{1}[a-z]{1,23})$


@bot.message_handler(state="enter_name", admins=ADMINS)
def girl_name_handler(message):

    # Проверка введённого имени по шаблону.
    if re.match(
        r"^([А-Я]{1}[а-яё]{1,23}|[A-Z]{1}[a-z]{1,23}).([А-Я]{1}[а-яё]{1,23}|[A-Z]{1}[a-z]{1,23})$",
        message.text,
    ):

        # Предварительное сохранение имени.
        bot.add_data(message.from_user.id, name=message.text)

        # Переход к следующему состоянию (шагу).
        bot.set_state(message.from_user.id, "enter_comment")

        bot.send_message(message.from_user.id, "Оставьте комментарий")

    else:
        bot.send_message(
            message.from_user.id,
            (
                "Вы ввели неверное Имя с Фамилией.\n"
                "Повторите ввод имени и фамилии с заглавной буквы.\n\n"
                "Например: Кристина Еременкина"
            ),
        )
        bot.send_message(message.from_user.id, "Напишите ещё раз")


@bot.message_handler(state="enter_comment", admins=ADMINS)
def girl_age_handler(message):

    # Предварительное сохранение возраста.
    bot.add_data(message.from_user.id, comment=message.text)

    data = {}

    with bot.retrieve_data(message.from_user.id) as state_data:
        data.update(state_data)

    try:
        cur.execute(
            "INSERT INTO girls (data, time, phone, name, comment) VALUES (?, ?, ?, ?, ?)",
            (data["data"], data["time"], data["phone"], data["name"], data["comment"]),
        )

        bot.set_state(message.from_user.id, "Will_return")

        bot.send_message(message.from_user.id, "Запись создана!")

        res = cur.execute("SELECT data, time, phone, name, comment FROM girls")

        girls = res.fetchall()

        for girl in girls:
            if girl[3] == data["name"]:
                bot.send_message(
                    message.from_user.id,
                    "Дата: {0}\nВремя: {1}\nИмя: {3}\nКомментарий: {4}".format(*girl),
                )

    except Exception as error:
        print(error)

        # Оповещение пользователя об ошибке.
        bot.send_message(
            message.from_user.id,
            "Произошла ошибка при добавлении.",
        )

    con.commit()

    # else:
    #     bot.send_message(
    #         message.from_user.id,
    #         (
    #             "Вы ввели неверно возраст.\n"
    #             "Повторите ввод возраста целым числом.\n\n"
    #             "Например: 26"
    #         ),
    #     )
    #     bot.send_message(message.from_user.id, "Ввидите возраст")


@bot.message_handler(func=lambda msg: msg.text == SHOW_ALL, admins=ADMINS)
def add_girl_button_handler(message):
    bot.set_state(message.from_user.id, "show_all")

    res = cur.execute("SELECT data, time, phone, name, comment FROM girls")

    girls = res.fetchall()

    for girl in girls:
        bot.send_message(
            message.from_user.id,
            "Дата: {0}\nВремя: {1}\nСредство связи: {2}\nИмя: {3}\nКомментарий: {4}".format(
                *girl
            ),
        )


@bot.message_handler(func=lambda msg: msg.text == SHOW_FREE, admins=ADMINS)
def add_girl_button_handler(message):
    bot.set_state(message.from_user.id, "show_free")

    res = cur.execute("SELECT telegram_id, first_name, age, status FROM girls")

    girls = res.fetchall()

    for girl in girls:
        if girl[3] == "Свободна":
            file = open("uploads/{0}.jpg".format(*girl), "rb")
            bot.send_photo(message.chat.id, file)

            bot.send_message(
                message.from_user.id,
                "ID: {0}\nИмя: {1}\nВозраст: {2}\nСтатус: {3}".format(*girl),
            )


@bot.message_handler(func=lambda msg: msg.text == DELETE_GIRL, admins=ADMINS)
def delete_girl_button_handler(message):
    bot.set_state(message.from_user.id, "delete_enter_name")

    bot.send_message(message.from_user.id, "Напиши Имя с Фамилией кого хочешь удалить")


@bot.message_handler(state="delete_enter_name", admins=ADMINS)
def delete_girl_handler(message):
    # Проверка введённого имени по шаблону.
    if re.match(
        r"^([А-Я]{1}[а-яё]{1,23}|[A-Z]{1}[a-z]{1,23}).([А-Я]{1}[а-яё]{1,23}|[A-Z]{1}[a-z]{1,23})$",
        message.text,
    ):
        # Предварительное сохранение имени.
        bot.add_data(message.from_user.id, delete_girl_name=message.text)

        # Переход к следующему состоянию (шагу).
        # bot.set_state(message.from_user.id, "delete_girl")

        print("Происходит удаление")
        data = {}

        with bot.retrieve_data(message.from_user.id) as state_data:
            data.update(state_data)

        try:
            # Удаление девушки из таблицы user
            cur.execute(
                "DELETE FROM girls WHERE name = (?)",
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
                "Вы ввели неверное имя с фамилией.\n"
                "Повторите ввод имени с фамилией заглавной буквы.\n\n"
                "Например: Ирина Кановалова"
            ),
        )
        bot.send_message(message.from_user.id, "Напиши ещё раз")


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
