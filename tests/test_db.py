from sqlalchemy import create_engine

DATABASE_URL = "postgresql+psycopg2://postgres:NvSTS2@localhost:5432/club_db"

engine = create_engine(DATABASE_URL, echo=False)
with engine.connect() as conn:
    result = conn.execute("SELECT version();")
    print(result.scalar())