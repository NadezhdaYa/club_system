def test_capacity_limit(session):
    # создаём 4 сессии для одного тренера в одно время
    from app.models import TrainingSession
    from datetime import datetime, timedelta
    now = datetime(2024, 1, 1, 10, 0)
    for i in range(4):
        s = TrainingSession(staff_id=1, start_at=now, end_at=now+timedelta(minutes=60), is_actual=True, status="planned")
        session.add(s)
    session.commit()

    # 5‑я должна не пройти
    from app.services import TrainingService
    assert TrainingService.check_capacity(session, 1, now, now+timedelta(minutes=60)) is False