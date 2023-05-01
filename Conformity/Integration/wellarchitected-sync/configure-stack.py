#!/usr/local/bin/python3

import argparse
import subprocess

parser = argparse.ArgumentParser(
    description='''
    Configures the Conformity-WellArchitected-Integration stack.
    
    Assumes the stack 'WellArchitectedReview-Conformity-Sync' does not exist in your account.
    
    Also assumes your AWS CLI is configured and that you have sufficient permissions
    to run 'aws cloudformation create-stack' with CAPABILITY_NAMED_IAM.'
    ''')
parser.add_argument('--workload', type=str, required=True,
                    help='Well Architected Workload Arn')
parser.add_argument('--accountId', type=str, required=True,
                    help='Cloud One Account Id')
parser.add_argument('--region', type=str, required=True, choices=[
                    'trend-us-1', 'us-1', 'au-1', 'ie-1', 'sg-1', 'in-1', 'jp-1', 'ca-1', 'de-1'], help='Cloud One Service region')
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

command = f'aws cloudformation create-stack --stack-name Conformity-WellArchitectedReview-Sync --template-body file://conformity-wellarchitected-sync.yaml --capabilities CAPABILITY_NAMED_IAM --parameters ParameterKey=Workload,ParameterValue={args.workload},UsePreviousValue=true ParameterKey=CloudOneAccountId,ParameterValue={args.accountId},UsePreviousValue=true ParameterKey=CloudOneRegion,ParameterValue={args.region},UsePreviousValue=true ParameterKey=CloudOneAPIKey,ParameterValue={args.apiKey},UsePreviousValue=true ParameterKey=ExternalId,ParameterValue={args.externalId},UsePreviousValue=true ParameterKey=ConformityAccountId,ParameterValue={args.conformityAccountId},UsePreviousValue=true ParameterKey=Owner,ParameterValue={args.owner},UsePreviousValue=true ParameterKey=Environment,ParameterValue={args.environment},UsePreviousValue=true' 
subprocess.run(args=command, shell=True)

