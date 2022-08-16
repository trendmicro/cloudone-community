import boto3
import urllib3
import json
import argparse

http = urllib3.PoolManager()

#variables needed
parser = argparse.ArgumentParser(description='Deploy to All Buckets')
parser.add_argument("--apikey", required=True, type=str, help="Cloud One API Key")
parser.add_argument("--c1region", required=True, type=str, help="Cloud One Account Region")
parser.add_argument("--functionname", required=True, type=str, help="Name of Slack Lambda Function")
parser.add_argument("--functionarn", required=True, type=str, help="ARN of Slack Lambda Function")
args = parser.parse_args()

fss_api = args.apikey
c1_region = args.c1region
fx_name = args.functionname
fx_arn = args.functionarn
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
    stack_names = []
    response = json.loads(stacks.data.decode("utf-8"))
    for name in response['stacks']:
        stack_names.append(name['name'])
    describe_fss_storage(stack_names)

# describe cft stacks to obtain each storage stack sns arn.
def describe_fss_storage(stack_names):
    
    cft_client = boto3.client('cloudformation')
    arnArray = []
    for stack in stack_names:
        response = cft_client.describe_stacks(StackName=stack)
        outputs = response["Stacks"][0]["Outputs"]

        for output in outputs:
            keyName = output["OutputKey"]
            if keyName == "ScanResultTopicARN":
                arnArray.append(output["OutputValue"])
    subscribe_sns(arnArray)    

# subscribe lambda to sns topics to receive events
def subscribe_sns(arnArray):
    id = 1
    for topic in arnArray:
        print("Subscribing Lambda to: " + topic)
        client = boto3.client('lambda')
        client.add_permission(Action="lambda:InvokeFunction", StatementId=("automate-"+ str(id)),FunctionName=fx_name, Principal='sns.amazonaws.com', SourceArn=topic)
        client = boto3.client('sns')
        client.subscribe(TopicArn=topic,Protocol='lambda',Endpoint=fx_arn)
        id = id + 1


fss_list_stack()