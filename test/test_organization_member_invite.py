import unittest

from src.bin.client import Client
from src.bin.organization_member_invite import (
    create_organization_members_invite,
    delete_organization_member_invite,
    get_organization_member_invite,
    iter_organization_members_invites,
    resend_organization_member_invite,
)
from src.lib.models import Roles

###################################################
# Organization Member Invite
###################################################


class OrganizationMemberInviteTest(unittest.TestCase):
    def test_iter_organization_members_invites(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"

        try:
            next(iter_organization_members_invites(organization_id))
        except StopIteration:
            pass

        Client._request.assert_called_once_with(
            "GET", f"/organizations/{organization_id}/invites"
        )

    def test_create_organization_members_invite(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        email = "juca@example.com"
        role = [Roles.ADMIN]

        create_organization_members_invite(organization_id, email, role)

        Client._request.assert_called_once_with(
            "POST",
            f"/organizations/{organization_id}/invites",
            body={"email": email, "roles": role},
        )

    def test_get_organization_member_invite(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        email = "juca@example.com"

        get_organization_member_invite(organization_id, email)

        Client._request.assert_called_once_with(
            "GET", f"/organizations/{organization_id}/invites/{email}"
        )

    def test_delete_organization_member_invite(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        email = "juca@example.com"

        delete_organization_member_invite(organization_id, email)

        Client._request.assert_called_once_with(
            "DELETE", f"/organizations/{organization_id}/invites/{email}"
        )

    def test_resend_organization_member_invite(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        email = "juca@example.com"

        resend_organization_member_invite(organization_id, email)

        Client._request.assert_called_once_with(
            "POST", f"/organizations/{organization_id}/invites/{email}/resend"
        )
