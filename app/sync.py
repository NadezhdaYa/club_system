from datetime import datetime
from sqlalchemy import select, update
from app.models import TrainingSession

def sync_training_sessions(session, records):
    """
    records: список dict с ключами: external_id, service_id, staff_id, client_id, start_at, end_at
    Логика:
      - если external_id уже есть и запись актуальна -> обновляем data_to, is_actual=False у старой, вставляем новую
      - если нет -> вставляем новую
    """
    now = datetime.utcnow()
    for r in records:
        external_id = r["external_id"]
        # ищем актуальную запись с этим external_id (если есть)
        q = select(TrainingSession).where(
            TrainingSession.external_id == external_id,  # нужно добавить колонку external_id в модель
            TrainingSession.is_actual == True
        )
        old = session.scalar(q)
        if old:
            # помечаем старую как неактуальную
            old.data_to = now
            old.is_actual = False
            session.add(old)

        new_ts = TrainingSession(
            external_id=external_id,
            service_id=r["service_id"],
            staff_id=r["staff_id"],
            client_id=r["client_id"],
            start_at=r["start_at"],
            end_at=r["end_at"],
            data_from=now,
            is_actual=True
        )
        session.add(new_ts)
    session.commit()