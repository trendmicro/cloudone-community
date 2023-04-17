import sys, warnings
import json
from typing import List
from pprint import pprint
import boto3
from botocore.exceptions import ClientError
import os
import deepsecurity as ds
from deepsecurity.rest import ApiException
from deepsecurity.models.intrusion_prevention_rule import IntrusionPreventionRule
from deepsecurity.models.intrusion_prevention_rules import IntrusionPreventionRules
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

API_VERSION = "v1"
AWS_REGION = os.environ.get("region")
SENDER = os.environ.get("sender")
RECIPIENTS = os.environ.get("recipients")
HOST = (
    f"https://workload.{os.environ.get('cloudoneregion')}.cloudone.trendmicro.com/api"
)
C1_API_KEY = os.environ.get("c1_api")
VULNERABILITY_REPORT_LAMBDA_FUNCTION = os.getenv(
    "vulnerability_report_lambda_function_name"
)

######################################## Uncomment the following if you running on your local machine and comment the above 7 lines
# API_VERSION = "v1"
# AWS_REGION = "us-east-1"  ##You can input the aws region you want here
# SENDER = "sender@email.com"
# RECIPIENTS = "recipient@email.com"
# HOST = "https://workload.trend-us-1.cloudone.trendmicro.com/api"
# API_KEY = 'Your Cloud One API KEY'


inspector = boto3.client("inspector2", region_name=AWS_REGION)
sts = boto3.client("sts")
# Create a new SES resource and specify a region.
ses = boto3.client("ses", region_name=AWS_REGION)
secrets_manager = boto3.client(
    "secretsmanager"
)  # You may not need this if running locally so you can comment when runing your local machine
lambda_client = boto3.client("lambda")


def get_account_id():
    return sts.get_caller_identity()["Account"]


def ds_config_and_version(cloud_one_api_key):
    # Setup
    if not sys.warnoptions:
        warnings.simplefilter("ignore")
    API_VERSION = "v1"
    conf = ds.Configuration()
    conf.host = HOST
    conf.api_key["Authorization"] = f"ApiKey {cloud_one_api_key}"
    return conf, API_VERSION


def list_all_ips_rules(conf, api_version) -> List[IntrusionPreventionRule]:
    api_client = ds.ApiClient(configuration=conf)
    all_ips_rules: List[IntrusionPreventionRule] = list()
    ips = ds.IntrusionPreventionRulesApi(api_client=api_client)
    search_criteria = ds.SearchCriteria(id_value=0, id_test="greater-than")
    search_filter = ds.SearchFilter(max_items=5000, search_criteria=[search_criteria])
    while True:
        rules: IntrusionPreventionRules = ips.search_intrusion_prevention_rules(
            api_version=api_version, search_filter=search_filter, async_req=False
        )
        ips_rules: List[IntrusionPreventionRule] = rules.intrusion_prevention_rules
        if not ips_rules:
            break
        all_ips_rules.extend(ips_rules)
        search_criteria.id_value = ips_rules[-1].id
    return all_ips_rules


def computer_from_instance_id(configuration, api_version, instance_id):
    # Set search criteria
    search_criteria = ds.SearchCriteria()
    search_criteria.field_name = "ec2VirtualMachineSummary/instanceID"
    search_criteria.string_test = "equal"
    search_criteria.string_value = instance_id
    # Create a search filter with maximum returned items
    search_filter = ds.SearchFilter()
    search_filter.search_criteria = [search_criteria]
    expand = ds.Expand(ds.Expand.intrusion_prevention)
    expand.add(ds.Expand.ec2_virtual_machine_summary)
    # Perform the search and do work on the results
    computers_api = ds.ComputersApi(ds.ApiClient(configuration))
    computers = computers_api.search_computers(
        api_version, search_filter=search_filter, expand=expand.list(), overrides=False
    )
    num_found = len(computers.computers)
    if num_found == 0:
        print(f"No computers found for instance id: {instance_id}")
    for computer in computers.computers:
        return computer


