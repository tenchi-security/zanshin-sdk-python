from copy import deepcopy
from datetime import datetime
from typing import Iterable, Optional, Union
from uuid import UUID

from zanshinsdk.common.enums import (
    AlertSeverity,
    AlertsOrderOpts,
    AlertState,
    Languages,
    SortOpts,
)


def validate_int(
    value, min_value=None, max_value=None, required=False
) -> Optional[int]:
    if value is None:
        if required:
            raise ValueError("required integer parameter missing")
        else:
            return value
    if not isinstance(value, int):
        raise TypeError(f"{repr(value)} is not an integer")
    if min_value and value < min_value:
        raise ValueError(f"{value} shouldn't be lower than {min_value}")
    if max_value and value > max_value:
        raise ValueError(f"{value} shouldn't be higher than {max_value}")
    return value


def validate_class(value, class_type):
    if not isinstance(value, class_type):
        raise TypeError(f"{repr(value)} is not an instance of {class_type.__name__}")
    return value


def validate_uuid(uuid: Union[UUID, str]) -> str:
    try:
        if isinstance(uuid, str):
            return str(UUID(uuid))

        if isinstance(uuid, UUID):
            return str(uuid)

        raise TypeError
    except (ValueError, TypeError) as ex:
        ex.args = (f"{repr(uuid)} is not a valid UUID",)
        raise ex


def validate_date(
    date: Union[str, datetime],
    date_formats: list = ["%Y-%m-%d", "%Y-%m-%dT%H:%M:%S.%fZ"],
    required: bool = False,
) -> Optional[datetime]:
    if date is None:
        if required:
            raise ValueError("required date parameter missing")
        return None

    if isinstance(date, datetime):
        return date

    if isinstance(date, str):
        for date_format in date_formats:
            try:
                return datetime.strptime(date, date_format)
            except ValueError:
                continue
        raise ValueError(
            f"{repr(date)} is not a valid date in the supported formats {date_formats}"
        )

    raise TypeError(f"{repr(date)} is not a valid date type")


def validate_base_alert_filter(
    body: dict,
    rules: Optional[Iterable[str]] = None,
    states: Optional[Iterable[AlertState]] = None,
    severities: Optional[Iterable[AlertSeverity]] = None,
    search: Optional[str] = None,
    lang: Optional[Languages] = None,
    opened_at_start: Optional[str] = None,
    opened_at_end: Optional[str] = None,
    resolved_at_start: Optional[str] = None,
    resolved_at_end: Optional[str] = None,
    created_at_start: Optional[str] = None,
    created_at_end: Optional[str] = None,
    updated_at_start: Optional[str] = None,
    updated_at_end: Optional[str] = None,
    order: Optional[AlertsOrderOpts] = None,
    sort: Optional[SortOpts] = None,
) -> dict:
    cloned_body = deepcopy(body)
    if rules:
        cloned_body["rules"] = [validate_class(rule, str) for rule in rules]
    if states:
        if isinstance(states, str) or isinstance(states, AlertState):
            states = [states]
        validate_class(states, Iterable)
        cloned_body["states"] = [
            validate_class(state, AlertState).value for state in states
        ]
    if severities:
        if isinstance(severities, str):
            severities = [severities]
        validate_class(severities, Iterable)
        cloned_body["severities"] = [
            validate_class(severity, AlertSeverity).value for severity in severities
        ]
    if lang:
        validate_class(lang, Languages)
        cloned_body["lang"] = lang.value
    if opened_at_start:
        cloned_body["openedAtStart"] = validate_date(opened_at_start).isoformat()
    if opened_at_end:
        cloned_body["openedAtEnd"] = validate_date(opened_at_end).isoformat()
    if resolved_at_start:
        cloned_body["resolvedAtStart"] = validate_date(resolved_at_start).isoformat()
    if resolved_at_end:
        cloned_body["resolvedAtEnd"] = validate_date(resolved_at_end).isoformat()
    if created_at_start:
        cloned_body["createdAtStart"] = validate_date(created_at_start).isoformat()
    if created_at_end:
        cloned_body["createdAtEnd"] = validate_date(created_at_end).isoformat()
    if updated_at_start:
        cloned_body["updatedAtStart"] = validate_date(updated_at_start).isoformat()
    if updated_at_end:
        cloned_body["updatedAtEnd"] = validate_date(updated_at_end).isoformat()
    if order:
        validate_class(order, AlertsOrderOpts)
        cloned_body["order"] = order.value
    if search:
        validate_class(search, str)
        cloned_body["search"] = search
    if sort:
        validate_class(sort, SortOpts)
        cloned_body["sort"] = sort.value
    return cloned_body
