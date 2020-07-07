#!/usr/local/bin/python
import boto3
import sys
import os
import json
import time

if len(sys.argv) != 2 :
	usage()
	sys.exit(0)

env = sys.argv[1]
current_region = sys.argv[2]

def usage():
	print("Usage: "+__file__+" env current_region eg: "+__file__+" prf us-west-2")
	exit(1)

def get_asg(env, region):
	client = boto3.client('autoscaling', region_name = region)
	paginator = client.get_paginator('describe_auto_scaling_groups')
	response_iterator = paginator.paginate()
	count = 0
	print "\n Filtering Active ASG in "+current_region+" for "+env+"\n"
	for asgs in response_iterator :
		#import pdb; pdb.set_trace()
		for each_group in asgs['AutoScalingGroups'] :
			#if env in each_group['AutoScalingGroupName'] and name in each_group['AutoScalingGroupName'] and each_group['Tags'][0]['Value'] == 'Active':
      if env in each_group['AutoScalingGroupName'] and each_group['Tags'][0]['Value'] == 'Active':
				asg_id = each_group['Tags'][0]['ResourceId']
				count = count+1
	if count != 1:
		print "\n ******* "+env+" has more than one or No Autoscaling group found Active in "+current_region+", If required, please deploy ****** \n"
		#sys.exit(0)

	return "\n ******** "+env+" has no active ASG in "+current_region+" ********"

