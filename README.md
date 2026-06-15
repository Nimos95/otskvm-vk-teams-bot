# 🤖 OTSKVM VK Teams Bot

Бот для ОТСКВМ в VK Workspace.

## 📋 Возможности

### Реализовано (День 1)
- ✅ Базовая модульная архитектура
- ✅ Фильтрация чатов (личные vs групповые)
- ✅ Команды `/start` и `/help`
- ✅ Автоматическая загрузка модулей

### В разработке
- 🔄 Интеграция с Google Calendar
- 🔄 Команды `/today`, `/tomorrow`, `/week`
- 🔄 База данных PostgreSQL
- 🔄 Учёт статусов аудиторий
- 🔄 Система уведомлений

## 🚀 Установка и запуск

### Требования
- Python 3.6+
- VK Workspace аккаунт с правами на создание бота

### Установка

1. Клонируйте репозиторий:
```bash
git clone https://github.com/YOUR_USERNAME/otskvm-vk-teams-bot.git
cd otskvm-vk-teams-bot
```

2. Создайте виртуальное окружение:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows
```

3. Установите зависимости:
```bash
pip install -r requirements.txt
```

4. Создайте файл .env и добавьте токен бота:
```bash
BOT_TOKEN=ваш_токен_от_metabot
```

5. Запустите бота:
```bash
python run.py
```

## 📁 Структура проекта
otskvm-vk-teams-bot/
├── src/
│   ├── core/           # Ядро бота (менеджер модулей, фильтры)
│   └── modules/        # Модули функциональности
├── run.py              # Точка входа
├── requirements.txt    # Зависимости
└── .env.example        # Пример конфигурации

## 👨‍💻 Разработка

Проект разрабатывается в рамках работы технической поддержки СПбПУ.

## 📞 Контакты
Инженер ОТСКВМ
Москвин Никита Романович
moskvin_nr@spbstu.ru
+7 (993) 486-4670