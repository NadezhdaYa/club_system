from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Numeric, Time, Date, func
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
    created_at = Column(DateTime, default=func.now())

class Staff(Base):
    __tablename__ = "staff"
    id = Column(Integer, primary_key=True)
    full_name = Column(String(255), nullable=False)
    phone = Column(String(50))
    email = Column(String(255))
    position = Column(String(100))
    is_active = Column(Boolean, nullable=False, default=True)

class Service(Base):
    __tablename__ = "services"
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    duration_minutes = Column(Integer, nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)

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