# src/modules/admin/handlers.py

import json
from src.core.constants import Commands, Emoji, ROLE_ADMIN, ROLE_SUPERADMIN
from src.core.db_sync import DatabaseSync
from src.modules.menu.handlers import _active_messages, send_or_edit, get_main_menu_keyboard
import traceback


def setup(bot, module_manager):
    """Инициализация модуля административной панели."""
    print("📦 Модуль 'admin' загружается...")
    
    module_manager.register_command('/admin', admin_panel_handler, 'admin')
    
    module_manager.register_callback('admin_stats', admin_stats_handler, 'admin')
    module_manager.register_callback('admin_status_stats', admin_status_stats_handler, 'admin') 
    module_manager.register_callback('admin_user_management', admin_user_management_handler, 'admin')
    module_manager.register_callback('back_to_main', admin_back_to_main_handler, 'admin')
    
    print("✅ Модуль 'admin' загружен")


def get_user_role_sync(user_id):
    """Получение роли пользователя."""
    row = DatabaseSync.fetchone(
        "SELECT role FROM users WHERE user_id = %s",
        (user_id,)
    )
    return row[0] if row else 'viewer'


def get_admin_keyboard(user_id):
    """Создаёт клавиатуру админ-панели."""
    role = get_user_role_sync(user_id)
    
    buttons = []
    
    if role in [ROLE_ADMIN, ROLE_SUPERADMIN]:
        buttons.append([
            {"text": "📊 Статистика", "callbackData": "admin_stats", "style": "primary"}
        ])
        buttons.append([
            {"text": "📊 Статусы аудиторий", "callbackData": "admin_status_stats", "style": "primary"}  # <-- НОВАЯ КНОПКА
        ])
        buttons.append([
            {"text": "👤 Список пользователей", "callbackData": "admin_users", "style": "primary"}
        ])
    
    if role == ROLE_SUPERADMIN:
        buttons.append([
            {"text": "👤 Управление пользователями", "callbackData": "admin_user_management", "style": "positive"}
        ])
    
    buttons.append([
        {"text": "◀️ В главное меню", "callbackData": "back_to_main", "style": "secondary"}
    ])
    
    return buttons


def admin_panel_handler(bot, event):
    """Показывает админ-панель."""
    user_id = event.from_chat
    role = get_user_role_sync(user_id)
    
    if role not in [ROLE_ADMIN, ROLE_SUPERADMIN]:
        bot.send_text(
            chat_id=user_id,
            text=f"{Emoji.ERROR} ⛔ Доступ запрещён.\n\n"
                 f"Админ-панель доступна только для администраторов.\n"
                 f"Ваша роль: <b>{role}</b>",
            parse_mode="HTML"
        )
        return
    
    text = f"{Emoji.SETTINGS} <b>Админ-панель</b>\n\n"
    text += f"Ваша роль: <b>{role}</b>\n\n"
    text += f"Выберите раздел:"
    
    keyboard = get_admin_keyboard(user_id)
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


def admin_stats_handler(bot, event):
    """Обработчик кнопки 'Статистика'."""
    user_id = event.from_chat
    msg_id = _active_messages.get(user_id)
    
    try:
        users_count = DatabaseSync.fetchone("SELECT COUNT(*) FROM users")[0]
        events_count = DatabaseSync.fetchone("SELECT COUNT(*) FROM calendar_events WHERE status != 'cancelled'")[0]
        auditories_count = DatabaseSync.fetchone("SELECT COUNT(*) FROM auditories WHERE is_active = TRUE")[0]
        
        text = f"{Emoji.STATS} <b>Статистика системы</b>\n\n"
        text += f"👤 Пользователей: <b>{users_count}</b>\n"
        text += f"📅 Активных событий: <b>{events_count}</b>\n"
        text += f"🏛️ Активных аудиторий: <b>{auditories_count}</b>"
        
        keyboard = get_admin_keyboard(user_id)
        
        new_msg_id = send_or_edit(
            bot,
            user_id,
            text,
            keyboard,
            msg_id
        )
        
        if new_msg_id:
            _active_messages[user_id] = new_msg_id
        
    except Exception as e:
        bot.send_text(
            chat_id=user_id,
            text=f"{Emoji.ERROR} Ошибка при получении статистики: {e}",
            parse_mode="HTML"
        )


