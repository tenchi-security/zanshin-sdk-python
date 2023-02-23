from math import ceil
from typing import Dict, Iterable, Iterator, Optional, Union
from uuid import UUID

from src.bin.client import Client, validate_class, validate_int, validate_uuid
from src.lib.models import (
    AlertSeverity,
    AlertsOrderOpts,
    AlertState,
    Languages,
    SortOpts,
)

###################################################
# Alerts
###################################################


def _get_alerts_page(
    organization_id: Union[UUID, str],
    scan_target_ids: Optional[Iterable[Union[UUID, str]]] = None,
    rule: Optional[str] = None,
    states: Optional[Iterable[AlertState]] = None,
    severities: Optional[Iterable[AlertSeverity]] = None,
    page: int = 1,
    page_size: int = 100,
    language: Optional[Languages] = None,
    created_at_start: Optional[str] = None,
    created_at_end: Optional[str] = None,
    updated_at_start: Optional[str] = None,
    updated_at_end: Optional[str] = None,
    search: Optional[str] = None,
    order: Optional[AlertsOrderOpts] = None,
    sort: Optional[SortOpts] = None,
) -> Dict:
    """
    Internal method to retrieve a single page of alerts from an organization
    :param organization_id: the ID of the organization
    :param scan_target_ids: optional list of scan target IDs to list alerts from, defaults to all
    :param rule: to filter alerts from (rule), not passing the field will fetch all
    :param states: optional list of states to filter returned alerts, defaults to all
    :param severities: optional list of severities to filter returned alerts, defaults to all
    :param page: page number, starting from 1
    :param page_size: page size of alerts
    :param language: language the rule will be returned
    :param created_at_start: Search alerts by creation date - greater or equals than
    :param created_at_end: Search alerts by creation date - less or equals than
    :param updated_at_start: Search alerts by update date - greater or equals than
    :param updated_at_end: Search alerts by update date - less or equals than
    :param order: Sort order to use (ascending or descending)
    :param sort: Which field to sort on
    :return: an iterator over the JSON decoded alerts
    :return:
    """
    validate_int(page, min_value=1, required=True)
    validate_int(page_size, min_value=1, required=True)
    body = {
        "organizationId": validate_uuid(organization_id),
        "page": page,
        "pageSize": page_size,
    }
    if search:
        validate_class(search, str)
        body["search"] = search
    if order:
        validate_class(order, AlertsOrderOpts)
        body["order"] = order.value
    if sort:
        validate_class(sort, SortOpts)
        body["sort"] = sort.value
    if scan_target_ids:
        if isinstance(scan_target_ids, str):
            scan_target_ids = [scan_target_ids]
        validate_class(scan_target_ids, Iterable)
        body["scanTargetIds"] = [validate_uuid(x) for x in scan_target_ids]
    if rule:
        body["rule"] = rule
    if states:
        if isinstance(states, str) or isinstance(states, AlertState):
            states = [states]
        validate_class(states, Iterable)
        body["states"] = [validate_class(x, AlertState).value for x in states]
    if severities:
        if isinstance(severities, str):
            severities = [severities]
        validate_class(severities, Iterable)
        body["severities"] = [
            validate_class(x, AlertSeverity).value for x in severities
        ]
    if language:
        validate_class(language, Languages)
        body["lang"] = language.value
    # TODO: Validate these dates.
    if created_at_start:
        body["createdAtStart"] = created_at_start
    if created_at_end:
        body["createdAtEnd"] = created_at_end
    if updated_at_start:
        body["updatedAtStart"] = updated_at_start
    if updated_at_end:
        body["updatedAtEnd"] = updated_at_end

    return t._request("POST", "/alerts", body=body).json()


