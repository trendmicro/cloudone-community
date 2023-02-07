#from cgitb import reset
from http.client import responses
import os.path
import json
import time
import boto3
import argparse
import urllib3
from botocore.config import Config
from botocore.exceptions import ClientError

http = urllib3.PoolManager()

'''
This script requires an additional text file for bucket to exclude from example "exclude.txt"
Will deploy a storage stack to all existing buckets
All storage stack will link to 1 Scanner Stack you define
'''

# variables needed
parser = argparse.ArgumentParser(description='Deploy to All Buckets')
parser.add_argument("--account", required=True, type=str, help="AWS Account ID where scanner stack exists")
parser.add_argument("--c1region", required=True, type=str, help="Cloud One Account Region")
parser.add_argument("--sqs", required=True, type=str, help="Scanner Stack SQS URL Value")
parser.add_argument("--scanner", required=True, type=str, help="Scanner Stack Name")
parser.add_argument("--apikey", required=True, type=str, help="Cloud One API Key")
parser.add_argument("--scanneralias", required=True, type=str, help="Scanner Lambda Alias ARN")
args = parser.parse_args()

Scan_Lambda_Arn_Alias = args.scanneralias
scanner_stack_name = args.scanner
aws_account_id = args.account
cloud_one_region = args.c1region
sqs_url = args.sqs
ws_api = args.apikey
filename = "exclude.txt"
stacks_api_url = "https://filestorage." + cloud_one_region + ".cloudone.trendmicro.com/api/"


# get list of buckets to exclude from deployment
def get_exclusions(filename):
    if not os.path.isfile(filename):
        print("No file for exclusions")
    else:
        with open(filename) as f:
            content = f.read().splitlines()
            get_buckets(content)


# get list of buckets available in aws
def get_buckets(content):
    # remove spaces from exclusions list
    content = [entry.strip() for entry in content]
    # setup client for s3
    s3_client = boto3.client('s3')
    # create empty list
    list_of_buckets = []
    # call to list buckets
    bucket_list = s3_client.list_buckets()
    name = bucket_list['Buckets']

    # append buckets to list
    for buckets in name:
        all_buckets = list_of_buckets.append(buckets['Name'])
    # remove excluded buckets from list
    for item in content:
        list_of_buckets.remove(item)

    get_encryption_region(list_of_buckets)

# gather encryption status and bucket region
def get_encryption_region(list_of_buckets):
    s3_client = boto3.client("s3")
    # check if encryption exists on bucket
    for bucket_name in list_of_buckets:
        try:
            encryption = s3_client.get_bucket_encryption(Bucket=bucket_name)
            try:
                # kms check
                kms_arn = \
                encryption["ServerSideEncryptionConfiguration"]["Rules"][0]["ApplyServerSideEncryptionByDefault"][
                    "KMSMasterKeyID"]
                response = s3_client.get_bucket_location(Bucket=bucket_name)
                region = response["LocationConstraint"]
                if region is None:
                    region = "us-east-1"
            except KeyError:
                # sse-s3 check
                sse_s3_bucket = \
                encryption["ServerSideEncryptionConfiguration"]["Rules"][0]["ApplyServerSideEncryptionByDefault"][
                    'SSEAlgorithm']
                kms_arn = ""
                response = s3_client.get_bucket_location(Bucket=bucket_name)
                region = response["LocationConstraint"]
                if region is None:
                    region = "us-east-1"
        except ClientError:
            # not encrypted
            kms_arn = ""
            response = s3_client.get_bucket_location(Bucket=bucket_name)
            region = response["LocationConstraint"]
            if region is None:
                region = "us-east-1"
        # check bucket tags
        try:
            response = s3_client.get_bucket_tagging(Bucket=bucket_name)
            tags = response["TagSet"]
            tag_status = tags
            if (next((x for x in tag_status if x['Key'] == 'FSSMonitored'), None)) == None:
                # if a exisitng lambda s3 notification exists then skip
                if check_for_s3_notification(s3_client, bucket_name) is True:
                    pass
                else:
                    deploy_storage(kms_arn, region, bucket_name)
                    add_tag(s3_client, bucket_name, tag_list=tag_status)
            else:
                for tags in tag_status:
                    if tags["Key"] == "FSSMonitored" and tags["Value"].lower() == "no":
                        # if tag FSSMonitored is no; skip
                        print("S3: " + bucket_name + " has tag FSSMonitored == no; skipping")
                        break
                    elif tags["Key"] == "FSSMonitored" and tags["Value"].lower() == "yes":
                        print("S3: " + bucket_name + " FSS Tag Found!, FSS is already deployed!")
                        #add logic to check s3 event notification
                        break
        # No tags at all on bucket                  
        except ClientError:
            no_tags = "does not have tags"
            tag_status = no_tags
            # if a exisiting lambda s3 notification exists then skip
            if check_for_s3_notification(s3_client, bucket_name) is True:
                pass
            else:
                deploy_storage(kms_arn, region, bucket_name)
                add_tag(s3_client, bucket_name, tag_list=[])

# adds FSS Monitored Tag to s3
def add_tag(s3_client, bucket_name, tag_list):
    tag_list.append({'Key': 'FSSMonitored', 'Value': 'Yes'})
    s3_client.put_bucket_tagging(
        Bucket=bucket_name,
        Tagging={"TagSet": tag_list},
    )
