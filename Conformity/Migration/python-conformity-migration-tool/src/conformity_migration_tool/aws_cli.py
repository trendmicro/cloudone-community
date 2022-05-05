import csv
import json
import multiprocessing as mp
import os
import time
from dataclasses import dataclass
from typing import Iterable, Tuple

import boto3
import click
from mypy_boto3_cloudformation import CloudFormationClient
from mypy_boto3_cloudformation.type_defs import (
    DescribeStacksOutputTypeDef,
    ParameterTypeDef,
    UpdateStackOutputTypeDef,
)

from .di import c1_conformity_api, legacy_conformity_api


@click.group()
@click.pass_context
def cli(ctx):
    ctx.ensure_object(dict)
    # ctx.obj["region"] = region
    # ctx.obj["profile"] = profile


@cli.command(
    "generate-csv",
    help="Creates a csv file containing AWS accounts to be used for 'update-stack --csv-file' command option.",
)
@click.argument("csv-file")
def generate_csv(csv_file: str):
    print(f"Generating CSV: {csv_file}")
    legacy_api = legacy_conformity_api()
    accts = [acct for acct in legacy_api.list_accounts() if acct.cloud_type == "aws"]
    with open(csv_file, newline="", mode="w") as fh:
        csvw = csv.DictWriter(
            fh,
            fieldnames=[
                "Account Name",
                "AWS Account Number",
                "Old ExternalID",
                "Conformity Stack Name",
                "Conformity Stack Region",
                "AWS_PROFILE",
                "AWS_ACCESS_KEY_ID",
                "AWS_SECRET_ACCESS_KEY",
                "AWS_SESSION_TOKEN",
            ],
            dialect="excel",
        )
        csvw.writeheader()
        for acct in accts:
            access_conf = legacy_api.get_account_access_configuration(
                acct_id=acct.account_id
            )
            old_external_id = access_conf["externalId"]

            csvw.writerow(
                {
                    "Account Name": acct.name,
                    "AWS Account Number": acct.attributes["awsaccount-id"],
                    "Old ExternalID": old_external_id,
                    "Conformity Stack Name": "CloudConformity",
                    "Conformity Stack Region": "us-east-1",
                    "AWS_PROFILE": "",
                    "AWS_ACCESS_KEY_ID": "",
                    "AWS_SECRET_ACCESS_KEY": "",
                    "AWS_SESSION_TOKEN": "",
                }
            )
    print("Done!")
    print(
        """
    You may now open and edit the csv especially the credentials column(s).
    You can either edit AWS_PROFILE or AWS_ACCESS_KEY_ID/AWS_SECRET_ACCESS_KEY/AWS_SESSION_TOKEN
    If you specify both, then it will ignore AWS_PROFILE.
    AWS_SESSION_TOKEN is optional - you will need this when the credentials are temporary ones.

    The values in the columns 'Conformity Stack Name' and 'Conformity Stack Region' are the default ones.
    You may edit them as necessary.
"""
    )


@cli.command("update-stack", help="Updates ExternalID of Cloud Conformity Stack")
@click.option(
    "--stack-name",
    default="CloudConformity",
    show_default=True,
    required=False,
    help="Name of the Cloud Conformity Stack",
)
@click.option(
    "--external-id",
    type=str,
    required=False,
    help="New value for the Stack paramater ExternalID. If not specified, it will use the ExternalId from Cloud One Conformity.",
)
@click.option(
    "--csv-file",
    type=click.Path(
        exists=True, file_okay=True, dir_okay=False, readable=True, resolve_path=True
    ),
    required=False,
    help="CSV files containing AWS accounts with each account's profile and region to use.",
)
@click.option(
    "--region",
    type=str,
    envvar="AWS_DEFAULT_REGION",
    show_envvar=True,
    required=False,
    show_default=True,
    default="us-east-1",
    help="Region where Cloud Conformity Stack is deployed",
)
@click.option(
    "--profile",
    type=str,
    envvar="AWS_PROFILE",
    show_envvar=True,
    required=False,
    default=None,
    help="AWS credentials/config profile to use",
)
@click.option(
    "--access-key",
    type=str,
    envvar="AWS_ACCESS_KEY_ID",
    show_envvar=True,
    required=False,
    default=None,
    help="AWS Access Key",
)
@click.option(
    "--secret-key",
    type=str,
    envvar="AWS_SECRET_ACCESS_KEY",
    show_envvar=True,
    required=False,
    default=None,
    help="AWS Secret Key",
)
@click.option(
    "--session-token",
    type=str,
    envvar="AWS_SESSION_TOKEN",
    show_envvar=True,
    required=False,
    default=None,
    help="AWS Session Token",
)
@click.pass_context
def update_stack(
    ctx,
    stack_name: str,
    external_id: str,
    csv_file: str,
    region: str,
    profile: str,
    access_key: str,
    secret_key: str,
    session_token: str,
):
    # region = ctx.obj["region"]
    # profile = ctx.obj["profile"]
    if not external_id:
        print("Retrieving ExternalId from Cloud One Conformity")
        external_id = c1_conformity_api().get_organisation_external_id()
        print(f"ExternalId: {external_id}")

    proc_count = 1
    accts: Iterable[AccountStackInfo]
    if csv_file:
        accts = read_csv_file(csv_file=csv_file)
        accts = _fill_acct_with_defaults(
            accts=accts,
            default_stack_name=stack_name,
            default_profile=profile,
            default_region=region,
            default_access_key=access_key,
            default_secret_key=secret_key,
            default_session_token=session_token,
        )
        accts = list(accts)
        proc_count = min(len(accts), 10)
    else:
        accts = [
            AccountStackInfo(
                account_name="",
                aws_account_number="",
                old_external_id="",
                stack_name=stack_name,
                stack_region=region,
                aws_profile=profile,
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key,
                aws_session_token=session_token,
            )
        ]

    with mp.Pool(processes=proc_count) as pool:
        params = _update_stack_params(accts=accts, external_id=external_id)
        pool.map(_update_stack_worker, params)


