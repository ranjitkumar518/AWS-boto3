from __future__ import print_function

import os
import json
import boto3
import botocore.config
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

logger.info('Loading function')

code_pipeline = boto3.client('codepipeline')

def lambda_handler(event, context):
    try:
        logger.info('Received complete event {}'.format(event))
        logger.info('Received event {}'.format(event['CodePipeline.job']['data']['actionConfiguration']))
        job_data = event['CodePipeline.job']['data']
        jobId = event['CodePipeline.job']['id']

        if 'UserParameters' not in job_data['actionConfiguration']['configuration']:
            logger.error("UserParameters not found in pipeline configuration, please ensure to pass all required parameters in UserParameters for Promote stage")
            sendFailureCodepipeline(jobId, "UserParameters not found in pipeline configuration, please ensure to pass all required parameters in UserParameters for Promote stage")
            return

        user_parameters = job_data['actionConfiguration']['configuration']['UserParameters']
        decoded_parameters = json.loads(user_parameters)
        if not validatePipelineInputParameters(decoded_parameters):
            logger.error("Failed validation of pipeline input parameters, please ensure to pass all required parameters in UserParameters for Promote stage")
            sendFailureCodepipeline(jobId, "Failed validation of pipeline input parameters, please ensure to pass all required parameters in UserParameters for Promote stage")
            return

        asgServiceTag = decoded_parameters['ASGServiceTag']
        functionARN = decoded_parameters['FunctionARN']
        region = decoded_parameters['Region']
        targetAccountName = decoded_parameters['TargetAccountName']

        if targetAccountName == "dev":
            crossAccountRoleARN = os.environ['CROSS_ACCOUNT_ROLE_ARN_PREPROD']
        elif targetAccountName == "preprod":
            crossAccountRoleARN = os.environ['CROSS_ACCOUNT_ROLE_ARN_COMMERCE_DEV']           
        elif targetAccountName == "prod":
            crossAccountRoleARN = os.environ['CROSS_ACCOUNT_ROLE_ARN_PROD']

        logger.info('Found Cross Account Role ARN {}'.format(crossAccountRoleARN))
        sts = boto3.client('sts')
        assumedRole = sts.assume_role(
            RoleArn=crossAccountRoleARN,
            RoleSessionName='LambdaCrossAccountSession'
        )
        credentials = assumedRole['Credentials']
        accessKey = credentials['AccessKeyId']
        secretAccessKey = credentials['SecretAccessKey']
        sessionToken = credentials['SessionToken']

        lambdaRequestPayload = dict(ASGServiceTag=asgServiceTag)
        logger.info('Lambda Request Payload {}'.format(lambdaRequestPayload))

        cfg = botocore.config.Config(connect_timeout=420, read_timeout=420, retries={'max_attempts': 0})
        lambdaClient = boto3.client('lambda', config=cfg, region_name=region,
            aws_access_key_id=accessKey,
            aws_secret_access_key=secretAccessKey,
            aws_session_token=sessionToken)
        lambdaResponse = lambdaClient.invoke(
            FunctionName=functionARN,
            InvocationType='RequestResponse',
            Payload=json.dumps(lambdaRequestPayload)
        )
        lambdaResponsePayload = json.loads(lambdaResponse['Payload'].read())
        logger.info('Lambda Response Payload: {}'.format(lambdaResponsePayload))
        logger.info('Lambda Response StatusCode: {}'.format(lambdaResponse['StatusCode']))
        if lambdaResponse['StatusCode'] == 200 and 'statusMessage' in lambdaResponsePayload:
            if lambdaResponsePayload['statusMessage'] == 'promotesuccess':
                logger.info('Promotion is successful')
                sendSuccessCodepipeline(jobId, "Promotion is successful")
            else:
                logger.info('Promotion failed due to this statusMessage {}'.format(lambdaResponsePayload['statusMessage']))
                sendFailureCodepipeline(jobId, lambdaResponsePayload['statusMessage'])
        else:
            logger.error("Promotion failed either due to non-success status or no status message in response from target account")
            sendFailureCodepipeline(jobId, "Promotion failed either due to non-success status or no status message in response from target account")
        
    except Exception as e:
        logger.error('Failed: {}'.format(e), exc_info=True)
        sendFailureCodepipeline(jobId, 'Promotion failed unexpectedly: {}'.format(e))
 
def validatePipelineInputParameters(parameters):
    invalidCount = 0
    if 'ASGServiceTag' not in parameters:
        logger.error("Missing ASGServiceTag in UserParameters of Promote stage")
        invalidCount=+1
    if 'FunctionARN' not in parameters:
        logger.error("Missing FunctionARN in UserParameters of Promote stage")
        invalidCount=+1
    if 'TargetAccountName' not in parameters:
        logger.error("Missing TargetAccountName in UserParameters of Promote stage")
        invalidCount=+1
    if 'Region' not in parameters:
        logger.error("Missing Region in UserParameters of Promote stage")
        invalidCount=+1
    if invalidCount>0:
        return False
    logger.info("Passed validation of all pipeline input parameters")
    return True

def sendSuccessCodepipeline(job, message):
    logger.info('Sending success signal to CodePipeline')
    code_pipeline.put_job_success_result(jobId=job)

def sendFailureCodepipeline(job, message):
    logger.info('Sending failure signal to CodePipeline')
    code_pipeline.put_job_failure_result(jobId=job, failureDetails={'message': message, 'type': 'JobFailed'})
