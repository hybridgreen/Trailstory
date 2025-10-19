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
    def __init__(self, secret: str,admin_token: str, jwt_expiry: int = 3600):
        self.secret = secret
        self.jwt_expiry = jwt_expiry
        self.admin_token = admin_token

class APILimits:
    def __init__(self):
        self.max_upload_size = 25*(1<<20)

class APIConfig():
    def __init__(self, db: DBConfig, auth: AuthConfig, api_limits: APILimits, env: str):
        self.db = db
        self.auth = auth
        self.limits = api_limits
        self.environment = env
            
            
config = APIConfig(
    db = DBConfig(url = EnvOrThrow('DB_URL')),
    auth = AuthConfig(secret=EnvOrThrow('SERVER_SECRET'), admin_token= EnvOrThrow('ADMIN_TOKEN')),
    api_limits = APILimits(),
    env = EnvOrThrow('ENVIRONMENT')
)
