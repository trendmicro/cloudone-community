#!/usr/local/bin/python3

from genericpath import isdir
import os
import argparse
import sys
from urllib import request, response
import requests
import json
import yaml

configFolder = os.path.expanduser(path='~/.conformity-custom-rule')
configFilename = 'config.yaml'

workspaceFolder = os.path.expanduser(path='./workspace')

apiEndpoint = "https://conformity.{}.cloudone.trendmicro.com/api/custom-rules"

def readConfiguration():
	configurationFile = f'{configFolder}/{configFilename}'
	
	if not os.path.isfile(configurationFile):
		raise Exception("Missing configuration. Run \"conformity-custom-rule configure help\" for further details.")

	with open(configurationFile, 'r') as configReader:
		configurations = yaml.safe_load(configReader)

		header = {
			"Content-Type": "application/vnd.api+json",
    			"api-version": "v1",
			"Authorization": "ApiKey {}".format(configurations.get("apiKey"))
		}

		region = "{}".format(configurations.get("region"))

		return header, region;

def configure(args):
	configuration = {
		"region": args.region,
		"apiKey": args.apiKey
	}

	if not os.path.isdir(configFolder):
		os.makedirs(configFolder)

	with open(f'{configFolder}/{configFilename}', 'w') as configWriter:
		yaml.dump(data=configuration, stream=configWriter)

	pass

def generate(args):

	sampleRule = {
		"name": "",
		"description": "",
		"remediationNotes": "",
		"service": "",
		"resourceType": "",
		"categories": [ "" ],
		"severity": "",
		"provider": "",
		"enabled": True,
		"attributes": [ {
			"name": "",
			"path": "",
			"required": True
		} ],
		"rules": [
			{
				"conditions": {
					"any": [ {
						"fact": "",
						"operator": "",
						"value": ""
					} ]
				},
				"event": { "type": "" }
			}
		]
	}
	
	with open(f'{workspaceFolder}/samplerule.yaml', 'w') as configWriter:
		yaml.dump(data=sampleRule, stream=configWriter, indent=4, sort_keys=False)

	pass

def create(args):
	header, region = readConfiguration()
	endpoint = f'{apiEndpoint.format(region)}' 

	with open(f'{workspaceFolder}/{args.file}', 'r') as ruleReader:
		rule = yaml.safe_load(stream=ruleReader)

		response = requests.post(url=endpoint, json=rule, headers=header)

		customRule = response.json()

		ruleId = customRule["data"]["id"]
		ruleFilename = f'{ruleId}.yaml'

		with open(f'{workspaceFolder}/{ruleFilename}', 'w') as ruleWriter:
			yaml.dump(data=customRule["data"], stream=ruleWriter, indent=4, sort_keys=False)

			print(f'Custom rule saved in file {ruleId}.yaml')

	pass

def get(args):
	header, region = readConfiguration()
	endpoint = f'{apiEndpoint.format(region)}/{args.ruleId}' 

	response = requests.get(url=endpoint, headers=header)
	rule = response.json()
	ruleId = rule["data"][0]["id"]
	ruleFilename = f'{ruleId}.yaml'

	with open(f'{workspaceFolder}/{ruleFilename}', 'w') as configWriter:
		yaml.dump(data=rule["data"][0], stream=configWriter, indent=4, sort_keys=False)

	print(f'Rule saved to file {ruleFilename}')
	pass

def update(args):
	header, region = readConfiguration()
	updatedRule = {}

	with open(f'{workspaceFolder}/{args.file}', 'r') as ruleReader:
		rule = yaml.safe_load(stream=ruleReader)

		endpoint = f'{apiEndpoint.format(region)}/{rule.get("id")}' 
		
		response = requests.put(url=endpoint, json=rule["attributes"], headers=header)
		updatedRule = response.json()
	
	ruleId = updatedRule["data"]["id"]
	ruleFilename = f'{ruleId}.yaml'

	with open(f'{workspaceFolder}/{ruleFilename}', 'w') as configWriter:
		yaml.dump(data=updatedRule["data"], stream=configWriter, indent=4, sort_keys=False)

	print(f'Rule saved to file {ruleFilename}')

	pass

def delete(args):
	header, region = readConfiguration()
	endpoint = f'{apiEndpoint.format(region)}/{args.ruleId}'
	
	response = requests.delete(url=endpoint, headers=header)

	print(f'Rule deleted. Run "custom-rule list" for updated list of rules')
	pass

def list(args):
	header, region = readConfiguration()
	endpoint = apiEndpoint.format(region)

	response = requests.get(url=endpoint, headers=header)
	rules = response.json()

	with open(f'{workspaceFolder}/rules.yaml', 'w') as configWriter:
		yaml.dump(data=rules["data"], stream=configWriter, indent=4, sort_keys=False)
	
	print("Rules were stored in rule.yaml file.")
	pass

