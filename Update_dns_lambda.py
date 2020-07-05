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
route_53_zone_id = os.environ['ROUTE_53_ZONE_ID']
TopicArn = os.environ['TOPIC_ARN']
Environment = os.environ['ENVIRONMENT']

# file_path to download and read the dns records from file
file_path = '/tmp/' + config_s3_key

client = boto3.client('route53')
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

def update_dns_record():
    with open(file_path, "rt", encoding='ascii') as data:
        reader = csv.reader(data, delimiter=",")
        for source, target in reader:
            print(source, target)
            try:
                response = client.change_resource_record_sets(
                HostedZoneId = route_53_zone_id,
                ChangeBatch= {
                    'Comment': 'Update %s -> %s' % (source, target),
                    'Changes': [
                        {
                            'Action': 'UPSERT',
                            'ResourceRecordSet': {
                                'Name': source,
                                'Type': 'CNAME',
                                'TTL': 10,
                                'ResourceRecords': [{'Value': target}]
                        }
                }]
                })
                print(response['ChangeInfo'])
            except Exception as e:
                print(e)
