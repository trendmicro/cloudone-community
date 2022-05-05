import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Optional, Set

import click
import yaml
from PyInquirer import prompt

from conformity_migration.cloud_accounts import get_cloud_account_adder
from conformity_migration.conformity_api import (
    CloudOneConformityAPI,
    ConformityError,
    LegacyConformityAPI,
)
from conformity_migration.models import (
    Account,
    AccountDetails,
    Check,
    CommunicationSettings,
    Group,
    Note,
    Profile,
    ReportConfig,
    Rule,
    User,
)

from . import __version__ as tool_version
from .di import (
    app_config,
    c1_conformity_api,
    legacy_conformity_api,
    logger,
    user_config_path,
)
from .utils import str2bool

log = logger()


def create_user_config(user_conf_path: Path):
    if user_conf_path.exists():
        recreate_ok = ask_confirmation(
            msg="Configuration file already exists. Do you want to recreate it?",
            ask_if_sure=True,
        )
        if not recreate_ok:
            return

    region_map = app_config()["REGION_API_URL"]
    region_choices = [*region_map.keys(), "Other"]
    legacy_region = ask_choices(
        msg="Legacy Conformity Region", choices=region_choices, default=1
    )
    legacy_api_url = region_map.get(legacy_region)
    if not legacy_api_url:
        legacy_api_url = ask_input(
            "Please input the Legacy Conformity API URL (e.g. https://us-west-2-api.cloudconformity.com/v1:"
        )
    legacy_api_key = ask_input("Legacy Conformity API KEY:", mask_input=True)

    c1_region = ask_choices(
        msg="CloudOne Conformity Region", choices=region_choices, default=1
    )
    c1_api_url = region_map.get(c1_region)
    if not c1_api_url:
        c1_api_url = ask_input(
            "Please input the CloudOne Conformity API URL (e.g. https://us-west-2-api.cloudconformity.com/v1:"
        )
    c1_api_key = ask_input("CloudOne Conformity API KEY:", mask_input=True)

    conf = {
        "CLOUD_ONE_CONFORMITY": {
            "API_KEY": c1_api_key,
            "API_BASE_URL": c1_api_url,
        },
        "LEGACY_CONFORMITY": {
            "API_KEY": legacy_api_key,
            "API_BASE_URL": legacy_api_url,
        },
    }
    with open(user_conf_path, mode="w") as fh:
        return yaml.dump(conf, fh)


def cloud_type_accts_map(accts: List[Account]) -> Dict[str, List[Account]]:
    accts_map: Dict[str, List[Account]] = dict()

    for acct in accts:
        cloud_type_accts = accts_map.setdefault(acct.cloud_type, [])
        cloud_type_accts.append(acct)

    return accts_map


def acct_env_suffix(acct_environment: str) -> str:
    return f" ({acct_environment})" if acct_environment else ""


def empty_c1_conformity(c1_api: CloudOneConformityAPI):
    continue_ok = ask_confirmation(
        msg="!!! WARNING !!! This will delete all your Cloud One Conformity accounts and configurations. Do you want to continue?",
        ask_if_sure=True,
    )
    if not continue_ok:
        return

    print("Resetting Organisational Profile")
    c1_api.reset_organisation_profile()

    print("Deleting all Custom Profiles")
    for prof in c1_api.get_custom_profiles():
        print(f"  -- {prof.name}")
        c1_api.delete_profile(profile_id=prof.profile_id)

    print("Deleting all Organisational Report Configs")
    for rconf in c1_api.list_organisation_report_configs():
        print(f"  -- {rconf.title}")
        c1_api.delete_report_config(report_conf_id=rconf.report_config_id)

    print("Deleting all Communication Settings (Organisation-level)")
    cs_ids = {cs.com_setting_id for cs in c1_api.get_communication_settings(acct_id="")}
    for cs_id in cs_ids:
        print(f" -- {cs_id}")
        c1_api.delete_communication_settings(com_setting_id=cs_id)

    groups = c1_api.list_groups()
    for group in groups:
        print(f"Deleting Report Configs for group {group.name}")
        for rconf in c1_api.list_group_report_configs(group_id=group.group_id):
            print(f"  -- {rconf.title}")
            c1_api.delete_report_config(report_conf_id=rconf.report_config_id)

    print("Deleting all Accounts")
    for acct in c1_api.list_accounts():
        env_suffix = acct_env_suffix(acct.environment)
        print(f"  -- {acct.name}{env_suffix}")
        c1_api.delete_account(acct_id=acct.account_id)

    print("Deleting all Groups")
    for group in groups:
        print(f"  -- {group.name}")
        c1_api.delete_group(group_id=group.group_id)


def prompt_initialize_organisation_profile():
    log.info(
        """The Organisation Profile of Cloud One Conformity must be manually initialized first before
this tool can migrate the Organisation Profile settings. Follow these steps to initialize it:
    1. Login to your Cloud One account.
    2. Click Conformity.
    3. On the top navigation bar, click on Profiles.
    4. Under the Default profiles, click on Organisation Profile
    5. Wait for the Rule Settings to load.

    When you are done, please choose Yes below.
"""
    )

    done = False
    while not done:
        done = ask_confirmation(msg="Are you done?", ask_if_sure=True)