def iter_alerts(
    organization_id: Union[UUID, str],
    scan_target_ids: Optional[Iterable[Union[UUID, str]]] = None,
    rule: Optional[str] = None,
    states: Optional[Iterable[AlertState]] = None,
    severities: Optional[Iterable[AlertSeverity]] = None,
    page_size: int = 100,
    language: Optional[Languages] = None,
    created_at_start: Optional[str] = None,
    created_at_end: Optional[str] = None,
    updated_at_start: Optional[str] = None,
    updated_at_end: Optional[str] = None,
    search: Optional[str] = None,
    order: Optional[AlertsOrderOpts] = None,
    sort: Optional[SortOpts] = None,
) -> Iterator[Dict]:
    """
    Iterates over the alerts of an organization by loading them, transparently paginating on the API
        <https://api.zanshin.tenchisecurity.com/#operation/listAllAlert>
    :param organization_id: the ID of the organization
    :param scan_target_ids: optional list of scan target IDs to list alerts from, defaults to all
    :param rule: to filter alerts from (rule), not passing the field will fetch all
    :param states: optional list of states to filter returned alerts, defaults to all
    :param severities: optional list of severities to filter returned alerts, defaults to all
    :param page_size: the number of alerts to load from the API at a time
    :param language: language the rule will be returned. Ignored when historical is enabled
    :param created_at_start: Search alerts by creation date - greater or equals than
    :param created_at_end: Search alerts by creation date - less or equals than
    :param updated_at_start: Search alerts by update date - greater or equals than
    :param updated_at_end: Search alerts by update date - less or equals than
    :param search: Search string to find in alerts
    :param order: Sort order to use (ascending or descending)
    :param sort: Which field to sort on
    :return: an iterator over the JSON decoded alerts
    """
    page = _get_alerts_page(
        organization_id,
        scan_target_ids,
        rule,
        states,
        severities,
        page=1,
        page_size=page_size,
        language=language,
        created_at_start=created_at_start,
        created_at_end=created_at_end,
        updated_at_start=updated_at_start,
        updated_at_end=updated_at_end,
        search=search,
        order=order,
        sort=sort,
    )
    yield from page.get("data", [])
    for page_number in range(2, int(ceil(page.get("total", 0) / float(page_size))) + 1):
        page = _get_alerts_page(
            organization_id,
            scan_target_ids,
            rule,
            states,
            severities,
            page=page_number,
            page_size=page_size,
            language=language,
            created_at_start=created_at_start,
            created_at_end=created_at_end,
            updated_at_start=updated_at_start,
            updated_at_end=updated_at_end,
            search=search,
            order=order,
            sort=sort,
        )
        yield from page.get("data", [])


def _get_following_alerts_page(
    organization_id: Union[UUID, str],
    following_ids: Optional[Iterable[Union[UUID, str]]] = None,
    rule: Optional[str] = None,
    states: Optional[Iterable[AlertState]] = None,
    severities: Optional[Iterable[AlertSeverity]] = None,
    page: int = 1,
    page_size: int = 100,
    language: Optional[Languages] = None,
    created_at_start: Optional[str] = None,
    created_at_end: Optional[str] = None,
    updated_at_start: Optional[str] = None,
    updated_at_end: Optional[str] = None,
    search: Optional[str] = None,
    order: Optional[AlertsOrderOpts] = None,
    sort: Optional[SortOpts] = None,
) -> Dict:
    """
    Internal method to retrieve a single page of alerts from organizations being followed
    :param organization_id: the ID of the organization
    :param following_ids: optional list of scan target IDs to list alerts from, defaults to all
    :param rule: to filter alerts from (rule), not passing the field will fetch all
    :param states: optional list of states to filter returned alerts, defaults to all
    :param severities: optional list of severities to filter returned alerts, defaults to all
    :param page: page number, starting from 1
    :param page_size: page size of alerts
    :param language: language the rule will be returned
    :param created_at_start: Search alerts by creation date - greater or equals than
    :param created_at_end: Search alerts by creation date - less or equals than
    :param updated_at_start: Search alerts by update date - greater or equals than
    :param updated_at_end: Search alerts by update date - less or equals than
    :param search: Search string to find in alerts
    :param order: Sort order to use (ascending or descending)
    :param sort: Which field to sort on
    :return: the decoded JSON response from the API
    """
    validate_int(page, min_value=1, required=True)
    validate_int(page_size, min_value=1, required=True)
    body = {
        "organizationId": validate_uuid(organization_id),
        "page": page,
        "pageSize": page_size,
    }

    if search:
        validate_class(search, str)
        body["search"] = search
    if order:
        validate_class(order, AlertsOrderOpts)
        body["order"] = order.value
    if sort:
        validate_class(sort, SortOpts)
        body["sort"] = sort.value
    if following_ids:
        if isinstance(following_ids, str):
            following_ids = [following_ids]
        validate_class(following_ids, Iterable)
        body["followingIds"] = [validate_uuid(x) for x in following_ids]
    if rule:
        body["rule"] = rule
    if states:
        if isinstance(states, str) or isinstance(states, AlertState):
            states = [states]
        validate_class(states, Iterable)
        body["states"] = [validate_class(x, AlertState).value for x in states]
    if severities:
        if isinstance(severities, str):
            severities = [severities]
        validate_class(severities, Iterable)
        body["severities"] = [
            validate_class(x, AlertSeverity).value for x in severities
        ]
    if language:
        validate_class(language, Languages)
        body["lang"] = language.value
    if created_at_start:
        body["CreatedAtStart"] = created_at_start
    if created_at_end:
        body["CreatedAtEnd"] = created_at_end
    if updated_at_start:
        body["UpdatedAtStart"] = updated_at_start
    if updated_at_end:
        body["UpdatedAtEnd"] = updated_at_end

    return Client._request("POST", "/alerts/following", body=body).json()


