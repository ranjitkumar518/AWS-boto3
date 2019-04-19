#!/usr/bin/env python3

import boto3
import sys

client = boto3.client('route53')
## Update your DNS here
response = client.list_hosted_zones_by_name(DNSName='com.a.abc.net')
zoneid = response['HostedZones'][0]['Id'].split('/')[2]
print zoneid
