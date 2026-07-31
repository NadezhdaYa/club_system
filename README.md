# Система учёта спортивного клуба (Python + PostgreSQL + PyQt6)

## Стек
- Python 3.10+
- PostgreSQL 14+
- PyQt6, SQLAlchemy, Alembic, python-dotenv, pytest

## Установка
1. `pip install -r requirements.txt`
2. Создайте `.env` с `DATABASE_URL`.
3. `alembic upgrade head`
4. `python main.py`

## Функционал
- Учёт клиентов, персонала, услуг.
- Расписание и тренировки с проверкой лимитов.
- Синхронизация внешних данных с историей версий.
- Отчёты: клиенты по статусу, расписание тренера, история посещений.

## Тесты
`pytest tests/`

## Документация
- ER-диаграмма: `docs/er_diagram.plantuml`
- Пояснительная записка: раздел «Архитектура», «Реализация», «Тестирование».