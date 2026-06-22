# src/modules/auditory/handlers.py

import json
import traceback
from datetime import datetime
from src.core.constants import Commands, Emoji, ROLE_ENGINEER, ROLE_ADMIN, ROLE_SUPERADMIN
from src.core.db_sync import DatabaseSync
from src.modules.menu.handlers import _active_messages, send_or_edit, get_main_menu_text, get_main_menu_keyboard

_pending_comments = {}


def setup(bot, module_manager):
    """Инициализация модуля статусов аудиторий."""
    print("📦 Модуль 'auditory' загружается...")
    
    module_manager.register_command('/status', status_handler, 'auditory')
    module_manager.register_command('/set_status', set_status_handler, 'auditory')
    
    print("✅ Модуль 'auditory' загружен")


def get_user_role_sync(user_id):
    """Получение роли пользователя."""
    row = DatabaseSync.fetchone(
        "SELECT role FROM users WHERE user_id = %s",
        (user_id,)
    )
    return row[0] if row else 'viewer'


def get_auditory_list_keyboard(user_id):
    """Создаёт клавиатуру со списком аудиторий."""
    role = get_user_role_sync(user_id)
    
    if role not in [ROLE_ENGINEER, ROLE_ADMIN, ROLE_SUPERADMIN]:
        return []
    
    rows = DatabaseSync.fetchall(
        """
        SELECT id, name, building
        FROM auditories
        WHERE is_active = TRUE
        ORDER BY name
        """
    )
    
    buttons = []
    for row in rows:
        auditory_id, name, building = row
        label = name
        if building:
            label += f" ({building})"
        buttons.append([
            {"text": label, "callbackData": f"auditory_select_{auditory_id}", "style": "primary"}
        ])
    
    buttons.append([
        {"text": "◀️ Отмена", "callbackData": "auditory_cancel", "style": "secondary"}
    ])
    
    return buttons


def get_comment_keyboard():
    """Создаёт клавиатуру с кнопками 'Сохранить без комментария' и 'Отмена'."""
    return [
        [
            {"text": "⏭️ Сохранить без комментария", "callbackData": "auditory_skip_comment", "style": "primary"},
            {"text": "❌ Отмена", "callbackData": "auditory_cancel_comment", "style": "secondary"}
        ]
    ]


def handle_auditory_callback(bot, event):
    """
    Универсальный обработчик для всех callback аудиторий.
    Возвращает True, если callback был обработан, иначе False.
    """
    user_id = event.from_chat
    callback_data = event.data.get('callbackData')
    
    print(f"🔍 handle_auditory_callback: {callback_data}")
    
    if not callback_data.startswith('auditory_'):
        return False
    
    parts = callback_data.split('_')
    
    if len(parts) < 2:
        return False
    
    action = parts[1]
    
    if action == 'skip' and len(parts) >= 3 and parts[2] == 'comment':
        auditory_skip_comment_callback(bot, event)
        return True
    
    if action == 'cancel' and len(parts) >= 3 and parts[2] == 'comment':
        auditory_cancel_comment_callback(bot, event)
        return True
    
    if action == 'select' and len(parts) >= 3:
        auditory_id = parts[2]
        auditory_select_callback(bot, event, auditory_id)
        return True
    
    if action == 'status' and len(parts) >= 4:
        auditory_id = parts[2]
        status = parts[3]
        auditory_status_callback(bot, event, auditory_id, status)
        return True
    
    if action == 'history' and len(parts) >= 3:
        auditory_id = parts[2]
        bot.answer_callback_query(
            query_id=event.data['queryId'],
            text="📋 История статусов в разработке",
            show_alert=True
        )
        return True
    
    if action == 'back':
        set_status_handler(bot, event)
        bot.answer_callback_query(
            query_id=event.data['queryId'],
            text="◀️ Возврат к списку",
            show_alert=False
        )
        return True
    
    if action == 'cancel' and len(parts) == 2:
        auditory_cancel_callback(bot, event)
        return True
    
    return False