def run_migration(
    legacy_api: LegacyConformityAPI,
    c1_api: CloudOneConformityAPI,
    include_accts=Optional[Set[str]],
    exclude_accts=Optional[Set[str]],
):
    # this is part of workaround fix for Conformity Public API
    # will initialize Organisation Profile
    prompt_initialize_organisation_profile()

    exec_migration_func(lambda: update_organisation_profile(legacy_api, c1_api))

    exec_migration_func(lambda: add_managed_groups(legacy_api, c1_api))

    log.info("Adding all cloud accounts", flush=True)
    cloud_accts_to_migrate = exec_migration_func(
        lambda: add_cloud_accounts(
            legacy_api=legacy_api,
            c1_api=c1_api,
            include_accts=include_accts,
            exclude_accts=exclude_accts,
        )
    )
    if cloud_accts_to_migrate is None:
        cloud_accts_to_migrate = dict()

    log.info("Retrieving Legacy Conformity Users", flush=True)
    legacy_users = legacy_api.get_all_users()

    log.info("Retrieving CloudOne Conformity Users", flush=True)
    c1_users = c1_api.get_all_users()

    users_to_invite = set(legacy_users).difference(set(c1_users))
    if users_to_invite:
        invite_users(users_to_invite)

    users_to_verify_mobile = [user for user in legacy_users if user.is_mobile_verified]
    if users_to_verify_mobile:
        verify_users_mobile_numbers(users_to_verify_mobile)

    if any([users_to_invite, users_to_verify_mobile]):
        log.info("Retrieving updated list of CloudOne Conformity Users", flush=True)
        c1_users = c1_api.get_all_users()

    exec_migration_func(lambda: create_user_defined_groups(legacy_api, c1_api))

    exec_migration_func(lambda: copy_custom_profiles(legacy_api, c1_api))

    exec_migration_func(lambda: copy_organisation_report_configs(legacy_api, c1_api))

    exec_migration_func(lambda: migrate_all_groups_configs(legacy_api, c1_api))

    c1_org_id = c1_api.get_organisation_id()

    log.info("Copying communication channel settings (organisation-level)", flush=True)
    exec_migration_func(
        lambda: copy_communication_channel_settings(
            legacy_api=legacy_api,
            c1_api=c1_api,
            legacy_acct_id="",
            c1_acct_id="",
            legacy_users=legacy_users,
            c1_users=c1_users,
            c1_org_id=c1_org_id,
        )
    )

    for _, acct_id_map in cloud_accts_to_migrate.items():
        for legacy_acct_id, c1_acct_id in acct_id_map.items():
            exec_migration_func(
                lambda: migrate_account_configurations(
                    legacy_api=legacy_api,
                    c1_api=c1_api,
                    legacy_acct_id=legacy_acct_id,
                    c1_acct_id=c1_acct_id,
                    legacy_users=legacy_users,
                    c1_users=c1_users,
                    c1_org_id=c1_org_id,
                )
            )
            log.info("")


def migrate_all_groups_configs(
    legacy_api: LegacyConformityAPI, c1_api: CloudOneConformityAPI
):
    c1_group_id_map: Dict[Group, str] = {g: g.group_id for g in c1_api.list_groups()}

    for legacy_group in legacy_api.list_groups():
        log.info(
            f"Migrating group configurations for Group={legacy_group.name}, Tags={legacy_group.tags}",
            flush=True,
        )
        legacy_group_id = legacy_group.group_id
        c1_group_id = c1_group_id_map.get(legacy_group)
        if not c1_group_id:
            log.warn(
                f"Can't find corresponding CloudOne group for: Group={legacy_group.name}, Tags={legacy_group.tags}. Cannot migrate it's configurations."
            )
            continue
        exec_migration_func(
            lambda: copy_group_report_configs(
                legacy_api=legacy_api,
                c1_api=c1_api,
                legacy_group_id=legacy_group_id,
                c1_group_id=c1_group_id,  # type: ignore
            )
        )


def update_organisation_profile(
    legacy_api: LegacyConformityAPI, c1_api: CloudOneConformityAPI
):
    log.info("Copying Organisation Profile", flush=True)
    legacy_org_profile = legacy_api.get_organisation_profile(include_rule_settings=True)
    c1_org_profile = c1_api.get_organisation_profile(include_rule_settings=True)

    if c1_org_profile.included_rules:
        overwrite = ask_confirmation_or_auto_overwrite(
            "CloudOne Organisation Profile has configured rules in it. Do you want to overwrite it?",
            ask_if_sure=True,
        )
        if not overwrite:
            return
    c1_api.update_organisation_profile(profile=legacy_org_profile)


