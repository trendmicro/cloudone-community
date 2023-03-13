import os
import sys, warnings
import csv
from io import StringIO
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
import pandas as pd

import json
import urllib.parse


s3 = boto3.client("s3")

#### leave the following uncomment for Cloud Formation Template deployment.. followings are parameters that need to be input##
API_VERSION = "v1"
AWS_REGION = os.environ.get("awsregion")
SENDER = os.environ.get("sender")
RECIPIENTS = os.environ.get("recipients")
API_KEY = os.environ.get("c1_api")
API_HOST = f"https://network.{os.environ.get('cloudoneregion')}.cloudone.trendmicro.com/api"
ACTION_SET = os.environ.get("actionset")
PROFILE_NAME = os.environ.get("profilename")
######################################## Uncomment the following if you running on your local machine
# AWS_REGION = "us-east-1"
# SENDER = "sender@email.com"
# RECIPIENTS = "recipient@email.com,recipient@email.com"
# API_KEY = "Your Cloud One API-KEY"
# API_HOST = "https://network.us-1.cloudone.trendmicro.com/api"
# PROFILE_NAME = "Default-Profile"
# ACTION_SET = "Block + Notify"

secrets = boto3.client('secretsmanager').get_secret_value(SecretId=API_KEY)
sm_data = json.loads(secrets["SecretString"])
new_api_format = sm_data["ApiKey"]
HEADERS = {
    "api-version": API_VERSION,
    "Authorization": f"ApiKey {new_api_format}",
    "Content-Type": "application/json",
    'Accept':'application/json'
}

## initialize the variables
# Create a new SES resource and specify a region.
ses = boto3.client("ses", region_name=AWS_REGION)


def send_email(sender, recipients, subject, html_body, attachment_details=None):
    if not attachment_details:
        attachment_details = []
    print("sending email ...")

    msg = MIMEMultipart()
    text_part = MIMEText(html_body, _subtype="html")
    msg.attach(text_part)

    msg["To"] = recipients
    msg["From"] = sender
    msg["Subject"] = subject

    for item in attachment_details:
        filename = item["filename"]
        attachment = item["attachment"]

        part = MIMEApplication(attachment.read(), filename)
        part.add_header("Content-Disposition", "attachment", filename=filename)
        msg.attach(part)

    ses.send_raw_email(RawMessage={"Data": msg.as_bytes()})


def get_all_policies(all_policies=[], next_token=None, limit=1000):
    params = {"limit": limit}
    if next_token:
        params["cursor"] = next_token
    # use the 'headers' parameter to set the HTTP headers:
    req = Request(API_HOST + "/policies/?" + urlencode(params))
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
                # input(policy.keys())
                policy_details = {
                    "id": policy["id"],
                    "name": policy["name"],
                    "severity": policy["severity"],
                    "cve": ref["value"],
                    "uuid": policy["uuid"],
                    "action_set_id": policy["policyDefaults"][0]
                    .get("recommendedActionSet", {})
                    .get("id"),
                }
                policies_with_cves.append(policy_details)
    print("policies with cve count = ", len(policies_with_cves))
    return policies_with_cves


def get_response(url, headers=None, method="GET", data=None):
    if data:
        data = json.dumps(data)
        # Convert to String
        data = str(data)
        # Convert string to byte
        data = data.encode("utf-8")
        # Post Method is invoked if data != None
        req = Request(url, method=method, data=data)
        # Response
    else:
        req = Request(url)
    if headers:
        for item in headers.items():
            req.add_header(item[0], item[1])
    response = json.loads(urlopen(req).read())
    return response


def get_action_set_id_from_name(action_set_name):
    # To GET the Actionset ID
    # https://network.us-1.cloudone.trendmicro.com/api/actionsets
    params = {"allowedOnly": False}

    action_set_url = API_HOST + "/actionsets" + "/?" + urlencode(params)
    response = get_response(url=action_set_url, headers=HEADERS)
    # pprint(response)
    for action_set in response["actionsets"]:
        # print(action_set)
        if action_set["name"] == action_set_name:
            block_and_notify_action_set_id = action_set["id"]
            print(
                f"Found actionset id for '{action_set_name}': {block_and_notify_action_set_id}"
            )
            return block_and_notify_action_set_id
    print(f"Error: coudn't find action set matching '{action_set_name}'")


