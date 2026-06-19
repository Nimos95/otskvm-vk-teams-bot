# src/modules/users/handlers.py

from src.core.constants import Commands, Emoji, ALL_ROLES, ROLE_SUPERADMIN
from src.core.db_sync import DatabaseSync


def setup(bot, module_manager):
    """Инициализация модуля пользователей."""
    print("📦 Модуль 'users' загружается...")
    
    module_manager.register_command('/my_role', my_role_handler, 'users')
    module_manager.register_command('/set_role', set_role_handler, 'users')
    module_manager.register_command('/list_users', list_users_handler, 'users')
    
    print("✅ Модуль 'users' загружен")


def get_user_role_sync(user_id):
    """Получение роли пользователя."""
    row = DatabaseSync.fetchone(
        "SELECT role FROM users WHERE user_id = %s",
        (user_id,)
    )
    return row[0] if row else 'viewer'


def register_user_sync(user_id, full_name=None):
    """Регистрация пользователя."""
    row = DatabaseSync.fetchone(
        "SELECT user_id FROM users WHERE user_id = %s",
        (user_id,)
    )
    if not row:
        DatabaseSync.execute(
            """
            INSERT INTO users (user_id, full_name, role)
            VALUES (%s, %s, 'viewer')
            """,
            (user_id, full_name or user_id.split('@')[0])
        )
        print(f"👤 Зарегистрирован новый пользователь: {user_id}")
    else:
        DatabaseSync.execute(
            "UPDATE users SET last_active = CURRENT_TIMESTAMP WHERE user_id = %s",
            (user_id,)
        )


def require_role(allowed_roles):
    """Декоратор для проверки прав доступа."""
    def decorator(func):
        def wrapper(bot, event):
            user_id = event.from_chat
            role = get_user_role_sync(user_id)
            
            if role not in allowed_roles:
                bot.send_text(
                    chat_id=event.from_chat,
                    text=f"{Emoji.ERROR} ⛔ Доступ запрещён.\n\n"
                         f"Ваша роль: <b>{role}</b>\n"
                         f"Требуется: {', '.join(allowed_roles)}",
                    parse_mode="HTML"
                )
                return
            
            return func(bot, event)
        return wrapper
    return decorator


# ============ Обработчики команд ============

def my_role_handler(bot, event):
    """Команда /my_role — показать свою роль."""
    user_id = event.from_chat
    
    try:
        row = DatabaseSync.fetchone(
            "SELECT full_name, role FROM users WHERE user_id = %s",
            (user_id,)
        )
        
        if not row:
            register_user_sync(user_id)
            bot.send_text(
                chat_id=user_id,
                text=f"{Emoji.INFO} Вы зарегистрированы как <b>viewer</b>.\n"
                     f"Напишите <b>/my_role</b> для просмотра профиля.",
                parse_mode="HTML"
            )
            return
        
        full_name, role = row
        full_name = full_name or user_id.split('@')[0]
        
        bot.send_text(
            chat_id=user_id,
            text=f"{Emoji.USER} <b>Ваш профиль</b>\n\n"
                 f"👤 Имя: {full_name}\n"
                 f"📧 Email: {user_id}\n"
                 f"🔑 Роль: <b>{role}</b>\n\n"
                 f"💡 Если роль не соответствует вашей должности, обратитесь к администратору.",
            parse_mode="HTML"
        )
        
    except Exception as e:
        print(f"❌ Ошибка в my_role_handler: {e}")
        import traceback
        traceback.print_exc()
        bot.send_text(
            chat_id=user_id,
            text=f"{Emoji.ERROR} Ошибка: {e}",
            parse_mode="HTML"
        )


@require_role([ROLE_SUPERADMIN])
def set_role_handler(bot, event):
    """Команда /set_role — назначить роль пользователю."""
    user_id = event.from_chat
    args = event.text.strip().split()
    
    if len(args) < 3:
        bot.send_text(
            chat_id=user_id,
            text=f"{Emoji.HELP} <b>Использование:</b>\n"
                 f"<code>/set_role email_пользователя роль</code>\n\n"
                 f"<b>Доступные роли:</b>\n"
                 f"{', '.join(ALL_ROLES)}\n\n"
                 f"<b>Пример:</b>\n"
                 f"<code>/set_role ivanov@spbstu.ru manager</code>",
            parse_mode="HTML"
        )
        return
    
    target_email = args[1]
    new_role = args[2].lower()
    
    if new_role not in ALL_ROLES:
        bot.send_text(
            chat_id=user_id,
            text=f"{Emoji.ERROR} Неизвестная роль: <b>{new_role}</b>\n\n"
                 f"Доступные роли: {', '.join(ALL_ROLES)}",
            parse_mode="HTML"
        )
        return
    
    row = DatabaseSync.fetchone(
        "SELECT user_id, full_name FROM users WHERE user_id = %s",
        (target_email,)
    )
    
    if not row:
        bot.send_text(
            chat_id=user_id,
            text=f"{Emoji.ERROR} Пользователь <b>{target_email}</b> не найден.\n"
                 f"Он должен хотя бы раз написать боту для регистрации.",
            parse_mode="HTML"
        )
        return
    
    DatabaseSync.execute(
        "UPDATE users SET role = %s WHERE user_id = %s",
        (new_role, target_email)
    )
    
    full_name = row[1] or target_email
    
    bot.send_text(
        chat_id=user_id,
        text=f"{Emoji.SUCCESS} <b>Роль обновлена!</b>\n\n"
             f"👤 Пользователь: {full_name}\n"
             f"📧 Email: {target_email}\n"
             f"🔑 Новая роль: <b>{new_role}</b>",
        parse_mode="HTML"
    )


@require_role([ROLE_SUPERADMIN, 'admin'])
def list_users_handler(bot, event):
    """Команда /list_users — список всех пользователей."""
    user_id = event.from_chat
    
    try:
        rows = DatabaseSync.fetchall(
            """
            SELECT user_id, full_name, role, created_at, is_active 
            FROM users 
            ORDER BY role, created_at
            """
        )
        
        if not rows:
            bot.send_text(
                chat_id=user_id,
                text=f"{Emoji.EMPTY} Пользователей пока нет.",
                parse_mode="HTML"
            )
            return
        
        roles = {}
        for row in rows:
            u_id, full_name, role, created_at, is_active = row
            if role not in roles:
                roles[role] = []
            roles[role].append((u_id, full_name, is_active))
        
        lines = [f"{Emoji.USERS} <b>Список пользователей</b>", ""]
        
        for role, users_list in sorted(roles.items()):
            lines.append(f"<b>{role.upper()}</b> ({len(users_list)} чел.):")
            for u_id, name, active in users_list:
                status = "🟢" if active else "🔴"
                display_name = name or u_id.split('@')[0]
                lines.append(f"   {status} {display_name} — <code>{u_id}</code>")
            lines.append("")
        
        lines.append("━━━━━━━━━━━━━━━━━━━━━")
        lines.append(f"{Emoji.INFO} Всего: {len(rows)} пользователей")
        
        bot.send_text(
            chat_id=user_id,
            text="\n".join(lines),
            parse_mode="HTML"
        )
        
    except Exception as e:
        print(f"❌ Ошибка в list_users_handler: {e}")
        import traceback
        traceback.print_exc()
        bot.send_text(
            chat_id=user_id,
            text=f"{Emoji.ERROR} Ошибка: {e}",
            parse_mode="HTML"
        )