def add_cloud_accounts(
    legacy_api: LegacyConformityAPI,
    c1_api: CloudOneConformityAPI,
    include_accts=Optional[Set[str]],
    exclude_accts=Optional[Set[str]],
) -> Dict[str, Dict[str, str]]:

    c1_accts = c1_api.list_accounts()
    legacy_accts = legacy_api.list_accounts()

    # a value of None means it will not choose any account to include -- all accounts will be added to Cloud One unless in the excluded list
    # a value of an empty set means it will include nothing -- no account will be added to Cloud One
    if include_accts is not None:
        legacy_accts = [acct for acct in legacy_accts if acct.name in include_accts]

    # a value of None or of an empty set means the same thing: it will exclude nothing
    if exclude_accts:
        legacy_accts = [acct for acct in legacy_accts if acct.name not in exclude_accts]

    legacy_cloud_type_accts_map = cloud_type_accts_map(legacy_accts)
    c1_cloud_type_accts_map = cloud_type_accts_map(c1_accts)

    cloud_accts_to_migrate: Dict[str, Dict[str, str]] = dict()

    for cloud_type, legacy_accts in legacy_cloud_type_accts_map.items():
        acct_adder = get_cloud_account_adder(
            cloud_type=cloud_type, legacy_api=legacy_api, c1_api=c1_api
        )
        if acct_adder is None:
            log.info(f"Does not support {cloud_type.upper()} yet! Skipping it.")
            continue

        log.info(f"Adding {cloud_type.upper()} accounts to CloudOne Conformity:")
        c1_cloud_type_accounts = c1_cloud_type_accts_map.get(cloud_type, [])

        accts_to_migrate: Dict[str, str] = dict()
        cloud_accts_to_migrate[cloud_type] = accts_to_migrate
        for acct in legacy_accts:
            c1_acct_id: str
            exists, c1_acct_id = acct_adder.account_exists(
                c1_accts=c1_cloud_type_accounts, acct=acct
            )
            env_suffix = acct_env_suffix(acct.environment)
            if exists:
                log.info(
                    f"Account {acct.name}{env_suffix} already exists in CloudOne Conformity!"
                )
                if not (
                    ask_confirmation_or_auto_overwrite(
                        "Do you want to migrate configurations for this account (will overwrite existing ones)?",
                        ask_if_sure=True,
                    )
                ):
                    continue
            else:
                log.info(f" --> Account: {acct.name}{env_suffix}")
                c1_acct_id = exec_migration_func(
                    lambda: acct_adder.account_add(acct=acct)  # type: ignore
                )
                if not c1_acct_id:
                    continue

            accts_to_migrate[acct.account_id] = c1_acct_id

    return cloud_accts_to_migrate


def create_custom_profile(
    profile: Profile, legacy_api: LegacyConformityAPI, c1_api: CloudOneConformityAPI
):
    log.info(f"  --> Profile: {profile.name}", flush=True)
    profile_with_rules = legacy_api.get_profile(
        profile_id=profile.profile_id, include_rule_settings=True
    )
    c1_api.create_new_profile(profile=profile_with_rules)


def copy_custom_profiles(
    legacy_api: LegacyConformityAPI, c1_api: CloudOneConformityAPI
):
    log.info("Copying Custom Profiles", flush=True)
    legacy_profiles = legacy_api.get_custom_profiles()
    c1_profiles = c1_api.get_custom_profiles()

    legacy_profiles_set = set(legacy_profiles)
    c1_profiles_to_replace = [p for p in c1_profiles if p in legacy_profiles_set]
    if c1_profiles_to_replace:
        log.info(
            "Found following custom profiles that will be replaced during migration:"
        )
        for c1_profile in c1_profiles_to_replace:
            log.info(f"  - Profile: {c1_profile.name}")
        cont = ask_confirmation_or_auto_overwrite(
            "Continue migrating custom profiles?", ask_if_sure=True
        )
        if not cont:
            return

    for profile in c1_profiles_to_replace:
        # log.info(f" --> Deleting CloudOne profile: {profile.name}")
        c1_api.delete_profile(profile_id=profile.profile_id)

    for profile in legacy_profiles:
        exec_migration_func(
            lambda: create_custom_profile(
                profile=profile, legacy_api=legacy_api, c1_api=c1_api
            )
        )


def check_existing_c1_report_configs(
    c1_api: CloudOneConformityAPI,
    legacy_report_configs: List[ReportConfig],
    c1_report_configs: List[ReportConfig],
    rconf_type: str,
) -> bool:
    rconf_type = rconf_type.capitalize()

    legacy_rconf_set = set(legacy_report_configs)
    c1_rconf_to_replace = [r for r in c1_report_configs if r in legacy_rconf_set]
    if c1_rconf_to_replace:
        log.info(
            f"Found following {rconf_type} Report Configs that will be replaced during migration:"
        )
        for c1_rconf in c1_rconf_to_replace:
            log.info(f"  - Report Config: {c1_rconf.title}")
        cont = ask_confirmation_or_auto_overwrite(
            f"Continue migrating {rconf_type} Report Configs?", ask_if_sure=True
        )
        if not cont:
            return False

    for rconf in c1_rconf_to_replace:
        # log.info(f" --> Deleting CloudOne {rconf_type} Report Config: {rconf.title}")
        c1_api.delete_report_config(report_conf_id=rconf.report_config_id)

    return True


