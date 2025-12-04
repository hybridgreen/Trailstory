from typing import Annotated
from fastapi import Header
from app.security import verify_JWT
from db.queries.users import get_user_by_id
from app.errors import AuthenticationError
from app.services.email_services import (
    send_password_reset_email,
    send_password_changed_email,
    send_verify_email,
    send_welcome_email
)

async def get_auth_user(authorization: Annotated[str, Header()] = None):
    if not authorization:
        raise AuthenticationError("Missing authorization header")
    parts = authorization.strip().split(" ")
    if parts[0] != "Bearer":
        raise AuthenticationError("Missing bearer symbol")
    user_id = verify_JWT(parts[1])
    return get_user_by_id(user_id)


async def get_bearer_token(authorization: Annotated[str, Header()]):
    parts = authorization.strip().split(" ")
    if parts[0].lower() != "bearer":
        raise Exception("Missing Bearer symbol")
    return parts[1]


def get_send_welcome_email():
    return send_welcome_email

def get_password_changed_email():
    return send_password_changed_email

def get_password_reset_email():
    return send_password_reset_email

def get_verify_email():
    return send_verify_email