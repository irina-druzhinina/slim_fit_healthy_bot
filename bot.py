from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from config import BOT_TOKEN
import handlers

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Регистрация обработчиков команд
handlers.setup(dp)

# Запуск бота
if __name__ == '__main__':
    print("Bot is running...")
    dp.run_polling(bot)