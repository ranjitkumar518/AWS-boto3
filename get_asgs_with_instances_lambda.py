#!/usr/local/bin/python
import boto3

### get_asgs_with_instances_lambda.py : It is lambda function helps to get the running instances count based on environment and region
def get_asgs_with_instances(env_list,  region_list):
        identified_Asg_list = ""
        for each_region in region_list :
                client = boto3.client('autoscaling', region_name = each_region)
                paginator = client.get_paginator('describe_auto_scaling_groups')
                response_iterator = paginator.paginate()
                found_asgs= {}
                asg_found = False
                for each_env in env_list:
                        for asgs in response_iterator :
                                for each_group in asgs['AutoScalingGroups'] :
                                        if each_env in each_group['AutoScalingGroupName'] :
                                                asg_found = True
                                                asg_name = each_group['AutoScalingGroupName']
                                                if len(each_group['Instances']):
                                                        identified_Asg_list+= "Instances found in ASG with name : "+asg_name+" and with environment "+each_env+" in the region :"+each_region+"\n"
                        if not asg_found  :
                                print "No ASG found for environment :"+each_env

        return identified_Asg_list

def lambda_handler(event, context):
	region_list = ['us-east-2', 'us-west-2']
	env_list = ['dev','QA', 'IT']
	asg_data = get_asgs_with_instances(env_list, region_list)
	if asg_data :
		print asg_data
		file = open("asginfo.txt","w")
		file.write(asg_data)
		file.close()
		print "Data written to file"
	else :
		print "No ASGS identified"
