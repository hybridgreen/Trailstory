from typing import Annotated
from fastapi import APIRouter, Depends, Form, Query
from db.queries.users import get_user_by_email, User, update_user, get_user_by_id
from db.queries.refresh_tokens import revoke_tokens_for_user,revoke_refresh_token, register_refresh_token, get_token,refresh_tokens
from db.queries.one_time_tokens import register_reset_token, register_verify_token
from app.security import verify_onetime_token, make_JWT, verify_password, create_refresh_Token, create_one_time_token, hash_password, validate_password, hash_token
from app.models import loginForm, LoginResponse, RefreshResponse, UserModel
from app.dependencies import get_bearer_token
from app.config import config 
from app.errors import NotFoundError, AuthenticationError, ServerError
from app.dependencies import get_auth_user
from app.services.email_services import send_password_reset_email, send_password_changed_email, send_verify_email
import resend


resend.api_key = config.resend

auth_router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)
        
@auth_router.post('/login/', status_code= 200)
def loginHandler(form_data: Annotated[loginForm, Form()]) -> LoginResponse:
    try:
        user: User = get_user_by_email(form_data.email)
        
    except NotFoundError:
        raise AuthenticationError("Wrong email or password")
    
    if(verify_password(form_data.password, user.hashed_password)):
        access_token = make_JWT(user.id)
        refresh_token = register_refresh_token(user.id, create_refresh_Token())
        return {
            'access_token' : access_token,
            'refresh_token': refresh_token.token,
            'user': user,
            "token_type" : "Bearer",
            "expires_in" : config.auth.jwt_expiry
            }
    else:
        raise AuthenticationError("Wrong email or password")
    
@auth_router.get('/refresh/', status_code= 200)
def refresh_handler(token : Annotated[str, Depends(get_bearer_token)]) -> RefreshResponse:
    
    token: refresh_tokens = get_token(token)
    if token.revoked:
        revoke_tokens_for_user(token.user_id)
        raise AuthenticationError("Invalid token")
    access_token = make_JWT(token.user_id)
    refresh_token = register_refresh_token(token.user_id, create_refresh_Token())
    revoke_refresh_token(token.id)
    return {
        'access_token' : access_token,
        'refresh_token' :refresh_token.token,
        "token_type" : "Bearer",
        "expires_in" : config.auth.jwt_expiry
    }

@auth_router.post('/password/reset/', status_code= 200)
def reset_pwd_handler(email: Annotated[str, Form()]):
    try:
        user = get_user_by_email(email)
        token = create_one_time_token()
        register_reset_token(user.id, hash_token(token))
        email = send_password_reset_email(user.email, token)
    except NotFoundError:
        pass
    except Exception as e:
        raise ServerError(str(e))
    finally:
        return {
            "message": "If an account exists with that email, you will receive a password reset link shortly."
            }
        
@auth_router.post('/password/confirm/', status_code= 204)
def confirm_pwd_handler(token: str, password: Annotated[str, Form()]):
        user = get_user_by_id(verify_onetime_token(token))
        validate_password(password)
        password_dict = {"hashed_password" : hash_password(password)}
        update_user(user.id, password_dict)
        revoke_tokens_for_user(user.id)
        send_password_changed_email(user.email, user.username)       

    
@auth_router.post("/email/verify/confirm/", status_code= 204)
def verify_email_handler(token:str):
    user = get_user_by_id(verify_onetime_token(token))
    update_dict = {"email_verified" : True}
    update_user(user.id, update_dict)

@auth_router.post("/email/verify/", status_code= 204)
def verify_email_handler(authed_user: Annotated[User, Depends(get_auth_user)]):
    
    verification_token = create_one_time_token()
    register_verify_token(authed_user.id , verification_token)
    send_verify_email(authed_user.email, authed_user.username, verification_token)

    
        
    
        
        
        