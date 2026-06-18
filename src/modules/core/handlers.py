# src/modules/core/handlers.py

from src.core.constants import Emoji


def setup(bot, module_manager):
    """Инициализация базового модуля."""
    print("📦 Модуль 'core' загружается...")
    
    # Регистрируем команду /help (она остаётся)
    module_manager.register_command('/help', help_handler, 'core')
    
    print("✅ Модуль 'core' загружен")


def help_handler(bot, event):
    """Обработчик команды /help."""
    bot.send_text(
        chat_id=event.from_chat,
        text=f"{Emoji.HELP} <b>Справка по командам</b>\n\n"
             f"• /start — Главное меню\n"
             f"• /help — Эта справка\n\n"
             f"📌 Все функции доступны через главное меню.",
        parse_mode="HTML"
    )