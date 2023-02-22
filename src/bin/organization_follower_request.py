from typing import Dict, Iterator, Union
from uuid import UUID

from src.bin.client import Client, validate_uuid

###################################################
# Organization Follower Request
###################################################


def iter_organization_follower_requests(
    organization_id: Union[UUID, str]
) -> Iterator[Dict]:
    """
    Iterates over the follower requests of an organization.
    <https://api.zanshin.tenchisecurity.com/#operation/getOrganizationFollowRequests>
    :param organization_id: the ID of the organization
    :return: an iterator over the organization follower requests objects
    """
    yield from Client._request(
        "GET", f"/organizations/{validate_uuid(organization_id)}/followers/requests"
    ).json()


def create_organization_follower_request(
    organization_id: Union[UUID, str], token: Union[UUID, str]
) -> Dict:
    """
    Create organization follower request.
    <https://api.zanshin.tenchisecurity.com/#operation/createOrganizationFollowRequests>
    :param organization_id: the ID of the organization
    :param token: the token of the follower request
    :return: a dict representing the organization follower
    """
    body = {
        "token": validate_uuid(token),
    }
    return Client._request(
        "POST",
        f"/organizations/{validate_uuid(organization_id)}/followers/requests",
        body=body,
    ).json()


def get_organization_follower_request(
    organization_id: Union[UUID, str], token: Union[UUID, str]
) -> Dict:
    """
    Get organization follower request.
    <https://api.zanshin.tenchisecurity.com/#operation/getOrganizationFollowRequestsByToken>
    :param organization_id: the ID of the organization
    :param token: the token of the follower request
    :return: a dict representing the organization follower
    """
    return Client._request(
        "GET",
        f"/organizations/{validate_uuid(organization_id)}/followers/requests/"
        f"{validate_uuid(token)}",
    ).json()


def delete_organization_follower_request(
    organization_id: Union[UUID, str], follower_id: Union[UUID, str]
) -> bool:
    """
    Delete organization follower request.
    <https://api.zanshin.tenchisecurity.com/#operation/deleteOrganizationFollowRequestsbyToken>
    :param organization_id: the ID of the organization
    :param follower_id: the ID of the follower
    :return: a boolean if success
    """
    return Client._request(
        "DELETE",
        f"/organizations/{validate_uuid(organization_id)}/followers/requests/"
        f"{validate_uuid(follower_id)}",
    ).json()