def get_profile_id_from_name(profile_name):
    # To GET the profile Id
    # https://network.us-1.cloudone.trendmicro.com/api/profiles
    profile_url = API_HOST + "/profiles"
    response = get_response(url=profile_url, headers=HEADERS)

    for profile in response["profiles"]:
        if profile["name"] == profile_name:
            profile_id = profile["id"]
            print(f"Found profile id for '{profile_name}' : {profile_id}")
            return profile_id
    print(f"Error: coudn't find profile id matching '{profile_name}'")


def get_distribution_history():
    # To GET distribution history
    # https://network.us-1.cloudone.trendmicro.com/api/appliancedistributions?type=profile
    distribution_history_url = API_HOST + "/appliancedistributions?type=profile"
    response = get_response(url=distribution_history_url, headers=HEADERS)
    print(response)


def get_appliance_ids():
    # To GET the appliances Id
    # https://network.us-1.cloudone.trendmicro.com/api/appliances
    appliance_ids = list()
    appliance_url = API_HOST + "/appliances"
    response = get_response(url=appliance_url, headers=HEADERS)
    for appliance in response["appliances"]:
        appliance_ids.append(appliance["ID"])
    return appliance_ids


def update_policy(profile_id, action_set_id, policy_signature_uuid):
    # To POST the Overrides to the filter/Policy:
    # https://network.us-1.cloudone.trendmicro.com/api/profiles/1/policyoverrides
    policy_override_api = f"{API_HOST}/profiles/{profile_id}/policyoverrides"
    body = {
        "signatureUuids": [policy_signature_uuid],
        "actionSetId": int(action_set_id),
        "toEnable": True,
    }
    response = get_response(
        url=policy_override_api, headers=HEADERS, data=body, method="PUT"
    )
    return response


def distribute_policy(appliance_id, profile_id):
    # To POST / distribute the policy to the appliances:
    # https://network.us-1.cloudone.trendmicro.com/api/appliancedistributions
    distribute_policy_api = API_HOST + "/appliancedistributions"
    body = {
        "applianceId": appliance_id,
        "type": "profile",
        "profile": {"id": profile_id},
    }
    response = get_response(url=distribute_policy_api, headers=HEADERS, data=body)
    return response


def cves_from_csv_string(csv_string):
    return pd.read_csv(StringIO(csv_string))["CVE"]


