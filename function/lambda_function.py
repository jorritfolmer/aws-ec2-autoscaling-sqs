import boto3
import logging
import json
from botocore.exceptions import ClientError

### CONFIGURE THESE VARIABLES:

queue_url = 'https://sqs.eu-west-1.amazonaws.com/123456789/your-queue-name'
asg_name  = 'Your_ASG_Name'
cloudwatch_namespace = 'YourCloudWatchNameSpace'
cloudwatch_metric_name = "SQSBacklogPerInstance"

### END CONFIG

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def get_instances_in_asg(asg_name):
    try:
        client = boto3.client('autoscaling')
    except ClientError as err:
        logger.error("Exception in boto3.client('ec2'): {}".format(err))
        exit(1)
    else:
        response = client.describe_auto_scaling_groups(
            AutoScalingGroupNames=[asg_name]
        )
        instances = [i.get("Instances",None) for i in response.get('AutoScalingGroups',{})][0]
        if instances is not None:
            instance_count = len(instances)
            logger.info("asg_name={}, instance_count={}, instances={}".format(asg_name,instance_count,instances))
            return(instance_count)
        else:
            logger.error("Error: Instances attribute is not available in AutoScalingGroup {}".format(asg_name))
            exit(2)

def get_msg_count_from_sqs_queue(queue_url):
    try:
        client = boto3.client('sqs')
    except ClientError as err:
        logger.error("Exception in boto3.client('sqs'): {}".format(err))
        exit(1)
    else:
        response = client.get_queue_attributes(
            QueueUrl=queue_url,
            AttributeNames=["ApproximateNumberOfMessages"]
        )
        msg_count = response.get('Attributes',{}).get('ApproximateNumberOfMessages',None)
        if msg_count is not None:
            logger.info("queue_url={}, msg_count={}".format(queue_url,msg_count))
            return(msg_count)
        else:
            logger.error("Error: ApproximateNumberOfMessages attribute is not available on queue {}".format(queue_url))
            exit(2)

def put_cloudwatch_metric(namespace, name, value):
    try:
        cloudwatch = boto3.client('cloudwatch')
    except ClientError as err:
        logger.error("Exception in boto3.client('cloudwatch'): {}".format(err))
        exit(1)
    else:
        response = cloudwatch.put_metric_data(
            MetricData = [
                {
                    'MetricName': name,
                    'Dimensions': [
                        {
                            'Name': 'Queue Metrics',
                            'Value': queue_url
                        },
                    ],
                    'Unit': 'Count',
                    'Value': value
                    
                },
            ],
            Namespace = namespace
        )
        logger.info("cloudwatch_metric_name={}, value={}, status_code={}".format(
            cloudwatch_metric_name,
            value,
            response.get('ResponseMetadata',{}).get('HTTPStatusCode',None)
        ))

def main():
    msg_count = get_msg_count_from_sqs_queue(queue_url)
    instance_count = get_instances_in_asg(asg_name)
    try:
        value = int(msg_count)/int(instance_count)
    except ZeroDivisionError:
        value = int(msg_count)
    put_cloudwatch_metric(cloudwatch_namespace, cloudwatch_metric_name, value)

def lambda_handler(event,context):
    main()

if __name__ == "__main__":
    ### You can also run this script from the command line
    logging.basicConfig(format="%(asctime)s %(message)s")
    main()
