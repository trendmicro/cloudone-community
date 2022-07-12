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
def get_azure_recommended_locations_list_by_geography_groups():

    az_locations_list = utils.azure_cli_run_command('account list-locations')

    unique_geography_groups_list = []

    for az_location in az_locations_list:
        if az_location["metadata"]["geographyGroup"] and az_location["metadata"]["geographyGroup"] not in unique_geography_groups_list:
            unique_geography_groups_list.append(az_location["metadata"]["geographyGroup"])

    for az_geography_group_item in unique_geography_groups_list:
        for az_location in az_locations_list:
            if az_location["metadata"]["geographyGroup"] == az_geography_group_item and az_location["metadata"]["regionCategory"] == "Recommended":
                print(az_location["metadata"]["geographyGroup"], '-', az_location["metadata"]["regionCategory"])

# get_azure_supported_locations - Lists all supported locations for Azure in the current subscription.
def get_azure_supported_locations():
    az_locations_list = utils.azure_cli_run_command('account list-locations')

    az_supported_locations_obj_by_geography_groups = {}

    for az_location in az_locations_list:
        if az_location["metadata"]["geographyGroup"] and az_location["metadata"]["geographyGroup"] not in az_supported_locations_obj_by_geography_groups.keys():
            az_supported_locations_obj_by_geography_groups.update({az_location["metadata"]["geographyGroup"]: []})
        elif not az_location["metadata"]["geographyGroup"]:
            az_supported_locations_obj_by_geography_groups.update({"Logical": []})

    for az_location in az_locations_list:
        if az_location["metadata"]["regionType"] == "Physical":
            az_supported_locations_obj_by_geography_groups[az_location["metadata"]["geographyGroup"]].append(az_location)
        else:
            az_supported_locations_obj_by_geography_groups["Logical"].append(az_location)

    return az_supported_locations_obj_by_geography_groups
