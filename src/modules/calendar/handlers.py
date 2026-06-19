# src/modules/calendar/handlers.py

import asyncio
import json
from datetime import datetime, timedelta
import pytz
from src.core.google_client import GoogleCalendarClient
from src.core.database import Database
from src.core.constants import Commands, Emoji, Defaults
from .sync import sync_calendar
from src.modules.menu.handlers import _active_messages, send_or_edit, get_main_menu_keyboard
from src.core.db_sync import DatabaseSync


# Глобальные переменные
_calendar_client = None
_loop = None

# Словарь для перевода дней недели на русский
WEEKDAYS_RU = {
    'Monday': 'Понедельник',
    'Tuesday': 'Вторник',
    'Wednesday': 'Среда',
    'Thursday': 'Четверг',
    'Friday': 'Пятница',
    'Saturday': 'Суббота',
    'Sunday': 'Воскресенье'
}


def get_event_loop():
    global _loop
    if _loop is None or _loop.is_closed():
        _loop = asyncio.new_event_loop()
        asyncio.set_event_loop(_loop)
    return _loop


def run_async(coro):
    loop = get_event_loop()
    if loop.is_running():
        future = asyncio.run_coroutine_threadsafe(coro, loop)
        return future.result()
    else:
        return loop.run_until_complete(coro)


def setup(bot, module_manager):
    global _calendar_client
    
    print("📦 Модуль 'calendar' загружается...")
    
    try:
        _calendar_client = GoogleCalendarClient()
    except FileNotFoundError as e:
        print(f"⚠️ {e}")
        return
    except Exception as e:
        print(f"⚠️ Ошибка подключения к Google Calendar: {e}")
        return
    
    module_manager.register_command(Commands.TODAY, today_handler, 'calendar')
    module_manager.register_command(Commands.TOMORROW, tomorrow_handler, 'calendar')
    module_manager.register_command(Commands.WEEK, week_handler, 'calendar')
    module_manager.register_command(Commands.SYNC, sync_handler, 'calendar')
    
    module_manager.register_callback('today', today_callback, 'calendar')
    module_manager.register_callback('tomorrow', tomorrow_callback, 'calendar')
    module_manager.register_callback('week', week_callback, 'calendar')
    module_manager.register_callback('sync', sync_callback, 'calendar')
    module_manager.register_callback('main_menu', main_menu_callback, 'calendar')
    
    print("✅ Модуль 'calendar' загружен")


def get_calendar_keyboard():
    """Создаёт клавиатуру календаря."""
    return [
        [
            {"text": "📅 Сегодня", "callbackData": "today", "style": "primary"}
        ],
        [
            {"text": "➡️ Завтра", "callbackData": "tomorrow", "style": "primary"}
        ],
        [
            {"text": "📆 Неделя", "callbackData": "week", "style": "primary"}
        ],
        [
            {"text": "🔄 Синхронизация", "callbackData": "sync", "style": "positive"}
        ],
        [
            {"text": "◀️ В главное меню", "callbackData": "main_menu", "style": "secondary"}
        ]
    ]


def show_calendar(bot, event, period, period_name):
    """Показывает календарь с редактированием существующего сообщения."""
    chat_id = event.from_chat
    print(f"🔍 show_calendar: period={period}, period_name={period_name}")
    
    try:
        tz = pytz.timezone(Defaults.TIMEZONE)
        now = datetime.now(tz)
        
        if period == 'today':
            start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end = start + timedelta(days=1)
        elif period == 'tomorrow':
            start = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
            end = start + timedelta(days=1)
        elif period == 'week':
            start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end = start + timedelta(days=7)
        else:
            return
        
        start_utc = start.astimezone(pytz.UTC).replace(tzinfo=None)
        end_utc = end.astimezone(pytz.UTC).replace(tzinfo=None)
        
        events = run_async(get_events_from_db(start_utc, end_utc))
        
        if not events:
            text = f"{Emoji.EMPTY} На {period_name} мероприятий нет."
        elif period == 'week':
            text = format_week_events(events, tz)
        else:
            text = format_events(events, period_name, tz)
        
        keyboard = get_calendar_keyboard()
        msg_id = _active_messages.get(chat_id)
        
        new_msg_id = send_or_edit(
            bot,
            chat_id,
            text,
            keyboard,
            msg_id
        )
        
        if new_msg_id:
            _active_messages[chat_id] = new_msg_id
            print(f"   ✅ Сохранён новый msgId: {new_msg_id}")
        
    except Exception as e:
        print(f"   ❌ Ошибка в show_calendar: {e}")
        import traceback
        traceback.print_exc()
        bot.send_text(
            chat_id=chat_id,
            text=f"{Emoji.ERROR} Ошибка: {e}"
        )


