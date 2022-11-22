#!/bin/bash

# exit when any command fails
set -e

# Check if number of arguments isn't equal to 2
if [ "$#" -ne 2 ]; then
    echo "You must enter 2 command line arguments: CLOUD_ONE_REGION CLOUD_ONE_API_KEY"
    exit
fi

# Check if helm is installed.
if ! command -v helm &> /dev/null
then
    echo "helm could not be found. Install it following this: https://helm.sh/docs/intro/install/"
    exit
fi

# Check if jq is installed.
if ! command -v jq &> /dev/null
then
    echo "jq could not be found. Install it following this: https://stedolan.github.io/jq/download/"
    exit
fi

# First parameter is the cloudone dev us1 api key.
REGION=$1
C1APIKEY=$2
echo $C1APIKEY

# Creates a new Cluster in Container Security
CSAPIKEY=$(curl --location --request POST "https://container.${REGION}.cloudone.trendmicro.com/api/clusters" \
--header 'api-version: v1' \
--header 'Content-Type: application/json' \
--header 'Accept: application/json' \
--header "Authorization: ApiKey ${C1APIKEY}" \
--data-raw '{
  "name": "DemoCluster",
  "description": "This is a demo cluster."
}' | jq -r '.apiKey')

echo "Your Container Security Cluster API Key is ${CSAPIKEY}"

sed -e "s/YOUR_REGION_HERE/${REGION}/" -e "s/YOUR_API_HERE/${CSAPIKEY}/" preview-overrides.yaml > my-overrides.yaml

# Installs Container Security to k8s Cluster
helm install \
     trendmicro \
     --namespace trendmicro-system --create-namespace \
     --values my-overrides.yaml \
     https://github.com/trendmicro/cloudone-container-security-helm/archive/master.tar.gz

# Creates a new Ruleset in Container Security
RULESETID=$(curl --location --request POST "https://container.${REGION}.cloudone.trendmicro.com/api/rulesets" \
--header 'api-version: v1' \
--header 'Content-Type: application/json' \
--header 'Accept: application/json' \
--header "Authorization: ApiKey ${C1APIKEY}" \
--data-raw '{
    "name": "DemoRuleset",
    "description": "Ruleset for demo purposes.",
    "labels": [
        {
                "key": "app",
                "value": "java-goof"
            }
    ],
    "rules": [
            {
                "ruleID": "TM-00000002",
                "enabled": true,
                "mitigation": "terminate"
            },
            {
                "ruleID": "TM-00000026",
                "enabled": true,
                "mitigation": "isolate"
            }
        ]
}' | jq -r '.id')

