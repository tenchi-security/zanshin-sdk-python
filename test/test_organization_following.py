import unittest

from src.bin.client import Client
from src.bin.organization_following import (
    iter_organization_following,
    stop_organization_following,
)

###################################################
# Organization Following
###################################################


class OrganizationFollowingTest(unittest.TestCase):
    def test_iter_organization_following(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"

        try:
            next(iter_organization_following(organization_id))
        except StopIteration:
            pass

        Client._request.assert_called_once_with(
            "GET", f"/organizations/{organization_id}/following"
        )

    def test_stop_organization_following(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        following_id = "e22f4225-43e9-4922-b6b8-8b0620bdb110"

        stop_organization_following(organization_id, following_id)

        Client._request.assert_called_once_with(
            "DELETE", f"/organizations/{organization_id}/following/{following_id}"
        )
