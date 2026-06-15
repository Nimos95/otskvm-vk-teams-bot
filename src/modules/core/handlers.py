# src/modules/core/handlers.py

"""
Базовый модуль с основными командами /start и /help
"""

def setup(bot, module_manager):
    """
    Эта функция вызывается при загрузке модуля
    bot - экземпляр бота
    module_manager - менеджер модулей для регистрации команд
    """
    print("📦 Модуль 'core' загружается...")
    
    # Регистрируем команды
    module_manager.register_command('/start', start_handler, 'core')
    module_manager.register_command('/help', help_handler, 'core')
    
    print("✅ Модуль 'core' загружен (команды: /start, /help)")

def start_handler(bot, event):
    """Обработчик команды /start"""
    bot.send_text(
        chat_id=event.from_chat,
        text="🤖 **Привет! Я бот для VK Workspace**\n\n"
             "📋 **Доступные команды:**\n"
             "• /start — приветствие\n"
             "• /help — справка\n\n"
             "⚙️ Функции будут добавляться по мере разработки:\n"
             "• 📅 Календарь (в разработке)\n"
             "• 📊 Статусы аудиторий (в разработке)"
    )

def help_handler(bot, event):
    """Обработчик команды /help"""
    # Получаем список всех команд из менеджера модулей
    from src.core.module_manager import ModuleManager
    # Нужно получить module_manager из контекста
    # Пока что простой вариант
    
    bot.send_text(
        chat_id=event.from_chat,
        text="📚 **Справка по командам**\n\n"
             "**Основные команды:**\n"
             "• /start — приветствие и информация\n"
             "• /help — эта справка\n\n"
             "**🔄 Календарь (в разработке):**\n"
             "• /today — события на сегодня\n"
             "• /tomorrow — события на завтра\n"
             "• /week — события на неделю\n\n"
             "💡 Все команды работают только в личных сообщениях."
    )