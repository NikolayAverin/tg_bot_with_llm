import logging
import os

from dotenv import load_dotenv
from telegram.ext import CommandHandler, Filters, MessageHandler, Updater

from database import BASE_DIR, create_database
from tg_bot import handle_message, start

load_dotenv(BASE_DIR / ".env")

TG_BOT_API_KEY = os.getenv("TG_BOT_API_KEY")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)


def main():
    """Основная функция работы приложения."""
    create_database()  # Создаем таблицы при каждом запуске
    updater = Updater(TG_BOT_API_KEY, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
