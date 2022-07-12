import json
import urllib3
http = urllib3.PoolManager()

import utils

def get_scanner_stacks():

    cloudone_fss_api_url = "https://filestorage.{region}.cloudone.trendmicro.com/api".format(region=str(utils.get_cloudone_region()))

    r = http.request(
        "GET",
        cloudone_fss_api_url + "/stacks?provider=azure&type=scanner",
        headers={
            "Authorization": "ApiKey " + str(utils.get_cloudone_api_key()),
            "Api-Version": "v1",
        },

    )

    return json.loads(r.data)

def get_storage_stacks():

    cloudone_fss_api_url = "https://filestorage.{region}.cloudone.trendmicro.com/api".format(region=str(utils.get_cloudone_region()))

    r = http.request(
        "GET",
        cloudone_fss_api_url + "/stacks?provider=azure&type=storage",
        headers={
            "Authorization": "ApiKey " + str(utils.get_cloudone_api_key()),
            "Api-Version": "v1",
        },

    )

    return json.loads(r.data)

def map_scanner_stacks_to_azure_locations():

    existing_scanner_stacks_dict = get_scanner_stacks()

    locationsDict = {}
    for scanner_stack in existing_scanner_stacks_dict["stacks"]:

        if scanner_stack["status"] == "ok":

            if scanner_stack["details"]["region"] not in locationsDict:
                locationsDict.update({scanner_stack["details"]["region"]: []})
            
            locationsDict[scanner_stack["details"]["region"]].append(scanner_stack)

    return locationsDict

def get_associated_storage_stacks_to_scanner_stack(scanner_stack_uuid):

    cloudone_fss_api_url = "https://filestorage.{region}.cloudone.trendmicro.com/api".format(region=str(utils.get_cloudone_region()))

    r = http.request(
        "GET",
        cloudone_fss_api_url + "/stacks?provider=azure&type=storage&scannerStack=" + scanner_stack_uuid,
        headers={
            "Authorization": "ApiKey " + str(utils.get_cloudone_api_key()),
            "Api-Version": "v1",
        },

    )

    return json.loads(r.data)