def copy_account_report_configs(
    legacy_api: LegacyConformityAPI,
    c1_api: CloudOneConformityAPI,
    legacy_acct_id: str,
    c1_acct_id: str,
):
    rconf_type = "Account"
    log.info(f"  --> Copying {rconf_type} Report Configs", flush=True)
    legacy_report_configs = legacy_api.list_account_report_configs(
        acct_id=legacy_acct_id
    )
    c1_report_configs = c1_api.list_account_report_configs(acct_id=c1_acct_id)

    cont_migration = check_existing_c1_report_configs(
        c1_api=c1_api,
        legacy_report_configs=legacy_report_configs,
        c1_report_configs=c1_report_configs,
        rconf_type=rconf_type,
    )
    if not cont_migration:
        return

    for report_config in legacy_report_configs:
        log.info(f"    --> Report Config: {report_config.title}")
        exec_migration_func(
            lambda: c1_api.create_account_report_config(
                report_conf=report_config.configuration, acct_id=c1_acct_id
            )
        )


def copy_group_report_configs(
    legacy_api: LegacyConformityAPI,
    c1_api: CloudOneConformityAPI,
    legacy_group_id: str,
    c1_group_id: str,
):
    rconf_type = "Group"
    log.info(f" --> Copying {rconf_type} Report Configs", flush=True)
    legacy_report_configs = legacy_api.list_group_report_configs(
        group_id=legacy_group_id
    )
    c1_report_configs = c1_api.list_group_report_configs(group_id=c1_group_id)

    cont_migration = check_existing_c1_report_configs(
        c1_api=c1_api,
        legacy_report_configs=legacy_report_configs,
        c1_report_configs=c1_report_configs,
        rconf_type=rconf_type,
    )
    if not cont_migration:
        return

    for report_config in legacy_report_configs:
        log.info(f"    --> Report Config: {report_config.title}")
        exec_migration_func(
            lambda: c1_api.create_group_report_config(
                report_conf=report_config.configuration, group_id=c1_group_id
            )
        )


def copy_organisation_report_configs(
    legacy_api: LegacyConformityAPI,
    c1_api: CloudOneConformityAPI,
):
    rconf_type = "Organisation"
    log.info(f"Copying {rconf_type} Report Configs", flush=True)
    legacy_report_configs = legacy_api.list_organisation_report_configs()
    c1_report_configs = c1_api.list_organisation_report_configs()

    cont_migration = check_existing_c1_report_configs(
        c1_api=c1_api,
        legacy_report_configs=legacy_report_configs,
        c1_report_configs=c1_report_configs,
        rconf_type=rconf_type,
    )
    if not cont_migration:
        return

    for report_config in legacy_report_configs:
        log.info(f"  --> Report Config: {report_config.title}")
        exec_migration_func(
            lambda: c1_api.create_organisation_report_config(
                report_conf=report_config.configuration
            )
        )


def create_user_defined_groups(
    legacy_api: LegacyConformityAPI, c1_api: CloudOneConformityAPI
):
    log.info("Creating groups")
    legacy_groups = legacy_api.list_groups(
        include_group_types=[Group.GROUP_TYPE_USER_DEFINED]
    )
    c1_groups = set(
        c1_api.list_groups(include_group_types=[Group.GROUP_TYPE_USER_DEFINED])
    )

    for group in legacy_groups:
        log.info(f" --> Group: {group.name}, Tags: {group.tags}", end="", flush=True)
        if group in c1_groups:
            log.info(" - Already exists! Skipping it.")
            continue
        exec_migration_func(
            lambda: c1_api.create_group(name=group.name, tags=group.tags)
        )

    if not legacy_groups:
        log.info(" --> No group found.")


def add_azure_group(mg: Group, c1_api: CloudOneConformityAPI):
    azure_conf = mg.cloud_data["azure"]  # type: ignore
    directory_name = mg.name
    directory_id = azure_conf["directoryId"]
    app_client_id = azure_conf["applicationId"]
    app_client_key = prompt_azure_app_client_id(
        directory_name, directory_id, app_client_id
    )
    c1_api.create_azure_directory(
        name=mg.name,
        directory_id=directory_id,
        app_client_id=app_client_id,
        app_client_key=app_client_key,
    )


def add_managed_groups(legacy_api: LegacyConformityAPI, c1_api: CloudOneConformityAPI):
    legacy_managed_groups = legacy_api.list_groups(
        include_group_types=[Group.GROUP_TYPE_MANAGED_GROUP]
    )
    c1_managed_groups = c1_api.list_groups(
        include_group_types=[Group.GROUP_TYPE_MANAGED_GROUP]
    )
    c1_managed_groups_set = set(c1_managed_groups)

    for mg in legacy_managed_groups:
        if mg in c1_managed_groups_set:
            # log.info(f"Managed Group {mg.name} ({mg.cloud_type.upper()}) already exists!")
            continue
        if mg.cloud_type == "azure":
            exec_migration_func(lambda: add_azure_group(mg=mg, c1_api=c1_api))


