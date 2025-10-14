
from pydantic import BaseModel, ConfigDict
from datetime import datetime

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
    user: UserResponse
    token_type: str | None
    expires_in: int | None
    