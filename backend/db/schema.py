from datetime import date, datetime, timedelta
import secrets
from uuid import uuid4
from sqlalchemy import ForeignKey, String, create_engine, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from geoalchemy2 import Geometry
from app.config import config


class Base(DeclarativeBase):
    pass

class TimestampMixin:
    created_at : Mapped[datetime] = mapped_column(default= lambda: datetime.now())
    updated_at : Mapped[datetime] = mapped_column(default= lambda: datetime.now(), onupdate= datetime.now)
    
class User(Base, TimestampMixin):
    __tablename__ = "users"
    id: Mapped[str] = mapped_column(primary_key=True, default= lambda : secrets.token_hex(8))
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
    __table_args__ = (UniqueConstraint("user_id","start_date"),)
    id: Mapped[str] = mapped_column(primary_key= True, default= lambda : secrets.token_hex(8))
    user_id : Mapped[str] = mapped_column(ForeignKey("users.id", ondelete= "CASCADE"))
    title: Mapped[str]
    description: Mapped[str | None] = mapped_column(String(3000))
    start_date: Mapped[date]
    end_date: Mapped[date | None]
    slug:Mapped[str] = mapped_column()
    total_distance: Mapped[float | None]
    total_elevation: Mapped[float| None]
    high_point: Mapped[float| None]
    route: Mapped[str | None] = mapped_column(Geometry('LINESTRING'),default= None)
    bounding_box: Mapped[str | None] = mapped_column(Geometry('POLYGON'), default= None)
    is_published: Mapped[bool] = mapped_column(default= False)
    user: Mapped[User] = relationship(back_populates='trips')
    rides : Mapped [list['Ride']] = relationship( back_populates='trip')


class Ride(Base, TimestampMixin):
    __tablename__ = "rides"
    __table_args__ = (UniqueConstraint("trip_id","date"),)
    id: Mapped[str] = mapped_column(primary_key= True, default= lambda : str(uuid4()))
    trip_id : Mapped[str] = mapped_column(ForeignKey('trips.id', ondelete='CASCADE'))
    title: Mapped[str | None]
    notes: Mapped[str| None]
    date: Mapped[date]
    distance : Mapped[float]
    elevation_gain : Mapped[float]
    high_point : Mapped[float]
    moving_time : Mapped [float]
    gpx_url: Mapped[str | None]
    route: Mapped[str] = mapped_column(Geometry('LINESTRING'))
    trip: Mapped[list['Trip']] = relationship(back_populates='rides')

class Photo(Base, TimestampMixin):
    __tablename__ = "photos"
    id: Mapped[str] = mapped_column(primary_key=True, default= lambda : str(uuid4()))
    url: Mapped[str]
    trip_id : Mapped[str| None] = mapped_column(ForeignKey('trips.id', ondelete='CASCADE'))
    user_id : Mapped[str| None] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'))
    thumbnail_url: Mapped[str | None]
    mime_type: Mapped[str]
    file_size: Mapped[int]
    h_dimm : Mapped[int|None]
    w_dimm : Mapped[int|None]
    s3_key: Mapped[str | None]
    taken_at: Mapped[str | None]

class refresh_tokens(Base):
    __tablename__ = "refresh_tokens"
    id: Mapped[str] = mapped_column(primary_key= True, default= lambda : str(uuid4()))
    token: Mapped[str] = mapped_column(unique=True)
    user_id : Mapped[str] = mapped_column(ForeignKey('users.id', ondelete="CASCADE"))
    created_at : Mapped[datetime] = mapped_column(default= lambda: datetime.now())
    expires_at : Mapped[datetime] = mapped_column(default= lambda: datetime.now() + timedelta(days= 30))
    revoked : Mapped[bool] = mapped_column(default= False)
    
class one_time_tokens(Base):
    __tablename__ = "onetime_tokens"
    id: Mapped[str] = mapped_column(primary_key= True, default= lambda : str(uuid4()))
    token: Mapped[str] = mapped_column(unique=True)
    type: Mapped[str] = mapped_column()
    user_id : Mapped[str] = mapped_column(ForeignKey('users.id', ondelete="CASCADE"))
    created_at : Mapped[datetime] = mapped_column(default= lambda: datetime.now())
    expires_at : Mapped[datetime] = mapped_column(default= lambda: datetime.now() + timedelta(hours=1))
    revoked : Mapped[bool] = mapped_column(default= False)


engine = create_engine(config.db.url, echo= config.db.echo_flag, plugins= ['geoalchemy2'])


    