def iter_following_alerts(
    organization_id: Union[UUID, str],
    following_ids: Optional[Iterable[Union[UUID, str]]] = None,
    rule: Optional[str] = None,
    states: Optional[Iterable[AlertState]] = None,
    severities: Optional[Iterable[AlertSeverity]] = None,
    page_size: int = 100,
    language: Optional[Languages] = None,
    created_at_start: Optional[str] = None,
    created_at_end: Optional[str] = None,
    updated_at_start: Optional[str] = None,
    updated_at_end: Optional[str] = None,
    search: Optional[str] = None,
    order: Optional[AlertsOrderOpts] = None,
    sort: Optional[SortOpts] = None,
) -> Iterator[Dict]:
    """
    Iterates over the following alerts froms organizations being followed by transparently paginating on the API.
        <https://api.zanshin.tenchisecurity.com/#operation/listFollowingAlerts>
    :param organization_id: the ID of the organization
    :param following_ids: optional list of IDs of organizations you are following to list alerts from, defaults to
               all
    :param rule: to filter alerts from (rule), not passing the field will fetch all
    :param states: optional list of states to filter returned alerts, defaults to all
    :param severities: optional list of severities to filter returned alerts, defaults to all
    :param page_size: the number of alerts to load from the API at a time
    :param language: language the rule will be returned
    :param created_at_start: Search alerts by creation date - greater or equals than
    :param created_at_end: Search alerts by creation date - less or equals than
    :param updated_at_start: Search alerts by update date - greater or equals than
    :param updated_at_end: Search alerts by update date - less or equals than
    :param search: Search string to find in alerts
    :param order: Sort order to use (ascending or descending)
    :param sort: Which field to sort on
    :return: an iterator over the JSON decoded alerts
    """

    page = _get_following_alerts_page(
        organization_id,
        following_ids,
        rule,
        states,
        severities,
        page=1,
        page_size=page_size,
        language=language,
        created_at_start=created_at_start,
        created_at_end=created_at_end,
        updated_at_start=updated_at_start,
        updated_at_end=updated_at_end,
        search=search,
        order=order,
        sort=sort,
    )
    yield from page.get("data", [])
    for page_number in range(2, int(ceil(page.get("total", 0) / float(page_size))) + 1):
        page = _get_following_alerts_page(
            organization_id,
            following_ids,
            rule,
            states,
            severities,
            page=page_number,
            page_size=page_size,
            language=language,
            created_at_start=created_at_start,
            created_at_end=created_at_end,
            updated_at_start=updated_at_start,
            updated_at_end=updated_at_end,
            search=search,
            order=order,
            sort=sort,
        )
        yield from page.get("data", [])


