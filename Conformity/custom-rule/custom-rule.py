#!/usr/local/bin/python3

import os
import argparse
import sys
from urllib.error import HTTPError
import requests
import json
import yaml

# helper function
def readFile(path, name):
	fileLocation = f'{path}/{name}'
	content = {}
	
	try:
		with open(fileLocation, 'r') as fileReader:
			content = yaml.safe_load(fileReader)

	except OSError as error:
		print(f'There was an error while reading from {fileLocation}')
		raise error
	else:
		return content

# helper function
def writeFile(folder, filename, content):
	location = f'{folder}/{filename}'	

	try:
		with open(location, 'w') as fileWriter:
			yaml.dump(data=content, stream=fileWriter, indent=4, sort_keys=False)

	except OSError as error:
		print(f'There was an error while writing to {location}')
		raise error 

# base class definition
class Command:
	def __init__(self, name):
		self.name = name
		self.help = f'{name} --help'
		pass

	def addArguments(self, parser):
		pass

	def execute(self, args):
		pass

class Configure(Command):
	def __init__(self, name):
		super().__init__(name)
		pass

	def addArguments(self, parser):
		parser.add_argument('--region', type=str, required=True, choices=['us-1', 'trend-us-1', 'au-1', 'ie-1', 'sg-1', 'in-1', 'jp-1', 'ca-1', 'de-1'], help='Cloud One Conformity service region')
		parser.add_argument('--apiKey', type=str, required=True, help='Full Access Cloud One API Key')
		parser.add_argument('--workspace', type=str, required=False, default='./workspace', help='Work folder containing rule and symbols files')
		pass

	def execute(self, args):
		try:
			self.configFolder = os.path.expanduser(path='~/.conformity-custom-rule')
			self.configFilename = "config.yaml"

			self.configuration = {
				"region": args.region,
				"apiKey": args.apiKey,
				"workspace": os.path.expanduser(path=args.workspace) 
			}

			# prepare the configuration file
			if not os.path.isdir(self.configFolder):
				os.makedirs(self.configFolder)

			writeFile(folder=self.configFolder, filename=self.configFilename, content=self.configuration)

			# prepare the workspace folder
			if not os.path.isdir(self.configuration["workspace"]):
				os.makedirs(self.configuration["workspace"])
			
		except OSError as error:

			print(f'There was an error while configuring the tool')
			print(error)			

		else:
			pass

# base class extension for commands needing configuration
class ConfiguredCommand(Command):
	def __init__(self, name):
		super().__init__(name)

	def configure(self):
		try:
			configFolder = os.path.expanduser(path='~/.conformity-custom-rule')
			configFilename = 'config.yaml'
			configurationLocation = f'{configFolder}/{configFilename}'
			configurations = readFile(configFolder, configFilename)

		except OSError as error :

			print("The was an error while opening the tool's configuration. Use './custom-rule.py configure help' to configure the tool")
			raise error

		else:
			self.header = {
				"Content-Type": "application/vnd.api+json",
				"api-version": "v1",
				"Authorization": f'ApiKey {configurations.get("apiKey")}'
			}

			self.region = configurations.get("region")
			self.configurationLocation = configurationLocation
			self.apiEndpoint = f'https://conformity.{self.region}.cloudone.trendmicro.com/api/custom-rules'
			self.workspaceFolder = configurations.get("workspace")

			pass

	def addArguments(self, parser):
		return super().addArguments(parser)

	def execute(self, args):
		return super().execute(args)
	pass

