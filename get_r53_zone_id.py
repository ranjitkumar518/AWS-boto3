#!/usr/local/bin/python
import boto3
import sys
import json

def usage():
	print("Usage: "+__file__+" zone_type eg: "+__file__+" public")
	exit(1)

if len(sys.argv) != 1 :
	usage()
	sys.exit(0)
	
## Pass zonetype public/private to get zone ID
zone_type = sys.argv[1]

    
def get_zoneid(dns_name):
	try :
		client = boto3.client('route53')
		response = client.list_hosted_zones_by_name(
			DNSName=dns_name
		)
		zoneid = response['HostedZones'][0]['Id'].split('/')[2]
		return zoneid
	except Exception as E:
		return None

if zone_type == 'public':
    DOMAIN_SUFFIX="abc.a.xyz.com"
    ZONE_ID=get_zoneid(DOMAIN_SUFFIX)

else :
    DOMAIN_SUFFIX="abc.b.xyz.com"
    ZONE_ID=get_zoneid(DOMAIN_SUFFIX)
