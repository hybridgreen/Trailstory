from pydantic import BaseModel
from datetime import date, datetime
from fastapi import HTTPException, APIRouter
from fastapi.responses import JSONResponse
from db.queries.users import *
from ..auth import *

class UserModel(BaseModel):
    email: str
    username: str
    password: str
    firstname : str | None = None
    lastname : str | None = None
    email_verified : bool = None

class UserResponse(BaseModel):
    id: str
    email: str
    username: str
    firstname: str | None
    lastname: str | None
    email_verified: bool
    created_at: datetime
    
    class Config:
        from_attributes = True # Allows conversion from SQLAlchemy model

user_router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

auth_router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

@user_router.post('/')
async def handler_create_user(user_data:UserModel) :
        new_user = user_data.model_dump(exclude={'password'})
        new_user['hashed_password'] = hash_password(user_data.password)
        db_User = create_user(new_user)
        token = makeJWT(user_id= db_User.id)
        return {
            'access_token' : token,
            'user': db_User,
            "token_type" : "Bearer",
            "expires_in" : 3600
            }

@user_router.get('/{username}')
async def handler_get_user_name(username:str) -> UserResponse:
       user = get_user_by_username(username)
       return user
   
@user_router.put('/{id}')
async def handler_update_user(id:str, user_data:UserModel):
    user = update_user(id, user_data)
    return user

@user_router.delete('/{id}', status_code= 204)
async def handler_delete_user(id:str):
    delete_user(id)
    return


class loginForm(BaseModel):
    username: str
    password: str

@auth_router.post('/login')
def index(form_data: loginForm):
    try:
        user = get_user_by_username(form_data.username)
    except UserNotFoundError:
        return JSONResponse(content="Invalid username or password", status_code= 401)
    
    if(validate_password(form_data.password, user.hashed_password)):
        token = makeJWT(user.id)
        return {
            'access_token' : token,
            'user': user,
            "token_type" : "Bearer",
            "expires_in" : 3600
            }
    else:
        return JSONResponse(content="Invalid username or password", status_code= 401)