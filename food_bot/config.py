import os

from dotenv import load_dotenv

# Суперподробное логирование для отладки
import logging
logging.basicConfig(level=logging.DEBUG)

aiohttp_logger = logging.getLogger("aiohttp")
aiohttp_logger.setLevel(logging.DEBUG)

# Загрузка переменных из .env файла
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

if not BOT_TOKEN or not OPENWEATHER_API_KEY:
    raise NameError