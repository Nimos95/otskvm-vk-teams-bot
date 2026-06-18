# src/bot.py

import os
import sys
from dotenv import load_dotenv
from bot.bot import Bot
from bot.handler import MessageHandler, BotButtonCommandHandler
from src.core.module_manager import ModuleManager
from src.core.chat_filter import is_private_chat, get_chat_type_name
from src.core.database import Database
from src.core.bot_wrapper import SafeBot

load_dotenv()

TOKEN = os.getenv('BOT_TOKEN')

if not TOKEN:
    print("❌ Ошибка: токен не найден в файле .env")
    sys.exit(1)


def create_bot():
    """Создаёт и настраивает бота"""
    
    # Инициализация базы данных
    import asyncio
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(Database.get_pool())
        loop.close()
        print("✅ База данных подключена")
    except Exception as e:
        print(f"⚠️ База данных НЕ подключена: {e}")
    
    bot = SafeBot(token=TOKEN)  # <-- ИСПОЛЬЗУЕМ SafeBot
    module_manager = ModuleManager(bot)
    
    # Загружаем модули
    module_manager.load_all_modules()
    
    # ЕДИНСТВЕННЫЙ обработчик кнопок для всего бота
    def global_button_handler(bot, event):
        """Распределяет callback по модулям."""
        chat_id = event.from_chat
        callback_data = event.data.get('callbackData')
        
        print(f"🔍 Глобальный callback: {callback_data}")
        print(f"🔍 Доступные callback'и: {list(module_manager.callbacks.keys())}")
        
        handler_info = module_manager.get_callback_handler(callback_data)
        if handler_info:
            module_name, handler = handler_info
            print(f"🎯 Выполняю callback {callback_data} из модуля {module_name}")
            handler(bot, event)
        else:
            print(f"⚠️ Нет обработчика для callback: {callback_data}")
        
        bot.answer_callback_query(
            query_id=event.data['queryId'],
            text="✅",
            show_alert=False
        )
    
    bot.dispatcher.add_handler(BotButtonCommandHandler(callback=global_button_handler))
    
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


if __name__ == "__main__":
    print("=" * 60)
    print("🤖 БОТ VK WORKSPACE - ДЕНЬ 4")
    print("=" * 60)
    
    bot, module_manager = create_bot()
    
    print(f"✅ Бот успешно создан")
    print(f"📦 Загружено модулей: {len(module_manager.modules)}")
    print(f"📋 Зарегистрировано команд: {len(module_manager.commands)}")
    print(f"📌 Зарегистрировано callback'ов: {len(module_manager.callbacks)}")
    print("-" * 60)
    print("Нажмите Ctrl+C для остановки")
    print("=" * 60)
    
    bot.start_polling()
    bot.idle()