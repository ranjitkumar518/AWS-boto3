#!/usr/bin/env bash

if [ $# -lt 3 ]; then
      echo "Usage: ./scale_down_autoscaling.sh <ENV> <AWS_PROFILE> [Component] [SCALE_DOWN]"
      echo "Required: ENV, AWS_PROFILE Component"
      echo "Optional: SCALE_DOWN (Default=3)"
      echo "Example: ./scale_down_autoscaling.sh perf web-app preprod"
      exit
fi

### Default value of ASG to Scale down to....
if [[ -z "$4" ]] ; then
    SCALE_DOWN=3
else
    SCALE_DOWN="$4"
fi

# Fetch the Active/blue auto scaling group
active_asg_name=$(aws autoscaling describe-tags --profile $2 \
    --query 'Tags[?Value==`Active`].[ResourceId]' \
    --output text | grep $1-ec2-$3-)
echo Found blue autoscaling group = $active_asg_name

# Fetch the Active/blue auto scaling group
ready_asg_name=$(aws autoscaling describe-tags --profile $2 \
    --query 'Tags[?Value==`Ready`].[ResourceId]' \
    --output text | grep $1-ec2-$3-)

echo Found blue autoscaling group = $ready_asg_name


echo Triggering scale down of Active ASG to $SCALE_DOWN instances...

### Scaling down only Active ASG

aws autoscaling update-auto-scaling-group --profile $2 \
    --auto-scaling-group-name $active_asg_name \
    --min-size $SCALE_DOWN \
    --max-size $SCALE_DOWN \
    --desired-capacity $SCALE_DOWN

echo Triggered scale down of Active ASG, instances will now be terminated.
