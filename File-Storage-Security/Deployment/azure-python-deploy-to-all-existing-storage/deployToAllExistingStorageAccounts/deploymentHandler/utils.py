import os
import json
import tempfile
import logging

from azure.cli.core import get_default_cli
from azure.identity import ClientSecretCredential
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.storage import StorageManagementClient
from azure.mgmt.storage.models import StorageAccountUpdateParameters
from glom import glom

import cloudone_fss_api
import locations

# compose_tags: Adds the FSSMonitored tag to the Storage Account(s) that are monitored by Trend Micro File Storage Security
def compose_tags(existing_tags, new_tags):
    existing_tags.update(new_tags)
    return existing_tags

# tag_resource_in_template: Introduce tags into the ARM template (JSON) before deployment
def tag_resource_in_template(template_dict, deployment_tags_dict={}):

    taggable_resource_type_list = ["microsoft.storage/storageaccounts", "microsoft.servicebus/namespaces", "microsoft.keyvault/vaults", "microsoft.logic/workflows", "microsoft.resources/deploymentscripts", "microsoft.web/serverfarms", "microsoft.web/sites", "microsoft.insights/components"]

    for resource in template_dict["resources"]:
        tags_dict = {}
        tags_dict.update(deployment_tags_dict)
        if "tags" in resource:
            tags_dict.update(resource["tags"])
        if resource["type"].lower() in taggable_resource_type_list:
            resource.update({"tags": tags_dict})

    return template_dict

# get_deployment_mode_from_env: Gets the deployment mode this script is executed with
def get_deployment_mode_from_env(mode_key, DEPLOYMENT_MODES, DEFAULT_DEPLOYMENT_MODE):

    # Default mode is 'existing' storage accounts only
    deployment_mode = str(get_config_from_file('deployment_mode'))
    if deployment_mode:
        return deployment_mode if deployment_mode in DEPLOYMENT_MODES else DEFAULT_DEPLOYMENT_MODE
    if mode_key in os.environ.keys():
        return os.environ.get(mode_key)  
    logging.error("Missing Deployment Mode selection. Check \"" + mode_key + "\" env. variable or \"deployment_mode\" in the config.json file.")
    raise Exception("Missing Deployment Mode selection. Check \"" + mode_key + "\" env. variable or \"deployment_mode\" in the config.json file.")

# get_deployment_model_from_env: Gets the deployment model this script is executed with
def get_deployment_model_from_env(model_key, DEPLOYMENT_MODELS, DEFAULT_DEPLOYMENT_MODEL):

    # Default model is 'geographies'
    deployment_model = str(get_config_from_file('deployment_model'))
    if deployment_model:
        return deployment_model if deployment_model in DEPLOYMENT_MODELS else DEFAULT_DEPLOYMENT_MODEL
    if model_key in os.environ.keys():
        return os.environ.get(model_key)  
    logging.error("Missing Deployment Model selection. Check \"" + model_key + "\" env. variable or \"deployment_model\" in the config.json file.")
    raise Exception("Missing Deployment Model selection. Check \"" + model_key + "\" env. variable or \"deployment_model\" in the config.json file.")

# def get_blob_account_url(file_url):
#     return '/'.join(file_url.split('/')[0:3])

def azure_cli_run_command(command):
    args = command.split()
    temp = tempfile.TemporaryFile(mode="w") 

    cli = get_default_cli()
    cli.invoke(args, None, temp)

    # temp.seek(0)
    # data = temp.read().strip()
    temp.close()

    if cli.result.result:
        return cli.result.result
    elif cli.result.error:
        logging.error(cli.result.error)
        raise Exception(cli.result.error)
    return None

