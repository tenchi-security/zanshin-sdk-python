from typing import Dict, Iterable, Iterator, Optional, Union
from uuid import UUID

from src.bin.client import Client, Roles, validate_uuid

###################################################
# Organization Member
###################################################


def iter_organization_members(organization_id: Union[UUID, str]) -> Iterator[Dict]:
    """
    Iterates over the users which are members of an organization.
    <https://api.zanshin.tenchisecurity.com/#operation/getOrganizationMembers>
    :param organization_id: the ID of the organization
    :return: an iterator over the organization members objects
    """
    yield from Client._request(
        "GET", f"/organizations/{validate_uuid(organization_id)}/members"
    ).json()


def get_organization_member(
    organization_id: Union[UUID, str], member_id: Union[UUID, str]
) -> Dict:
    """
    Get details on a user's organization membership.
    <https://api.zanshin.tenchisecurity.com/#operation/getOrganizationMembers>
    :param organization_id: the ID of the organization
    :param member_id: the ID of the member
    :return: a dict representing the organization member
    """
    return Client._request(
        "GET",
        f"/organizations/{validate_uuid(organization_id)}/members/"
        f"{validate_uuid(member_id)}",
    ).json()


def update_organization_member(
    self,
    organization_id: Union[UUID, str],
    member_id: Union[UUID, str],
    roles: Optional[Iterable[Roles]],
) -> Dict:
    """
    Update organization member.
    <https://api.zanshin.tenchisecurity.com/#operation/editOrganizationMembersById>
    :param organization_id: the ID of the organization
    :param member_id: the ID of the member
    :param roles: the Role of the member (ADMIN, None)
    :return: a dict representing the organization member
    """
    body = {
        "roles": roles,
    }
    return Client._request(
        "PUT",
        f"/organizations/{validate_uuid(organization_id)}/members/{validate_uuid(member_id)}",
        body=body,
    ).json()


def delete_organization_member(
    organization_id: Union[UUID, str], member_id: Union[UUID, str]
) -> bool:
    """
    Delete organization member.
    <https://api.zanshin.tenchisecurity.com/#operation/removeOrganizationMemberById>
    :param organization_id: the ID of the organization
    :param member_id: the ID of the member
    :return: a boolean if success
    """
    return Client._request(
        "DELETE",
        f"/organizations/{validate_uuid(organization_id)}/members/"
        f"{validate_uuid(member_id)}",
    ).json()


def reset_organization_member_mfa(
    organization_id: Union[UUID, str], member_id: Union[UUID, str]
) -> bool:
    """
    Reset organization member MFA.
    <https://api.zanshin.tenchisecurity.com/#operation/resetOrganizationMemberMfaById>
    :param organization_id: the ID of the organization
    :param member_id: the ID of the member
    :return: a boolean if success
    """
    return Client._request(
        "POST",
        f"/organizations/{validate_uuid(organization_id)}/members/"
        f"{validate_uuid(member_id)}/mfa/reset",
    ).json()


def reset_delete_organization_password(
    organization_id: Union[UUID, str], member_id: Union[UUID, str]
) -> bool:
    """
    Reset organization member Password.
    <https://api.zanshin.tenchisecurity.com/#operation/resetOrganizationMemberPasswordById>
    :param organization_id: the ID of the organization
    :param member_id: the ID of the member
    :return: a boolean if success
    """
    return Client._request(
        "POST",
        f"/organizations/{validate_uuid(organization_id)}/members/"
        f"{validate_uuid(member_id)}/password/reset",
    ).json()