# ============ Обработчики команд ============

def today_handler(bot, event):
    show_calendar(bot, event, 'today', 'сегодня')


def tomorrow_handler(bot, event):
    show_calendar(bot, event, 'tomorrow', 'завтра')


def week_handler(bot, event):
    show_calendar(bot, event, 'week', 'неделю')


def sync_handler(bot, event):
    """Команда /sync — принудительная синхронизация (резервный вариант)."""
    user_id = event.from_chat
    
    # Проверка прав
    row = DatabaseSync.fetchone(
        "SELECT role FROM users WHERE user_id = %s",
        (user_id,)
    )
    role = row[0] if row else 'viewer'
    
    if role not in ['admin', 'superadmin']:
        bot.send_text(
            chat_id=user_id,
            text=f"{Emoji.ERROR} ⛔ Доступ запрещён.\n\n"
                 f"Синхронизация доступна только для администраторов.\n"
                 f"Ваша роль: <b>{role}</b>",
            parse_mode="HTML"
        )
        return
    
    bot.send_text(
        chat_id=user_id,
        text=f"{Emoji.SYNC} Запускаю синхронизацию..."
    )
    
    try:
        result = run_async(sync_calendar())
        
        message = f"{Emoji.SUCCESS} *Синхронизация завершена!*\n\n"
        message += f"📊 Получено событий: {result['total']}\n"
        message += f"💾 Сохранено в БД: {result['saved']}"
        
        bot.send_text(
            chat_id=user_id,
            text=message,
            parse_mode="MarkdownV2"
        )
        
        show_calendar(bot, event, 'today', 'сегодня')
        
    except Exception as e:
        bot.send_text(
            chat_id=user_id,
            text=f"{Emoji.ERROR} Ошибка синхронизации: {e}"
        )


# ============ Обработчики callback ============

def today_callback(bot, event):
    today_handler(bot, event)


def tomorrow_callback(bot, event):
    tomorrow_handler(bot, event)


def week_callback(bot, event):
    week_handler(bot, event)


def sync_callback(bot, event):
    """
    Обработчик нажатия на кнопку 'Синхронизация'.
    Показывает модальное окно с результатом (без промежуточного уведомления).
    """
    user_id = event.from_chat
    
    # Проверка прав
    row = DatabaseSync.fetchone(
        "SELECT role FROM users WHERE user_id = %s",
        (user_id,)
    )
    role = row[0] if row else 'viewer'
    
    if role not in ['admin', 'superadmin']:
        bot.answer_callback_query(
            query_id=event.data['queryId'],
            text="⛔ Доступ запрещён. Только для администраторов.",
            show_alert=True
        )
        return
    
    # Запускаем синхронизацию
    try:
        result = run_async(sync_calendar())
        
        # Обновляем календарь
        show_calendar(bot, event, 'today', 'сегодня')
        
        # Модальное окно с результатом
        message = f"✅ Синхронизация завершена!\n\n"
        message += f"📊 Получено: {result['total']} событий\n"
        message += f"💾 Сохранено: {result['saved']} событий"
        
        bot.answer_callback_query(
            query_id=event.data['queryId'],
            text=message,
            show_alert=True  # <-- Модальное окно
        )
        
    except Exception as e:
        bot.answer_callback_query(
            query_id=event.data['queryId'],
            text=f"❌ Ошибка: {str(e)[:100]}",
            show_alert=True
        )
        print(f"   ❌ Ошибка синхронизации: {e}")
        import traceback
        traceback.print_exc()


