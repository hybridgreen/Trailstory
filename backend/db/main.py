from sqlalchemy import create_engine
from dotenv import load_dotenv
import os


load_dotenv()
dbsecret = os.getenv("DB_SECRET")

connection_str = f"postgresql://yayao:{dbsecret}@localhost/trailstory_db"

engine = create_engine(connection_str)

db = engine.connect()