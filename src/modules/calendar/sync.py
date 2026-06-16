# src/modules/calendar/sync.py

from src.core.google_client import calendar_client


async def sync_calendar(days: int = 30) -> dict:
    """
    Синхронизирует календарь с базой данных.
    
    Args:
        days: количество дней вперёд для синхронизации
        
    Returns:
        dict: статистика синхронизации
    """
    try:
        events = await calendar_client.fetch_events(days)
        
        if not events:
            return {'total': 0, 'saved': 0}
        
        saved = await calendar_client.save_events_to_db(events)
        
        return {'total': len(events), 'saved': saved}
        
    except Exception as e:
        print(f"❌ Ошибка при синхронизации календаря: {e}")
        raise