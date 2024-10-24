import os

from dotenv import load_dotenv
from gigachat import GigaChat
from telegram import Update
from telegram.ext import CallbackContext

from database import BASE_DIR, db_connect

load_dotenv(BASE_DIR / ".env")

GIGACHAT_API_KEY = os.getenv("GIGACHAT_API_KEY")


def chat_with_gigachat(message_text):
    """Функция для отправки сообщения в gigachat"""
    with GigaChat(credentials=GIGACHAT_API_KEY, verify_ssl_certs=False) as giga:
        response = giga.chat(message_text)
        return response.choices[0].message.content


def start(update: Update, context: CallbackContext):
    """Команда старта."""
    update.message.reply_text(
        "Привет. Я твой самый умный бот! Можешь задавать мне любые вопросы, например "
        "'Кто с тобой общается?', 'Сколько у тебя пользователей?', "
        "'О чем мы говорили вчера?', 'Какие вопросы тебе чаще всего задают?', "
        "'Покажи все мои вопросы' или другой, интересующий тебя вопрос!"
    )


def get_usernames(update: Update, context: CallbackContext):
    """Команда для получения имен пользователей."""
    with db_connect() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT username FROM users")
        users = cursor.fetchall()
        cursor.close()
    users_list = ", ".join([user[0] for user in users])
    update.message.reply_text(f"Пользователи, которые общались со мной: {users_list}")


def get_users_count(update: Update, context: CallbackContext):
    """Команда для получения количества пользователей."""
    with db_connect() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users")
        users_count = cursor.fetchall()[0][0]
        cursor.close()
    update.message.reply_text(
        f"Количество пользователей, общающихся со мной: {users_count}"
    )


def get_yesterday_messages(update: Update, context: CallbackContext):
    """Команда для получения вчерашних сообщений."""
    user_name = update.message.from_user.username
    with db_connect() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE username = %s;", (user_name,))
        user_id = cursor.fetchone()
        if not user_id:
            update.message.reply_text("Кто вы такой???")
        else:
            cursor.execute(
                "SELECT * FROM messages WHERE timestamp >= CURRENT_DATE - INTERVAL '1 day' AND timestamp < CURRENT_DATE AND user_id = %s;",
                (user_id,),
            )
            messages = cursor.fetchall()
        cursor.close()
    if messages:
        update.message.reply_text(
            "Сообщения за вчера:\n" + "\n".join([msg[2] for msg in messages])
        )
    else:
        update.message.reply_text("Мы вчера не общались...")


def get_history(update: Update, context: CallbackContext):
    """Команда для получения всех сообщений пользователя."""
    user_name = update.message.from_user.username
    with db_connect() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE username = %s;", (user_name,))
        user_id = cursor.fetchone()
        if not user_id:
            update.message.reply_text("Кто вы такой???")
        else:
            cursor.execute("SELECT * FROM messages WHERE user_id = %s;", (user_id,))
            messages = cursor.fetchall()
        cursor.close()
    if messages:
        update.message.reply_text(
            "Вот все ваши запросы:\n" + "\n".join([msg[2] for msg in messages])
        )
    else:
        update.message.reply_text("Мы только начинаем нашу беседу...")


def get_popular_questions(update: Update, context: CallbackContext):
    """Команда для получения пяти популярных запросов от пользователей."""
    with db_connect() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT message FROM messages GROUP BY message ORDER BY COUNT(*) DESC LIMIT 5"
        )
        popular_questions = cursor.fetchall()
        cursor.close()
    popular_questions_list = "\n".join([question[0] for question in popular_questions])
    update.message.reply_text(
        f"Вот пять наиболее задаваемых вопросов:\n{popular_questions_list}"
    )


def handle_message(update: Update, context: CallbackContext):
    """Обработчик сообщений."""
    user_name = update.message.from_user.username
    user_message = update.message.text

    with db_connect() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (username) VALUES (%s) ON CONFLICT (username) DO NOTHING",
            (user_name,),
        )
        cursor.execute("SELECT id FROM users WHERE username = %s", (user_name,))
        user_id = cursor.fetchone()[0]
        cursor.execute(
            "INSERT INTO messages (user_id, message) VALUES (%s, %s)",
            (user_id, user_message.lower()),
        )
        conn.commit()

    if "кто с тобой общается" in update.message.text.lower():
        get_usernames(update, context)
    elif "сколько у тебя пользователей" in update.message.text.lower():
        get_users_count(update, context)
    elif "о чем мы говорили вчера" in update.message.text.lower():
        get_yesterday_messages(update, context)
    elif "покажи все мои вопросы" in update.message.text.lower():
        get_history(update, context)
    elif "какие вопросы тебе чаще всего задают" in update.message.text.lower():
        get_popular_questions(update, context)
    else:
        bot_reply = chat_with_gigachat(user_message)
        update.message.reply_text(bot_reply)
