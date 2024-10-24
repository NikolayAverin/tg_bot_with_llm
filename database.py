import os
from pathlib import Path

import psycopg2
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")


def db_connect():
    """Подключение к БД."""
    return psycopg2.connect(
        host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASSWORD
    )


def create_database():
    """Функция для создания таблиц."""
    with db_connect() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username TEXT UNIQUE
        )"""
        )
        cursor.execute(
            """CREATE TABLE IF NOT EXISTS messages (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id),
            message TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )"""
        )
        conn.commit()
