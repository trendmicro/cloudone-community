import utils
import locations
import geographies
import service_principal
import cloudone_fss_api

from Deployer import Deployer

def deploy_fss_scanner_stack(subscription_id, azure_supported_locations_obj_by_geography_groups_dict, azure_location, fss_supported_regions_list, azure_storage_account_name=None, scanner_stack_name=None, resource_group_name=None, geography_group_name=None):

    # File Storage Security Scanner Stack deployment templates can be found at https://github.com/trendmicro/cloudone-filestorage-deployment-templates/blob/master/azure/FSS-Scanner-Stack-Template.json or in the ./templates directory

    app_id = str(utils.get_config_from_file("app_id"))
    cloudone_region = str(utils.get_cloudone_region())

    if app_id and cloudone_region:

        # print("\n\tDeploying Scanner Stack - " + str(scanner_stacks_map_by_geographies_dict), " \n\t+++++ Storage Stack - ", str(storage_stacks_map_by_geographies_dict))

        # TODO: Needs better testing. Working on single deployment right now. Needs geographies or one-to-one deployment models.
        if azure_location not in fss_supported_regions_list:

            print("Azure location (" + azure_location + ") is not part of the FSS supported regions. Choosing the next Azure recommended location in the same geography.")
            geography_group_name = geographies.get_geography_group_from_location(azure_location, azure_supported_locations_obj_by_geography_groups_dict)

            azure_location = locations.get_azure_recommended_location_by_geography_group(geography_group_name, azure_supported_locations_obj_by_geography_groups_dict, fss_supported_regions_list)
            print("New Azure location: " + azure_location)

            scanner_stack_name = "fss-scanner-stack-" + utils.trim_location_name(azure_location) + "-" + utils.trim_resource_name(azure_storage_account_name, 10, 10) + "-autodeploy"

        if not geography_group_name:
            geography_group_name = geographies.get_geography_group_from_location(azure_location, azure_supported_locations_obj_by_geography_groups_dict)

        if not scanner_stack_name:            
            scanner_stack_name = "fss-scanner-stack-" + geography_group_name + "-" + azure_location + "-autodeploy"
        if not resource_group_name:
            resource_group_name = scanner_stack_name + "-rg"

        print("\nInitializing the Deployer class with subscription id: {}, resource group: {} ...\n".format(subscription_id, resource_group_name))

        service_principal_id = service_principal.get_service_principal_id(app_id)

        scanner_stack_params = {
            'FileStorageSecurityServicePrincipalID': service_principal_id,
            'CloudOneRegion': cloudone_region,
            'StackPackageLocation': 'https://file-storage-security.s3.amazonaws.com',
            'Version': 'latest',
            'SharedAccessSignature': ''
        }

        print("scanner_stack_params - " + str(scanner_stack_params))

        # Initialize the deployer class
        deployer = Deployer(subscription_id, resource_group_name)

        # Deploy the template
        print("\nBeginning the deployment...\n")
        
        deployment_outputs = deployer.deploy(azure_location, "scanner", scanner_stack_params)

        cloudone_scanner_stack_id = cloudone_fss_api.register_scanner_stack_with_cloudone(deployment_outputs["scannerStackResourceGroupID"]["value"], deployment_outputs["tenantID"]["value"])
        deployment_outputs.update({'cloudOneScannerStackId': cloudone_scanner_stack_id})

        print("\nDone deploying!!\n")

        return deployment_outputs

def deploy_fss_storage_stack(subscription_id, storage_account, cloudone_scanner_stack_id, scanner_identity_principal_id, scanner_queue_namespace, storage_stack_name=None, resource_group_name=None):

    # File Storage Security Storage Stack deployment template can be found at https://github.com/trendmicro/cloudone-filestorage-deployment-templates/blob/master/azure/FSS-Storage-Stack-Template.json or in the ./templates directory

    app_id = str(utils.get_config_from_file("app_id"))
    cloudone_region = str(utils.get_cloudone_region())

    if not storage_stack_name:
        storage_stack_name = "fss-storage-stack-" + utils.trim_location_name(storage_account["location"]) + "-" + utils.trim_resource_name(storage_account["name"], 10, 10) +  "-autodeploy"

    if not resource_group_name:
        resource_group_name = storage_stack_name + "-rg"

    # resource_group_name = resource_groups.create_resource_group(subscription_id, resource_group_name, storage_account["location"])

    print(storage_stack_name, str(storage_account), resource_group_name)

    print("\nInitializing the Deployer class with subscription id: {}, resource group: {}...\n".format(subscription_id, resource_group_name))

    service_principal_id = service_principal.query_service_principal(app_id)

    if not service_principal_id:
        service_principal_id = utils.azure_cli_run_command('ad sp create --id ' + app_id)
    print(str(service_principal_id))
    # rbac.createServicePrincipal()

    storage_stack_params = {
        'FileStorageSecurityServicePrincipalID': service_principal_id,
        'CloudOneRegion': cloudone_region,
        'ScannerIdentityPrincipalID': scanner_identity_principal_id,
        'ScannerQueueNamespace': scanner_queue_namespace,
        'BlobStorageAccountResourceID': storage_account["id"],
        'BlobSystemTopicExist': 'No',
        'BlobSystemTopicName': 'BlobEventTopic-' + utils.trim_resource_name(storage_account["name"], 40, 40),
        'UpdateScanResultToBlobMetadata': 'Yes',
        'ReportObjectKey': 'No',
        'StackPackageLocation': 'https://file-storage-security.s3.amazonaws.com',
        'Version': 'latest',
        'SharedAccessSignature': ''
    }

    # Initialize the deployer class
    deployer = Deployer(subscription_id, resource_group_name)

    print("\nBeginning the deployment... \n")
    # Deploy the template
    deployment_outputs = deployer.deploy(storage_account["location"], "storage", storage_stack_params)

    cloudone_fss_api.register_storage_stack_with_cloudone(cloudone_scanner_stack_id, deployment_outputs["storageStackResourceGroupID"]["value"], deployment_outputs["tenantID"]["value"])

    print("\nDone deploying!!\n")

    return deployment_outputs

