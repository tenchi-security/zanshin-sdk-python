import unittest

from client import Client
from organization_follower_request import (
    create_organization_follower_request,
    delete_organization_follower_request,
    get_organization_follower_request,
    iter_organization_follower_requests,
)

###################################################
# Organization Follower Request
###################################################


class OrganizationFollowerRequestTest(unittest.TestCase):
    def test_iter_organization_follower_requests(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        try:
            next(iter_organization_follower_requests(organization_id))
        except StopIteration:
            pass

        Client._request.assert_called_once_with(
            "GET", f"/organizations/{organization_id}/followers/requests"
        )

    def test_create_organization_follower_request(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        token = "e22f4225-43e9-4922-b6b8-8b0620bdb110"

        create_organization_follower_request(organization_id, token)

        Client._request.assert_called_once_with(
            "POST",
            f"/organizations/{organization_id}/followers/requests",
            body={"token": token},
        )

    def test_get_organization_follower_request(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        follower_id = "e22f4225-43e9-4922-b6b8-8b0620bdb110"

        get_organization_follower_request(organization_id, follower_id)

        Client._request.assert_called_once_with(
            "GET", f"/organizations/{organization_id}/followers/requests/{follower_id}"
        )

    def test_delete_organization_follower_request(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        follower_id = "e22f4225-43e9-4922-b6b8-8b0620bdb110"

        delete_organization_follower_request(organization_id, follower_id)

        Client._request.assert_called_once_with(
            "DELETE",
            f"/organizations/{organization_id}/followers/requests/{follower_id}",
        )
