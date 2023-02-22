from typing import Dict, Iterable, Optional, Union
from uuid import UUID

from client import Client, Languages, validate_class, validate_int, validate_uuid

###################################################
# Summary
###################################################


def get_alert_summaries(
    organization_id: Union[UUID, str],
    scan_target_ids: Optional[Iterable[Union[UUID, str]]] = None,
    search: Optional[str] = None,
    language: Optional[Languages] = None,
) -> Dict:
    """
    Gets a summary of the current state of alerts for an organization, both in total and broken down by scan
    target.
    <https://api.zanshin.tenchisecurity.com/#operation/alertSummary>
    :param organization_id: the ID of the organization whose alert summaries are desired
    :param scan_target_ids: optional list of scan target IDs to summarize alerts from, defaults to all
    :param language: language to use for the returned rules
    :param search: Search string to find in alerts
    :return: JSON object containing the alert summaries
    """

    body = {"organizationId": validate_uuid(organization_id)}

    if scan_target_ids:
        if isinstance(scan_target_ids, str):
            scan_target_ids = [scan_target_ids]
        validate_class(scan_target_ids, Iterable)
        body["scanTargetIds"] = [validate_uuid(x) for x in scan_target_ids]
    if search:
        validate_class(search, str)
        body["search"] = search
    if language:
        validate_class(language, Languages)
        body["lang"] = language.value

    return Client._request("POST", "/alerts/summaries", body=body).json()


def get_following_alert_summaries(
    organization_id: Union[UUID, str],
    following_ids: Optional[Iterable[Union[UUID, str]]] = None,
    search: Optional[str] = None,
    language: Optional[Languages] = None,
) -> Dict:
    """
    Gets a summary of the current state of alerts for followed organizations.
    <https://api.zanshin.tenchisecurity.com/#operation/alertFollowingSummary>
    :param organization_id:
    :param following_ids: list of IDs of organizations being followed to summarize alerts from
    :param language: language to use for the returned rules
    :param search: Search string to find in alerts
    :return: JSON object containing the alert summaries
    """
    body = {"organizationId": validate_uuid(organization_id)}

    if following_ids:
        if isinstance(following_ids, str):
            following_ids = [following_ids]
        validate_class(following_ids, Iterable)
        body["followingIds"] = [validate_uuid(x) for x in following_ids]
    if search:
        validate_class(search, str)
        body["search"] = search
    if language:
        validate_class(language, Languages)
        body["lang"] = language.value

    return Client._request("POST", "/alerts/summaries/following", body=body).json()


def get_scan_summaries(
    organization_id: Union[UUID, str],
    scan_target_ids: Optional[Iterable[Union[UUID, str]]] = None,
    days: Optional[int] = 7,
) -> Dict:
    """
    Returns summaries of scan results over a period of time, summarizing number of alerts that changed states.
    <https://api.zanshin.tenchisecurity.com/#operation/scanSummary>
    :param organization_id: the ID of the organization whose scan summaries are desired
    :param scan_target_ids: optional list of scan target IDs to summarize scans from, defaults to all
    :param days: number of days to go back in time in historical search
    :return: JSON object containing the scan summaries
    """

    body = {
        "organizationId": validate_uuid(organization_id),
        "daysBefore": validate_int(days, min_value=1),
    }

    if scan_target_ids:
        if isinstance(scan_target_ids, str):
            scan_target_ids = [scan_target_ids]
        validate_class(scan_target_ids, Iterable)
        body["scanTargetIds"] = [validate_uuid(x) for x in scan_target_ids]

    return Client._request("POST", "/alerts/summaries/scans", body=body).json()


def get_following_scan_summaries(
    organization_id: Union[UUID, str],
    following_ids: Optional[Iterable[Union[UUID, str]]] = None,
    days: Optional[int] = 7,
) -> Dict:
    """
    Gets a summary of the current state of alerts for followed organizations.
    <https://api.zanshin.tenchisecurity.com/#operation/scanSummaryFollowing>
    :param organization_id:
    :param following_ids: list of IDs of organizations being followed to summarize alerts from
    :param days: number of days to go back in time in historical search
    :return: JSON object containing the scan summaries
    """

    body = {
        "organizationId": validate_uuid(organization_id),
        "daysBefore": validate_int(days, min_value=1),
    }

    if following_ids:
        if isinstance(following_ids, str):
            following_ids = [following_ids]
        validate_class(following_ids, Iterable)
        body["followingIds"] = [validate_uuid(x) for x in following_ids]

    return Client._request(
        "POST", "/alerts/summaries/scans/following", body=body
    ).json()


def __repr__(self):
    return (
        f"Connection(api_url='{Client.api_url}', api_key='***{Client._api_key[-6:]}', "
        f"user_agent='{Client.user_agent}', proxy_url='{Client._get_sanitized_proxy_url()}')"
    )
