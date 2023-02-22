from typing import Dict, Iterator, Union
from uuid import UUID

from client import Client, validate_uuid

###################################################
# Organization Follower
###################################################


def iter_organization_followers(organization_id: Union[UUID, str]) -> Iterator[Dict]:
    """
    Iterates over the followers of an organization.
    <https://api.zanshin.tenchisecurity.com/#operation/getOrganizationFollowers>
    :param organization_id: the ID of the organization
    :return: an iterator over the organization followers objects
    """
    yield from Client._request(
        "GET", f"/organizations/{validate_uuid(organization_id)}/followers"
    ).json()


def stop_organization_follower(
    organization_id: Union[UUID, str], follower_id: Union[UUID, str]
) -> bool:
    """
    Stops one organization follower of another.
    <https://api.zanshin.tenchisecurity.com/#operation/removeOrganizationFollower>
    :param organization_id: the ID of the organization
    :param follower_id: the ID of the follower
    :return: a boolean if success
    """
    return Client._request(
        "DELETE",
        f"/organizations/{validate_uuid(organization_id)}/followers/"
        f"{validate_uuid(follower_id)}",
    ).json()
