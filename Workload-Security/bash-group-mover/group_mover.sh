#!/bin/bash

# This will stop the script when an error is returned from any of the CLI commands
set -e

# Set the internal field separator
IFS=$'\n'

# Define Variables for the DSM
export DSMAPIKEY=""
export DSM="dsm.trendmicro.com"
export DSMPORT="4119"

# Define Variables for the Cloud One Workload Security
export WSAPIKEY=""
export REGION="us-1"
export SERVICE="workload"

# Export all groups names and description from DSM to an Array
export GROUPS_NAMES=(`curl -k -s -X GET https://$DSM:$DSMPORT/api/computergroups -H "api-secret-key: $DSMAPIKEY" -H 'api-version: v1' | jq '.[][].name'`)
export GROUPS_DESCRIPTION=(`curl -k -s -X GET https://$DSM:$DSMPORT/api/computergroups -H "api-secret-key: $DSMAPIKEY" -H 'api-version: v1' | jq '.[][].description'`)
export GROUPS_PARENTID=(`curl -k -s -X GET https://$DSM:$DSMPORT/api/computergroups -H "api-secret-key: $DSMAPIKEY" -H 'api-version: v1' | jq '.[][].parentGroupID'`)

# Count how many groups will be created
GROUPCOUNT=${#GROUPS_NAMES[@]}

# Loop to add all root Groups to Workload Security
echo ""
echo " - Adding all root Groups to Workload Security..."
echo ""
i=0
for (( i; i<$GROUPCOUNT; i++ ))
  do
     if [ ${GROUPS_PARENTID[i]} = 'null' ]; then
     curl -k -s -X POST https://$SERVICE.$REGION.cloudone.trendmicro.com/api/computergroups \
     -H 'Authorization: ApiKey '$WSAPIKEY'' \
     -H 'api-version: v1' \
     -H "Content-Type: application/json" \
     -d '{ "name": '${GROUPS_NAMES[i]}', "description": '${GROUPS_DESCRIPTION[i]}' }'
     echo ""
     sleep 5
     fi
  done

# Loop to add all Sub-Groups to Workload Security
echo ""
echo " - Adding all Sub-Groups to Workload Security..."

i=0
for (( i; i<$GROUPCOUNT; i++ ))
  do
     if [ ${GROUPS_PARENTID[i]} != "null" ]; then
    DSMGROUPSNAME=(`curl -k -s -X POST https://$DSM:$DSMPORT/api/computergroups/search -H "api-secret-key: $DSMAPIKEY" -H 'api-version: v1' -H "Content-Type: application/json" -d '{ "maxItems": 1, "searchCriteria": [{ "idValue": "'${GROUPS_PARENTID[i]}'" }]}' | jq '.[][].name' | sed 's/"//g'`)
    NEW_PARENTID=(`curl -k -s -X POST https://$SERVICE.$REGION.cloudone.trendmicro.com/api/computergroups/search -H 'Authorization: ApiKey '$WSAPIKEY'' -H 'api-version: v1' -H "Content-Type: application/json" -d '{ "maxItems": 1, "searchCriteria": [{ "fieldName":"name", "stringValue":"'$DSMGROUPSNAME'" }]}' | jq '.[][].ID'`)
    echo ""
    curl -k -s -X POST https://$SERVICE.$REGION.cloudone.trendmicro.com/api/computergroups \
     -H 'Authorization: ApiKey '$WSAPIKEY'' \
     -H 'api-version: v1' \
     -H "Content-Type: application/json" \
     -d '{ "name": '${GROUPS_NAMES[i]}', "description": '${GROUPS_DESCRIPTION[i]}', "parentGroupID": "'$NEW_PARENTID'" }'
     fi
  done
echo ""
echo "No more groups to be added :)"
echo ""