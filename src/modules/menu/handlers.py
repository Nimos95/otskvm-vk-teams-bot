# src/modules/menu/handlers.py

import json
from src.core.constants import Commands, Emoji, ROLE_ADMIN, ROLE_SUPERADMIN, ROLE_MANAGER, ROLE_ENGINEER
from src.core.db_sync import DatabaseSync

# Словарь для хранения msgId активных сообщений
_active_messages = {}


def setup(bot, module_manager):
    """Инициализация модуля главного меню."""
    print("📦 Модуль 'menu' загружается...")
    
    module_manager.register_command(Commands.START, start_handler, 'menu')
    module_manager.register_callback('calendar', calendar_callback, 'menu')
    module_manager.register_callback('my_events', my_events_callback, 'menu')
    module_manager.register_callback('statuses', statuses_callback, 'menu')
    module_manager.register_callback('assignments', assignments_callback, 'menu')
    module_manager.register_callback('reports', reports_callback, 'menu')
    module_manager.register_callback('admin_panel', admin_panel_callback, 'menu')
    
    print("✅ Модуль 'menu' загружен")


def get_user_role_sync(user_id):
    """Получение роли пользователя."""
    row = DatabaseSync.fetchone(
        "SELECT role FROM users WHERE user_id = %s",
        (user_id,)
    )
    return row[0] if row else 'viewer'


def get_main_menu_keyboard(user_id):
    """Создаёт клавиатуру главного меню."""
    role = get_user_role_sync(user_id)
    
    buttons = []
    
    buttons.append([
        {"text": f"{Emoji.CALENDAR} Календарь", "callbackData": "calendar", "style": "primary"}
    ])
    
    if role in [ROLE_ENGINEER, ROLE_ADMIN, ROLE_SUPERADMIN]:
        buttons.append([
            {"text": "🟢 Статусы аудиторий", "callbackData": "statuses", "style": "primary"}
        ])
    
    if role in [ROLE_ENGINEER, ROLE_ADMIN, ROLE_SUPERADMIN]:
        buttons.append([
            {"text": "👤 Мои мероприятия", "callbackData": "my_events", "style": "primary"}
        ])
    
    if role in [ROLE_ADMIN, ROLE_SUPERADMIN]:
        buttons.append([
            {"text": "👥 Назначения", "callbackData": "assignments", "style": "primary"}
        ])
    
    if role in [ROLE_ADMIN, ROLE_MANAGER, ROLE_SUPERADMIN]:
        buttons.append([
            {"text": "📊 Отчётность", "callbackData": "reports", "style": "primary"}
        ])
    
    if role in [ROLE_ADMIN, ROLE_SUPERADMIN]:
        buttons.append([
            {"text": "⚙️ Админ-панель", "callbackData": "admin_panel", "style": "positive"}
        ])
    
    return buttons


def get_main_menu_text(user_id):
    """Возвращает текст главного меню с учётом роли."""
    role = get_user_role_sync(user_id)
    return f"{Emoji.INFO} *Главное меню*\n\nВаша роль: *{role}*\n\nВыберите раздел:"


def send_or_edit(bot, chat_id, text, keyboard, msg_id=None):
    """
    Отправляет новое сообщение или редактирует существующее.
    """
    print(f"🔍 send_or_edit: chat_id={chat_id}, msg_id={msg_id}")
    
    keyboard_json = json.dumps(keyboard)
    
    if msg_id:
        print(f"   ✏️ Пытаемся редактировать сообщение {msg_id}")
        try:
            bot.edit_text(
                chat_id=chat_id,
                msg_id=msg_id,
                text=text,
                parse_mode="MarkdownV2",
                inline_keyboard_markup=keyboard_json
            )
            print(f"   ✅ Сообщение отредактировано")
            return msg_id
        except Exception as e:
            print(f"   ❌ Ошибка редактирования: {e}")
            print(f"   📤 Отправляем новое сообщение (fallback)")
            result = bot.send_text(
                chat_id=chat_id,
                text=text,
                parse_mode="MarkdownV2",
                inline_keyboard_markup=keyboard_json
            )
            try:
                data = result.json()
                new_msg_id = data.get('msgId')
                print(f"   ✅ Отправлено новое сообщение, msgId: {new_msg_id}")
                return new_msg_id
            except:
                return result
    else:
        print(f"   📤 Отправляем новое сообщение")
        result = bot.send_text(
            chat_id=chat_id,
            text=text,
            parse_mode="MarkdownV2",
            inline_keyboard_markup=keyboard_json
        )
        try:
            data = result.json()
            new_msg_id = data.get('msgId')
            print(f"   ✅ Отправлено новое сообщение, msgId: {new_msg_id}")
            return new_msg_id
        except:
            return result