def prompt_azure_app_client_id(directory_name, directory_id, app_client_id) -> str:
    log.info(
        f"""
Please enter the App registration key for the following Active Directory:
If you lost the key, you may generate a new Client Secret on your Azure App Registration.
    Active Directory Name: {directory_name}
    Active Directory Tenant ID: {directory_id}
    App registration Application ID: {app_client_id}
"""
    )
    return ask_input("App registration key:", mask_input=True)


def _filter_users_with_verified_mobile(
    c1_user_ids: List[str],
    mobile_verified_c1_users: Set[str],
    c1_user_id_email_map: Dict[str, str],
) -> List[str]:

    c1_user_ids_set = set(c1_user_ids)
    unverified_user_ids = c1_user_ids_set.difference(mobile_verified_c1_users)
    for user_id in unverified_user_ids:
        email = c1_user_id_email_map.get(user_id, user_id)
        log.warn(
            f"User {email} doesn't have a mobile number verified. Excluding from SMS notification"
        )

    verified_c1_user_ids = c1_user_ids_set.intersection(mobile_verified_c1_users)
    return list(verified_c1_user_ids)


def _legacy_user_ids_to_c1_user_ids(
    legacy_user_ids: List[str],
    legacy_user_id_email_map: Dict[str, str],
    c1_email_user_id_map: Dict[str, str],
    channel: str,
) -> List[str]:
    c1_user_ids = []
    for legacy_user_id in legacy_user_ids:
        email = legacy_user_id_email_map.get(legacy_user_id)
        if email is None:
            log.warn(
                f"Cannot find email of Legacy Conformity user with an ID of: {legacy_user_id}. Excluding user from {channel} notification."
            )
            continue

        c1_user_id = c1_email_user_id_map.get(email)
        if c1_user_id is None:
            log.warn(
                f"Cannot find corresponding user in CloudOne Conformity: {email}. Excluding user from {channel} notification."
            )
            continue

        c1_user_ids.append(c1_user_id)

    return c1_user_ids


def copy_communication_channel_settings(
    legacy_api: LegacyConformityAPI,
    c1_api: CloudOneConformityAPI,
    legacy_acct_id: str,
    c1_acct_id: str,
    legacy_users: List[User],
    c1_users: List[User],
    c1_org_id: str,
):
    legacy_user_id_email_map = {user.user_id: user.email for user in legacy_users}
    c1_email_user_id_map = {user.email: user.user_id for user in c1_users}
    c1_user_id_email_map = {user.user_id: user.email for user in c1_users}
    mobile_verified_c1_users = {
        user.user_id for user in c1_users if user.is_mobile_verified
    }

    legacy_com_settings = legacy_api.get_communication_settings(acct_id=legacy_acct_id)
    candidate_com_settings: Set[CommunicationSettings] = set()
    for s in legacy_com_settings:
        legacy_conf = s.configuration
        c1_conf = legacy_conf
        if s.channel in ("email", "sms"):
            c1_conf["users"] = _legacy_user_ids_to_c1_user_ids(
                legacy_conf["users"],
                legacy_user_id_email_map,
                c1_email_user_id_map,
                s.channel,
            )
            if s.channel == "sms":
                c1_conf["users"] = _filter_users_with_verified_mobile(
                    c1_conf["users"], mobile_verified_c1_users, c1_user_id_email_map
                )

        candidate_com_settings.add(
            CommunicationSettings(
                com_setting_id=s.com_setting_id,
                channel=s.channel,
                enabled=s.enabled,
                filter=s.filter,
                configuration=c1_conf,
            )
        )

    c1_com_settings = set(c1_api.get_communication_settings(acct_id=c1_acct_id))
    new_com_settings = candidate_com_settings.difference(c1_com_settings)
    if new_com_settings:
        c1_api.create_communication_settings(
            com_settings=new_com_settings, acct_id=c1_acct_id, org_id=c1_org_id
        )


