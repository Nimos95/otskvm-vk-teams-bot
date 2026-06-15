# src/bot.py

import os
import sys
from dotenv import load_dotenv

# Добавляем родительскую папку в путь для импортов
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bot.bot import Bot
from bot.handler import MessageHandler
from src.core.module_manager import ModuleManager
from src.core.chat_filter import is_private_chat, get_chat_type_name

# Загрузка переменных окружения
load_dotenv()

TOKEN = os.getenv('BOT_TOKEN')

if not TOKEN:
    print("❌ Ошибка: токен не найден в файле .env")
    sys.exit(1)

def create_bot():
    """Создаёт и настраивает бота"""
    
    # Создаём бота
    bot = Bot(token=TOKEN)
    
    # Создаём менеджер модулей
    module_manager = ModuleManager(bot)
    
    # Загружаем все модули
    module_manager.load_all_modules()
    
    # Главный обработчик сообщений
    def main_handler(bot, event):
        chat_id = event.from_chat
        message_text = event.text.strip() if event.text else ""
        
        if not message_text:
            return
        
        # Определяем тип чата
        is_private = is_private_chat(chat_id)
        chat_type_name = get_chat_type_name(chat_id)
        
        print(f"📨 [{chat_type_name}] {chat_id}: {message_text}")
        
        # В общих чатах игнорируем
        if not is_private:
            print(f"⏭️ Игнорирую (общий чат)")
            return
        
        # В личке обрабатываем команды
        if message_text.startswith('/'):
            command = message_text.split()[0].lower()
            handler_info = module_manager.get_command_handler(command)
            
            if handler_info:
                module_name, handler = handler_info
                print(f"🎯 Выполняю команду {command} из модуля {module_name}")
                handler(bot, event)
            else:
                bot.send_text(
                    chat_id=chat_id,
                    text=f"❓ Неизвестная команда `{command}`\n\nНапишите /help"
                )
        else:
            # Обычное сообщение (не команда)
            bot.send_text(
                chat_id=chat_id,
                text=f"🔄 Эхо: {message_text}\n\n(Напишите /help для списка команд)"
            )
    
    # Регистрируем обработчик
    bot.dispatcher.add_handler(MessageHandler(callback=main_handler))
    
    return bot, module_manager

if __name__ == "__main__":
    print("=" * 60)
    print("🤖 БОТ VK WORKSPACE - МОДУЛЬНАЯ ВЕРСИЯ")
    print("=" * 60)
    print("📌 Правила определения чатов:")
    print("   • Личные чаты: email пользователя (например, user@company.ru)")
    print("   • Групповые чаты: заканчиваются на @chat.agent")
    print("-" * 60)
    
    bot, module_manager = create_bot()
    
    print(f"✅ Бот успешно создан")
    print(f"📦 Загружено модулей: {len(module_manager.modules)}")
    print(f"📋 Зарегистрировано команд: {len(module_manager.commands)}")
    print("-" * 60)
    print("📌 Личные сообщения: бот отвечает на команды")
    print("📢 Общие чаты: бот полностью игнорирует")
    print("-" * 60)
    print("Нажмите Ctrl+C для остановки")
    print("=" * 60)
    
    bot.start_polling()
    bot.idle()