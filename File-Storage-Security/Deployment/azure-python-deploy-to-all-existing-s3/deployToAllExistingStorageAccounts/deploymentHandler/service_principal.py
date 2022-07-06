import utils
import os

def query_service_principal(appId):
    sp_list = utils.azure_cli_run_command('ad sp list')
    for sp_item in sp_list:
        if sp_item["appId"] == appId:
            print(str(sp_item["id"]))
            return sp_item["id"]
    return None