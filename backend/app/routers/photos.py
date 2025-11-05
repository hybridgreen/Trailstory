import secrets
import tempfile
import asyncio
import io
from uuid import uuid4
from PIL import Image
from typing import Annotated
from datetime import date
from fastapi import APIRouter, Depends, UploadFile, Form
from fastapi.concurrency import run_in_threadpool
from db.schema import Photo, User
from db.queries.photos import add_photo, get_trip_photos, update_photo
from db.queries.trips import get_trip
from app.config import config 
from app.dependencies import get_auth_user
from app.errors import UnauthorizedError, InputError, ServerError
from app.routers.trips import trip_router
from app.services.file_services import s3
import os 


photo_router = APIRouter(
    prefix="/photos",
    tags=["Photos"]
)

tempdir = tempfile.gettempdir()

def validate_photo(file: UploadFile):
    if file.size == 0 :
            raise InputError(f"File : {file.filename} is empty")
    if not file.filename.endswith(('.jpg','.png','.heic','.jpg')):
            raise InputError(f'File : {file.filename} has Invalid file type. Supported types: .jpeg, .png .heic')
    if file.size > config.limits.max_upload_size:
        raise InputError("Maximum file size exceeded. 15MB")
    if file.content_type not in ["image/jpeg", "image/png", "image/webp", "image/heic"]:
        raise InputError(f"Invalid content type header. Received: {file.content_type}")

@trip_router.get("/{trip_id}/photos", status_code=200)
def getPhotosHandler(trip_id: str):
    
    trip = get_trip(trip_id)
    photos = get_trip_photos(trip.id)
    
    return photos
    
@trip_router.post("/{trip_id}/photos", status_code= 201)
async def uploadPhotosHandler(
    trip_id: str, 
    files: list[UploadFile],
    auth_user: Annotated[User, Depends(get_auth_user)]
    ):
    
    trip = get_trip(trip_id)
    
    if len(files) > 30:
        raise InputError("Max number of images: 30")
    
    if trip.user_id != auth_user.id:
        raise UnauthorizedError("Trip does not belong to this user")
    
    for file in files:
        validate_photo(file)
    
    photos_li = []
    for file in files:
        # Path : tripid-rand(32)
        extension = os.path.splitext(file.filename)[1]
        content = await file.read()
        image = Image.open(io.BytesIO(content))
        width, height = image.size
            
        id = str(uuid4())
        key = f"trips/{trip_id}/photos/{id}{extension}"
        url = f"https://{config.s3.bucket}.{config.s3.region}.amazonaws.com/{key}"
        try:
            await asyncio.to_thread(
                lambda:s3.Bucket(config.s3.bucket).put_object(
                    Key=key,
                    Body=content,
                    ContentType=file.content_type)
            )
        except Exception as e:
            raise ServerError(str(e))
        
        photo_data = {
            "id": id,
            "url": url,
            "trip_id" : trip_id,
            "thumbnail_url" : None,
            "mime_type": file.content_type,
            "file_size": file.size,
            'h_dimm' : height,
            'w_dimm' : width,
            's3_key': key
        }
        db_photo = add_photo(Photo(**photo_data))
        photos_li.append(db_photo)
        
    return photos_li

@photo_router.post("/profile", status_code= 201)
async def uploadProfilePhotoHandler(
    file: UploadFile,
    auth_user: Annotated[User, Depends(get_auth_user)]
    ):
    
    validate_photo(file)
    
    extension = os.path.splitext(file.filename)[1]
    savePath = tempdir + f"{secrets.token_urlsafe(32)}{extension}"
    content = await file.read()
    image = Image.open(io.BytesIO(content))
    width, height = image.size
    with open(savePath, "wb") as f:
        f.write(content)
    
    
    photo_data = {
        "url": savePath,
        "user_id" : auth_user.id,
        "thumbnail_url" : None,
        "mime_type": file.content_type,
        "file_size": file.size,
        'h_dimm' : height,
        'w_dimm' : width,
        's3_key': None
    }
    
    db_photo = add_photo(Photo(**photo_data))
        
    return db_photo