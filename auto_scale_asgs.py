#!/usr/local/bin/python
import boto3
import sys
import os
import json
from configparser import ConfigParser
import time

if len(sys.argv) != 2 :
	usage()
	sys.exit(0)

env = sys.argv[1]
current_region = sys.argv[2]

def usage():
	print("Usage: "+__file__+" env current_region eg: "+__file__+" prf us-west-2")
	exit(1)

def get_asg(env, name, region):
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


def autoscale_to(asgname, region, min_number, max_number, desired_capacity):
	try:
		#print "Autoscaling "+asgname + ", min_number : "+min_number + ", max_number :"+max_number+",desired_capacity :"+desired_capacity
		client = boto3.client('autoscaling', region_name=region)
		response = client.update_auto_scaling_group(AutoScalingGroupName=str(asgname), MinSize=min_number, MaxSize=max_number,
								DesiredCapacity=desired_capacity)
		print response
	except Exception as E:
		print E

# file_name = env+"/"+env+"_failover_config.json"
file_name = file_name = "elb_config.json"

# Read the config from file_name
with open(file_name) as json_data:
				data_object = json.load(json_data)
				json_data.close()
config_object = data_object['configdata']
elblist = config_object['elblist'].split(' ')
asg_list_current_region = asg_object['asg_list_current_region']

for each_asg in asg_list_current_region:
	asg_id = get_asg(env, each_asg['name'], region, 'current')
	print "\n ###### Proceeding ASG scaling down "+asg_id+" in: "+current_region+" "
	autoscale_to(asg_id, current_region, int(each_asg['min_value']),int(each_asg['max_value']),int(each_asg['desired_value']))