def status_handler(bot, event):
    """Команда /status — просмотр статусов всех аудиторий."""
    user_id = event.from_chat
    print(f"🔍 status_handler вызван для чата {user_id}")
    
    try:
        rows = DatabaseSync.fetchall(
            """
            SELECT 
                a.id,
                a.name,
                a.building,
                sl.status,
                sl.comment,
                sl.created_at,
                u.full_name AS reported_by
            FROM auditories a
            LEFT JOIN (
                SELECT DISTINCT ON (auditory_id) 
                    auditory_id, status, comment, created_at, reported_by
                FROM status_log
                ORDER BY auditory_id, created_at DESC
            ) sl ON a.id = sl.auditory_id
            LEFT JOIN users u ON sl.reported_by = u.user_id
            WHERE a.is_active = TRUE
            ORDER BY a.name
            """
        )
        
        print(f"🔍 Получено аудиторий: {len(rows) if rows else 0}")
        
        if not rows:
            bot.send_text(
                chat_id=user_id,
                text=f"{Emoji.EMPTY} Аудиторий пока нет.",
                parse_mode="MarkdownV2"
            )
            return
        
        lines = [f"{Emoji.LOCATION} **Статусы аудиторий**", ""]
        
        for row in rows:
            try:
                auditory_id, name, building, status, comment, created_at, reported_by = row
                
                status_emoji = {
                    'green': '🟢',
                    'yellow': '🟡',
                    'red': '🔴'
                }.get(status, '⚪')
                
                status_text = {
                    'green': 'Всё работает',
                    'yellow': 'Есть проблемы',
                    'red': 'Не работает'
                }.get(status, 'Статус неизвестен')
                
                line = f"{status_emoji} **{name}** — {status_text}"
                
                if building:
                    line += f" ({building})"
                
                lines.append(line)
                
                if comment:
                    lines.append(f"   📝 {comment}")
                if reported_by and created_at:
                    time_str = created_at.strftime('%H:%M')
                    lines.append(f"   👤 {reported_by} ({time_str})")
                
                lines.append("")
            except Exception as e:
                print(f"   ⚠️ Ошибка при обработке строки {row}: {e}")
                continue
        
        if len(lines) <= 2:
            bot.send_text(
                chat_id=user_id,
                text=f"{Emoji.EMPTY} Не удалось загрузить статусы.",
                parse_mode="MarkdownV2"
            )
            return
        
        bot.send_text(
            chat_id=user_id,
            text="\n".join(lines),
            parse_mode="MarkdownV2"
        )
        print(f"   ✅ Сообщение отправлено")
        
    except Exception as e:
        print(f"   ❌ Ошибка в status_handler: {e}")
        traceback.print_exc()
        bot.send_text(
            chat_id=user_id,
            text=f"{Emoji.ERROR} Ошибка при загрузке статусов: {e}"
        )


def set_status_handler(bot, event):
    """Команда /set_status — интерактивная отметка статуса."""
    user_id = event.from_chat
    print(f"🔍 set_status_handler вызван для чата {user_id}")
    
    try:
        role = get_user_role_sync(user_id)
        if role not in [ROLE_ENGINEER, ROLE_ADMIN, ROLE_SUPERADMIN]:
            bot.send_text(
                chat_id=user_id,
                text=f"{Emoji.ERROR} ⛔ Доступ запрещён.\n\n"
                     f"Отметка статусов доступна только для инженеров и администраторов.\n"
                     f"Ваша роль: <b>{role}</b>",
                parse_mode="HTML"
            )
            return
        
        keyboard = get_auditory_list_keyboard(user_id)
        
        if not keyboard:
            bot.send_text(
                chat_id=user_id,
                text=f"{Emoji.EMPTY} Аудиторий пока нет.",
                parse_mode="MarkdownV2"
            )
            return
        
        msg_id = _active_messages.get(user_id)
        send_or_edit(
            bot,
            user_id,
            f"{Emoji.LOCATION} **Выберите аудиторию:**",
            keyboard,
            msg_id
        )
        print(f"   ✅ Сообщение отправлено/отредактировано")
        
    except Exception as e:
        print(f"   ❌ Ошибка в set_status_handler: {e}")
        traceback.print_exc()
        bot.send_text(
            chat_id=user_id,
            text=f"{Emoji.ERROR} Ошибка: {e}"
        )


