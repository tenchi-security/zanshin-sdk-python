import unittest

from src.bin.client import Client
from src.bin.organization_follower import (
    iter_organization_followers,
    stop_organization_follower,
)

###################################################
# Organization Follower
###################################################


class OrganizationFollowingTest(unittest.TestCase):
    def test_iter_organization_followers(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"

        try:
            next(iter_organization_followers(organization_id))
        except StopIteration:
            pass

        Client._request.assert_called_once_with(
            "GET", f"/organizations/{organization_id}/followers"
        )

    def test_stop_organization_follower(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        follower_id = "e22f4225-43e9-4922-b6b8-8b0620bdb110"

        stop_organization_follower(organization_id, follower_id)

        Client._request.assert_called_once_with(
            "DELETE", f"/organizations/{organization_id}/followers/{follower_id}"
        )
