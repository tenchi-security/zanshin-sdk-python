from typing import Dict, Iterator, Union
from uuid import UUID

from src.bin.client import (
    Client,
    ScanTargetGroupCredentialListORACLE,
    ScanTargetKind,
    validate_class,
    validate_uuid,
)

###################################################
# Organization Scan Target Groups
###################################################


def iter_organization_scan_target_groups(
    organization_id: Union[UUID, str]
) -> Iterator[Dict]:
    """
    Iterates over the scan targets groups.
    <https://api.zanshin.tenchisecurity.com/#operation/getOrganizationScanTargetGroups>
    :param organization_id: the ID of the organization
    : return: an iterator over the scan target groups
    """
    yield from Client._request(
        "GET", f"/organizations/{validate_uuid(organization_id)}/scantargetgroups"
    ).json()


def get_organization_scan_target_group(
    organization_id: Union[UUID, str], scan_target_group_id: Union[UUID, str]
) -> Dict:
    """
    Get scan target group of organization.
    <https://api.zanshin.tenchisecurity.com/#operation/getOrganizationScanTargetGroupById>
    :param scan_target_group_id:
    :param organization_id: the ID of the organization
    :return: a dict representing the scan target group
    """
    return Client._request(
        "GET",
        f"/organizations/{validate_uuid(organization_id)}/scantargetgroups/"
        f"{validate_uuid(scan_target_group_id)}",
    ).json()


def create_scan_target_group(
    organization_id: Union[UUID, str], kind: ScanTargetKind, name: str
) -> Dict:
    """
    Create a new scan target group.
    <https://api.zanshin.tenchisecurity.com/#operation/createOrganizationScanTargetGroup>
    :param organization_id: the ID of the organization
    :param kind: The type of cloud of this scan target group
    :param name: the name of the scan target group
    :return: a dict representing the newly created scan target group
    """
    validate_class(kind, ScanTargetKind)
    validate_class(name, str)
    if kind != ScanTargetKind.ORACLE:
        raise ValueError(f"{repr(kind.value)} is not accepted. 'ORACLE' is expected")

    body = {
        "name": name,
        "kind": kind,
    }
    return Client._request(
        "POST",
        f"/organizations/{validate_uuid(organization_id)}/scantargetgroups",
        body=body,
    ).json()


def update_scan_target_group(
    organization_id: Union[UUID, str],
    scan_target_group_id: Union[UUID, str],
    name: str,
) -> Dict:
    """
    Update scan target group.
    <https://api.zanshin.tenchisecurity.com/#operation/UpdateOrganizationScanTargetGroup>
    :param scan_target_group_id: the ID of the scan target group
    :param name: The scan target group assigned name
    :param organization_id: the ID of the organization
    :return: a dict representing the scan target group
    """

    body = {"name": name}

    return Client._request(
        "PUT",
        f"/organizations/{validate_uuid(organization_id)}/scantargetgroups/"
        f"{validate_uuid(scan_target_group_id)}",
        body=body,
    ).json()


def iter_scan_target_group_compartments(
    organization_id: Union[UUID, str], scan_target_group_id: Union[UUID, str]
) -> Iterator[Dict]:
    """
    Iterates over the compartments of a scan target group.
    <https://api.zanshin.tenchisecurity.com/#operation/getOrganizationComapartmentsFromScanTargetGroup>
    :param organization_id: the ID of the organization
    :param scan_target_group_id: the ID of the scan target group
    :return: an iterator over the compartments of a scan target group
    """
    yield from Client._request(
        "GET",
        f"/organizations/{validate_uuid(organization_id)}/scantargetgroups/"
        f"{validate_uuid(scan_target_group_id)}/targets",
    ).json()


def get_scan_target_group_script(
    organization_id: Union[UUID, str], scan_target_group_id: Union[UUID, str]
) -> Dict:
    """
    Get the terraform download URL of the scan target group.
    <https://api.zanshin.tenchisecurity.com/#operation/getOrganizationScanTargetGroupScrip>
    :param organization_id: the ID of the organization
    :param scan_target_group_id: the ID of the scan target group
    :return: Scan target group terraform URL
    """
    return Client._request(
        "GET",
        f"/organizations/{validate_uuid(organization_id)}/scantargetgroups/"
        f"{validate_uuid(scan_target_group_id)}/scripts",
    ).json()


def iter_scan_targets_from_group(
    organization_id: Union[UUID, str], scan_target_group_id: Union[UUID, str]
) -> Iterator[Dict]:
    """
    Iterates over the scan targets of a group.
    <https://api.zanshin.tenchisecurity.com/#operation/getOrganizationScanTargetFromScanTargetGroup>
    :param organization_id: the ID of the organization
    :param scan_target_group_id: the ID of the scan target group
    :return: an iterator over scan targets of a group
    """
    yield from Client._request(
        "GET",
        f"/organizations/{validate_uuid(organization_id)}/scantargetgroups/"
        f"{validate_uuid(scan_target_group_id)}/scantargets",
    ).json()


def delete_organization_scan_target_group(
    organization_id: Union[UUID, str], scan_target_group_id: Union[UUID, str]
) -> bool:
    """
    Delete scan target group of organization.
    <https://api.zanshin.tenchisecurity.com/#operation/deleteOrganizationScanTargetGroupById>
    :param organization_id: the ID of the organization
    :param scan_target_group_id:
    :return: a boolean if success
    """
    return Client._request(
        "DELETE",
        f"/organizations/{validate_uuid(organization_id)}/scantargetgroups/"
        f"{validate_uuid(scan_target_group_id)}",
    ).json()


def insert_scan_target_group_credential(
    organization_id: Union[UUID, str],
    scan_target_group_id: Union[UUID, str],
    credential: ScanTargetGroupCredentialListORACLE,
) -> Dict:
    """
    Insert an already created scan target group.
    <https://api.zanshin.tenchisecurity.com/#operation/UpdateOrganizationScanTargetGroupCredential>
    :param organization_id: the ID of the organization
    :param scan_target_group_id: the ID of the scan target group
    :param credential: scan target group credential oracle
    :return: a dict representing scan target group
    """

    validate_class(credential, ScanTargetGroupCredentialListORACLE)

    body = {
        "credential": credential,
    }
    return Client._request(
        "POST",
        f"/organizations/{validate_uuid(organization_id)}/scantargetgroups/"
        f"{validate_uuid(scan_target_group_id)}",
        body=body,
    ).json()


def create_scan_target_by_compartments(
    organization_id: Union[UUID, str],
    scan_target_group_id: Union[UUID, str],
    name: str,
    ocid: str,
) -> Dict:
    """
    Create Scan Targets from previous listed compartments inside the scan target group.
    <https://api.zanshin.tenchisecurity.com/#operation/createOrganizationScanTargetByCompartments>
    :param organization_id: the ID of the organization
    :param scan_target_group_id: the ID of the scan target group
    :param ocid: Oracle Compartment Id
    :param name: the name of the scan target group
    :return: a dict representing the scan target
    """
    validate_class(ocid, str)
    validate_class(name, str)

    compartments = [{"name": name, "ocid": ocid}]

    body = {"compartments": compartments}
    return Client._request(
        "POST",
        f"/organizations/{validate_uuid(organization_id)}/scantargetgroups/"
        f"{validate_uuid(scan_target_group_id)}/targets",
        body=body,
    ).json()
