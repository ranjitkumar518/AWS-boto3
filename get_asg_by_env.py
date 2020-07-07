#!/usr/local/bin/python
import boto3
import sys
import os
import json
import time


def usage():
	print("Usage: "+__file__+" env current_region failover_region eg: "+__file__+" prf us-west-2 us-east-2 2")
	exit(1)

def get_asg(env, region, region_type):
	client = boto3.client('autoscaling', region_name = region)
	paginator = client.get_paginator('describe_auto_scaling_groups')
	response_iterator = paginator.paginate()
	count = 0
	print "\n Filtering Active ASG in "+failover_region+" for "+env+"\n"
	for asgs in response_iterator :
		#import pdb; pdb.set_trace()
		for each_group in asgs['AutoScalingGroups'] :
			#if env in each_group['AutoScalingGroupName'] and name in each_group['AutoScalingGroupName'] and each_group['Tags'][0]['Value'] == 'Active':
      if env in each_group['AutoScalingGroupName'] and each_group['Tags'][0]['Value'] == 'Active':
				asg_id = each_group['Tags'][0]['ResourceId']
				count = count+1
	if count != 1 and region_type == 'failover':
		print "\n ******* "+env+" has more than one or No Autoscaling group found Active in "+failover_region+", If required, please deploy ****** \n"
		#sys.exit(0)

	return "\n ******** "+env+" has no active ASG in "+failover_region+" ********"
