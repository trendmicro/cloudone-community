import boto3
import botocore
import random
import string
import urllib3
import json
import argparse

http = urllib3.PoolManager()

#arguments require
parser = argparse.ArgumentParser(description='Subscribe Slack Plugin to SNS')
parser.add_argument("--apikey", required=True, type=str, help="Cloud One API Key")
parser.add_argument("--c1region", required=True, type=str, help="Cloud One Account Region")
parser.add_argument("--functionname", required=True, type=str, help="Name of Slack Lambda Function")
parser.add_argument("--functionarn", required=True, type=str, help="ARN of Slack Lambda Function")
parser.add_argument("--awsprofile", required=True, type=str, help="AWS Profile to use for credentials")
parser.add_argument("--pluginregion", required=True, type=str, help="AWS Region Slack plugin is deployed")
args = parser.parse_args()

fss_api = args.apikey
c1_region = args.c1region
fx_name = args.functionname
fx_arn = args.functionarn
aws_profile = args.awsprofile
plugin_region = args.pluginregion
#fss base api call url
call_url = "https://filestorage."+c1_region+".cloudone.trendmicro.com/api/"


# obtain C1 FSS storage stacks
def fss_list_stack():
    stacks = http.request(
        "GET",
        call_url+"stacks?type=storage&provider=aws",
        headers={
            "Authorization": "ApiKey " + fss_api,
            "Api-Version": "v1",
        },
        
    )
    stacks_info = []
    response = json.loads(stacks.data.decode("utf-8"))
    for name in response['stacks']:
        stacks_info.append([name['name'], name['details']['region']])
    
    describe_fss_storage(stacks_info)

# describe cft stacks to obtain each storage stack sns arn.
def describe_fss_storage(stacks_info):
    
    for stack in stacks_info:
        # set aws profile sessions
        session = boto3.Session(profile_name=aws_profile, region_name=str(stack[1]))
        cft_client = session.client('cloudformation')
        try:
            response = cft_client.describe_stacks(StackName=str(stack[0]))
            outputs = response["Stacks"][0]["Outputs"]

            for output in outputs:
                keyName = output["OutputKey"]
                if keyName == "ScanResultTopicARN":
                    topic_arn = output["OutputValue"]
                    subscribe_sns(topic_arn, session)
        # Skip deploy FSS stacks that do not exist in current AWS account
        except botocore.exceptions.ClientError as err:
            print("Skipping " + str(stack[0]) + ", does not exist in this AWS Account")

# subscribe lambda to sns topics to receive events
def subscribe_sns(topic_arn, session):

    #for topic in arnArray:
    try:    
        client_lambda = session.client('lambda')
        client_lambda.add_permission(Action="lambda:InvokeFunction", StatementId=(''.join(random.choices(string.ascii_lowercase, k=5))),FunctionName=fx_name, Principal='sns.amazonaws.com', SourceArn=topic_arn)
        client_sns = session.client('sns')
        client_sns.subscribe(TopicArn=topic_arn,Protocol='lambda',Endpoint=fx_arn)
        print("Subscribing Lambda to: " + topic_arn)
        
    except botocore.exceptions.ClientError as error:
        # handle invalid passed params
        if error.response['Error']['Code'] == 'InvalidParameter':
            print(error)
        # handle subscription when topic lives in another AWS Region
        elif error.response['Error']['Code'] == 'ResourceNotFoundException':
            session = boto3.Session(profile_name=aws_profile, region_name=plugin_region)
            client_lambda = session.client('lambda')
            client_lambda.add_permission(Action="lambda:InvokeFunction", StatementId=(''.join(random.choices(string.ascii_lowercase, k=5))),FunctionName=fx_name, Principal='sns.amazonaws.com', SourceArn=topic_arn)
            print("Subscribing Lambda to: " + topic_arn)
            
fss_list_stack()