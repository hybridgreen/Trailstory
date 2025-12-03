from db.schema import engine, Base
from app.config import config
from sqlalchemy import text

with engine.connect() as conn:
    conn.execute(text("GRANT ALL PRIVILEGES ON DATABASE database_name TO username"))
    conn.execute(text("GRANT ALL ON SCHEMA public TO admin"))
    conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis"))
    
    conn.commit()


if config.environment == "TEST":
    Base.metadata.create_all(bind=engine)
    
