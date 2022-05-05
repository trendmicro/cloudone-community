import json
from typing import Any, Dict, List, Optional, Union

from deepdiff import DeepDiff, DeepHash


class User:
    ROLE_ADMIN = "ADMIN"
    ROLE_USER = "USER"
    ROLE_READ_ONLY = "READ_ONLY"

    def __init__(
        self,
        user_id: str,
        email: str,
        first_name: str,
        last_name: str,
        role: str,
        mobile_number="",
        is_mobile_verified=False,
        is_cloud_one_user=False,
    ) -> None:
        self.user_id = user_id
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self.role = role
        self.mobile_number = mobile_number
        self.is_mobile_verified = is_mobile_verified
        self.is_cloud_one_user = is_cloud_one_user

    def __hash__(self) -> int:
        return hash(self.email)

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, User):
            return False
        other: User = other
        return self.email == other.email


class Group:

    GROUP_TYPE_MANAGED_GROUP = "MANAGED_GROUP"
    GROUP_TYPE_USER_DEFINED = ""

    def __init__(
        self,
        group_id: str,
        name: str,
        tags: List[str] = None,
        group_type: str = None,
        cloud_type: str = None,
        cloud_data: dict = None,
    ) -> None:
        self.group_id = group_id
        self.name = name
        self.tags = [] if tags is None else tags
        self._tags = tuple() if tags is None else tuple(sorted(tags))
        self.group_type = group_type
        self.cloud_type = cloud_type
        self.cloud_data = cloud_data

    def __hash__(self) -> int:
        return hash(self.name)

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Group):
            return False
        other: Group = other

        return self.name == other.name and self._tags == other._tags

    def __str__(self) -> str:
        fields = vars(self)
        del fields["_tags"]
        return json.dumps(fields, indent=4)


class CommunicationSettings:
    def __init__(
        self,
        com_setting_id: str,
        channel: str,
        enabled: bool,
        filter: dict,
        configuration: dict,
    ) -> None:
        self.com_setting_id = com_setting_id
        self.channel = channel
        self.enabled = enabled
        self.filter = filter
        self.configuration = configuration
        self._obj = {
            "channel": channel,
            "filter": filter,
            "configuration": configuration,
        }

    def __hash__(self) -> int:
        dh = DeepHash(self._obj)[self._obj]
        return hash(dh)

    def __eq__(self, other: Any) -> bool:
        diff = DeepDiff(self._obj, other._obj, ignore_order=True)
        return len(diff) == 0

    def __str__(self) -> str:
        fields = vars(self)
        del fields["_obj"]
        return json.dumps(fields, indent=4)


class Note:
    def __init__(self, note: str, created_by: str, created_ts: int) -> None:
        self.note = note
        self.created_by = created_by
        self.created_ts = created_ts

    def __str__(self) -> str:
        return json.dumps(vars(self), indent=4)


class Check:
    def __init__(
        self,
        check_id: str,
        acct_id: str,
        rule_id: str,
        service: str,
        region: str,
        resource: str,
        resource_name: str,
        message: str,
        suppressed: Optional[bool],
        suppressed_until: Optional[int],
        notes: List[Note] = None,
    ) -> None:
        self.check_id = check_id
        self.acct_id = acct_id
        self.rule_id = rule_id
        self.service = service
        self.region = region
        self.resource = resource
        self.resource_name = resource_name
        self.message = message
        self.suppressed = suppressed
        self.suppressed_until = suppressed_until
        self.notes = notes if notes is not None else []

    def __hash__(self) -> int:
        return hash(f"{self.rule_id}|{self.resource}")

    def __eq__(self, other: Any) -> bool:
        """
        The equality check is based from how the checkId is composed according
        to the Conformity's API documentation for Custom Check.
        checkID = ccc:accountId:ruleId:service:region:resourceId

        However, for migration purposes, accountId isn't used in this equality
        check because the source and the destination account when migrating
        suppressed check won't have the same accountId. To make sure the
        comparison is accurate, comparison must only be done between two checks
        that come from the same accounts (i.e. 2nd account is the account migrated
        from the 1st account)
        """
        if not isinstance(other, Check):
            return False
        other: Check = other

        return (
            self.rule_id == other.rule_id
            and self.service == other.service
            and self.region == other.region
            and self.resource == other.resource
        )

    def __str__(self) -> str:
        return json.dumps(vars(self), indent=4)


