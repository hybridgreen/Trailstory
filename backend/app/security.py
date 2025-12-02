import bcrypt
import hashlib
import jwt
import secrets
from datetime import datetime, timedelta, timezone
from .config import config
from .errors import AuthenticationError
import re
from db.queries.one_time_tokens import revoke_one_time_token, get_one_time_token


class JWTPayload:
    iss: str
    sub: str
    iat: datetime
    exp: datetime


def hash_password(password: str):
    hashed_pwd = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    return hashed_pwd


def verify_password(password: str, hashed_pwd: bytes):
    return bcrypt.checkpw(password.encode("utf-8"), hashed_pwd)


def validate_email(email):
    email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    if not re.match(email_pattern, email):
        raise ValueError("Invalid email")


def validate_password(password):
    password_pattern = r"^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9]).{8,}$"
    if not re.match(password_pattern, password):
        raise ValueError("Weak Password")


def make_JWT(user_id: str):
    payload = {
        "iss": "trailstory",
        "sub": user_id,
        "iat": datetime.now(tz=timezone.utc),
        "exp": datetime.now(tz=timezone.utc) + timedelta(hours=1),
    }
    return jwt.encode(payload, config.auth.secret, algorithm="HS256")


def verify_JWT(token: str):
    try:
        payload = jwt.decode(token, config.auth.secret, algorithms="HS256")

        if payload["iss"] != "trailstory":
            raise AuthenticationError("Invalid claim")
        return payload["sub"]
    except jwt.ExpiredSignatureError as e:
        raise AuthenticationError("Token Expired") from e
    except Exception as e:
        raise AuthenticationError from e


def create_refresh_Token():
    return secrets.token_hex(256)


def create_one_time_token():
    return secrets.token_urlsafe(32)


def hash_token(token: str):
    return hashlib.sha256(token.encode()).hexdigest()


def verify_onetime_token(token: str):
    hashed_input = hash_token(token)
    stored_token = get_one_time_token(hashed_input)
    print(stored_token.revoked)
    if stored_token.revoked or stored_token.expires_at < datetime.now():
        raise AuthenticationError("Invalid or expired token")
    revoke_one_time_token(stored_token.id)
    return stored_token.user_id