def _get_alerts_history_page(
    organization_id: Union[UUID, str],
    scan_target_ids: Optional[Iterable[Union[UUID, str]]] = None,
    page_size: int = 100,
    language: Optional[Iterable[Languages]] = None,
    cursor: Optional[str] = None,
) -> Dict:
    """
    Internal method to retrieve a single page of alerts history from an organization
    :param organization_id: the ID of the organization
    :param scan_target_ids: optional list of scan target IDs to list alerts from, defaults to all
    :param page_size: page size of alerts
    :param language: language the rule will be returned
    :param cursor: Alert Cursor of the last alert consumed, when this value is passed, subsequent alert histories
           will be returned.
    :return: an iterator over the JSON decoded alerts
    :return:
    """
    validate_int(page_size, min_value=1, required=True)
    body = {"organizationId": validate_uuid(organization_id), "pageSize": page_size}

    if scan_target_ids:
        if isinstance(scan_target_ids, str):
            scan_target_ids = [scan_target_ids]
        validate_class(scan_target_ids, Iterable)
        body["scanTargetIds"] = [validate_uuid(x) for x in scan_target_ids]
    if language:
        validate_class(language, Languages)
        body["lang"] = language.value
    if cursor:
        body["cursor"] = cursor

    return Client._request("POST", "/alerts/history", body=body).json()


def iter_alerts_history(
    organization_id: Union[UUID, str],
    scan_target_ids: Optional[Iterable[Union[UUID, str]]] = None,
    page_size: int = 100,
    language: Optional[Languages] = None,
    cursor: Optional[str] = None,
) -> Iterator[Dict]:
    """
    Iterates over the alert's history of an organization by loading them, transparently paginating on the API.
        <https://api.zanshin.tenchisecurity.com/#operation/listAllAlertsHistory>
    :param organization_id: the ID of the organization
    :param scan_target_ids: optional list of scan target IDs to list alerts from, defaults to all
    :param page_size: the number of alerts to load from the API at a time
    :param language: language the rule will be returned.
    :param cursor: Alert Cursor of the last alert consumed, when this value is passed, subsequent alert histories
           will be returned.
    :return: an iterator over the JSON decoded alerts
    """

    page = _get_alerts_history_page(
        organization_id,
        scan_target_ids,
        page_size=page_size,
        language=language,
        cursor=cursor,
    )
    data = page.get("data", [])
    yield from data

    while len(data) > 0:
        cursor = data[len(data) - 1]["cursor"]
        page = _get_alerts_history_page(
            organization_id,
            scan_target_ids,
            page_size=page_size,
            language=language,
            cursor=cursor,
        )
        data = page.get("data", [])
        yield from data


def _get_alerts_following_history_page(
    organization_id: Union[UUID, str],
    following_ids: Optional[Iterable[Union[UUID, str]]] = None,
    page_size: int = 100,
    language: Optional[Languages] = None,
    cursor: Optional[str] = None,
) -> Dict:
    """
    Internal method to retrieve a single page of alerts history from an organization
    :param organization_id: the ID of the organization
    :param following_ids: optional list of IDs of organizations you are following to list alerts from, defaults to
               all
    :param page_size: page size of alerts
    :param language: language the rule will be returned
    :param cursor: Alert Cursor of the last alert consumed, when this value is passed, subsequent alert histories
           will be returned.
    :return: an iterator over the JSON decoded alerts
    :return:
    """
    validate_int(page_size, min_value=1, required=True)
    body = {"organizationId": validate_uuid(organization_id), "pageSize": page_size}

    if following_ids:
        if isinstance(following_ids, str):
            following_ids = [following_ids]
        validate_class(following_ids, Iterable)
        body["followingIds"] = [validate_uuid(x) for x in following_ids]
    if language:
        validate_class(language, Languages)
        body["lang"] = language.value
    if cursor:
        body["cursor"] = cursor

    return Client._request("POST", "/alerts/history/following", body=body).json()


