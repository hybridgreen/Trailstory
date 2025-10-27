from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.routers import users, auth, trips, admin
from .errors import *
from fastapi.middleware.cors import CORSMiddleware
# Clear database and recreate (Temporary)



app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.auth_router)
app.include_router(users.user_router)
app.include_router(trips.trip_router)
app.include_router(admin.admin_router)

@app.exception_handler(NotFoundError)
async def user_not_found_handler(req: Request, exc: NotFoundError):
    return JSONResponse(content={"detail": str(exc)}, status_code= 404)

@app.exception_handler(ValueError)
async def value_not_found_handler(req: Request, exc: ValueError):
    return JSONResponse(content={"detail": str(exc)}, status_code = 409)

@app.exception_handler(DatabaseError)
async def database_error_handler(req: Request, exc: DatabaseError):
    return JSONResponse(content={"detail": str(exc)}, status_code = 500)

@app.exception_handler(AuthenticationError)
async def auth_error_handler(req:Request, exc: AuthenticationError):   
    return JSONResponse(content={'detail': str(exc)}, status_code= 401)

@app.exception_handler(InvalidGPXError)
async def gpx_error_handler(req:Request, exc: InvalidGPXError):   
    return JSONResponse(content={'detail': str(exc)}, status_code= 400)
    
@app.exception_handler(InputError)
async def input_error_handler(req:Request, exc: InputError):   
    return JSONResponse(content={'detail': str(exc)}, status_code= 400)

@app.exception_handler(ServerError)
async def server_error_handler(req:Request, exc: ServerError):   
    return JSONResponse(content={'detail': str(exc)}, status_code= 500)

@app.get('/') #Should show signup page
def index():
    return{"Welcome to Trailstory"}