def auditory_select_callback(bot, event, auditory_id):
    """Обработчик выбора аудитории."""
    user_id = event.from_chat
    print(f"🔍 auditory_select_callback: пользователь {user_id}, аудитория {auditory_id}")
    
    try:
        auditory = DatabaseSync.fetchone(
            """
            SELECT id, name, building, floor, equipment
            FROM auditories
            WHERE id = %s AND is_active = TRUE
            """,
            (auditory_id,)
        )
        
        if not auditory:
            bot.answer_callback_query(
                query_id=event.data['queryId'],
                text="❌ Аудитория не найдена.",
                show_alert=True
            )
            return
        
        auditory_id, name, building, floor, equipment = auditory
        
        status_row = DatabaseSync.fetchone(
            """
            SELECT 
                sl.status,
                sl.comment,
                sl.created_at,
                u.full_name AS reported_by
            FROM status_log sl
            LEFT JOIN users u ON sl.reported_by = u.user_id
            WHERE sl.auditory_id = %s
            ORDER BY sl.created_at DESC
            LIMIT 1
            """,
            (auditory_id,)
        )
        
        if status_row:
            status, comment, created_at, reported_by = status_row
            status_emoji = {
                'green': '🟢',
                'yellow': '🟡',
                'red': '🔴'
            }.get(status, '⚪')
            status_text = {
                'green': 'Всё работает',
                'yellow': 'Есть проблемы',
                'red': 'Не работает'
            }.get(status, 'Статус неизвестен')
            status_info = f"{status_emoji} {status_text}"
            
            extra_info = ""
            if comment:
                extra_info += f"\n📝 {comment}"
            if reported_by and created_at:
                time_str = created_at.strftime('%H:%M')
                extra_info += f"\n👤 {reported_by} ({time_str})"
        else:
            status_info = "⚪ Статус не установлен"
            extra_info = ""
        
        card = f"🏛️ **{name}**\n\n"
        
        if building:
            card += f"📍 {building}"
            if floor is not None:
                card += f", {floor} этаж"
            card += "\n"
        
        if equipment:
            card += f"🔧 {equipment}\n"
        
        card += f"\n**Текущий статус:** {status_info}{extra_info}"
        
        buttons = [
            [
                {"text": "🟢 Всё работает", "callbackData": f"auditory_status_{auditory_id}_green", "style": "positive"},
                {"text": "🟡 Есть проблемы", "callbackData": f"auditory_status_{auditory_id}_yellow", "style": "primary"}
            ],
            [
                {"text": "🔴 Не работает", "callbackData": f"auditory_status_{auditory_id}_red", "style": "negative"},
                {"text": "📋 История", "callbackData": f"auditory_history_{auditory_id}", "style": "secondary"}
            ],
            [
                {"text": "◀️ Назад к списку", "callbackData": "auditory_back", "style": "secondary"}
            ]
        ]
        
        bot.answer_callback_query(
            query_id=event.data['queryId'],
            text="🏛️ Загружаю информацию...",
            show_alert=False
        )
        
        msg_id = _active_messages.get(user_id)
        send_or_edit(
            bot,
            user_id,
            card,
            buttons,
            msg_id
        )
        
    except Exception as e:
        print(f"   ❌ Ошибка в auditory_select_callback: {e}")
        traceback.print_exc()
        bot.answer_callback_query(
            query_id=event.data['queryId'],
            text=f"❌ Ошибка: {e}",
            show_alert=True
        )


def auditory_cancel_callback(bot, event):
    """Обработчик кнопки 'Отмена'."""
    user_id = event.from_chat
    
    bot.answer_callback_query(
        query_id=event.data['queryId'],
        text="❌ Отменено",
        show_alert=False
    )
    
    from src.modules.menu.handlers import start_handler
    start_handler(bot, event)


