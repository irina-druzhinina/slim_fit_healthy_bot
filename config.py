import os
from dotenv import load_dotenv

load_dotenv()  # Загружаем переменные окружения из файла .env

# Токен Telegram бота
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Ключ API OpenWeatherMap
OPENWEATHERMAP_API_KEY = os.getenv("OPENWEATHERMAP_API_KEY")

# Данные пользователя
USERS_DATA = {} 