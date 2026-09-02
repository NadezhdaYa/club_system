from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models import Client, Staff, Service, TrainingSession, ScheduleSlot
from datetime import datetime


class ClientRepository:
    @staticmethod
    def get_all(session: Session):
        return session.query(Client).all()

    @staticmethod
    def get_by_id(session: Session, client_id: int):
        return session.query(Client).filter(Client.id == client_id).one_or_none()

    @staticmethod
    def get_by_status(session: Session, status: str):
        return session.query(Client).filter(Client.status == status).all()

    @staticmethod
    def create(session: Session, full_name, phone=None, email=None,
               birth_date=None, status="new"):
        c = Client(full_name=full_name, phone=phone, email=email,
                   birth_date=birth_date, status=status)
        session.add(c)
        session.commit()
        return c

    @staticmethod
    def update(session: Session, client_id, **kwargs):
        c = session.query(Client).filter(Client.id == client_id).one_or_none()
        if c:
            for k, v in kwargs.items():
                setattr(c, k, v)
            session.commit()
        return c


class StaffRepository:
    @staticmethod
    def get_all(session: Session):
        return session.query(Staff).all()

    @staticmethod
    def get_active(session: Session):
        return session.query(Staff).filter(Staff.is_active == True).all()

    @staticmethod
    def create(session: Session, full_name, phone=None, email=None,
               position=None, is_active=True):
        s = Staff(full_name=full_name, phone=phone, email=email,
                  position=position, is_active=is_active)
        session.add(s)
        session.commit()
        return s


class ServiceRepository:
    @staticmethod
    def get_all(session: Session):
        return session.query(Service).all()

    @staticmethod
    def get_active(session: Session):
        return session.query(Service).filter(Service.is_active == True).all()

    @staticmethod
    def create(session: Session, name, price, duration_minutes, is_active=True):
        s = Service(name=name, price=price,
                    duration_minutes=duration_minutes, is_active=is_active)
        session.add(s)
        session.commit()
        return s


class ScheduleSlotRepository:
    @staticmethod
    def get_all(session: Session):
        return session.query(ScheduleSlot).all()

    @staticmethod
    def get_by_staff(session: Session, staff_id: int):
        return session.query(ScheduleSlot).filter(
            ScheduleSlot.staff_id == staff_id
        ).order_by(ScheduleSlot.day_of_week, ScheduleSlot.start_time).all()

    @staticmethod
    def create(session: Session, staff_id, day_of_week, start_time,
               end_time, max_clients):
        slot = ScheduleSlot(staff_id=staff_id, day_of_week=day_of_week,
                            start_time=start_time, end_time=end_time,
                            max_clients=max_clients)
        session.add(slot)
        session.commit()
        return slot


class TrainingSessionRepository:
    @staticmethod
    def get_planned_for_staff(session: Session, staff_id: int, start_at, end_at):
        return session.query(TrainingSession).filter(
            TrainingSession.staff_id == staff_id,
            TrainingSession.is_actual == True,
            TrainingSession.status == "planned",
            TrainingSession.start_at < end_at,
            TrainingSession.end_at > start_at
        ).all()

    @staticmethod
    def get_history_for_client(session: Session, client_id: int):
        return session.query(TrainingSession).filter(
            TrainingSession.client_id == client_id,
            TrainingSession.is_actual == True
        ).order_by(TrainingSession.start_at.desc()).all()

    @staticmethod
    def get_schedule_for_staff(session: Session, staff_id: int,
                               date_from=None, date_to=None):
        q = session.query(TrainingSession).filter(
            TrainingSession.staff_id == staff_id,
            TrainingSession.is_actual == True
        )
        if date_from:
            q = q.filter(TrainingSession.start_at >= date_from)
        if date_to:
            q = q.filter(TrainingSession.start_at <= date_to)
        return q.order_by(TrainingSession.start_at).all()


class ReportRepository:
    """Отчёты для диплома — три типа по ТЗ"""

    @staticmethod
    def clients_by_status(session: Session):
        """Отчёт: клиенты по статусу (с количеством)"""
        return session.query(
            Client.status,
            func.count(Client.id).label("count")
        ).group_by(Client.status).all()

    @staticmethod
    def staff_schedule(session: Session, staff_id: int,
                       date_from=None, date_to=None):
        """Отчёт: расписание тренера с привязкой услуг и клиентов"""
        q = session.query(
            TrainingSession.id,
            TrainingSession.start_at,
            TrainingSession.end_at,
            TrainingSession.status,
            Service.name.label("service_name"),
            Client.full_name.label("client_name"),
            Staff.full_name.label("staff_name")
        ).join(
            Service, TrainingSession.service_id == Service.id
        ).join(
            Client, TrainingSession.client_id == Client.id
        ).join(
            Staff, TrainingSession.staff_id == Staff.id
        ).filter(
            TrainingSession.staff_id == staff_id,
            TrainingSession.is_actual == True
        )
        if date_from:
            q = q.filter(TrainingSession.start_at >= date_from)
        if date_to:
            q = q.filter(TrainingSession.start_at <= date_to)
        return q.order_by(TrainingSession.start_at).all()

    @staticmethod
    def client_visit_history(session: Session, client_id: int):
        """Отчёт: история посещений клиента"""
        return session.query(
            TrainingSession.start_at,
            TrainingSession.end_at,
            TrainingSession.status,
            Service.name.label("service_name"),
            Staff.full_name.label("staff_name")
        ).join(
            Service, TrainingSession.service_id == Service.id
        ).join(
            Staff, TrainingSession.staff_id == Staff.id
        ).filter(
            TrainingSession.client_id == client_id,
            TrainingSession.is_actual == True
        ).order_by(TrainingSession.start_at.desc()).all()