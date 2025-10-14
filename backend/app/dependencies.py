from typing import Annotated
from fastapi import Header
from app.security import verifyJWT
from app.errors import *
from db.queries.users import get_user_by_id

async def get_auth_token(authorization: Annotated[str, Header()] = None):
    parts = authorization.strip().split(' ')
    if parts[0] != 'Bearer':
        raise Exception('Invalid bearer symbol')
    user_id = verifyJWT(parts[1])
    return get_user_by_id(user_id)