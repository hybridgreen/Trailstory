from pydantic import BaseModel, ConfigDict
from datetime import datetime, date

### User Models


class UserModel(BaseModel):
    email: str
    username: str
    password: str
    firstname: str | None = None
    lastname: str | None = None
    email_verified: bool = None


class UserUpdate(BaseModel):
    email: str | None = None
    username: str | None = None
    firstname: str | None = None
    lastname: str | None = None
    email_verified: bool | None = None


class UserResponse(BaseModel):
    id: str
    email: str
    username: str
    firstname: str | None
    lastname: str | None
    email_verified: bool
    created_at: datetime
    avatar_id: str | None

    model_config = ConfigDict(
        from_attributes=True
    )  # Allows conversion from SQLAlchemy model


### Authentication
class loginForm(BaseModel):
    email: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    user: UserResponse
    token_type: str | None
    expires_in: int | None


class RefreshResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str | None
    expires_in: int | None


### Trip Models
class TripDraft(BaseModel):
    title: str
    description: str | None
    start_date: date
    end_date: date | None = None


class TripModel(BaseModel):
    title: str
    description: str
    start_date: date
    end_date: date
    is_published: str | None = None


class TripResponse(BaseModel):
    id: str
    user_id: str
    title: str
    description: str
    start_date: date | None
    end_date: date | None
    total_distance: float | None
    total_elevation: float | None
    high_point: float | None
    route: str | None
    bounding_box: str | None
    slug: str | None
    is_published: bool

    model_config = ConfigDict(
        from_attributes=True
    )  # Allows conversion from SQLAlchemy model


class TripsResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )  # Allows conversion from SQLAlchemy model
    id: str
    user_id: str
    title: str
    description: str
    start_date: date | None
    slug: str | None
    is_published: bool
    thumbnail_id: str | None


### Ride Models
class RideResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )  # Allows conversion from SQLAlchemy model

    id: str
    trip_id: str
    title: str | None
    notes: str | None
    date: datetime
    distance: float
    elevation_gain: float
    high_point: float
    moving_time: float
    gpx_url: str | None
    route: str


class RideModel(BaseModel):
    title: str | None
    notes: str | None


### Complex models
class TripDetailResponse(BaseModel):
    trip: TripResponse
    rides: list[RideResponse]