def auditory_cancel_comment_callback(bot, event):
    """
    Обработчик кнопки 'Отмена' при вводе комментария.
    Отменяет изменение статуса и возвращает к списку аудиторий.
    """
    user_id = event.from_chat
    print(f"🔍 auditory_cancel_comment_callback: пользователь {user_id}")
    
    if user_id in _pending_comments:
        del _pending_comments[user_id]
        print(f"   📝 Удалено состояние для {user_id}")
    
    bot.answer_callback_query(
        query_id=event.data['queryId'],
        text="❌ Изменение статуса отменено",
        show_alert=False
    )
    
    set_status_handler(bot, event)


def auditory_skip_comment_callback(bot, event):
    """
    Обработчик кнопки 'Сохранить без комментария'.
    Сохраняет статус без комментария, показывает подтверждение,
    затем возвращает к списку аудиторий.
    """
    user_id = event.from_chat
    print(f"🔍 auditory_skip_comment_callback: пользователь {user_id}")
    
    if user_id not in _pending_comments:
        bot.answer_callback_query(
            query_id=event.data['queryId'],
            text="❌ Нет активного изменения статуса.",
            show_alert=True
        )
        return
    
    pending = _pending_comments[user_id]
    auditory_id = pending['auditory_id']
    auditory_name = pending['auditory_name']
    status = pending['status']
    
    del _pending_comments[user_id]
    
    role = get_user_role_sync(user_id)
    if role not in [ROLE_ENGINEER, ROLE_ADMIN, ROLE_SUPERADMIN]:
        bot.answer_callback_query(
            query_id=event.data['queryId'],
            text="⛔ Доступ запрещён.",
            show_alert=True
        )
        return
    
    try:
        DatabaseSync.execute(
            """
            INSERT INTO status_log (auditory_id, status, comment, reported_by)
            VALUES (%s, %s, %s, %s)
            """,
            (auditory_id, status, '', user_id)
        )
        
        status_emoji = {
            'green': '🟢',
            'yellow': '🟡',
            'red': '🔴'
        }.get(status, '⚪')
        
        status_text = {
            'green': 'Всё работает',
            'yellow': 'Есть проблемы',
            'red': 'Не работает'
        }.get(status, 'Статус неизвестен')
        
        bot.answer_callback_query(
            query_id=event.data['queryId'],
            text=f"✅ Статус обновлён!",
            show_alert=False
        )
        
        # 1. Редактируем текущее сообщение — показываем подтверждение
        msg_id = _active_messages.get(user_id)
        send_or_edit(
            bot,
            user_id,
            f"{Emoji.SUCCESS} **Статус обновлён!**\n\n"
            f"🏛️ Аудитория: **{auditory_name}**\n"
            f"🔄 Статус: {status_emoji} **{status_text}**\n"
            f"📝 Комментарий: (без комментария)\n"
            f"👤 Отметил: {user_id}\n"
            f"🕐 {datetime.now().strftime('%H:%M')}",
            [],
            msg_id
        )
        
        # 2. Возвращаемся к списку аудиторий
        set_status_handler(bot, event)
        
    except Exception as e:
        print(f"   ❌ Ошибка при сохранении статуса: {e}")
        traceback.print_exc()
        bot.answer_callback_query(
            query_id=event.data['queryId'],
            text=f"❌ Ошибка: {e}",
            show_alert=True
        )


