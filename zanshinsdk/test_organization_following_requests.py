import unittest

from client import Client
from organization_following_request import (
    accept_organization_following_request,
    decline_organization_following_request,
    get_organization_following_request,
    iter_organization_following_requests,
)

###################################################
# Organization Following Request
###################################################


class OrganizationFollowingRequestsTest(unittest.TestCase):
    def test_iter_organization_following_requests(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"

        try:
            next(iter_organization_following_requests(organization_id))
        except StopIteration:
            pass

        Client._request.assert_called_once_with(
            "GET", f"/organizations/{organization_id}/following/requests"
        )

    def test_get_organization_following_request(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        following_id = "e22f4225-43e9-4922-b6b8-8b0620bdb110"

        get_organization_following_request(organization_id, following_id)

        Client._request.assert_called_once_with(
            "GET", f"/organizations/{organization_id}/following/requests/{following_id}"
        )

    def test_accept_organization_following_request(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        following_id = "e22f4225-43e9-4922-b6b8-8b0620bdb110"

        accept_organization_following_request(organization_id, following_id)

        Client._request.assert_called_once_with(
            "POST",
            f"/organizations/{organization_id}/following/requests/{following_id}/accept",
        )

    def test_decline_organization_following_request(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        following_id = "e22f4225-43e9-4922-b6b8-8b0620bdb110"

        decline_organization_following_request(organization_id, following_id)

        Client._request.assert_called_once_with(
            "POST",
            f"/organizations/{organization_id}/following/requests/{following_id}/decline",
        )
