# Мой Telegram-бот
Проект представляет собой Telegram-бота, который помогает пользователям отслеживать питание, физическую активность и потребление воды. 

## Описание установки.

Требования:
- Python версии 3.11

Библиотеки: 
- aiogram == 3.*
- aiohttp
- python-dotenv
- pydantic-settings
- requests == 2.32.5
- pandas>=2.2,<2.4
- matplotlib==3.7.2
- seaborn==0.12.2
- plotly==5.17.0
- numpy==1.25.*

## Локальный запуск
1. Скачать или клонировать репозиторий:

2. Установить зависимости:
pip install -r requirements.txt

3. Создать файл .env и заполнить его токеном Telegram-бота и  API ключом для OpenWeatherMap:
```text
BOT_TOKEN=<your_bot_token_here>
ENWEATHERMAP_API_KEY = <your_api_key>
```
4. Запустить бота:
python app.py
