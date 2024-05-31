from enum import Enum


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


class ScanTargetKind(str, Enum):
    AWS = "AWS"
    GCP = "GCP"
    AZURE = "AZURE"
    HUAWEI = "HUAWEI"
    DOMAIN = "DOMAIN"
    ORACLE = "ORACLE"
    MS365 = "MS365"
    GITHUB = "GITHUB"
    ZENDESK = "ZENDESK"
    GWORKSPACE = "GWORKSPACE"
    SLACK = "SLACK"
    BITBUCKET = "BITBUCKET"
    JIRA = "JIRA"
    GITLAB = "GITLAB"
    SALESFORCE = "SALESFORCE"


class ScanTargetGroupKind(str, Enum):
    ORACLE = "ORACLE"
    BITBUCKET = "BITBUCKET"
    GITLAB = "GITLAB"


class OAuthTargetKind(str, Enum):
    ZENDESK = "ZENDESK"
    GWORKSPACE = "GWORKSPACE"
    SLACK = "SLACK"
    BITBUCKET = "BITBUCKET"
    JIRA = "JIRA"
    GITLAB = "GITLAB"
    SALESFORCE = "SALESFORCE"


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


class Frequency(Enum):
    SIX_HOURS = "6h"
    TWELVE_HOURS = "12h"
    DAILY = "1d"
    WEEKLY = "7d"


class TimeOfDay(Enum):
    MORNING = "MORNING"
    AFTERNOON = "AFTERNOON"
    EVENING = "EVENING"
    NIGHT = "NIGHT"


class Day(Enum):
    SUNDAY = "SUNDAY"
    MONDAY = "MONDAY"
    TUESDAY = "TUESDAY"
    WEDNESDAY = "WEDNESDAY"
    THURSDAY = "THURSDAY"
    FRIDAY = "FRIDAY"
    SATURDAY = "SATURDAY"


class Roles(str, Enum):
    ADMIN = "ADMIN"


class Languages(str, Enum):
    PT_BR = "pt-BR"
    EN_US = "en-US"
