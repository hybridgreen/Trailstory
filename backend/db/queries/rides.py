from db.schema import Ride, engine
from sqlalchemy.orm import Session
from sqlalchemy import exc as db_err
from sqlalchemy import select, update, delete
from app.errors import DatabaseError

def create_ride(ride_data: Ride):
    try: 
        with Session(engine) as session:
            session.add(ride_data)
            session.commit()
            session.refresh(ride_data)
            return ride_data
    except db_err.IntegrityError as e:
        raise ValueError("Duplicate ride detected.") from e
    except Exception as e:
        raise DatabaseError(f"Internal database Error:{str(e)}") from e
    
def get_ride(ride_id: str):
    