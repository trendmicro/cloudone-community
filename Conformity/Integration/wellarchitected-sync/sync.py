#!/usr/local/bin/python3

import argparse
import json
import boto3

parser = argparse.ArgumentParser(
    description='''
    Syncs Conformity findings and the AWS Well-Architected Review using the infrastructure
    created by the stack conformity-wellarchitected-sync.yaml. 
    
    Assumes your AWS CLI is configured and that you have sufficient permissions
    to invoke Lambda functions.'
    ''')
parser.add_argument('--stackName', type=str, default='Conformity-WellArchitectedReview-Sync',
                    help='Name used to create the Conformity->Well Architected Review sync stack')
args = parser.parse_args()

cfnClient = boto3.client('cloudformation')
stacks = cfnClient.describe_stacks(StackName=f'{args.stackName}')
stack = stacks['Stacks'][0]
outputs = stack['Outputs']
lambdaFunctionArn = [ x['OutputValue'] for x in outputs if x['OutputKey'] == 'LambdaFunctionName' ][0]

lambdaClient = boto3.client('lambda')
response = lambdaClient.invoke(FunctionName=f'{lambdaFunctionArn}', InvocationType='RequestResponse')
print(response)
