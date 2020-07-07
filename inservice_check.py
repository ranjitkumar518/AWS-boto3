#!/usr/local/bin/python
import boto3
import sys
import os
import json
import time


def inservice_check(elb_list, env, region):
	"In service status"
	print "\n ############  Retrieving service status ############ \n"
	try:
		client = boto3.client('elb', region_name=region)
		for each_elb in elb_list:
			try:
				elb_name = each_elb+"-"+env
				print "\n service status for elb :  "+elb_name+" in "+region+" \n"
				response = client.describe_instance_health(
					LoadBalancerName=elb_name
				)

				if len(response['InstanceStates']):
					for each_instance in response['InstanceStates'] :
						print each_instance['InstanceId']+" =====> " + each_instance['State']
				else :
					print "\n ****** No Instances available. Please Check the services ******"

			except Exception as E:
				print E
				continue
	except Exception as E:
		print E

		# Program Main
if len(sys.argv) != 2 :
	usage()
	sys.exit(0)
env = sys.argv[1]
region = sys.argv[2]

# Config file name to load the list of elb
# file_name = env+"/"+env+"_failover_config.json"
file_name = file_name = "elb_config.json"

# Read the config from file_name
with open(file_name) as json_data:
				data_object = json.load(json_data)
				json_data.close()
config_object = data_object['configdata']
elblist = config_object['elblist'].split(' ')


############### inservice_check ###############
inservice_check(elblist, env, region)
