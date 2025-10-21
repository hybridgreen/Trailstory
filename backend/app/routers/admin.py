from typing import Annotated
from fastapi import APIRouter, Depends
from app.dependencies import get_bearer_token
from app.config import config 
from app.errors import UnauthorizedError, DatabaseError
from db.schema import engine, Base

admin_router = APIRouter(
    prefix='/admin',
    tags=["Administrator"]
)

@admin_router.post('/reset', status_code= 204)
async def handler_reset(authorization : Annotated[str, Depends(get_bearer_token)]):
    if config.auth.admin_token != authorization:
        raise UnauthorizedError('Invalid admin token')
    if config.environment =='PROD':
        raise UnauthorizedError('Endpoint not available in production')
    try:
        Base.metadata.drop_all(bind= engine) 
        Base.metadata.create_all(bind= engine)
    except Exception as e:
        raise DatabaseError(f'Error while resetting the Database: {str(e)}') from e