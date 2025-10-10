from pydantic import BaseModel
from datetime import date, datetime
from fastapi import HTTPException, APIRouter
from fastapi.responses import JSONResponse
from db.queries.users import *

class UserModel(BaseModel):
    email: str
    username: str
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

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

@router.post('')
async def handler_create_user(user_data:UserModel)-> UserResponse:
        new_user= create_user(user_data)
        return new_user

@router.get('/{username}')
async def handler_get_user_name(username:str) -> UserResponse:
       user = get_user_by_username(username)
       return user
   
@router.put('/{id}')
async def handler_update_user(id:str, user_data:UserModel):
    user = update_user(id, user_data)
    return user

@router.delete('/{id}', status_code= 204)
async def handler_delete_user(id:str):
    delete_user(id)
    return

