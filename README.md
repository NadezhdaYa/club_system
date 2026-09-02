# Система автоматизации учёта спортивного клуба

## Стек
- Python 3.11+
- PostgreSQL 14+
- SQLAlchemy 2.x
- Alembic
- PyQt6
- psycopg2

## Структура проекта

club_system/
├── ui/
│   ├── clients_window.py      — окно списка клиентов
│   └── training_form.py        — форма добавления тренировки
├── models.py                   — ORM-модели
├── repositories.py             — слой доступа к данным
├── services.py                 — бизнес-логика
├── sync.py                     — синхронизация внешних данных
├── config.py                   — конфигурация
├── main.py                     — точка входа
├── migrations/
│   ├── env.py
│   ├── script.py.mako
│   ├── README
│   └── versions/
│       └── v1_initial_schema.py
├── docs/
│   └── er_diagram.plantuml
├── tests/
│   ├── test_conn.py
│   ├── test_db.py
│   ├── test_services.py
│   └── test_sync.py
├── alembic.ini
└── README.md

## Установка

1. Создать БД:
   ```sql
   CREATE DATABASE club_db;

## Документация
- ER-диаграмма: `docs/er_diagram.plantuml`
- Пояснительная записка: раздел «Архитектура», «Реализация», «Тестирование».

2. Установить зависимости:
   ```bash
   pip install sqlalchemy psycopg2-binary alembic PyQt6 pytest

3. Указать пароль в config.py и alembic.ini.
4. Применить миграции:
   ```bash
   alembic upgrade head

5. Запустить приложение:
   ```bash
   python main.py

6. Запустить тесты:
   ```bash
   pytest tests/
