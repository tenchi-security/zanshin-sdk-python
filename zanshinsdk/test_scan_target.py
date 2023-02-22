import unittest

from client import (
    Client,
    ScanTargetAWS,
    ScanTargetAZURE,
    ScanTargetDOMAIN,
    ScanTargetGCP,
    ScanTargetHUAWEI,
    ScanTargetKind,
    ScanTargetORACLE,
    ScanTargetSchedule,
)
from scan_target import (
    check_organization_scan_target,
    create_organization_scan_target,
    delete_organization_scan_target,
    get_gworkspace_oauth_link,
    get_organization_scan_target,
    iter_organization_scan_targets,
    start_organization_scan_target_scan,
    stop_organization_scan_target_scan,
    update_organization_scan_target,
)

###################################################
# Organization Scan Target
###################################################


class ScanTargetTest(unittest.TestCase):
    def test_iter_organization_scan_targets(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"

        try:
            next(iter_organization_scan_targets(organization_id))
        except StopIteration:
            pass

        Client._request.assert_called_once_with(
            "GET", f"/organizations/{organization_id}/scantargets"
        )

    def test_create_organization_scan_target_AWS(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        kind = ScanTargetKind.AWS
        name = "ScanTargetTest"
        credential = ScanTargetAWS("123456")
        schedule = "24h"

        create_organization_scan_target(
            organization_id, kind, name, credential, schedule
        )

        Client._request.assert_called_once_with(
            "POST",
            f"/organizations/{organization_id}/scantargets",
            body={
                "name": name,
                "kind": kind,
                "credential": credential,
                "schedule": schedule,
            },
        )

    def test_create_organization_scan_target_AZURE(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        kind = ScanTargetKind.AZURE
        name = "ScanTargetTest"
        credential = ScanTargetAZURE("1234567890", "0123456789", "2345678901", "SECRET")
        schedule = "24h"

        create_organization_scan_target(
            organization_id, kind, name, credential, schedule
        )

        Client._request.assert_called_once_with(
            "POST",
            f"/organizations/{organization_id}/scantargets",
            body={
                "name": name,
                "kind": kind,
                "credential": credential,
                "schedule": schedule,
            },
        )

    def test_create_organization_scan_target_GCP(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        kind = ScanTargetKind.GCP
        name = "ScanTargetTest"
        credential = ScanTargetGCP("123456")
        schedule = "24h"

        create_organization_scan_target(
            organization_id, kind, name, credential, schedule
        )

        Client._request.assert_called_once_with(
            "POST",
            f"/organizations/{organization_id}/scantargets",
            body={
                "name": name,
                "kind": kind,
                "credential": credential,
                "schedule": schedule,
            },
        )

    def test_create_organization_scan_target_HUAWEI(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        kind = ScanTargetKind.HUAWEI
        name = "ScanTargetTest"
        credential = ScanTargetHUAWEI("123456")
        schedule = "24h"

        create_organization_scan_target(
            organization_id, kind, name, credential, schedule
        )

        Client._request.assert_called_once_with(
            "POST",
            f"/organizations/{organization_id}/scantargets",
            body={
                "name": name,
                "kind": kind,
                "credential": credential,
                "schedule": schedule,
            },
        )

    def test_create_organization_scan_target_DOMAIN(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        kind = ScanTargetKind.DOMAIN
        name = "ScanTargetTest"
        credential = ScanTargetDOMAIN("domain.com")
        schedule = "24h"

        create_organization_scan_target(
            organization_id, kind, name, credential, schedule
        )

        Client._request.assert_called_once_with(
            "POST",
            f"/organizations/{organization_id}/scantargets",
            body={
                "name": name,
                "kind": kind,
                "credential": credential,
                "schedule": schedule,
            },
        )

    def test_get_organization_scan_target(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        scan_target_id = "e22f4225-43e9-4922-b6b8-8b0620bdb110"

        get_organization_scan_target(organization_id, scan_target_id)

        Client._request.assert_called_once_with(
            "GET", f"/organizations/{organization_id}/scantargets/{scan_target_id}"
        )

    def test_update_organization_scan_target(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        scan_target_id = "e22f4225-43e9-4922-b6b8-8b0620bdb110"
        name = "ScanTargetTest"
        schedule = "24h"

        update_organization_scan_target(organization_id, scan_target_id, name, schedule)

        Client._request.assert_called_once_with(
            "PUT",
            f"/organizations/{organization_id}/scantargets/{scan_target_id}",
            body={"name": name, "schedule": schedule},
        )

    def test_delete_organization_scan_target(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        scan_target_id = "e22f4225-43e9-4922-b6b8-8b0620bdb110"

        delete_organization_scan_target(organization_id, scan_target_id)

        Client._request.assert_called_once_with(
            "DELETE", f"/organizations/{organization_id}/scantargets/{scan_target_id}"
        )

    def test_start_organization_scan_target_scan(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        scan_target_id = "e22f4225-43e9-4922-b6b8-8b0620bdb110"

        start_organization_scan_target_scan(organization_id, scan_target_id, True)

        Client._request.assert_called_once_with(
            "POST",
            f"/organizations/{organization_id}/scantargets/{scan_target_id}/scan",
            params={"force": "true"},
        )

    def test_stop_organization_scan_target_scan(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        scan_target_id = "e22f4225-43e9-4922-b6b8-8b0620bdb110"

        stop_organization_scan_target_scan(organization_id, scan_target_id)

        Client._request.assert_called_once_with(
            "POST",
            f"/organizations/{organization_id}/scantargets/{scan_target_id}/stop",
        )

    def test_check_organization_scan_target(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        scan_target_id = "e22f4225-43e9-4922-b6b8-8b0620bdb110"

        check_organization_scan_target(organization_id, scan_target_id)

        Client._request.assert_called_once_with(
            "POST",
            f"/organizations/{organization_id}/scantargets/{scan_target_id}/check",
        )

    def test_get_gworkspace_oauth_link(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        scan_target_id = "e22f4225-43e9-4922-b6b8-8b0620bdb110"
        get_gworkspace_oauth_link(organization_id, scan_target_id)

        Client._request.assert_called_once_with(
            "GET",
            f"/gworkspace/oauth/link?scanTargetId={scan_target_id}"
            f"&organizationId={organization_id}",
        )
