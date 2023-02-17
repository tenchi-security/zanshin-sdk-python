from typing import Dict, Iterable, Iterator, Optional, Union
from uuid import UUID

from client import Client, Roles, validate_uuid

###################################################
# Organization Member Invite
###################################################


def iter_organization_members_invites(
    organization_id: Union[UUID, str]
) -> Iterator[Dict]:
    """
    Iterates over the members invites of an organization.
    <https://api.zanshin.tenchisecurity.com/#operation/getOrgamizationInvites>
    :param organization_id: the ID of the organization
    :return: an iterator over the organization members invites objects
    """
    yield from Client._request(
        "GET", f"/organizations/{validate_uuid(organization_id)}/invites"
    ).json()


def create_organization_members_invite(
    organization_id: Union[UUID, str],
    email: str,
    roles: Optional[Iterable[Roles]],
) -> Iterator[Dict]:
    """
    Create organization member invite.
    <https://api.zanshin.tenchisecurity.com/#operation/createOrgamizationInvite>
    :param organization_id: the ID of the organization
    :param email: the e-mail of the new member
    :param roles: the Role of the member (ADMIN, None)
    :return: a dict representing the organization member invite
    """
    body = {
        "email": email,
        "roles": roles,
    }
    return Client._request(
        "POST",
        f"/organizations/{validate_uuid(organization_id)}/invites",
        body=body,
    ).json()


def get_organization_member_invite(
    organization_id: Union[UUID, str], email: str
) -> Iterator[Dict]:
    """
    Get organization member invite.
    <https://api.zanshin.tenchisecurity.com/#operation/getOrganizationInviteByEmail>
    :param organization_id: the ID of the organization
    :param email: the e-mail of the invited member
    :return: a dict representing the organization member invite
    """
    return Client._request(
        "GET", f"/organizations/{validate_uuid(organization_id)}/invites/{email}"
    ).json()


def delete_organization_member_invite(
    organization_id: Union[UUID, str], email: str
) -> bool:
    """
    Delete organization member invite.
    <https://api.zanshin.tenchisecurity.com/#operation/deleteOrganizationInviteByEmail>
    :param organization_id: the ID of the organization
    :param email: the e-mail of the invited member
    :return: a boolean if success
    """
    return Client._request(
        "DELETE", f"/organizations/{validate_uuid(organization_id)}/invites/{email}"
    ).json()


def resend_organization_member_invite(
    organization_id: Union[UUID, str], email: str
) -> Dict:
    """
    Resend organization member invitation.
    <https://api.zanshin.tenchisecurity.com/#operation/resendOrganizationInviteByEmail>
    :param organization_id: the ID of the organization
    :param email: the e-mail of the invited member
    :return: a boolean if success
    """
    return Client._request(
        "POST",
        f"/organizations/{validate_uuid(organization_id)}/invites/{email}/resend",
    ).json()
