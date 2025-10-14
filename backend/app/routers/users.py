import re
from typing import Annotated
from fastapi import APIRouter, Depends
from db.queries.users import *
from app.security import makeJWT, hash_password, verifyJWT
from app.models import AuthResponse, UserModel, UserResponse, UserUpdate
from app.errors import *
from app.dependencies import *


user_router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

def validateCredentials(email, password):
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    password_pattern = r'^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9]).{8,}$'
    if not re.match(email_pattern, email):
        raise ValueError('Invalid email')
    if not re.match(password_pattern, password):
        raise ValueError('Weak Password')

@user_router.post('/')
async def handler_create_user(user_data:UserModel) -> AuthResponse:
    
        validateCredentials(user_data.email, user_data.password)
    
        new_user = user_data.model_dump(exclude={'password'})
        
        new_user['hashed_password'] = hash_password(user_data.password)
        db_User : UserResponse = create_user(new_user)
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
   
@user_router.get('/{id}')
async def handler_get_user_id(username:str) -> UserResponse:
       user = get_user_by_id
       return user
   
@user_router.put('/{id}')
async def handler_update_user(
    id:str,
    user_data: UserUpdate,
    authed_user: Annotated[User, Depends(get_auth_token)]) -> UserResponse:
    
    if authed_user.id != id:
        raise UnauthorizedError('Not allowed')
    
    if user_data.email or user_data.password:
        validateCredentials(user_data.email, user_data.password)
    
    updated_user = user_data.model_dump(exclude_unset=True, exclude='password')
    updated_user['hashed_password'] = hash_password(user_data.password)
    
    user = update_user(id,updated_user)
    return user

@user_router.delete('/{id}', status_code= 204)
async def handler_delete_user(id:str, authed_user: Annotated[User, Depends(get_auth_token)]):
    if authed_user.id != id:
        raise UnauthorizedError('Not allowed')
    delete_user(id)
    return
