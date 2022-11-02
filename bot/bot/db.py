import sqlite3

from pathlib import Path

# Подключение к базе данных.
try:
    con = sqlite3.connect(Path("individual.db"), check_same_thread=False)
except sqlite3.Error as error:
    print("Ошибка при подключении к sqlite", error)


# Create Cursor
cur = con.cursor()

# Создание таблицы
try:
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS girls
        (
            telegram_id INTEGER,
            first_name TEXT,
            age INTEGER,
            status TEXT
        );
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS user (
            id	            INTEGER,
            telegram_id	    INTEGER NOT NULL,
            first_name	    TEXT NOT NULL,
            account_type	INTEGER NOT NULL,
            PRIMARY KEY("id" AUTOINCREMENT)
        );
        """
    )
except sqlite3.Error as error:
    print("Ошибка при создании таблицы в базе данных", error)

    con.close()

    exit(1)


__all__ = ["cur"]
