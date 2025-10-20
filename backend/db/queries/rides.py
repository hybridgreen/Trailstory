from db.schema import Ride, engine
from sqlalchemy.orm import Session
from sqlalchemy import exc as db_err
from sqlalchemy import select, update, delete, insert
from app.errors import DatabaseError, NotFoundError

def create_ride(ride: Ride):
    try: 
        with Session(engine) as session:
            session.add(ride)
            session.commit()
            session.refresh(ride)
            return ride
    except db_err.IntegrityError as e:
        raise ValueError("Duplicate ride detected.") from e
    except Exception as e:
        raise DatabaseError(f"Internal database Error:{str(e)}") from e

def create_rides(rides: list[Ride]):
    try:
        with Session(engine) as session:
            session.add_all(rides)
            session.commit()
            for ride in rides:
                session.refresh(ride)
            return rides
    except db_err.IntegrityError as e:
        raise ValueError("Duplicate ride detected.") from e
    except Exception as e:
        raise DatabaseError(f"Internal database Error:{str(e)}") from e

def get_ride(ride_id: str):
    with Session(engine) as session:
        ride = session.get(Ride, ride_id)
        if not ride:
                raise NotFoundError(f"Trip with ID: {ride_id}, not found.")
        return ride

def get_trip_rides_asc(trip_ip:str):
    try:
        with Session(engine) as session:
            query = select(Ride).where(Ride.trip_id == trip_ip).order_by(Ride.date)
            rides = session.scalars(query).all()
            return rides
    except db_err.NoResultFound as e:
        raise NotFoundError(f"No rides found for trip")
    except Exception as e:
        raise DatabaseError(f"Internal database Error:{str(e)}") from e
    

def update_ride(ride_id: str, ride):
    try: 
        with Session(engine) as session:
            query = update(Ride).where(Ride.id == ride_id).values(ride)
            session.execute(query)
            session.commit()
            session.refresh(ride_id)
            return ride
    except Exception as e:
        raise DatabaseError(f"Internal database Error:{str(e)}") from e
    
def delete_ride(ride_id: str):
    try: 
        with Session(engine) as session:
            query = delete(Ride).where(Ride.id == ride_id)
            session.execute(query)
            session.commit()
    except Exception as e:
        raise DatabaseError(f"Internal database Error:{str(e)}") from e
    