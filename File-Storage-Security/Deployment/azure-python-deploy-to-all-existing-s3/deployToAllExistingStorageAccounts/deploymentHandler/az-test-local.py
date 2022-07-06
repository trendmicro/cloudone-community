import logging
import os
# import json

import azure.functions as func
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobClient, BlobServiceClient
from azure.storage.blob._shared.models import AccountSasPermissions
from azure.storage.blob._shared_access_signature import BlobSharedAccessSignature
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.storage import StorageManagementClient

from datetime import datetime

from yaml import scan

from Deployer import Deployer

import utils
import locations
import geographies
import service_principal
# import resource_groups
# import rbac


'''
This script requires an additional text file for storage accounts to exclude, found in the "exclude.txt" file
Will deploy FSS Storage stack(s) to all existing or new storage accounts,  defined by your DEPLOYMENT_MODE environment variable
All FSS Storage stack(s) will link to FSS Scanner Stack(s), defined by your DEPLOYMENT_MODEL environment variable
'''

exclusion_file_name = 'exclude.txt'
DEPLOYMENT_MODES = {
    'existing',  # Deploy FSS scanning to existing buckets (runs one-time)
    'new',  # Deploy FSS scanning for new storage accounts (via an event listener)
}
DEFAULT_DEPLOYMENT_MODE = 'existing'

DEPLOYMENT_MODELS = {
    'geographies',  # One per geographyGroup, Default
    'one-to-one',  # One per Storage Account
    'single'  # Just One for all Storage Accounts (not recommended for multi-region storage accounts)
}
DEFAULT_DEPLOYMENT_MODEL = 'geographies'

FSS_LOOKUP_TAG = 'AutoDeployFSS'
FSS_MONITORED_TAG = 'FSSMonitored'

def main():
    '''
        Mind map (Existing Storage Accounts)
        --------------------------------------

        - getStorageAccounts() with the FSS_LOOKUP_TAG set to True -- DONE
        - Iterate over each Storage Account and deploy the Storage Stack -- IN PROGRESS
        - Build atleast 1 Scanner Stack
        - Associate Storage Stack(s) with the Scanner Stack
        - Display warning on scalability of the Scanner Stack and Azure Service Quotas. Recommend to split into multiple Scanner Stacks by raising a support ticket
        - Recommend scanning all existing blobs in the Storage Account(s) that are not scanned by FSS for reasons of compliance and better OpsSec 

        Mind map (New Storage Accounts)
        ---------------------------------

        - Setup a listener for new Storage Accounts. The listener gets triggered once the creation event occurs
        - getStorageAccounts() with the new Storage Account name
        - Build a Storage Stack for the new Storage Account
        - Identify an existing Scanner Stack that can be used to associate the new Storage Stack
        - Associate Storage Stack(s) with the Scanner Stack
        - Display warning on scalability of the Scanner Stack and Azure Service Quotas. Recommend to split into multiple Scanner Stacks by raising a support ticket

        Note: All new blobs in the new Storage Account should be scanned by FSS as and when they are dumped in the Storage Account
    '''

    subscription_id = utils.get_subscription_id()

    azure_supported_locations_obj_by_geography_groups_dict = locations.get_azure_supported_locations()

    # FSS Storage Stack Deployment

    deploy_storage_stack_list = []
    deployment_mode = utils.get_deployment_mode_from_env('DEPLOYMENT_MODE', DEPLOYMENT_MODES, DEFAULT_DEPLOYMENT_MODE)

    if deployment_mode == 'existing':
        deploy_storage_stack_list = get_storage_accounts(FSS_LOOKUP_TAG)

        if deploy_storage_stack_list:
            deploy_storage_stack_list = utils.apply_exclusions(exclusion_file_name, deploy_storage_stack_list)
            deploy_fss_storage_stack(subscription_id,deploy_storage_stack_list)
        else:
            raise Exception('No Storage Account(s) match the \"' + FSS_LOOKUP_TAG + '\" tag. Exiting ...')
    else:
        # deployment_mode == 'new'
        # TODO: Build an event listener to trigger deployment based on Storage Account creation events.
        raise Exception('Deploying to new storage account based on an event listener is yet to be built into this tool.')

    # FSS Scanner Stack Deployment
    deployment_model = utils.get_deployment_model_from_env('DEPLOYMENT_MODEL', DEPLOYMENT_MODELS, DEFAULT_DEPLOYMENT_MODEL)

    if deployment_model == 'geographies':
        unique_geographies = geographies.get_geographies_from_storage_accounts(deploy_storage_stack_list, azure_supported_locations_obj_by_geography_groups_dict)
        deploy_fss_scanner_stack(subscription_id, unique_geographies)

    # credentials = DefaultAzureCredential(exclude_environment_credential=True)
    # resource_client = ResourceManagementClient(credentials, subscription_id)
    # storage_client = StorageManagementClient(credentials, subscription_id)

    # for item in storage_client.storage_accounts.list():
    #     print_item(item)

