from db.schema import engine, Base
from app.config import config

if config.environment == "TEST":
    Base.metadata.create_all(bind=engine)