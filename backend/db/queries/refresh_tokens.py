from db.schema import refresh_tokens, User,  engine
from sqlalchemy.orm import Session
from sqlalchemy import exc as db_err
from sqlalchemy import select, update
from app.errors import AuthenticationError, DatabaseError

def register_refresh_token(u_id: str, rt: str ):
    try:
        with Session(engine) as session:
            new_token = refresh_tokens(token = rt, user_id = u_id)
            session.add(new_token)
            session.commit()
            session.refresh(new_token)
            return new_token
    except db_err.IntegrityError as exc:
        raise ValueError("User already exists") from exc
    except Exception as e:
        raise DatabaseError(f"Internal database Error:{str(e)}") from e

def get_token(token:str):
    try:
        with Session(engine) as session:
            query = select(refresh_tokens).where(refresh_tokens.token == token)
            token_obj = session.scalars(query).one()
            return token_obj
    except db_err.NoResultFound as exc:
        raise AuthenticationError("Invalid token") from exc
    except Exception as e:
        raise DatabaseError(f"Internal database Error:{str(e)}") from e

def revoke_tokens_for_user(user_id:str):
    try:
        with Session(engine) as session:
            query = update(refresh_tokens).where(refresh_tokens.user_id == user_id).values(revoked = True)
            session.execute(query)
            session.commit()
    except Exception as e:
        raise DatabaseError(f"Internal database Error:{str(e)}") from e

def revoke_refresh_token(token_id:str):
    try:
        with Session(engine) as session:
            query = update(refresh_tokens). where(refresh_tokens.id == token_id).values(revoked = True )
            session.execute(query)
            session.commit()
            return 0
    except Exception as e:
        raise DatabaseError(f"Internal database Error:{str(e)}") from e