def main_menu_callback(bot, event):
    """Обработчик кнопки 'В главное меню'."""
    from src.modules.menu.handlers import get_main_menu_text, get_main_menu_keyboard, send_or_edit, _active_messages
    
    user_id = event.from_chat
    msg_id = _active_messages.get(user_id)
    
    text = get_main_menu_text(user_id)
    keyboard = get_main_menu_keyboard(user_id)
    
    new_msg_id = send_or_edit(
        bot,
        user_id,
        text,
        keyboard,
        msg_id
    )
    
    if new_msg_id:
        _active_messages[user_id] = new_msg_id


# ============ Работа с БД ============

async def get_events_from_db(start_utc, end_utc):
    pool = await Database.get_pool()
    
    async with pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT 
                ce.google_event_id, 
                ce.title, 
                ce.description,
                ce.start_time, 
                ce.end_time, 
                ce.organizer, 
                ce.status,
                a.name AS auditory_name,
                a.building AS auditory_building
            FROM calendar_events ce
            LEFT JOIN auditories a ON ce.auditory_id = a.id
            WHERE ce.start_time >= $1 AND ce.start_time < $2
              AND ce.status != 'cancelled'
            ORDER BY ce.start_time ASC
        """, start_utc, end_utc)
        
        return [dict(row) for row in rows]


# ============ Форматирование ============

def format_events(events, period_name, tz):
    if not events:
        return f"{Emoji.EMPTY} На {period_name} мероприятий нет."
    
    lines = [f"{Emoji.CALENDAR} *События на {period_name}*", ""]
    
    for ev in events:
        title = ev.get('title', 'Без названия')
        
        start_time = ev['start_time']
        if start_time.tzinfo is None:
            start_time = pytz.UTC.localize(start_time)
        start_local = start_time.astimezone(tz)
        
        lines.append(f"{Emoji.TIME} *{start_local.strftime('%H:%M')}* — {title}")
        
        auditory_name = ev.get('auditory_name')
        if auditory_name:
            auditory_building = ev.get('auditory_building', '')
            if auditory_building:
                lines.append(f"   {Emoji.LOCATION} {auditory_name} ({auditory_building})")
            else:
                lines.append(f"   {Emoji.LOCATION} {auditory_name}")
        
        lines.append("")
    
    lines.append("━━━━━━━━━━━━━━━━━━━━━")
    lines.append(f"{Emoji.INFO} Итого: {len(events)} мероприятий")
    
    return "\n".join(lines)


def format_week_events(events, tz):
    if not events:
        return f"{Emoji.EMPTY} На неделю мероприятий нет."
    
    days = {}
    for ev in events:
        start_time = ev['start_time']
        if start_time.tzinfo is None:
            start_time = pytz.UTC.localize(start_time)
        start_local = start_time.astimezone(tz)
        
        day_en = start_local.strftime('%A')
        day_ru = WEEKDAYS_RU.get(day_en, day_en)
        day_key = f"{start_local.strftime('%d.%m')} ({day_ru})"
        
        if day_key not in days:
            days[day_key] = []
        days[day_key].append(ev)
    
    lines = [f"{Emoji.WEEK} *События на неделю*", ""]
    for day_name, day_events in sorted(days.items()):
        lines.append(f"*{day_name}*")
        for ev in day_events:
            start_time = ev['start_time']
            if start_time.tzinfo is None:
                start_time = pytz.UTC.localize(start_time)
            start_local = start_time.astimezone(tz)
            
            title = ev.get('title', 'Без названия')
            line = f"   {Emoji.TIME} *{start_local.strftime('%H:%M')}* — {title}"
            lines.append(line)
            
            auditory_name = ev.get('auditory_name')
            if auditory_name:
                auditory_building = ev.get('auditory_building', '')
                if auditory_building:
                    lines.append(f"      {Emoji.LOCATION} {auditory_name} ({auditory_building})")
                else:
                    lines.append(f"      {Emoji.LOCATION} {auditory_name}")
        lines.append("")
    
    return "\n".join(lines)