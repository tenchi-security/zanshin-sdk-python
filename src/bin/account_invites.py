from typing import Dict, Iterator, Union
from uuid import UUID

from src.bin.client import Client, validate_uuid

###################################################
# Account Invites
###################################################


def iter_invites() -> Iterator[Dict]:
    """
    Iterates over the invites of current logged user.
    <https://api.zanshin.tenchisecurity.com/#operation/getInvites>
    :return: an iterator over the invites objects
    """
    yield from Client._request("GET", "/me/invites").json()


def get_invite(invite_id: Union[UUID, str]) -> Dict:
    """
    Gets a specific invitation details, it only works if the invitation was made for the current logged user.
    <https://api.zanshin.tenchisecurity.com/#operation/getInviteById>
    :param invite_id: the ID of the invite
    :return: a dict representing the user invite
    """
    return Client._request("GET", f"/me/invites/{validate_uuid(invite_id)}").json()


def accept_invite(invite_id: Union[UUID, str]) -> Dict:
    """
    Accepts an invitation with the informed ID, it only works if the user accepting the invitation is the user that
    received the invitation.
    <https://api.zanshin.tenchisecurity.com/#operation/acceptInviteById>
    :param invite_id: the ID of the invite
    :return: a dict representing the organization of this invite
    """
    return Client._request(
        "POST", f"/me/invites/{validate_uuid(invite_id)}/accept"
    ).json()
