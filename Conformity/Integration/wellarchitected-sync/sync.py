#!/usr/local/bin/python3

import argparse
import subprocess
import json

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

jsonData = None
with subprocess.Popen(args=[ "aws", "cloudformation", "describe-stacks", "--stack-name", f"{args.stackName}", "--output", "json"], stdout=subprocess.PIPE) as proc:
    jsonData = json.loads(proc.stdout.read().decode('utf-8'))

stack = jsonData["Stacks"][0]
outputs = stack["Outputs"]
lambdaFunctionArn = [ x['OutputValue'] for x in outputs if x['OutputKey'] == 'LambdaFunctionName' ][0]

jsonData = None
with subprocess.Popen(args=[ "aws", "lambda", "invoke", "--function-name", f"{lambdaFunctionArn}", "--invocation-type", "RequestResponse", "response.json", "--output", "json"], stdout=subprocess.PIPE) as proc:
    jsonData = json.loads(proc.stdout.read().decode('utf-8'))

print(jsonData)




