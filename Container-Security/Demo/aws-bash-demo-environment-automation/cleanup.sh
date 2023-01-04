#!/bin/bash

# exit when any command fails
set -e

# Check if number of arguments isn't equal to 2
if [ "$#" -ne 2 ]; then
    echo "You must enter 2 command line arguments: CLOUD_ONE_REGION CLOUD_ONE_API_KEY"
    exit
fi

# Check if jq is installed.
if ! command -v jq &> /dev/null
then
    echo "jq could not be found. Install it following this: https://stedolan.github.io/jq/download/"
    exit
fi

# Set color green for echo output
green=$(tput setaf 2)

# Defie State File name
STATE_FILE=".container-security-demo"

# First parameter is the cloudone dev us1 api key.
REGION=$1
C1APIKEY=$2

# Reads the cluster name and deletes it
echo "💬 ${green}Destroying the cluster..."
CLUSTER_NAME=$(cat $STATE_FILE | jq -r '.clustername')
eksctl delete cluster "$CLUSTER_NAME"

# Reads the cluster id and deletes it
echo "💬 ${green}Deleting the cluster in Container Security..."
CLUSTERID=$(cat $STATE_FILE | jq -r '.clusterid')
curl --location --request DELETE "https://container.${REGION}.cloudone.trendmicro.com/api/clusters/${CLUSTERID}" \
--header 'api-version: v1' \
--header 'Content-Type: application/json' \
--header 'Accept: application/json' \
--header "Authorization: ApiKey ${C1APIKEY}"

# Reads the policy id and deletes it
echo "💬 ${green}Deleting the policy in Container Security..."
POLICYID=$(cat $STATE_FILE | jq -r '.policyid')
curl --location --request DELETE "https://container.${REGION}.cloudone.trendmicro.com/api/policies/${POLICYID}" \
--header 'api-version: v1' \
--header 'Content-Type: application/json' \
--header 'Accept: application/json' \
--header "Authorization: ApiKey ${C1APIKEY}"

# Reads the ruleset id and deletes it
echo "💬 ${green}Deleting the ruleset in Container Security..."
RULESETID=$(cat $STATE_FILE | jq -r '.rulesetid')
curl --location --request DELETE "https://container.${REGION}.cloudone.trendmicro.com/api/rulesets/${RULESETID}" \
--header 'api-version: v1' \
--header 'Content-Type: application/json' \
--header 'Accept: application/json' \
--header "Authorization: ApiKey ${C1APIKEY}"

echo "💬 ${green}Demo was succesfully deleted."