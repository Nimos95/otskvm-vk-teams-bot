# 🤖 OTSKVM VK Teams Bot

Бот для учёта состояния аудиторий и интеграции с Google Calendar в VK Workspace.

[![Python](https://img.shields.io/badge/Python-3.6-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![VK Teams](https://img.shields.io/badge/VK%20Teams-Bot%20API-0077FF?style=for-the-badge&logo=vk&logoColor=white)](https://teams.vk.com/botapi/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-18-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)](https://postgresql.org)
[![Google Calendar](https://img.shields.io/badge/Google%20Calendar-API-4285F4?style=for-the-badge&logo=google&logoColor=white)](https://developers.google.com/calendar)

---

## 📋 О проекте

**OTSKVM VK Teams Bot** — бот для инженеров технического сопровождения конгрессно-выставочных мероприятий СПбПУ. Бот позволяет быстро отмечать состояние аудиторий, отслеживать проблемы, координировать работу и интегрироваться с Google Calendar.

Проект разработан для автоматизации процессов отдела и перехода от реактивного обслуживания к проактивному управлению инфраструктурой.

---

## 🎯 Возможности

### ✅ Реализовано

#### 📅 **Интеграция с Google Calendar**
- ✅ Команда `/today` — мероприятия на сегодня
- ✅ Команда `/tomorrow` — мероприятия на завтра
- ✅ Команда `/week` — мероприятия на неделю с группировкой по дням
- ✅ Команда `/sync` — принудительная синхронизация с Google Calendar
- ✅ Автоматическое кэширование событий в PostgreSQL
- ✅ Поддержка событий на целый день и с конкретным временем
- ✅ Русские названия дней недели
- ✅ HTML-форматирование (жирный шрифт)

#### 🏛️ **Привязка событий к аудиториям**
- ✅ Автоматическое извлечение названия аудитории из `location` события
- ✅ Нормализация названий через словарь синонимов
- ✅ Отображение аудитории и здания в сообщениях
- ✅ Логирование ненайденных аудиторий для пополнения словаря

#### 🏗️ **Архитектура**
- ✅ Модульная структура (легко добавлять новые функции)
- ✅ Фильтрация чатов (личные vs групповые)
- ✅ База данных PostgreSQL с пулом соединений
- ✅ Безопасная обработка сигналов (корректный Ctrl+C)

---

## 🛠 Технологический стек

| Компонент | Технология | Версия |
|-----------|------------|--------|
| **Язык программирования** | Python | 3.6 |
| **VK Teams Bot API** | mailru-im-bot | latest |
| **База данных** | PostgreSQL | 18.x |
| **Асинхронный драйвер** | asyncpg | 0.30.0 |
| **Google Calendar API** | google-api-python-client | 1.12.8 |
| **Парсинг дат** | python-dateutil | 2.8.2 |
| **Транслитерация** | cyrtranslit | 0.9.2 |
| **Конфигурация** | python-dotenv | 1.0.0 |

---

## 🚀 Установка и запуск

### Требования
- Python 3.6+
- PostgreSQL 18+
- VK Workspace аккаунт с правами на создание бота
- Google Cloud проект с включённым Calendar API

### Установка

1. Клонируйте репозиторий:
```bash
git clone https://github.com/YOUR_USERNAME/otskvm-vk-teams-bot.git
cd otskvm-vk-teams-bot
```

2. Создайте виртуальное окружение:
```bash
python -m venv venv
# source venv/bin/activate  # Linux/Mac
venv\Scripts\activate   # Windows
```

3. Установите зависимости:
```bash
pip install -r requirements.txt
```

4. Создайте файл .env и добавьте токен бота:
```bash
# VK Workspace
BOT_TOKEN=ваш_токен_от_metabot

# База данных PostgreSQL
DATABASE_URL=postgresql://user:password@localhost:5432/database_name

# Google Calendar
GOOGLE_CALENDAR_ID=primary  # или ID вашего календаря
```

5. Настройте Google Calendar API:
```bash
Скачайте credentials.json из Google Cloud Console
Положите в корень проекта
```

6. Запустите бота:
```bash
python run.py
```

## 🐛 Известные проблемы и решения

### Ошибки при запуске и работе бота

| Проблема | Причина | Решение |
|----------|---------|---------|
| `ModuleNotFoundError: No module named 'bot.bot'` | Конфликт имён: ваш файл `bot.py` перекрывает библиотеку `mailru-im-bot` | Переименуйте файл `bot.py` в `run.py` (или `main.py`) и обновите точку входа |
| `SyntaxError: future feature annotations is not defined` | Использование `from __future__ import annotations` в Python 3.6 | Удалите эту строку из файла (поддерживается только с Python 3.7+) |
| `TypeError: _signal_handler() takes 2 positional arguments but 3 were given` | Конфликт обработчиков сигналов в библиотеке `mailru-im-bot` на Windows | Используйте `bot_wrapper.py` с переопределённым методом `idle()` (реализовано в проекте) |
| `RuntimeError: Event loop is closed` | Проблемы с event loop при асинхронных операциях | Используйте `run_async()` для изоляции асинхронных вызовов (реализовано в проекте) |
| `ImportError: cannot import name 'Final'` | `typing.Final` не поддерживается в Python 3.6 | Удалите аннотации `Final` из `constants.py` (исправлено) |
| `type object 'datetime.datetime' has no attribute 'fromisoformat'` | `datetime.fromisoformat()` работает некорректно с некоторыми форматами в Python 3.6 | Используйте `python-dateutil` для парсинга дат (реализовано) |

### Проблемы с Google Calendar API

| Проблема | Причина | Решение |
|----------|---------|---------|
| Бот не видит события в календаре | Неправильный `GOOGLE_CALENDAR_ID` в `.env` | Проверьте ID календаря. Используйте `primary` для основного календаря или скопируйте ID из настроек Google Calendar |
| `FileNotFoundError: credentials.json not found` | Файл с учётными данными Google OAuth отсутствует | Скачайте `credentials.json` из Google Cloud Console (Desktop app) и положите в корень проекта |
| Ошибка авторизации при первом запуске | Требуется подтверждение доступа к календарю | При первом запуске откроется браузер для авторизации. Войдите в аккаунт и разрешите доступ |
| `HttpError 403: Rate Limit Exceeded` | Превышен лимит запросов к Google API | Увеличьте интервал синхронизации или уменьшите количество дней в `fetch_events()` |

### Проблемы с базой данных

| Проблема | Причина | Решение |
|----------|---------|---------|
| `Connection refused` при подключении к БД | PostgreSQL не запущен или неправильные параметры подключения | Проверьте, что контейнер Docker запущен (`docker ps`). Проверьте `DATABASE_URL` в `.env` |
| `relation "calendar_events" does not exist` | Таблица не создана | Таблицы создаются автоматически при первом запуске через `database.py`. Убедитесь, что у пользователя есть права на создание таблиц |
| `column "location" does not exist` | В проекте используется `auditory_id` вместо `location` | В текущей версии проекта поле `location` не используется. Проверьте структуру таблицы `calendar_events` |

### Проблемы с нормализацией аудиторий

| Проблема | Причина | Решение |
|----------|---------|---------|
| `⚠️ Аудитория не найдена: '...'` в логах | Название аудитории из календаря отсутствует в словаре синонимов | Добавьте новый вариант в `ALIASES` в файле `src/utils/auditory_normalizer.py` |
| Название аудитории не отображается в сообщениях | `auditory_id` не найден или `LEFT JOIN` не сработал | Проверьте, что в таблице `auditories` есть запись с соответствующим названием. Проверьте SQL-запрос в `get_events_from_db()` |

### Проблемы с VK Workspace

| Проблема | Причина | Решение |
|----------|---------|---------|
| Бот не отвечает в общих чатах | Не настроена фильтрация чатов | Проверьте функцию `is_private_chat()` — для корпоративной версии личные чаты определяются по email |
| Бот не видит сообщения в личке | Бот не добавлен в чат или нет прав | Убедитесь, что бот добавлен в чат. Проверьте токен и права доступа через `@metabot` |
| Кнопки не работают | Не зарегистрирован `BotButtonCommandHandler` | Убедитесь, что в `setup()` модуля зарегистрирован обработчик кнопок |
| `parse_mode="HTML"` не работает | VK Teams не поддерживает HTML в сообщениях | Используйте MarkdownV2 или проверьте документацию VK Teams Bot API |

### Прочие проблемы

| Проблема | Причина | Решение |
|----------|---------|---------|
| `pip install` не находит нужную версию пакета | Старая версия `pip` | Обновите pip: `python -m pip install --upgrade pip` |
| `protobuf` требует Python >=3.7 | Новая версия `protobuf` не совместима с Python 3.6 | Установите `protobuf==3.19.6` (указано в `requirements.txt`) |
| Названия дней недели на английском в `/week` | Удалён словарь `WEEKDAYS_RU` или используется `%A` без перевода | Добавьте словарь `WEEKDAYS_RU` и используйте его в `week_handler` |

### Как сообщить о новой проблеме

1. Проверьте логи в консоли — там может быть подробная информация об ошибке.
2. Проверьте, не описана ли проблема выше.
3. Если проблема новая, создайте issue в репозитории с описанием:
   - Что вы делали
   - Что ожидали увидеть
   - Что увидели на самом деле
   - Полный вывод ошибки (traceback)

---

### Быстрая диагностика

1. **Проверить подключение к БД:**
   ```bash
   python -c "from src.core.database import Database; import asyncio; asyncio.run(Database.get_pool()); print('✅ БД подключена')"
   ```

2. **Проверить Google Calendar:**
   ```bash
   python -c "from src.core.google_client import calendar_client; events = calendar_client.fetch_events(1); print(f'✅ Получено {len(events)} событий')"
   ```

3. **Проверить нормализацию:**
   ```bash
   python -c "from src.utils.auditory_normalizer import AuditoryNormalizer; print(AuditoryNormalizer.normalize('лекц. 1'))"
   # Ожидаемый вывод: Лекционный зал 1
   ```

4. **Проверить импорты модулей:**
   ```bash
   python -c "import src.modules.calendar.handlers; print('✅ Модуль календаря загружен')"
   ```

## 📝 Планы развития

- Главное меню и инлайн-кнопки
- Ролевая модель и управление пользователями
- Учёт статусов аудиторий и назначения инженеров
- Система уведомлений и админ-панель
- Модуль задач и финальная полировка

## 👨‍💻 Разработка

### Добавление нового модуля

1. Создайте папку в src/modules/
2. Создайте handlers.py с функцией setup()
3. Зарегистрируйте команды через module_manager.register_command()
4. Модуль автоматически загрузится при запуске

### Пример модуля:
```python
# src/modules/example/handlers.py

def setup(bot, module_manager):
    module_manager.register_command('/example', example_handler, 'example')

def example_handler(bot, event):
    bot.send_text(chat_id=event.from_chat, text="Пример команды")
```


## 🔗 Ссылки

### 📚 Документация
| Ресурс | Ссылка | Описание |
|--------|--------|----------|
| **Репозиторий проекта** | [otskvm-vk-teams-bot](https://github.com/Nimos95/otskvm-vk-teams-bot) | Исходный код бота |
| **VK Teams Bot API** | [teams.vk.com/botapi/](https://teams.vk.com/botapi/) | Официальная документация по ботам VK Teams |
| **Google Calendar API** | [developers.google.com/calendar](https://developers.google.com/calendar/api/guides/overview) | Документация по Google Calendar API |
| **PostgreSQL** | [postgresql.org/docs](https://www.postgresql.org/docs/) | Документация по PostgreSQL |

### 🛠 Инструменты
| Ресурс | Ссылка | Описание |
|--------|--------|----------|
| **Google Cloud Console** | [console.cloud.google.com](https://console.cloud.google.com/) | Настройка API и получение `credentials.json` |
| **DBeaver** | [dbeaver.io](https://dbeaver.io/) | Клиент для работы с PostgreSQL |
| **PostgreSQL Docker** | [hub.docker.com/_/postgres](https://hub.docker.com/_/postgres) | Образ PostgreSQL для Docker |

### 🔗 Связанные проекты
| Ресурс | Ссылка | Описание |
|--------|--------|----------|
| **OTSKVMBot (Telegram)** | [github.com/Nimos95/otskvm-bot](https://github.com/Nimos95/otskvm-bot) | Исходная версия бота для Telegram |

---

### 👨‍💻 Контакты

- **Автор:** Москвин Никита Романович — [@Nimos95](https://github.com/Nimos95)
- **Организация:** СПбПУ Петра Великого, отдел технического сопровождения КВМ
- moskvin_nr@spbstu.ru
- +7 (993) 486-4670

---


