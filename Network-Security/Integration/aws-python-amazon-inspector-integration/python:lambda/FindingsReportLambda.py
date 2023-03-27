import os
import sys, warnings
import csv
import json
from typing import List
from pprint import pprint
from tempfile import TemporaryFile
import boto3
from botocore.exceptions import ClientError
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from urllib.request import Request, urlopen
from urllib.parse import urlencode

API_VERSION = "v1"
AWS_REGION = os.environ.get("awsregion")
SENDER = os.environ.get("sender")
RECIPIENTS = os.environ.get("recipients")
API_KEY = os.environ.get("c1_api")
HOST = f"https://network.{os.environ.get('cloudoneregion')}.cloudone.trendmicro.com/api/policies"

######################################## Uncomment the following if you running on your local machine
# AWS_REGION = "us-east-1"  ##You input the aws region you want
# SENDER = "sender@email.com"
# RECIPIENTS = "recipient@email.com"
# API_KEY = "Your ApiKey"
# HOST = "https://network.us-1.cloudone.trendmicro.com/api/policies/"

secrets = boto3.client('secretsmanager').get_secret_value(SecretId=API_KEY)
sm_data = json.loads(secrets["SecretString"])
new_api_format = sm_data["ApiKey"]
HEADERS = {"api-version": API_VERSION, "Authorization": f"ApiKey {new_api_format}"}
## initialize the variables
inspector = boto3.client("inspector2", region_name="us-east-1")
# Create a new SES resource and specify a region.
ses = boto3.client("ses", region_name=AWS_REGION)
sts = boto3.client("sts")

def get_account_id():
    return sts.get_caller_identity()["Account"]

def send_email(sender, recipients, subject, html_body, attachment_details):
    print("sending email ...")

    msg = MIMEMultipart()
    text_part = MIMEText(html_body, _subtype="html")
    msg.attach(text_part)

    msg["To"] = recipients
    msg["From"] = sender
    msg["Subject"] = subject ##

    for item in attachment_details:
        filename = item["filename"]
        attachment = item["attachment"]

        part = MIMEApplication(attachment.read(), filename)
        part.add_header("Content-Disposition", "attachment", filename=filename)
        msg.attach(part)

    ses.send_raw_email(RawMessage={"Data": msg.as_bytes()})


def cves_from_instance(instance_id, inspector):
    cves = list()
    result = list()
    # print('instance', instance_id)
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


def findings_from_inspector(inspector, all_findings=[], next_token=None):
    print("curent inspector findings count = ", len(all_findings))
    params = {}
    if next_token:
        params = {"nextToken": next_token}
    response = inspector.list_findings(**params)
    all_findings.extend(response["findings"])
    next_token = response.get("nextToken")
    if next_token:
        findings_from_inspector(inspector, all_findings, next_token)
    print("total inspector findings count = ", len(all_findings))
    return all_findings


def filter_findings_with_cves(all_findings):
    findings_with_cves = []
    for finding in all_findings:
        if finding.get("packageVulnerabilityDetails", {}).get("vulnerabilityId"):
            finding_info = {
                "title": finding["title"],
                "cve": finding["packageVulnerabilityDetails"]["vulnerabilityId"],
            }
            findings_with_cves.append(finding_info)
    print("findings with cve count = ", len(findings_with_cves))
    return findings_with_cves


def get_all_policies(all_policies=[], next_token=None, limit=1000):
    params = {"limit": limit}
    if next_token:
        params['cursor'] = next_token
    # use the 'headers' parameter to set the HTTP headers:
    req = Request(HOST + '?' + urlencode(params))
    for item in HEADERS.items():
        req.add_header(item[0], item[1])
    response = json.loads(urlopen(req).read())
    all_policies.extend(response["policies"])

    print(f'Fetched {len(all_policies)}/{response["totalCount"]}')
    next_token = response.get("next")
    if next_token:
        get_all_policies(all_policies, next_token)
    return all_policies


