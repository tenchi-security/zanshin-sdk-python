from __future__ import annotations

from enum import Enum
from typing import Union


class AlertState(str, Enum):
    OPEN = "OPEN"
    ACTIVE = "ACTIVE"
    IN_PROGRESS = "IN_PROGRESS"
    RISK_ACCEPTED = "RISK_ACCEPTED"
    MITIGATING_CONTROL = "MITIGATING_CONTROL"
    FALSE_POSITIVE = "FALSE_POSITIVE"
    CLOSED = "CLOSED"


class AlertSeverity(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"


class AlertsOrderOpts(str, Enum):
    SCAN_TARGET_ID = "scanTargetId"
    RESOURCE = "resource"
    RULE = "rule"
    SEVERITY = "severity"
    STATE = "state"
    CREATED_AT = "createdAt"
    UPDATED_AT = "updatedAt"


class SortOpts(str, Enum):
    ASC = "asc"
    DESC = "desc"


class ScanTargetKind(str, Enum):
    AWS = "AWS"
    GCP = "GCP"
    AZURE = "AZURE"
    HUAWEI = "HUAWEI"
    DOMAIN = "DOMAIN"
    ORACLE = "ORACLE"


class ScanTargetSchedule(str, Enum):
    ONE_HOUR = "1h"
    SIX_HOURS = "6h"
    TWELVE_HOURS = "12h"
    TWENTY_FOUR_HOURS = "24h"
    SEVEN_DAYS = "7d"

    def from_value(cls, schedule: Union[str, ScanTargetSchedule]) -> ScanTargetSchedule:
        if isinstance(schedule, cls):
            return schedule

        if isinstance(schedule, str):
            # try to match with current enum values
            try:
                return cls(schedule.lower())
            except ValueError:
                pass

            # failing that, let's convert cron format to the new one
            if schedule == "0 * * * *":
                return cls.ONE_HOUR
            elif schedule == "0 */6 * * *":
                return cls.SIX_HOURS
            elif schedule == "0 */12 * * *":
                return cls.TWELVE_HOURS
            elif schedule == "0 0 * * *":
                return cls.TWENTY_FOUR_HOURS
            elif schedule == "0 0 * * 0":
                return cls.SEVEN_DAYS
            else:
                raise ValueError(f"Unexpected schedule value '{schedule}'")
        else:
            raise TypeError(
                "schedule must be a string or an instance of ScanTargetSchedule"
            )


class ScanTargetAWS(dict):
    def __init__(self, account):
        dict.__init__(self, account=account)


class ScanTargetAZURE(dict):
    def __init__(self, application_id, subscription_id, directory_id, secret):
        dict.__init__(
            self,
            applicationId=application_id,
            subscriptionId=subscription_id,
            directoryId=directory_id,
            secret=secret,
        )


class Roles(str, Enum):
    ADMIN = "ADMIN"


class ScanTargetGCP(dict):
    def __init__(self, project_id):
        dict.__init__(self, projectId=project_id)


class ScanTargetHUAWEI(dict):
    def __init__(self, account_id):
        dict.__init__(self, accountId=account_id)


class ScanTargetDOMAIN(dict):
    def __init__(self, domain):
        dict.__init__(self, domain=domain)


class ScanTargetORACLE(dict):
    def __init__(self, compartment_id, region, tenancy_id, user_id, key_fingerprint):
        dict.__init__(
            self,
            compartment_id=compartment_id,
            region=region,
            tenancy_id=tenancy_id,
            user_id=user_id,
            key_fingerprint=key_fingerprint,
        )


class ScanTargetGroupCredentialListORACLE(dict):
    def __init__(self, region, tenancy_id, user_id, key_fingerprint):
        dict.__init__(
            self,
            region=region,
            tenancy_id=tenancy_id,
            user_id=user_id,
            key_fingerprint=key_fingerprint,
        )


class Languages(str, Enum):
    PT_BR = "pt-BR"
    EN_US = "en-US"
