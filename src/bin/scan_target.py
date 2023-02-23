from typing import Iterator, Optional, Union
from uuid import UUID

from src.bin.client import Client, validate_class, validate_uuid
from src.lib.models import (
    ScanTargetAWS,
    ScanTargetAZURE,
    ScanTargetDOMAIN,
    ScanTargetGCP,
    ScanTargetHUAWEI,
    ScanTargetKind,
    ScanTargetORACLE,
    ScanTargetSchedule,
)

###################################################
# Organization Scan Target
###################################################


def iter_organization_scan_targets(organization_id: Union[UUID, str]) -> Iterator[dict]:
    """
    Iterates over the scan targets of an organization.
    <https://api.zanshin.tenchisecurity.com/#operation/getOrganizationScanTargets>
    :param organization_id: the ID of the organization
    : return: an iterator over the scan target objects
    """
    yield from Client._request(
        "GET", f"/organizations/{validate_uuid(organization_id)}/scantargets"
    ).json()


def create_organization_scan_target(
    organization_id: Union[UUID, str],
    kind: ScanTargetKind,
    name: str,
    credential: Union[
        ScanTargetAWS,
        ScanTargetAZURE,
        ScanTargetGCP,
        ScanTargetHUAWEI,
        ScanTargetDOMAIN,
        ScanTargetORACLE,
    ],
    schedule: Union[str, ScanTargetSchedule] = ScanTargetSchedule.TWENTY_FOUR_HOURS,
) -> dict:
    """
    Create a new scan target in organization.
    <https://api.zanshin.tenchisecurity.com/#operation/createOrganizationScanTargets>
    :param organization_id: the ID of the organization
    :param kind: the Kind of scan target (AWS, GCP, AZURE)
    :param name: the name of the scan target
    :param credential: credentials to access the cloud account to be scanned:
        * For AWS scan targets, provide the account ID in the *account* field
        * For Azure scan targets, provide *applicationId*, *subscriptionId*, *directoryId* and *secret* fields.
        * For GCP scan targets, provide a *projectId* field
        * For DOMAIN scan targets, provide a URL in the *domain* field
    :param schedule: schedule as a string or enum version of the scan frequency
    :return: a dict representing the newly created scan target
    """
    validate_class(kind, ScanTargetKind)
    validate_class(name, str)

    if kind == ScanTargetKind.AWS:
        validate_class(credential, ScanTargetAWS)
    elif kind == ScanTargetKind.AZURE:
        validate_class(credential, ScanTargetAZURE)
    elif kind == ScanTargetKind.GCP:
        validate_class(credential, ScanTargetGCP)
    elif kind == ScanTargetKind.HUAWEI:
        validate_class(credential, ScanTargetHUAWEI)
    elif kind == ScanTargetKind.DOMAIN:
        validate_class(credential, ScanTargetDOMAIN)
    elif kind == ScanTargetKind.ORACLE:
        validate_class(credential, ScanTargetORACLE)

    body = {
        "name": name,
        "kind": kind,
        "credential": credential,
        "schedule": ScanTargetSchedule.from_value(schedule).value,
    }
    return Client._request(
        "POST",
        f"/organizations/{validate_uuid(organization_id)}/scantargets",
        body=body,
    ).json()


def get_organization_scan_target(
    organization_id: Union[UUID, str], scan_target_id: Union[UUID, str]
) -> dict:
    """
    Get scan target of organization.
    <https://api.zanshin.tenchisecurity.com/#operation/getOrganizationScanTargetById>
    :param scan_target_id:
    :param organization_id: the ID of the organization
    :return: a dict representing the scan target
    """
    return Client._request(
        "GET",
        f"/organizations/{validate_uuid(organization_id)}/scantargets/"
        f"{validate_uuid(scan_target_id)}",
    ).json()


def update_organization_scan_target(
    organization_id: Union[UUID, str],
    scan_target_id: Union[UUID, str],
    name: str,
    schedule: Union[str, ScanTargetSchedule],
) -> dict:
    """
    Update scan target of organization.
    <https://api.zanshin.tenchisecurity.com/#operation/editOrganizationScanTargetById>
    :param schedule:
    :param scan_target_id:
    :param name:
    :param organization_id: the ID of the organization
    :return: a dict representing the organization follower
    """

    body = {
        "name": name,
        "schedule": ScanTargetSchedule.from_value(schedule).value,
    }

    return Client._request(
        "PUT",
        f"/organizations/{validate_uuid(organization_id)}/scantargets/"
        f"{validate_uuid(scan_target_id)}",
        body=body,
    ).json()


def delete_organization_scan_target(
    organization_id: Union[UUID, str], scan_target_id: Union[UUID, str]
) -> bool:
    """
    Delete scan target of organization.
    <https://api.zanshin.tenchisecurity.com/#operation/deleteOrganizationScanTargetById>
    :param organization_id: the ID of the organization
    :param scan_target_id:
    :return: a boolean if success
    """
    return Client._request(
        "DELETE",
        f"/organizations/{validate_uuid(organization_id)}/scantargets/"
        f"{validate_uuid(scan_target_id)}",
    ).json()


def start_organization_scan_target_scan(
    organization_id: Union[UUID, str],
    scan_target_id: Union[UUID, str],
    force: Optional[bool],
) -> bool:
    """
    Starts a scan on the specified scan target.
    <https://api.zanshin.tenchisecurity.com/#operation/scanOrganizationScanTarget>
    :param organization_id: the ID of organization the scan target belongs to
    :param scan_target_id: the ID of the scan target
    :param force: whether to force a scan that is in state NEW or INVALID_CREDENTIAL
    :return: a boolean if success
    """

    params = {"force": "true" if force else "false"}  # Http params are always strings
    return Client._request(
        "POST",
        f"/organizations/{validate_uuid(organization_id)}/scantargets/"
        f"{validate_uuid(scan_target_id)}/scan",
        params=params,
    ).json()


def stop_organization_scan_target_scan(
    organization_id: Union[UUID, str], scan_target_id: Union[UUID, str]
) -> bool:
    """
    Stop a scan on the specific scan target
    :param organization_id: the ID of organization the scan target belongs to
    :param scan_target_id: the ID of the scan target
    :return: a boolean if success
    """
    return Client._request(
        "POST",
        f"/organizations/{validate_uuid(organization_id)}/scantargets/"
        f"{validate_uuid(scan_target_id)}/stop",
    ).json()


def check_organization_scan_target(
    organization_id: Union[UUID, str], scan_target_id: Union[UUID, str]
) -> dict:
    """
    Check scan target.
    <https://api.zanshin.tenchisecurity.com/#operation/checkOrganizationScanTarget>
    :param organization_id: the ID of organization the scan target belongs to
    :param scan_target_id: the ID of the scan target
    :return: a dict representing the scan target
    """
    return Client._request(
        "POST",
        f"/organizations/{validate_uuid(organization_id)}/scantargets/"
        f"{validate_uuid(scan_target_id)}/check",
    ).json()


def get_gworkspace_oauth_link(
    organization_id: Union[UUID, str], scan_target_id: Union[UUID, str]
) -> dict:
    """
    Retrieve a link to allow the user to authorize zanshin to read info from their gworkspace environment.
    <https://api.zanshin.tenchisecurity.com/#operation/getGworkspaceOauthLink>
    :return: a dict with the link
    """
    return Client._request(
        "GET",
        f"/gworkspace/oauth/link?scanTargetId={validate_uuid(scan_target_id)}"
        f"&organizationId={validate_uuid(organization_id)}",
    ).json()
