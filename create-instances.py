#aws opsworks --region us-east-1 create-instance --hostname my_instance1 --instance-type m1.large --os "Amazon Linux"
#!/usr/bin/env python
import boto3
ec2 = boto3.resource('ec2')
instance = ec2.create_instances(
    ImageId='ami-1e299d7e',
    MinCount=1,
    MaxCount=1,
    InstanceType='t2.micro')
print instance[0].id