class Create(ConfiguredCommand):
	def __init__(self, name):
		super().__init__(name)
		pass
	
	def addArguments(self, parser):
		parser.add_argument('--file', type=str, help='rule filename in workspace folder')
		pass
	
	def execute(self, args):
		super().configure()

		try:
			rule = readFile(path=self.workspaceFolder, name=args.file)

			apiEndpoint = self.apiEndpoint.format(self.region)
			response = requests.post(apiEndpoint, json=rule, headers=self.header)
			customRule = response.json()

			if "errors" in customRule:
				raise ValueError(f'{customRule}')

			ruleId = customRule["data"]["id"]
			ruleFilename = f'{ruleId}.yaml'

			writeFile(folder=self.workspaceFolder, filename=ruleFilename, content=customRule["data"])

		except ValueError as valueError:
			print("The Cloud One Conformity API returned an error.")
			print(valueError)

		except requests.RequestException as apiError:
			print("There was an error while interacting with the Cloud One API")
			print(apiError)		

		except OSError as error:
			print("There was an error while reading and saving the rule locally.")
			print(error)
		
		else:
			print(f'Custom rule saved to file {ruleId}.yaml')
			pass

	pass

class Get(ConfiguredCommand):

	def __init__(self, name):
		super().__init__(name)
		pass

	def addArguments(self, parser):
		parser.add_argument('--ruleId', type=str, required=True, help='Conformity Custom Rule Id')
		pass

	def execute(self, args):
		super().configure()

		try:

			endpoint = f'{self.apiEndpoint}/{args.ruleId}' 

			response = requests.get(url=endpoint, headers=self.header)
			rule = response.json()

			if "errors" in rule:
				raise ValueError(f'{rule}')

			ruleId = rule["data"][0]["id"]
			ruleFilename = f'{ruleId}.yaml'

			writeFile(folder=self.workspaceFolder, filename=ruleFilename, content=rule["data"][0])

		except ValueError as badIdError:
			print(f'Custom Rule {args.ruleId} was invalid.')
			print(badIdError)

		except requests.exceptions.RequestException as apiError:
			print("There was an error while interacting with the Cloud One API.")
			print(apiError)		

		except OSError as error:
			print("There was an error while saving the rule locally.")
			print(error)
		
		else:
			print(f'Custom rule saved to file {ruleFilename}.yaml')
			pass
	pass

class Update(ConfiguredCommand):

	def __init__(self, name):
		super().__init__(name)
		pass
	
	def addArguments(self, parser):
		parser.add_argument('--file', type=str, help='rule filename in workspace folder')
		pass
	
	def execute(self, args):
		super().configure()

		try:
			rule = readFile(path=self.workspaceFolder, name=args.file)
			endpoint = f'{self.apiEndpoint}/{rule.get("id")}' 

			response = requests.put(url=endpoint, json=rule["attributes"], headers=self.header)
			updatedRule = response.json()
			
			if "errors" in updatedRule:
				raise ValueError(f'{updatedRule}')

			ruleId = updatedRule["data"]["id"]
			ruleFilename = f'{ruleId}.yaml'

			writeFile(folder=self.workspaceFolder, filename=ruleFilename, content=updatedRule["data"])

		except ValueError as valueError:
			print("The Cloud One Conformity API returned an error.")
			print(valueError)

		except requests.RequestException as apiError:
			print("There was an error while interacting with the Cloud One API")
			print(apiError)		

		except OSError as error:
			print("There was an error while saving the rule locally.")
			print(error)
		
		else:
			print(f'Custom rule saved to file {ruleFilename}.yaml')
			pass

	pass

class Delete(ConfiguredCommand):

	def __init__(self, name):
		super().__init__(name)
	
	def addArguments(self, parser):
		parser.add_argument('--ruleId', type=str, required=True, help='Conformity Custom Rule Id')
		pass

	def execute(self, args):
		self.configure()

		try:
			endpoint = f'{self.apiEndpoint}/{args.ruleId}'
			response = requests.delete(url=endpoint, headers=self.header)
			deletedRule = response.json()

			if "errors" in deletedRule:
				raise ValueError(f'{deletedRule}')

		except ValueError as valueError:
			print("The Cloud One Conformity API returned an error.")
			print(valueError)

		except requests.RequestException as apiError:

			print("There was an error while interacting with the Cloud One API")
			print(apiError)		

		else:
			print(f'Custom Rule "{args.ruleId}" deleted.')
			pass
