# src/modules/menu/handlers.py

import json
from src.core.constants import Commands, Emoji


def setup(bot, module_manager):
    print("📦 Модуль 'menu' загружается...")
    
    module_manager.register_command(Commands.START, start_handler, 'menu')
    module_manager.register_callback('calendar', calendar_callback, 'menu')
    
    print("✅ Модуль 'menu' загружен")


def get_main_menu_text():
    return f"{Emoji.INFO} *Главное меню*\n\nВыберите раздел:"


def get_main_menu_keyboard():
    return [
        [
            {"text": "📅 Календарь", "callbackData": "calendar", "style": "primary"}
        ]
    ]


def start_handler(bot, event):
    """Обработчик команды /start."""
    print(f"🔍 start_handler вызван для чата {event.from_chat}")
    
    from src.modules.calendar.handlers import _active_messages, send_or_edit
    
    chat_id = event.from_chat
    msg_id = _active_messages.get(chat_id)
    
    if msg_id:
        try:
            bot.edit_text(
                chat_id=chat_id,
                msg_id=msg_id,
                text=get_main_menu_text(),
                parse_mode="MarkdownV2",
                inline_keyboard_markup=json.dumps(get_main_menu_keyboard())
            )
            print(f"   ✅ Главное меню отредактировано (msgId: {msg_id})")
        except Exception as e:
            print(f"   ⚠️ Не удалось отредактировать: {e}")
            new_msg_id = send_or_edit(
                bot,
                chat_id,
                get_main_menu_text(),
                get_main_menu_keyboard(),
                None
            )
            if new_msg_id:
                _active_messages[chat_id] = new_msg_id
                print(f"   ✅ Отправлено новое главное меню, msgId: {new_msg_id}")
    else:
        new_msg_id = send_or_edit(
            bot,
            chat_id,
            get_main_menu_text(),
            get_main_menu_keyboard(),
            None
        )
        if new_msg_id:
            _active_messages[chat_id] = new_msg_id
            print(f"   ✅ Отправлено новое главное меню, msgId: {new_msg_id}")


def calendar_callback(bot, event):
    """Обработчик нажатия на кнопку 'Календарь'."""
    print(f"🔍 calendar_callback вызван для чата {event.from_chat}")
    try:
        from src.modules.calendar.handlers import today_handler
        today_handler(bot, event)
    except Exception as e:
        print(f"   ❌ Ошибка в calendar_callback: {e}")
        import traceback
        traceback.print_exc()
        bot.send_text(
            chat_id=event.from_chat,
            text=f"⚠️ Ошибка при открытии календаря: {e}"
        )