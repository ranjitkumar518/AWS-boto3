#!/usr/bin/env python3

import boto3
import sys

client = boto3.client('route53')
response = client.list_hosted_zones_by_name(DNSName='ecom.a.intuit.net')
zoneid = response['HostedZones'][0]['Id'].split('/')[2]
print zoneid
