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

## 📝 Планы развития

- Автоматическая привязка аудиторий к событиям
- Инлайн-кнопки для выбора периода
- Утренняя и дневная сводка в общие чаты
- Система уведомлений
- Административная панель

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

Проект разрабатывается в рамках работы технической поддержки СПбПУ.

## 📞 Контакты
- Инженер ОТСКВМ
- Москвин Никита Романович
- moskvin_nr@spbstu.ru
- +7 (993) 486-4670