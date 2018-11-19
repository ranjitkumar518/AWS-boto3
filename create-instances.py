# aws opsworks --region us-east-1 create-instance --hostname my_instance1 --instance-type m1.large --os "Amazon Linux"
# aws ec2 run-instances --image-id ami-xxxxxxxx --count 1 --instance-type t2.micro --key-name MyKeyPair --security-group-ids sg-xxxxxxxx --subnet-id subnet-xxxxxxxx

#!/usr/bin/env python
import boto3
ec2 = boto3.resource('ec2')
instance = ec2.create_instances(
    ImageId='ami-1e299d7e',
    MinCount=1,
    MaxCount=1,
    InstanceType='m1.large')
print instance[0].id