# apply_exclusions - get list of storage accounts to exclude from deployment
def apply_exclusions(filename, azure_storage_account_list):
    if not os.path.isfile(filename):
        logging.error("No file for exclusions. File 'exclude.txt' not found.\n")
        raise Exception("No file for exclusions. File 'exclude.txt' not found.\n")
    else:
        content = []
        with open(filename) as f:
            content = f.read().splitlines()

        temp_list = []
        for storage_account_name in content:
            for storage_account in azure_storage_account_list:                
                if storage_account["name"] == storage_account_name:
                    temp_list.append(storage_account)

        if len(temp_list):
            temp_list_names = ""
            for item in temp_list:
                temp_list_names += str(item["name"]) + ", "

            logging.info('Excluding ' + str(len(temp_list)) + ' storage accounts [' + temp_list_names + '] as per the contents in exclude.txt')
        else:
            logging.info('Excluding ' + str(len(temp_list)) + ' storage accounts from the deployment')

        for item in temp_list:
            azure_storage_account_list.remove(item)

        return azure_storage_account_list

# # Convert all Dict keys into a list for set-issubset checks
# def get_all_keys(dict):
#     for key, value in dict.items():
#         yield key
#         if isinstance(value, dict):
#             yield from get_all_keys(value)

def get_config_from_file(config_key):
    try:
        with open('config.json', 'r+') as f:
            json_object = json.loads(f.read())

        # Accessing Dict with Object notation for complex queries, using Glom
        if "." in config_key:          
            config_value = glom(json_object, config_key)
            if config_value:
                return config_value

        env_key = config_key.replace(".", "_").upper()        

        if env_key in os.environ.keys():
            env_value = os.environ.get(env_key)
            if env_value:
                return env_value

        if json_object[config_key]:
            return json_object[config_key]
    except:
        logging.error("ConfigError. Check environment variable \"" + env_key + "\" or \"" + config_key + "\" in the config.json file.")
        raise Exception("ConfigError. Check environment variable \"" + env_key + "\" or \"" + config_key + "\" in the config.json file.")

# def get_cloudone_region():
#     cloudone_config = get_config_from_file('cloudone')
#     if cloudone_config and "region" in cloudone_config.keys():
#         if cloudone_config['region']:
#             return str(cloudone_config['region'])
#     if 'CLOUDONE_REGION' in os.environ.keys():
#         return os.environ.get('CLOUDONE_REGION')
#     logging.error("Missing Cloud One Region. Check \"CLOUDONE_REGION\" env. variable or \"cloudone.region\" in the config.json file.")
#     raise Exception("Missing Cloud One Region. Check \"CLOUDONE_REGION\" env. variable or \"cloudone.region\" in the config.json file.")
    
# def get_cloudone_api_key():
#     cloudone_config = get_config_from_file('cloudone')
#     if cloudone_config and "api_key" in cloudone_config.keys():
#         if cloudone_config['api_key']:
#             return str(cloudone_config['api_key'])
#     if 'CLOUDONE_API_KEY' in os.environ.keys():
#         return os.environ.get('CLOUDONE_API_KEY')
#     logging.error("Missing Cloud One API Key. Check \"CLOUDONE_API_KEY\" env. variable or \"cloudone.api_key\" in the config.json file.")
#     raise Exception("Missing Cloud One API Key. Check \"CLOUDONE_API_KEY\" env. variable or \"cloudone.api_key\" in the config.json file.")

# def get_cloudone_max_storage_to_scanner_count():
#     cloudone_config = get_config_from_file('cloudone')
#     if cloudone_config and "max_storage_stack_per_scanner_stack" in cloudone_config.keys():
#         if cloudone_config['max_storage_stack_per_scanner_stack']:
#             return str(cloudone_config['max_storage_stack_per_scanner_stack'])
#     if 'MAX_STORAGE_STACK_PER_SCANNER_STACK' in os.environ.keys():
#         return os.environ.get('MAX_STORAGE_STACK_PER_SCANNER_STACK')
#     return 50 # Recommended value for the number of Storage Stack(s) per Scanner Stack

def get_subscription_id():
    azure_subscription_id = str(get_config_from_file('subscription_id'))
    if azure_subscription_id:
        return azure_subscription_id
    if 'AZURE_SUBSCRIPTION_ID' in os.environ.keys():
        return os.environ.get('AZURE_SUBSCRIPTION_ID')  
    logging.error("Missing Azure Subscription ID. Check \"AZURE_SUBSCRIPTION_ID\" env. variable or \"subscription_id\" in the config.json file.")
    raise Exception("Missing Azure Subscription ID. Check \"AZURE_SUBSCRIPTION_ID\" env. variable or \"subscription_id\" in the config.json file.")

