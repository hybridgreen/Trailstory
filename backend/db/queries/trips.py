from db.schema import Trip, engine
from sqlalchemy.orm import Session
from sqlalchemy import exc as db_err
from sqlalchemy import select, update, delete, func
from app.errors import DatabaseError, NotFoundError


def create_trip(trip: Trip):
    try:
        with Session(engine) as session:
            session.add(trip)
            session.commit()
            session.refresh(trip)
            return trip
    except db_err.IntegrityError:
        raise ValueError("Mutiple trips cannot start on the same day.")
    except Exception as e:
        raise DatabaseError(f"Internal database Error:{str(e)}") from e


def get_user_trips(user_id):
    try:
        with Session(engine) as session:
            query = select(Trip).where(Trip.user_id == user_id)
            trips = session.scalars(query).all()
            return trips
    except db_err.NoResultFound as e:
        raise NotFoundError("No trip found for user") from e
    except Exception as e:
        raise DatabaseError(f"Internal database Error:{str(e)}") from e
    pass


def get_trip(trip_id):
    with Session(engine) as session:
        trip = session.get(Trip, trip_id)
        if not trip:
            raise NotFoundError(f"Trip with ID: {trip}, not found.")
        return trip

def get_total_trips():
    with Session(engine) as session:   
        count = session.scalar(select(func.count(Trip.id)))
        return count

def update_trip(trip_id: str, values: dict):
    try:
        with Session(engine) as session:
            query = update(Trip).where(Trip.id == trip_id).values(**values)
            session.execute(query)
            session.commit()
            return session.get(Trip, trip_id)
    except Exception as e:
        raise DatabaseError(f"Internal database Error:{str(e)}") from e


def delete_trip(trip_id: str):
    try:
        with Session(engine) as session:
            query = delete(Trip).where(Trip.id == trip_id)
            session.execute(query)
            session.commit()
    except Exception as e:
        raise DatabaseError(f"Internal database Error:{str(e)}") from e