def start_handler(bot, event):
    """Обработчик команды /start."""
    user_id = event.from_chat
    print(f"🔍 start_handler вызван для чата {user_id}")
    
    try:
        from src.modules.users.handlers import register_user_sync
        register_user_sync(user_id)
        
        text = get_main_menu_text(user_id)
        keyboard = get_main_menu_keyboard(user_id)
        
        # Проверяем, есть ли уже активное сообщение
        msg_id = _active_messages.get(user_id)
        
        new_msg_id = send_or_edit(
            bot,
            user_id,
            text,
            keyboard,
            msg_id
        )
        
        if new_msg_id:
            _active_messages[user_id] = new_msg_id
            print(f"   ✅ Сохранён msgId: {new_msg_id}")
        
    except Exception as e:
        print(f"   ❌ Ошибка в start_handler: {e}")
        import traceback
        traceback.print_exc()
        try:
            bot.send_text(
                chat_id=user_id,
                text=f"{Emoji.ERROR} Ошибка: {e}"
            )
        except:
            pass


# ============ Обработчики кнопок главного меню ============

def show_section(bot, event, title, content, keyboard_func):
    """
    Универсальная функция для показа разделов с редактированием.
    """
    user_id = event.from_chat
    msg_id = _active_messages.get(user_id)
    
    text = f"{title}\n\n{content}"
    keyboard = keyboard_func(user_id)
    
    new_msg_id = send_or_edit(
        bot,
        user_id,
        text,
        keyboard,
        msg_id
    )
    
    if new_msg_id:
        _active_messages[user_id] = new_msg_id


def calendar_callback(bot, event):
    """Обработчик кнопки 'Календарь'."""
    from src.modules.calendar.handlers import show_calendar
    show_calendar(bot, event, 'today', 'сегодня')


def my_events_callback(bot, event):
    """Обработчик кнопки 'Мои мероприятия'."""
    show_section(
        bot, event,
        f"{Emoji.INFO} *Мои мероприятия*",
        "Здесь будут показываться мероприятия, на которые вы назначены.\n\nРаздел в разработке.",
        lambda uid: get_main_menu_keyboard(uid)
    )


def statuses_callback(bot, event):
    """Обработчик кнопки 'Статусы аудиторий'."""
    show_section(
        bot, event,
        f"{Emoji.INFO} *Статусы аудиторий*",
        "Здесь можно будет просматривать и отмечать статусы аудиторий.\n\nРаздел в разработке.",
        lambda uid: get_main_menu_keyboard(uid)
    )


def assignments_callback(bot, event):
    """Обработчик кнопки 'Назначения'."""
    show_section(
        bot, event,
        f"{Emoji.INFO} *Назначения*",
        "Здесь можно будет назначать инженеров на мероприятия.\n\nРаздел в разработке.",
        lambda uid: get_main_menu_keyboard(uid)
    )


def reports_callback(bot, event):
    """Обработчик кнопки 'Отчётность'."""
    show_section(
        bot, event,
        f"{Emoji.INFO} *Отчётность*",
        "Здесь будет доступна статистика и отчёты.\n\nРаздел в разработке.",
        lambda uid: get_main_menu_keyboard(uid)
    )


def admin_panel_callback(bot, event):
    """Обработчик кнопки 'Админ-панель'."""
    from src.modules.admin.handlers import admin_panel_handler
    admin_panel_handler(bot, event)