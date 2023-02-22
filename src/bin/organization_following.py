from typing import Dict, Iterator, Union
from uuid import UUID

from src.bin.client import Client, validate_uuid

###################################################
# Organization Following
###################################################


def iter_organization_following(organization_id: Union[UUID, str]) -> Iterator[Dict]:
    """
    Iterates over the following of an organization.
    <https://api.zanshin.tenchisecurity.com/#operation/getOrganizationFollowing>
    :param organization_id: the ID of the organization whose followed organizations we should list
    :return: an iterator over the JSON decoded followed organizations
    """
    yield from Client._request(
        "GET", f"/organizations/{validate_uuid(organization_id)}/following"
    ).json()


def stop_organization_following(
    organization_id: Union[UUID, str], following_id: Union[UUID, str]
) -> bool:
    """
    Stops one organization following of another.
    <https://api.zanshin.tenchisecurity.com/#operation/removeOrganizationFollowingById>
    :param organization_id: the follower organization ID
    :param following_id:  the followed organization ID
    :return: a boolean indicating whether the operation was successful
    """
    return Client._request(
        "DELETE",
        f"/organizations/{validate_uuid(organization_id)}/following/"
        f"{validate_uuid(following_id)}",
    ).json()
