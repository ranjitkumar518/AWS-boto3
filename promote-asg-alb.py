from __future__ import print_function

from botocore.exceptions import ClientError, ParamValidationError
import json
import time
import boto3
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

logger.info('Loading function')

def lambda_handler(event, context):
    try:
        logger.info('Received event {}'.format(event))
        logger.info('Received context {}'.format(context))
        asgServiceTag = event['ASGServiceTag']

        autoscalingClient = boto3.client('autoscaling')
        elbv2Client = boto3.client('elbv2')

        # Get current active and current ready ASGs
        currentActiveASG,currentReadyASG = getASGs(autoscalingClient,asgServiceTag)
        logger.info('Current Active ASG: {}'.format(currentActiveASG))
        logger.info('Current Ready ASG: {}'.format(currentReadyASG))

        # Get ARN of Active Target Group
        activeTargetGroupName = asgServiceTag
        activeTargetGroupARN = getTargetGroupARN(elbv2Client, activeTargetGroupName)
        logger.info('Active TG ARN: {}'.format(activeTargetGroupARN))

        # Get ARN of Ready Target Group
        readyTargetGroupName = asgServiceTag + "-green"
        readyTargetGroupARN = getTargetGroupARN(elbv2Client, readyTargetGroupName)
        logger.info('Ready TG ARN: {}'.format(readyTargetGroupARN))

        if not evaluateTargetGroupHealth(elbv2Client, readyTargetGroupARN):
            logger.error('Failed health check for ready Target Group: {}'.format(readyTargetGroupARN))
            returnResponse = dict(statusMessage='Failed: health check for ready Target Group {}'.format(readyTargetGroupARN))
            return returnResponse

        # Attach ActiveTargetGroup to current ready ASG
        attachASGtoTG(autoscalingClient, activeTargetGroupARN, currentReadyASG)

        logger.info('Starting 1st DETACH')
        # Detach ReadyTargetGroup from current ready ASG
        detachASGfromTG(autoscalingClient, readyTargetGroupARN, currentReadyASG)

        # Wait for all EC2 to be healthy in ActiveTargetGroup
        time.sleep(30)
        if not evaluateTargetGroupHealth(elbv2Client, activeTargetGroupARN):
            logger.error('Failed health check for Target Group: {}'.format(activeTargetGroupARN))
            returnResponse = dict(statusMessage='Failed: health check for Target Group {}'.format(activeTargetGroupARN))
            return returnResponse

        if currentActiveASG is not None:
            logger.info('Starting 2nd DETACH')
            # Remove ActiveTargetGroup from current Active ASG
            detachASGfromTG(autoscalingClient, activeTargetGroupARN, currentActiveASG)

            # Wait for all EC2 to be healthy in ActiveTargetGroupARN
            time.sleep(30)
            if not evaluateTargetGroupHealth(elbv2Client, activeTargetGroupARN):
                logger.error('Failed 2nd health check for Target Group: {}'.format(activeTargetGroupARN))
                returnResponse = dict(statusMessage='Failed: 2nd health check for Target Group {}'.format(activeTargetGroupARN))
                return returnResponse
            updateASGTags(autoscalingClient, currentActiveASG, "Ready")

        # Swap tag Cfn-Create-Action for both current ready and current active ASG
        updateASGTags(autoscalingClient, currentReadyASG, "Active")
        logger.info('Finished processing promote, sending back success')
        returnResponse = dict(statusMessage="promotesuccess")
        return returnResponse
    except ParamValidationError as e:
        logger.error("Parameter validation error", exc_info=True)
        returnResponse = dict(statusMessage='Failed: {}'.format(e))
        return returnResponse
    except ClientError as e:
        logger.error("Client error occurred", exc_info=True)
        returnResponse = dict(statusMessage='Failed: {}'.format(e))
        return returnResponse
    except Exception as e:
        logger.error("General exception occurred.", exc_info=True)
        returnResponse = dict(statusMessage='Failed: {}'.format(e))
        return returnResponse

def getASGs(autoscalingClient, asgServiceTag):
    currentActiveASG = None
    currentReadyASG = None
    paginator = autoscalingClient.get_paginator('describe_auto_scaling_groups')
    page_iterator = paginator.paginate(
        PaginationConfig={'PageSize': 100}
    )
    filtered_asgs = page_iterator.search(
        'AutoScalingGroups[] | [?contains(Tags[?Key==`{}`].Value, `{}`)]'.format(
            'Service', asgServiceTag)
    )
    for asg in filtered_asgs:
        logger.info('Looking up ASG {} to check if it is Active/Ready'.format(asg['AutoScalingGroupName']))
        tagsResponse = autoscalingClient.describe_tags(
            Filters=[
                {
                    'Name': 'auto-scaling-group',
                    'Values': [
                        asg['AutoScalingGroupName'],
                    ]
                },
                {
                    'Name': 'value',
                    'Values': [
                        'Active',
                    ]
                }
            ]
        )
        if len(tagsResponse['Tags']) == 1:
            currentActiveASG = asg['AutoScalingGroupName']
        elif len(tagsResponse['Tags']) == 0:
            currentReadyASG = asg['AutoScalingGroupName']
        else:
            logger.info('More than 1 ASG contains Active/Ready tags. Please check.')
    return currentActiveASG,currentReadyASG

def attachASGtoTG(autoscalingClient, targetGroupARN, asgName):
    logger.info('Attaching ASG {} to TG {}'.format(asgName,targetGroupARN))
    response = autoscalingClient.attach_load_balancer_target_groups(
        AutoScalingGroupName=asgName,
        TargetGroupARNs=[
            targetGroupARN,
        ]
    )

def detachASGfromTG(autoscalingClient, targetGroupARN, asgName):
    logger.info('Detaching ASG {} from TG {}'.format(asgName,targetGroupARN))
    response = autoscalingClient.detach_load_balancer_target_groups(
        AutoScalingGroupName=asgName,
        TargetGroupARNs=[
            targetGroupARN,
        ]
    )
    except ClientError as e:
        errorMessage = '{}'.format(e)
        if errorMessage.find("Trying to remove Target Groups that are not part of the group"):
            logger.error('Client error occurred: ' + errorMessage , exc_info=True)
            response = dict(statusMessage='Success')
        else:
            raise ClientError
