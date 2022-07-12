import utils
import logging

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