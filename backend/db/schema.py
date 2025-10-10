from sqlalchemy import ForeignKey, String, create_engine, column
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from geoalchemy2 import Geometry

from datetime import date, datetime, timedelta
from uuid import uuid4

from dotenv import load_dotenv
import os


class Base(DeclarativeBase):
    pass

class TimestampMixin:
    created_at : Mapped[datetime] = mapped_column(default= lambda: datetime.now())
    updated_at : Mapped[datetime] = mapped_column(default= lambda: datetime.now(), onupdate= datetime.now)
    
class User(Base, TimestampMixin):
    __tablename__ = "users"
    id: Mapped[str] = mapped_column(primary_key=True, default= lambda : str(uuid4()))
    email: Mapped[str] = mapped_column(nullable= False, unique= True)
    username: Mapped[str] = mapped_column(nullable= False, unique= True)
    hashed_password: Mapped[bytes] = mapped_column(nullable= False)
    firstname : Mapped[str | None]
    lastname : Mapped[str | None]
    trips: Mapped[list['Trip']] = relationship(back_populates = "user")
    email_verified : Mapped[bool] = mapped_column (default= False)

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, name={self.username!r})"

class Trip(Base, TimestampMixin):
    __tablename__ = "trips"
    id: Mapped[str] = mapped_column(primary_key= True, default= lambda : str(uuid4()))
    user_id : Mapped[str] = mapped_column(ForeignKey("users.id", ondelete= "CASCADE"))
    title: Mapped[str]
    description: Mapped[str | None] = mapped_column(String(300))
    start_date: Mapped[date]
    end_date: Mapped[date]
    slug:Mapped[str]
    user: Mapped[User] = relationship(back_populates='trips')
    rides : Mapped [list['Ride']] = relationship( back_populates='trip')


class Ride(Base, TimestampMixin):
    __tablename__ = "ride"
    id: Mapped[str] = mapped_column(primary_key= True, default= lambda : str(uuid4()))
    trip_id : Mapped[str] = mapped_column(ForeignKey('trips.id', ondelete='CASCADE'))
    notes: Mapped[str]
    date: Mapped[str]
    distance : Mapped[float]
    elevation_gain : Mapped[int]
    moving_time : Mapped [timedelta]
    gpx_url: Mapped[str]
    route: Mapped[str] = mapped_column(Geometry('LINESTRING',))
    bounding_box: Mapped[str] = mapped_column(Geometry('POLYGON'))
    trip: Mapped[list['Trip']] = relationship(back_populates='rides') 
    
#class Photos(Base, TimestampMixin):
    #__tablename__ = "photos"
    #id: Mapped[str] = mapped_column(primary_key=True)
    #signed_url: Mapped[str]
    # * trip_id (foreign key)
    # * ride_id (foreign key, nullable - might not be tied to specific ride)
    # * user_id (foreign key)
    # * image_url (link)
    # * thumbnail_url (S3 link to resized version)
    # * caption (text)
    # * location (PostGIS POINT) - lat/lng from EXIF or manual pin
    # * taken_at (timestamp from EXIF)

  
load_dotenv()

connection_str = f"postgresql://server:{os.getenv('POSTGRES_PASSWORD')}@localhost/trailstory_db"
engine = create_engine(connection_str, echo= True, plugins= ['geoalchemy2'])



    