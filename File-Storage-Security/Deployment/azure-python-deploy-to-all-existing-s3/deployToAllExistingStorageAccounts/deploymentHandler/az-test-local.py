from distutils import dep_util
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
import storage_accounts
import service_principal
import cloudone_fss_api

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
# FSS_SUPPORTED_REGIONS = ["centralus", "eastus", "eastus2", "southcentralus", "westus", "westus2", "centralindia", "eastasia", "japaneast", "koreacentral", "southeastasia", "francecentral", "germanywestcentral", "northeurope", "switzerlandnorth", "uksouth", "westeurope", "uaenorth", "brazilsouth"]

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

    # locations.get_azure_supported_locations_sdk()

    azure_supported_locations_obj_by_geography_groups_dict = locations.get_azure_supported_locations()

    # Get List of Storage Accounts to deploy FSS
    deploy_storage_stack_list = []
    deployment_mode = utils.get_deployment_mode_from_env('DEPLOYMENT_MODE', DEPLOYMENT_MODES, DEFAULT_DEPLOYMENT_MODE)

    if deployment_mode == 'existing':
        deploy_storage_stack_list = storage_accounts.get_storage_accounts(FSS_LOOKUP_TAG)

        if deploy_storage_stack_list:
            deploy_storage_stack_list = utils.apply_exclusions(exclusion_file_name, deploy_storage_stack_list)
            deploy_storage_stack_list = utils.remove_storage_accounts_with_storage_stacks(deploy_storage_stack_list)
        else:
            raise Exception('No Storage Account(s) match the \"' + FSS_LOOKUP_TAG + '\" tag. Exiting ...')
    else:
        # deployment_mode == 'new'
        # # TODO: Build an event listener to trigger deployment based on Storage Account creation events.
        raise Exception('Deploying to new storage account based on an event listener is yet to be built into this tool.')

    # FSS Scanner Stack Deployment
    deployment_model = utils.get_deployment_model_from_env('DEPLOYMENT_MODEL', DEPLOYMENT_MODELS, DEFAULT_DEPLOYMENT_MODEL)

    if deployment_model == 'geographies':

        # Inventory of existing storage accounts
        # unique_storage_account_geographies = geographies.get_geographies_from_storage_accounts(deploy_storage_stack_list, azure_supported_locations_obj_by_geography_groups_dict)

        # Scanner Stack Map
        scanner_stacks_map_by_geographies_dict = geographies.build_geographies_map_dict()        

        # Inventory of existing FSS scanner stacks by Azure location
        existing_scanner_stacks_by_location = cloudone_fss_api.map_scanner_stacks_to_azure_locations()

        print("\nScanner Stack Locations: " + str(existing_scanner_stacks_by_location))

        # Fetching Geography groups for the existing storage stacks, building a map
        
        # for existing_scanner_stack_location in existing_scanner_stacks_by_location:

            # geography = geographies.get_geography_group_from_location(existing_scanner_stack_location, azure_supported_locations_obj_by_geography_groups_dict)

            # if geography not in scanner_stacks_map_by_geographies_dict:
            #     scanner_stacks_map_by_geographies_dict.update({geography: []}) # { "US": [], "Europe" [], ...} only existing scanner stack in the azure location

        # print("\nAll Geos where scanner stack exists: " + str(scanner_stacks_map_by_geographies_dict))

        for existing_scanner_stack_by_location in existing_scanner_stacks_by_location:

            geography = geographies.get_geography_group_from_location(existing_scanner_stack_by_location, azure_supported_locations_obj_by_geography_groups_dict)

            scanner_stacks_map_by_geographies_dict[geography] = existing_scanner_stacks_by_location[existing_scanner_stack_by_location]

        # ----

        # # Building Geos with locations map
        # temp_existing_scanner_stack_location_list = []
        # temp_new_scanner_stack_location_list = []

        # # Cycle through everywhere we need a storage stack deployed for the storage account
        # for storage_account in deploy_storage_stack_list:

        #     # Cycle through all the Azure locations we have scanner stacks
        #     for existing_scanner_stack_location in existing_scanner_stacks_by_location:

        #         # If they correlate, map storage accounts to existing scanner stacks locations
        #         print(str(storage_account["location"]), str(existing_scanner_stack_location))
        #         if storage_account["location"] == existing_scanner_stack_location:

        #             temp_existing_scanner_stack_location_list.append(storage_account)

        #         # No correlation, mark them for new scanner stack deployment
        #         else:
        #             temp_new_scanner_stack_location_list.append(storage_account)

        # for geography in scanner_stacks_map_by_geographies_dict:

        #             # scanner_stacks_map_by_geographies_dict[geography].append({existing_scanner_stack_location: temp_existing_scanner_stack_location_list}) # { "US": [{"eastus": [...]}], "Europe": []}   

        #     scanner_stacks_map_by_geographies_dict[geography].append(temp_existing_scanner_stack_location_list)

        # for storage_account in temp_new_scanner_stack_location_list:

        #     print("\nNew Scanner Stack required: " + str(storage_account["location"]))

        #     geography = geographies.get_geography_group_from_location(storage_account["location"], azure_supported_locations_obj_by_geography_groups_dict)

        #     if geography not in scanner_stacks_map_by_geographies_dict:

        #         print("\nNew Scanner Stack Geography: " + str(geography))

        #         scanner_stacks_map_by_geographies_dict.update({geography: []}) # { "Middle East": [], "Europe" [], ...} new scanner stack geographies mapping
            
        #         print("\nUpdating Scanner Stack Geography: " + str(geography))
        #         scanner_stacks_map_by_geographies_dict[geography].append({storage_account["location"]: temp_existing_scanner_stack_location_list})

        # ----        

        # Storage Stacks Map
        storage_stacks_map_by_geographies_dict = geographies.build_geographies_map_dict()        

        for storage_account in deploy_storage_stack_list:

            for existing_scanner_stack_by_location in existing_scanner_stacks_by_location:

                # if "storageStacks" not in existing_scanner_stacks_by_location[existing_scanner_stack_by_location][0].keys():

                #         existing_scanner_stacks_by_location[existing_scanner_stack_by_location][0]["storageStacks"] = []                

                existing_scanner_stack_geography = geographies.get_geography_group_from_location(existing_scanner_stacks_by_location[existing_scanner_stack_by_location][0]["details"]["region"], azure_supported_locations_obj_by_geography_groups_dict)
                storage_account_geography = geographies.get_geography_group_from_location(storage_account["location"], azure_supported_locations_obj_by_geography_groups_dict)

                if existing_scanner_stack_geography == storage_account_geography:

                    temp_storage_stacks_dict = storage_stacks_map_by_geographies_dict[existing_scanner_stack_geography]                    

                    temp_storage_stacks_dict.append(storage_account)

                    storage_stacks_map_by_geographies_dict[existing_scanner_stack_geography] = temp_storage_stacks_dict

                    print("\nFound a match... " + str(existing_scanner_stack_geography) + " = " + str(storage_account_geography))

                else:
                    print("\nFound a mismatch... " + str(existing_scanner_stack_geography) + " ~ " + str(storage_account_geography))

        print("\nscanner_stacks_map_by_geographies_dict - " + str(scanner_stacks_map_by_geographies_dict) + "\n")
        print("\nstorage_stacks_map_by_geographies_dict - " + str(storage_stacks_map_by_geographies_dict) + "\n")

    # print(str(cloudone_fss_api.get))
    
    # Deploy FSS Scanner Stacks for the different geographies we have storage accounts
    deploy_fss_scanner_stack(subscription_id, scanner_stacks_map_by_geographies_dict, storage_stacks_map_by_geographies_dict) # Subscription Id, Existing Scanner stacks so we dont recreate one for the geography, list of geographies we need Scanner stacks in (might overlap with existing), storage accounts that exist without a scanner-storage stack

    # # FSS Storage Stack Deployment
    # deploy_fss_storage_stack(subscription_id,  deploy_storage_stack_list)