def iter_alerts_following_history(
    organization_id: Union[UUID, str],
    following_ids: Optional[Iterable[Union[UUID, str]]] = None,
    page_size: int = 100,
    language: Optional[Languages] = None,
    cursor: Optional[str] = None,
) -> Iterator[Dict]:
    """
    Iterates over the alert's history of an organization by loading them, transparently paginating on the API
        <https://api.zanshin.tenchisecurity.com/#operation/listAllAlertsHistoryFollowing>
    :param organization_id: the ID of the organization
    :param following_ids: optional list of IDs of organizations you are following to list alerts from, defaults to
               all
    :param page_size: the number of alerts to load from the API at a time
    :param language: language the rule will be returned. Ignored when historical is enabled
    :param cursor: Alert Cursor of the last alert consumed, when this value is passed, subsequent alert histories
           will be returned
    :return: an iterator over the JSON decoded alerts
    """
    page = _get_alerts_following_history_page(
        organization_id,
        following_ids,
        page_size=page_size,
        language=language,
        cursor=cursor,
    )
    data = page.get("data", [])
    yield from data

    while len(data) > 0:
        cursor = data[len(data) - 1]["cursor"]
        page = _get_alerts_following_history_page(
            organization_id,
            following_ids,
            page_size=page_size,
            language=language,
            cursor=cursor,
        )
        data = page.get("data", [])
        yield from data


def _get_grouped_alerts_page(
    organization_id: Union[UUID, str],
    scan_target_ids: Optional[Iterable[Union[UUID, str]]] = None,
    states: Optional[Iterable[AlertState]] = None,
    severities: Optional[Iterable[AlertSeverity]] = None,
    page: int = 1,
    page_size: int = 100,
    language: Optional[Languages] = None,
    search: Optional[str] = None,
    order: Optional[AlertsOrderOpts] = None,
    sort: Optional[SortOpts] = None,
) -> Dict:
    """
    Internal method to retrieve a single page of alerts from an organization
    :param organization_id: the ID of the organization
    :param scan_target_ids: optional list of scan target IDs to list alerts from, defaults to all
    :param states: optional list of states to filter returned alerts, defaults to all
    :param severities: optional list of severities to filter returned alerts, defaults to all
    :param page: page number, starting from 1
    :param page_size: page size of alerts
    :param language: language to use for the returned rules
    :param search: Search string to find in alerts
    :param order: Sort order to use (ascending or descending)
    :param sort: Which field to sort on

    :return:
    """
    validate_int(page, min_value=1, required=True)
    validate_int(page_size, min_value=1, required=True)
    body = {
        "organizationId": validate_uuid(organization_id),
        "page": page,
        "pageSize": page_size,
    }
    if language:
        validate_class(language, Languages)
        body["lang"] = language.value
    if search:
        validate_class(search, str)
        body["search"] = search
    if order:
        validate_class(order, AlertsOrderOpts)
        body["order"] = order.value
    if sort:
        validate_class(sort, SortOpts)
        body["sort"] = sort.value
    if scan_target_ids:
        if isinstance(scan_target_ids, str):
            scan_target_ids = [scan_target_ids]
        validate_class(scan_target_ids, Iterable)
        body["scanTargetIds"] = [validate_uuid(x) for x in scan_target_ids]
    if states:
        if isinstance(states, str) or isinstance(states, AlertState):
            states = [states]
        validate_class(states, Iterable)
        body["states"] = [validate_class(x, AlertState).value for x in states]
    if severities:
        if isinstance(severities, str):
            severities = [severities]
        validate_class(severities, Iterable)
        body["severities"] = [
            validate_class(x, AlertSeverity).value for x in severities
        ]
    return Client._request("POST", "/alerts/rules", body=body).json()