# def vulnerabilities_from_instance(configuration, api_version, instance_id):
def vulnerabilities_from_instance(
    configuration, api_version, instance_id, all_rules_dict
):
    # Set search criteria
    search_criteria = ds.SearchCriteria()
    search_criteria.field_name = "ec2VirtualMachineSummary/instanceID"
    search_criteria.string_test = "equal"
    search_criteria.string_value = instance_id
    # Create a search filter with maximum returned items
    search_filter = ds.SearchFilter()
    search_filter.search_criteria = [search_criteria]
    expand = ds.Expand(ds.Expand.intrusion_prevention)
    expand.add(ds.Expand.ec2_virtual_machine_summary)
    # Perform the search and do work on the results
    computers_api = ds.ComputersApi(ds.ApiClient(configuration))
    rows = []
    computers = computers_api.search_computers(
        api_version, search_filter=search_filter, expand=expand.list(), overrides=False
    )
    num_found = len(computers.computers)
    if num_found == 0:
        print(f"No computers found for instance id: {instance_id}")
    for computer in computers.computers:
        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>   id", computer.id)
        if computer.intrusion_prevention.rule_ids:
            for ipr_id in computer.intrusion_prevention.rule_ids:
                print(">>>>>>>>> checking rule id:", ipr_id)
                cves = all_rules_dict.get(ipr_id)
                if cves:
                    for cve in cves:
                        rows.append(cve)
        else:
            print(f"instance has no ips - {instance_id}")
    return rows


def add_rules_to_computer(configuration, api_version, computer_id, rule_ids):
    # Initialization
    # Set Any Required Values
    api_instance = ds.ComputerIntrusionPreventionRuleAssignmentsRecommendationsApi(
        ds.ApiClient(configuration)
    )
    intrusion_prevention_rule_ids = ds.RuleIDs(rule_ids=rule_ids)
    overrides = False
    try:
        api_response = api_instance.add_intrusion_prevention_rule_ids_to_computer(
            computer_id,
            api_version,
            intrusion_prevention_rule_ids=intrusion_prevention_rule_ids,
            overrides=overrides,
        )
        pprint(api_response)
    except ApiException as e:
        print(
            "An exception occurred when calling ComputerIntrusionPreventionRuleAssignmentsRecommendationsApi.add_intrusion_prevention_rule_ids_to_computer: %s\n"
            % e
        )


def cves_from_instance(instance_id, inspector):
    cves = list()
    result = list()
    resp = inspector.list_findings(
        filterCriteria={
            "findingStatus": [{"comparison": "EQUALS", "value": "ACTIVE"}],
            "resourceId": [{"comparison": "EQUALS", "value": instance_id}],
        }
    )
    result.extend(resp["findings"])
    next_token = resp.get("nextToken")
    while next_token:
        resp = inspector.list_findings(
            filterCriteria={
                "findingStatus": [{"comparison": "EQUALS", "value": "ACTIVE"}],
                "resourceId": [{"comparison": "EQUALS", "value": instance_id}],
            },
            nextToken=next_token,
        )
        result.extend(resp["findings"])
        next_token = resp.get("nextToken")
    for finding in result:
        cve = finding.get("packageVulnerabilityDetails", {}).get("vulnerabilityId")
        if cve:
            cves.append(cve)
        # print(cve)
    return cves


def all_instances_details_from_inspector(inspector):
    instances = list()
    result = list()
    findings = inspector.list_finding_aggregations(
        aggregationType="AWS_EC2_INSTANCE",
        # aggregationRequest='AWS_EC2_INSTANCE',
    )
    result.extend(findings["responses"])
    next_token = findings.get("nextToken")
    while next_token:
        findings = inspector.list_finding_aggregations(
            aggregationType="AWS_EC2_INSTANCE",
            # aggregationRequest='AWS_EC2_INSTANCE',
            nextToken=next_token,
        )
        result.extend(findings["responses"])
        next_token = findings.get("nextToken")
    for finding in result:
        instance_details = {
            "id": finding["ec2InstanceAggregation"]["instanceId"],
            "name": finding["ec2InstanceAggregation"]
            .get("instanceTags", {})
            .get("Name"),
        }
        instances.append(instance_details)
    print("Found total instances =", len(instances))
    return instances


def find_rule_for_cve(all_rules, cve):
    return [rule for rule in all_rules if cve in (rule.to_dict()["cve"] or [])]


def send_email(sender, recipients, subject, body, html_body):
    print("sending email confirmation...")
    # The character encoding for the email.
    CHARSET = "UTF-8"

    # Try to send the email.
    try:
        # Provide the contents of the email.
        response = ses.send_email(
            Destination={
                "ToAddresses": recipients,
            },
            Message={
                "Body": {
                    "Html": {
                        "Charset": CHARSET,
                        "Data": html_body,
                    },
                    "Text": {
                        "Charset": CHARSET,
                        "Data": body,
                    },
                },
                "Subject": {
                    "Charset": CHARSET,
                    "Data": subject,
                },
            },
            Source=sender,
            # If you are not using a configuration set, comment or delete the
            # following line
            # ConfigurationSetName=CONFIGURATION_SET,
        )
    # Display an error if something goes wrong.
    except ClientError as e:
        print(e.response["Error"]["Message"])
    else:
        print("Email sent! Message ID:"),
        print(response["MessageId"])


