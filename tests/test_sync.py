from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base, Client, Staff, Service, TrainingSession
from config import DATABASE_URL
from datetime import datetime
from app.sync import sync_training_sessions

engine = create_engine(DATABASE_URL)
TestingSession = sessionmaker(bind=engine)

def test_sync_inserts_and_updates():
    session = TestingSession()
    try:
        staff = Staff(full_name="Тренер Синх", position="Тренер", is_active=True)
        service = Service(name="Пилатес", price=1500, duration_minutes=60, is_active=True)
        client = Client(full_name="Клиент Синх", status="active")
        session.add_all([staff, service, client])
        session.commit()

        # Первая синхронизация — вставка
        records_v1 = [{
            "external_id": "ext-001",
            "service_id": service.id,
            "staff_id": staff.id,
            "client_id": client.id,
            "start_at": datetime(2026, 9, 5, 10, 0),
            "end_at": datetime(2026, 9, 5, 11, 0),
            "status": "planned"
        }]
        result1 = sync_training_sessions(session, records_v1, source="test")
        assert result1["inserted"] == 1
        assert result1["updated"] == 0

        # Проверяем, что запись актуальна
        actual = session.query(TrainingSession).filter(
            TrainingSession.external_id == "ext-001",
            TrainingSession.is_actual == True
        ).one()
        assert actual.start_at == datetime(2026, 9, 5, 10, 0)

        # Вторая синхронизация — обновление (изменилось время)
        records_v2 = [{
            "external_id": "ext-001",
            "service_id": service.id,
            "staff_id": staff.id,
            "client_id": client.id,
            "start_at": datetime(2026, 9, 5, 12, 0),
            "end_at": datetime(2026, 9, 5, 13, 0),
            "status": "planned"
        }]
        result2 = sync_training_sessions(session, records_v2, source="test")
        assert result2["inserted"] == 1
        assert result2["updated"] == 1

        # Старая версия помечена неактуальной
        old = session.query(TrainingSession).filter(
            TrainingSession.external_id == "ext-001",
            TrainingSession.is_actual == False
        ).one()
        assert old.data_to is not None
        assert old.start_at == datetime(2026, 9, 5, 10, 0)

        # Новая версия актуальна
        new = session.query(TrainingSession).filter(
            TrainingSession.external_id == "ext-001",
            TrainingSession.is_actual == True
        ).one()
        assert new.start_at == datetime(2026, 9, 5, 12, 0)
    finally:
        session.query(TrainingSession).delete()
        session.query(Client).delete()
        session.query(Service).delete()
        session.query(Staff).delete()
        session.commit()
        session.close()