def deploy_fss_scanner_stack(subscription_id, scanner_stacks_map_by_geographies_dict, storage_stacks_map_by_geographies_dict):

    # File Storage Security Scanner Stack deployment templates can be found at https://github.com/trendmicro/cloudone-filestorage-deployment-templates/blob/master/azure/FSS-Scanner-Stack-Template.json

    app_id = str(utils.get_config_from_file("app_id"))
    cloudone_region = str(utils.get_cloudone_region())

    if app_id and cloudone_region:

        print("\n\tDeploying Scanner Stack - " + str(scanner_stacks_map_by_geographies_dict), " \n\n\t+++++ ", str(storage_stacks_map_by_geographies_dict))

        # Starting with the geography-based scanner requirements
        for geography_group in scanner_stacks_map_by_geographies_dict:

            if geography_group not in scanner_stacks_map_by_geographies_dict.keys():
    
                scanner_stack_name = "fss-scanner-" + str(geography_group.lower()) + "-autodeploy"
                resource_group_name = scanner_stack_name + "-rg"

                # Find a recommended Azure location to deploy the FSS Scanner Stack
                azure_recommended_location = locations.get_azure_recommended_location_by_geography_group(geography_group, scanner_stacks_map_by_geographies_dict)

                print("\nCreating a new Scanner Stack in Azure location {azure_recommended_location} - {geography_group}\n".format(azure_recommended_location, geography_group))

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
                    'CloudOneRegion': cloudone_region,
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

            else:
                # A Scanner stack for this storage account location has been identified
                print("\nFound " + str(geography_group) + " - " + str(scanner_stacks_map_by_geographies_dict[geography_group]) + " ...\n")                

                for scanner_stack in scanner_stacks_map_by_geographies_dict[geography_group]:

                    if len(cloudone_fss_api.get_associated_storage_stacks_to_scanner_stack(scanner_stack["stackID"])) <= utils.get_cloudone_max_storage_to_scanner_count():

                        resource_group_name = scanner_stack["name"].lower() + "-rg"

                        # --- Repeat steps TODO: Remove repitition and create a function
                        msg = "\nInitializing the Deployer class with subscription id: {}, resource group: {} ...\n\n"
                        msg = msg.format(subscription_id, resource_group_name)
                        print(msg)

                        service_principal_id = service_principal.query_service_principal(app_id)

                        if not service_principal_id:
                            service_principal_id = utils.azure_cli_run_command('ad sp create --id ' + app_id)
                        print(str(service_principal_id))
                        # rbac.createServicePrincipal()

                        scanner_stack_params = {
                            'FileStorageSecurityServicePrincipalID': service_principal_id,
                            'CloudOneRegion': cloudone_region,
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

def deploy_fss_storage_stack(subscription_id, deploy_storage_stack_list):

    # File Storage Security Storage Stack deployment template can be found at https://github.com/trendmicro/cloudone-filestorage-deployment-templates/blob/master/azure/FSS-Storage-Stack-Template.json

    app_id = str(utils.get_config_from_file("app_id"))
    cloudone_region = str(utils.get_cloudone_region())

    if app_id and cloudone_region:

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
                'CloudOneRegion': cloudone_region,
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

if __name__ == "__main__":
    main()
