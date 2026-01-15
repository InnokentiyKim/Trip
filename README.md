# Hotels Backend Service

[![Python](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/downloads/release/python-3110/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.95.2-green.svg)](https://fastapi.tiangolo.com/)
[![Build Status](https://img.shields.io/github/actions/workflow/status/yettey/backend/ci.yml?branch=main)]()

#### Современный backend-сервис для бронирования отелей, построенный на принципах Чистой Архитектуры. Предоставляет надежные API для управления отелями, бронированиями, аутентификацией пользователей и платежными операциями.
- **🏛️ Чистая Архитектура** - Четкое разделение слоев обеспечивает легкую поддержку и тестирование
- **⚡ Высокая производительность** - Асинхронная архитектура на FastAPI и SQLAlchemy 2.0
- **🔒 Корпоративная безопасность** - JWT, OAuth2, MFA и Argon2 для защиты данных
- **📊 Полная наблюдаемость** - Интеграция Sentry, Prometheus и Grafana
- **🧪 Качество кода** - Статическая типизация, автоматическое тестирование и линтинг
- **🔄 CQRS паттерн** - Оптимизированная обработка команд и запросов
- **📦 Современный стек** - UV для управления зависимостями, Ruff для форматирования

## 🏗️ Реализация Чистой Архитектуры
```
├── 💎 Слой домена (domain/)
│   ├── Бизнес сущности, комманды, и основная логика
│   └── Независимость от внешних зависимостей
├── 🎯 Слой приложения (application/)
│   ├── Use cases and сервисы приложения
│   └── Оркестрация бизнес процессами
├── 🔌 Слой инфраструктуры (adapters/, controllers/)
│   ├── Внешние интерфейсы, Базы данных, HTTP контроллеры
│   └── Специфичные реализации фреймворков
└── 🛠️ Общий слой (common/)
    └── Общие утилиты и кросс-функциональные компоненты
```

## 🔧 Стек технологий

### Основной фреймворк и библиотеки
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.0-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-D71F00?style=flat&logo=sqlalchemy&logoColor=white)](https://www.sqlalchemy.org/)
[![Alembic](https://img.shields.io/badge/Alembic-1.13-6BA81E?style=flat)](https://alembic.sqlalchemy.org/)
[![Dishka](https://img.shields.io/badge/Dishka-1.3-blue?style=flat)](https://github.com/reagento/dishka)
- **FastAPI** - Высокопроизводительный веб-фреймворк
- **SQLAlchemy 2.0** - Асинхронная ORM с PostgreSQL
- **Alembic** - Миграции базы данных
- **Dishka** - Внедрение зависимостей

### Инфраструктура
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?style=flat&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![RabbitMQ](https://img.shields.io/badge/RabbitMQ-3.13-FF6600?style=flat&logo=rabbitmq&logoColor=white)](https://www.rabbitmq.com/)
[![MinIO](https://img.shields.io/badge/MinIO-S3-C72E49?style=flat&logo=minio&logoColor=white)](https://min.io/)
- **PostgreSQL** - Основная база данных
- **RabbitMQ** - Брокер сообщений для фоновых задач
- **MinIO/S3** - Объектное хранилище для файлов

### Аутентификация и безопасность
[![JWT](https://img.shields.io/badge/JWT-Auth-000000?style=flat&logo=jsonwebtokens&logoColor=white)](https://jwt.io/)
[![OAuth2](https://img.shields.io/badge/OAuth2-Enabled-3C873A?style=flat&logo=oauth&logoColor=white)](https://oauth.net/2/)
[![Argon2](https://img.shields.io/badge/Argon2-Password_Hash-5C2D91?style=flat)](https://github.com/P-H-C/phc-winner-argon2)
[![MFA](https://img.shields.io/badge/MFA-Enabled-2FA?style=flat&logo=authy&logoColor=white)](https://en.wikipedia.org/wiki/Multi-factor_authentication)
- **JWT** - Аутентификация на основе токенов
- **OAuth2** - Интеграция с Google, Yandex
- **Argon2** - Хеширование паролей
- **MFA** - Многофакторная аутентификация

### Мониторинг и наблюдаемость
[![Sentry](https://img.shields.io/badge/Sentry-Error_Tracking-362D59?style=flat&logo=sentry&logoColor=white)](https://sentry.io/)
[![Prometheus](https://img.shields.io/badge/Prometheus-Metrics-E6522C?style=flat&logo=prometheus&logoColor=white)](https://prometheus.io/)
[![Grafana](https://img.shields.io/badge/Grafana-Dashboards-F46800?style=flat&logo=grafana&logoColor=white)](https://grafana.com/)
[![Logging](https://img.shields.io/badge/Logging-JSON-000000?style=flat&logo=json&logoColor=white)](https://www.json.org/)
- **Sentry** - Отслеживание ошибок и исключений
- **Prometheus** - Сбор метрик и мониторинг
- **Grafana** - Визуализация метрик
- **Structured Logging** - Структурированные JSON-логи

### Инструменты разработки
[![Ruff](https://img.shields.io/badge/Ruff-Linter-261230?style=flat&logo=ruff&logoColor=white)](https://docs.astral.sh/ruff/)
[![MyPy](https://img.shields.io/badge/MyPy-Type_Check-2A6DB2?style=flat&logo=python&logoColor=white)](http://mypy-lang.org/)
[![Pytest](https://img.shields.io/badge/Pytest-8.3-0A9EDC?style=flat&logo=pytest&logoColor=white)](https://pytest.org/)
[![Pre\-commit](https://img.shields.io/badge/Pre--commit-Hooks-FAB040?style=flat&logo=pre-commit&logoColor=white)](https://pre-commit.com/)
[![UV](https://img.shields.io/badge/UV-Package_Manager-DE5FE9?style=flat)](https://github.com/astral-sh/uv)
- **Ruff** - Быстрый линтер и форматтер
- **MyPy** - Статическая проверка типов
- **Pytest** - Фреймворк для тестирования с поддержкой async
- **Pre-commit** - Git-хуки для поддержки качества кода
- **UV** - Быстрый менеджер пакетов Python


## 🚀 Установка и запуск

1. **Вариант локального запуска**
   ```bash
   # Клонирование репозитория
   git clone git@github.com:InnokentiyKim/Trip.git
   # Установка зависимостей и синхронизация окружения
   uv sync
   # Запуск миграций базы данных
   alembic upgrade head
   # Запуск приложения на локальном хосте
   python src/main.py --port 8001
   ```
2. **Вариант с Docker**
   ```bash
   # Клонирование репозитория
   git clone git@github.com:InnokentiyKim/Trip.git
   # Запуск приложения с Docker Compose
   docker-compose up -d --build
   ```

## 📋 Доступные команды

### Разработка
- `uv sync` - Установка зависимостей и синхронизация окружения
- `python src/main.py --port 8001` - Запуск сервера на локальном хосте

### Качество кода
- `ruff check --fix` - Запуск линтера с авто исправлением
- `ruff format` - Форматирование кода
- `mypy src` - Запуск статической проверки типов
- `pre-commit run --all-files` - Запуск всех pre-commit хуков

### Тестирование
- `pytest` - Запуск всех тестов
- `pytest tests/bookings/` - Запуск тестов для конкретного модуля

### База данных
- `alembic upgrade head` - Применение всех миграций
- `alembic revision --autogenerate -m "description"` - Генерация новой миграции
- `alembic downgrade -1` - Откат последней миграции

### Использование CLI (командной строки)
- `python -m scripts.cli database_data migrate --load-samples` - Запуск миграций и загрузка тестовых данных


## 📊 API документация

- **OpenAPI/Swagger**: Доступен на `/docs` при запуске сервера
- **ReDoc**: Доступен на `/redoc`

### Ключевые паттерны и практики

- **Repository Pattern**: Gateway-классы управляют сохранением данных
- **CQRS**: Отдельные команды и запросы с выделенными обработчиками
- **Result Pattern**: Явные результаты успеха/неудачи вместо исключений
- **Interactor Pattern**: Сервисы приложения оркестрируют бизнес-логику
- **Controller-as-Orchestrator**: HTTP-контроллеры компонуют бизнес-процессы