# Python Lambda function for EC2 autoscaling based on SQS queue size

EC2 autoscaling based on SQS queue size requires some additional logic to get up-and-running smoothly. This is useful for batch processing work orders from a queue. For example processing uploaded files to an S3 bucket.

The AWS documentation on [Scaling based on Amazon SQS](https://docs.aws.amazon.com/autoscaling/ec2/userguide/as-using-sqs-queue.html) suggests to create an application that polls metadata from SQS and publishes it as a custom metric in CloudWatch. It allows you to use this custom metric in a target tracking policy.

## Ingredients

This nano-repo contains:

1. A Lambda function to monitor an SQS queue and publish a metric called SQSBacklogPerInstance
2. A Target tracking configuration JSON file

## Applying autoscaling target tracking policy to EC2 ASG

```
aws autoscaling put-scaling-policy --policy-name AnnualRptScaling \
    --auto-scaling-group-name Annual_Rpt_Runners \
    --policy-type TargetTrackingScaling \
    --target-tracking-configuration file://asg-scaling-policy.json
```
