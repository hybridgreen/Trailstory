from db.schema import User, engine
from sqlalchemy.orm import Session
from sqlalchemy.exc import *
from sqlalchemy import select, update, delete, insert
from app.errors import *

def create_user(user_data):
    try: 
        with Session(engine) as session:
            new_user = User(**user_data)
            session.add(new_user)
            session.commit()
            session.refresh(new_user)
            return new_user
    except IntegrityError as e:
        raise ValueError(f"User already exists")
    except Exception as e:
        raise DatabaseError(f"Internal database Error: {e}")
        
def get_user_by_id(user_id:str):
        with Session(engine) as session:
            user = session.get(User, user_id)
            if not user:
                raise UserNotFoundError(f"User with id {user_id} not found.")
            return user
        
def get_user_by_username(username:str):
    try:
        with Session(engine) as session:
            query = select(User).where(User.username == username)
            user = session.scalars(query).one()
            return user
    except NoResultFound:
        raise UserNotFoundError(f"User with name {username} not found.")
    except Exception as e:
        raise DatabaseError(f"Internal database Error: {e}")
    
def get_user_by_email(email:str):
    try:
        with Session(engine) as session:
            query = select(User).where(User.email == email)
            user = session.scalars(query).one()
            return user
    except NoResultFound:
        raise UserNotFoundError(f"User with name {email} not found.")
    except Exception as e:
        raise DatabaseError(f"Internal database Error: {e}")

def delete_user(user_id: str):
    try:
        with Session(engine) as session:
            query = delete(User).where(User.id == user_id)
            user = session.execute(query)
            session.commit()
    except Exception as e:
        raise DatabaseError(f"Internal database Error: {e}")
    
def update_user(user_id: str, user_data):
    try:
        with Session(engine) as session:
            query = update(User).where(User.id == user_id).values(user_data.dict())
            session.execute(query)
            updated_user = session.get(User, user_id)
            return updated_user
    except IntegrityError:
        raise ValueError(f"This username or email is already taken")
    except Exception as e:
        raise DatabaseError(f"Internal database Error: {e}")
    pass