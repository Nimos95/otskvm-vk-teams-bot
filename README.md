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
- ✅ MarkdownV2-форматирование (жирный шрифт)
- ✅ Модальные окна с результатами синхронизации

#### 🏛️ **Привязка событий к аудиториям**
- ✅ Автоматическое извлечение названия аудитории из `location` события
- ✅ Нормализация названий через словарь синонимов
- ✅ Отображение аудитории и здания в сообщениях
- ✅ Логирование ненайденных аудиторий для пополнения словаря

#### 🟢 **Учёт статусов аудиторий** 
- ✅ Команда `/status` — просмотр текущих статусов всех аудиторий
- ✅ Команда `/set_status` — интерактивная отметка статуса с выбором аудитории
- ✅ Инлайн-кнопки для быстрого выбора статуса (🟢 Всё работает, 🟡 Есть проблемы, 🔴 Не работает)
- ✅ Карточка аудитории с информацией о текущем статусе
- ✅ Изменение статуса с обязательным комментарием
- ✅ Кнопка «⏭️ Сохранить без комментария»
- ✅ Подтверждение сохранения статуса
- ✅ Уведомления в общий чат при отметке 🟡/🔴
- ✅ Статистика по статусам в админ-панели
- ✅ История статусов с указанием времени и автора
- ✅ Права доступа: только Engineer+ могут менять статусы
- ✅ Автоматическое обновление списка аудиторий после сохранения статуса


#### 🎛️ **Навигация и интерфейс**
- ✅ Главное меню с инлайн-кнопками (команда `/start`)
- ✅ Динамическое меню в зависимости от роли пользователя
- ✅ Админ-панель с разграничением по ролям
- ✅ Модальные окна для результатов действий
- ✅ Редактирование сообщений вместо отправки новых
- ✅ Вертикальное расположение кнопок для удобства на мобильных устройствах

#### 👥 **Управление пользователями и ролями**
- ✅ Автоматическая регистрация новых пользователей
- ✅ Команда `/my_role` — просмотр своей роли
- ✅ Команда `/set_role` — назначение роли (только Superadmin)
- ✅ Команда `/list_users` — список всех пользователей
- ✅ Ролевая модель:
  - **Viewer** — только просмотр календаря
  - **Engineer** — календарь + статусы + мои мероприятия
  - **Admin** — все технические операции + админ-панель
  - **Manager** — календарь + отчётность
  - **Superadmin** — полный доступ

#### 🏗️ **Архитектура**
- ✅ Модульная структура (легко добавлять новые функции)
- ✅ Единый диспетчер callback-событий
- ✅ Синхронный драйвер БД (psycopg2)
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
| **Синхронный драйвер БД** | psycopg2-binary | 2.9.3 |
| **Асинхронный драйвер БД** | asyncpg | 0.30.0 |
| **Google Calendar API** | google-api-python-client | 1.12.8 |
| **Парсинг дат** | python-dateutil | 2.8.2 |
| **Транслитерация** | cyrtranslit | 0.9.2 |
| **Конфигурация** | python-dotenv | 1.0.0 |

---

## 🔐 Матрица доступа

### 📊 Сводная таблица

| Функция / Роль | Viewer | Engineer | Admin | Manager | Superadmin |
|----------------|:------:|:--------:|:-----:|:-------:|:----------:|
| **Календарь** | | | | | |
| Просмотр событий (`/today`, `/tomorrow`, `/week`) | ✅ | ✅ | ✅ | ✅ | ✅ |
| Синхронизация (`/sync`) | ❌ | ❌ | ✅ | ❌ | ✅ |
| **Аудитории** | | | | | |
| Просмотр статусов аудиторий | ✅ | ✅ | ✅ | ✅ | ✅ |
| Отметка статуса аудитории (`/set_status`) | ❌ | ✅ | ✅ | ❌ | ✅ |
| История статусов аудитории | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Назначения** | | | | | |
| Просмотр своих мероприятий | ❌ | ✅ | ✅ | ❌ | ✅ |
| Назначение инженера на мероприятие (`/assign`) | ❌ | ❌ | ✅ | ❌ | ✅ |
| Подтверждение/отказ от назначения | ❌ | ✅ | ✅ | ❌ | ✅ |
| Просмотр всех назначений | ❌ | ❌ | ✅ | ✅ | ✅ |
| **Пользователи** | | | | | |
| Просмотр своего профиля (`/my_role`) | ✅ | ✅ | ✅ | ✅ | ✅ |
| Список всех пользователей (`/list_users`) | ❌ | ❌ | ✅ | ✅ | ✅ |
| Назначение роли (`/set_role`) | ❌ | ❌ | ❌ | ❌ | ✅ |
| **Отчётность** | | | | | |
| Статистика (`/stats`) | ❌ | ❌ | ✅ | ✅ | ✅ |
| **Администрирование** | | | | | |
| Доступ к админ-панели | ❌ | ❌ | ✅ | ❌ | ✅ |

