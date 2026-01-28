from typing import Annotated
from fastapi import Header, Request, Depends
from app.security import verify_JWT
from db.schema import User
from db.queries.users import get_user_by_id
from app.errors import AuthenticationError, UnauthorizedError
from app.services.email_services import (
    send_password_reset_email,
    send_password_changed_email,
    send_verify_email,
    send_welcome_email,
)
from app.config import config


async def get_auth_user(authorization: Annotated[str, Header()] = None):
    if not authorization:
        raise AuthenticationError("Missing authorization header")
    parts = authorization.strip().split(" ")
    if parts[0] != "Bearer":
        raise AuthenticationError("Missing bearer symbol")
    user_id = verify_JWT(parts[1])

    return get_user_by_id(user_id)


def block_guest(req: Request, auth_user: Annotated[User, Depends(get_auth_user)]):
    if (
        req.method in ["POST", "PUT", "DELETE"]
        and auth_user.email == "guest@trailstory.com"
        and config.environment == "PROD"
    ):
        raise UnauthorizedError("Action not allowed in guest mode")


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
