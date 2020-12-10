### Prerequisites for the lambda to run
## lambda env: Python 3.6
## Required IAM role access to Allow: cloudformation:DescribeStacks,  Allow: cloudformation:UpdateStack
## Replace $stack-name with your actual stack name

import boto3
cl = boto3.client('cloudformation')
def handler(event, context):
  new_ami_id = event.get('ami_id')
  rsp = cl.describe_stacks(StackName='$stack-name')
  for param in [p for p in rsp['Stacks'][0]['Parameters'] if p['ParameterKey'] == "AmiId"]:
    if param['ParameterValue'] != new_ami_id:
      print("Updating $stack-name with new AMI ID", new_ami_id)
      rsp = cl.update_stack(
        StackName='$stack-name',
        UsePreviousTemplate=True,
        Capabilities=['CAPABILITY_IAM'],
        Parameters=[
          # NOTE: Make sure to add any new parameters to this list!
          {'ParameterKey': 'AmiId', 'ParameterValue': new_ami_id},
          {'ParameterKey': 'InstanceType', 'UsePreviousValue': True},
          {'ParameterKey': 'KeyName', 'UsePreviousValue': True},
          {'ParameterKey': 'Name', 'UsePreviousValue': True},
          {'ParameterKey': 'PublicHostedZoneName', 'UsePreviousValue': True},
          {'ParameterKey': 'SubnetType', 'UsePreviousValue': True},
          {'ParameterKey': 'VpcId', 'UsePreviousValue': True},
          {'ParameterKey': 'SecurityGroupName', 'UsePreviousValue': True},
          {'ParameterKey': 'EnableRestacker', 'UsePreviousValue': True},
        ],
      )
      cl.get_waiter('stack_update_complete').wait(
        StackName='$stack-name',
        WaiterConfig={
          'Delay': 10,
          'MaxAttempts': 30,
        }
      )
      print("Stack update complete")
    else:
      print("$stack-name is already up to date")
