import boto3
from app.config import config
from botocore.config import Config

my_config = Config(
    region_name = 'us-west-2',
    signature_version = 'v4',
    retries = {
        'max_attempts': 10,
        'mode': 'standard'
    }
)

s3client = boto3.client(
    's3',
    aws_access_key_id=config.s3.key,
    aws_secret_access_key=config.s3.secret_key,
    config = my_config
)