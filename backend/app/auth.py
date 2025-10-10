import bcrypt

def hash_password(password:str):
    hashed_pwd = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    return hashed_pwd

def validate_password(password: str , hashed_pwd: bytes):
    return bcrypt.checkpw(password.encode('utf-8'), hashed_pwd)

