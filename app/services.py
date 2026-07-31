from sqlalchemy import func, select
from datetime import timedelta
from app.models import TrainingSession

class TrainingService:
    @staticmethod
    def check_capacity(session, staff_id, start_at, end_at):
        # считаем активные (is_actual) и не отменённые сессии в интервале
        q = (
            select(func.count(TrainingSession.id))
            .where(
                TrainingSession.staff_id == staff_id,
                TrainingSession.is_actual == True,
                TrainingSession.status != "cancelled",
                TrainingSession.start_at < end_at,
                TrainingSession.end_at > start_at
            )
        )
        count = session.scalar(q) or 0
        # лимит можно брать из schedule_slots или хардкодить для прототипа
        max_clients = 4  # например
        return count < max_clients