import secrets
import tempfile
import asyncio
import io
from uuid import uuid4
from PIL import Image
from typing import Annotated
from datetime import date
from fastapi import APIRouter, Depends, UploadFile, Form
from db.schema import Photo, User
from db.queries.photos import add_photo, get_trip_photos, update_photo, get_photo
from db.queries.trips import get_trip
from db.queries.users import get_user_by_id, update_user
from app.config import config 
from app.dependencies import get_auth_user
from app.errors import UnauthorizedError, InputError, ServerError
from app.routers.trips import trip_router
from app.routers.users import user_router
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

async def upload_to_s3(file:UploadFile, content:bytes, owner_id: str, id: str):
    extension = os.path.splitext(file.filename)[1]
    key = f"{owner_id}/{id}{extension}"
    try:
        await asyncio.to_thread(
            lambda:s3.Bucket(config.s3.bucket).put_object(
                Key=key,
                Body=content,
                ContentType=file.content_type)
        )
        
    except Exception as e:
        raise ServerError(str(e))
    
    return key


@trip_router.get("/{trip_id}/photos/", status_code=200)
def getPhotosHandler(trip_id: str):
    
    trip = get_trip(trip_id)
    photos = get_trip_photos(trip.id)
    
    links = []
    for photo in photos:
        links.append(photo)
        
    return links
    
@trip_router.post("/{trip_id}/photos/", status_code= 201)
async def uploadPhotosHandler(
    trip_id: str, 
    files: list[UploadFile],
    auth_user: Annotated[User, Depends(get_auth_user)]
    ):
    
    trip = get_trip(trip_id)
    print(f"Received {len(files)} files")
    
    if len(files) > 20:
        raise InputError("Max number of images: 20")
    
    if trip.user_id != auth_user.id:
        raise UnauthorizedError("Trip does not belong to this user")
    
    for file in files:
        validate_photo(file)
    
    photos_links = []
    
    for file in files:
        content = await file.read()
        item_id = str(uuid4())
        
        key = await upload_to_s3(file, content, trip_id, item_id)
        
        with Image.open(io.BytesIO(content)) as im:
            width, height = im.size
        

        photo_data = {
            "id": item_id,
            "trip_id" : trip_id,
            "mime_type": file.content_type,
            "file_size": file.size,
            'h_dimm' : height,
            'w_dimm' : width,
            's3_key': key
        }
        
        db_photo = add_photo(Photo(**photo_data))
        url = s3.meta.client.generate_presigned_url(
            'get_object',
            Params={'Bucket': config.s3.bucket, 'Key': db_photo.s3_key},
            ExpiresIn=3600)
        photos_links.append(url)
    
    return {"links": photos_links, "expiry": 3600}

@user_router.post("/avatar/", status_code= 201)
async def uploadProfilePhotoHandler(
    file: UploadFile,
    auth_user: Annotated[User, Depends(get_auth_user)]
    ):
    
    validate_photo(file)
    content = await file.read()
    item_id = str(uuid4()) 
    size = 120, 120
    
    
    with Image.open(io.BytesIO(content)) as im:
        im.thumbnail(size)
        buffer = io.BytesIO()
        im.save(buffer, format='JPEG')  # or 'PNG', etc.
        image_bytes = buffer.getvalue()
        key = await upload_to_s3(file, image_bytes, auth_user.id, item_id)
    
    photo = {
        "id": item_id,
        "user_id" : auth_user.id,
        "mime_type": file.content_type,
        "file_size": file.size,
        'h_dimm' : 20,
        'w_dimm' : 20,
        's3_key': key
    }
        
    db_photo = add_photo(Photo(**photo))
    update_user(auth_user.id, {"avatar_id": item_id})
    url = s3.meta.client.generate_presigned_url(
            'get_object',
            Params={'Bucket': config.s3.bucket, 'Key': db_photo.s3_key},
            ExpiresIn=3600)
    
    return url
    
@user_router.get("{user_id}/avatar/", status_code= 200)
def getAvatarHandler(user_id: str):
    user = get_user_by_id(user_id)
    photo = get_photo(user.avatar_id)
    
    url = s3.meta.client.generate_presigned_url(
            'get_object',
            Params={'Bucket': config.s3.bucket, 'Key': photo.s3_key},
            ExpiresIn=3600)
    
    return url
    
    