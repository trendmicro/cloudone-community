#!/usr/local/bin/python3

import argparse
import json
import boto3
from botocore.response import StreamingBody

parser = argparse.ArgumentParser(
    description="""
    Syncs Conformity findings and the AWS Well-Architected Review using the infrastructure
    created by the stack conformity-wellarchitected-sync.yaml. 
    
    Assumes your AWS CLI is configured and that you have sufficient permissions
    to invoke Lambda functions.

    The function ARN can be found in the Outputs section of the stack.
    """
)
parser.add_argument( "--stackName", type=str, default="Conformity-WellArchitectedReview-Sync", help="Name used to create the Conformity->Well-Architected Review sync stack")
parser.add_argument("--workloadArn", type=str, required=True, help="Well-Architected Review to synchronize")
args = parser.parse_args()

cfnClient = boto3.client("cloudformation")
stacks = cfnClient.describe_stacks(StackName=f"{args.stackName}")
stack = stacks["Stacks"][0]
outputs = stack["Outputs"]
lambdaFunctionArn = [ x["OutputValue"] for x in outputs if x["OutputKey"] == "LambdaFunctionName" ][0]

lambdaClient = boto3.client("lambda")
arguments = {"workloadArn": f"{args.workloadArn}"}
response = lambdaClient.invoke( FunctionName=f"{lambdaFunctionArn}", InvocationType="RequestResponse", Payload=json.dumps(arguments).encode("utf-8"))
apiResponse = json.loads(response['Payload'].read().decode('utf-8'))
print(json.dumps(apiResponse, indent=4))
