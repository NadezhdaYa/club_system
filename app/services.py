from datetime import timedelta
from app.repositories import TrainingSessionRepository

class SchedulingService:
    @staticmethod
    def check_staff_conflict(session, staff_id, start_at, end_at) -> bool:
        conflicts = TrainingSessionRepository.get_planned_for_staff(session, staff_id, start_at, end_at)
        return len(conflicts) == 0

    @staticmethod
    def check_group_limit(session, service_id, start_at, end_at, limit: int) -> bool:
        # упрощённо: считаем все актуальные "planned" сессии в этом интервале
        from models import TrainingSession as TS
        count = session.query(TS).filter(
            TS.service_id == service_id,
            TS.is_actual == True,
            TS.status == "planned",
            TS.start_at < end_at,
            TS.end_at > start_at
        ).count()
        return count < limit
