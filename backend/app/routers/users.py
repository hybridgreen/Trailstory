from typing import Annotated
from fastapi import APIRouter, Depends, Form
from db.queries.users import User, delete_user, create_user, update_user, get_user_by_id
from db.queries.trips import get_user_trips
from db.queries.refresh_tokens import register_refresh_token
from app.security import make_JWT, hash_password, create_refresh_Token, validate_email, validate_password, verify_password
from app.models import LoginResponse, UserModel, UserResponse, UserUpdate, TripsResponse
from app.errors import *
from app.config import config 
from app.dependencies import get_auth_user
from app.email_services import send_password_changed_email

# todo endpoints:
# Update password
# Verify email

user_router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


@user_router.post('/', status_code= 201)
async def handler_create_user(user_data:Annotated[UserModel, Form()]) -> LoginResponse:

        validate_email(user_data.email)
        validate_password(user_data.password)
        
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

@user_router.get('/me/', status_code= 200) 
async def handler_get_current_user(
    authed_user: Annotated[User, Depends(get_auth_user)])-> UserResponse:
    return authed_user
   
@user_router.get('/{id}/', status_code= 200)
async def handler_get_user_id(id:str) -> UserResponse:
       user = get_user_by_id(id)
       return user

@user_router.get('/{user_id}/trips/', status_code= 200)
async def handler_get_trips(user_id: str) -> list[TripsResponse]:
    
    trips: list[TripsResponse] = get_user_trips(user_id)
    return trips

@user_router.put('/', status_code= 200)
async def handler_update_user(
    user_data: Annotated[UserUpdate, Form()],
    authed_user: Annotated[User, Depends(get_auth_user)])-> UserResponse:
    
    if user_data.email:
        validate_email(user_data.email)
    
    updated_user = user_data.model_dump(exclude_unset=True)
    user = update_user(authed_user.id,updated_user)
    return user

@user_router.put('/password/', status_code= 204)
async def handler_change_password(
    old_password: Annotated[str, Form()],
    new_password: Annotated[str, Form()],
    authed_user: Annotated[User, Depends(get_auth_user)]):
    
    if not verify_password(old_password, authed_user.hashed_password):
        raise AuthenticationError("Incorrect password")
    
    if verify_password(new_password, authed_user.hashed_password):
        raise AuthenticationError("Please choose a new password")
    
    validate_password(new_password)
    password_dict = {"hashed_password" : hash_password(new_password)}
    update_user(authed_user.id,password_dict)
    send_password_changed_email(authed_user.email, authed_user.username)

@user_router.delete('/', status_code= 204)
async def handler_delete_user( authed_user: Annotated[User, Depends(get_auth_user)]):
    delete_user(authed_user.id)