---

### 📋 Описание ролей

| Роль | Должность | Описание | Ключевые права |
|------|-----------|----------|----------------|
| **Superadmin** | Разработчик, главный администратор | Полный контроль над системой | ✅ Всё, включая управление пользователями и ролями |
| **Admin** | Начальник отдела | Оперативное управление, участие в работе | 🔧 Все технические операции, админ-панель |
| **Manager** | Начальник управления | Стратегическое управление, контроль работы отдела | 📊 Статистика, список пользователей, просмотр назначений |
| **Engineer** | Инженер | Исполнение задач, работа с аудиториями | 🛠️ Статусы, свои мероприятия |
| **Viewer** | Внешний наблюдатель | Только просмотр | 👁️ Календарь, статусы аудиторий |

---

### 📝 Команды и их доступность

| Команда | Viewer | Engineer | Admin | Manager | Superadmin |
|---------|:------:|:--------:|:-----:|:-------:|:----------:|
| `/start` | ✅ | ✅ | ✅ | ✅ | ✅ |
| `/help` | ✅ | ✅ | ✅ | ✅ | ✅ |
| `/today` | ✅ | ✅ | ✅ | ✅ | ✅ |
| `/tomorrow` | ✅ | ✅ | ✅ | ✅ | ✅ |
| `/week` | ✅ | ✅ | ✅ | ✅ | ✅ |
| `/sync` | ❌ | ❌ | ✅ | ❌ | ✅ |
| `/my_role` | ✅ | ✅ | ✅ | ✅ | ✅ |
| `/list_users` | ❌ | ❌ | ✅ | ✅ | ✅ |
| `/set_role` | ❌ | ❌ | ❌ | ❌ | ✅ |
| `/status` | ✅ | ✅ | ✅ | ✅ | ✅ |
| `/set_status` | ❌ | ✅ | ✅ | ❌ | ✅ |
| `/assign` | ❌ | ❌ | ✅ | ❌ | ✅ |
| `/my_assignments` | ❌ | ✅ | ✅ | ❌ | ✅ |
| `/stats` | ❌ | ❌ | ✅ | ✅ | ✅ |
| `/history` | ✅ | ✅ | ✅ | ✅ | ✅ |

---

### ✅ Итоговая логика ролей

| Роль | Календарь | Статусы | Назначения | Пользователи | Отчётность | Админ-панель |
|------|:---------:|:-------:|:----------:|:------------:|:----------:|:------------:|
| **Viewer** | ✅ (просмотр) | ✅ (просмотр) | ❌ | ❌ | ❌ | ❌ |
| **Engineer** | ✅ (просмотр) | ✅ (изменение) | ✅ (свои) | ❌ | ❌ | ❌ |
| **Admin** | ✅ (всё) | ✅ (всё) | ✅ (все) | ✅ (просмотр) | ✅ | ✅ (ограниченная) |
| **Manager** | ✅ (просмотр) | ✅ (просмотр) | ✅ (просмотр) | ✅ (просмотр) | ✅ | ❌ |
| **Superadmin** | ✅ (всё) | ✅ (всё) | ✅ (все) | ✅ (полный) | ✅ | ✅ (полная) |

---

### 🔒 Принципы назначения ролей

1. **Viewer** — автоматически при первом обращении к боту.
2. **Engineer** — назначается администратором или суперадминистратором.
3. **Manager** — назначается администратором или суперадминистратором.
4. **Admin** — назначается только суперадминистратором.
5. **Superadmin** — назначается только вручную через БД (или другим суперадминистратором).

