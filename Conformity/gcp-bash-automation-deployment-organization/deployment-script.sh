#!/bin/bash
set -e

while getopts d:o:c: args
do
  case "${args}" in
    d) DEPLOYMENT_NAME=${OPTARG};;
    o) CLOUD_ONE_API_KEY=${OPTARG};;
    c) CLOUD_ONE_REGION=${OPTARG};;
    *) echo "Invalid option: -${OPTARG}."
       exit 1 ;;
  esac
done

ORG_ID=$(gcloud organizations list --format 'value(ID)')
PROJECT_LIST_ID=$(gcloud projects list --format="value(PROJECT_ID)")

echo "Enabling Google Cloud APIs for projects..."
for project in $PROJECT_LIST_ID
do
# Enable Google APIs
gcloud services enable dns.googleapis.com bigquery.googleapis.com bigquerymigration.googleapis.com bigquerystorage.googleapis.com cloudapis.googleapis.com cloudresourcemanager.googleapis.com iam.googleapis.com accessapproval.googleapis.com cloudkms.googleapis.com compute.googleapis.com storage.googleapis.com sqladmin.googleapis.com dataproc.googleapis.com container.googleapis.com logging.googleapis.com pubsub.googleapis.com cloudresourcemanager.googleapis.com cloudasset.googleapis.com
echo "Conformity APIs enabled for $project"
done

# Create a custom role containing the permissions below:
echo "Deploying Cloud One Conformity Role..."
gcloud iam roles create CloudOneConformityAccess --organization="$ORG_ID" --file=cc-roles.yaml
CONFORMITY_ROLE=$(gcloud iam roles list --filter=CloudOneConformityAccess --organization="$ORG_ID" --format="value(NAME)")
echo "Conformity custom role created"
echo "$CONFORMITY_ROLE"

# Create Cloud One Conformity Service Account
echo "Deploying Cloud One Conformity Service Account..."
gcloud iam service-accounts create cloud-one-conformity-bot --description="GCP service account for connecting Cloud One Conformity Bot to GCP" --display-name="Cloud One Conformity Bot"
CONFORMITY_SA_EMAIL=$(gcloud iam service-accounts list --filter=cloud-one-conformity-bot --format="value(EMAIL)")
echo "Conformity Service Account created"
echo "$CONFORMITY_SA_EMAIL"

# Generate a Service Account JSON key
echo "Generating JSON file..."
gcloud iam service-accounts keys create Conformitykey.json --iam-account="$CONFORMITY_SA_EMAIL"
serviceAccountKeyJson=$(cat Conformitykey.json)

CONFORMITY_SA_UID=$(gcloud iam service-accounts describe "$CONFORMITY_SA_EMAIL" --format 'value(uniqueId)')
PROJECT_LIST_ID=$(gcloud projects list --format="value(PROJECT_ID)")

echo "------------------------"
echo "Adding GCP Organization to Cloud One Console..."
echo "------------------------"

wget -qO- --no-check-certificate \
  --method POST \
  --timeout=0 \
  --header "Content-Type: application/vnd.api+json" \
  --header "Authorization: apiKey $CLOUD_ONE_API_KEY" \
  --body-data "{
  'data': {
    'serviceAccountName': $DEPLOYMENT_NAME,
    'serviceAccountKeyJson': $serviceAccountKeyJson
  }
}" \
   "https://conformity.$CLOUD_ONE_REGION.cloudone.trendmicro.com/api/gcp/organisations"
   

echo "Mapping Cloud One Conformity Service Account to accounts..."
for project in $PROJECT_LIST_ID
do
echo "Adding Conformity Service Account to $project..."
gcloud projects add-iam-policy-binding "$project" --member=serviceAccount:"$CONFORMITY_SA_EMAIL" --role="$CONFORMITY_ROLE"
PROJECT_NAME=$(gcloud projects list --filter="$project" --format='value(NAME)')

ACCOUNT_ID=$(wget -qO- --no-check-certificate \
  --method POST \
  --timeout=0 \
  --header "Content-Type: application/vnd.api+json" \
  --header "Authorization: apiKey $CLOUD_ONE_API_KEY" \
  --body-data "{
  'data': {
    'type': 'account',
    'attributes': {
      'name': $PROJECT_NAME,
      'access': {
        'projectId': $project,
        'projectName': $PROJECT_NAME,
        'serviceAccountUniqueId': '$CONFORMITY_SA_UID' 
      } 
    }    
  }	
}" \
   "https://conformity.$CLOUD_ONE_REGION.cloudone.trendmicro.com/api/accounts/gcp" | jq '.data.id' | tr -d '"')

echo "$project added to Cloud One Conformity console" 
echo "Starting to scan $project"
echo "Account id: $ACCOUNT_ID" 

wget -qO- --no-check-certificate \
  --method POST \
  --timeout=0 \
  --header "Content-Type: application/vnd.api+json" \
  --header "Authorization: apiKey $CLOUD_ONE_API_KEY" \
   "https://conformity.$CLOUD_ONE_REGION.cloudone.trendmicro.com/api/accounts/$ACCOUNT_ID/scan"
   
done

echo "The projects have been added successfully to Cloud One Conformity. Go to your Cloud One Conformity console to check this out."