# def deploy_fss_scanner_stack(subscription_id, azure_supported_locations_obj_by_geography_groups_dict, scanner_stacks_map_by_geographies_dict, storage_stacks_map_by_geographies_dict):

#     # File Storage Security Scanner Stack deployment templates can be found at https://github.com/trendmicro/cloudone-filestorage-deployment-templates/blob/master/azure/FSS-Scanner-Stack-Template.json

#     app_id = str(utils.get_config_from_file("app_id"))
#     cloudone_region = str(utils.get_cloudone_region())

#     if app_id and cloudone_region:

#         print("\n\tDeploying Scanner Stack - " + str(scanner_stacks_map_by_geographies_dict), " \n\t+++++ Storage Stack - ", str(storage_stacks_map_by_geographies_dict))

#         # Starting with the geography-based scanner requirements
#         for geography_group in scanner_stacks_map_by_geographies_dict:

#             print(str(geography_group), str(scanner_stacks_map_by_geographies_dict), str(geography_group in scanner_stacks_map_by_geographies_dict.keys()))

#             if geography_group not in scanner_stacks_map_by_geographies_dict.keys():
    
#                 scanner_stack_name = "fss-scanner-stack-" + str(geography_group.lower()) + "-autodeploy"
#                 resource_group_name = scanner_stack_name + "-rg"

#                 # Find a recommended Azure location to deploy the FSS Scanner Stack                
#                 azure_recommended_location = locations.get_azure_recommended_location_by_geography_group(geography_group, azure_supported_locations_obj_by_geography_groups_dict) # 

#                 print("\nCreating a new Scanner Stack in Azure location {} - {}\n".format(azure_recommended_location, geography_group))

#                 # resource_group_name = resource_groups.create_resource_group(subscription_id, resource_group_name, azure_recommended_location)

#                 print("\nInitializing the Deployer class with subscription id: {}, resource group: {} ...\n".format(subscription_id, resource_group_name))

#                 service_principal_id = service_principal.query_service_principal(app_id)

#                 if not service_principal_id:
#                     service_principal_id = utils.azure_cli_run_command('ad sp create --id ' + app_id)                
#                 # rbac.createServicePrincipal()

#                 scanner_stack_params = {
#                     'FileStorageSecurityServicePrincipalID': service_principal_id,
#                     'CloudOneRegion': cloudone_region,
#                     'StackPackageLocation': 'https://file-storage-security.s3.amazonaws.com',
#                     'Version': 'latest',
#                     'SharedAccessSignature': ''
#                 }

#                 print("scanner_stack_params - " + str(scanner_stack_params))

#                 # Initialize the deployer class
#                 deployer = Deployer(subscription_id, resource_group_name)

#                 print("Beginning the deployment...")
#                 # Deploy the template
#                 deployment = deployer.deploy(azure_recommended_location, "scanner", scanner_stack_params)

#                 print("Done deploying!!\n")

#             else:
#                 # A Scanner stack for this storage account location has been identified
#                 print("Found " + str(geography_group) + " - " + str(scanner_stacks_map_by_geographies_dict[geography_group]) + " ...")                

#                 for scanner_stack in scanner_stacks_map_by_geographies_dict[geography_group]:

#                     if len(cloudone_fss_api.get_associated_storage_stacks_to_scanner_stack(scanner_stack["stackID"])) <= utils.get_cloudone_max_storage_to_scanner_count():

#                         resource_group_name = scanner_stack["name"].lower() + "-rg"

#                         azure_recommended_location = scanner_stack["details"]["region"]

#                         print("\nAdding to an existing Scanner Stack in Azure location {} - {}\n".format(azure_recommended_location, geography_group))

#                         # --- Repeat steps TODO: Remove repitition and create a function
#                         print("\nInitializing the Deployer class with subscription id: {}, resource group: {} ...\n".format(subscription_id, resource_group_name))

#                         service_principal_id = service_principal.query_service_principal(app_id)

