from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base, Client, Staff, Service
from config import DATABASE_URL
from datetime import date

engine = create_engine(DATABASE_URL)
TestingSession = sessionmaker(bind=engine)

def test_create_client():
    Base.metadata.create_all(engine)
    session = TestingSession()
    try:
        c = Client(
            full_name="Иванов Иван Иванович",
            phone="+79991234567",
            email="ivanov@test.ru",
            birth_date=date(1990, 5, 15),
            status="new"
        )
        session.add(c)
        session.commit()
        assert c.id is not None
        assert c.status == "new"
    finally:
        session.query(Client).delete()
        session.commit()
        session.close()

def test_create_staff():
    session = TestingSession()
    try:
        s = Staff(full_name="Петров Пётр", position="Тренер", is_active=True)
        session.add(s)
        session.commit()
        assert s.id is not None
        assert s.is_active is True
    finally:
        session.query(Staff).delete()
        session.commit()
        session.close()