def admin_users_callback(bot, event):
    """
    Обработчик кнопки 'Список пользователей'.
    Показывает модальное окно со списком пользователей.
    """
    user_id = event.from_chat
    
    # Проверка прав (дополнительная, на случай прямого вызова)
    role = get_user_role_sync(user_id)
    if role not in [ROLE_ADMIN, ROLE_SUPERADMIN]:
        bot.answer_callback_query(
            query_id=event.data['queryId'],
            text="⛔ Доступ запрещён.",
            show_alert=True
        )
        return
    
    try:
        # Получаем список пользователей
        rows = DatabaseSync.fetchall(
            """
            SELECT user_id, full_name, role, created_at, is_active 
            FROM users 
            ORDER BY role, created_at
            """
        )
        
        if not rows:
            bot.answer_callback_query(
                query_id=event.data['queryId'],
                text="📭 Пользователей пока нет.",
                show_alert=True
            )
            return
        
        # Группируем по ролям
        roles = {}
        for row in rows:
            u_id, full_name, role, created_at, is_active = row
            if role not in roles:
                roles[role] = []
            roles[role].append((u_id, full_name, is_active))
        
        # Формируем сообщение для модального окна
        # В модальном окне ограничение по длине, поэтому делаем кратко
        message = f"👤 Список пользователей ({len(rows)} чел.)\n\n"
        
        for role, users_list in sorted(roles.items()):
            message += f"{role.upper()} ({len(users_list)} чел.)\n"
            for u_id, name, active in users_list[:3]:  # Показываем первых 3 для краткости
                status = "🟢" if active else "🔴"
                display_name = name or u_id.split('@')[0]
                message += f"  {status} {display_name}\n"
            if len(users_list) > 3:
                message += f"  ... и ещё {len(users_list) - 3}\n"
            message += "\n"
        

        
        # Показываем модальное окно
        bot.answer_callback_query(
            query_id=event.data['queryId'],
            text=message,
            show_alert=True
        )
        
        # Также обновляем основное сообщение (админ-панель остаётся)
        # Можно оставить как есть или обновить
        
    except Exception as e:
        bot.answer_callback_query(
            query_id=event.data['queryId'],
            text=f"❌ Ошибка: {str(e)[:100]}",
            show_alert=True
        )
        print(f"   ❌ Ошибка в admin_users_callback: {e}")
        import traceback
        traceback.print_exc()


def admin_user_management_handler(bot, event):
    """Заглушка для 'Управление пользователями'."""
    user_id = event.from_chat
    msg_id = _active_messages.get(user_id)
    
    text = f"{Emoji.INFO} <b>Управление пользователями</b>\n\n"
    text += f"Доступно только для <b>Superadmin</b>.\n\n"
    text += f"Используйте команды:\n"
    text += f"• <code>/list_users</code> — список пользователей\n"
    text += f"• <code>/set_role</code> — назначение роли"
    
    keyboard = get_admin_keyboard(user_id)
    
    new_msg_id = send_or_edit(
        bot,
        user_id,
        text,
        keyboard,
        msg_id
    )
    
    if new_msg_id:
        _active_messages[user_id] = new_msg_id


def admin_back_to_main_handler(bot, event):
    """Обработчик кнопки 'В главное меню'."""
    from src.modules.menu.handlers import start_handler
    start_handler(bot, event)

def admin_status_stats_handler(bot, event):
    """Обработчик кнопки '📊 Статусы аудиторий'."""
    user_id = event.from_chat
    msg_id = _active_messages.get(user_id)
    
    try:
        # Получаем статистику по статусам
        rows = DatabaseSync.fetchall(
            """
            SELECT 
                COUNT(*) FILTER (WHERE sl.status = 'green') as green_count,
                COUNT(*) FILTER (WHERE sl.status = 'yellow') as yellow_count,
                COUNT(*) FILTER (WHERE sl.status = 'red') as red_count,
                COUNT(*) FILTER (WHERE sl.status IS NULL) as no_status,
                COUNT(*) as total
            FROM auditories a
            LEFT JOIN (
                SELECT DISTINCT ON (auditory_id) 
                    auditory_id, status
                FROM status_log
                ORDER BY auditory_id, created_at DESC
            ) sl ON a.id = sl.auditory_id
            WHERE a.is_active = TRUE
            """
        )
        
        if rows:
            row = rows[0]
            green, yellow, red, no_status, total = row
        else:
            green = yellow = red = no_status = 0
            total = 0
        
        # Получаем список аудиторий с проблемами
        problem_rows = DatabaseSync.fetchall(
            """
            SELECT 
                a.name,
                a.building,
                sl.status,
                sl.comment,
                sl.created_at
            FROM auditories a
            JOIN (
                SELECT DISTINCT ON (auditory_id) 
                    auditory_id, status, comment, created_at
                FROM status_log
                ORDER BY auditory_id, created_at DESC
            ) sl ON a.id = sl.auditory_id
            WHERE sl.status IN ('yellow', 'red')
            ORDER BY sl.created_at DESC
            LIMIT 10
            """
        )
        
        # Формируем сообщение
        lines = [f"{Emoji.STATS} **Статистика по статусам аудиторий**", ""]
        lines.append(f"🟢 Всё работает: **{green}**")
        lines.append(f"🟡 Есть проблемы: **{yellow}**")
        lines.append(f"🔴 Не работает: **{red}**")
        lines.append(f"⚪ Статус не установлен: **{no_status}**")
        lines.append("")
        lines.append(f"━━━━━━━━━━━━━━━━━━━━━")
        lines.append(f"📊 Всего аудиторий: **{total}**")
        
        if problem_rows:
            lines.append("")
            lines.append("**🔴 Проблемные аудитории:**")
            for row in problem_rows:
                name, building, status, comment, created_at = row
                status_emoji = '🟡' if status == 'yellow' else '🔴'
                date_str = created_at.strftime('%d.%m.%Y')
                line = f"   {status_emoji} **{name}**"
                if building:
                    line += f" ({building})"
                if comment:
                    line += f" — {comment[:50]}"
                line += f" {date_str}"
                lines.append(line)
        
        keyboard = get_admin_keyboard(user_id)
        
        new_msg_id = send_or_edit(
            bot,
            user_id,
            "\n".join(lines),
            keyboard,
            msg_id
        )
        
        if new_msg_id:
            _active_messages[user_id] = new_msg_id
        
    except Exception as e:
        print(f"   ❌ Ошибка в admin_status_stats_handler: {e}")
        traceback.print_exc()
        bot.send_text(
            chat_id=user_id,
            text=f"{Emoji.ERROR} Ошибка: {e}"
        )