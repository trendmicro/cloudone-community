import geographies
import cloudone_fss_api

def deploy_geographically(azure_supported_locations_obj_by_geography_groups_dict, azure_storage_account_list):
    # Inventory of existing storage accounts
    # unique_storage_account_geographies = geographies.get_geographies_from_storage_accounts(azure_storage_account_list, azure_supported_locations_obj_by_geography_groups_dict)

    # Scanner Stack Map
    scanner_stacks_map_by_geographies_dict = geographies.build_geographies_map_dict()  

    # Storage Stacks Map
    storage_stacks_map_by_geographies_dict = geographies.build_geographies_map_dict()      

    # Populate the Scanner stack map by geographies
    # Inventory of existing FSS scanner stacks by Azure location
    existing_scanner_stacks_by_location = cloudone_fss_api.map_scanner_stacks_to_azure_locations()        

    if existing_scanner_stacks_by_location:

        print("\nScanner Stack Locations: " + str(existing_scanner_stacks_by_location))

        # Fetching Geography groups for the existing storage stacks, building a map
        
        # for existing_scanner_stack_location in existing_scanner_stacks_by_location:

            # geography = geographies.get_geography_group_from_location(existing_scanner_stack_location, azure_supported_locations_obj_by_geography_groups_dict)

            # if geography not in scanner_stacks_map_by_geographies_dict:
            #     scanner_stacks_map_by_geographies_dict.update({geography: []}) # { "US": [], "Europe" [], ...} only existing scanner stack in the azure location

        # print("\nAll Geos where scanner stack exists: " + str(scanner_stacks_map_by_geographies_dict))

        for existing_scanner_stack_by_location in existing_scanner_stacks_by_location:

            scanner_stack_geography = geographies.get_geography_group_from_location(existing_scanner_stack_by_location, azure_supported_locations_obj_by_geography_groups_dict)

            scanner_stacks_map_by_geographies_dict[scanner_stack_geography] = existing_scanner_stacks_by_location[existing_scanner_stack_by_location]

    # ----

    # # Building Geos with locations map
    # temp_existing_scanner_stack_location_list = []
    # temp_new_scanner_stack_location_list = []

    # # Cycle through everywhere we need a storage stack deployed for the storage account
    # for storage_account in azure_storage_account_list:

    #     # Cycle through all the Azure locations we have scanner stacks
    #     for existing_scanner_stack_location in existing_scanner_stacks_by_location:

    #         # If they correlate, map storage accounts to existing scanner stacks locations
    #         print(str(storage_account["location"]), str(existing_scanner_stack_location))
    #         if storage_account["location"] == existing_scanner_stack_location:

    #             temp_existing_scanner_stack_location_list.append(storage_account)

    #         # No correlation, mark them for new scanner stack deployment
    #         else:
    #             temp_new_scanner_stack_location_list.append(storage_account)

    # for geography in scanner_stacks_map_by_geographies_dict:

    #             # scanner_stacks_map_by_geographies_dict[geography].append({existing_scanner_stack_location: temp_existing_scanner_stack_location_list}) # { "US": [{"eastus": [...]}], "Europe": []}   

    #     scanner_stacks_map_by_geographies_dict[geography].append(temp_existing_scanner_stack_location_list)

    # for storage_account in temp_new_scanner_stack_location_list:

    #     print("\nNew Scanner Stack required: " + str(storage_account["location"]))

    #     geography = geographies.get_geography_group_from_location(storage_account["location"], azure_supported_locations_obj_by_geography_groups_dict)

    #     if geography not in scanner_stacks_map_by_geographies_dict:

    #         print("\nNew Scanner Stack Geography: " + str(geography))

    #         scanner_stacks_map_by_geographies_dict.update({geography: []}) # { "Middle East": [], "Europe" [], ...} new scanner stack geographies mapping
        
    #         print("\nUpdating Scanner Stack Geography: " + str(geography))
    #         scanner_stacks_map_by_geographies_dict[geography].append({storage_account["location"]: temp_existing_scanner_stack_location_list})

    # ----        

    # Populate the Storage stack map by geographies
    for storage_account in azure_storage_account_list:

        if existing_scanner_stacks_by_location:

            for existing_scanner_stack_by_location in existing_scanner_stacks_by_location:

                # if "storageStacks" not in existing_scanner_stacks_by_location[existing_scanner_stack_by_location][0].keys():

                #         existing_scanner_stacks_by_location[existing_scanner_stack_by_location][0]["storageStacks"] = []

                existing_scanner_stack_geography = geographies.get_geography_group_from_location(existing_scanner_stacks_by_location[existing_scanner_stack_by_location][0]["details"]["region"], azure_supported_locations_obj_by_geography_groups_dict)
                storage_account_geography = geographies.get_geography_group_from_location(storage_account["location"], azure_supported_locations_obj_by_geography_groups_dict)

                if existing_scanner_stack_geography == storage_account_geography:

                    temp_storage_stacks_dict = storage_stacks_map_by_geographies_dict[existing_scanner_stack_geography]                    

                    temp_storage_stacks_dict.append(storage_account)

                    storage_stacks_map_by_geographies_dict[existing_scanner_stack_geography] = temp_storage_stacks_dict

                    print("\nFound a match... " + str(existing_scanner_stack_geography) + " = " + str(storage_account_geography))

                else:
                    print("\nFound a mismatch... " + str(existing_scanner_stack_geography) + " ~ " + str(storage_account_geography))
        else:
            storage_account_geography = geographies.get_geography_group_from_location(storage_account["location"], azure_supported_locations_obj_by_geography_groups_dict)

            temp_storage_stacks_dict = storage_stacks_map_by_geographies_dict[storage_account_geography]                    

            temp_storage_stacks_dict.append(storage_account)

            storage_stacks_map_by_geographies_dict[storage_account_geography] = temp_storage_stacks_dict


    return scanner_stacks_map_by_geographies_dict, storage_stacks_map_by_geographies_dict