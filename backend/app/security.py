import bcrypt
import jwt
import secrets
from datetime import datetime, timedelta, timezone
from .config import config
from .errors import AuthenticationError

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

def make_JWT(user_id: str):
    
    payload = {
        "iss":"trailstory",
        "sub":user_id,
        "iat": datetime.now(tz = timezone.utc),
        "exp": datetime.now(tz = timezone.utc) + timedelta(hours=1)
    }
    return jwt.encode(payload, config.auth.secret , algorithm="HS256")

def verify_JWT(token : str):
    try:
        payload = jwt.decode(token, config.auth.secret, algorithms="HS256")
        
        if payload['iss'] != 'trailstory':
            raise AuthenticationError('Invalid claim')
        return payload['sub']
    except jwt.ExpiredSignatureError as e:
        raise AuthenticationError('Token Expired') from e
    except Exception as e:
        raise AuthenticationError from e

def create_refresh_Token():
    return secrets.token_hex(256)
