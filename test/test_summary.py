import unittest

from src.bin.client import Client
from src.bin.summary import (
    get_alert_summaries,
    get_following_alert_summaries,
    get_following_scan_summaries,
    get_scan_summaries,
)

###################################################
# Summary
###################################################


class SummaryTest(unittest.TestCase):
    def test_get_alert_summaries(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"

        get_alert_summaries(organization_id)

        Client._request.assert_called_once_with(
            "POST", f"/alerts/summaries", body={"organizationId": organization_id}
        )

    def test_get_alert_summaries_str_scan_target_ids(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        scan_target_ids = "e22f4225-43e9-4922-b6b8-8b0620bdb110"

        get_alert_summaries(organization_id, scan_target_ids=scan_target_ids)

        Client._request.assert_called_once_with(
            "POST",
            f"/alerts/summaries",
            body={
                "organizationId": organization_id,
                "scanTargetIds": [scan_target_ids],
            },
        )

    def test_get_alert_summaries_iterable_scan_target_ids(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        scan_target_ids = [
            "e22f4225-43e9-4922-b6b8-8b0620bdb110",
            "e22f4225-43e9-4922-b6b8-8b0620bdb112",
        ]

        get_alert_summaries(organization_id, scan_target_ids=scan_target_ids)

        Client._request.assert_called_once_with(
            "POST",
            f"/alerts/summaries",
            body={"organizationId": organization_id, "scanTargetIds": scan_target_ids},
        )

    def test_get_following_alert_summaries(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"

        get_following_alert_summaries(organization_id)

        Client._request.assert_called_once_with(
            "POST",
            f"/alerts/summaries/following",
            body={"organizationId": organization_id},
        )

    def test_get_following_alert_summaries_str_following_ids(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        following_ids = "e22f4225-43e9-4922-b6b8-8b0620bdb110"

        get_following_alert_summaries(organization_id, following_ids=following_ids)

        Client._request.assert_called_once_with(
            "POST",
            f"/alerts/summaries/following",
            body={"organizationId": organization_id, "followingIds": [following_ids]},
        )

    def test_get_following_alert_summaries_iterable_following_ids(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        following_ids = [
            "e22f4225-43e9-4922-b6b8-8b0620bdb110",
            "e22f4225-43e9-4922-b6b8-8b0620bdb112",
        ]

        get_following_alert_summaries(organization_id, following_ids=following_ids)

        Client._request.assert_called_once_with(
            "POST",
            f"/alerts/summaries/following",
            body={"organizationId": organization_id, "followingIds": following_ids},
        )

    def test_get_scan_summaries(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        days = 7

        get_scan_summaries(organization_id, days=days)

        Client._request.assert_called_once_with(
            "POST",
            f"/alerts/summaries/scans",
            body={"organizationId": organization_id, "daysBefore": days},
        )

    def test_get_scan_summaries_str_scan_target_ids(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        days = 7
        scan_target_ids = "e22f4225-43e9-4922-b6b8-8b0620bdb110"

        get_scan_summaries(organization_id, days=days, scan_target_ids=scan_target_ids)

        Client._request.assert_called_once_with(
            "POST",
            f"/alerts/summaries/scans",
            body={
                "organizationId": organization_id,
                "daysBefore": days,
                "scanTargetIds": [scan_target_ids],
            },
        )

    def test_get_scan_summaries_iterable_scan_target_ids(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        days = 7
        scan_target_ids = [
            "e22f4225-43e9-4922-b6b8-8b0620bdb110",
            "e22f4225-43e9-4922-b6b8-8b0620bdb112",
        ]

        get_scan_summaries(organization_id, days=days, scan_target_ids=scan_target_ids)

        Client._request.assert_called_once_with(
            "POST",
            f"/alerts/summaries/scans",
            body={
                "organizationId": organization_id,
                "daysBefore": days,
                "scanTargetIds": scan_target_ids,
            },
        )

    def test_get_following_scan_summaries(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        days = 7

        get_following_scan_summaries(organization_id, days=days)

        Client._request.assert_called_once_with(
            "POST",
            f"/alerts/summaries/scans/following",
            body={"organizationId": organization_id, "daysBefore": days},
        )

    def test_get_following_scan_summaries_str_following_ids(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        days = 7
        following_ids = "e22f4225-43e9-4922-b6b8-8b0620bdb110"

        get_following_scan_summaries(
            organization_id, days=days, following_ids=following_ids
        )

        Client._request.assert_called_once_with(
            "POST",
            f"/alerts/summaries/scans/following",
            body={
                "organizationId": organization_id,
                "daysBefore": days,
                "followingIds": [following_ids],
            },
        )

    def test_get_following_scan_summaries_iterable_following_ids(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        days = 7
        following_ids = [
            "e22f4225-43e9-4922-b6b8-8b0620bdb110",
            "e22f4225-43e9-4922-b6b8-8b0620bdb112",
        ]

        get_following_scan_summaries(
            organization_id, days=days, following_ids=following_ids
        )

        Client._request.assert_called_once_with(
            "POST",
            f"/alerts/summaries/scans/following",
            body={
                "organizationId": organization_id,
                "daysBefore": days,
                "followingIds": following_ids,
            },
        )
