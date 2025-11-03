import os
from dotenv import load_dotenv

load_dotenv()

def EnvOrThrow(key:str):
    var = os.getenv(key)
    if not var:
        raise KeyError(f"Missing environment variable {key}")
    return var

class DBConfig:
    def __init__(self, url: str, echo_flag: str):
        self.url = url
        self.echo_flag = echo_flag

class AuthConfig:
    def __init__(self, secret: str,admin_token: str, jwt_expiry: int = 3600):
        self.secret = secret
        self.jwt_expiry = jwt_expiry
        self.admin_token = admin_token

class APILimits:
    def __init__(self):
        self.max_upload_size = 15*(1<<20)

class APIConfig():
    def __init__(self,client: str, db: DBConfig, auth: AuthConfig, api_limits: APILimits, env: str, resend: str):
        self.client = client
        self.db = db
        self.auth = auth
        self.limits = api_limits
        self.environment = env
        self.resend = resend
       
            
if EnvOrThrow('ENVIRONMENT') == 'DEV':
    db_url = EnvOrThrow('TEST_DB_URL')

    echo_flag = True
if EnvOrThrow('ENVIRONMENT') == 'TEST':
    db_url = EnvOrThrow('TEST_DB_URL')
    echo_flag = False
elif EnvOrThrow('ENVIRONMENT') == 'PROD':
    db_url = EnvOrThrow('DB_URL')
    echo_flag = False
    client_url = EnvOrThrow("CLIENT_BASE_URL")
    
    
config = APIConfig(
    client = client_url,
    db = DBConfig(url = db_url, echo_flag= echo_flag),
    auth = AuthConfig(secret=EnvOrThrow('SERVER_SECRET'), admin_token= EnvOrThrow('ADMIN_TOKEN')),
    api_limits = APILimits(),
    env = EnvOrThrow('ENVIRONMENT'),
    resend= EnvOrThrow('RESEND_API_KEY')
)
