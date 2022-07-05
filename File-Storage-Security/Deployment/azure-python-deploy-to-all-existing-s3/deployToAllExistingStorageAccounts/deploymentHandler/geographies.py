def get_geographies(deploy_storage_stack_list, az_supported_locations_obj_by_geography_groups_dict):

    unique_scanner_stack_list = []

    for storageAccount in deploy_storage_stack_list:

        az_geography_group = get_geography_group_from_location(storageAccount["location"], az_supported_locations_obj_by_geography_groups_dict)

        if az_geography_group not in unique_scanner_stack_list:

            unique_scanner_stack_list.append(az_geography_group)

    return unique_scanner_stack_list

def get_geography_group_from_location(az_location_name, az_geography_groups_dict): # eastus, { az_geography_groups_dict ... }

    for az_geography_group_item in az_geography_groups_dict:

        for az_location in az_geography_groups_dict[az_geography_group_item]:

            if az_location_name == az_location["name"]:

                return az_geography_group_item

    return None