# get_storage_accounts: Provides a list of all Azure Storage Accounts in this subscription with the Tag AutoDeployFSS = true
def get_storage_accounts(FSS_LOOKUP_TAG):

    cliCommand = 'storage account list'

    getStorageAccountsJSONResponse = utils.azure_cli_run_command(cliCommand)

    logging.info("\n\tTag Lookup: " + FSS_LOOKUP_TAG)

    deploy_storage_stack_list = []

    if getStorageAccountsJSONResponse:

        for storageAccount in getStorageAccountsJSONResponse:

            if storageAccount["tags"]:
                
                if FSS_LOOKUP_TAG in storageAccount["tags"].keys():

                    if storageAccount["tags"][FSS_LOOKUP_TAG]:

                        deploy_storage_stack_list.append({"name": storageAccount["name"], "location": storageAccount["location"], "tags": storageAccount["tags"]})
                
        return deploy_storage_stack_list

    return None
        
    # print(str(deploy_storage_stack_list))

    # # TODO: Complete the get_storage_accounts block
    # credential = DefaultAzureCredential(exclude_environment_credential=True)
    # blob_service_client = BlobServiceClient(account_url=self.url, credential=credential)

def deploy_fss_storage_stack(subscription_id, deploy_storage_stack_list):

    # File Storage Security Storage Stack deployment template can be found at https://github.com/trendmicro/cloudone-filestorage-deployment-templates/blob/master/azure/FSS-Storage-Stack-Template.json

    app_id = utils.get_config_from_file("app_id")
    cloud_one_region = utils.get_config_from_file("cloud_one_region")

    if app_id and cloud_one_region:

        for storage_account in deploy_storage_stack_list:

            storage_stack_name = "fss-storage-stack-" + str(storage_account["name"]) + str(storage_account["location"]) + "-autodeploy"
            resource_group_name = storage_stack_name + "-rg"

            # resource_group_name = resource_groups.create_resource_group(subscription_id, resource_group_name, storage_account["location"])

            print(storage_stack_name, str(storage_account), resource_group_name)

            msg = "\n\tInitializing the Deployer class with subscription id: {}, resource group: {}...\n"
            msg = msg.format(subscription_id, resource_group_name)
            print(msg)

            service_principal_id = service_principal.query_service_principal(app_id)

            if not service_principal_id:
                service_principal_id = utils.azure_cli_run_command('ad sp create --id ' + app_id)
            print(str(service_principal_id))
            # rbac.createServicePrincipal()

            storage_stack_params = {
                'FileStorageSecurityServicePrincipalID': service_principal_id,
                'CloudOneRegion': cloud_one_region,
                'ScannerIdentityPrincipalID': '',
                'ScannerQueueNamespace': '',
                'BlobStorageAccountResourceID': '',
                'BlobSystemTopicExist': 'No',
                'BlobSystemTopicName': 'BlobEventTopic',
                'UpdateScanResultToBlobMetadata': 'Yes',
                'ReportObjectKey': 'No',
                'StackPackageLocation': 'https://file-storage-security.s3.amazonaws.com',
                'Version': 'latest',
                'SharedAccessSignature': ''
            }

            # Initialize the deployer class
            deployer = Deployer(subscription_id, resource_group_name, storage_stack_params)

            print("Beginning the deployment... \n\n")
            # Deploy the template
            my_deployment = deployer.deploy(storage_account["location"], "storage")

            print("Done deploying!!\n\n")

def deploy_fss_scanner_stack(subscription_id, geography_groups):

    # File Storage Security Scanner Stack deployment templates can be found at https://github.com/trendmicro/cloudone-filestorage-deployment-templates/blob/master/azure/FSS-Scanner-Stack-Template.json

    app_id = utils.get_config_from_file("app_id")
    cloud_one_region = utils.get_config_from_file("cloud_one_region")

    if app_id and cloud_one_region:

        for geography_group in geography_groups:
        
            scanner_stack_name = "fss-scanner-" + str(geography_group.lower()) + "-autodeploy"
            resource_group_name = scanner_stack_name + "-rg"

            azure_recommended_location = locations.get_azure_recommended_location_by_geography_group(geography_group, geography_groups)

            # resource_group_name = resource_groups.create_resource_group(subscription_id, resource_group_name, azure_recommended_location)

            msg = "\nInitializing the Deployer class with subscription id: {}, resource group: {}...\n\n"
            msg = msg.format(subscription_id, resource_group_name)
            print(msg)

            service_principal_id = service_principal.query_service_principal(app_id)

            if not service_principal_id:
                service_principal_id = utils.azure_cli_run_command('ad sp create --id ' + app_id)
            print(str(service_principal_id))
            # rbac.createServicePrincipal()

            scanner_stack_params = {
                'FileStorageSecurityServicePrincipalID': service_principal_id,
                'CloudOneRegion': cloud_one_region,
                'StackPackageLocation': 'https://file-storage-security.s3.amazonaws.com',
                'Version': 'latest',
                'SharedAccessSignature': ''
            }

            # Initialize the deployer class
            deployer = Deployer(subscription_id, resource_group_name, scanner_stack_params)

            print("Beginning the deployment... \n\n")
            # Deploy the template
            my_deployment = deployer.deploy(azure_recommended_location, "scanner")

            print("Done deploying!!\n\n")

if __name__ == "__main__":
    main()
