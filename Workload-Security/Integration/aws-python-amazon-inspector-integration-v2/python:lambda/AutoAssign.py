import os
import csv
import json
from copy import deepcopy
from urllib.request import Request, urlopen
import boto3


API_VERSION = "v1"
TOPIC_ARN = os.environ.get("topic_arn")
AWS_REGION = os.environ.get("aws_region")
BUCKET_NAME = os.environ.get("bucket_name")
FILE_NAME = os.environ.get("csv_filename")
C1_API_KEY = os.environ.get("c1_api_key")
HOST = (
    f"https://workload.{os.environ.get('cloudoneregion')}.cloudone.trendmicro.com/api"
)

# get secret
secrets = boto3.client("secretsmanager").get_secret_value(SecretId=C1_API_KEY)
sm_data = json.loads(secrets["SecretString"])
api_key = sm_data["ApiKey"]


######################################## Uncomment the following if you running on your local machine and comment the above 7 lines
# API_VERSION = "v1"
# AWS_REGION = "us-east-1"  ##You can input the aws region you want here
# BUCKET_NAME = "YOUR BUCKET NAME"
# FILE_NAME = "vulnerability_report.csv" # You can put the name of the file you want
# TOPIC_ARN = "arn:aws:sns:us-east-1:123456789012:test" # Your SNS Topic arn
# HOST = "https://workload.trend-us-1.cloudone.trendmicro.com/api"  # Your Cloud One host URL, make sure you use the right Cloud One Region
# api_key = "YOUR CLOUD ONE API KEY"
############################################## END OF TEST CODE ############################################################

HEADERS = {
    "Authorization": f"ApiKey {api_key}",
    "api-version": API_VERSION,
    "Content-Type": "application/json",
}

inspector = boto3.client("inspector2", AWS_REGION)
sts = boto3.client("sts")
sns = boto3.client("sns")
s3 = boto3.client("s3")


def get_response(url, headers=None, method="GET", data=None):
    if data:
        data = json.dumps(data)
        # Convert to String
        data = str(data)
        # Convert string to byte
        data = data.encode("utf-8")
        # Post Method is being invoked if data != None
        req = Request(url, method=method, data=data)
    else:
        req = Request(url)
    if headers:
        for item in headers.items():
            req.add_header(item[0], item[1])
    # Response
    response = json.loads(urlopen(req).read())
    return response


def add_ips_rule_to_specific_computer(rule_ids, computer_id):
    print("computer id:", computer_id)
    print("rule_ids", rule_ids)
    req_url = f"{HOST}/computers/{computer_id}/intrusionprevention/assignments"
    data = {"ruleIDs": rule_ids}
    res = get_response(url=req_url, headers=HEADERS, method="POST", data=data)
    return res


def ips_rules_from_cve_number(cve_number):
    req_url = f"{HOST}/intrusionpreventionrules/search"
    data = {
        "searchCriteria": [
            {"fieldName": "CVE", "stringTest": "equal", "stringValue": cve_number}
        ]
    }
    res = get_response(url=req_url, headers=HEADERS, method="POST", data=data)
    rules = res["intrusionPreventionRules"]
    # for rule in rules:
    #    print(rule["name"])
    #    print(rule["ID"])
    return rules


def get_specific_dsa_info_from_instance_id(instance_id):
    # Get DSA information for a specific instance ID
    req_url = f"{HOST}/computers"
    res = get_response(req_url, headers=HEADERS)
    computers = res["computers"]
    target_dsa = ""
    for computer in computers:
        aws_info = computer.get(
            "ec2VirtualMachineSummary", computer.get("noConnectorVirtualMachineSummary")
        )
        # print("HostName: {}".format(computer.get("hostName")))
        # print("ID: {}".format(computer.get("ID")))
        # print("displayName: {}".format(computer.get("displayName")))

        if aws_info:
            # print("InstanceID: {}".format(aws_info.get("instanceID")))
            if aws_info.get("instanceID") == instance_id:
                target_dsa = computer
    return target_dsa


def send_sns(topic_arn, subject, message):
    response = sns.publish(
        TargetArn=topic_arn,
        Subject=subject,
        Message=message,
        #   MessageStructure = 'json'
    )

    return response


def lambda_handler(event, context):
    # print event for debug
    print("received event:", event)

    instance_ids = event["resources"]
    cve_number = event["detail"]["title"]
    rules = ips_rules_from_cve_number(cve_number)  # CVE

    if rules:
        computers = []
        non_agents = []
        for instance_id in instance_ids:
            computer = get_specific_dsa_info_from_instance_id(instance_id)
            if computer:
                computers.append(computer)
            else:
                non_agents.append(instance_id)

        if computers:
            computers_updated = []
            for computer in computers:
                computer_id = computer["ID"]
                print("------------------------------------------------------")
                print("computer id;", computer_id)
                computer_assigned_ips_rules = computer.get(
                    "intrusionPrevention", {}
                ).get("ruleIDs", [])
                print("computer_assigned_ips_rules:", len(computer_assigned_ips_rules))

                not_assigned_rules = deepcopy(rules)
                print("rules:", len(rules))
                for rule in rules:
                    if rule["ID"] in computer_assigned_ips_rules:
                        not_assigned_rules.remove(rule)
                print("not_assigned_rules:", len(not_assigned_rules))

                if not not_assigned_rules:
                    print("Already assigned target rules!")
                    continue
                print(
                    add_ips_rule_to_specific_computer(
                        rule_ids=[rule["ID"] for rule in not_assigned_rules],
                        computer_id=computer_id,
                    )
                )
                print(f"Added target rules to computer - {computer.get('displayName')}")
                computers_updated.append(computer)
            if computers_updated:
                file_data = [
                    [
                        "Account Id",
                        "Instance Id",
                        "CVE",
                        "IPS Rule",
                    ],
                ]
                for computer in computers_updated:
                    for rule in not_assigned_rules:
                        file_data.extend(
                            [
                                [
                                    computer["ec2VirtualMachineSummary"]["accountID"],
                                    computer["ec2VirtualMachineSummary"]["instanceID"],
                                    cve_number,
                                    f'{rule["identifier"]} - {rule["name"]}',
                                ]
                            ]
                        )

                with open("/tmp/" + FILE_NAME, "w", newline="") as file:
                    writer = csv.writer(file)
                    writer.writerows(file_data)

                s3.upload_file("/tmp/" + FILE_NAME, BUCKET_NAME, FILE_NAME)
                message = f'IPS Rules assigned to {len(computers_updated)} instances for {cve_number}, for more details check "{FILE_NAME}" on "{BUCKET_NAME}" bucket'
            else:
                message = f"Already assigned rules to computers for {cve_number}"
        else:
            print("No computers found, skipping agents")
            message = f"No computers found for {cve_number}"
    else:
        print("Not found Corresponding Filter. CVE: {}".format(cve_number))
        message = f"No coreesponding rule found for {cve_number}"

    subject = "Auto remediation for CVEs from Inspector"
    print("sendig sns...")
    send_sns(topic_arn=TOPIC_ARN, subject=subject, message=message)


######################################## Uncomment the following if you running on your local machine
test_event = {
    "resources": ["i-097e06e3e6570246c", "i-0a968b3fe2ceae37b"],
    "detail": {"title": "CVE-2021-43267"},
}
lambda_handler(test_event, None)
