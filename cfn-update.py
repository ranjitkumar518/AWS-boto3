#from future import print_function

from botocore.exceptions import ClientError, ParamValidationError
from datetime import date
import json
import time
import boto3
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

logger.info('Loading function')

client = boto3.client('cloudformation', region_name = 'us-west-2');

Parameters=[
   {
            'key': 'AMIKeyid',
            'UsePreviousValue': True
        },
	
]

def fetch_cft(stack_name) :
    try : 
        response = client.describe_stacks(
            StackName = stack_name
        )
        if len(response['Stacks']) > 0 :
            cur_stack = response['Stacks'][0]
            return {"Status" : True, "Tags" : cur_stack['Tags'] }
        else : 
            return {"Status" : True, "Tags" : []}
    except Exception as E:
        return {"Status" : False, "Tags" : []}

def handler(event,context) :
    stack_name = "dev-ec2-1570423532"
    try :
        today = date.today()
        today_date = today.strftime("%B %d, %Y")
        tags_info = fetch_cft(stack_name)
        if (tags_info['Status']) :
            tags = tags_info['Tags']
            for i in range(len(tags)): 
                if tags[i]['Key'] == 'date': 
                    del tags[i] 
                    break
            date_dict = {}
            date_dict['Key'] = 'date'
            date_dict['Value'] = today_date
            tags.append(date_dict)
            response = client.update_stack(StackName=stack_name, UsePreviousTemplate=True, Tags = tags, Parameters=Parameters)
            print "Stack Updated"
        else :
            print "No tags available"
    except Exception as E:
        print E
handler("","")
