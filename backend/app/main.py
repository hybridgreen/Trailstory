from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from db.schema import engine, Base
from app.routers import users, auth, trips
from .errors import *
# Clear database and recreate (Temporary)
#Base.metadata.drop_all(bind= engine) 
Base.metadata.create_all(bind= engine)


app = FastAPI()

app.include_router(auth.auth_router)
app.include_router(users.user_router)
app.include_router(trips.trip_router)


@app.exception_handler(NotFoundError)
async def user_not_found_handler(req: Request, exc: NotFoundError):
    return JSONResponse(content={"detail": str(exc)}, status_code= 404)

@app.exception_handler(ValueError)
async def user_not_found_handler(req: Request, exc: ValueError):
    return JSONResponse(content={"detail": str(exc)}, status_code = 401)

@app.exception_handler(DatabaseError)
async def database_error_handler(req: Request, exc: DatabaseError):
    return JSONResponse(content={"detail": str(exc)}, status_code = 500)

@app.exception_handler(AuthenticationError)
async def auth_error_handler(req:Request, exc: AuthenticationError):   
    return JSONResponse(content={'detail': str(exc)}, status_code= 401)

@app.exception_handler(InvalidGPXError)
async def auth_error_handler(req:Request, exc: InvalidGPXError):   
    return JSONResponse(content={'detail': str(exc)}, status_code= 400)
    
@app.exception_handler(InputError)
async def auth_error_handler(req:Request, exc: InputError):   
    return JSONResponse(content={'detail': str(exc)}, status_code= 400)


@app.get('/') #Should show signup page
def index():
    return{"Welcome to Trailstory"}

