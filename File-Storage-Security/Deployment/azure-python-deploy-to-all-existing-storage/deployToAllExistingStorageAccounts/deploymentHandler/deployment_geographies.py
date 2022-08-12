import logging
import time

import deployments
import locations
import geographies
import cloudone_fss_api
import utils

def deploy_geographically(subscription_id, azure_supported_locations_obj_by_geography_groups_dict, fss_supported_regions_list, azure_storage_account_list):    

    # Scanner Stack Map
    scanner_stacks_map_by_geographies_dict = geographies.build_geographies_map_dict()
    scanner_stack_names_list = []

    # Storage Stacks Map
    storage_stacks_map_by_geographies_dict = geographies.build_geographies_map_dict()      

    # Populate the Scanner stack map by geographies that are registered within this subscription
    # Inventory of existing FSS scanner stacks in this subscription by Azure location
    existing_scanner_stacks_by_location = cloudone_fss_api.map_scanner_stacks_to_azure_locations()    

    # If scanner stacks exist, add them to the Scanner Stack Map
    if existing_scanner_stacks_by_location:

        # Existing scanner stack location by location
        for existing_scanner_stack_by_location in existing_scanner_stacks_by_location:

            # Get scanner stack geography
            scanner_stack_geography = geographies.get_geography_group_from_location(existing_scanner_stack_by_location, azure_supported_locations_obj_by_geography_groups_dict)

            # Build a geographical map of existing scanner stacks
            scanner_stacks_map_by_geographies_dict[scanner_stack_geography] = existing_scanner_stacks_by_location[existing_scanner_stack_by_location]

            # scanner_stack_names_list[scanner_stack_geography] = 
            for scanner_stack  in existing_scanner_stacks_by_location[existing_scanner_stack_by_location]:
                scanner_stack_names_list.append(scanner_stack["name"])

    # Remove any scanner stacks that violate the 50:1 Storage to Scanner stack ratio in this run
    max_storage_to_scanner_count = utils.get_config_from_file('cloudone.max_storage_stack_per_scanner_stack') - len(azure_storage_account_list)
    scanner_stacks_map_by_geographies_dict = utils.remove_scanner_stacks_exceed_max_storage_account_count(scanner_stacks_map_by_geographies_dict, max_storage_to_scanner_count)

    # If storage accounts exist
    if azure_storage_account_list:

        # Existing storage account
        for storage_account in azure_storage_account_list:

            # Get storage stack geography
            storage_stack_geography = geographies.get_geography_group_from_location(storage_account["location"], azure_supported_locations_obj_by_geography_groups_dict)

            temp_storage_stacks_by_geographies_list = storage_stacks_map_by_geographies_dict[storage_stack_geography]

            temp_storage_stacks_by_geographies_list.append(storage_account)
            storage_stacks_map_by_geographies_dict[storage_stack_geography] = temp_storage_stacks_by_geographies_list
    
    for storage_account_geography in storage_stacks_map_by_geographies_dict:

        cloudone_scanner_stack_id = scanner_stack_identity_principal_id = scanner_stack_queue_namespace = None

        for scanner_stack_geography in scanner_stacks_map_by_geographies_dict:

            if storage_stacks_map_by_geographies_dict[storage_account_geography]:
                
                if storage_account_geography == scanner_stack_geography: 

                    # If a scanner stack exists, then map to storage stack in the geography
                    if scanner_stacks_map_by_geographies_dict[scanner_stack_geography]:

                        cloudone_scanner_stack_id = scanner_stacks_map_by_geographies_dict[scanner_stack_geography][0]["stackID"]
                        scanner_stack_identity_principal_id = scanner_stacks_map_by_geographies_dict[scanner_stack_geography][0]["details"]["scannerIdentityPrincipalID"]
                        scanner_stack_queue_namespace = scanner_stacks_map_by_geographies_dict[scanner_stack_geography][0]["details"]["scannerQueueNamespace"]

                        for storage_account in storage_stacks_map_by_geographies_dict[storage_account_geography]:

                            # Deploy Storage Stack for the storage_account, Associate to previously identified existing scanner stack
                            if cloudone_scanner_stack_id and scanner_stack_identity_principal_id and scanner_stack_queue_namespace:     

                                # storage_stack_deployment_outputs = 
                                deployments.deploy_fss_storage_stack(
                                    subscription_id = subscription_id, 
                                    storage_account = storage_account, 
                                    cloudone_scanner_stack_id = cloudone_scanner_stack_id, 
                                    scanner_identity_principal_id = scanner_stack_identity_principal_id, 
                                    scanner_queue_namespace = scanner_stack_queue_namespace
                                )

                                # if storage_stack_deployment_outputs:
                                #     print("\tstorage_stack_deployment_outputs - " + str(storage_stack_deployment_outputs))

                                # Update storageStackCount
                                for scanner_stack in scanner_stacks_map_by_geographies_dict[scanner_stack_geography]:

                                    print(str(scanner_stack))

                                    if scanner_stack["stackID"] == cloudone_scanner_stack_id:
                                        scanner_stack.update({"storageStackCount": scanner_stack["storageStackCount"] + 1})
                                        print("Storage Stack Count - " + str(scanner_stack["storageStackCount"]))

                            else:
                                logging.error("Deployment Failed. The deployment did not create any output(s). Check deployment status for more details on how to troubleshoot this issue.")
                                raise Exception("Deployment Failed. The deployment did not create any output(s). Check deployment status for more details on how to troubleshoot this issue.")

                    # If no scanner stacks exist, deploy one
                    else:

                        azure_recommended_location = locations.get_azure_recommended_location_by_geography_group(storage_account_geography, azure_supported_locations_obj_by_geography_groups_dict, fss_supported_regions_list)

                        # Deploy One Scanner Stack
                        scanner_stack_name_prefix = "fss-scanner-" + storage_account_geography + "-" + utils.trim_location_name(azure_recommended_location)
                        print("Deploying a Scanner Stack " + scanner_stack_name_prefix + " in " + str(azure_recommended_location) + "...")
                        scanner_stack_deployment_outputs = deployments.deploy_fss_scanner_stack(
                            subscription_id = subscription_id, 
                            azure_supported_locations_obj_by_geography_groups_dict = azure_supported_locations_obj_by_geography_groups_dict, 
                            azure_location = azure_recommended_location, 
                            fss_supported_regions_list = fss_supported_regions_list,
                            deployment_model = "geo", 
                            scanner_stack_names_list = scanner_stack_names_list,
                            azure_storage_account_name = None,
                            scanner_stack_name_prefix = scanner_stack_name_prefix
                        )

                        if scanner_stack_deployment_outputs:

                            cloudone_scanner_stack_id = scanner_stack_deployment_outputs["cloudOneScannerStackId"]
                            cloudone_scanner_stack_name = str(scanner_stack_deployment_outputs["scannerStackResourceGroupID"]["value"]).split("/")[-1]
                            cloudone_scanner_stack_tenant_id = scanner_stack_deployment_outputs["tenantID"]["value"]
                            cloudone_scanner_stack_resource_group_id = scanner_stack_deployment_outputs["scannerStackResourceGroupID"]["value"]
                            scanner_stack_queue_namespace = scanner_stack_deployment_outputs["scannerQueueNamespace"]["value"]
                            cloudone_scanner_stack_region = scanner_stack_deployment_outputs["cloudOneRegion"]["value"]
                            scanner_stack_identity_principal_id = scanner_stack_deployment_outputs["scannerIdentityPrincipalID"]["value"]

                            temp_stack_output_skeleton = {
                                "stackID": cloudone_scanner_stack_id,
                                "name": cloudone_scanner_stack_name,
                                "details": {
                                    "tenantID": cloudone_scanner_stack_tenant_id,
                                    "resourceGroupID": cloudone_scanner_stack_resource_group_id,
                                    "scannerQueueNamespace": scanner_stack_queue_namespace,
                                    "region": cloudone_scanner_stack_region,
                                    "scannerIdentityPrincipalID": scanner_stack_identity_principal_id
                                },
                                "provider": "azure",
                                "type": "scanner",
                                "storageStackCount": 0
                            }

                            # temp_scanner_stacks_by_geography_list = None
                            if scanner_stacks_map_by_geographies_dict[scanner_stack_geography]:                                
                                scanner_stacks_map_by_geographies_dict[scanner_stack_geography].append(temp_stack_output_skeleton)
                            else:
                                scanner_stacks_map_by_geographies_dict[scanner_stack_geography].append(temp_stack_output_skeleton)

                        else:
                            logging.error("Deployment Failed. The deployment did not create any output(s). Check deployment status for more details on how to troubleshoot this issue.")
                            raise Exception("Deployment Failed. The deployment did not create any output(s). Check deployment status for more details on how to troubleshoot this issue.")

                        print("Scanner Stacks 1: " + str(scanner_stacks_map_by_geographies_dict))

                        # Deploy Storage Stack for the storage_account, Associate to previously identified existing scanner stack
                        if cloudone_scanner_stack_id and scanner_stack_identity_principal_id and scanner_stack_queue_namespace:

                            for storage_account in storage_stacks_map_by_geographies_dict[storage_account_geography]:    

                                # storage_stack_deployment_outputs = 
                                deployments.deploy_fss_storage_stack(
                                    subscription_id = subscription_id, 
                                    storage_account = storage_account, 
                                    cloudone_scanner_stack_id = cloudone_scanner_stack_id, 
                                    scanner_identity_principal_id = scanner_stack_identity_principal_id, 
                                    scanner_queue_namespace = scanner_stack_queue_namespace
                                )

                                # if storage_stack_deployment_outputs:
                                #     print(str(storage_stack_deployment_outputs))

                                # Update storageStackCount
                                if scanner_stacks_map_by_geographies_dict[scanner_stack_geography]:

                                    for scanner_stack_geography_dict in scanner_stacks_map_by_geographies_dict[scanner_stack_geography]:

                                        if scanner_stack_geography_dict["stackID"] == cloudone_scanner_stack_id:

                                            scanner_stack_geography_dict["storageStackCount"] += 1

                        else:
                            logging.error("Deployment Failed. The deployment did not create any output(s). Check deployment status for more details on how to troubleshoot this issue.")
                            raise Exception("Deployment Failed. The deployment did not create any output(s). Check deployment status for more details on how to troubleshoot this issue.")

                else:
                    logging.info("Found a geography mismatch... " + str(scanner_stack_geography) + " ~ " + str(storage_account_geography) + ". Retrying...")
            else:
                    logging.info("Skipping '" + str(scanner_stack_geography) + "' geography as no new storage stacks are needed in this region... ")