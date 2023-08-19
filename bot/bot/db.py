import sqlite3

from pathlib import Path

# Подключение к базе данных.
try:
    con = sqlite3.connect(Path("records.db"), check_same_thread=False)
except sqlite3.Error as error:
    print("Ошибка при подключении к sqlite", error)


# Create Cursor
cur = con.cursor()

# Создание таблицы
try:
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS admins
        (
            telegram_id     INTEGER,
            first_name      TEXT,
            account_type	INTEGER NOT NULL
        );
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS girls
        (
            data	        INTEGER NOT NULL,
            time	        INTEGER NOT NULL,
            phone	        INTEGER,
            name	        TEXT NOT NULL,
            comment	        TEXT
        );
        """
    )
except sqlite3.Error as error:
    print("Ошибка при создании таблицы в базе данных", error)

    con.close()

    exit(1)


__all__ = [
    "cur",
    "con",
]
