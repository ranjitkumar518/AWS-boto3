# aws ec2 describe-instances will provide the list of instances with their status from CLI.

#!/usr/bin/env python
import boto3
ec2 = boto3.resource('ec2')
for instance in ec2.instances.all():
    print instance.id, instance.state