def migrate_account_configurations(
    legacy_api: LegacyConformityAPI,
    c1_api: CloudOneConformityAPI,
    legacy_acct_id: str,
    c1_acct_id: str,
    legacy_users: List[User],
    c1_users: List[User],
    c1_org_id: str,
):

    legacy_acct_details = legacy_api.get_account_details(acct_id=legacy_acct_id)
    name = legacy_acct_details.name
    environment = legacy_acct_details.environment
    cloud_type = legacy_acct_details.cloud_type
    env_suffix = acct_env_suffix(environment)
    log.info(
        f"Migrating account configurations for: {name}{env_suffix} [{cloud_type.upper()}]:"
    )

    log.info("  --> Updating account tags", flush=True)
    exec_migration_func(
        lambda: c1_api.update_account(
            acct_id=c1_acct_id,
            name=name,
            environment=environment,
            tags=legacy_acct_details.tags,
        )
    )

    log.info("  --> Copying account bot settings", flush=True)
    # bot_settings = legacy_api.get_account_bot_settings(acct_id=legacy_acct_id)
    bot_settings = legacy_acct_details.bot_settings
    if bot_settings:
        bot_settings.pop("lastModifiedFrom", None)
        bot_settings.pop("lastModifiedBy", None)
        if cloud_type == "aws" and str2bool(
            os.getenv("ENABLE_C1_AWS_CONFORMITY_BOT", "False")
        ):
            bot_settings["disabled"] = None
        exec_migration_func(
            lambda: c1_api.update_account_bot_settings(
                acct_id=c1_acct_id, settings=bot_settings
            )
        )

    log.info("  --> Copying account rules settings:", flush=True)
    exec_migration_func(
        lambda: copy_account_rules_settings(
            legacy_api=legacy_api,
            c1_api=c1_api,
            legacy_acct_id=legacy_acct_id,
            c1_acct_id=c1_acct_id,
            legacy_acct_details=legacy_acct_details,
            legacy_users=legacy_users,
        )
    )

    log.info("  --> Copying communication channel settings", flush=True)
    exec_migration_func(
        lambda: copy_communication_channel_settings(
            legacy_api=legacy_api,
            c1_api=c1_api,
            legacy_acct_id=legacy_acct_id,
            c1_acct_id=c1_acct_id,
            legacy_users=legacy_users,
            c1_users=c1_users,
            c1_org_id=c1_org_id,
        )
    )

    exec_migration_func(
        lambda: copy_account_report_configs(
            legacy_api=legacy_api,
            c1_api=c1_api,
            legacy_acct_id=legacy_acct_id,
            c1_acct_id=c1_acct_id,
        )
    )

    if has_suppressed_check(legacy_api=legacy_api, acct_id=legacy_acct_id):
        log.info("  --> Waiting for bot scan to finish ")
        exec_migration_func(
            lambda: wait_for_bot_scan_to_finish(c1_api=c1_api, acct_id=c1_acct_id)
        )

        log.info("  --> Copying suppressed checks")
        exec_migration_func(
            lambda: copy_suppressed_checks(
                legacy_api=legacy_api,
                c1_api=c1_api,
                legacy_acct_id=legacy_acct_id,
                c1_acct_id=c1_acct_id,
            )
        )
    else:
        log.info("  --> No suppressed check found to migrate")


def copy_account_rule_setting(
    legacy_api: LegacyConformityAPI,
    c1_api: CloudOneConformityAPI,
    legacy_acct_id: str,
    c1_acct_id: str,
    rule: Rule,
    user_map: dict,
):
    rule_id = rule.rule_id
    log.info(
        f"    --> Rule: {rule_id} ({'enabled' if rule.enabled else 'disabled'})",
        flush=True,
    )
    rule_with_notes = legacy_api.get_account_rule_setting(
        acct_id=legacy_acct_id, rule_id=rule_id, with_notes=True
    )

    note_msg = create_new_note_from_history_of_notes(
        notes=rule_with_notes.notes, user_map=user_map
    )

    c1_api.update_account_rule_setting(
        acct_id=c1_acct_id,
        rule_id=rule_id,
        setting=rule_with_notes.setting,
        note=note_msg,
    )


def copy_account_rules_settings(
    legacy_api: LegacyConformityAPI,
    c1_api: CloudOneConformityAPI,
    legacy_acct_id: str,
    c1_acct_id: str,
    legacy_acct_details: AccountDetails,
    legacy_users: List[User],
):

    user_map = {user.user_id: user for user in legacy_users}
    for rule in legacy_acct_details.rules:
        exec_migration_func(
            lambda: copy_account_rule_setting(
                legacy_api=legacy_api,
                c1_api=c1_api,
                legacy_acct_id=legacy_acct_id,
                c1_acct_id=c1_acct_id,
                rule=rule,
                user_map=user_map,
            )
        )


def truncate_txt_to_length(txt: str, length=-1, truncated_suffix="") -> str:
    if length == -1 or (0 <= len(txt) <= length):
        return txt

    return txt[: length - len(truncated_suffix)] + truncated_suffix


def get_most_recent_note_msg(notes: List[Note]) -> str:
    if not notes:
        return ""
    note = sorted(notes, key=lambda note: note.created_ts, reverse=True)[0]
    return note.note


def create_new_note_from_history_of_notes(
    notes: List[Note], user_map: Dict[str, User]
) -> str:
    note_msg = "[Copied settings via migration tool]"
    if not notes:
        return f"{note_msg} No history of notes found."

    note_frags = []
    sorted_notes = sorted(notes, key=lambda note: note.created_ts, reverse=True)
    for note in sorted_notes:
        user = user_map.get(note.created_by)
        user_name = f"{user.first_name} {user.last_name}" if user else ""
        ts = int(note.created_ts / 1000)
        dt_str = datetime.fromtimestamp(ts, tz=timezone.utc).isoformat(sep=" ")
        note_frag = f"On: {dt_str}\nBy: {user_name}\nNote: {note.note}"
        note_frags.append(note_frag)

    note_history = "\n\n".join(note_frags)

    note_msg = f"""{note_msg} History of notes:
-----------------------
{note_history}
-----------------------
"""

    return note_msg