@dataclass
class AccountStackInfo:
    account_name: str
    aws_account_number: str
    old_external_id: str
    stack_name: str
    stack_region: str
    aws_profile: str
    aws_access_key_id: str
    aws_secret_access_key: str
    aws_session_token: str


def _update_stack_params(
    accts: Iterable[AccountStackInfo],
    external_id: str,
) -> Iterable[Tuple[AccountStackInfo, str]]:
    for acct in accts:
        yield (acct, external_id)


def _update_stack_worker(params: Tuple[AccountStackInfo, str]):
    # print(f"[Process: {os.getpid()}] Params: {params}")
    acct, external_id = params
    try:
        _update_stack(acct=acct, external_id=external_id)
    except Exception as e:
        print(f"Failed to update stack for {acct.account_name}. Error: {e}")


def _fill_acct_with_defaults(
    accts: Iterable[AccountStackInfo],
    default_stack_name: str,
    default_profile: str,
    default_region: str,
    default_access_key: str,
    default_secret_key: str,
    default_session_token: str,
) -> Iterable[AccountStackInfo]:
    for acct in accts:
        stack_name = acct.stack_name if acct.stack_name else default_stack_name
        stack_region = acct.stack_region if acct.stack_region else default_region
        aws_profile = acct.aws_profile if acct.aws_profile else default_profile
        access_key = (
            acct.aws_access_key_id if acct.aws_access_key_id else default_access_key
        )
        secret_key = (
            acct.aws_secret_access_key
            if acct.aws_secret_access_key
            else default_secret_key
        )
        session_token = (
            acct.aws_session_token if acct.aws_session_token else default_session_token
        )
        yield AccountStackInfo(
            account_name=acct.account_name,
            aws_account_number=acct.aws_account_number,
            old_external_id=acct.old_external_id,
            stack_name=stack_name,
            stack_region=stack_region,
            aws_profile=aws_profile,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            aws_session_token=session_token,
        )


def read_csv_file(csv_file: str) -> Iterable[AccountStackInfo]:
    with open(csv_file, newline="", mode="r") as fh:
        csvr = csv.DictReader(fh, dialect="excel")
        for rec in csvr:
            acct = AccountStackInfo(
                account_name=rec["Account Name"],
                aws_account_number=rec["AWS Account Number"].strip(),
                old_external_id=rec["Old ExternalID"].strip(),
                stack_name=rec["Conformity Stack Name"].strip(),
                stack_region=rec["Conformity Stack Region"].strip(),
                aws_profile=rec["AWS_PROFILE"].strip(),
                aws_access_key_id=rec["AWS_ACCESS_KEY_ID"].strip(),
                aws_secret_access_key=rec["AWS_SECRET_ACCESS_KEY"].strip(),
                aws_session_token=rec["AWS_SESSION_TOKEN"].strip(),
            )
            yield acct


def _update_stack(acct: AccountStackInfo, external_id: str):

    if acct.aws_profile:
        os.environ["AWS_PROFILE"] = acct.aws_profile
        boto3.setup_default_session(profile_name=acct.aws_profile)
    else:
        boto3.setup_default_session(profile_name=None)

    if acct.aws_access_key_id and acct.aws_secret_access_key:
        session_token = acct.aws_session_token if acct.aws_session_token else None
        cfn = boto3.client(
            "cloudformation",
            region_name=acct.stack_region,
            aws_access_key_id=acct.aws_access_key_id,
            aws_secret_access_key=acct.aws_secret_access_key,
            aws_session_token=session_token,
        )
    else:
        cfn = boto3.client("cloudformation", region_name=acct.stack_region)
    old_external_id = get_stack_external_id(cfn=cfn, stack_name=acct.stack_name)

    acct_info = (
        f" [AWS={acct.aws_account_number} ({acct.account_name})]"
        if acct.aws_account_number
        else ""
    )

    if external_id == old_external_id:
        print(
            f"[Update stack skipped]{acct_info} [{old_external_id} --> {external_id}]",
            flush=True,
        )
        return

    print(
        f"[Update stack started]{acct_info} [{old_external_id} --> {external_id}]",
        flush=True,
    )

    params = [
        ParameterTypeDef(
            ParameterKey="AccountId",
            UsePreviousValue=True,
        ),
        ParameterTypeDef(
            ParameterKey="ExternalId",
            ParameterValue=external_id,
        ),
    ]
    res: UpdateStackOutputTypeDef = cfn.update_stack(
        StackName=acct.stack_name,
        UsePreviousTemplate=True,
        Parameters=params,
        Capabilities=["CAPABILITY_NAMED_IAM"],
    )
    stack_id = res["StackId"]

    (is_successful, reason) = wait_for_update_stack(
        cfn=cfn, stack_id=stack_id, check_interval_in_secs=5
    )
    if is_successful:
        print(
            f"[Update stack success]{acct_info} [{old_external_id} --> {external_id}]"
        )
    else:
        print(
            f"[Update stack failed! Reason={reason}]{acct_info} [{old_external_id} --> {external_id}]"
        )


