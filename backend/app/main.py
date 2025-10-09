from fastapi import FastAPI
from db.queries.users import create_user
from db.schema import engine, Base
from pydantic import BaseModel
from datetime import date


app = FastAPI()
Base.metadata.create_all(bind= engine)


class User(BaseModel):
    email: str
    username: str
    firstname : str | None
    lastname : str | None



@app.get('/')
def root():
    return{"Welcome to Trailstory"}


@app.post('/users')
async def handler_create_user(user:User):
    try:
        create_user()
        return {"Hello from create"}
    except:
        return{"Welcome to Trailstory"}

@app.get('/users/{id}')
async def handler_get_user(user_id:str):
    pass