def get_deployment_tags():    
    deployment_tags = get_config_from_file('deployment_tags')
    if deployment_tags:
        return deployment_tags
    return None

def get_subscription_id_from_resource_group_id(resource_group_id):

    return resource_group_id.split('/')[2]

def get_resource_name_from_resource_id(resource_id):

    return resource_id.split('/')[-1]

def get_resource_group_name_from_resource_id(resource_id):

    return resource_id.split('/')[4]

def remove_storage_accounts_with_cloudone_storage_stacks(azure_storage_account_list):

    cloudone_storage_stack_list = cloudone_fss_api.get_storage_stacks()

    if cloudone_storage_stack_list:

        temp_list = []
        for storage_account in azure_storage_account_list:
            
            for storage_stack in cloudone_storage_stack_list["stacks"]:

                if storage_account["name"] == storage_stack["storage"]:

                    temp_list.append(storage_account)

        for storage_account in temp_list:

            azure_storage_account_list.remove(storage_account)        

    return azure_storage_account_list

def remove_scanner_stacks_exceed_max_storage_account_count(scanner_stacks_map_by_geographies_dict, max_storage_to_scanner_count):

    remove_scanner_stack_list = []

    for scanner_stack_geography in scanner_stacks_map_by_geographies_dict:

        for scanner_stack in scanner_stacks_map_by_geographies_dict[scanner_stack_geography]:

            storage_account_count = len(cloudone_fss_api.get_associated_storage_stacks_to_scanner_stack(scanner_stack["stackID"])["stacks"])
            # Update storageStackCount value to the scanner_stack
            scanner_stack.update({"storageStackCount": storage_account_count})

            if storage_account_count > max_storage_to_scanner_count:                
                remove_scanner_stack_list.append(scanner_stack["stackID"])            
    
    for stack_id in remove_scanner_stack_list:

        for scanner_stack_geography in scanner_stacks_map_by_geographies_dict:

            for scanner_stack in scanner_stacks_map_by_geographies_dict[scanner_stack_geography]:
                
                if stack_id == scanner_stack["stackID"]:

                    scanner_stacks_map_by_geographies_dict[scanner_stack_geography].remove(scanner_stack)

    return scanner_stacks_map_by_geographies_dict

# function to return dict key for any value
def get_dict_key(value_dict, val):
    if value_dict:
        for key, value in value_dict.items():
            if val == value:
                return key
    return None

def trim_resource_name(resource_name, start_trim_count=0, end_trim_count=0):
    if len(resource_name) > (start_trim_count + end_trim_count):
        return resource_name[:start_trim_count] + resource_name[-end_trim_count:]
    return resource_name.lower()

def trim_location_name(azure_location_name):
    if len(azure_location_name) > 6:
        azure_location_display_name = locations.get_azure_location_detail(azure_location_name)["displayName"]
        string_output = None
        temp_list = azure_location_display_name.split(" ")    
        for item in temp_list[:len(temp_list)-1]:
            if not string_output:
                string_output = str(item[0])
            else:
                string_output = string_output + str(item[0])
        string_output = string_output + str(temp_list[-1][:3])
        return string_output.lower()
    return azure_location_name

def trim_spaces(string_value):
    if " " in string_value:
        string_output = None
        temp_list = string_value.split(" ")
        for item in temp_list[:len(temp_list)-1]:
            if not string_output:
                string_output = str(item[0])
            else:
                string_output = string_output + str(item[0])
        string_output = string_output + str(temp_list[-1])
        return string_output.lower()
    elif len(string_value) > 6:
        return string_value[:3].lower()
    return string_value.lower()

def list_resources_in_resource_group(subscription_id, resource_group_name):
    credentials = ClientSecretCredential(
        client_id=os.environ['AZURE_CLIENT_ID'],
        client_secret=os.environ['AZURE_CLIENT_SECRET'],
        tenant_id=os.environ['AZURE_TENANT_ID']       
    )
    client = ResourceManagementClient(credentials, subscription_id)
    return client.resources.list_by_resource_group(resource_group_name)