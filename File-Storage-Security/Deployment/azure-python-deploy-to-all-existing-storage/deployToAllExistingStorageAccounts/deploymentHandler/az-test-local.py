import logging
from re import A

import azure.functions as func
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobClient, BlobServiceClient
from azure.storage.blob._shared.models import AccountSasPermissions
from azure.storage.blob._shared_access_signature import BlobSharedAccessSignature
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.storage import StorageManagementClient

from datetime import datetime

import utils
import locations
import storage_accounts
import deployments
import deployment_geographies
import deployment_one_to_one
import deployment_single

# TODO: Remove unused code and dependencies
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
# TODO: Add tags to FSS deployed stacks/resources
FSS_MONITORED_TAG = 'FSSMonitored'
FSS_SUPPORTED_REGIONS = ["centralus", "eastus", "eastus2", "southcentralus", "westus", "westus2", "centralindia", "eastasia", "japaneast", "koreacentral", "southeastasia", "francecentral", "germanywestcentral", "northeurope", "switzerlandnorth", "uksouth", "westeurope", "uaenorth", "brazilsouth"] # List last updated on 2022-07-19T11:32:11-04:00, from https://cloudone.trendmicro.com/docs/file-storage-security/supported-azure/

def main():
    '''
        Mind map (Existing Storage Accounts)
        --------------------------------------

        - getStorageAccounts() with the FSS_LOOKUP_TAG set to True -- DONE
        - Iterate over each Storage Account and deploy atleast 1 Scanner Stack -- IN PROGRESS
        - Iterate over each Storage Account and build Storage Stack and Associate Scanner Stack in the process -- IN PROGRESS
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

    # # Testing
    # # TODO: Remove offline hacks
    # print(str(cloudone_fss_api.map_scanner_stacks_to_azure_locations()))
    # exit(0)

    subscription_id = utils.get_subscription_id()

    azure_supported_locations_obj_by_geography_groups_dict = locations.get_azure_supported_locations()

    # Get List of Storage Accounts to deploy FSS
    deploy_storage_stack_list = []
    deployment_mode = utils.get_deployment_mode_from_env('DEPLOYMENT_MODE', DEPLOYMENT_MODES, DEFAULT_DEPLOYMENT_MODE)

    if deployment_mode == 'existing':
        deploy_storage_stack_list = storage_accounts.get_storage_accounts(FSS_LOOKUP_TAG)

        if deploy_storage_stack_list:
            deploy_storage_stack_list = utils.apply_exclusions(exclusion_file_name, deploy_storage_stack_list)            
        else:
            raise Exception('No Storage Account(s) match the \"' + FSS_LOOKUP_TAG + '\" tag. Exiting ...')

        if deploy_storage_stack_list:
            deploy_storage_stack_list = utils.remove_storage_accounts_with_storage_stacks(deploy_storage_stack_list)
        else:
            raise Exception('No Storage Account(s) match the \"' + FSS_LOOKUP_TAG + '\" tag. Exiting ...')

    else: # deployment_mode == 'new'        
        # # TODO: Build an event listener to trigger deployment based on Storage Account creation events.
        raise Exception('Deploying to new storage account based on an event listener is yet to be built into this tool.')

    # Get Deployment Model - geographies, one-to-one or  single
    deployment_model = utils.get_deployment_model_from_env('DEPLOYMENT_MODEL', DEPLOYMENT_MODELS, DEFAULT_DEPLOYMENT_MODEL)

    if deployment_model == 'geographies':

        scanner_stacks_map_by_geographies_dict, storage_stacks_map_by_geographies_dict = deployments.build_geography_dict(azure_supported_locations_obj_by_geography_groups_dict, deploy_storage_stack_list)

        print("\nscanner_stacks_map_by_geographies_dict - " + str(scanner_stacks_map_by_geographies_dict) + "\n")
        print("\nstorage_stacks_map_by_geographies_dict - " + str(storage_stacks_map_by_geographies_dict) + "\n")        

        # Scanner and Storage Stack Maps are built. Now, let's deploy.            
        # Deploy FSS Scanner Stacks for the different geographies we have storage accounts
        deployments.deploy_fss_scanner_stack(subscription_id, azure_supported_locations_obj_by_geography_groups_dict, scanner_stacks_map_by_geographies_dict, storage_stacks_map_by_geographies_dict) # TODO: Fix this description. Subscription Id, Existing Scanner stacks so we dont recreate one for the geography, list of geographies we need Scanner stacks in (might overlap with existing), storage accounts that exist without a scanner-storage stack

        # # FSS Storage Stack Deployment
        # deployments.deploy_fss_storage_stack(subscription_id,  deploy_storage_stack_list)

    elif deployment_model == 'one-to-one':
        pass

    elif deployment_model == 'single':

        subscription_id = utils.get_subscription_id()

        deployment_single.deploy_single(subscription_id, azure_supported_locations_obj_by_geography_groups_dict, FSS_SUPPORTED_REGIONS, deploy_storage_stack_list)


if __name__ == "__main__":
    main()
