# run.py

import sys
import os
import asyncio
import signal
from dotenv import load_dotenv

load_dotenv()

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.core.database import Database
from src.modules.calendar.handlers import get_event_loop


def signal_handler(signum, frame):
    """Обработчик сигналов"""
    print("\n👋 Получен сигнал остановки...")
    sys.exit(0)


def init_db_sync():
    """Синхронная инициализация БД"""
    try:
        loop = get_event_loop()
        loop.run_until_complete(Database.get_pool())
        return True
    except Exception as e:
        print(f"⚠️ База данных НЕ подключена: {e}")
        return False


def main():
    """Главная функция"""
    print("=" * 60)
    print("🚀 ЗАПУСК БОТА")
    print("=" * 60)
    
    try:
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    except:
        pass
    
    db_ok = init_db_sync()
    
    from src.bot import create_bot
    bot, module_manager = create_bot()
    
    print(f"✅ Бот успешно создан")
    print(f"📦 Загружено модулей: {len(module_manager.modules)}")
    print(f"📋 Зарегистрировано команд: {len(module_manager.commands)}")
    print(f"💾 Состояние БД: {'✅ Подключена' if db_ok else '⚠️ Не подключена'}")
    print("-" * 60)
    print("Нажмите Ctrl+C для остановки")
    print("=" * 60)
    
    try:
        bot.start_polling()
        bot.idle()
    except KeyboardInterrupt:
        print("\n👋 Бот остановлен пользователем")
    except Exception as e:
        print(f"❌ Ошибка при работе бота: {e}")
    finally:
        try:
            loop = get_event_loop()
            loop.run_until_complete(Database.close())
        except:
            pass


if __name__ == "__main__":
    main()