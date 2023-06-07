import requests
import json
from pprint import pprint

#define Deep Security manager hostname with port and API key
DSM_HOSTNAME = "<YOUR HOSTNAME HERE>"
DSM_API_KEY = "<YOUR DSM API KEY HERE>"

#define Cloud One Workload Security region
REGION = "<YOUR WORKLOAD REGION HERE>"
C1_API_KEY = "<YOUR C1 API KEY HERE>"

def get_folder_id(computer_group_id):
    if computer_group_id is not None:
        c1_cgep = f"https://{DSM_HOSTNAME}/api/computergroups/{computer_group_id}"
        response = requests.get(c1_cgep, headers=dsm_headers)
        cgdata = json.loads(response.content)
        cgname = cgdata['name']
        c1_scg = f"https://workload.{REGION}.cloudone.trendmicro.com/api/computergroups"
        response = requests.get(c1_scg, headers=c1_headers)
        search_data = json.loads(response.content)
        folder_id = None
        for group in search_data["computerGroups"]:
            if group["name"] == cgname:
                folder_id = group["ID"]
                break
        if folder_id is not None:
            return {
                "computerFilter": {
                    "type": "computers-in-group",
                    "computerGroupID": folder_id
                }
            }
    return None

dsmurl = f"https://{DSM_HOSTNAME}/api/scheduledtasks"
dsm_headers = {"api-version": "v1", "Content-Type": "application/json", "Authorization": DSM_API_KEY}

#setup Cloud One API and headers
c1 = f"https://workload.{REGION}.cloudone.trendmicro.com/api/scheduledtasks"
c1_headers = {"api-version": "v1", "Content-Type": "application/json", "Authorization": C1_API_KEY}

response = requests.get(dsmurl, headers=dsm_headers)
data = json.loads(response.content)

for task in data["scheduledTasks"]:
    payload = {
        "name": task["name"],
        "type": task["type"],
        "scheduleDetails": task["scheduleDetails"],
        "enabled": task["enabled"],
    }
    if "lastRunTime" in task:
        payload["lastRunTime"] = task["lastRunTime"]
    if "nextRunTime" in task:
        payload["nextRunTime"] = task["nextRunTime"]
    if task["type"] == "synchronize-cloud-account" and "synchronizeCloudAccountTaskParameters" in task:
        computer_group_id = task["synchronizeCloudAccountTaskParameters"]["computerFilter"].get("computerGroupID")
        payload["synchronizeCloudAccountTaskParameters"] = task["synchronizeCloudAccountTaskParameters"]
    elif task["type"] == "check-for-security-updates" and "checkForSecurityUpdatesTaskParameters" in task:
        computer_group_id = task["checkForSecurityUpdatesTaskParameters"]["computerFilter"].get("computerGroupID")
        payload["checkForSecurityUpdatesTaskParameters"] = get_folder_id(computer_group_id) or task["checkForSecurityUpdatesTaskParameters"]
    elif task["type"] == "scan-for-recommendations" and "scanForRecommendationsTaskParameters" in task:
        computer_group_id = task["scanForRecommendationsTaskParameters"]["computerFilter"].get("computerGroupID")
        payload["scanForRecommendationsTaskParameters"] = get_folder_id(computer_group_id) or task["scanForRecommendationsTaskParameters"]
    elif task["type"] == "generate-report" and "generateReportTaskParameters" in task:
        computer_group_id = task["generateReportTaskParameters"]["computerFilter"].get("computerGroupID")
        payload["generateReportTaskParameters"] = get_folder_id(computer_group_id) or task["generateReportTaskParameters"]
    elif task["type"] == "scheduled-agent-upgrade" and "scheduledAgentUpgradeTaskParameters" in task:
        computer_group_id = task["scheduledAgentUpgradeTaskParameters"]["computerFilter"].get("computerGroupID")
        payload["scheduledAgentUpgradeTaskParameters"] = get_folder_id(computer_group_id) or task["scheduledAgentUpgradeTaskParameters"]
    elif task["type"] == "send-alert-summary" and "sendAlertSummaryTaskParameters" in task:
        payload["sendAlertSummaryTaskParameters"] = get_folder_id(computer_group_id) or task["sendAlertSummaryTaskParameters"]
    elif task["type"] == "scan-for-integrity-changes" and "scanForIntegrityChangesTaskParameters" in task:
        computer_group_id = task["scanForIntegrityChangesTaskParameters"]["computerFilter"].get("computerGroupID")
        payload["scanForIntegrityChangesTaskParameters"] = get_folder_id(computer_group_id) or task["scanForIntegrityChangesTaskParameters"]
    elif task["type"] == "send-policy" and "sendPolicyTaskParameters" in task:
        computer_group_id = task["sendPolicyTaskParameters"]["computerFilter"].get("computerGroupID")
        payload["sendPolicyTaskParameters"] = get_folder_id(computer_group_id) or task["sendPolicyTaskParameters"]
    if task["type"] == "scan-for-malware" and "scanForMalwareTaskParameters" in task:
        computer_group_id = task["scanForMalwareTaskParameters"]["computerFilter"].get("computerGroupID")
        payload["scanForMalwareTaskParameters"] = get_folder_id(computer_group_id) or task["scanForMalwareTaskParameters"]
    # Send a POST request to create the task
    response = requests.post(c1, headers=c1_headers, json=payload)

    if response.status_code == 200:
        print(f"Task {task['name']} successfully created")
    else:
        print(f"Error creating task {task['name']}: {response.content}")