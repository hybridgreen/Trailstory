import boto3
import asyncio
import os
from botocore.config import Config
from fastapi import UploadFile
from app.config import config
from app.errors import  ServerError



s3 = boto3.resource(
    's3',
    aws_access_key_id=config.s3.key,
    aws_secret_access_key=config.s3.secret_key,
    region_name = config.s3.region
)

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

async def remove_from_s3(keys):
    for key in keys:
        try:
            result = await asyncio.to_thread(
                lambda: 
                    s3.Bucket(config.s3.bucket).Object(key).delete()
    )
            if result.get('DeleteMarker') or result.get('ResponseMetadata', {}).get('HTTPStatusCode') == 204:
                return True
            else:
                raise ServerError(f"Failed to delete object: {result}")
        except Exception as e:
            print(str(e))
            raise ServerError(str(e)) from e
    
    
    