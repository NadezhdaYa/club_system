from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base, Staff, Service, TrainingSession, Client
from config import DATABASE_URL
from datetime import datetime
from app.services import SchedulingService
from app.repositories import TrainingSessionRepository

engine = create_engine(DATABASE_URL)
TestingSession = sessionmaker(bind=engine)

def test_check_staff_conflict():
    session = TestingSession()
    try:
        # Создаём тренера, услугу, клиента
        staff = Staff(full_name="Тренер Тестов", position="Тренер", is_active=True)
        service = Service(name="Йога", price=1000, duration_minutes=60, is_active=True)
        client = Client(full_name="Клиент Тестов", status="active")
        session.add_all([staff, service, client])
        session.commit()

        # Первая тренировка
        start1 = datetime(2026, 9, 1, 10, 0)
        end1 = datetime(2026, 9, 1, 11, 0)
        ts1 = TrainingSession(
            service_id=service.id, staff_id=staff.id, client_id=client.id,
            start_at=start1, end_at=end1, status="planned", is_actual=True
        )
        session.add(ts1)
        session.commit()

        # Проверяем конфликт — пересекающееся время
        start2 = datetime(2026, 9, 1, 10, 30)
        end2 = datetime(2026, 9, 1, 11, 30)
        assert SchedulingService.check_staff_conflict(session, staff.id, start2, end2) is False

        # Проверяем свободное время
        start3 = datetime(2026, 9, 1, 12, 0)
        end3 = datetime(2026, 9, 1, 13, 0)
        assert SchedulingService.check_staff_conflict(session, staff.id, start3, end3) is True
    finally:
        session.query(TrainingSession).delete()
        session.query(Client).delete()
        session.query(Service).delete()
        session.query(Staff).delete()
        session.commit()
        session.close()