# src/core/constants.py
"""
Общие константы проекта OTSKVM VK Teams Bot.

Назначение модуля:
- собрать в одном месте все строковые константы (статусы, роли, типы уведомлений);
- исключить «магические строки» в SQL‑запросах и бизнес‑логике;
- упростить поиск мест использования при изменении бизнес‑правил.

Группы констант:
- статусы аудиторий (`STATUS_*`, `AUDITORY_STATUSES`);
- статусы назначений мероприятий (`ASSIGNMENT_STATUS_*`, `ASSIGNMENT_STATUSES_ACTIVE`);
- роли пользователей (`ROLE_*`, `ALL_ROLES`);
- типы уведомлений (`NOTIFICATION_*`);
- статусы событий календаря (`EVENT_STATUS_*`);
- команды бота (`COMMAND_*`);
- emoji для форматирования.
"""

from typing import Tuple
from typing_extensions import Final


# ============================================================
# СТАТУСЫ АУДИТОРИЙ
# ============================================================

STATUS_GREEN: Final[str] = "green"
STATUS_YELLOW: Final[str] = "yellow"
STATUS_RED: Final[str] = "red"

AUDITORY_STATUSES: Final[Tuple[str, ...]] = (
    STATUS_GREEN,
    STATUS_YELLOW,
    STATUS_RED,
)


# ============================================================
# СТАТУСЫ НАЗНАЧЕНИЙ МЕРОПРИЯТИЙ
# ============================================================

ASSIGNMENT_STATUS_ASSIGNED: Final[str] = "assigned"
ASSIGNMENT_STATUS_ACCEPTED: Final[str] = "accepted"
ASSIGNMENT_STATUS_DONE: Final[str] = "done"
ASSIGNMENT_STATUS_CANCELLED: Final[str] = "cancelled"
ASSIGNMENT_STATUS_REPLACING: Final[str] = "replacing"
ASSIGNMENT_STATUS_REPLACEMENT_REQUESTED: Final[str] = "replacement_requested"

ASSIGNMENT_STATUSES_ACTIVE: Final[Tuple[str, ...]] = (
    ASSIGNMENT_STATUS_ASSIGNED,
    ASSIGNMENT_STATUS_ACCEPTED,
    ASSIGNMENT_STATUS_REPLACING,
)


# ============================================================
# РОЛИ ПОЛЬЗОВАТЕЛЕЙ
# ============================================================

ROLE_SUPERADMIN: Final[str] = "superadmin"
ROLE_ADMIN: Final[str] = "admin"
ROLE_MANAGER: Final[str] = "manager"
ROLE_ENGINEER: Final[str] = "engineer"
ROLE_VIEWER: Final[str] = "viewer"

ALL_ROLES: Final[Tuple[str, ...]] = (
    ROLE_SUPERADMIN,
    ROLE_ADMIN,
    ROLE_MANAGER,
    ROLE_ENGINEER,
    ROLE_VIEWER,
)


# ============================================================
# ТИПЫ УВЕДОМЛЕНИЙ
# ============================================================

NOTIFICATION_REMINDER: Final[str] = "reminder"
NOTIFICATION_COMPLETION_REMINDER: Final[str] = "completion_reminder"
NOTIFICATION_CONFIRMATION: Final[str] = "confirmation"
NOTIFICATION_MANUAL_COMPLETION: Final[str] = "manual_completion"
NOTIFICATION_EARLY_COMPLETION: Final[str] = "early_completion"


# ============================================================
# СТАТУСЫ СОБЫТИЙ КАЛЕНДАРЯ (добавлено для нового функционала)
# ============================================================

EVENT_STATUS_CONFIRMED: Final[str] = "confirmed"
EVENT_STATUS_CANCELLED: Final[str] = "cancelled"
EVENT_STATUS_TENTATIVE: Final[str] = "tentative"

EVENT_STATUSES: Final[Tuple[str, ...]] = (
    EVENT_STATUS_CONFIRMED,
    EVENT_STATUS_CANCELLED,
    EVENT_STATUS_TENTATIVE,
)