# Creates a new Policy and adds the Ruleset to it.
POLICYID=$(curl --location --request POST "https://container.${REGION}.cloudone.trendmicro.com/api/policies" \
--header 'api-version: v1' \
--header 'Content-Type: application/json' \
--header 'Accept: application/json' \
--header "Authorization: ApiKey ${C1APIKEY}" \
--data-raw '{
    "name": "DemoPolicy",
    "description": "A Policy for demo purposes.",
    "default": {
        "rules": [
            {
                "action": "log",
                "mitigation": "log",
                "type": "podSecurityContext",
                "enabled": true,
                "statement": {
                    "properties": [
                        {
                            "key": "runAsNonRoot",
                            "value": "false"
                        }
                    ]
                }
            },
            {
                "action": "log",
                "mitigation": "log",
                "type": "podSecurityContext",
                "enabled": true,
                "statement": {
                    "properties": [
                        {
                            "key": "hostNetwork",
                            "value": "true"
                        }
                    ]
                }
            },
            {
                "action": "log",
                "mitigation": "log",
                "type": "podSecurityContext",
                "enabled": true,
                "statement": {
                    "properties": [
                        {
                            "key": "hostIPC",
                            "value": "true"
                        }
                    ]
                }
            },
            {
                "action": "log",
                "mitigation": "log",
                "type": "podSecurityContext",
                "enabled": true,
                "statement": {
                    "properties": [
                        {
                            "key": "hostPID",
                            "value": "true"
                        }
                    ]
                }
            },
            {
                "action": "log",
                "mitigation": "log",
                "type": "containerSecurityContext",
                "enabled": true,
                "statement": {
                    "properties": [
                        {
                            "key": "runAsNonRoot",
                            "value": "false"
                        }
                    ]
                }
            },
            {
                "action": "log",
                "mitigation": "log",
                "type": "containerSecurityContext",
                "enabled": true,
                "statement": {
                    "properties": [
                        {
                            "key": "privileged",
                            "value": "true"
                        }
                    ]
                }
            },
            {
                "action": "log",
                "mitigation": "log",
                "type": "containerSecurityContext",
                "enabled": true,
                "statement": {
                    "properties": [
                        {
                            "key": "allowPrivilegeEscalation",
                            "value": "true"
                        }
                    ]
                }
            },
            {
                "action": "log",
                "mitigation": "log",
                "type": "containerSecurityContext",
                "enabled": true,
                "statement": {
                    "properties": [
                        {
                            "key": "readOnlyRootFilesystem",
                            "value": "false"
                        }
                    ]
                }
            },
            {
                "action": "log",
                "mitigation": "log",
                "type": "podexec",
                "enabled": true,
                "statement": {
                    "properties": [
                        {
                            "key": "podExec",
                            "value": "true"
                        }
                    ]
                }
            },
            {
                "action": "log",
                "mitigation": "log",
                "type": "portforward",
                "enabled": true,
                "statement": {
                    "properties": [
                        {
                            "key": "podPortForward",
                            "value": "true"
                        }
                    ]
                }
            },
            {
                "action": "log",
                "mitigation": "log",
                "type": "unscannedImage",
                "enabled": true
            },
            {
                "action": "log",
                "mitigation": "log",
                "type": "malware",
                "enabled": true,
                "statement": {
                    "properties": [
                        {
                            "key": "count",
                            "value": "0"
                        }
                    ]
                }
            },
            {
                "action": "log",
                "mitigation": "log",
                "type": "podexec",
                "enabled": true,
                "statement": {
                    "properties": [
                        {
                            "key": "podExec",
                            "value": "true"
                        }
                    ]
                }
            },
            {
                "action": "log",
                "mitigation": "log",
                "type": "portforward",
                "enabled": true,
                "statement": {
                    "properties": [
                        {
                            "key": "podPortForward",
                            "value": "true"
                        }
                    ]
                }
            },
            {
                "action": "log",
                "mitigation": "log",
                "type": "vulnerabilities",
                "enabled": true,
                "statement": {
                    "properties": [
                        {
                            "key": "max-severity",
                            "value": "high"
                        }
                    ]
                }
            },
            {
                "action": "log",
                "mitigation": "log",
                "type": "contents",
                "enabled": true,
                "statement": {
                    "properties": [
                        {
                            "key": "max-severity",
                            "value": "high"
                        }
                    ]
                }
            },
            {
                "action": "log",
                "mitigation": "log",
                "type": "checklists",
                "enabled": true,
                "statement": {
                    "properties": [
                        {
                            "key": "max-severity",
                            "value": "high"
                        }
                    ]
                }
            },
            {
                "action": "log",
                "mitigation": "log",
                "type": "cvssAttackVector",
                "enabled": true,
                "statement": {
                    "properties": [
                        {
                            "key": "cvss-attack-vector",
                            "value": "network"
                        },
                        {
                            "key": "max-severity",
                            "value": "high"
                        }
                    ]
                }
            },
            {
                "action": "log",
                "mitigation": "log",
                "type": "cvssAttackComplexity",
                "enabled": true,
                "statement": {
                    "properties": [
                        {
                            "key": "cvss-attack-complexity",
                            "value": "high"
                        },
                        {
                            "key": "max-severity",
                            "value": "high"
                        }
                    ]
                }
            },
            {
                "action": "log",
                "mitigation": "log",
                "type": "cvssAvailability",
                "enabled": true,
                "statement": {
                    "properties": [
                        {
                            "key": "cvss-availability",
                            "value": "high"
                        },
                        {
                            "key": "max-severity",
                            "value": "high"
                        }
                    ]
                }
            },
            {
                "action": "log",
                "mitigation": "log",
                "type": "checklistProfile",
                "enabled": true,
                "statement": {
                    "properties": [
                        {
                            "key": "checklist-profile",
                            "value": "hipaa"
                        },
                        {
                            "key": "max-severity",
                            "value": "high"
                        }
                    ]
                }
            }
        ]
    },
    "runtime": {
            "default": {
                "rulesets": [
                    {
                        "name": "DemoRuleset",
                        "id": "'${RULESETID}'"
                    }
                ]
            }
        }
}' | jq -r '.id')

# Create demo namespace if it doesn't exist
kubectl create namespace demo --dry-run=client -o yaml | kubectl apply -f -

# Deplouy Vulnerable demo app
kubectl apply -f pods/java-goof.yaml
until kubectl get service/nginx-service-loadbalancer --output=jsonpath='{.status.loadBalancer}' | grep "ingress"; do : ; done
JAVAGOOFURL=$(kubectl get svc -n demo --selector=app=java-goof -o jsonpath='{.items[*].status.loadBalancer.ingress[0].hostname}')
echo "java-goof URL: http://${JAVAGOOFURL}"

# Deploy openssl vulnerable app
kubectl apply -f pods/openssl3.yaml
until kubectl get service/web-app-service --output=jsonpath='{.status.loadBalancer}' | grep "ingress"; do : ; done
WEBAPPURL=$(kubectl get svc -n demo --selector=app=web-app -o jsonpath='{.items[*].status.loadBalancer.ingress[0].hostname}')
echo "web-app URL: http://${WEBAPPURL}"