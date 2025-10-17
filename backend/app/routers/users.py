import re
from typing import Annotated
from fastapi import APIRouter, Depends
from db.queries.users import User, delete_user, create_user, update_user, get_user_by_username, get_user_by_id
from db.queries.refresh_tokens import register_refresh_token
from app.security import make_JWT, hash_password, create_refresh_Token
from app.models import AuthResponse, UserModel, UserResponse, UserUpdate
from app.errors import *
from app.config import config 
from app.dependencies import get_auth_user


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
        db_User : UserResponse = create_user(User(**new_user))
        access_token = make_JWT(user_id= db_User.id)
        refresh_token = register_refresh_token(db_User.id, create_refresh_Token())
        return {
            'access_token' : access_token,
            'refresh_token': refresh_token.token,
            'user': db_User,
            "token_type" : "Bearer",
            "expires_in" : config.auth.jwt_expiry
            }

@user_router.get('/me') 
async def handler_get_current_user(authed_user: Annotated[User, Depends(get_auth_user)]) -> UserResponse:
    return authed_user

@user_router.get('/username/{username}')
async def handler_get_user_name(username:str) -> UserResponse:
       user = get_user_by_username(username)
       return user
   
@user_router.get('/{id}')
async def handler_get_user_id(id:str) -> UserResponse:
       user = get_user_by_id(id)
       return user
   
@user_router.put('/{id}')
async def handler_update_user(
    id:str,
    user_data: UserUpdate,
    authed_user: Annotated[User, Depends(get_auth_user)]) -> UserResponse:
    
    if authed_user.id != id:
        raise UnauthorizedError('Not allowed')
    
    if user_data.email or user_data.password:
        validateCredentials(user_data.email, user_data.password)
    
    updated_user = user_data.model_dump(exclude_unset=True, exclude='password')
    updated_user['hashed_password'] = hash_password(user_data.password)
    
    user = update_user(id,updated_user)
    return user

@user_router.delete('/{id}', status_code= 204)
async def handler_delete_user(id:str, authed_user: Annotated[User, Depends(get_auth_user)]):
    if authed_user.id != id:
        raise UnauthorizedError('Not allowed')
    delete_user(id)
    return
