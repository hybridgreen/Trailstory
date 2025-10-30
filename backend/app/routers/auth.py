from typing import Annotated
from fastapi import APIRouter, Depends, Form
from fastapi.responses import JSONResponse
from db.queries.users import get_user_by_email, User
from db.queries.refresh_tokens import revoke_tokens_for_user,revoke_refresh_token, register_refresh_token, get_token,refresh_tokens
from app.security import make_JWT, validate_password, create_refresh_Token
from app.models import loginForm, LoginResponse, RefreshResponse
from app.dependencies import get_bearer_token
from app.config import config 
from app.errors import NotFoundError, AuthenticationError

"""
Future Auth endpoints
POST /auth/logout
POST auth/password/reset
POST /auth/password/reset/confirm
POST /auth/email/verify 
"""

auth_router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

@auth_router.post('/login', status_code= 200)
def loginHandler(form_data: Annotated[loginForm, Form()]) -> LoginResponse:
    try:
        user: User = get_user_by_email(form_data.email)
        
    except NotFoundError:
        raise AuthenticationError("Wrong email or password")
    
    if(validate_password(form_data.password, user.hashed_password)):
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
    
@auth_router.get('/refresh', status_code= 200)
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