def filter_policies_with_cves(all_policies):
    policies_with_cves = []
    for policy in all_policies:
        for ref in policy.get("signatureReferences"):
            if ref["type"] == "cve":
                policy_details = {
                    "id": policy["id"],
                    "name": policy["name"],
                    "severity": policy["severity"],
                    "cve": ref["value"],
                    "uuid": policy["uuid"]
                }
                policies_with_cves.append(policy_details)
    print("policies with cve count = ", len(policies_with_cves))
    return policies_with_cves


def lambda_handler(event, context):

    # findings = filter_findings_with_cves(findings_from_inspector(inspector))
    policies = filter_policies_with_cves(get_all_policies())

    csv_rows_unprotected_cves = list()
    csv_rows_found_policies = list()

    all_instance_details = all_instances_details_from_inspector(inspector)
    for instance_details in all_instance_details:
        instance_id = instance_details["id"]
        instance_name = instance_details["name"]
        cves = cves_from_instance(instance_id, inspector)
        for cve in cves:
            policy_found = False
            for policy in policies:
                if policy["cve"] == cve:
                    print(
                        f"foung policy for {cve} on instance {instance_name} - {policy}"
                    )
                    print (policy)
                    csv_rows_found_policies.append(
                        [instance_id, instance_name, cve, policy["name"]]
                    )
                    policy_found = True
            if not policy_found:
                csv_rows_unprotected_cves.append([instance_id, instance_name, cve])

    print(csv_rows_found_policies)
    # print(csv_rows_unprotected_cves)

    tmp_csv_file_unprotected_cves = TemporaryFile(mode="w+", newline="")
    writer = csv.writer(tmp_csv_file_unprotected_cves)
    csv_header_unprotected_cves = ["instance id", "instance name", "cve"]
    writer.writerow(csv_header_unprotected_cves)
    for row in csv_rows_unprotected_cves:
        writer.writerow(row)
    tmp_csv_file_unprotected_cves.seek(0)

    # The subject line for the email.
    subject = f"Vulnerability Report (CVEs) from Cloud One Network Security - {get_account_id()}, {AWS_REGION}"

    unprotected_cves_html = '<table border="1">' + "\n"
    # write headers
    unprotected_cves_html += "</tr>" + "\n"
    for col in csv_header_unprotected_cves:
        unprotected_cves_html += f"<th>{col}</th>" + "\n"
    unprotected_cves_html += "</tr>" + "\n"
    # write rows
    for row in csv_rows_unprotected_cves:
        unprotected_cves_html += "<tr>" + "\n"
        for col in row:
            unprotected_cves_html += f"<td>{col}</td>" + "\n"
        unprotected_cves_html += "</tr>" + "\n"
    unprotected_cves_html += "</table>"

    tmp_csv_file_found_policies = TemporaryFile(mode="w+", newline="")
    writer = csv.writer(tmp_csv_file_found_policies)
    csv_header_found_policies = ["instance_id", "instance name", "cve", "Intrusion Prevention Filtering"]
    writer.writerow(csv_header_found_policies)
    for row in csv_rows_found_policies:
        writer.writerow(row)
    tmp_csv_file_found_policies.seek(0)

    found_policies_html = '<table border="1">' + "\n"
    # write headers
    found_policies_html += "</tr>" + "\n"
    for col in csv_header_found_policies:
        found_policies_html += f"<th>{col}</th>" + "\n"
    found_policies_html += "</tr>" + "\n"
    # write rows
    for row in csv_rows_found_policies:
        found_policies_html += "<tr>" + "\n"
        for col in row:
            found_policies_html += f"<td>{col}</td>" + "\n"
        found_policies_html += "</tr>" + "\n"
    found_policies_html += "</table>"

    # The HTML body of the email.
    body_html = f"""<html>
    <head></head>
    <body>
        <h1>Found Policies for CVE</h1>
        {found_policies_html}
        <h1>Unprotected CVEs</h1>
        {unprotected_cves_html}
    </body>
    </html>
    """

    send_email(
        SENDER,
        RECIPIENTS,
        subject,
        body_html,
        [
            {
                "filename": "unprotected_instances.csv",
                "attachment": tmp_csv_file_unprotected_cves,
            },
            {
                "filename": "protected_instances.csv",
                "attachment": tmp_csv_file_found_policies,
            },
        ],
    )
