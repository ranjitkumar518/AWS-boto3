#!/usr/local/bin/python
import boto3
import sys
import os
import json
import time

if len(sys.argv) != 2 :
	usage()
	sys.exit(0)

cluster_identifier = sys.argv[1]
current_region = sys.argv[2]

def db_available(cluster_identifier, current_region):
	print "\n ###### Checking status of Database: "+cluster_identifier+" in "+current_region+" ######\n"
	count = 0
	while(1) :
		client = boto3.client('rds', region_name=current_region)
		response = client.describe_db_instances(DBInstanceIdentifier=cluster_identifier)
		status = response['DBInstances'][0]['DBInstanceStatus']
		if status == 'available':
			print "DB status: "+cluster_identifier+" "+status+" "
			break
		count = count + 1
		if count <= 20 :
			time.sleep(10)
			continue
		break
	return status

db_available(cluster_identifier, current_region)
