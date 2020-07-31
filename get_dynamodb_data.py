
import boto3
import csv, json, sys
from boto3.dynamodb.conditions import Key
from decimal import Decimal
import datetime
from datetime import timedelta

#sys.setdefaultencoding("UTF-8") #set the encode to utf8
fileInput = 'dynamodb_dev.json'
fileOutput = "dynamodb_dev.csv"
TableName = 'dev_order'


#import pdb;pdb.set_trace()
# dynamodb = boto3.client('dynamodb')
# paginator = dynamodb.get_paginator('scan')
# response_iterator = paginator.paginate(
#     TableName=TableName,
#     AttributesToGet=[
#         'orderNumber', 'status', 'creationTime', 'accountID'
#     ],
#     # Limit=10,
#     )
#### Working code
dynamodb = boto3.resource('dynamodb', region_name="us-west-2")
table = dynamodb.Table(TableName)
response = table.scan(
AttributesToGet=[
        'orderNumber', 'status', 'creationTime', 'accountID'
    ],
    Limit=10,
    )
print(response)


final_data= []
for da in response['Items']:
	if isinstance(da['creationTime'], Decimal):
		da['creationTime']=str(da['creationTime'])
	final_data.append(da)

if final_data:  
    with open(fileInput, 'w', encoding='utf-8') as f:
        json.dump(final_data, f, ensure_ascii=False, indent=4)
else:
    print("No data found in Response")
data_for_csv = []
for i in final_data:
    if i['status'] == 'SUBMITTED':
        your_dt = datetime.datetime.fromtimestamp(int(i['creationTime'])/1000)
        back_date = datetime.datetime.now()  + timedelta(days=-100)
        if your_dt > back_date:
            # i['user_readable_format'] = your_dt.strftime("%Y-%m-%d %H:%M:%S")        
            data_for_csv.append(i)
if data_for_csv:
    with open(fileOutput, 'w', encoding='utf8', newline='') as output_file:
        fc = csv.DictWriter(output_file,
                            fieldnames=data_for_csv[0].keys(),
   
                           )
        fc.writeheader()
        fc.writerows(data_for_csv)
else:
    print("No data found in last 30 days")


