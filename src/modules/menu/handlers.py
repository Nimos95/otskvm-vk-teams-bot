# src/modules/menu/handlers.py

import json
from src.core.constants import Commands, Emoji, ROLE_ADMIN, ROLE_SUPERADMIN, ROLE_MANAGER, ROLE_ENGINEER
from src.core.db_sync import DatabaseSync

_active_messages = {}


def send_or_edit(bot, chat_id, text, keyboard, msg_id=None):
    """Отправляет новое сообщение или редактирует существующее."""
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
            except Exception as e2:
                print(f"   ⚠️ Не удалось получить msgId: {e2}")
                return None
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
        except Exception as e:
            print(f"   ⚠️ Не удалось получить msgId: {e}")
            return None


def setup(bot, module_manager):
    print("📦 Модуль 'menu' загружается...")
    
    module_manager.register_command(Commands.START, start_handler, 'menu')
    module_manager.register_callback('calendar', calendar_callback, 'menu')
    module_manager.register_callback('auditory_statuses', auditory_statuses_callback, 'menu')
    module_manager.register_callback('my_events', my_events_callback, 'menu')
    module_manager.register_callback('assignments', assignments_callback, 'menu')
    module_manager.register_callback('reports', reports_callback, 'menu')
    module_manager.register_callback('admin_panel', admin_panel_callback, 'menu')
    
    print("✅ Модуль 'menu' загружен")


def get_user_role_sync(user_id):
    row = DatabaseSync.fetchone(
        "SELECT role FROM users WHERE user_id = %s",
        (user_id,)
    )
    return row[0] if row else 'viewer'


def get_main_menu_keyboard(user_id):
    """Создаёт клавиатуру главного меню (массив массивов)."""
    role = get_user_role_sync(user_id)
    
    buttons = []
    
    buttons.append([
        {"text": f"{Emoji.CALENDAR} Календарь", "callbackData": "calendar", "style": "primary"}
    ])
    
    if role in [ROLE_ENGINEER, ROLE_ADMIN, ROLE_SUPERADMIN]:
        buttons.append([
            {"text": "🟢 Статусы аудиторий", "callbackData": "auditory_statuses", "style": "primary"}
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
    role = get_user_role_sync(user_id)
    return f"{Emoji.INFO} *Главное меню*\n\nВаша роль: *{role}*\n\nВыберите раздел:"


def start_handler(bot, event):
    """Обработчик команды /start."""
    user_id = event.from_chat
    print(f"🔍 start_handler вызван для чата {user_id}")
    
    from src.modules.users.handlers import register_user_sync
    register_user_sync(user_id)
    
    text = get_main_menu_text(user_id)
    keyboard = get_main_menu_keyboard(user_id)
    
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


# ============ Обработчики кнопок главного меню ============

def calendar_callback(bot, event):
    print(f"🔍 calendar_callback вызван для чата {event.from_chat}")
    from src.modules.calendar.handlers import today_handler
    today_handler(bot, event)


def auditory_statuses_callback(bot, event):
    user_id = event.from_chat
    print(f"🔍 auditory_statuses_callback вызван для чата {user_id}")
    
    role = get_user_role_sync(user_id)
    if role not in [ROLE_ENGINEER, ROLE_ADMIN, ROLE_SUPERADMIN]:
        bot.send_text(
            chat_id=user_id,
            text=f"{Emoji.ERROR} ⛔ Доступ запрещён.",
            parse_mode="MarkdownV2"
        )
        return
    
    from src.modules.auditory.handlers import set_status_handler
    set_status_handler(bot, event)


def my_events_callback(bot, event):
    user_id = event.from_chat
    bot.send_text(
        chat_id=user_id,
        text=f"{Emoji.INFO} *Мои мероприятия*\n\nЗдесь будут показываться мероприятия, на которые вы назначены.\n\nРаздел в разработке.",
        parse_mode="MarkdownV2"
    )


def assignments_callback(bot, event):
    user_id = event.from_chat
    bot.send_text(
        chat_id=user_id,
        text=f"{Emoji.INFO} *Назначения*\n\nЗдесь можно будет назначать инженеров на мероприятия.\n\nРаздел в разработке.",
        parse_mode="MarkdownV2"
    )


def reports_callback(bot, event):
    user_id = event.from_chat
    bot.send_text(
        chat_id=user_id,
        text=f"{Emoji.INFO} *Отчётность*\n\nЗдесь будет доступна статистика и отчёты.\n\nРаздел в разработке.",
        parse_mode="MarkdownV2"
    )


def admin_panel_callback(bot, event):
    user_id = event.from_chat
    from src.modules.admin.handlers import admin_panel_handler
    admin_panel_handler(bot, event)