def exec_migration_func(migration_func: Callable) -> Any:
    if not str2bool(os.getenv("SKIP_MIGRATION_FAILURES", "False")):
        return migration_func()
    try:
        return migration_func()
    except Exception:
        log.exception("There was a failure in migration")


def wait_for_bot_scan_to_finish(c1_api: CloudOneConformityAPI, acct_id: str):
    while not c1_api.is_bot_scan_done(acct_id=acct_id):
        time.sleep(app_config()["BOT_SCAN_CHECK_INTERVAL_IN_SECS"])
        continue


def has_suppressed_check(legacy_api: LegacyConformityAPI, acct_id: str) -> bool:
    checks = legacy_api.get_suppressed_checks(acct_id=acct_id, limit=1)
    return len(list(checks)) > 0


def copy_suppressed_check(
    legacy_api: LegacyConformityAPI,
    c1_api: CloudOneConformityAPI,
    c1_acct_id: str,
    legacy_check: Check,
):
    log.info(
        f"    --> {legacy_check.rule_id}|{legacy_check.region}|{legacy_check.service}|{legacy_check.resource_name}|{legacy_check.resource}",
        flush=True,
    )
    filters: Dict[str, Any] = {
        "ruleIds": [legacy_check.rule_id],
        "services": [legacy_check.service],
        "regions": [legacy_check.region],
        "statuses": "FAILURE",
    }
    if legacy_check.resource:
        filters["resourceSearchMode"] = "text"
        filters["resource"] = legacy_check.resource
    c1_checks = list(c1_api.get_checks(acct_id=c1_acct_id, filters=filters))
    c1_checks_map = {c: c for c in c1_checks}
    c1_check = c1_checks_map.get(legacy_check)
    if c1_check is None:
        show_instructions_for_missing_check(legacy_check)
        return
    legacy_check_detail = legacy_api.get_check_detail(
        check_id=legacy_check.check_id, with_notes=True
    )
    note_msg = get_most_recent_note_msg(legacy_check_detail.notes)
    if not note_msg:
        note_msg = "[Migration tool: No note found from the source Check]"
    note_msg = truncate_txt_to_length(txt=note_msg, length=200, truncated_suffix="..")
    # log.info(f"Note: {note_msg}")
    c1_api.suppress_check(
        check_id=c1_check.check_id,
        suppressed_until=legacy_check.suppressed_until,
        note=note_msg,
    )


def copy_suppressed_checks(
    legacy_api: LegacyConformityAPI,
    c1_api: CloudOneConformityAPI,
    legacy_acct_id: str,
    c1_acct_id: str,
):
    legacy_checks = legacy_api.get_suppressed_checks(acct_id=legacy_acct_id)
    for legacy_check in legacy_checks:
        exec_migration_func(
            lambda: copy_suppressed_check(
                legacy_api=legacy_api,
                c1_api=c1_api,
                c1_acct_id=c1_acct_id,
                legacy_check=legacy_check,
            )
        )


def show_instructions_for_missing_check(check: Check):
    log.warn(
        f"""
    Can't find the corresponding check in Cloud One. Please manually suppress the check below or try running Conformity Bot
    on this account and run this tool again.
        RuleID: {check.rule_id}
        Region: {check.region}
        Resource: {check.resource}
        Message: {check.message}
"""
    )


def verify_users_mobile_numbers(users_to_verify_mobile: Iterable[User]):
    log.info(
        """
Please have the following users in your CloudOne Account to have their mobile
numbers verified. If they are one of the recipients for SMS notifications,
then it is important to do this now before we proceed with migration:
"""
    )
    for user in users_to_verify_mobile:
        log.info(
            f" --> {user.first_name} {user.last_name}; Email={user.email}; Mobile={user.mobile_number}"
        )
    log.info("")
    ask_when_mobile_verification__done()


def invite_users(users_to_invite: Iterable[User]):
    log.info(
        """
Please invite the following users to your CloudOne Account.
If they are one of the recipients for your communication channel,
then it is important to add them now before we proceed with migration:
"""
    )
    for user in users_to_invite:
        log.info(f" --> {user.first_name} {user.last_name}; Email={user.email}")
    log.info("")
    ask_when_user_invite_done()


def ask_confirmation_or_auto_overwrite(
    msg: str, default=False, ask_if_sure=False
) -> bool:
    if str2bool(os.getenv("C1_CONFORMITY_OVERWRITE_ALL", "False")):
        return True

    return ask_confirmation(msg=msg, default=default, ask_if_sure=ask_if_sure)


def ask_confirmation(msg: str, default=False, ask_if_sure=False) -> bool:
    questions = [
        {
            "type": "confirm",
            "message": msg,
            "name": "continue",
            "default": default,
        },
    ]
    while True:
        answer = prompt(questions=questions)
        cont = answer["continue"]
        if not ask_if_sure or not cont:
            return cont

        sure = ask_confirmation(
            f"You chose {'Yes' if cont else 'No'}. Are you sure?", default=False
        )
        if sure:
            return cont