---

### 📊 Сравнение ролей: ключевые различий

| Характеристика | Viewer | Engineer | Admin | Manager | Superadmin |
|----------------|:------:|:--------:|:-----:|:-------:|:----------:|
| Может отмечать статусы | ❌ | ✅ | ✅ | ❌ | ✅ |
| Может назначать инженеров | ❌ | ❌ | ✅ | ❌ | ✅ |
| Может назначать роли | ❌ | ❌ | ❌ | ❌ | ✅ |
| Видит всех пользователей | ❌ | ❌ | ✅ | ✅ | ✅ |
| Имеет доступ к админ-панели | ❌ | ❌ | ✅ | ❌ | ✅ |
| Может синхронизировать календарь | ❌ | ❌ | ✅ | ❌ | ✅ |

---

### 💡 Примеры использования

| Сценарий | Кто может |
|----------|-----------|
| Инженер отмечает проблему в аудитории 501 | Engineer, Admin, Superadmin |
| Менеджер смотрит статистику по мероприятиям | Admin, Manager, Superadmin |
| Администратор назначает инженера на мероприятие | Admin, Superadmin |
| Суперадминистратор назначает нового администратора | Superadmin |
| Наблюдатель смотрит расписание на сегодня | Все |

---

## 🗄️ Структура базы данных

### Таблица `users` — пользователи системы

| Поле | Тип | Ограничение | Описание |
|------|-----|-------------|----------|
| `user_id` | VARCHAR(255) | PRIMARY KEY | ID пользователя (email из VK Workspace) |
| `full_name` | VARCHAR(100) | | Имя для отображения |
| `role` | VARCHAR(20) | DEFAULT 'viewer' | Роль: superadmin / admin / manager / engineer / viewer |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Дата регистрации |
| `last_active` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Последняя активность |
| `is_active` | BOOLEAN | DEFAULT TRUE | Активен ли пользователь |

### Таблица `status_log` — история статусов аудиторий (Новое в День 6)

| Поле | Тип | Ограничение | Описание |
|------|-----|-------------|----------|
| `id` | SERIAL | PRIMARY KEY | Внутренний ID |
| `auditory_id` | INTEGER | FOREIGN KEY (auditories.id) NOT NULL | ID аудитории |
| `status` | VARCHAR(10) | NOT NULL | green / yellow / red |
| `comment` | TEXT | | Комментарий к проблеме |
| `reported_by` | VARCHAR(255) | FOREIGN KEY (users.user_id) NOT NULL | Кто отметил |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Когда отметили |
| `resolved_at` | TIMESTAMP | | Когда починили |
| `resolution_comment` | TEXT | | Как починили |

**Индексы:**
- `idx_status_log_auditory` — для быстрого поиска по аудитории
- `idx_status_log_created` — для поиска по дате

### Таблица `calendar_events` — мероприятия из Google Calendar

| Поле | Тип | Ограничение | Описание |
|------|-----|-------------|----------|
| `id` | SERIAL | PRIMARY KEY | Внутренний ID |
| `google_event_id` | VARCHAR(255) | UNIQUE NOT NULL | ID из Google Calendar |
| `auditory_id` | INTEGER | FOREIGN KEY (auditories.id) | ID аудитории |
| `title` | VARCHAR(500) | NOT NULL | Название мероприятия |
| `description` | TEXT | | Описание мероприятия |
| `location` | TEXT | | Место проведения (из Google Calendar) |
| `start_time` | TIMESTAMP WITH TIME ZONE | NOT NULL | Начало мероприятия |
| `end_time` | TIMESTAMP WITH TIME ZONE | NOT NULL | Конец мероприятия |
| `is_all_day` | BOOLEAN | DEFAULT FALSE | Целодневное событие |
| `status` | VARCHAR(20) | DEFAULT 'confirmed' | confirmed / cancelled / tentative |
| `organizer` | VARCHAR(255) | | Организатор (email) |
| `last_sync` | TIMESTAMP WITH TIME ZONE | DEFAULT CURRENT_TIMESTAMP | Время последней синхронизации |
| `created_at` | TIMESTAMP WITH TIME ZONE | DEFAULT CURRENT_TIMESTAMP | Дата создания записи |
| `updated_at` | TIMESTAMP WITH TIME ZONE | DEFAULT CURRENT_TIMESTAMP | Дата обновления записи |