def run(args):
	header, region = readConfiguration()
	endpoint = f'{apiEndpoint.format(region)}/run?accountId={args.accountId}&resourceData=true'
	
	rule = {}
	with open(f'{workspaceFolder}/{args.ruleId}.yaml', 'r') as ruleReader:
		rule = {
			"configuration": yaml.safe_load(stream=ruleReader)["attributes"]
		}
	
	rule["configuration"]["resourceId"] = args.resourceId
	response = requests.post(url=endpoint, json=rule, headers=header)

	dryrunFilename = f'{args.ruleId}.run.yaml'
	with open(f'{workspaceFolder}/{dryrunFilename}', 'w') as configWriter:
		yaml.dump(data=response.json(), stream=configWriter, indent=4, sort_keys=False)

	print(f'Run trace saved to file {dryrunFilename}. Note that resourceData information can be used for rule development')
	pass

def showProviders(args):
	response = requests.get(url="https://us-west-2.cloudconformity.com/v1/providers")
	providers = response.json()
	
	print(json.dumps([x.get("id") for x in providers["data"]], indent=4))
	pass

def showServices(args):
	response = requests.get(url="https://us-west-2.cloudconformity.com/v1/services")
	services = response.json()
	
	print(json.dumps([ x["id"] for x in services["data"] if x["attributes"]["provider"] == args.provider ], indent=4))
	pass

def showResourceTypes(args):
	response = requests.get(url="https://us-west-2.cloudconformity.com/v1/resource-types")
	resourceTypes = response.json()
	
	print(json.dumps([ x["id"] for x in resourceTypes["data"] if x["relationships"]["service"]["data"]["id"] == args.service ], indent=4))
	pass

parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
    description='''\
Manages custom rules in C1 Conformity.
See https://cloudone.trendmicro.com/docs/conformity/in-preview-custom-rules-overview/#using-custom-rules
For automation scenarios check out the Conformity Terraform Provider https://registry.terraform.io/providers/trendmicro/conformity/latest/docs''')

subparsers = parser.add_subparsers(help='sub-command help')

generateParser = subparsers.add_parser('generate', help='generate help')
generateParser.set_defaults(func=generate)

createParser = subparsers.add_parser('create', help='create help')
createParser.add_argument('--file', type=str, help='rule filename in /workspace folder')
createParser.set_defaults(func=create)

getParser = subparsers.add_parser('get', help='get help')
getParser.add_argument('--ruleId', type=str, required=True,
                    help='Conformity Custom Rule Id')
getParser.set_defaults(func=get)

updateParser = subparsers.add_parser('update', help='update help')
updateParser.add_argument('--file', type=str, help='rule filename in /workspace folder')
updateParser.set_defaults(func=update)

deleteParser = subparsers.add_parser('delete', help='delete help')
deleteParser.add_argument('--ruleId', type=str, required=True,
                    help='Conformity Custom Rule Id')
deleteParser.set_defaults(func=delete)

listParser = subparsers.add_parser('list', help='list help')
listParser.set_defaults(func=list)

runParser = subparsers.add_parser('run', help='list help')
runParser.add_argument('--ruleId', type=str, required=True,
                    help='Conformity Custom Rule Id')
runParser.add_argument('--resourceId', type=str, required=True,
                    help='Provider resource Id')
runParser.add_argument('--accountId', type=str, required=True,
                    help='Conformity Account Id where the resource is located')
runParser.set_defaults(func=run)

showProvidersParser = subparsers.add_parser('show-providers', help='show-providers help')
showProvidersParser.set_defaults(func=showProviders)

showServicesParser = subparsers.add_parser('show-services', help='show-services help')
showServicesParser.add_argument('--provider', type=str, required=True, choices=[
                    'aws', 'azure', 'gcp'], help='C1 Conformity Cloud Providers. See https://us-west-2.cloudconformity.com/v1/providers')
showServicesParser.set_defaults(func=showServices)

showResourceTypesParser = subparsers.add_parser('show-resource-types', help='show-resource-types help')
showResourceTypesParser.add_argument('--service', type=str, required=True,
                    help='Conformity Cloud Service. See https://us-west-2.cloudconformity.com/v1/services')
showResourceTypesParser.set_defaults(func=showResourceTypes)

configureParser = subparsers.add_parser('configure', help='configure help')
configureParser.add_argument('--region', type=str, required=True, choices=['us-1', 'trend-us-1', 'au-1', 'ie-1', 'sg-1', 'in-1', 'jp-1', 'ca-1', 'de-1'], help='Cloud One Conformity service region')
configureParser.add_argument('--apiKey', type=str, required=True, help='Full Access Cloud One API Key')
configureParser.set_defaults(func=configure)

args = parser.parse_args()
args.func(args)