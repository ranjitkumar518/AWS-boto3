#!/usr/local/bin/python
import boto3
import sys
import os
import json
from configparser import ConfigParser
import time

def autoscale_to(asgname, region, min_number, max_number, desired_capacity):
	try:
		#print "Autoscaling "+asgname + ", min_number : "+min_number + ", max_number :"+max_number+",desired_capacity :"+desired_capacity
		client = boto3.client('autoscaling', region_name=region)
		response = client.update_auto_scaling_group(AutoScalingGroupName=str(asgname), MinSize=min_number, MaxSize=max_number,
								DesiredCapacity=desired_capacity)
		print response
	except Exception as E:
		print E
