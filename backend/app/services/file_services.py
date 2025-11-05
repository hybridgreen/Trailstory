import boto3
from app.config import config
from botocore.config import Config


s3 = boto3.resource(
    's3',
    aws_access_key_id=config.s3.key,
    aws_secret_access_key=config.s3.secret_key,
    region_name = config.s3.region
)