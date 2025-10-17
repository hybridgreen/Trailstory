
from pydantic import BaseModel, ConfigDict
from datetime import datetime, date

### User Models 

class UserModel(BaseModel):
    email: str
    username: str | None = None
    password: str
    firstname : str | None = None
    lastname : str | None = None
    email_verified : bool = None

class UserUpdate(UserModel):
    email: str | None = None
    username: str | None = None
    password: str | None = None
    firstname : str | None = None
    lastname : str | None = None
    email_verified : bool | None = None

class UserResponse(BaseModel):
    id: str
    email: str
    username: str
    firstname: str | None
    lastname: str | None
    email_verified: bool
    created_at: datetime
    
    model_config = ConfigDict (from_attributes = True )# Allows conversion from SQLAlchemy model    

### Authentication
class loginForm(BaseModel):
    email: str
    password: str
    
class AuthResponse(BaseModel):
    access_token: str
    refresh_token: str
    user: UserResponse
    token_type: str | None
    expires_in: int | None

### Trip Models
class TripModel(BaseModel):
    title: str
    description: str | None
    start_date: date
    end_date: date | None = None


### Ride Models
class RideResponse(BaseModel):
    id: str
    trip_id : str
    title: str | None
    notes: str | None
    date: date
    distance : float
    elevation_gain : float
    high_point : float
    moving_time : float
    gpx_url: str | None