def auditory_status_callback(bot, event, auditory_id, status):
    """Обработчик изменения статуса аудитории."""
    user_id = event.from_chat
    print(f"🔍 auditory_status_callback: пользователь {user_id}, аудитория {auditory_id}, статус {status}")
    
    role = get_user_role_sync(user_id)
    if role not in [ROLE_ENGINEER, ROLE_ADMIN, ROLE_SUPERADMIN]:
        bot.answer_callback_query(
            query_id=event.data['queryId'],
            text="⛔ Доступ запрещён. Только для инженеров и администраторов.",
            show_alert=True
        )
        return
    
    auditory = DatabaseSync.fetchone(
        "SELECT id, name FROM auditories WHERE id = %s AND is_active = TRUE",
        (auditory_id,)
    )
    
    if not auditory:
        bot.answer_callback_query(
            query_id=event.data['queryId'],
            text="❌ Аудитория не найдена.",
            show_alert=True
        )
        return
    
    status_names = {
        'green': '🟢 Всё работает',
        'yellow': '🟡 Есть проблемы',
        'red': '🔴 Не работает'
    }
    
    _pending_comments[user_id] = {
        'auditory_id': int(auditory_id),
        'auditory_name': auditory[1],
        'status': status
    }
    print(f"   📝 Сохранено состояние для {user_id}: {_pending_comments[user_id]}")
    
    bot.answer_callback_query(
        query_id=event.data['queryId'],
        text=f"📝 Введите комментарий",
        show_alert=False
    )
    
    msg_id = _active_messages.get(user_id)
    send_or_edit(
        bot,
        user_id,
        f"{Emoji.INFO} **Введите комментарий**\n\n"
        f"🏛️ Аудитория: **{auditory[1]}**\n"
        f"🔄 Статус: {status_names.get(status, status)}\n\n"
        f"📝 Напишите комментарий в следующем сообщении.\n"
        f"💡 Нажмите «⏭️ Сохранить без комментария», чтобы пропустить.",
        get_comment_keyboard(),
        msg_id
    )


def handle_comment_message(bot, event):
    """
    Обработчик текстовых сообщений для ввода комментария.
    Сохраняет статус с комментарием, показывает подтверждение новым сообщением,
    затем отправляет главное меню.
    """
    user_id = event.from_chat
    text = event.text.strip()
    
    if user_id not in _pending_comments:
        return False
    
    pending = _pending_comments[user_id]
    auditory_id = pending['auditory_id']
    auditory_name = pending['auditory_name']
    status = pending['status']
    
    del _pending_comments[user_id]
    
    role = get_user_role_sync(user_id)
    if role not in [ROLE_ENGINEER, ROLE_ADMIN, ROLE_SUPERADMIN]:
        bot.send_text(
            chat_id=user_id,
            text=f"{Emoji.ERROR} ⛔ Доступ запрещён.",
            parse_mode="HTML"
        )
        return True
    
    try:
        DatabaseSync.execute(
            """
            INSERT INTO status_log (auditory_id, status, comment, reported_by)
            VALUES (%s, %s, %s, %s)
            """,
            (auditory_id, status, text, user_id)
        )
        
        status_emoji = {
            'green': '🟢',
            'yellow': '🟡',
            'red': '🔴'
        }.get(status, '⚪')
        
        status_text = {
            'green': 'Всё работает',
            'yellow': 'Есть проблемы',
            'red': 'Не работает'
        }.get(status, 'Статус неизвестен')
        
        # 1. Отправляем НОВОЕ сообщение с подтверждением (без форматирования)
        bot.send_text(
            chat_id=user_id,
            text=f"✅ Статус обновлён!\n\n"
                 f"🏛️ Аудитория: {auditory_name}\n"
                 f"🔄 Статус: {status_emoji} {status_text}\n"
                 f"📝 Комментарий: {text}\n"
                 f"👤 Отметил: {user_id}\n"
                 f"🕐 {datetime.now().strftime('%H:%M')}"
        )
        print(f"   ✅ Отправлено подтверждение (без форматирования)")
        
        # 2. Отправляем НОВОЕ сообщение с главным меню
        menu_text = get_main_menu_text(user_id)
        menu_keyboard = get_main_menu_keyboard(user_id)
        
        result = bot.send_text(
            chat_id=user_id,
            text=menu_text,
            parse_mode="MarkdownV2",
            inline_keyboard_markup=json.dumps(menu_keyboard)
        )
        print(f"   ✅ Отправлено новое главное меню (последнее сообщение)")
        
        # Обновляем _active_messages на новое сообщение
        try:
            data = result.json()
            new_msg_id = data.get('msgId')
            if new_msg_id:
                _active_messages[user_id] = new_msg_id
                print(f"   ✅ Обновлён msgId: {new_msg_id}")
        except:
            pass
        
    except Exception as e:
        print(f"   ❌ Ошибка при сохранении статуса: {e}")
        traceback.print_exc()
        bot.send_text(
            chat_id=user_id,
            text=f"{Emoji.ERROR} Ошибка при сохранении статуса: {e}"
        )
    
    return True