def lambda_handler(event, context):
    print("Received event: " + json.dumps(event, indent=2))

    # Get the object from the event and show its content type
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    # bucket = "c1nstestingstackbuckettt"
    # key = "sample.csv"
    try:
        print("downloading csv from bucket...")
        response = s3.get_object(Bucket=bucket, Key=key)
        print("CONTENT TYPE: " + response["ContentType"])
        body = response["Body"]
        csv_string = body.read().decode("utf-8")
        # print("csv_string", csv_string)

    except Exception as e:
        print(e)
        print(
            "Error getting object {} from bucket {}. Make sure they exist and your bucket is in the same region as this function.".format(
                key, bucket
            )
        )
        raise e

    table_rows_updated_filters = list()
    failed_table_rows_updated_filters = list()
    table_rows_policies_already_matched = list()

    # get the action set id
    action_set_id = get_action_set_id_from_name(ACTION_SET)
    # get the profile id
    profile_id = get_profile_id_from_name(PROFILE_NAME)
    cves = cves_from_csv_string(csv_string=csv_string)
    cves = list(set(cves))
    print(f"total CVEs from csv string: {len(cves)}")

    policies = filter_policies_with_cves(get_all_policies())

    policies_to_update = list()

    for cve in cves:
        for policy in policies:
            if policy["cve"] == cve:
                print(f"foung policy for {cve} - {policy}")
                if policy["action_set_id"] == action_set_id:
                    print(
                        ">>>>>>>>>>>>>>>>>> skipping policy update as action set id already mathces required action set"
                    )
                    table_rows_policies_already_matched.append(
                        [ACTION_SET, cve, policy["name"]]
                    )
                else:
                    policies_to_update.append([cve, policy])

    print(f"Number of policies to update: {len(policies_to_update)}")

    updated_policies = []
    for cve, policy in policies_to_update:
        if policy["uuid"] not in updated_policies:
            try:
                print(
                    update_policy(
                        profile_id=profile_id,
                        action_set_id=action_set_id,
                        policy_signature_uuid=str(policy["uuid"]),
                    )
                )
                updated_policies.append(policy["uuid"])
                table_rows_updated_filters.append([ACTION_SET, cve, policy["name"]])
            except Exception as e:
                print(e)
                failed_table_rows_updated_filters.append([policy["name"], e])

    # print('test policy update')
    # print(update_policy(profile_id, action_set_id, '00000001-0001-0001-0001-000000041752'))

    # get_distribution_history()
    appliance_ids = get_appliance_ids()
    # print(appliance_ids)
    for appliance in appliance_ids:
        try:
            distribute_policy(appliance_id=appliance, profile_id=profile_id)
        except Exception as e:
            print(e)

    # The subject line for the email.
    subject = "Intrusion Prevention Filtering Update from Network Security"

    # check if any intrusion prevention filters were updated or not and send email
    no_filters_to_update_html_body = "<p>No Intrusion Prevention Filters to update</p>"

    updated_filters_html_body = ""
    failed_updated_filters_html_body = ""
    skipped_updated_filters_html_body = ""

    if table_rows_updated_filters:
        updated_filters_html = '<table border="1">' + "\n"
        # write headers
        updated_filters_html += "</tr>" + "\n"
        for col in ["action id", "CVE", "Intrusion Prevention Filtering"]:
            updated_filters_html += f"<th>{col}</th>" + "\n"
        updated_filters_html += "</tr>" + "\n"
        # write rows
        for row in table_rows_updated_filters:
            updated_filters_html += "<tr>" + "\n"
            for col in row:
                updated_filters_html += f"<td>{col}</td>" + "\n"
            updated_filters_html += "</tr>" + "\n"
        updated_filters_html += "</table>"
        updated_filters_html_body = f"""<h1>Updated Intrusion Prevention Filters</h1>
        {updated_filters_html}
        """
        no_filters_to_update_html_body = ""

    if failed_table_rows_updated_filters:
        failed_updated_filters_html = '<table border="1">' + "\n"
        # write headers
        failed_updated_filters_html += "</tr>" + "\n"
        for col in ["Intrusion Prevention Filtering", "Reason"]:
            failed_updated_filters_html += f"<th>{col}</th>" + "\n"
        failed_updated_filters_html += "</tr>" + "\n"
        # write rows
        for row in failed_table_rows_updated_filters:
            failed_updated_filters_html += "<tr>" + "\n"
            for col in row:
                failed_updated_filters_html += f"<td>{col}</td>" + "\n"
            failed_updated_filters_html += "</tr>" + "\n"
        failed_updated_filters_html += "</table>"
        failed_updated_filters_html_body = f"""Failures in updating Intrusion Prevention Filters</h1>
        {failed_updated_filters_html}
        """
        no_filters_to_update_html_body = ""

    if table_rows_policies_already_matched:
        skipped_updated_filters_html = '<table border="1">' + "\n"
        # write headers
        skipped_updated_filters_html += "</tr>" + "\n"
        for col in ["action id", "CVE", "Intrusion Prevention Filtering"]:
            skipped_updated_filters_html += f"<th>{col}</th>" + "\n"
        skipped_updated_filters_html += "</tr>" + "\n"
        # write rows
        for row in table_rows_policies_already_matched:
            skipped_updated_filters_html += "<tr>" + "\n"
            for col in row:
                skipped_updated_filters_html += f"<td>{col}</td>" + "\n"
            skipped_updated_filters_html += "</tr>" + "\n"
        skipped_updated_filters_html += "</table>"
        skipped_updated_filters_html_body = f"""<h1>Already Updated Intrusion Prevention Filters</h1>
        {skipped_updated_filters_html}
        """
        no_filters_to_update_html_body = ""

    html_body = (
        updated_filters_html_body
        + failed_updated_filters_html_body
        + skipped_updated_filters_html_body
        + no_filters_to_update_html_body
    )

    # The HTML body of the email.
    body_html = f"""<html>
    <head></head>
    <body>
        {html_body}
    </body>
    </html>
    """

    send_email(
        SENDER,
        RECIPIENTS,
        subject,
        body_html,
    )

######################################## Uncomment the following if you running on your local machine
# lambda_handler(None, None)