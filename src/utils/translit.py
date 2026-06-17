"""Утилиты для работы с транслитерацией между кириллицей и латиницей.

Задачи модуля:
- предоставить единообразный способ транслитерации, независимо от того,
  где именно вызывается конвертация в коде;
- централизованно обрабатывать редкие ошибки библиотеки `cyrtranslit`,
  не ломая основные сценарии бота;
- гарантировать, что в случае любой ошибки пользователь увидит исходный
  текст, а не traceback.
"""

import logging
from typing import Optional

import cyrtranslit

logger = logging.getLogger(__name__)


def to_cyrillic(text: Optional[str]) -> str:
    """
    Безопасно конвертирует строку в кириллицу.
    
    Аргументы:
        text: исходная строка (как правило, из календаря или внешней системы).
    
    Возвращает:
        Строку в кириллице.
        Если `text is None` — пустую строку.
        Если при конвертации произошла ошибка — исходный текст.
    """
    if text is None:
        return ""
    try:
        return cyrtranslit.to_cyrillic(text)
    except Exception as exc:
        logger.error("Ошибка транслитерации в кириллицу: %s", exc)
        return text


def to_latin(text: Optional[str]) -> str:
    """
    Безопасно конвертирует строку в латиницу.
    
    Аргументы:
        text: исходная строка (чаще всего кириллическая).
    
    Возвращает:
        Строку в латинице.
        Если `text is None` — пустую строку.
        Если при конвертации произошла ошибка — исходный текст.
    """
    if text is None:
        return ""
    try:
        return cyrtranslit.to_latin(text)
    except Exception as exc:
        logger.error("Ошибка транслитерации в латиницу: %s", exc)
        return text