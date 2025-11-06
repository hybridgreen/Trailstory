from db.schema import Photo, engine
from sqlalchemy.orm import Session
from sqlalchemy import exc as db_err
from sqlalchemy import select, update, delete
from app.errors import DatabaseError, NotFoundError

def get_trip_photos(trip_id:str):
    try:
        with Session(engine) as session:
            query = select(Photo).where(Photo.trip_id == trip_id)
            photos = session.scalars(query).all()
            return photos
    except Exception as e:
        raise DatabaseError(f"Internal database Error:{str(e)}") from e
    
def get_photo(id:str):
    try:
        with Session(engine) as session:
            return session.get(Photo, id)
    except Exception as e:
        raise DatabaseError(f"Internal database Error:{str(e)}") from e
    
def add_photo(photo: Photo):
    try: 
        with Session(engine) as session:
            session.add(photo)
            session.commit()
            session.refresh(photo)
            return photo
    except Exception as e:
        raise DatabaseError(f"Internal database Error:{str(e)}") from e     

def delete_photo(id: str):
    try:
        with Session(engine) as session:
            session.get(Photo, id)
            query = delete(Photo).where(Photo.id == id)
            session.execute(query)
            session.commit()
            return
    except Exception as e:
        raise DatabaseError(f"Internal database Error:{str(e)}") from e
    
def update_photo(id: str, photo_data):
    try:
        with Session(engine) as session:
            query = update(Photo).where(Photo.id == id).values(**photo_data)
            session.execute(query)
            session.commit()
            photo = session.get(Photo, id)
            return photo
    except Exception as e:
        raise DatabaseError(f"Internal database Error:{str(e)}") from e