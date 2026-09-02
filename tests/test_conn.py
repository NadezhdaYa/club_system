from sqlalchemy import create_engine, text
from config import DATABASE_URL

#DATABASE_URL = "postgresql+psycopg2://postgres:NvSTS2@localhost:5432/club_db"
def test_connection():
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        assert result.scalar() == 1