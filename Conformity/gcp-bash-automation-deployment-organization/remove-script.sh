#!/bin/bash
set -e

GCP_PROJECT_ID=$(gcloud config list --format 'value(core.project)' 2> /dev/null)
ORG_ID=$(gcloud organizations list --format 'value(ID)')
PROJECT_LIST_ID=$(gcloud projects list --format="value(PROJECT_ID)")
CONFORMITY_SA_EMAIL=$(gcloud iam service-accounts list --filter=cloud-one-conformity-bot --format="value(EMAIL)")
CONFORMITY_ROLE=$(gcloud iam roles list --filter=CloudOneConformityAccess --organization=$ORG_ID --format="value(NAME)")

PROJECT_LIST_ID=$(gcloud projects list --format="value(PROJECT_ID)")

for project in $PROJECT_LIST_ID
do
echo "Removing Conformity Service Account from $project..."
gcloud projects remove-iam-policy-binding $project --member=serviceAccount:$CONFORMITY_SA_EMAIL --role=$CONFORMITY_ROLE
done

echo "The Conformity Service Account has been removed successfully from projects."


# Delete a custom role containing the permissions below:
echo "Deleting Cloud One Conformity Role..."
gcloud iam roles delete CloudOneConformityAccess --organization=$ORG_ID 
echo "Conformity custom role deleted"

# Delete Cloud One Conformity Service Account
echo "Deleting Cloud One Conformity Service Account..."
gcloud iam service-accounts delete $CONFORMITY_SA_EMAIL --project=$GCP_PROJECT_ID
echo "Conformity Service Account deleted"
