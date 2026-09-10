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
    def create(session: Session, full_name, phone=None, email=None, birth_date=None):
        c = Client(full_name=full_name, phone=phone, email=email, birth_date=birth_date, status="new")
        session.add(c)
        session.commit()
        return c

    @staticmethod
    def update(session: Session, client_id: int, **kwargs):
        client = session.query(Client).filter(Client.id == client_id).one_or_none()
        if not client:
            raise ValueError("Client not found")
        for k, v in kwargs.items():
            setattr(client, k, v)
        session.commit()
        return client

    @staticmethod
    def update_status(session: Session, client_id: int, new_status: str) -> tuple[bool, str]:
        """
        Возвращает (True, "") при успехе,
        (False, "причина") при отказе.
        """
        client = session.query(Client).filter(Client.id == client_id).one_or_none()
        if not client:
            return False, "Клиент не найден."

        from app.models import TrainingSession

        # Нельзя закрыть клиента с активными тренировками
        if new_status == "closed":
            active_count = (
                session.query(TrainingSession)
                .filter(
                    TrainingSession.client_id == client_id,
                    TrainingSession.is_actual == True,
                    TrainingSession.status.in_(["planned", "completed"]),
                )
                .count()
            )
            if active_count > 0:
                return False, (
                        f"Нельзя закрыть клиента: есть {active_count} активных тренировок "
                        f"(запланированных или завершённых). Сначала отмените или удалите их."
                )

        # Нельзя заморозить клиента с запланированными тренировками
        if new_status == "frozen":
            planned_count = (
                session.query(TrainingSession)
                .filter(
                    TrainingSession.client_id == client_id,
                    TrainingSession.is_actual == True,
                    TrainingSession.status == "planned",
                )
                .count()
            )
            if planned_count > 0:
                return False, (
                    f"Нельзя заморозить клиента: есть {planned_count} запланированных тренировок. "
                    f"Сначала отмените или перенесите их."
            )

        client.status = new_status
        session.commit()
        return True, ""

    @staticmethod
    def delete(session: Session, client_id: int) -> bool:
        client = session.query(Client).filter(Client.id == client_id).one_or_none()
        if not client:
            return False
        session.delete(client)
        session.commit()
        return True


class StaffRepository:
    @staticmethod
    def get_all(session: Session):
        return session.query(Staff).all()

    @staticmethod
    def get_active(session: Session):
        return session.query(Staff).filter(Staff.is_active == True).all()

    @staticmethod
    def get_by_id(session: Session, staff_id: int):
        return session.query(Staff).filter(Staff.id == staff_id).one_or_none()

    @staticmethod
    def create(session: Session, **kwargs):
        staff = Staff(**kwargs)
        session.add(staff)
        session.commit()
        session.refresh(staff)
        return staff

    @staticmethod
    def update(session: Session, staff_id: int, **kwargs):
        staff = session.query(Staff).filter(Staff.id == staff_id).one_or_none()
        if not staff:
            return None
        for k, v in kwargs.items():
            setattr(staff, k, v)
        session.commit()
        return staff

    @staticmethod
    def delete(session: Session, staff_id: int) -> bool:
        staff = session.query(Staff).filter(Staff.id == staff_id).one_or_none()
        if not staff:
            return False
        session.delete(staff)  # удалим связанные schedule_slots
        session.commit()
        return True


class ServiceRepository:
    @staticmethod
    def get_all(session: Session):
        return session.query(Service).all()

    @staticmethod
    def get_active(session: Session):
        return session.query(Service).filter(Service.is_active == True).all()

    @staticmethod
    def create(session: Session, **kwargs):
        service = Service(**kwargs)
        session.add(service)
        session.commit()
        session.refresh(service)
        return service

    @staticmethod
    def get_by_id(session: Session, service_id: int):
        return session.query(Service).filter(Service.id == service_id).one_or_none()

    @staticmethod
    def update(session: Session, service_id: int, **kwargs):
        service = session.query(Service).filter(Service.id == service_id).one_or_none()
        if not service:
            return None
        for k, v in kwargs.items():
            setattr(service, k, v)
        session.commit()
        return service

    @staticmethod
    def delete(session: Session, service_id: int) -> bool:
        service = session.query(Service).filter(Service.id == service_id).one_or_none()
        if not service:
            return False
        session.delete(service)
        session.commit()
        return True


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
    def create(session: Session, **kwargs):
        slot = ScheduleSlot(**kwargs)
        session.add(slot)
        session.commit()
        session.refresh(slot)
        return slot

    @staticmethod
    def get_by_id(session: Session, slot_id: int):
        return session.query(ScheduleSlot).filter(ScheduleSlot.id == slot_id).one_or_none()

    @staticmethod
    def update(session: Session, slot_id, **kwargs):
        slot = session.query(ScheduleSlot).filter(ScheduleSlot.id == slot_id).one_or_none()
        if slot:
            for k, v in kwargs.items():
                setattr(slot, k, v)
            session.commit()
        return slot

    @staticmethod
    def delete(session: Session, slot_id: int) -> bool:
        slot = session.query(ScheduleSlot).filter(ScheduleSlot.id == slot_id).one_or_none()
        if not slot:
            return False
        session.delete(slot)
        session.commit()
        return True


class TrainingSessionRepository:
    @staticmethod
    def get_all(session: Session):
        return (
            session.query(TrainingSession)
            .filter(TrainingSession.is_actual == True)
            .order_by(TrainingSession.start_at.desc())
            .all()
        )

    @staticmethod
    def get_by_id(session: Session, training_id: int):
        return (
            session.query(TrainingSession)
            .filter(
                TrainingSession.id == training_id,
                TrainingSession.is_actual == True,
            )
            .one_or_none()
        )

    @staticmethod
    def create(session: Session, **kwargs):
        t = TrainingSession(**kwargs)
        session.add(t)
        session.commit()
        session.refresh(t)
        return t

    @staticmethod
    def update(session: Session, training_id: int, **kwargs):
        t = session.query(TrainingSession).filter(
            TrainingSession.id == training_id
        ).one_or_none()
        if not t:
            return None
        for k, v in kwargs.items():
            setattr(t, k, v)
        session.commit()
        return t

    @staticmethod
    def delete(session: Session, training_id: int) -> bool:
        t = session.query(TrainingSession).filter(
            TrainingSession.id == training_id
        ).one_or_none()
        if not t:
            return False
        session.delete(t)
        session.commit()
        return True

    @staticmethod
    def check_conflict(session: Session, staff_id: int, start_at, end_at,
                       exclude_id: int = None):
        """
        Возвращает список тренировок, пересекающихся по времени
        с заданным интервалом для указанного тренера.
        exclude_id — ID тренировки, которую исключаем из проверки
        (используется при редактировании, чтобы не найти саму себя).
        """
        query = session.query(TrainingSession).filter(
            TrainingSession.staff_id == staff_id,
            TrainingSession.is_actual == True,
            TrainingSession.status != "cancelled",
            TrainingSession.start_at < end_at,
            TrainingSession.end_at > start_at,
        )
        if exclude_id:
            query = query.filter(TrainingSession.id != exclude_id)
        return query.all()

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