import boto3

def get_asg(env, name, region):
    client = boto3.client('autoscaling', region_name = region)
    paginator = client.get_paginator('describe_auto_scaling_groups')
    response_iterator = paginator.paginate()
    for asgs in response_iterator :
        for each_group in asgs['AutoScalingGroups'] :
            if env in each_group['AutoScalingGroupName'] and name in each_group['AutoScalingGroupName'] :
                return each_group['AutoScalingGroupName']
    return None

regions = ['us-east-2', 'us-west-2' ]
asg_info = {}

for each_region in regions:
    asg_info['ag_cmserver_'+each_region]= get_asg('dev', 'webserver', each_region)

print asg_info
