#!/usr/local/bin/python
import boto3
import sys
import os
import json
from configparser import ConfigParser
import time

def db_available(cluster_identifier, failover_region):
	print "\n ###### Checking status of Database: "+cluster_identifier+" in "+failover_region+" ######\n"
	count = 0
	while(1) :
		client = boto3.client('rds', region_name=failover_region)
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
