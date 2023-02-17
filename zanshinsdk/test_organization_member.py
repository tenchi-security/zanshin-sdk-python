import unittest

from client import Client
from organization_member import (
    Roles,
    delete_organization_member,
    get_organization_member,
    iter_organization_members,
    reset_delete_organization_password,
    reset_organization_member_mfa,
    update_organization_member,
)

###################################################
# Organization Member
###################################################


class OrganizationMemberTest(unittest.TestCase):
    def test_iter_organization_members(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"

        try:
            next(iter_organization_members(organization_id))
        except StopIteration:
            pass

        Client._request.assert_called_once_with(
            "GET", f"/organizations/{organization_id}/members"
        )

    def test_get_organization_members(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        member_id = "e22f4225-43e9-4922-b6b8-8b0620bdb110"

        get_organization_member(organization_id, member_id)

        Client._request.assert_called_once_with(
            "GET", f"/organizations/{organization_id}/members/{member_id}"
        )

    def test_update_organization_members(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        member_id = "e22f4225-43e9-4922-b6b8-8b0620bdb110"
        role = [Roles.ADMIN]

        update_organization_member(organization_id, member_id, role)

        Client._request.assert_called_once_with(
            "PUT",
            f"/organizations/{organization_id}/members/{member_id}",
            body={"roles": role},
        )

    def test_delete_organization_members(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        member_id = "e22f4225-43e9-4922-b6b8-8b0620bdb110"

        delete_organization_member(organization_id, member_id)

        Client._request.assert_called_once_with(
            "DELETE", f"/organizations/{organization_id}/members/{member_id}"
        )

    def test_reset_organization_member_mfa(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        member_id = "e22f4225-43e9-4922-b6b8-8b0620bdb110"

        reset_organization_member_mfa(organization_id, member_id)

        Client._request.assert_called_once_with(
            "POST", f"/organizations/{organization_id}/members/{member_id}/mfa/reset"
        )

    def test_reset_delete_organization_password(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        member_id = "e22f4225-43e9-4922-b6b8-8b0620bdb110"

        reset_delete_organization_password(organization_id, member_id)

        Client._request.assert_called_once_with(
            "POST",
            f"/organizations/{organization_id}/members/{member_id}/password/reset",
        )
