from db.schema import User, engine
from sqlalchemy.orm import Session
from sqlalchemy import exc as db_err
from sqlalchemy import select, update, delete
from app.errors import DatabaseError, UserNotFoundError

def create_user(user_data):
    try: 
        with Session(engine) as session:
            new_user = User(**user_data)
            session.add(new_user)
            session.commit()
            session.refresh(new_user)
            return new_user
    except db_err.IntegrityError as e:
        raise ValueError("User already exists") from e
    except Exception as e:
        raise DatabaseError("Internal database Error-") from e
        
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
    except db_err.NoResultFound as e:
        raise UserNotFoundError(f"User with name {username} not found.") from e
    except Exception as e:
        raise DatabaseError("Internal database Error-") from e
    
def get_user_by_email(email:str):
    try:
        with Session(engine) as session:
            query = select(User).where(User.email == email)
            user = session.scalars(query).one()
            return user
    except db_err.NoResultFound as e:
        raise UserNotFoundError(f"User with name {email} not found.") from e
    except Exception as e:
        raise DatabaseError("Internal database Error-") from e

def delete_user(user_id: str):
    try:
        with Session(engine) as session:
            query = delete(User).where(User.id == user_id)
            session.execute(query)
            session.commit()
    except Exception as e:
        raise DatabaseError("Internal database Error-") from e
    
def update_user(user_id: str, user_data):
    try:
        with Session(engine) as session:
            query = update(User).where(User.id == user_id).values(**user_data)
            session.execute(query)
            session.commit()
            updated_user = session.get(User, user_id)
            return updated_user
    except db_err.IntegrityError as e:
        raise ValueError("This username or email is already taken") from e
    except Exception as e:
        raise DatabaseError("Internal database Error-") from e