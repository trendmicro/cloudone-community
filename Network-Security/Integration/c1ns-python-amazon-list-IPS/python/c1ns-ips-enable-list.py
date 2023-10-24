import os
import sys
import warnings
import csv
import json
import boto3
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from urllib.request import Request, urlopen
from urllib.parse import urlencode

API_VERSION = "v1"

#### leave the following uncomment for Cloud Formation Template deployment.. followings are parameters that need to be input##
# AWS_REGION = os.environ.get("awsregion")
# SENDER = os.environ.get("sender")
# RECIPIENTS = os.environ.get("recipients")
# API_KEY = os.environ.get("apikey")
# API_HOST = f"https://network.{os.environ.get('cloudoneregion')}.cloudone.trendmicro.com/api"


# Uncomment the following if you running on your local machine
AWS_REGION = "us-east-1"
SENDER = "sender@email.com"
RECIPIENTS = "recipient@email.com,recipient@email.com"
API_KEY = "YOUR CLOUD ONE API KEY"
API_HOST = "https://network.trend-us-1.cloudone.trendmicro.com/api"

#### leave the following uncomment for Cloud Formation Template deployment.. followings are getting API KEY secret from secret manager##
# secrets = boto3.client('secretsmanager').get_secret_value(SecretId=API_KEY)
# sm_data = json.loads(secrets["SecretString"])
# new_api_format = sm_data["ApiKey"]
# HEADERS = {"api-version": API_VERSION, "Authorization": f"ApiKey {new_api_format}"}

##################### Comment out the following for Cloud Formation Template deployment or if you are not running locally#############
HEADERS = {
    "api-version": API_VERSION,
    "Authorization": f"ApiKey {API_KEY}",
    "Content-Type": "application/json",
}

# initialize the variables
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


def save_to_csv(data):
    csv_file = "Enabled_ips.csv"
    # Define the CSV headers
    csv_headers = ["Enabled IPS"]

    # Write data to the CSV file
    with open(csv_file, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(csv_headers)
        for row in data:
            writer.writerow(row)
    return csv_file


def lambda_handler(event, context):
    all_policies = get_all_policies()
    active_policies = []
    for policy in all_policies:
        if policy["policyDefaults"]:
            if policy["policyDefaults"][0]["recommendedActive"]:
                active_policies.append([policy["name"]])
        if policy["policyOverrides"]:
            if policy["policyOverrides"][0]["enabled"]:
                active_policies.append([policy["name"]])

    print(f"Number of IPS Filters Enabled: {len(active_policies)}")

    # save_to_csv(active_policies)
    # The subject line for the email.
    subject = (
        "List of Intrusion Prevention Filters Enabled from Cloud One Network Security"
    )

    csv_file = save_to_csv(active_policies)

    attachment_details = [{"filename": csv_file, "attachment": open(csv_file)}]

    updated_filters_html = '<table border="1">' + "\n"
    # write headers
    updated_filters_html += "</tr>" + "\n"
    for col in ["name"]:
        updated_filters_html += f"<th>{col}</th>" + "\n"
    updated_filters_html += "</tr>" + "\n"
    # write rows
    for row in active_policies:
        updated_filters_html += "<tr>" + "\n"
        for col in row:
            updated_filters_html += f"<td>{col}</td>" + "\n"
        updated_filters_html += "</tr>" + "\n"
    updated_filters_html += "</table>"

    html_body = updated_filters_html

    # The HTML body of the email.
    body_html = f"""<html>
    <head></head>
    <body>
        {html_body}
    </body>
    </html>
    """

    send_email(SENDER, RECIPIENTS, subject, body_html, attachment_details)


lambda_handler(None, None)
