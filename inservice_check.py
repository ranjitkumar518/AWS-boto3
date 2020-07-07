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
