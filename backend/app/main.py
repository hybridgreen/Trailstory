from fastapi import FastAPI, Request
from fastapi import HTTPException
from app.routers import users, auth, trips, admin, photos
from app.config import config
from .errors import (
    NotFoundError,
    DatabaseError,
    UnauthorizedError,
    AuthenticationError,
    InvalidGPXError,
    InputError,
    ServerError,
)
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from db.schema import engine, Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://trailstory.vercel.app",
        "https://trailstory.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.auth_router)
app.include_router(users.user_router)
app.include_router(trips.trip_router)
app.include_router(trips.rides_router)
app.include_router(photos.photo_router)

if config.environment == "TEST":
    app.include_router(admin.admin_router)


@app.exception_handler(NotFoundError)
async def user_not_found_handler(req: Request, exc: NotFoundError):
    raise HTTPException(detail=str(exc), status_code=404)


@app.exception_handler(ValueError)
async def value_not_found_handler(req: Request, exc: ValueError):
    raise HTTPException(detail=str(exc), status_code=409)


@app.exception_handler(DatabaseError)
async def database_error_handler(req: Request, exc: DatabaseError):
    raise HTTPException(detail=str(exc), status_code=500)


@app.exception_handler(UnauthorizedError)
async def unauth_error_handler(req: Request, exc: UnauthorizedError):
    raise HTTPException(detail=str(exc), status_code=403)


@app.exception_handler(AuthenticationError)
async def auth_error_handler(req: Request, exc: AuthenticationError):
    raise HTTPException(detail=str(exc), status_code=401)


@app.exception_handler(InvalidGPXError)
async def gpx_error_handler(req: Request, exc: InvalidGPXError):
    raise HTTPException(detail=str(exc), status_code=400)


@app.exception_handler(InputError)
async def input_error_handler(req: Request, exc: InputError):
    raise HTTPException(detail=str(exc), status_code=400)


@app.exception_handler(ServerError)
async def server_error_handler(req: Request, exc: ServerError):
    raise HTTPException(detail=str(exc), status_code=500)


@app.get("/")  # Should show signup page
def index():
    return {"Welcome to Trailstory"}