def iter_grouped_alerts(
    organization_id: Union[UUID, str],
    scan_target_ids: Optional[Iterable[Union[UUID, str]]] = None,
    states: Optional[Iterable[AlertState]] = None,
    severities: Optional[Iterable[AlertSeverity]] = None,
    page_size: int = 100,
    language: Optional[Languages] = None,
    search: Optional[str] = None,
    order: Optional[AlertsOrderOpts] = None,
    sort: Optional[SortOpts] = None,
) -> Iterator[Dict]:
    """
    Iterates over the grouped alerts of an organization by loading them, transparently paginating on the API.
        <https://api.zanshin.tenchisecurity.com/#operation/listAllAlertRules>
    :param organization_id: the ID of the organization
    :param scan_target_ids: optional list of scan target IDs to list alerts from, defaults to all
    :param states: optional list of states to filter returned alerts, defaults to all
    :param severities: optional list of severities to filter returned alerts, defaults to all
    :param page_size: the number of alerts to load from the API at a time
    :param language: language to use for the returned rules
    :param search: Search string to find in alerts
    :param order: Sort order to use (ascending or descending)
    :param sort: Which field to sort on

    :return: an iterator over the JSON decoded alerts
    """
    page = _get_grouped_alerts_page(
        organization_id,
        scan_target_ids,
        states,
        severities,
        page=1,
        page_size=page_size,
        language=language,
        search=search,
        order=order,
        sort=sort,
    )
    yield from page.get("data", [])
    for page_number in range(2, int(ceil(page.get("total", 0) / float(page_size))) + 1):
        page = _get_grouped_alerts_page(
            organization_id,
            scan_target_ids,
            states,
            severities,
            page=page_number,
            page_size=page_size,
            language=language,
            search=search,
            order=order,
            sort=sort,
        )
        yield from page.get("data", [])


def _get_grouped_following_alerts_page(
    organization_id: Union[UUID, str],
    following_ids: Optional[Iterable[Union[UUID, str]]] = None,
    states: Optional[Iterable[AlertState]] = None,
    severities: Optional[Iterable[AlertSeverity]] = None,
    page: int = 1,
    page_size: int = 100,
    language: Optional[Languages] = None,
    search: Optional[str] = None,
    order: Optional[AlertsOrderOpts] = None,
    sort: Optional[SortOpts] = None,
) -> Dict:
    """
    Internal method to retrieve a single page of alerts from organizations being followed
    :param organization_id: the ID of the organization
    :param following_ids: optional list of scan target IDs to list alerts from, defaults to all
    :param states: optional list of states to filter returned alerts, defaults to all
    :param severities: optional list of severities to filter returned alerts, defaults to all
    :param page: page number, starting from 1
    :param page_size: page size of alerts
    :param language: language to use for the returned rules
    :param search: Search string to find in alerts
    :param order: Sort order to use (ascending or descending)
    :param sort: Which field to sort on
    :return: the decoded JSON response from the API
    """
    validate_int(page, min_value=1, required=True)
    validate_int(page_size, min_value=1, required=True)
    body = {
        "organizationId": validate_uuid(organization_id),
        "page": page,
        "pageSize": page_size,
    }
    if language:
        validate_class(language, Languages)
        body["lang"] = language.value
    if search:
        validate_class(search, str)
        body["search"] = search
    if order:
        validate_class(order, AlertsOrderOpts)
        body["order"] = order.value
    if sort:
        validate_class(sort, SortOpts)
        body["sort"] = sort.value
    if following_ids:
        if isinstance(following_ids, str):
            following_ids = [following_ids]
        validate_class(following_ids, Iterable)
        body["followingIds"] = [validate_uuid(x) for x in following_ids]
    if states:
        if isinstance(states, str) or isinstance(states, AlertState):
            states = [states]
        validate_class(states, Iterable)
        body["states"] = [validate_class(x, AlertState).value for x in states]
    if severities:
        if isinstance(severities, str):
            severities = [severities]
        validate_class(severities, Iterable)
        body["severities"] = [
            validate_class(x, AlertSeverity).value for x in severities
        ]

    return Client._request("POST", "/alerts/rules/following", body=body).json()


