#!/usr/local/bin/python3

import argparse
import boto3
import json

parser = argparse.ArgumentParser(
    description='''
    Configures the Conformity-WellArchitected-Integration stack.
    
    Assumes the stack 'WellArchitectedReview-Conformity-Sync' does not exist in your account.
    
    Also assumes your AWS CLI is configured and that you have sufficient permissions
    to run 'aws cloudformation create-stack' with CAPABILITY_NAMED_IAM.'
    ''')
parser.add_argument('--accountId', type=str, required=True,
                    help='Cloud One Account Id')
parser.add_argument('--region', type=str, required=True, choices=[
                    'trend-us-1', 'us-1', 'au-1', 'ie-1', 'sg-1', 'in-1', 'jp-1', 'ca-1', 'de-1', 'gb-1'], help='Cloud One Service region')
parser.add_argument('--apiKey', type=str, required=True,
                    help='Cloud One API Key with Admin Rights')
parser.add_argument('--conformityAccountId', type=str, required=True,
                    help='Cloud One Conformity AWS Account Id')
parser.add_argument('--externalId', type=str, required=True,
                    help='Cloud One Conformity External Id')
parser.add_argument('--owner', type=str, required=True,
                    help='Owner\'s email')
parser.add_argument('--environment', type=str, required=True,
                    help='Environment where this is being deployed')
args = parser.parse_args()

client = boto3.client('cloudformation')

response = None
with open('conformity-wellarchitected-sync.yaml', 'r') as reader:
    response = client.create_stack(StackName='Conformity-WellArchitectedReview-Sync',
                               TemplateBody=reader.read(),
                               Capabilities=[ 'CAPABILITY_NAMED_IAM' ],
                               Parameters=[
                                   {
                                       'ParameterKey': 'CloudOneAccountId',
                                       'ParameterValue': f'{args.accountId}',
                                       'UsePreviousValue': True
                                   },
                                   {
                                       'ParameterKey': 'CloudOneRegion',
                                       'ParameterValue': f'{args.region}',
                                       'UsePreviousValue': True
                                   },
                                   {
                                       'ParameterKey': 'CloudOneAPIKey',
                                       'ParameterValue': f'{args.apiKey}',
                                       'UsePreviousValue': True
                                   },
                                   {
                                      'ParameterKey': 'ConformityAccountId',
                                      'ParameterValue': f'{args.conformityAccountId}',
                                      'UsePreviousValue': True
                                   },
                                   {
                                       'ParameterKey': 'ExternalId',
                                       'ParameterValue': f'{args.externalId}',
                                       'UsePreviousValue': True
                                   },
                                   {
                                      'ParameterKey': 'Owner',
                                      'ParameterValue': f'{args.owner}',
                                      'UsePreviousValue': True
                                   },
                                   {
                                      'ParameterKey': 'Environment',
                                      'ParameterValue': f'{args.environment}',
                                      'UsePreviousValue': True 
                                   }
                               ])
print(json.dumps(response, indent=4))