#                         if not service_principal_id:
#                             service_principal_id = utils.azure_cli_run_command('ad sp create --id ' + app_id)                        
#                         # rbac.createServicePrincipal()

#                         scanner_stack_params = {
#                             'FileStorageSecurityServicePrincipalID': service_principal_id,
#                             'CloudOneRegion': cloudone_region,
#                             'StackPackageLocation': 'https://file-storage-security.s3.amazonaws.com',
#                             'Version': 'latest',
#                             'SharedAccessSignature': ''
#                         }

#                         # Initialize the deployer class
#                         deployer = Deployer(subscription_id, resource_group_name)

#                         print("Beginning the deployment...")
#                         # Deploy the template
#                         deployment = deployer.deploy(azure_recommended_location, "scanner", scanner_stack_params)

#                         print("Done deploying!!\n")

# def deploy_fss_storage_stack(subscription_id, azure_storage_account_list):

    # # File Storage Security Storage Stack deployment template can be found at https://github.com/trendmicro/cloudone-filestorage-deployment-templates/blob/master/azure/FSS-Storage-Stack-Template.json

    # app_id = str(utils.get_config_from_file("app_id"))
    # cloudone_region = str(utils.get_cloudone_region())

    # if app_id and cloudone_region:

    #     for storage_account in azure_storage_account_list:

    #         storage_stack_name = "fss-storage-stack-" + str(storage_account["name"]) + str(storage_account["location"]) + "-autodeploy"
    #         resource_group_name = storage_stack_name + "-rg"

    #         # resource_group_name = resource_groups.create_resource_group(subscription_id, resource_group_name, storage_account["location"])

    #         print(storage_stack_name, str(storage_account), resource_group_name)

    #         print("\nInitializing the Deployer class with subscription id: {}, resource group: {}...\n".format(subscription_id, resource_group_name))

    #         service_principal_id = service_principal.query_service_principal(app_id)

    #         if not service_principal_id:
    #             service_principal_id = utils.azure_cli_run_command('ad sp create --id ' + app_id)
    #         print(str(service_principal_id))
    #         # rbac.createServicePrincipal()

    #         storage_stack_params = {
    #             'FileStorageSecurityServicePrincipalID': service_principal_id,
    #             'CloudOneRegion': cloudone_region,
    #             'ScannerIdentityPrincipalID': '',
    #             'ScannerQueueNamespace': '',
    #             'BlobStorageAccountResourceID': '',
    #             'BlobSystemTopicExist': 'No',
    #             'BlobSystemTopicName': 'BlobEventTopic',
    #             'UpdateScanResultToBlobMetadata': 'Yes',
    #             'ReportObjectKey': 'No',
    #             'StackPackageLocation': 'https://file-storage-security.s3.amazonaws.com',
    #             'Version': 'latest',
    #             'SharedAccessSignature': ''
    #         }

    #         # Initialize the deployer class
    #         deployer = Deployer(subscription_id, resource_group_name)

    #         print("Beginning the deployment... \n")
    #         # Deploy the template
    #         deployment = deployer.deploy(storage_account["location"], "storage", storage_stack_params)

    #         print("Done deploying!!\n")

def build_geography_dict(azure_supported_locations_obj_by_geography_groups_dict, azure_storage_account_list):
    # Inventory of existing storage accounts
    # unique_storage_account_geographies = geographies.get_geographies_from_storage_accounts(azure_storage_account_list, azure_supported_locations_obj_by_geography_groups_dict)

    # Scanner Stack Map
    scanner_stacks_map_by_geographies_dict = geographies.build_geographies_map_dict()  

    # Storage Stacks Map
    storage_stacks_map_by_geographies_dict = geographies.build_geographies_map_dict()      

    # Populate the Scanner stack map by geographies
    # Inventory of existing FSS scanner stacks by Azure location
    existing_scanner_stacks_by_location = cloudone_fss_api.map_scanner_stacks_to_azure_locations()        

    if existing_scanner_stacks_by_location:

        print("\nScanner Stack Locations: " + str(existing_scanner_stacks_by_location))

        for existing_scanner_stack_by_location in existing_scanner_stacks_by_location:

            scanner_stack_geography = geographies.get_geography_group_from_location(existing_scanner_stack_by_location, azure_supported_locations_obj_by_geography_groups_dict)

            scanner_stacks_map_by_geographies_dict[scanner_stack_geography] = existing_scanner_stacks_by_location[existing_scanner_stack_by_location]

    # Populate the Storage stack map by geographies
    for storage_account in azure_storage_account_list:

        if existing_scanner_stacks_by_location:

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
        else:
            storage_account_geography = geographies.get_geography_group_from_location(storage_account["location"], azure_supported_locations_obj_by_geography_groups_dict)

            temp_storage_stacks_dict = storage_stacks_map_by_geographies_dict[storage_account_geography]                    

            temp_storage_stacks_dict.append(storage_account)

            storage_stacks_map_by_geographies_dict[storage_account_geography] = temp_storage_stacks_dict


    return scanner_stacks_map_by_geographies_dict, storage_stacks_map_by_geographies_dict