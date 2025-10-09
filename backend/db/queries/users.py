from db.schema import User, engine
from sqlalchemy.orm import Session


def create_user():
    with Session(engine) as session:
        spongebob = User(
            email = 'spongenbob@pineapple.com',
            username = 'spongey',
        )
        session.add(spongebob)
        session.commit()
        
def get_user():
    pass