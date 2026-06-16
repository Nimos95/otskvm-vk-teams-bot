# run.py - точка входа (исправлено)

import sys
import os
import asyncio
import signal

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.core.database import Database


def signal_handler(signum, frame):
    """Обработчик сигналов"""
    print("\n👋 Получен сигнал остановки...")
    sys.exit(0)


def init_db_sync():
    """Синхронная инициализация БД"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(Database.get_pool())
        loop.close()
        print("✅ База данных подключена")
        return True
    except Exception as e:
        print(f"⚠️ База данных НЕ подключена: {e}")
        print("   Бот будет работать без сохранения данных")
        return False


def main():
    """Главная функция"""
    print("=" * 60)
    print("🚀 ЗАПУСК БОТА")
    print("=" * 60)
    
    # Настройка обработчиков сигналов (для корректного завершения)
    try:
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    except:
        pass
    
    # Инициализация БД
    db_ok = init_db_sync()
    
    # Импортируем create_bot
    from src.bot import create_bot
    
    # Создаём бота с использованием SafeBot
    bot, module_manager = create_bot()
    
    print(f"✅ Бот успешно создан")
    print(f"📦 Загружено модулей: {len(module_manager.modules)}")
    print(f"📋 Зарегистрировано команд: {len(module_manager.commands)}")
    print(f"💾 Состояние БД: {'✅ Подключена' if db_ok else '⚠️ Не подключена'}")
    print("-" * 60)
    print("Нажмите Ctrl+C для остановки")
    print("=" * 60)
    
    try:
        # Запускаем поллинг
        bot.start_polling()
        # Используем наш безопасный idle
        bot.idle()
    except KeyboardInterrupt:
        print("\n👋 Бот остановлен пользователем")
    except Exception as e:
        print(f"❌ Ошибка при работе бота: {e}")
    finally:
        # Закрываем соединение с БД
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(Database.close())
            loop.close()
        except:
            pass


if __name__ == "__main__":
    main()