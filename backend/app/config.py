import os
from dotenv import load_dotenv

load_dotenv()



def EnvOrThrow(key:str):
    var = os.getenv(key)
    if not var:
        raise KeyError(f"Missing environment variable {key}")
    return var

class DBConfig:
    def __init__(self, url: str):
        self.url = url

class AuthConfig:
    def __init__(self, secret: str):
        self.secret = secret

class APIConfig():
    def __init__(self, db: DBConfig, auth: AuthConfig):
        self.db = db
        self.auth = auth
            
            
config = APIConfig(
    db = DBConfig(url = EnvOrThrow('DB_URL')),
    auth = AuthConfig(secret=EnvOrThrow('SERVER_SECRET'))
)