pass

class List(ConfiguredCommand):

	def __init__(self, name):
		super().__init__(name)

	def execute(self, args):
		super().configure()

		try:
			endpoint = self.apiEndpoint

			response = requests.get(url=endpoint, headers=self.header)
			response.raise_for_status()

			if "errors" in rules:
				raise ValueError(f'Error {response.json()}')

			rules = response.json()
			if len(rules["data"]) == 0:
				raise IndexError("No custom rules returned.")

			for rule in rules["data"]:
				ruleId = rule["id"]
				writeFile(folder=self.workspaceFolder, filename=f'{ruleId}.yaml', content=rule)

			print(f'Rules were stored in individual files at {self.workspaceFolder}')
			pass

		except ValueError as valueError:
			print("The Cloud One Conformity API returned an error")
			print(valueError)

		except IndexError as indexError:
			print("This organization has no custom rules")

		except HTTPError as httpError:
			print("There was an error while processing the API request.")
			print(httpError)

		except requests.RequestException as apiError:
			print("There was an error while interacting with the Cloud One API")
			print(apiError)		

		except OSError as error:
			print("There was an error while saving the rule locally.")
			print(error)

class Generate(ConfiguredCommand):

	def __init__(self, name):
		super().__init__(name)
	
	def execute(self, args):
		super().configure()

		try:

			emptyRule = {
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

			writeFile(folder=self.workspaceFolder, filename="emptyRule.yaml", content=emptyRule)

		except OSError as error:
			print("There was an error while saving the rule locally.")
			print(error)
		
		else:
			print(f'Sample rule was stored at {self.workspaceFolder}/emptyRule.yaml')
			pass
		
class Run(ConfiguredCommand):
	def __init__(self, name):
		super().__init__(name)

	def addArguments(self, parser):
		parser.add_argument('--ruleId', type=str, required=True, help='Conformity Custom Rule Id')
		parser.add_argument('--resourceId', type=str, required=True, help='Provider resource Id')
		parser.add_argument('--accountId', type=str, required=True, help='Conformity Account Id where the resource is located')
		pass

	def execute(self, args):
		super().configure()

		try:
			endpoint = f'{self.apiEndpoint}/run?accountId={args.accountId}&resourceData=true'
			
			rule = {
				"configuration": readFile(path=self.workspaceFolder, name=f'{args.ruleId}.yaml')["attributes"]
			}
			
			rule["configuration"]["resourceId"] = args.resourceId
			response = requests.post(url=endpoint, json=rule, headers=self.header)

			runTrace = response.json()
			if "errors" in runTrace:
				raise ValueError(f'{runTrace}')

			ruleRunFilename = f'{args.ruleId}.run.yaml'
			writeFile(folder=self.workspaceFolder, filename=ruleRunFilename, content=runTrace)
					
		except ValueError as valueError:
			print("The Cloud One Conformity API returned an error")
			print(valueError)

		except requests.RequestException as apiError:
			print("There was an error while interacting with the Cloud One API")
			print(apiError)		

		except HTTPError as httpError:
			print("There was an error while processing the API request.")
			print(httpError)

		except OSError as error:
			print("There was an error while saving the rule locally.")
			print(error)
		
		else:
			print(f'Run trace saved to file {self.workspaceFolder}/{ruleRunFilename}. Note that resourceData information can be used for rule development')
			pass

# base class for symbols command
class SymbolsCommand(ConfiguredCommand):
	def __init__(self, name):
		super().__init__(name)

	def addArguments(self, parser):
		return super().addArguments(parser)

	def execute(self, args):
		super().configure()

		# amend the api endpoint
		self.apiEndpoint = f'https://us-west-2.cloudconformity.com'

		pass

class Providers(SymbolsCommand):
	def __init__(self, name):
		super().__init__(name)
		
	def execute(self, args):
		super().execute(args)

		try:
			endpoint = f'{self.apiEndpoint}/v1/providers'
			response = requests.get(url=endpoint)

			providersFilename = 'providers.yaml'
			providers = response.json() 

			writeFile(folder=self.workspaceFolder, filename=providersFilename, content=[x.get("id") for x in providers["data"]])
					
		except requests.RequestException as apiError:
			print("There was an error while interacting with the Cloud One API")
			print(apiError)		

		except OSError as error:
			print("There was an error while saving the providers locally.")
			print(error)
		
		else:
			print(f'Providers written to {self.workspaceFolder}/{providersFilename}')
			pass

class Services(SymbolsCommand):
	def __init__(self, name):
		super().__init__(name)

	def addArguments(self, parser):
		parser.add_argument('--provider', type=str, required=True, choices=['aws', 'azure', 'gcp'], help='C1 Conformity Cloud Providers')

	def execute(self, args):
		super().execute(args)

		try:
			endpoint = f'{self.apiEndpoint}/v1/services'
			response = requests.get(url=endpoint)
			allServices = response.json()
			selectedServices = [ x["id"] for x in allServices["data"] if x["attributes"]["provider"] == args.provider]

			if len(selectedServices) == 0:
				raise IndexError(f'No cloud services returned.')

			servicesFilename = 'services.yaml'

			writeFile(folder=self.workspaceFolder, filename=servicesFilename, content=selectedServices)
		except ValueError as badArgument:
			print(f'No services were returned for provider {args.provider}')
			print(badArgument)
					
		except requests.RequestException as apiError:
			print("There was an error while interacting with the Cloud One API")
			print(apiError)		

		except OSError as error:
			print("There was an error while saving the providers locally.")
			print(error)
		
		else:
			print(f'Services written to {self.workspaceFolder}/{servicesFilename}')
			pass

class Resources(SymbolsCommand):
	def __init__(self, name):
		super().__init__(name)
	
	def addArguments(self, parser):
		parser.add_argument('--service', type=str, required=True,
                    help='Conformity Cloud Service')

	def execute(self, args):
		super().execute(args)

		try:
			endpoint = f'{self.apiEndpoint}/v1/resource-types'
			response = requests.get(url=endpoint)

			allResourceTypes = response.json()
			selectedResourceTypes = [ x["id"] for x in allResourceTypes["data"] if x["relationships"]["service"]["data"]["id"] == args.service ]

			if len(selectedResourceTypes) == 0:
				raise IndexError(f'No resource types were returned')

			resourcesFilename = 'resource-types.yaml'

			writeFile(folder=self.workspaceFolder, filename=resourcesFilename, content=selectedResourceTypes)
		
		except IndexError as badArgument:
			print(f'No resource types were returned for service {args.service}')
			print(badArgument)
					
		except requests.RequestException as apiError:
			print("There was an error while interacting with the Cloud One API")
			print(apiError)		

		except OSError as error:
			print("There was an error while saving the providers locally.")
			print(error)
		
		else:
			print(f'Resource types written to {self.workspaceFolder}/{resourcesFilename}')
			pass
		
parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
    description='''\
Manages custom rules in C1 Conformity.
See https://cloudone.trendmicro.com/docs/conformity/in-preview-custom-rules-overview/#using-custom-rules for a detailed explanation of Conformity Custom Rules.
For automation scenarios check out the Conformity Terraform Provider https://registry.terraform.io/providers/trendmicro/conformity/latest/docs''')

subparsers = parser.add_subparsers(help='sub-command help')

commands = [
	Configure('configure'),
	Create('create'),
	Get('get'),
	Update('update'),
	Delete('delete'),
	List('list'),
	Generate('generate'),
	Run('run'),
	Providers('show-providers'),
	Services('show-services'),
	Resources('show-resource-types')
]

for cmd in commands:
	subparser = subparsers.add_parser(name=cmd.name, help=cmd.help)
	cmd.addArguments(subparser)
	subparser.set_defaults(func=cmd.execute)

args = parser.parse_args()
args.func(args)