def iter_grouped_following_alerts(
    organization_id: Union[UUID, str],
    following_ids: Optional[Iterable[Union[UUID, str]]] = None,
    states: Optional[Iterable[AlertState]] = None,
    severities: Optional[Iterable[AlertSeverity]] = None,
    page_size: int = 100,
    language: Optional[Languages] = None,
    search: Optional[str] = None,
    order: Optional[AlertsOrderOpts] = None,
    sort: Optional[SortOpts] = None,
) -> Iterator[Dict]:
    """
    Iterates over the grouped following alerts froms organizations being followed by transparently paginating on the
        API.
        <https://api.zanshin.tenchisecurity.com/#operation/listAllAlertRulesFollowing>
    :param organization_id: the ID of the organization
    :param following_ids: optional list of IDs of organizations you are following to list alerts from, defaults to
               all
    :param states: optional list of states to filter returned alerts, defaults to all
    :param severities: optional list of severities to filter returned alerts, defaults to all
    :param page_size: the number of alerts to load from the API at a time
    :param language: language to use for the returned rules
    :param search: Search string to find in alerts
    :param order: Sort order to use (ascending or descending)
    :param sort: Which field to sort on
    :return: an iterator over the JSON decoded alerts
    """

    page = _get_grouped_following_alerts_page(
        organization_id,
        following_ids,
        states,
        severities,
        page=1,
        page_size=page_size,
        language=language,
        search=search,
        order=order,
        sort=sort,
    )
    yield from page.get("data", [])
    for page_number in range(2, int(ceil(page.get("total", 0) / float(page_size))) + 1):
        page = _get_grouped_following_alerts_page(
            organization_id,
            following_ids,
            states,
            severities,
            page=page_number,
            page_size=page_size,
            language=language,
            search=search,
            order=order,
            sort=sort,
        )
        yield from page.get("data", [])


def get_alert(alert_id: Union[UUID, str]) -> Dict:
    """
    returns the detailed object that describes an alert.
        <https://api.zanshin.tenchisecurity.com/#operation/getAlertById>
    :param alert_id: the ID of the alert
    :return: the decoded JSON object returned by the API
    """
    return Client._request("GET", f"/alerts/{validate_uuid(alert_id)}").json()


def iter_alert_history(alert_id: Union[UUID, str]) -> Iterator[Dict]:
    """
    Iterates over the history of an alert.
        <https://api.zanshin.tenchisecurity.com/#operation/listAllAlertHistory>
    :param alert_id: the ID of the alert
    :return:
    """
    yield from Client._request(
        "GET", f"/alerts/{validate_uuid(alert_id)}/history"
    ).json()


def iter_alert_comments(alert_id: Union[UUID, str]) -> Iterator[Dict]:
    """
    Iterates over the comment of an alert.
        <https://api.zanshin.tenchisecurity.com/#operation/listAllAlertComments>
    :param alert_id: the ID of the alert
    :return:
    """
    yield from Client._request(
        "GET", f"/alerts/{validate_uuid(alert_id)}/comments"
    ).json()


def update_alert(
    organization_id: Union[UUID, str],
    scan_target_id: Union[UUID, str],
    alert_id: Union[UUID, str],
    state: Optional[AlertState],
    labels: Optional[Iterable[str]],
    comment: Optional[str],
) -> Dict:
    """
    update alert.
        <https://api.zanshin.tenchisecurity.com/#operation/editOrganizationScanTargetAlertById>
    :param comment:
    :param labels:
    :param state:
    :param scan_target_id:
    :param organization_id:
    :param alert_id: the ID of the alert
    :return: the decoded JSON object returned by the API
    """

    body = dict()
    if state:
        body["state"] = state

    if labels:
        body["labels"] = labels

    if comment:
        body["comment"] = comment

    return Client._request(
        "PUT",
        f"/organizations/{validate_uuid(organization_id)}/scantargets/"
        f"{validate_uuid(scan_target_id)}/alerts/{validate_uuid(alert_id)}",
        body=body,
    ).json()


def create_alert_comment(
    organization_id: Union[UUID, str],
    scan_target_id: Union[UUID, str],
    alert_id: Union[UUID, str],
    comment: str,
) -> Iterator[Dict]:
    """
    Iterates over the comment of an alert.
        <https://api.zanshin.tenchisecurity.com/#operation/listAllAlertComments>
    :param comment:
    :param organization_id: the ID of the organization
    :param scan_target_id: the ID of the scan target
    :param alert_id: the ID of the alert
    :return:
    """

    body = {"comment": comment}

    return Client._request(
        "POST",
        f"/organizations/{validate_uuid(organization_id)}/scantargets/"
        f"{validate_uuid(scan_target_id)}/alerts/{validate_uuid(alert_id)}/comments",
        body=body,
    ).json()
