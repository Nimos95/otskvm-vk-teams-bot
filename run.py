# run.py - точка входа (находится в корне проекта)

import sys
import os

# Добавляем текущую папку в путь для импортов
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Импортируем и запускаем бота
from src.bot import create_bot

if __name__ == "__main__":
    print("🚀 Запуск бота...")
    
    bot, module_manager = create_bot()
    
    print(f"✅ Бот запущен")
    print(f"📦 Модули: {', '.join(module_manager.modules.keys())}")
    
    try:
        bot.start_polling()
        bot.idle()
    except KeyboardInterrupt:
        print("\n👋 Бот остановлен")
    except Exception as e:
        print(f"❌ Ошибка: {e}")