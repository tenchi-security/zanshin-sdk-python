from typing import Dict, Iterator, Union
from uuid import UUID

from client import Client, validate_uuid

###################################################
# Organization Scan Target Scan
###################################################


def iter_organization_scan_target_scans(
    organization_id: Union[UUID, str], scan_target_id: Union[UUID, str]
) -> Iterator[Dict]:
    """
    Iterates over the scan of a scan target.
    <https://api.zanshin.tenchisecurity.com/#operation/getOrganizationScanTargetScans>
    :param organization_id: the ID of the organization
    :param scan_target_id: the ID of the scan target
    :return: an iterator over the JSON decoded scans
    """
    yield from Client._request(
        "GET",
        f"/organizations/{validate_uuid(organization_id)}/scantargets/"
        f"{validate_uuid(scan_target_id)}/scans",
    ).json().get("data", [])


def get_organization_scan_target_scan(
    organization_id: Union[UUID, str],
    scan_target_id: Union[UUID, str],
    scan_id: Union[UUID, str],
) -> Dict:
    """
    Get scan of scan target.
    <https://api.zanshin.tenchisecurity.com/#operation/getOrganizationScanTargetScanSlot>
    :param organization_id: the ID of the organization
    :param scan_target_id: the ID of the scan target
    :param scan_id: the ID of the scan
    :return: a dict representing the scan
    """
    return Client._request(
        "GET",
        f"/organizations/{validate_uuid(organization_id)}/scantargets/"
        f"{validate_uuid(scan_target_id)}/scans/{scan_id}",
    ).json()