# determines if a S3 event notification exists
def check_for_s3_notification(s3_client, bucket_name):
    response = s3_client.get_bucket_notification_configuration(
        Bucket=bucket_name
    )
    # s3:ObjectCreated:* event in use
    if "LambdaFunctionConfigurations" in response:
        event = response["LambdaFunctionConfigurations"][0]["Events"]
        print("Skip: " + bucket_name + ' ' + str(event) + " in use, See: " + "https://cloudone.trendmicro.com/docs/file-storage-security/aws-object-created-event-in-use/")
        return True
    elif "QueueConfigurations" in response:
        event = response["QueueConfigurations"][0]["Events"]
        print("Skip: " + bucket_name + ' ' + str(event) + " in use, See: " + "https://cloudone.trendmicro.com/docs/file-storage-security/aws-object-created-event-in-use/")
        return True
    elif "TopicConfigurations" in response:
        event = response["TopicConfigurations"][0]["Events"]
        print("Skip: " + bucket_name + ' ' + str(event) + " in use, See: " + "https://cloudone.trendmicro.com/docs/file-storage-security/aws-object-created-event-in-use/")
        return True
    else:
        return False

# function to deploy fss storage stack
def deploy_storage(kms_arn, region, bucket_name):
    # set up aws Config for region changes
    print("deploying to : " + bucket_name)
    my_region_config = Config(
        region_name=region,
        signature_version='v4',
        retries={
            'max_attempts': 10,
            'mode': 'standard'
        }
    )
    # gather cloud one ext id
    
    r = http.request(
        "GET",
        stacks_api_url+"external-id",
        headers={
            "Authorization": "ApiKey " + ws_api,
            "Api-Version": "v1",
        },
    )
    try:
        ext_id = json.loads(r.data.decode("utf-8"))['externalID']
    except json.decoder.JSONDecodeError:
        time.sleep(1)
        ext_id = json.loads(r.data.decode("utf-8"))['externalID']
    
    # set fss api doc parameters
    ExternalID = {"ParameterKey": "ExternalID", "ParameterValue": ext_id}
    CloudOneRegion = {"ParameterKey": "CloudOneRegion", "ParameterValue": cloud_one_region}
    S3BucketToScan = {"ParameterKey": "S3BucketToScan", "ParameterValue": bucket_name}
    Trigger_with_event = {
        "ParameterKey": "TriggerWithObjectCreatedEvent",
        "ParameterValue": "true",
    }
    scanner_queue_url = {"ParameterKey": "ScannerSQSURL", "ParameterValue": sqs_url}
    scanner_aws_account = {
        "ParameterKey": "ScannerAWSAccount",
        "ParameterValue": aws_account_id,
    }
    ScannerLambdaAliasARN = {"ParameterKey": "ScannerLambdaAliasARN", "ParameterValue": Scan_Lambda_Arn_Alias}
    S3_Encryption = {"ParameterKey": "KMSKeyARNForBucketSSE", "ParameterValue": kms_arn}
    cft_client = boto3.client("cloudformation", config=my_region_config)

    # using python sdk to deploy cft [cant define region though so all is deployed to my default]
    cfbucketname = bucket_name.replace(".", "-")
    cft_client.create_stack(
        StackName="C1-FSS-Storage-" + cfbucketname,
        TemplateURL="https://file-storage-security.s3.amazonaws.com/latest/templates/FSS-Storage-Stack.template",
        Parameters=[
            ExternalID,
            CloudOneRegion,
            S3BucketToScan,
            scanner_queue_url,
            Trigger_with_event,
            scanner_aws_account,
            S3_Encryption,
            ScannerLambdaAliasARN,
        ],
        Capabilities=["CAPABILITY_IAM"],
    )
    cft_waiter = cft_client.get_waiter("stack_create_complete")
    cft_waiter.wait(StackName="C1-FSS-Storage-" + cfbucketname)
    res = cft_client.describe_stacks(StackName="C1-FSS-Storage-" + cfbucketname)
    storage_stack = res["Stacks"][0]["Outputs"][2]["OutputValue"]
    # gather scanner stack id
    id_call = http.request('GET', stacks_api_url + "stacks", fields={"limit": "100", "type": "scanner"},
                           headers={'Authorization': 'ApiKey ' + ws_api, 'Api-Version': 'v1'})
    try:
        id_resp = json.loads(id_call.data.decode('utf-8'))['stacks']
    except json.decoder.JSONDecodeError:
        time.sleep(1)
        id_resp = json.loads(id_call.data.decode('utf-8'))['stacks']
    for data in id_resp:
        if 'name' in data and data['name'] is not None:
            if scanner_stack_name == data['name']:
                stack_id = data['stackID']

    add_to_cloudone(ws_api, stack_id, storage_stack)

# call to cloudone to register stacks in FSS
def add_to_cloudone(ws_api, stack_id, storage_stack):
    print("FSS StorageRole Arn: " + storage_stack)
    # add to c1
    payload = {
        "type": "storage",
        "scannerStack": stack_id,
        "provider": "aws",
        "details": {"managementRole": storage_stack}
    }
    encoded_msg = json.dumps(payload)
    resp = http.request(
        "POST",
        stacks_api_url + "stacks",
        headers={
            "Content-Type": "application/json",
            "Authorization": "ApiKey " + ws_api,
            "Api-Version": "v1",
        },
        body=encoded_msg,
    )
    transform = json.loads(resp.data.decode("utf-8"))
    url = "https://filestorage." + cloud_one_region + ".cloudone.trendmicro.com/api/stacks/" + transform['stackID']


get_exclusions(filename)