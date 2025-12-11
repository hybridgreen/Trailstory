from db.schema import engine, Base
from app.config import config
from sqlalchemy import text

with engine.connect() as conn:
    conn.execute(text("GRANT ALL PRIVILEGES ON DATABASE test_db TO admin"))
    conn.execute(text("GRANT ALL ON SCHEMA public TO admin"))
    conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis"))

    conn.commit()


if config.environment == "TEST" or config.environment == "DEV":
    Base.metadata.create_all(bind=engine)
