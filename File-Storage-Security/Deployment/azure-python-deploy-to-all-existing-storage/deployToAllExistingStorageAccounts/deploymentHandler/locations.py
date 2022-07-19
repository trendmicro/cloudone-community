from azure.mgmt.subscription import SubscriptionClient
from azure.identity import DefaultAzureCredential
from azure.common.credentials import ServicePrincipalCredentials
from azure.identity import ClientSecretCredential

import os
import utils
import random

# get_azure_recommended_location_by_geography_group - Pick one Azure recommended location in the geography location. 
def get_azure_recommended_location_by_geography_group(az_geography_group, az_geography_groups_list):
    for az_geography_group_item in az_geography_groups_list:
        if az_geography_group == az_geography_group_item:

            print("Print List: " + str(az_geography_groups_list))

            print("Index: " + str(az_geography_groups_list.index(az_geography_group)))
            print("Value: " + str(az_geography_groups_list[az_geography_groups_list.index(az_geography_group)]))
            print("Value 2: " + str(az_geography_groups_list[az_geography_groups_list.index(az_geography_group)]))
            print("Length: " + str(len(az_geography_groups_list[az_geography_groups_list[az_geography_groups_list.index(az_geography_group)]])))
            print("Random Index: " + str(random.randint(0, len(az_geography_groups_list[az_geography_groups_list.index(az_geography_group)])-1)))
            print("Random Index Value: " + str(az_geography_groups_list[az_geography_groups_list.index(az_geography_group)][random.randint(0, len(az_geography_groups_list[az_geography_groups_list.index(az_geography_group)])-1)]))
            print("Random Index Value Name: " + str(print("Random Index Value: " + str(az_geography_groups_list[az_geography_groups_list.index(az_geography_group)][random.randint(0, len(az_geography_groups_list[az_geography_groups_list.index(az_geography_group)])-1)]))))

            return az_geography_groups_list[az_geography_groups_list.index(az_geography_group)][random.randint(0, len(az_geography_groups_list[az_geography_groups_list.index(az_geography_group)])-1)]["name"]

# # TODO: Deprecate this function if not in use
# def get_azure_recommended_locations_list_by_geography_groups():

#     az_locations_list = utils.azure_cli_run_command('account list-locations')

#     unique_geography_groups_list = []

#     for az_location in az_locations_list:
#         if az_location["metadata"]["geographyGroup"] and az_location["metadata"]["geographyGroup"] not in unique_geography_groups_list:
#             unique_geography_groups_list.append(az_location["metadata"]["geographyGroup"])

#     for az_geography_group_item in unique_geography_groups_list:
#         for az_location in az_locations_list:
#             if az_location["metadata"]["geographyGroup"] == az_geography_group_item and az_location["metadata"]["regionCategory"] == "Recommended":
#                 print(az_location["metadata"]["geographyGroup"], '-', az_location["metadata"]["regionCategory"])

# get_azure_supported_locations - Lists all supported locations for Azure in the current subscription.
def get_azure_supported_locations():
    az_locations_list = utils.azure_cli_run_command('account list-locations')

    az_supported_locations_obj_by_geography_groups = {}

    for az_location in az_locations_list:
        if az_location["metadata"]["geographyGroup"] and utils.trim_spaces(az_location["metadata"]["geographyGroup"]) not in az_supported_locations_obj_by_geography_groups.keys():
            az_supported_locations_obj_by_geography_groups.update({utils.trim_spaces(az_location["metadata"]["geographyGroup"]): []})
        elif not az_location["metadata"]["geographyGroup"]:
            az_supported_locations_obj_by_geography_groups.update({"logical": []})

    for az_location in az_locations_list:
        if az_location["metadata"]["regionType"] == "Physical":
            az_supported_locations_obj_by_geography_groups[utils.trim_spaces(az_location["metadata"]["geographyGroup"])].append(az_location)
        else:
            az_supported_locations_obj_by_geography_groups["logical"].append(az_location)

    return az_supported_locations_obj_by_geography_groups

# TODO: get_azure_supported_locations_sdk - Lists all supported locations for Azure in the current subscription via Azure SDK.
def get_azure_supported_locations_sdk():

    # credentials =  ServicePrincipalCredentials(
    #     client_id=os.environ['AZURE_CLIENT_ID'],
    #     secret=os.environ['AZURE_CLIENT_SECRET'],
    #     tenant=os.environ['AZURE_TENANT_ID']
    # )
    credentials =  ClientSecretCredential(
        client_id=os.environ['AZURE_CLIENT_ID'],
        client_secret=os.environ['AZURE_CLIENT_SECRET'],
        tenant_id=os.environ['AZURE_TENANT_ID']       
    )
    # credentials = DefaultAzureCredential(exclude_environment_credential=False)
    subscription_client = SubscriptionClient(credentials, api_version='2021-01-01')

    subscription_id = utils.get_subscription_id()

    az_locations_iter = subscription_client.subscriptions.list_locations(subscription_id)    
    
    az_locations_list = []
    for location in az_locations_iter:
        az_locations_list.append(location.name)

    return az_locations_list