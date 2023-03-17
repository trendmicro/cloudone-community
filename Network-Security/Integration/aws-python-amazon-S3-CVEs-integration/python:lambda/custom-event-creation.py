from __future__ import print_function
import json
import boto3
import cfnresponse

SUCCESS = "SUCCESS"
FAILED = "FAILED"

print('Loading function')
s3 = boto3.resource('s3')

def lambda_handler(event, context):
    print("Received event: " + json.dumps(event, indent=2))
    responseData={}
    try:
        if event['RequestType'] == 'Delete':
            print("Request Type:",event['RequestType'])
            Bucket=event['ResourceProperties']['Bucket']
            delete_notification(Bucket)
            print("Sending response to custom resource after Delete")
        elif event['RequestType'] == 'Create' or event['RequestType'] == 'Update':
            print("Request Type:",event['RequestType'])
            LambdaArn=event['ResourceProperties']['LambdaArn']
            Bucket=event['ResourceProperties']['Bucket']
            add_notification(LambdaArn, Bucket)
            responseData={'Bucket':Bucket}
            print("Sending response to custom resource")
        responseStatus = 'SUCCESS'
    except Exception as e:
        print('Failed to process:', e)
        responseStatus = 'FAILED'
        responseData = {'Failure': 'Something bad happened.'}
    cfnresponse.send(event, context, responseStatus, responseData)

def add_notification(LambdaArn, Bucket):
    bucket_notification = s3.BucketNotification(Bucket)
    response = bucket_notification.put(
        NotificationConfiguration={
        'LambdaFunctionConfigurations': [
            {
                'LambdaFunctionArn': LambdaArn,
                'Events': [
                    's3:ObjectCreated:*'
                ]
            }
        ]
        }
    )
    print("Put request completed....")
    
def delete_notification(Bucket):
    bucket_notification = s3.BucketNotification(Bucket)
    response = bucket_notification.put(
        NotificationConfiguration={}
    )
    print("Delete request completed....")