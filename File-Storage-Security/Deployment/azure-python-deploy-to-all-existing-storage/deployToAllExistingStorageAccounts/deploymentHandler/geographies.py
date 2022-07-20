import locations

def get_geographies_from_storage_accounts(azure_storage_account_list, az_supported_locations_obj_by_geography_groups_dict):

    unique_scanner_stack_list = []

    for storage_account in azure_storage_account_list:

        az_geography_group = get_geography_group_from_location(storage_account["location"], az_supported_locations_obj_by_geography_groups_dict)

        print("\nStorage Account - " + str(az_geography_group))

        if az_geography_group not in unique_scanner_stack_list:
            unique_scanner_stack_list.append(az_geography_group)

    return unique_scanner_stack_list

def get_geography_group_from_location(az_location_name, az_geography_groups_dict): # eastus, { az_geography_groups_dict ... }

    for az_geography_group_item in az_geography_groups_dict:
        for az_location in az_geography_groups_dict[az_geography_group_item]:
            if az_location_name == az_location["name"]:
                return az_geography_group_item
    return None

def build_geographies_map_dict():

    geography_map_dict = {}

    azure_supported_locations_obj_by_geography_groups_dict = locations.get_azure_supported_locations()

    # print(str(azure_supported_locations_obj_by_geography_groups_dict))

    for azure_geography_group in azure_supported_locations_obj_by_geography_groups_dict:
        if azure_geography_group not in geography_map_dict:
            geography_map_dict.update({azure_geography_group: []})

    # Remove any logical Azure Locations in Map Dictionary
    geography_map_dict.pop("logical")

    return geography_map_dict

