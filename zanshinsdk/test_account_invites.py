import unittest

from account_invites import accept_invite, get_invite, iter_invites
from client import Client


###################################################
# Account Invites
###################################################
class AccountInvitesTest(unittest.TestCase):
    def test_iter_invites(self):
        try:
            next(iter_invites())
        except StopIteration:
            pass

        Client._request.assert_called_once_with("GET", "/me/invites")

    def test_get_invite(self):
        invite_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"

        get_invite(invite_id)

        Client._request.assert_called_once_with("GET", f"/me/invites/{invite_id}")

    def test_accept_invite(self):
        invite_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"

        accept_invite(invite_id)

        Client._request.assert_called_once_with(
            "POST", f"/me/invites/{invite_id}/accept"
        )
