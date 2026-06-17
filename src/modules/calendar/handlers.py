# src/modules/calendar/handlers.py

import asyncio
from datetime import datetime, timedelta
import pytz
from src.core.google_client import GoogleCalendarClient
from src.core.database import Database
from src.core.constants import Commands, Emoji, Defaults
from .sync import sync_calendar

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
    """Получение или создание event loop"""
    global _loop
    if _loop is None or _loop.is_closed():
        _loop = asyncio.new_event_loop()
        asyncio.set_event_loop(_loop)
    return _loop


def run_async(coro):
    """Запускает асинхронную функцию в общем event loop"""
    loop = get_event_loop()
    if loop.is_running():
        future = asyncio.run_coroutine_threadsafe(coro, loop)
        return future.result()
    else:
        return loop.run_until_complete(coro)


def setup(bot, module_manager):
    """Инициализация модуля календаря"""
    global _calendar_client
    
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
    
    print("✅ Модуль 'calendar' загружен")


def today_handler(bot, event):
    """Команда /today — события на сегодня"""
    try:
        tz = pytz.timezone(Defaults.TIMEZONE)
        now = datetime.now(tz)
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=1)
        
        start_utc = start.astimezone(pytz.UTC).replace(tzinfo=None)
        end_utc = end.astimezone(pytz.UTC).replace(tzinfo=None)
        
        events = run_async(get_events_from_db(start_utc, end_utc))
        
        if not events:
            bot.send_text(
                chat_id=event.from_chat,
                text=f"{Emoji.EMPTY} На сегодня мероприятий нет.",
                parse_mode="HTML"
            )
            return
        
        message = format_events(events, "сегодня", tz)
        bot.send_text(
            chat_id=event.from_chat,
            text=message,
            parse_mode="HTML"
        )
        
    except Exception as e:
        bot.send_text(
            chat_id=event.from_chat,
            text=f"{Emoji.ERROR} Ошибка: {e}",
            parse_mode="HTML"
        )


def tomorrow_handler(bot, event):
    """Команда /tomorrow — события на завтра"""
    try:
        tz = pytz.timezone(Defaults.TIMEZONE)
        now = datetime.now(tz)
        start = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=1)
        
        start_utc = start.astimezone(pytz.UTC).replace(tzinfo=None)
        end_utc = end.astimezone(pytz.UTC).replace(tzinfo=None)
        
        events = run_async(get_events_from_db(start_utc, end_utc))
        
        if not events:
            bot.send_text(
                chat_id=event.from_chat,
                text=f"{Emoji.EMPTY} На завтра мероприятий нет.",
                parse_mode="HTML"
            )
            return
        
        message = format_events(events, "завтра", tz)
        bot.send_text(
            chat_id=event.from_chat,
            text=message,
            parse_mode="HTML"
        )
        
    except Exception as e:
        bot.send_text(
            chat_id=event.from_chat,
            text=f"{Emoji.ERROR} Ошибка: {e}",
            parse_mode="HTML"
        )


def week_handler(bot, event):
    """Команда /week — события на неделю с аудиториями"""
    try:
        tz = pytz.timezone(Defaults.TIMEZONE)
        now = datetime.now(tz)
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=7)
        
        start_utc = start.astimezone(pytz.UTC).replace(tzinfo=None)
        end_utc = end.astimezone(pytz.UTC).replace(tzinfo=None)
        
        events = run_async(get_events_from_db(start_utc, end_utc))
        
        if not events:
            bot.send_text(
                chat_id=event.from_chat,
                text=f"{Emoji.EMPTY} На ближайшую неделю мероприятий нет.",
                parse_mode="HTML"
            )
            return
        
        # Группируем по дням
        days = {}
        for ev in events:
            start_time = ev['start_time']
            if start_time.tzinfo is None:
                start_time = pytz.UTC.localize(start_time)
            start_local = start_time.astimezone(tz)
            day_key = start_local.strftime('%d.%m (%A)')
            if day_key not in days:
                days[day_key] = []
            days[day_key].append(ev)
        
        lines = [f"{Emoji.WEEK} <b>События на неделю</b>", ""]
        for day_name, day_events in sorted(days.items()):
            lines.append(f"<b>{day_name}</b>")
            for ev in day_events:
                start_time = ev['start_time']
                if start_time.tzinfo is None:
                    start_time = pytz.UTC.localize(start_time)
                start_local = start_time.astimezone(tz)
                
                title = ev.get('title', 'Без названия')
                line = f"   {Emoji.TIME} <b>{start_local.strftime('%H:%M')}</b> — {title}"
                lines.append(line)
                
                # Добавляем аудиторию, если есть
                auditory_name = ev.get('auditory_name')
                if auditory_name:
                    auditory_building = ev.get('auditory_building', '')
                    if auditory_building:
                        lines.append(f"      {Emoji.LOCATION} {auditory_name} ({auditory_building})")
                    else:
                        lines.append(f"      {Emoji.LOCATION} {auditory_name}")
            lines.append("")
        
        bot.send_text(
            chat_id=event.from_chat,
            text="\n".join(lines),
            parse_mode="HTML"
        )
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        bot.send_text(
            chat_id=event.from_chat,
            text=f"{Emoji.ERROR} Ошибка: {e}",
            parse_mode="HTML"
        )


def sync_handler(bot, event):
    """Команда /sync — принудительная синхронизация"""
    bot.send_text(
        chat_id=event.from_chat,
        text=f"{Emoji.SYNC} Запускаю синхронизацию с Google Calendar...",
        parse_mode="HTML"
    )
    
    try:
        result = run_async(sync_calendar())
        
        message = f"{Emoji.SUCCESS} <b>Синхронизация завершена!</b>\n\n"
        message += f"📊 Получено событий: {result['total']}\n"
        message += f"💾 Сохранено в БД: {result['saved']}"
        
        bot.send_text(
            chat_id=event.from_chat,
            text=message,
            parse_mode="HTML"
        )
        
    except Exception as e:
        bot.send_text(
            chat_id=event.from_chat,
            text=f"{Emoji.ERROR} Ошибка синхронизации: {e}",
            parse_mode="HTML"
        )


async def get_events_from_db(start_utc, end_utc):
    """Получение событий из БД за период (в UTC) с информацией об аудиториях"""
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


def format_events(events, period_name, tz):
    """Форматирует события с информацией об аудиториях и зданиях"""
    if not events:
        return f"{Emoji.EMPTY} На {period_name} мероприятий нет."
    
    lines = [f"{Emoji.CALENDAR} <b>События на {period_name}</b>", ""]
    
    for ev in events:
        title = ev.get('title', 'Без названия')
        
        # Время
        start_time = ev['start_time']
        if start_time.tzinfo is None:
            start_time = pytz.UTC.localize(start_time)
        start_local = start_time.astimezone(tz)
        
        # Строка с временем и названием события
        lines.append(f"{Emoji.TIME} <b>{start_local.strftime('%H:%M')}</b> — {title}")
        
        # Строка с аудиторией (если есть)
        auditory_name = ev.get('auditory_name')
        if auditory_name:
            auditory_building = ev.get('auditory_building', '')
            if auditory_building:
                lines.append(f"   {Emoji.LOCATION} {auditory_name} ({auditory_building})")
            else:
                lines.append(f"   {Emoji.LOCATION} {auditory_name}")
        
        lines.append("")  # Пустая строка между событиями
    
    lines.append("━━━━━━━━━━━━━━━━━━━━━")
    lines.append(f"{Emoji.INFO} Итого: {len(events)} мероприятий")
    
    return "\n".join(lines)