from typing import Dict, Iterator, Union
from uuid import UUID

from client import Client, validate_uuid

###################################################
# Organization Following Request
###################################################


def iter_organization_following_requests(
    organization_id: Union[UUID, str]
) -> Iterator[Dict]:
    """
    Returns all requests received by an organization to follow another.
    <https://api.zanshin.tenchisecurity.com/#operation/getOrganizationFollowingRequests>
    :param organization_id: the ID of the organization that was invited to follow another
    :return: an iterator over the JSON decoded following requests
    """
    yield from Client._request(
        "GET", f"/organizations/{validate_uuid(organization_id)}/following/requests"
    ).json()


def get_organization_following_request(
    organization_id: Union[UUID, str], following_id: Union[UUID, str]
) -> Dict:
    """
    Returns a request received by an organization to follow another.
    <https://api.zanshin.tenchisecurity.com/#operation/getOrganizationFollowingRequestByToken>
    :param organization_id: the ID of the organization
    :param following_id: the ID of the following
    :return: a dict representing the following request
    """
    return Client._request(
        "GET",
        f"/organizations/{validate_uuid(organization_id)}/following/requests/"
        f"{validate_uuid(following_id)}",
    ).json()


def accept_organization_following_request(
    organization_id: Union[UUID, str], following_id: Union[UUID, str]
) -> Dict:
    """
    Accepts a request to follow another organization.
    <https://api.zanshin.tenchisecurity.com/#operation/acceptOrganizationFollowingRequestByToken>
    :param organization_id: the ID of the organization who was invited to follow another
    :param following_id: the ID of the organization who is going to be followed
    :return: a decoded JSON object describing the newly established following relationship
    """
    return Client._request(
        "POST",
        f"/organizations/{validate_uuid(organization_id)}/following/requests/"
        f"{validate_uuid(following_id)}/accept",
    ).json()


def decline_organization_following_request(
    organization_id: Union[UUID, str], following_id: Union[UUID, str]
) -> Dict:
    """
    Declines a request to follow another organization.
    <https://api.zanshin.tenchisecurity.com/#operation/declineOrganizationFollowingRequestByToken>
    :param organization_id: the ID of the organization who was invited to follow another
    :param following_id: the ID of the organization who was going to be followed
    :return: a decoded JSON object describing the newly established following relationship
    """
    return Client._request(
        "POST",
        f"/organizations/{validate_uuid(organization_id)}/following/requests/"
        f"{validate_uuid(following_id)}/decline",
    ).json()
