# src/core/google_client.py

import pickle
import os
import datetime
import pytz
from typing import List, Dict, Any, Optional
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv
from dateutil import parser

from src.core.database import Database

from src.utils.auditory_normalizer import AuditoryNormalizer

load_dotenv()

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
TOKEN_FILE = 'token.pickle'
CREDENTIALS_FILE = 'credentials.json'


class GoogleCalendarClient:
    """Клиент для работы с Google Calendar API."""
    
    def __init__(self, credentials_file=CREDENTIALS_FILE):
        self.credentials_file = credentials_file
        self.calendar_id = os.getenv('GOOGLE_CALENDAR_ID', 'primary')
        self.service = self._authenticate()
    
    def _authenticate(self):
        """Аутентификация через OAuth 2.0."""
        creds = None
        
        if os.path.exists(TOKEN_FILE):
            try:
                with open(TOKEN_FILE, 'rb') as token:
                    creds = pickle.load(token)
            except:
                pass
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(self.credentials_file):
                    raise FileNotFoundError(
                        f"Файл {self.credentials_file} не найден!\n"
                        "Скачайте его из Google Cloud Console"
                    )
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, SCOPES
                )
                creds = flow.run_local_server(port=0)
            
            with open(TOKEN_FILE, 'wb') as token:
                pickle.dump(creds, token)
        
        return build('calendar', 'v3', credentials=creds)
    
    async def fetch_events(self, days: int = 30) -> List[Dict[str, Any]]:
        """
        Получает события из календаря на указанное количество дней вперёд.
        
        Args:
            days: количество дней от сегодня
            
        Returns:
            Список событий
        """
        try:
            now = datetime.datetime.now(datetime.timezone.utc)
            time_min = now.isoformat()
            time_max = (now + datetime.timedelta(days=days)).isoformat()
            
            events_result = self.service.events().list(
                calendarId=self.calendar_id,
                timeMin=time_min,
                timeMax=time_max,
                singleEvents=True,
                orderBy="startTime"
            ).execute()
            
            return events_result.get("items", [])
            
        except HttpError as error:
            print(f"❌ Ошибка при получении событий: {error}")
            return []
    
    def _parse_datetime(self, date_str: str):
        """
        Парсит дату из строки в datetime объект (без часового пояса, в UTC).
        """
        try:
            dt = parser.parse(date_str)
            if dt.tzinfo is not None:
                dt = dt.astimezone(pytz.UTC)
            return dt.replace(tzinfo=None)
        except Exception:
            return None
    
    def _extract_auditory_from_event(self, event: Dict) -> Optional[str]:
        """
        Извлекает название аудитории из события.
        Ищет только в поле location (самое надёжное место).
        """
        location = event.get("location", "")
        if location and location.strip():
            return location.strip()
        
        return None
    
    async def _find_auditory_id(self, raw_name: str, pool) -> Optional[int]:
        """
        Находит ID аудитории по названию с использованием нормализации.
        
        Алгоритм:
        1. Проверка на пустое название.
        2. Прямой поиск в БД по названию (ILIKE).
        3. Нормализация через AuditoryNormalizer.
        4. Повторный поиск по нормализованному названию.
        5. Логирование ненайденных аудиторий для пополнения словаря.
        """
        name = (raw_name or "").strip()
        if not name:
            return None
        
        # 1. Прямой поиск (оригинальное название)
        row = await pool.fetchrow(
            "SELECT id FROM auditories WHERE name ILIKE $1",
            f"%{name}%",
        )
        if row:
            return row["id"]
        
        # 2. Нормализация названия
        normalized = AuditoryNormalizer.normalize(name)
        
        # Если нормализация изменила название — пробуем найти снова
        if normalized != name:
            row = await pool.fetchrow(
                "SELECT id FROM auditories WHERE name = $1",
                normalized,
            )
            if row:
                print(f"   🏫 Найдена аудитория по нормализованному названию: '{name}' -> '{normalized}' (ID: {row['id']})")
                return row["id"]
        
        # 3. Если не найдено — логируем для пополнения словаря
        print(f"   ⚠️ Аудитория не найдена: '{name}' (нормализовано: '{normalized}')")
        return None
    
    async def save_events_to_db(self, events: List[Dict[str, Any]]) -> int:
        """
        Сохраняет полученные из Google Calendar события в базу данных.
        
        Returns:
            int: количество сохранённых событий
        """
        pool = await Database.get_pool()
        saved_count = 0
        
        for event in events:
            try:
                start_str = event["start"].get("dateTime", event["start"].get("date"))
                end_str = event["end"].get("dateTime", event["end"].get("date"))
                
                start = self._parse_datetime(start_str)
                end = self._parse_datetime(end_str)
                
                if start is None or end is None:
                    continue
                
                title = event.get("summary", "Без названия")
                
                auditory_name = self._extract_auditory_from_event(event)
                auditory_id = None
                if auditory_name:
                    auditory_id = await self._find_auditory_id(auditory_name, pool)
                
                await pool.execute(
                    """
                    INSERT INTO calendar_events 
                    (google_event_id, auditory_id, title, description, 
                     start_time, end_time, organizer, status, last_sync)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, NOW())
                    ON CONFLICT (google_event_id) DO UPDATE SET
                        auditory_id = EXCLUDED.auditory_id,
                        title = EXCLUDED.title,
                        description = EXCLUDED.description,
                        start_time = EXCLUDED.start_time,
                        end_time = EXCLUDED.end_time,
                        organizer = EXCLUDED.organizer,
                        status = EXCLUDED.status,
                        last_sync = NOW()
                    """,
                    event["id"],
                    auditory_id,
                    title,
                    event.get("description", ""),
                    start,
                    end,
                    event.get("organizer", {}).get("email", ""),
                    event.get("status", "confirmed")
                )
                
                saved_count += 1
                
            except Exception:
                # Пропускаем событие при ошибке
                pass
        
        return saved_count


# Создаём глобальный экземпляр клиента
calendar_client = GoogleCalendarClient()