import bcrypt
import jwt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from db.schema import User
from datetime import datetime, timedelta, timezone
from .config import config
from .errors import *

class JWTPayload():
    iss: str
    sub: str
    iat: datetime
    exp: datetime

def hash_password(password:str):
    hashed_pwd = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    return hashed_pwd

def validate_password(password: str , hashed_pwd: bytes):
    return bcrypt.checkpw(password.encode('utf-8'), hashed_pwd)


def makeJWT(user_id: str):
    
    payload = {
        "iss":"trailstory",
        "sub":user_id,
        "iat": datetime.now(tz = timezone.utc),
        "exp": datetime.now(tz = timezone.utc) + timedelta(hours=1)
    }
    return jwt.encode(payload, config.auth.secret , algorithm="HS256")

def verifyJWT(user: User, token : str):
    try:
        payload = jwt.decode(token, config.auth.secret, algorithms="HS256")
        if payload['sub'] == user.id:
            return True
        return False
    except jwt.ExpiredSignatureError:
        raise AuthenticationError('Token Expired')
    except Exception as e:
        raise AuthenticationError(e)
