from datetime import datetime
from sqlalchemy.orm import Session
from app.models import TrainingSession

def sync_training_sessions(session: Session, records: list[dict], source: str):
    now = datetime.utcnow()
    inserted = 0
    updated = 0

    for r in records:
        external_id = r["external_id"]
        existing = session.query(TrainingSession).filter(
            TrainingSession.external_id == external_id,
            TrainingSession.is_actual == True
        ).one_or_none()

        if existing:
            existing.is_actual = False
            existing.data_to = now
            updated += 1

        new_row = TrainingSession(
            external_id=r["external_id"],
            service_id=r["service_id"],
            staff_id=r["staff_id"],
            client_id=r["client_id"],
            start_at=r["start_at"],
            end_at=r["end_at"],
            status=r.get("status", "planned"),
            notes=r.get("notes"),
            data_from=r.get("data_from") or now,
            data_to=r.get("data_to"),
            is_actual=True
        )
        session.add(new_row)
        inserted += 1

    session.commit()
    return {"inserted": inserted, "updated": updated}