def ask_choices(msg: str, choices: List[str], default=1):
    questions = [
        {
            "type": "list",
            "message": msg,
            "name": "choice",
            "choices": choices,
            "default": default,
        },
    ]
    answer = prompt(questions=questions)
    return answer["choice"]


def ask_when_mobile_verification__done() -> None:
    while True:

        is_done = ask_confirmation(
            "Are you done with mobile verification?",
            default=False,
            ask_if_sure=True,
        )
        if is_done:
            return


def ask_when_user_invite_done() -> None:
    while True:

        is_done = ask_confirmation(
            "Are you done adding the users to Cloud One?",
            default=False,
            ask_if_sure=True,
        )
        if is_done:
            return


def ask_input(msg: str, mask_input=False) -> str:
    name = "input"
    questions = [
        {
            "type": "password" if mask_input else "input",
            "message": msg,
            "name": name,
            "default": "",
        },
    ]
    answer = prompt(questions=questions)
    return answer[name]


def pretty_print_com_settings(com_settings):
    for s in com_settings:
        log.debug(s)


@click.group(
    help=f"Conformity Migration Tool (ver {tool_version})\n\nMigrates your visiblity information in cloudconformity.com to cloudone.trendmicro.com",
)
@click.version_option(version=tool_version)
def cli():
    pass


@cli.command(help="Configures migration tool")
def configure():
    create_user_config(user_config_path())


@cli.command(help="Runs migration")
@click.option(
    "--skip-aws-prompt",
    is_flag=True,
    envvar="SKIP_AWS_PROMPT",
    show_envvar=True,
    required=False,
    default=False,
    help="Skips prompting for manually editing AWS Conformity stack",
)
@click.option(
    "--overwrite-all",
    is_flag=True,
    envvar="C1_CONFORMITY_OVERWRITE_ALL",
    show_envvar=True,
    required=False,
    default=False,
    help="Always overwrites Cloud One Conformity configurations. This prevents asking user for confirmation.",
)
@click.option(
    "--skip-migration-failures",
    is_flag=True,
    envvar="SKIP_MIGRATION_FAILURES",
    show_envvar=True,
    required=False,
    default=False,
    help="Will always allow migration to continue even when some configuration fails to migrate.",
)
@click.option(
    "--include-accounts-file",
    required=False,
    type=str,
    help="Text file containing account names that will be the only ones included in migration. Each account name should be in a separate line. An empty text file means the tool won't include any account in the migration.",
)
@click.option(
    "--exclude-accounts-file",
    required=False,
    type=str,
    help="Text file containing account names that will be excluded from migration. Each account name should be in a separate line.",
)
@click.option(
    "--enable-aws-bot",
    is_flag=True,
    envvar="ENABLE_C1_AWS_CONFORMITY_BOT",
    show_envvar=True,
    required=False,
    default=False,
    help="Enables bot settings for all migrated AWS accounts on Cloud One Conformity.",
)
def run(
    skip_aws_prompt: bool,
    overwrite_all: bool,
    skip_migration_failures: bool,
    include_accounts_file: str,
    exclude_accounts_file: str,
    enable_aws_bot: bool,
):
    include_accts: Optional[Set[str]] = None
    exclude_accts: Optional[Set[str]] = None
    if include_accounts_file:
        include_accts = read_accts_file(accounts_file=include_accounts_file)
    if exclude_accounts_file:
        exclude_accts = read_accts_file(accounts_file=exclude_accounts_file)

    os.environ["SKIP_AWS_PROMPT"] = "True" if skip_aws_prompt else "False"
    os.environ["C1_CONFORMITY_OVERWRITE_ALL"] = "True" if overwrite_all else "False"
    os.environ["SKIP_MIGRATION_FAILURES"] = (
        "True" if skip_migration_failures else "False"
    )
    os.environ["ENABLE_C1_AWS_CONFORMITY_BOT"] = "True" if enable_aws_bot else "False"
    try:
        run_migration(
            legacy_api=legacy_conformity_api(),
            c1_api=c1_conformity_api(),
            include_accts=include_accts,
            exclude_accts=exclude_accts,
        )
    except ConformityError as e:
        log.error(e)
        log.error(e.details)
        # raise e


def read_accts_file(accounts_file: str) -> Set[str]:
    accts = set()
    accounts_path = Path(accounts_file.strip())
    if not accounts_path.exists():
        raise FileNotFoundError(f"File does not exists: {accounts_file}")
    if not accounts_path.is_file():
        raise FileNotFoundError(f"Not a regular file: {accounts_file}")

    with open(accounts_path, mode="r") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            accts.add(line)
    return accts


@cli.command(
    "empty-c1",
    help="Deletes all accounts and configurations in Cloud One Conformity",
    hidden=True,
)
def empty_c1():
    try:
        empty_c1_conformity(c1_api=c1_conformity_api())
    except ConformityError as e:
        print(e)
        print(e.details)
        # raise e


if __name__ == "__main__":
    cli()
