import boto3
import os
import csv, json
import datetime
from dateutil.tz import tzutc
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

logger.info('Loading function')

# defining bucket name, region and config file name.
config_s3_region = os.environ['CONFIG_S3_REGION']
config_s3_bucket = os.environ['CONFIG_S3_BUCKET']
config_s3_key = os.environ['CONFIG_S3_KEY']

# file_path to download from file
file_path = '/tmp/' + config_s3_key

def read_s3_config():
    # Define the S3 client.
    s3_client = boto3.client(
        's3',
        config_s3_region,
    )

    # Download the config to /tmp
    s3_client.download_file(
        config_s3_bucket,
        config_s3_key,
        '/tmp/%s' % config_s3_key
    )
