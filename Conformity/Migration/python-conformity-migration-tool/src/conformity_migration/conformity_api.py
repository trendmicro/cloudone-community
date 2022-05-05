import json
from typing import Any, Dict, Iterable, List, Optional
from urllib.parse import quote

import backoff
import requests

from .models import (
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
from .typing import Protocol


class ConformityError(Exception):
    def __init__(self, *args: object, details="") -> None:
        super().__init__(*args)
        self.details = details


class ConformityConnectionError(ConformityError):
    pass


class ConformityUnauthorizedError(ConformityError):
    pass


class ConformityForbiddenError(ConformityError):
    pass


class ConformityResourceNotFoundError(ConformityError):
    pass


class ConformityClientError(ConformityError):
    pass


class ConformityServerInternalError(ConformityError):
    pass


class ConformityOtherError(ConformityError):
    pass


class ConformityAPI(Protocol):
    def current_user(self) -> User:
        pass

    def get_organisation_external_id(self) -> str:
        pass

    def get_account_access_configuration(self, acct_id: str) -> Dict[str, Any]:
        pass

    def add_aws_account(
        self,
        name: str,
        environment: str,
        role_arn: str,
        external_id: str,
        subscription_type="advanced",
    ) -> Dict[str, Any]:
        pass

    def add_azure_subscription(
        self,
        name: str,
        environment: str,
        subscription_id: str,
        active_directory_id: str,
    ) -> Dict[str, Any]:
        pass

    def get_group_details(self, group_id: str) -> Dict[str, Any]:
        pass

    def get_organisation_id(self) -> str:
        pass

    def get_all_users(self) -> List[User]:
        pass

    def list_groups(self, include_group_types: List[str] = None) -> List[Group]:
        pass

    def delete_account(self, acct_id: str) -> dict:
        pass

    def list_accounts(self) -> List[Account]:
        pass

    def get_organisation_profile(self, include_rule_settings=False) -> Profile:
        pass

    def update_organisation_profile(self, profile: Profile) -> Profile:
        pass

    def reset_organisation_profile(self) -> dict:
        pass

    def get_custom_profiles(self) -> List[Profile]:
        pass

    def get_profile(self, profile_id: str, include_rule_settings=False) -> Profile:
        pass

    def create_new_profile(self, profile: Profile) -> Profile:
        pass

    def delete_profile(self, profile_id: str):
        pass

    def list_organisation_report_configs(self) -> List[ReportConfig]:
        pass

    def list_group_report_configs(self, group_id: str) -> List[ReportConfig]:
        pass

    def list_account_report_configs(self, acct_id: str) -> List[ReportConfig]:
        pass

    def create_organisation_report_config(self, report_conf: Dict[str, Any]):
        pass

    def create_group_report_config(self, report_conf: Dict[str, Any], group_id: str):
        pass

    def create_account_report_config(self, report_conf: Dict[str, Any], acct_id: str):
        pass

    def delete_report_config(self, report_conf_id: str):
        pass

    def delete_group(self, group_id: str) -> dict:
        pass

    def create_group(self, name, tags=List[str]):
        pass

    def create_azure_directory(
        self, name: str, directory_id: str, app_client_id: str, app_client_key: str
    ):
        pass

    def delete_communication_settings(self, com_setting_id: str) -> dict:
        pass

    def get_communication_settings(self, acct_id: str) -> List[CommunicationSettings]:
        pass

    def create_communication_settings(
        self, com_settings: Iterable[CommunicationSettings], acct_id: str, org_id: str
    ):
        pass

    def get_account_details(self, acct_id: str) -> AccountDetails:
        pass

    def update_account(
        self, acct_id: str, name: str, environment: str, tags: List[str]
    ):
        pass

    def update_account_bot_settings(self, acct_id: str, settings: dict):
        pass

    def get_account_rule_setting(
        self, acct_id: str, rule_id: str, with_notes=False
    ) -> Rule:
        pass

    def update_account_rule_setting(
        self, acct_id: str, rule_id: str, setting: dict, note: str = "Copied from API"
    ):
        pass

    def is_bot_scan_done(self, acct_id: str) -> bool:
        pass

    def get_suppressed_checks(self, acct_id: str, limit=0) -> Iterable[Check]:
        pass

    def get_checks(
        self, acct_id: str, filters: Optional[Dict[str, Any]] = None, limit=0
    ) -> Iterable[Check]:
        pass

    def get_check_detail(
        self, check_id: str, with_notes=False, notes_limit=100
    ) -> Check:
        pass

    def suppress_check(
        self, check_id: str, suppressed_until: Optional[int], note="Copied from API"
    ):
        pass


class DefaultConformityAPI:
    def __init__(
        self, api_key: str, base_url: str, http: requests.Session = None
    ) -> None:
        self._api_key = api_key
        self._base_url = base_url.strip().rstrip("/")
        self.http = requests.Session() if http is None else http
        self._headers = {
            "Authorization": f"ApiKey {self._api_key}",
            "Content-Type": "application/vnd.api+json",
        }
        self._current_user: Optional[User] = None
        self._validate_api()
        self._organisation_external_id = ""

    def _err_details(self, resp: requests.Response) -> str:
        req = resp.request
        return f"""Request:
{req.method} {req.url}
Response:
{resp.status_code} {resp.reason}
{resp.text}"""

    def _raise_for_status(self, resp: requests.Response):
        try:
            resp.raise_for_status()
        except requests.exceptions.HTTPError as e:
            err_resp: requests.Response = e.response
            status_code = err_resp.status_code
            details = self._err_details(resp=err_resp)
            msg = str(e)
            if status_code == 401:
                raise ConformityUnauthorizedError(msg, details=details) from e
            elif status_code == 403:
                raise ConformityForbiddenError(msg, details=details) from e
            elif status_code == 404:
                raise ConformityResourceNotFoundError(msg, details=details) from e
            elif 400 <= status_code < 500:
                raise ConformityClientError(msg, details=details)
            elif 500 <= status_code < 600:
                raise ConformityServerInternalError(msg, details=details) from e
            else:
                raise ConformityOtherError(msg, details=details) from e

    def _get_request(self, url, params=None):
        return self._exec_request("GET", url, params=params)

    def _post_request(self, url, data):
        return self._exec_request("POST", url, data=data)

    def _delete_request(self, url):
        return self._exec_request("DELETE", url)

    def _patch_request(self, url, data):
        return self._exec_request("PATCH", url, data=data)

    def _exec_request(self, method, url, params=None, data=None):
        json_data = json.dumps(data, indent=4) if data else None
        try:
            resp = self.http.request(
                method=method,
                url=url,
                params=params,
                data=json_data,
                headers=self._headers,
            )
        except requests.exceptions.ConnectTimeout as e:
            raise ConformityConnectionError(
                f"Cannot connect to {self._base_url}"
            ) from e
        else:
            self._raise_for_status(resp)

            return resp.json()

    def _validate_api(self):
        try:
            user = self.current_user()
        except ConformityForbiddenError as e:
            raise ConformityForbiddenError(
                f"API Key does not have permission for: {self._base_url}"
            ) from e
        else:
            if user.role != User.ROLE_ADMIN:
                raise ConformityForbiddenError(
                    f"Insufficient permisison. API Key must have an ADMIN privilege for: {self._base_url}"
                )

    def current_user(self) -> User:
        if not self._current_user:
            res = self._get_request(f"{self._base_url}/users/whoami")
            user = self._user_dict_to_user_obj(res["data"])
            self._current_user = user
        return self._current_user

    def delete_account(self, acct_id: str) -> dict:
        res = self._delete_request(f"{self._base_url}/accounts/{acct_id}")
        return res

    def list_accounts(self) -> List[Account]:
        res = self._get_request(f"{self._base_url}/accounts")
        return [Account(acct_data=acct_data) for acct_data in res["data"]]

    def get_organisation_external_id(self) -> str:
        if not self._organisation_external_id:
            res = self._get_request(f"{self._base_url}/organisation/external-id")
            self._organisation_external_id = res["data"]["id"]
        return self._organisation_external_id

    def get_account_access_configuration(self, acct_id) -> dict:
        res = self._get_request(f"{self._base_url}/accounts/{acct_id}/access")
        return res["attributes"]["configuration"]

    @backoff.on_exception(
        wait_gen=backoff.expo,
        factor=2,
        exception=ConformityClientError,
        max_time=30,
        jitter=None,
    )
    def add_aws_account(
        self,
        name: str,
        environment: str,
        role_arn: str,
        external_id: str,
        subscription_type="advanced",
    ) -> dict:

        res = self._post_request(
            url=f"{self._base_url}/accounts",
            data={
                "data": {
                    "attributes": {
                        "name": name,
                        "environment": environment,
                        "access": {
                            "keys": {"roleArn": role_arn, "externalId": external_id}
                        },
                        "subscriptionType": subscription_type,
                    },
                }
            },
        )

        return res["data"]

    def add_azure_subscription(
        self,
        name: str,
        environment: str,
        subscription_id: str,
        active_directory_id: str,
    ) -> dict:

        res = self._post_request(
            url=f"{self._base_url}/accounts/azure",
            data={
                "data": {
                    "attributes": {
                        "name": name,
                        "environment": environment,
                        "access": {
                            "subscriptionId": subscription_id,
                            "activeDirectoryId": active_directory_id,
                        },
                    },
                }
            },
        )

        return res["data"]

    def update_account(
        self, acct_id: str, name: str, environment: str, tags: List[str]
    ):
        res = self._patch_request(
            url=f"{self._base_url}/accounts/{acct_id}",
            data={
                "data": {
                    "attributes": {
                        "name": name,
                        "environment": environment,
                        "tags": tags,
                    },
                },
            },
        )
        return res

    def get_account_bot_settings(self, acct_id: str) -> dict:
        res = self._get_request(f"{self._base_url}/accounts/{acct_id}/settings/bot")
        return res["data"]["attributes"]["settings"]["bot"]

    def update_account_bot_settings(self, acct_id: str, settings: dict):
        res = self._patch_request(
            url=f"{self._base_url}/accounts/{acct_id}/settings/bot",
            data={
                "data": {"attributes": {"settings": {"bot": settings}}},
            },
        )
        return res

    def get_account_details(self, acct_id: str) -> AccountDetails:
        res = self._get_request(f"{self._base_url}/accounts/{acct_id}")
        return AccountDetails(acct_data=res["data"])

    def get_account_rules_settings(self, acct_id: str) -> list:
        try:
            res = self._get_request(
                f"{self._base_url}/accounts/{acct_id}/settings/rules"
            )
            return res["data"]["attributes"]["settings"]["rules"]
        except ConformityResourceNotFoundError:
            print("ResourceNotFoundError!!! So returning empty list instead :-)")
            return []
        except Exception as e:
            raise e

    def update_account_rule_settings(
        self, acct_id: str, settings: dict, note: str = "Copied from API"
    ):
        res = self._patch_request(
            url=f"{self._base_url}/accounts/{acct_id}/settings/rules",
            data={
                "data": {"attributes": {"note": note, "ruleSettings": settings}},
            },
        )
        return res

    def get_account_rule_setting(
        self, acct_id: str, rule_id: str, with_notes=False
    ) -> Rule:
        res = self._get_request(
            f"{self._base_url}/accounts/{acct_id}/settings/rules/{rule_id}",
            params={"notes": "true" if with_notes else "false"},
        )
        # print(json.dumps(res, indent=4))
        setting = res["data"]["attributes"]["settings"]["rules"][0]
        notes: List[Note] = []
        if with_notes:
            meta = res["meta"]
            ns = meta.get("notes")
            if ns is None:
                ns = meta["deprecation"]["notes"]
            notes = [
                Note(
                    note=n["note"],
                    created_by=n["createdBy"],
                    created_ts=n["createdDate"],
                )
                for n in ns
            ]
        return Rule(setting=setting, notes=notes)

    def update_account_rule_setting(
        self, acct_id: str, rule_id: str, setting: dict, note: str = "Copied from API"
    ):
        res = self._patch_request(
            url=f"{self._base_url}/accounts/{acct_id}/settings/rules/{rule_id}",
            data={
                "data": {"attributes": {"ruleSetting": setting, "note": note}},
            },
        )
        return res["data"]

    def get_group_details(self, group_id: str) -> dict:
        res = self._get_request(f"{self._base_url}/groups/{group_id}")
        return res["data"][0]

    def list_groups(self, include_group_types: List[str] = None) -> List[Group]:
        res = self._get_request(f"{self._base_url}/groups")
        if include_group_types is None:
            include_group_types = []
        groups = []
        for g in res["data"]:
            gattrib = g["attributes"]
            group_type = gattrib.get("group-type", Group.GROUP_TYPE_USER_DEFINED)
            if include_group_types and group_type not in include_group_types:
                continue
            group = Group(
                group_id=g["id"],
                name=gattrib["name"],
                tags=gattrib.get("tags"),
                group_type=group_type,
                cloud_type=gattrib.get("cloud-type"),
                cloud_data=gattrib.get("cloud-data"),
            )
            groups.append(group)
        return groups

    def create_group(self, name, tags=List[str]):
        res = self._post_request(
            url=f"{self._base_url}/groups",
            data={"data": {"attributes": {"name": name, "tags": tags}}},
        )
        return res["data"]

    def delete_group(self, group_id: str) -> dict:
        res = self._delete_request(f"{self._base_url}/groups/{group_id}")
        return res

    def get_organisation_id(self) -> str:
        res = self._get_request(f"{self._base_url}/users")
        return res["data"][0]["relationships"]["organisation"]["data"]["id"]

    def list_all_users(self) -> List[dict]:
        res = self._get_request(f"{self._base_url}/users")
        return res["data"]

    def _user_dict_to_user_obj(self, u: dict) -> User:
        user_attrib = u["attributes"]
        email: str = user_attrib.get("email", "")
        return User(
            user_id=u["id"],
            email=email,
            first_name=user_attrib.get("first-name", ""),
            last_name=user_attrib.get("last-name", ""),
            role=user_attrib["role"],
            mobile_number=user_attrib.get("mobile", ""),
            is_mobile_verified=user_attrib.get("mobile-verified", False),
            is_cloud_one_user=user_attrib.get("is-cloud-one-user", False),
        )

    def get_all_users(self) -> List[User]:
        res = self._get_request(f"{self._base_url}/users")
        users = []
        for u in res["data"]:
            user = self._user_dict_to_user_obj(u)
            if not user.email:  # skip users who does not have email, e.g. Api key user
                continue
            users.append(user)
        return users

    def get_user_details(self, user_id: str) -> dict:
        res = self._get_request(f"{self._base_url}/users/{user_id}")
        return res["data"]

    def invite_user(self, user: dict) -> List[dict]:
        attrib = user["attributes"]
        first_name = attrib["first-name"]
        last_name = attrib["last-name"]
        email = attrib["email"]
        role = attrib["role"]

        data = {
            "data": {
                "attributes": {
                    "firstName": first_name,
                    "lastName": last_name,
                    "email": email,
                    "role": role,
                }
            }
        }
        if role == "USER":
            data["data"]["attributes"]["accessList"] = user["relationships"][
                "accountAccessList"
            ]

        res = self._post_request(
            url=f"{self._base_url}/users",
            data=data,
        )
        return res["data"]

    def delete_communication_settings(self, com_setting_id: str) -> dict:
        res = self._delete_request(f"{self._base_url}/settings/{com_setting_id}")
        return res

    def get_communication_settings(self, acct_id: str) -> List[CommunicationSettings]:
        if acct_id:
            params = {"accountId": acct_id}
        else:
            params = {"includeParents": "true"}
        res = self._get_request(
            f"{self._base_url}/settings/communication", params=params
        )
        # return res["data"]
        settings: List[CommunicationSettings] = []
        for s in res["data"]:
            attrib = s["attributes"]
            settings.append(
                CommunicationSettings(
                    com_setting_id=s["id"],
                    channel=attrib["channel"],
                    enabled=attrib["enabled"],
                    filter=attrib.get("filter"),
                    configuration=attrib.get("configuration"),
                )
            )
        return settings

    def create_communication_settings(
        self, com_settings: Iterable[CommunicationSettings], acct_id: str, org_id: str
    ):
        # for cs in com_settings:
        #     print(cs)
        settings = []
        for cs in com_settings:
            if not cs.configuration:
                continue
            s: dict = {
                "type": "settings",
                "attributes": {
                    "type": "communication",
                    "enabled": cs.enabled,
                    "channel": cs.channel,
                    "filter": cs.filter,
                    "configuration": cs.configuration,
                },
                "relationships": {
                    "account": {
                        "data": None,
                    },
                    "organisation": {
                        "data": {
                            "type": "organisations",
                            "id": org_id,
                        }
                    },
                },
            }
            if acct_id:
                s["relationships"]["account"]["data"] = {
                    "type": "accounts",
                    "id": acct_id,
                }

            settings.append(s)

        res = self._post_request(
            url=f"{self._base_url}/settings/communication", data={"data": settings}
        )
        return res

    def create_azure_directory(
        self, name: str, directory_id: str, app_client_id: str, app_client_key: str
    ):
        res = self._post_request(
            url=f"{self._base_url}/azure/active-directories",
            data={
                "data": {
                    "attributes": {
                        "name": name,
                        "directoryId": directory_id,
                        "applicationId": app_client_id,
                        "applicationKey": app_client_key,
                    }
                }
            },
        )
        return res["data"]

    def _limit_reached(self, limit, total) -> bool:
        is_limited: bool = limit > 0
        limit_reached = is_limited and total >= limit
        # if limit_reached:
        #     print("Limit reached!")
        return limit_reached

    def _check_dict_to_check_obj(self, c: dict) -> Check:
        attrib: dict = c["attributes"]
        ns = attrib.get("notes", [])
        notes = [
            Note(
                note=n["note"],
                created_by=n["createdBy"],
                created_ts=n["created-date"],
            )
            for n in ns
        ]
        return Check(
            check_id=c["id"],
            acct_id=c["relationships"]["account"]["data"]["id"],
            rule_id=c["relationships"]["rule"]["data"]["id"],
            service=attrib["service"],
            region=attrib["region"],
            resource_name=attrib.get("resourceName", ""),
            resource=attrib.get("resource", ""),
            message=attrib["message"],
            suppressed=attrib.get("suppressed"),
            suppressed_until=attrib.get("suppressed-until"),
            notes=notes,
        )

    def get_checks(
        self, acct_id: str, filters: Optional[Dict[str, Any]] = None, limit=0
    ) -> Iterable[Check]:

        page_size_max = 100
        page_size = limit if (0 < limit < page_size_max) else page_size_max

        params = {
            "accountIds": acct_id,
            "page[size]": page_size,
        }
        if filters:
            for filter_name, filter_val in filters.items():
                params[f"filter[{filter_name}]"] = filter_val

        total_items = 0
        page_num = 0
        while True:
            params["page[number]"] = page_num
            res = self._get_request(
                f"{self._base_url}/checks",
                params=params,
            )
            data = res["data"]
            for c in data:
                yield self._check_dict_to_check_obj(c)
                total_items += 1
                if self._limit_reached(limit, total_items):
                    break

            meta = res["meta"]
            # print(meta)
            # print(f"total_items: {total_items}")
            if self._limit_reached(limit, total_items):
                break

            if total_items >= meta["total"]:
                break
            page_num += 1

    def get_suppressed_checks(self, acct_id: str, limit=0) -> Iterable[Check]:
        return self.get_checks(
            acct_id=acct_id,
            filters={"suppressed": True, "suppressedFilterMode": "v2"},
            limit=limit,
        )

    def suppress_check(
        self, check_id: str, suppressed_until: Optional[int], note="Copied from API"
    ):
        res = self._patch_request(
            url=f"{self._base_url}/checks/{quote(check_id, safe='')}",
            data={
                "data": {
                    "type": "checks",
                    "attributes": {
                        "suppressed": True,
                        "suppressed-until": suppressed_until,
                    },
                },
                "meta": {
                    "note": note,
                },
            },
        )
        return res["data"]

    def get_check_detail(
        self, check_id: str, with_notes=False, notes_limit=100
    ) -> Check:
        notes_limit = notes_limit if (0 < notes_limit < 100) else 100
        params = {"filter[notes]": "true" if with_notes else "false"}
        if with_notes:
            params["filter[notesLength]"] = notes_limit
        res = self._get_request(
            f"{self._base_url}/checks/{quote(check_id, safe='')}", params=params
        )
        return self._check_dict_to_check_obj(res["data"])

    def is_bot_scan_done(self, acct_id: str) -> bool:
        bot_status = self.get_account_details(acct_id=acct_id).bot_status
        return bot_status is None

    def get_custom_profiles(self) -> List[Profile]:
        res = self._get_request(f"{self._base_url}/profiles")
        profiles: List[Profile] = []
        for prof_data in res["data"]:
            settings = {"data": prof_data}
            profiles.append(Profile(settings=settings))
        return profiles

    def get_profile(self, profile_id: str, include_rule_settings=False) -> Profile:
        params = {"includes": "ruleSettings"} if include_rule_settings else None
        res = self._get_request(
            f"{self._base_url}/profiles/{profile_id}", params=params
        )
        return Profile(settings=res)

    def _get_org_profile_id(self) -> str:
        return f"organisation-{self.get_organisation_id()}"

    def get_organisation_profile(self, include_rule_settings=False) -> Profile:
        return self.get_profile(
            profile_id=self._get_org_profile_id(),
            include_rule_settings=include_rule_settings,
        )

    def update_organisation_profile(self, profile: Profile) -> Profile:
        profile.delete_meta()
        profile.delete_profile_id()
        profile_id = self._get_org_profile_id()
        profile.profile_id = profile_id
        res = self._patch_request(
            url=f"{self._base_url}/profiles/{profile_id}", data=profile.settings
        )
        return Profile(settings=res)

    @classmethod
    def create_empty_organisation_profile(
        cls, org_id: str, has_empty_included_field=True
    ) -> Profile:
        settings = {
            "meta": {},
            "data": {
                "type": "profiles",
                "id": f"organisation-{org_id}",
                "attributes": {
                    "name": "Organisational Profile",
                    "description": "Organisational Profile",
                },
                "relationships": {"ruleSettings": {"data": []}},
            },
        }
        if has_empty_included_field:
            settings["included"] = []
        return Profile(settings=settings)

    def reset_organisation_profile(self) -> dict:
        org_id = self.get_organisation_id()
        profile = self.create_empty_organisation_profile(
            org_id=org_id, has_empty_included_field=False
        )
        # print(json.dumps(profile.settings, indent=4))
        res = self._post_request(
            url=f"{self._base_url}/profiles", data=profile.settings
        )
        return res

    def create_new_profile(self, profile: Profile) -> Profile:
        profile.delete_meta()
        profile.delete_profile_id()
        res = self._post_request(
            url=f"{self._base_url}/profiles", data=profile.settings
        )
        return Profile(settings=res)

    def delete_profile(self, profile_id: str):
        res = self._delete_request(f"{self._base_url}/profiles/{profile_id}")
        # print(res)
        return res

    def _list_report_configs(self, params: dict = None) -> List[ReportConfig]:
        res = self._get_request(url=f"{self._base_url}/report-configs", params=params)
        return [ReportConfig(data=rdata) for rdata in res["data"]]

    def list_organisation_report_configs(self) -> List[ReportConfig]:
        return self._list_report_configs()

    def list_group_report_configs(self, group_id: str) -> List[ReportConfig]:
        return self._list_report_configs(params={"groupId": group_id})

    def list_account_report_configs(self, acct_id: str) -> List[ReportConfig]:
        return self._list_report_configs(params={"accountId": acct_id})

    def _create_report_config(
        self,
        report_conf: Dict[str, Any],
        acct_id: str = None,
        group_id: str = None,
    ) -> Dict[str, Any]:
        data: Dict[str, Any] = {"data": {"attributes": {"configuration": report_conf}}}
        if acct_id:
            data["data"]["attributes"]["accountId"] = acct_id
        elif group_id:
            data["data"]["attributes"]["groupId"] = group_id

        res = self._post_request(url=f"{self._base_url}/report-configs", data=data)
        return res["data"]

    def create_organisation_report_config(self, report_conf: Dict[str, Any]):
        return self._create_report_config(report_conf=report_conf)

    def create_group_report_config(self, report_conf: Dict[str, Any], group_id: str):
        return self._create_report_config(report_conf=report_conf, group_id=group_id)

    def create_account_report_config(self, report_conf: Dict[str, Any], acct_id: str):
        return self._create_report_config(report_conf=report_conf, acct_id=acct_id)

    def delete_report_config(self, report_conf_id: str):
        res = self._delete_request(f"{self._base_url}/report-configs/{report_conf_id}")
        return res


class ConformityAPIBaseDecorator:
    def __init__(self, api: ConformityAPI) -> None:
        self._api = api

    @property
    def api(self) -> ConformityAPI:
        return self._api

    def __getattr__(self, name):
        return getattr(self._api, name)


class LegacyConformityAPI(ConformityAPIBaseDecorator):
    def __init__(self, api: ConformityAPI) -> None:
        super().__init__(api)
        self._validate_api()

    def _validate_api(self):
        user = self.current_user()
        if user.is_cloud_one_user:
            raise ConformityError("Not a valid Legacy Conformity API URL")


class CloudOneConformityAPI(ConformityAPIBaseDecorator):
    def __init__(self, api: ConformityAPI) -> None:
        super().__init__(api)
        self._validate_api()

    def _validate_api(self):
        user = self.current_user()
        if not user.is_cloud_one_user:
            raise ConformityError("Not a valid Cloud One Conformity API URL")


class WorkaroundFixConformityAPI(ConformityAPIBaseDecorator):
    def __init__(self, api: ConformityAPI) -> None:
        super().__init__(api)
        self._already_tried_to_access_users = False
        self._successfully_accessed_users = False

    def get_all_users(self) -> List[User]:
        try:
            self._already_tried_to_access_users = True
            users = self.api.get_all_users()
            self._successfully_accessed_users = True
            return users
        except Exception as e:
            self._successfully_accessed_users = True
            raise e

    def _confirmed_not_a_permission_error(self) -> bool:
        # print("Confirming if not a permission error.")
        if not self._already_tried_to_access_users:
            try:
                # print("Trying to access users..")
                self.get_all_users()
                return True
            except Exception:
                return False
        return self._successfully_accessed_users

    def _return_empty_obj_or_raise_error(self, empty_obj, e: Exception):
        if self._confirmed_not_a_permission_error():
            # print("Not really a permission error")
            return empty_obj
        else:
            # print("It is indeed a permission error!")
            raise e

    def list_groups(self, include_group_types: List[str] = None) -> List[Group]:
        try:
            return self.api.list_groups(include_group_types=include_group_types)
        except ConformityForbiddenError as e:
            return self._return_empty_obj_or_raise_error([], e)

    def get_custom_profiles(self) -> List[Profile]:
        try:
            return self.api.get_custom_profiles()
        except ConformityForbiddenError as e:
            return self._return_empty_obj_or_raise_error([], e)

    def list_organisation_report_configs(self) -> List[ReportConfig]:
        try:
            return self.api.list_organisation_report_configs()
        except ConformityForbiddenError as e:
            return self._return_empty_obj_or_raise_error([], e)

    def get_organisation_profile(self, include_rule_settings=False) -> Profile:
        try:
            return self.api.get_organisation_profile(
                include_rule_settings=include_rule_settings
            )
        except ConformityForbiddenError as e:
            org_id = self.get_organisation_id()
            empty_profile = DefaultConformityAPI.create_empty_organisation_profile(
                org_id=org_id, has_empty_included_field=False
            )
            return self._return_empty_obj_or_raise_error(empty_profile, e)

    def list_accounts(self) -> List[Account]:
        accts = self.api.list_accounts()
        if accts is None:
            accts = []
        return accts

    def get_communication_settings(self, acct_id: str) -> List[CommunicationSettings]:
        com_settings = self.api.get_communication_settings(acct_id=acct_id)
        if com_settings is None:
            com_settings = []
        return com_settings
