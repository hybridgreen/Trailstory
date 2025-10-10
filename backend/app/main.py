from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from db.schema import engine, Base
from app.routers import users
from .errors import * 
# Clear database and recreate (Temporary)
Base.metadata.drop_all(bind= engine) 
Base.metadata.create_all(bind= engine)

app = FastAPI()

app.include_router(users.auth_router)
app.include_router(users.user_router)

@app.exception_handler(UserNotFoundError)
async def user_not_found_handler(request: Request, exc: UserNotFoundError):
    return JSONResponse(content={"detail": str(exc)}, status_code= 404)

@app.exception_handler(ValueError)
async def user_not_found_handler(request: Request, exc: ValueError):
    return JSONResponse(content={"detail": str(exc)}, status_code = 400)

@app.exception_handler(DatabaseError)
async def database_error_handler(req: Request, exc: DatabaseError):
    return JSONResponse(content={"detail": str(exc)}, status_code = 500)


@app.get('/') #Should show signup page
def index():
    return{"Welcome to Trailstory"}

