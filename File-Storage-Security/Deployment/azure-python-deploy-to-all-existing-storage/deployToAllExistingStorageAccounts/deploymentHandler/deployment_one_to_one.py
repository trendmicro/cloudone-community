import deployments
import cloudone_fss_api
import utils

def deploy_one_to_one(subscription_id, azure_supported_locations_obj_by_geography_groups_dict, fss_supported_regions_list, azure_storage_account_list):

    for storage_account in azure_storage_account_list:

        cloudone_scanner_stack_id = scanner_stack_identity_principal_id = scanner_stack_queue_namespace = None

        # Deploy One Scanner Stack
        scanner_stack_deployment_outputs = deployments.deploy_fss_scanner_stack(
            subscription_id, 
            azure_supported_locations_obj_by_geography_groups_dict, 
            storage_account["location"], 
            fss_supported_regions_list, 
            azure_storage_account_name = storage_account["name"], 
            scanner_stack_name = "fss-scanner-stack-" + utils.trim_location_name(storage_account["location"]) + "-" + utils.trim_resource_name(storage_account["name"], 10, 10) + "-autodeploy"
        )
        
        if scanner_stack_deployment_outputs:            

            cloudone_scanner_stack_id = scanner_stack_deployment_outputs["cloudOneScannerStackId"]
            scanner_stack_identity_principal_id = scanner_stack_deployment_outputs["scannerIdentityPrincipalID"]["value"]
            scanner_stack_queue_namespace = scanner_stack_deployment_outputs["scannerQueueNamespace"]["value"]

        else:
            # TODO: In these scenarios, use try...except to throw exceptions
            raise Exception("Deployment Failed. The deployment did not create any output(s). Check deployment status for more details on how to troubleshoot this issue.")

        # Deploy One Storage Stack, Associate to previously created One Scanner Stack
        if cloudone_scanner_stack_id and scanner_stack_identity_principal_id and scanner_stack_queue_namespace:

            print("cloudone_scanner_stack_id - " + str(cloudone_scanner_stack_id))
            print("scanner_stack_identity_principal_id - " + str(scanner_stack_identity_principal_id))
            print("scanner_stack_queue_namespace - " + str(scanner_stack_queue_namespace))      

            storage_stack_deployment_outputs = deployments.deploy_fss_storage_stack(
                subscription_id, 
                storage_account, 
                cloudone_scanner_stack_id, 
                scanner_stack_identity_principal_id, 
                scanner_stack_queue_namespace
            )

            if storage_stack_deployment_outputs:    

                print(str(storage_stack_deployment_outputs))        

                # cloudone_scanner_stack_id = storage_stack_deployment_outputs["cloudOneScannerStackId"]

            else:
                raise Exception("Deployment Failed. The deployment did not create any output(s). Check deployment status for more details on how to troubleshoot this issue.")