EVENT_STATUSES_ACTIVE: Final[Tuple[str, ...]] = (
    EVENT_STATUS_CONFIRMED,
    EVENT_STATUS_TENTATIVE,
)


# ============================================================
# КОМАНДЫ БОТА
# ============================================================

class Commands:
    """Контейнер для команд бота"""
    
    # Основные команды
    START: Final[str] = "/start"
    HELP: Final[str] = "/help"
    
    # Команды календаря
    TODAY: Final[str] = "/today"
    TOMORROW: Final[str] = "/tomorrow"
    WEEK: Final[str] = "/week"
    SYNC: Final[str] = "/sync"
    
    # Команды аудиторий
    STATUS: Final[str] = "/status"
    SET_STATUS: Final[str] = "/set_status"
    
    # Команды назначений
    ASSIGN: Final[str] = "/assign"
    MY_TASKS: Final[str] = "/my_tasks"
    MY_ASSIGNMENTS: Final[str] = "/my_assignments"
    
    # Админские команды
    ADMIN: Final[str] = "/admin"
    STATS: Final[str] = "/stats"
    USERS: Final[str] = "/users"


# ============================================================
# EMOJI ДЛЯ ФОРМАТИРОВАНИЯ
# ============================================================

class Emoji:
    """Контейнер для emoji"""
    
    # Календарь и время
    CALENDAR: Final[str] = "📅"
    TODAY: Final[str] = "📆"
    TOMORROW: Final[str] = "➡️"
    WEEK: Final[str] = "📊"
    TIME: Final[str] = "🕐"
    CLOCK: Final[str] = "⏰"
    
    # События и описание
    EVENT: Final[str] = "📌"
    LOCATION: Final[str] = "📍"
    ORGANIZER: Final[str] = "👤"
    DESCRIPTION: Final[str] = "📝"
    LINK: Final[str] = "🔗"
    
    # Статусы
    GREEN: Final[str] = "🟢"
    YELLOW: Final[str] = "🟡"
    RED: Final[str] = "🔴"
    CHECK: Final[str] = "✅"
    CROSS: Final[str] = "❌"
    WARNING: Final[str] = "⚠️"
    
    # Общие
    INFO: Final[str] = "ℹ️"
    HELP: Final[str] = "❓"
    SETTINGS: Final[str] = "⚙️"
    SYNC: Final[str] = "🔄"
    SUCCESS: Final[str] = "🎉"
    ERROR: Final[str] = "🚫"
    EMPTY: Final[str] = "📭"
    SEARCH: Final[str] = "🔍"
    USER: Final[str] = "👤"
    USERS: Final[str] = "👥"
    CHAT: Final[str] = "💬"
    LOCK: Final[str] = "🔒"
    UNLOCK: Final[str] = "🔓"
    KEY: Final[str] = "🔑"
    FILE: Final[str] = "📄"
    FOLDER: Final[str] = "📁"
    PIN: Final[str] = "📌"
    STAR: Final[str] = "⭐"
    FIRE: Final[str] = "🔥"


# ============================================================
# ТИПЫ ЧАТОВ VK WORKSPACE
# ============================================================

class ChatType:
    """Типы чатов в VK Workspace"""
    
    PRIVATE: Final[str] = "private"
    GROUP: Final[str] = "group"
    UNKNOWN: Final[str] = "unknown"


# ============================================================
# НАСТРОЙКИ ПО УМОЛЧАНИЮ
# ============================================================

class Defaults:
    """Настройки по умолчанию"""
    
    TIMEZONE: Final[str] = "Europe/Moscow"
    SYNC_INTERVAL_HOURS: Final[int] = 6
    DAYS_AHEAD_FOR_SYNC: Final[int] = 30
    DAYS_BACK_FOR_SYNC: Final[int] = 7
    MAX_EVENTS_PER_REQUEST: Final[int] = 500
    
    # Лимиты для отображения
    MAX_EVENTS_TO_SHOW: Final[int] = 50
    MAX_DESCRIPTION_LENGTH: Final[int] = 200
    MAX_TITLE_LENGTH: Final[int] = 100