def lambda_handler(event, context):
    # get secret
    secrets = secrets_manager.get_secret_value(SecretId=C1_API_KEY)
    sm_data = json.loads(secrets["SecretString"])
    new_api_format = sm_data["ApiKey"]
    conf, api_version = ds_config_and_version(new_api_format)
    ######################################## Uncomment the following (the line below) if you running on your local machine and comment the above last 4 lines
    # conf, api_version = ds_config_and_version(API_KEY)
    add_rules_output = dict()
    ips_rules = list_all_ips_rules(conf=conf, api_version=api_version)
    ips_rules_info = dict()
    for ipr in ips_rules:
        if ipr.cve:
            ips_rules_info[ipr.id] = {"cves": ipr.cve, "name": ipr.name}
    all_instance_details = all_instances_details_from_inspector(inspector)
    for instance_details in all_instance_details:
        instance_id = instance_details["id"]
        instance_name = instance_details["name"]
        vul_from_instance = vulnerabilities_from_instance(
            conf, api_version, instance_id, ips_rules_info
        )
        print(instance_name, instance_id)
        cves = cves_from_instance(instance_id, inspector)
        print("deep security", vul_from_instance)
        print("inspector", cves)
        for cve in cves:
            print(f"finding rule for {cve}")
            rules = [
                rule_id
                for rule_id in ips_rules_info
                if cve in ips_rules_info[rule_id]["cves"]
            ]
            if rules:
                computer = computer_from_instance_id(
                    configuration=conf,
                    api_version=api_version,
                    instance_id=instance_id,
                )
                print(f"adding rules - {rules} to computer")
                for rule_id in rules:
                    if (
                        computer.intrusion_prevention.rule_ids
                        and rule_id in computer.intrusion_prevention.rule_ids
                    ):
                        print(
                            f'rule "{rule_id}" already assigned to computer, skipping...'
                        )
                    else:
                        add_rules_to_computer(conf, api_version, computer.id, rule_id)
                        add_rules_output[instance_id] = ips_rules_info[rule_id]["name"]
    print(f"added rules to {len(add_rules_output)} computer(s)")
    print(add_rules_output)
    if add_rules_output:
        # Specify a configuration set. If you do not want to use a configuration
        # set, comment the following variable, and the
        # ConfigurationSetName=CONFIGURATION_SET argument below.

        # The email body for recipients with non-HTML email clients.
        body = f"Added rules:\r\n" "{add_rules_output}\r\n"
        added_rules_table_html = '<table border="1">' + "\n"
        # write headers
        added_rules_table_html += "</tr>" + "\n"
        for col in ["instance id", "rule name"]:
            added_rules_table_html += f"<th>{col}</th>" + "\n"
        added_rules_table_html += "</tr>" + "\n"
        # write rows
        for instance_id in add_rules_output:
            added_rules_table_html += "<tr>" + "\n"
            added_rules_table_html += f"<td>{instance_id}</td>" + "\n"
            added_rules_table_html += f"<td>{add_rules_output[instance_id]}</td>" + "\n"
            added_rules_table_html += "</tr>" + "\n"
        added_rules_table_html += "</table>"
        # The HTML body of the email.
        body_html = f"""<html>
        <head></head>
        <body>
        <h1>Added rules</h1>
        {added_rules_table_html}
        </body>
        </html>
        """
    else:
        body = "No new IPS rules added to instances"
        body_html = f"""<html>
        <head></head>
        <body>
        No new IPS rules added to instances
        </body>
        </html>
        """
    # The subject line for the email.
    subject = (
        f"IPS Rules Update from Workload Security - {get_account_id()}, {AWS_REGION}"
    )
    send_email(SENDER, RECIPIENTS.split(","), subject, body, body_html)

    ######################################## Uncomment the following if you running on your local machine
    lambda_payload = b""
    lambda_client.invoke(
        FunctionName=VULNERABILITY_REPORT_LAMBDA_FUNCTION,
        InvocationType="Event",
        Payload=lambda_payload,
    )
    print("triggered vulnerability report lambda function")


######################################## Uncomment the following if you running on your local machine
# lambda_handler(None, None)
