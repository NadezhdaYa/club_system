from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Numeric, Date, CheckConstraint, \
    UniqueConstraint
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime

Base = declarative_base()

class Client(Base):
    __tablename__ = "clients"
    id = Column(Integer, primary_key=True)
    full_name = Column(String(255), nullable=False)
    phone = Column(String(50))
    email = Column(String(255))
    birth_date = Column(Date)
    status = Column(String(50), nullable=False, default="new")
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    sessions = relationship("TrainingSession", back_populates="client")

class Staff(Base):
    __tablename__ = "staff"
    id = Column(Integer, primary_key=True)
    full_name = Column(String(255), nullable=False)
    phone = Column(String(50))
    email = Column(String(255))
    position = Column(String(100))
    is_active = Column(Boolean, nullable=False, default=True)

    slots = relationship("ScheduleSlot", back_populates="staff")
    sessions = relationship("TrainingSession", back_populates="staff")

class Service(Base):
    __tablename__ = "services"
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    duration_minutes = Column(Integer, nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)

    sessions = relationship("TrainingSession", back_populates="service")

class ScheduleSlot(Base):
    __tablename__ = "schedule_slots"
    id = Column(Integer, primary_key=True)
    staff_id = Column(Integer, ForeignKey("staff.id", ondelete="CASCADE"), nullable=False)
    day_of_week = Column(Integer, nullable=False)
    start_time = Column(String, nullable=False)
    end_time = Column(String, nullable=False)
    max_clients = Column(Integer, nullable=False)

    __table_args__ = (
        CheckConstraint("day_of_week BETWEEN 1 AND 7", name="chk_day_range"),
        CheckConstraint("end_time > start_time", name="chk_time_range"),
        UniqueConstraint("staff_id", "day_of_week", "start_time", "end_time", name="uq_slot_staff_day_time"),
    )

    staff = relationship("Staff", back_populates="slots")


class TrainingSession(Base):
    __tablename__ = "training_sessions"
    id = Column(Integer, primary_key=True)
    external_id = Column(String(100))
    service_id = Column(Integer, ForeignKey("services.id"), nullable=False)
    staff_id = Column(Integer, ForeignKey("staff.id"), nullable=False)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    start_at = Column(DateTime, nullable=False)
    end_at = Column(DateTime, nullable=False)
    status = Column(String(50), nullable=False, default="planned")
    notes = Column(String)
    data_from = Column(DateTime)
    data_to = Column(DateTime)
    is_actual = Column(Boolean, nullable=False, default=True)

    __table_args__ = (
        CheckConstraint("end_at > start_at", name="chk_ts_time_range"),
    )

    client = relationship("Client", back_populates="sessions")
    staff = relationship("Staff", back_populates="sessions")
    service = relationship("Service", back_populates="sessions")

    @staticmethod
    def is_time_overlap(start1, end1, start2, end2):
        return start1 < end2 and start2 < end1