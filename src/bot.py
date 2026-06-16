# src/bot.py

import os
import sys
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.bot_wrapper import SafeBot  # Используем обёртку
from bot.handler import MessageHandler
from src.core.module_manager import ModuleManager
from src.core.chat_filter import is_private_chat, get_chat_type_name

load_dotenv()

TOKEN = os.getenv('BOT_TOKEN')

if not TOKEN:
    print("❌ Ошибка: токен не найден в файле .env")
    sys.exit(1)


def create_bot():
    """Создаёт и настраивает бота"""
    
    # Используем SafeBot вместо Bot
    bot = SafeBot(token=TOKEN)
    module_manager = ModuleManager(bot)
    
    # Загружаем модули
    module_manager.load_all_modules()
    
    # Главный обработчик сообщений
    def main_handler(bot, event):
        chat_id = event.from_chat
        message_text = event.text.strip() if event.text else ""
        
        if not message_text:
            return
        
        is_private = is_private_chat(chat_id)
        chat_type_name = get_chat_type_name(chat_id)
        
        print(f"📨 [{chat_type_name}] {chat_id}: {message_text}")
        
        if not is_private:
            print(f"⏭️ Игнорирую (общий чат)")
            return
        
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
            bot.send_text(
                chat_id=chat_id,
                text=f"🔄 Эхо: {message_text}\n\n(Напишите /help для списка команд)"
            )
    
    bot.dispatcher.add_handler(MessageHandler(callback=main_handler))
    
    return bot, module_manager