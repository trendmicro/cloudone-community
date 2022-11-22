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

# Set color green for echo output
green=$(tput setaf 2)

# First parameter is the cloudone dev us1 api key.
REGION=$1
C1APIKEY=$2
echo "$C1APIKEY"

# Creates a new Ruleset in Container Security
echo "💬 ${green}Creating rules and policies in your Container Security..."
RULESETID=$(curl --location --request POST "https://container.${REGION}.cloudone.trendmicro.com/api/rulesets" \
--header 'api-version: v1' \
--header 'Content-Type: application/json' \
--header 'Accept: application/json' \
--header "Authorization: ApiKey ${C1APIKEY}" \
--data-raw '{
    "name": "DemoRuleset",
    "description": "Ruleset for demo purposes.",
    "labels": [],
    "rules": [
        {
            "ruleID": "TM-00000001",
            "enabled": true,
            "mitigation": "log"
        },
        {
            "ruleID": "TM-00000002",
            "enabled": true,
            "mitigation": "log"
        },
        {
            "ruleID": "TM-00000003",
            "enabled": true,
            "mitigation": "log"
        },
        {
            "ruleID": "TM-00000004",
            "enabled": true,
            "mitigation": "log"
        },
        {
            "ruleID": "TM-00000005",
            "enabled": true,
            "mitigation": "log"
        },
        {
            "ruleID": "TM-00000006",
            "enabled": true,
            "mitigation": "log"
        },
        {
            "ruleID": "TM-00000007",
            "enabled": true,
            "mitigation": "log"
        },
        {
            "ruleID": "TM-00000008",
            "enabled": true,
            "mitigation": "log"
        },
        {
            "ruleID": "TM-00000009",
            "enabled": true,
            "mitigation": "log"
        },
        {
            "ruleID": "TM-00000010",
            "enabled": true,
            "mitigation": "log"
        },
        {
            "ruleID": "TM-00000011",
            "enabled": true,
            "mitigation": "log"
        },
        {
            "ruleID": "TM-00000012",
            "enabled": true,
            "mitigation": "log"
        },
        {
            "ruleID": "TM-00000013",
            "enabled": true,
            "mitigation": "log"
        },
        {
            "ruleID": "TM-00000014",
            "enabled": true,
            "mitigation": "log"
        },
        {
            "ruleID": "TM-00000015",
            "enabled": true,
            "mitigation": "log"
        },
        {
            "ruleID": "TM-00000016",
            "enabled": true,
            "mitigation": "log"
        },
        {
            "ruleID": "TM-00000017",
            "enabled": true,
            "mitigation": "log"
        },
        {
            "ruleID": "TM-00000018",
            "enabled": true,
            "mitigation": "log"
        },
        {
            "ruleID": "TM-00000019",
            "enabled": true,
            "mitigation": "log"
        },
        {
            "ruleID": "TM-00000020",
            "enabled": true,
            "mitigation": "log"
        },
        {
            "ruleID": "TM-00000021",
            "enabled": true,
            "mitigation": "log"
        },
        {
            "ruleID": "TM-00000022",
            "enabled": true,
            "mitigation": "log"
        },
        {
            "ruleID": "TM-00000023",
            "enabled": true,
            "mitigation": "log"
        },
        {
            "ruleID": "TM-00000024",
            "enabled": true,
            "mitigation": "log"
        },
        {
            "ruleID": "TM-00000025",
            "enabled": true,
            "mitigation": "log"
        },
        {
            "ruleID": "TM-00000026",
            "enabled": true,
            "mitigation": "log"
        },
        {
            "ruleID": "TM-00000027",
            "enabled": true,
            "mitigation": "log"
        },
        {
            "ruleID": "TM-00000028",
            "enabled": true,
            "mitigation": "log"
        },
        {
            "ruleID": "TM-00000029",
            "enabled": true,
            "mitigation": "log"
        },
        {
            "ruleID": "TM-00000030",
            "enabled": true,
            "mitigation": "log"
        },
        {
            "ruleID": "TM-00000031",
            "enabled": true,
            "mitigation": "log"
        },
        {
            "ruleID": "TM-00000032",
            "enabled": true,
            "mitigation": "log"
        },
        {
            "ruleID": "TM-00000033",
            "enabled": true,
            "mitigation": "log"
        },
        {
            "ruleID": "TM-00000034",
            "enabled": true,
            "mitigation": "log"
        },
        {
            "ruleID": "TM-00000035",
            "enabled": true,
            "mitigation": "log"
        },
        {
            "ruleID": "TM-00000036",
            "enabled": true,
            "mitigation": "log"
        },
        {
            "ruleID": "TM-00000037",
            "enabled": true,
            "mitigation": "log"
        },
        {
            "ruleID": "TM-00000038",
            "enabled": true,
            "mitigation": "log"
        },
        {
            "ruleID": "TM-00000039",
            "enabled": true,
            "mitigation": "log"
        },
        {
            "ruleID": "TM-00000040",
            "enabled": true,
            "mitigation": "log"
        },
        {
            "ruleID": "TM-00000041",
            "enabled": true,
            "mitigation": "log"
        },
        {
            "ruleID": "TM-00000042",
            "enabled": true,
            "mitigation": "log"
        },
        {
            "ruleID": "TM-00000043",
            "enabled": true,
            "mitigation": "log"
        },
        {
            "ruleID": "TM-00000044",
            "enabled": true,
            "mitigation": "log"
        },
        {
            "ruleID": "TM-00000046",
            "enabled": true,
            "mitigation": "log"
        },
        {
            "ruleID": "TM-00000047",
            "enabled": true,
            "mitigation": "log"
        },
        {
            "ruleID": "TM-00000048",
            "enabled": true,
            "mitigation": "log"
        },
        {
            "ruleID": "TM-00000049",
            "enabled": true,
            "mitigation": "log"
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
                        "id": "'"${RULESETID}"'"
                    }
                ]
            }
        }
}' | jq -r '.id')
echo "💬 ${green}Rules and policy created."

# Creates a new Cluster in Container Security
echo "💬 ${green}Deploying Container Security..."
CREATE_CLUSTER_RESULT=$(curl --location --request POST "https://container.${REGION}.cloudone.trendmicro.com/api/clusters" \
--header 'api-version: v1' \
--header 'Content-Type: application/json' \
--header 'Accept: application/json' \
--header "Authorization: ApiKey ${C1APIKEY}" \
--data-raw '{
  "name": "DemoCluster",
  "description": "This is a demo cluster.",
  "policyID": "'"${POLICYID}"'"
}' | jq -r .)
echo "$CREATE_CLUSTER_RESULT" > "$STATE_FILE"

CSAPIKEY=$( < "$STATE_FILE"  jq -r '.apiKey')

sed -e "s/YOUR_REGION_HERE/${REGION}/" -e "s/YOUR_API_HERE/${CSAPIKEY}/" demo-overrides.yaml > my-overrides.yaml

# Installs Container Security to k8s Cluster
helm install \
     trendmicro \
     --namespace trendmicro-system --create-namespace \
     --values my-overrides.yaml \
     https://github.com/trendmicro/cloudone-container-security-helm/archive/master.tar.gz
echo "💬 ${green}Container Security deployed."