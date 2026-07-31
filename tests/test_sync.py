def test_sync_history(session):
    from app.sync import sync_training_sessions
    from app.models import TrainingSession
    records = [
        {"external_id": "A1", "service_id": 1, "staff_id": 1, "client_id": 1,
         "start_at": datetime(2024,1,1,9,0), "end_at": datetime(2024,1,1,10,0)}
    ]
    sync_training_sessions(session, records)
    # проверяем, что появилась актуальная запись
    q = select(TrainingSession).where(TrainingSession.external_id=="A1", TrainingSession.is_actual==True)
    assert session.scalar(q) is not None