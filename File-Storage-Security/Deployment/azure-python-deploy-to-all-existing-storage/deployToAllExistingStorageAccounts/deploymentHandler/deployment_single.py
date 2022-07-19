import deployments
import cloudone_fss_api
import utils

def deploy_single(subscription_id, azure_supported_locations_obj_by_geography_groups_dict, fss_supported_regions_list, deploy_storage_stack_list):

    # Get All Scanner Stacks in this Azure Subscription
    # scanner_stacks_list = cloudone_fss_api.filter_stacks_by_subscription_id(subscription_id, cloudone_fss_api.get_scanner_stacks())    
    scanner_stacks_list = cloudone_fss_api.get_scanner_stacks()    

    temp_storage_account_dict = {}
    for storage_account in deploy_storage_stack_list:

        if storage_account["location"] not in temp_storage_account_dict:
            temp_storage_account_dict.update({storage_account["location"]: 1})
        else:            
            temp_storage_account_dict[storage_account["location"]] = temp_storage_account_dict[storage_account["location"]] + 1

    values_list = list(temp_storage_account_dict.values())
    max_storage_account_count = max(values_list)

    scanner_stack_identity_principal_id = scanner_stack_queue_namespace = None

    # If no Scanner Stack(s) exist in this Azure subscription
    if not len(scanner_stacks_list["stacks"]):

        # Deploy One Scanner Stack
        scanner_stack_deployment_outputs = deployments.deploy_fss_scanner_stack(subscription_id,  azure_supported_locations_obj_by_geography_groups_dict,  azure_location=utils.get_dict_key(temp_storage_account_dict, max_storage_account_count), fss_supported_regions_list=fss_supported_regions_list)
        
        if scanner_stack_deployment_outputs:            

            scanner_stack_identity_principal_id = scanner_stack_deployment_outputs["scannerIdentityPrincipalID"]["value"]
            scanner_stack_queue_namespace = scanner_stack_deployment_outputs["scannerQueueNamespace"]["value"]

        else:
            raise Exception("Deployment Failed. The deployment did not create any output(s). Check deployment status for more details on how to troubleshoot this issue.")

    # TODO: Fetch Scanner Stack Identity Principal ID from the existing Scanner Stack Deployment Template Outputs
    else:        

        scanner_stack_identity_principal_id = scanner_stacks_list["stacks"][0]["details"]["scannerIdentityPrincipalID"]
        scanner_stack_queue_namespace = scanner_stacks_list["stacks"][0]["details"]["scannerQueueNamespace"]

    if scanner_stack_identity_principal_id and scanner_stack_queue_namespace:

        print("scanner_stack_identity_principal_id - " + str(scanner_stack_identity_principal_id))
        print("scanner_stack_queue_namespace - " + str(scanner_stack_queue_namespace))

        for storage_account in deploy_storage_stack_list:        

            deployments.deploy_fss_storage_stack(subscription_id, storage_account, scanner_stack_identity_principal_id, scanner_stack_queue_namespace)