import boto3
import os
import csv, json
import datetime
from dateutil.tz import tzutc
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

logger.info('Loading function')

### Upload csv file in the s3 bucket with the list of dns records. Examplefile in repo: dns_records.csv

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
                
def fetch_dns_records():
    paginator = client.get_paginator('list_resource_record_sets')

    try:
        msg = ''
        source_zone_records = paginator.paginate(HostedZoneId=route_53_zone_id)
        for record_set in source_zone_records:
            for record in record_set['ResourceRecordSets']:
                with open(file_path, "rt", encoding='ascii') as data:
                    reader = csv.reader(data, delimiter=",")
                    for source, target in reader:
                        # Append dot to the record name
                        source = source + '.'
                        # if record['Name'] == source  and record['ResourceRecords'][0]['Value'] == target:
                        if record['Name'] == source :
                            msg = msg + '--------------------------------------------------------------------------------------------------------------------'
                            msg= msg + '\n'
                            # Append dns records into msg
                            msg = msg + 'Record Name --> '+record['Name']+', Record Value -->'+ record['ResourceRecords'][0]['Value']
                            msg= msg + '\n'
        print(msg)
        Subject = 'Updated DNS records for ' + Environment
        sns_notify (Subject, msg, TopicArn)

    except Exception as error:
        print('An error occurred getting records from zone {}:'.format(route_53_zone_id))
        print(str(error))
        raise
        
def sns_notify(Subject, msg, TopicArn):
    client = boto3.client('sns')
    response = client.publish(
    TopicArn = TopicArn,
    Message = msg,
    Subject = Subject
)
    
# Main function execution    
def lambda_handler(event, context):
    try:
        logger.info('Reading config file {}'.format(file_path))
        read_s3_config()
        logger.info('Updating dns records in file {}'.format(file_path))
        update_dns_record()
        logger.info('Fetching the dns records from R53')
        fetch_dns_records()
    except Exception as e:
        logger.error("Exception occurred.", exc_info=True)
        returnResponse = dict(statusMessage='Failed: {}'.format(e))
        return returnResponse
