from sqlalchemy import select
from app.models import TrainingSession, Client, Staff, Service

class TrainingSessionRepo:
    @staticmethod
    def create(session, service_id, staff_id, client_id, start_at, end_at, status="planned", notes=None):
        ts = TrainingSession(
            service_id=service_id,
            staff_id=staff_id,
            client_id=client_id,
            start_at=start_at,
            end_at=end_at,
            status=status,
            notes=notes,
            data_from=session.bind.execute("SELECT NOW()").scalar(),
            is_actual=True
        )
        session.add(ts)
        session.flush()
        return ts