class Rule:
    def __init__(self, setting: dict, notes: List[Note] = None) -> None:
        self.setting = setting
        self.notes = notes if notes is not None else []
        self.rule_id = setting["id"]
        self.enabled = setting["enabled"]
        self.configured = setting.get("configured", False)

    def __hash__(self) -> int:
        return hash(self.rule_id)

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Rule):
            return False
        other: Rule = other
        return self.rule_id == other.rule_id


class Profile:
    def __init__(self, settings: dict) -> None:
        self.settings = settings
        # data = settings["data"]
        # attrib = data["attributes"]
        # self.profile_id = data.get("id", "")
        # self.name = attrib["name"]
        # self.description = attrib.get("description", "")

    @property
    def profile_id(self) -> str:
        return self.settings["data"].get("id", "")

    @profile_id.setter
    def profile_id(self, profile_id: str) -> None:
        self.settings["data"]["id"] = profile_id

    @property
    def name(self) -> str:
        return self.settings["data"]["attributes"]["name"]

    @name.setter
    def name(self, name: str) -> None:
        self.settings["data"]["attributes"]["name"] = name

    @property
    def description(self) -> str:
        return self.settings["data"]["attributes"].get("description", "")

    @description.setter
    def description(self, description: str) -> None:
        self.settings["data"]["attributes"]["description"] = description

    @property
    def included_rules(self) -> Union[List[dict], None]:
        return self.settings.get("included")

    def delete_profile_id(self) -> None:
        if "id" in self.settings["data"]:
            del self.settings["data"]["id"]

    def delete_meta(self) -> None:
        if "meta" in self.settings:
            del self.settings["meta"]

    def __hash__(self) -> int:
        return hash(self.name)

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Profile):
            return False
        other: Profile = other
        return self.name == other.name


class Account:
    def __init__(self, acct_data: Dict[str, Any]) -> None:
        self.data = acct_data

    @property
    def attributes(self) -> Dict[str, Any]:
        return self.data["attributes"]

    @property
    def account_id(self) -> str:
        return self.data["id"]

    @property
    def name(self) -> str:
        return self.attributes["name"]

    @property
    def environment(self) -> str:
        return self.attributes["environment"]

    @property
    def cloud_type(self) -> str:
        return self.attributes["cloud-type"]

    @property
    def tags(self) -> List[str]:
        return self.attributes.get("tags", [])

    @property
    def managed_group_id(self) -> str:
        return self.attributes["managed-group-id"]

    @property
    def security_package(self) -> bool:
        return self.attributes["security-package"]

    @property
    def organisation_id(self) -> str:
        return self.data["relationships"]["organisation"]["data"]["id"]


class AccountDetails(Account):
    def __init__(self, acct_data: Dict[str, Any]) -> None:
        super().__init__(acct_data=acct_data)

    @property
    def rules(self) -> List[Rule]:
        rsettings = self.attributes["settings"].get("rules")
        if not rsettings:
            return []
        return [Rule(setting=rule_setting) for rule_setting in rsettings]

    @property
    def bot_settings(self) -> Union[Dict[str, Any], None]:
        return self.attributes["settings"].get("bot")

    @property
    def bot_status(self) -> Union[str, None]:
        return self.attributes.get("bot-status")


class ReportConfig:
    def __init__(self, data: Dict[str, Any]) -> None:
        self.data = data

    @property
    def report_config_id(self) -> str:
        return self.data["id"]

    @property
    def enabled(self) -> bool:
        return self.data["attributes"]["enabled"]

    @property
    def configuration(self) -> Dict[str, Any]:
        return self.data["attributes"]["configuration"]

    @property
    def title(self) -> str:
        return self.configuration["title"]

    @property
    def description(self) -> str:
        return self.configuration["description"]

    @property
    def scheduled(self) -> bool:
        return self.configuration["scheduled"]

    @property
    def is_account_level(self) -> bool:
        return self.data["attributes"]["is-account-level"]

    @property
    def is_group_level(self) -> bool:
        return self.data["attributes"]["is-group-level"]

    @property
    def is_organisation_level(self) -> bool:
        return self.data["attributes"]["is-organisation-level"]

    def __hash__(self) -> int:
        return hash(self.title)

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, ReportConfig):
            return False
        other: ReportConfig = other
        return self.title == other.title
