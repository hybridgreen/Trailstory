from db.schema import one_time_tokens, engine
from sqlalchemy.orm import Session
from sqlalchemy import exc as db_err
from sqlalchemy import select, update
from app.errors import AuthenticationError, DatabaseError
from datetime import datetime, timedelta


def register_reset_token(u_id: str, tkn: str):
    try:
        with Session(engine) as session:
            new_token = one_time_tokens(
                token=tkn,
                user_id=u_id,
                type="reset",
                expires_at=datetime.now() + timedelta(hours=1),
            )
            session.add(new_token)
            session.commit()
            session.refresh(new_token)
            return new_token
    except db_err.IntegrityError as exc:
        raise ValueError("Value already exists") from exc
    except Exception as e:
        raise DatabaseError(f"Internal database Error:{str(e)}") from e


def register_verify_token(u_id: str, tkn: str):
    try:
        with Session(engine) as session:
            new_token = one_time_tokens(
                token=tkn,
                user_id=u_id,
                type="verification",
                expires_at=datetime.now() + timedelta(hours=24),
            )
            session.add(new_token)
            session.commit()
            session.refresh(new_token)
            return new_token
    except db_err.IntegrityError as exc:
        raise ValueError("Value already exists") from exc
    except Exception as e:
        raise DatabaseError(f"Internal database Error:{str(e)}") from e


def get_one_time_token(token: str):
    try:
        with Session(engine) as session:
            query = select(one_time_tokens).where(one_time_tokens.token == token)
            token_obj = session.scalars(query).one()
            return token_obj
    except db_err.NoResultFound as exc:
        raise AuthenticationError("Invalid or expired token") from exc
    except Exception as e:
        raise DatabaseError(f"Internal database Error:{str(e)}") from e


def revoke_one_time_token(token_id: str):
    try:
        with Session(engine) as session:
            query = (
                update(one_time_tokens)
                .where(one_time_tokens.id == token_id)
                .values(revoked=True)
            )
            session.execute(query)
            session.commit()
            return 0
    except Exception as e:
        raise DatabaseError(f"Internal database Error:{str(e)}") from e
