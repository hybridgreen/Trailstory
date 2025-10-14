import re
from fastapi import APIRouter
from db.queries.users import *
from app.security import makeJWT, hash_password
from app.models import AuthResponse, UserModel, UserResponse


user_router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

@user_router.post('/')
async def handler_create_user(user_data:UserModel) -> AuthResponse:
        
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        password_pattern = r'^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9]).{8,}$'
        if not re.match(email_pattern, user_data.email):
            raise ValueError('Invalid email')
        if not re.match(password_pattern, user_data.password):
            raise ValueError('Weak Password')
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
   
@user_router.put('/{id}')
async def handler_update_user(id:str, user_data:UserModel):
    user = update_user(id, user_data)
    return user

@user_router.delete('/{id}', status_code= 204)
async def handler_delete_user(id:str):
    delete_user(id)
    return