def get_stack_external_id(cfn: CloudFormationClient, stack_name: str) -> str:
    res: DescribeStacksOutputTypeDef = cfn.describe_stacks(StackName=stack_name)
    stack = res["Stacks"][0]
    params = stack["Parameters"]
    for param in params:
        if param["ParameterKey"] == "ExternalId":
            return param["ParameterValue"]
    return ""


def wait_for_update_stack(
    cfn: CloudFormationClient, stack_id: str, check_interval_in_secs=5
) -> Tuple[bool, str]:
    is_success = False
    reason = ""
    while True:
        res: DescribeStacksOutputTypeDef = cfn.describe_stacks(StackName=stack_id)
        stack = res["Stacks"][0]
        status = stack["StackStatus"]
        if status == "UPDATE_IN_PROGRESS":
            time.sleep(check_interval_in_secs)
            continue
        reason = stack.get("StackStatusReason", "")
        reason = f"({status}) {reason}"
        if status in {"UPDATE_COMPLETE", "UPDATE_COMPLETE_CLEANUP_IN_PROGRESS"}:
            is_success = True
            break
        else:
            pretty_print(res)
            is_success = False
            break
    return is_success, reason


# @cli.command("update-stackset", help="Updates ExternalID of Cloud Conformity StackSet")
# @click.option(
#     "--stackset-name",
#     default="CloudConformity",
#     show_default=True,
#     required=False,
#     help="Name of the Cloud Conformity StackSet",
# )
# @click.option(
#     "--external-id",
#     type=str,
#     required=True,
#     help="New value for the StackSet paramater ExternalID",
# )
# @click.pass_context
# def update_stackset(ctx, stackset_name: str, external_id: str):

#     region = ctx.obj["region"]
#     profile = ctx.obj["profile"]

#     if profile:
#         os.environ["AWS_PROFILE"] = profile
#     cfn = boto3.client("cloudformation", region_name=region)

#     print(f"Region: {region}")
#     print(f"AWS_PROFILE: {profile}")
#     print(f"StackSet: {stackset_name}")
#     print(f"ExternalID: {external_id}")

#     params = [
#         ParameterTypeDef(
#             ParameterKey="AccountId",
#             UsePreviousValue=True,
#         ),
#         ParameterTypeDef(
#             ParameterKey="ExternalId",
#             ParameterValue=external_id,
#         ),
#     ]
#     res: UpdateStackSetOutputTypeDef = cfn.update_stack_set(
#         StackSetName=stackset_name,
#         UsePreviousTemplate=True,
#         Parameters=params,
#         Capabilities=["CAPABILITY_NAMED_IAM"],
#     )
#     pretty_print(res)
#     operation_id = res["OperationId"]
#     print(f"OperationId: {operation_id}")

#     (is_successful, reason) = wait_for_update_stack_set(
#         cfn=cfn,
#         stackset_name=stackset_name,
#         operation_id=operation_id,
#         check_interval_in_secs=5,
#     )
#     if is_successful:
#         print("Updated Successfully :-)")
#     else:
#         print("Update Failed!")
#         print(f"Reason: {reason}")


# def wait_for_update_stack_set(
#     cfn: CloudFormationClient,
#     stackset_name: str,
#     operation_id: str,
#     check_interval_in_secs=5,
# ) -> Tuple[bool, str]:
#     print("Waiting for StackSet update to finish", end="")
#     is_success = False
#     reason = ""
#     while True:
#         print(".", end="")
#         res: DescribeStackSetOperationOutputTypeDef = cfn.describe_stack_set_operation(
#             StackSetName=stackset_name, OperationId=operation_id
#         )
#         operation = res["StackSetOperation"]
#         status = operation["Status"]
#         if status in {"RUNNING", "QUEUED"}:
#             time.sleep(check_interval_in_secs)
#             continue
#         reason = f"Status: {status}"
#         if status == "SUCCEEDED":
#             is_success = True
#             break
#         else:
#             pretty_print(res)
#             is_success = False
#             break
#     print()
#     return is_success, reason


def pretty_print(obj):
    print(json.dumps(obj, indent=4, default=str))


if __name__ == "__main__":
    cli()
