import json
import urllib3
http = urllib3.PoolManager()

import utils

def filter_stacks_by_subscription_id(subscription_id, cloudone_fss_stacks_output):

    temp_stacks_output_list = []
    for stack in cloudone_fss_stacks_output["stacks"]:             
        if utils.get_subscription_id_from_resource_group_id(stack["details"]["resourceGroupID"]) != subscription_id:
            temp_stacks_output_list.append(stack)
        
    for stack in temp_stacks_output_list:
        cloudone_fss_stacks_output["stacks"].remove(stack)
    return cloudone_fss_stacks_output

def get_scanner_stacks():
    try:
        region = utils.get_cloudone_region()
        api_key = utils.get_cloudone_api_key()
        subscription_id = utils.get_subscription_id()
        
        if region and api_key and subscription_id:
            cloudone_fss_api_url = "https://filestorage.{}.cloudone.trendmicro.com/api".format(region)

            r = http.request(
                "GET",
                cloudone_fss_api_url + "/stacks?provider=azure&type=scanner",
                headers={
                    "Authorization": "ApiKey " + api_key,
                    "Api-Version": "v1",
                },

            )
            if r.status == 200:
                return json.loads(r.data)
            else:
                raise Exception("HTTP Request failure (code: " + str(r.status) + "). Check cloudone section in the config.json file or environment variables [\"CLOUDONE_API_KEY\", \"CLOUDONE_REGION\"] for valid input.")
    except:
        raise Exception("HTTP Request failure (code: " + str(r.status) + "). Check the logs for more information.")

def get_storage_stacks():
    try:    
        region = utils.get_cloudone_region()
        api_key = utils.get_cloudone_api_key()
        subscription_id = utils.get_subscription_id()

        if region and api_key and subscription_id:
            cloudone_fss_api_url = "https://filestorage.{}.cloudone.trendmicro.com/api".format(region)

            r = http.request(
                "GET",
                cloudone_fss_api_url + "/stacks?provider=azure&type=storage",
                headers={
                    "Authorization": "ApiKey " + api_key,
                    "Api-Version": "v1",
                },

            )
            if r.status == 200:
                return json.loads(r.data)
            else:
                raise Exception("HTTP Request failure (code: " + str(r.status) + "). Check cloudone section in the config.json file or environment variables [\"CLOUDONE_API_KEY\", \"CLOUDONE_REGION\"] for valid input.")
    except:
        raise Exception("HTTP Request failure (code: " + str(r.status) + "). Check the logs for more information.")

def map_scanner_stacks_to_azure_locations():

    existing_scanner_stacks_dict = get_scanner_stacks()

    if existing_scanner_stacks_dict:
        locationsDict = {}
        for scanner_stack in existing_scanner_stacks_dict["stacks"]:

            if scanner_stack["status"] == "ok":

                if scanner_stack["details"]["region"] not in locationsDict:
                    locationsDict.update({scanner_stack["details"]["region"]: []})
                
                locationsDict[scanner_stack["details"]["region"]].append(scanner_stack)

        return locationsDict
    return None

def get_associated_storage_stacks_to_scanner_stack(scanner_stack_uuid):
    try:    
        region = utils.get_cloudone_region()
        api_key = utils.get_cloudone_api_key()
        
        if region and api_key:
            cloudone_fss_api_url = "https://filestorage.{}.cloudone.trendmicro.com/api".format(region)

            r = http.request(
                "GET",
                cloudone_fss_api_url + "/stacks?provider=azure&type=storage&scannerStack=" + scanner_stack_uuid,
                headers={
                    "Authorization": "ApiKey " + api_key,
                    "Api-Version": "v1",
                },

            )
            if r.status == 200:
                return json.loads(r.data)
            else:
                raise Exception("HTTP Request failure (code: " + str(r.status) + "). Check cloudone section in the config.json file or environment variables [\"CLOUDONE_API_KEY\", \"CLOUDONE_REGION\"] for valid input.")
    except:
        raise Exception("HTTP Request failure (code: " + str(r.status) + "). Check the logs for more information.")