### Таблица `auditories` — аудитории

| Поле | Тип | Ограничение | Описание |
|------|-----|-------------|----------|
| `id` | SERIAL | PRIMARY KEY | Внутренний ID |
| `name` | VARCHAR(50) | NOT NULL | Номер аудитории ('501', '315') |
| `building` | VARCHAR(50) | | Корпус |
| `floor` | INTEGER | | Этаж |
| `equipment` | TEXT | | Описание оборудования |
| `notes` | TEXT | | Заметки |
| `is_active` | BOOLEAN | DEFAULT TRUE | Не списана ли |

### Таблица `sync_log` — лог синхронизации

| Поле | Тип | Ограничение | Описание |
|------|-----|-------------|----------|
| `id` | SERIAL | PRIMARY KEY | Внутренний ID |
| `sync_type` | VARCHAR(20) | NOT NULL | Тип: full / incremental |
| `events_processed` | INTEGER | DEFAULT 0 | Всего обработано событий |
| `events_inserted` | INTEGER | DEFAULT 0 | Добавлено событий |
| `events_updated` | INTEGER | DEFAULT 0 | Обновлено событий |
| `events_cancelled` | INTEGER | DEFAULT 0 | Отменено событий |
| `status` | VARCHAR(20) | DEFAULT 'success' | success / partial / failed |
| `error_message` | TEXT | | Текст ошибки (если была) |
| `started_at` | TIMESTAMP WITH TIME ZONE | DEFAULT CURRENT_TIMESTAMP | Начало синхронизации |
| `finished_at` | TIMESTAMP WITH TIME ZONE | | Окончание синхронизации |

---

### Связи между таблицами

```mermaid
erDiagram
    users ||--o{ calendar_events : "организует"
    users ||--o{ status_log : "отмечает"
    auditories ||--o{ calendar_events : "расположена в"
    auditories ||--o{ status_log : "имеет статус"
    users {
        varchar user_id PK
        varchar full_name
        varchar role
        timestamp created_at
        timestamp last_active
        boolean is_active
    }
    status_log {
        serial id PK
        integer auditory_id FK
        varchar status
        text comment
        varchar reported_by FK
        timestamp created_at
        timestamp resolved_at
        text resolution_comment
    }
    calendar_events {
        serial id PK
        varchar google_event_id UK
        integer auditory_id FK
        varchar title
        text description
        text location
        timestamp start_time
        timestamp end_time
        boolean is_all_day
        varchar status
        varchar organizer
        timestamp last_sync
    }
    auditories {
        serial id PK
        varchar name
        varchar building
        integer floor
        text equipment
        text notes
        boolean is_active
    }
    sync_log {
        serial id PK
        varchar sync_type
        integer events_processed
        integer events_inserted
        integer events_updated
        integer events_cancelled
        varchar status
        text error_message
        timestamp started_at
        timestamp finished_at
    }
```

---   

## 📋 Примеры работы модулей

---

### 📅 Модуль календаря

#### Команда `/today` — просмотр событий на сегодня
```bash
📅 События на сегодня

🕐 10:00 — Встреча с командой
📍 Аудитория: 501 (Главный корпус)
👤 Иванов И.И.

🕐 14:00 — Техническое совещание
📍 Аудитория: Лекционный зал 1 (Корпус Б)

━━━━━━━━━━━━━━━━━━━━━
ℹ️ Итого: 2 мероприятия

[📅 Сегодня]
[➡️ Завтра]
[📆 Неделя]
[🔄 Синхронизация]
[◀️ В главное меню]
```

#### Команда `/week` — просмотр событий на неделю
```bash
📊 События на неделю

22.06 (Понедельник)
🕐 10:00 — Планёрка по УМСиИ
🏛️ 118 (ГУК)

23.06 (Вторник)
🕐 09:00 — Совещание первого корпуса
🏛️ 315 (Главный корпус)
🕐 16:00 — Конференция
🏛️ Лекционный зал 1

━━━━━━━━━━━━━━━━━━━━━
ℹ️ Итого: 3 мероприятия
```

