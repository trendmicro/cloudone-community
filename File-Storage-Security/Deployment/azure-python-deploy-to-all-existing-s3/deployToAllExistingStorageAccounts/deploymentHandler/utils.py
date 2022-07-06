import os
import json
from re import template
from azure.cli.core import get_default_cli

# compose_tags: Adds the FSSMonitored tag to the Storage Account(s) that are monitored by Trend Micro File Storage Security
def compose_tags(existing_tags, FSS_MONITORED_TAG):
    return {
        **existing_tags,
        **{
            f'{FSS_MONITORED_TAG}': True
        }
    }

# get_deployment_mode_from_env: Gets the deployment mode this script is executed with
def get_deployment_mode_from_env(mode_key, DEPLOYMENT_MODES, DEFAULT_DEPLOYMENT_MODE):

    # Default mode is 'existing' storage accounts only
    mode = os.environ.get(mode_key, 'existing').lower()
    return mode if mode in DEPLOYMENT_MODES else DEFAULT_DEPLOYMENT_MODE

# get_deployment_model_from_env: Gets the deployment model this script is executed with
def get_deployment_model_from_env(model_key, DEPLOYMENT_MODELS, DEFAULT_DEPLOYMENT_MODEL):

    # Default model is 'geographies'
    model = os.environ.get(model_key, 'geographies').lower()
    return model if model in DEPLOYMENT_MODELS else DEFAULT_DEPLOYMENT_MODEL

def get_blob_account_url(file_url):
    return '/'.join(file_url.split('/')[0:3])

def azure_cli_run_command(command):
    args = command.split()

    cli = get_default_cli()
    cli.invoke(args)

    if cli.result.result:
        return cli.result.result
    elif cli.result.error:
        raise Exception(cli.result.error)
    return None

# apply_exclusions - get list of storage accounts to exclude from deployment
def apply_exclusions(filename, deploy_storage_stack_list):
    if not os.path.isfile(filename):
        print("\n\tNo file for exclusions. File 'exclude.txt' not found.\n")
    else:
        content = []
        with open(filename) as f:
            content = f.read().splitlines()
        
        temp_list = []
        for storage_account_name in content:
            for storage_account in deploy_storage_stack_list:
                if storage_account["name"] == storage_account_name:
                    temp_list.append(storage_account)

        if len(temp_list):
            temp_list_names = ""
            for item in temp_list:
                temp_list_names += str(item["name"]) + ", "

            print('\n\tExcluding ' + str(len(temp_list)) + ' storage accounts [' + temp_list_names + '] as per the contents in exclude.txt')
        else:
            print('\n\tExcluding ' + str(len(temp_list)) + ' storage accounts from the deployment')

        for item in temp_list:
            deploy_storage_stack_list.remove(item)

        return deploy_storage_stack_list

    return None

def get_config_from_file(config_key):
    f = open('config.json', 'r+')
    json_object = json.loads(f.read())
    if config_key in json_object.keys():
        return str(json_object[config_key])
    return ""

def get_subscription_id():
    azure_subscription_id = get_config_from_file('subscription_id')
    return os.environ.get('AZURE_SUBSCRIPTION_ID', azure_subscription_id) # your Azure Subscription Id - 00000000-0000-0000-0000-000000000000