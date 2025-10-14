
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from db.queries.users import *
from app.security import *
from app.models import loginForm, AuthResponse, UserResponse

auth_router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

@auth_router.post('/login')
def index(form_data: loginForm) -> AuthResponse:
    try:
        user: UserResponse = get_user_by_email(form_data.email)
        
    except UserNotFoundError:
        return JSONResponse(content="Wrong username or password", status_code= 401)
    
    if(validate_password(form_data.password, user.hashed_password)):
        token = makeJWT(user.id)
        return {
            'access_token' : token,
            'user': user,
            "token_type" : "Bearer",
            "expires_in" : 3600
            }
    else:
        return JSONResponse(content="Wrong username or password", status_code= 401)