#### Синхронизация с Google Calendar

При нажатии кнопки **🔄 Синхронизация** появляется модальное окно с результатом:
```bash
✅ Синхронизация завершена!

📊 Получено: 43 событий
💾 Сохранено: 43 событий
```

---

### 🟢 Модуль аудиторий

#### Команда `/status` — просмотр статусов всех аудиторий
```bash
🏛️ Статусы аудиторий

🟢 501 — Всё работает (Главный корпус)
👤 Иванов Иван (10:15)

🟡 Лекционный зал 1 — Есть проблемы
📝 Проектор не включается
👤 Петров Пётр (08:30)

🔴 118 — Не работает
📝 Нет звука в колонках
👤 Сидоров Сидор (08:00)

━━━━━━━━━━━━━━━━━━━━━
ℹ️ Всего: 7 аудиторий
```

#### Команда `/set_status` — интерактивная отметка статуса

**Шаг 1: Выбор аудитории**
```bash
🏛️ Выберите аудиторию:

[501 (Главный корпус)]
[315 (Главный корпус)]
[Лекционный зал 1 (Главный корпус)]
[Семенов]
[Капица]
[118 (ГУК)]
[130]
[◀️ Отмена]
```

**Шаг 2: Карточка аудитории**
```bash
🏛️ 501

📍 Главный корпус, 5 этаж
🔧 Проектор, звук, HDMI

Текущий статус: 🟢 Всё работает
👤 Иванов Иван (10:15)

[🟢 Всё работает] [🟡 Есть проблемы]
[🔴 Не работает] [📋 История]
[◀️ Назад к списку]
```

**Шаг 3: Выбор статуса**
```bash
📝 Введите комментарий

🏛️ Аудитория: 501
🔄 Статус: 🟡 Есть проблемы

📝 Напишите комментарий в следующем сообщении.
💡 Нажмите «⏭️ Сохранить без комментария», чтобы пропустить.

[⏭️ Сохранить без комментария] [❌ Отмена]
```

**Шаг 4: Подтверждение сохранения статуса**
```bash
✅ Статус обновлён!

🏛️ Аудитория: 501
🔄 Статус: 🟡 Есть проблемы
📝 Комментарий: Проектор не включается
👤 Отметил: Иванов Иван
🕐 10:20
```
#### Команда `/history` - история статусов конкретной аудитории
```bash
📋 История статусов: 501

🟢 Всё работает — 10:15 22.06
👤 Иванов Иван

🟡 Есть проблемы — 10:20 22.06
📝 Проектор не включается
👤 Петров Пётр

🔴 Не работает — 08:00 22.06
📝 Нет звука в колонках
👤 Сидоров Сидор
✅ Исправлено: заменили кабель

━━━━━━━━━━━━━━━━━━━━━
ℹ️ Последние 3 изменения
```
---

#### 🔔 Уведомление в общий чат (при отметке статуса 🟡/🔴)
```bash
⚠️ Изменение статуса аудитории

🏛️ Аудитория: 501 (Главный корпус)
🔄 Статус: 🟡 Есть проблемы
📝 Комментарий: Проектор не включается
👤 Отметил: Иванов Иван
🕐 10:20
```

---

## 🚀 Установка и запуск

### Требования
- Python 2.7, 3.4, 3.5, 3.6
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

- Назначения инженеров на мероприятия из календаря
- Модуль задач и финальная полировка

## 👨‍💻 Разработка

### Добавление нового модуля

1. Создайте папку в src/modules/
2. Создайте handlers.py с функцией setup()
3. Зарегистрируйте команды через module_manager.register_command()
4. Зарегистрируйте callback'и через module_manager.register_callback()
5. Модуль автоматически загрузится при запуске

### Пример модуля:
```python
# src/modules/example/handlers.py

def setup(bot, module_manager):
    module_manager.register_command('/example', example_handler, 'example')
    module_manager.register_callback('example_callback', example_callback, 'example')

def example_handler(bot, event):
    # обработка команды
    pass

def example_callback(bot, event):
    # обработка кнопки
    pass
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
- 📧 moskvin_nr@spbstu.ru
- 📞 +7 (993) 486-4670

---


