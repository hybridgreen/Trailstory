import asyncio
import io
from uuid import uuid4
from PIL import Image
from typing import Annotated
from datetime import date
from fastapi import APIRouter, Depends, UploadFile, Form
from db.schema import Photo, User
from db.queries.photos import add_photo, get_trip_photos, update_photo, get_photo, delete_photo
from db.queries.trips import get_trip, update_trip
from db.queries.users import get_user_by_id, update_user
from app.config import config 
from app.dependencies import get_auth_user
from app.errors import UnauthorizedError, InputError, ServerError
from app.routers.trips import trip_router
from app.routers.users import user_router
from app.services.file_services import s3, upload_to_s3, remove_from_s3


photo_router = APIRouter(
    prefix="/photos",
    tags=["Photos"]
)


def validate_photo(file: UploadFile):
    if file.size == 0 :
            raise InputError(f"File : {file.filename} is empty")
    if not file.filename.endswith(('.jpg','.png','.heic','.jpeg')):
            raise InputError(f'File : {file.filename} has Invalid file type. Supported types: .jpeg, .png .heic')
    if file.size > config.limits.max_upload_size:
        raise InputError("Maximum file size exceeded. 15MB")
    if file.content_type not in ["image/jpeg", "image/png", "image/webp", "image/heic"]:
        raise InputError(f"Invalid content type header. Received: {file.content_type}")


# Generic photo endpoints
@photo_router.delete("/{photo_id}/", status_code= 204)
async def uploadPhotosHandler(
    photo_id: str, 
    auth_user: Annotated[User, Depends(get_auth_user)]
    ):
    
    photo = get_photo(photo_id)
    if photo.trip_id:
        trip = get_trip(photo.trip_id)
        if auth_user.id != trip.user_id:
            raise UnauthorizedError("Photo does not belong to user")
    if photo.user_id:
        user = get_user_by_id(photo.user_id)
        if auth_user.id != user.id:
            raise UnauthorizedError("Photo does not belong to user")
    
    if await remove_from_s3([photo.s3_key]):
        delete_photo(photo_id)
    
    
#Trip photos endpoints 

@trip_router.get("/{trip_id}/photos/", status_code=200)
def getPhotosHandler(trip_id: str):
    
    trip = get_trip(trip_id)
    photos = get_trip_photos(trip.id)
    
    links = {}
    for photo in photos:
        url = s3.meta.client.generate_presigned_url(
            'get_object',
            Params={'Bucket': config.s3.bucket, 'Key': photo.s3_key},
            ExpiresIn=3600)
        links[photo.id] = url
        
    return links
    
@trip_router.post("/{trip_id}/photos/", status_code= 201)
async def uploadPhotosHandler(
    trip_id: str, 
    files: list[UploadFile],
    auth_user: Annotated[User, Depends(get_auth_user)]
    ):
    
    trip = get_trip(trip_id)
    allowance = 20 - len(get_trip_photos(trip_id))
    
    if allowance <= 0 :
        raise InputError(f"File allowance exceeded. You can upload {allowance} more files")
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

@trip_router.put("/{trip_id}/thumbnail/", status_code= 204)
async def uploadPhotosHandler(
    trip_id: str, 
    files: list[UploadFile],
    auth_user: Annotated[User, Depends(get_auth_user)]
    ):
    
    trip = get_trip(trip_id)
    print(f"Received {len(files)} files")
    
    if trip.user_id != auth_user.id:
        raise UnauthorizedError("Trip does not belong to this user")
    
    for file in files:
        validate_photo(file)
    
    for file in files:
        content = await file.read()
        item_id = str(uuid4())
        size = 290, 192
        
        key = await upload_to_s3(file, content, trip_id, item_id)
        
        with Image.open(io.BytesIO(content)) as im:
            im.thumbnail(size)
            buffer = io.BytesIO()
            im.save(buffer, format='JPEG')  # or 'PNG', etc.
            image_bytes = buffer.getvalue()
            key = await upload_to_s3(file, image_bytes, auth_user.id, item_id)
            
        photo_data = {
            "id": item_id,
            "trip_id" : trip_id,
            "mime_type": file.content_type,
            "file_size": file.size,
            'h_dimm' : 192,
            'w_dimm' : 290,
            's3_key': key
        }
        
        db_photo = add_photo(Photo(**photo_data))
        update_trip(trip.id, {"thumbnail_id":db_photo.id})

### User photo endpoints
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
        'h_dimm' : 120,
        'w_dimm' : 120,
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
    
