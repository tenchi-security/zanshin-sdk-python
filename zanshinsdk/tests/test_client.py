import os
import unittest
from pathlib import Path
from unittest.mock import Mock, call, patch
from uuid import UUID

import zanshinsdk


class TestClient(unittest.TestCase):
    ###################################################
    # setUp
    ###################################################

    @patch("zanshinsdk.client.isfile")
    @patch("zanshinsdk.Client._request")
    def setUp(self, request, mock_is_file):
        mock_is_file.return_value = True

        self.sdk = zanshinsdk.Client(
            profile=False,
            api_key="api_key",
            api_url="https://api.test",
            user_agent="test_agent"
        )
        self.sdk._request = request

        self.HAVE_BOTO3 = False
        try:
            import boto3

            self.HAVE_BOTO3 = True
        except ModuleNotFoundError:
            pass
            self.HAVE_BOTO3 = False

    ###################################################
    # __mock_aws_credentials__
    ###################################################

    def mock_aws_credentials(self):
        """Mocked AWS Credentials for moto."""
        moto_credentials_file_path = (
            Path(__file__).parent.absolute() / "data/dummy_aws_credentials"
        )
        os.environ["AWS_SHARED_CREDENTIALS_FILE"] = str(moto_credentials_file_path)

    ###################################################
    # Account
    ###################################################

    def test_get_me(self):
        self.sdk.get_me()

        self.sdk._request.assert_called_once_with("GET", "/me")

    ###################################################
    # Account Invites
    ###################################################

    def test_iter_invites(self):
        try:
            next(self.sdk.iter_invites())
        except StopIteration:
            pass

        self.sdk._request.assert_called_once_with("GET", "/me/invites")

    def test_get_invite(self):
        invite_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"

        self.sdk.get_invite(invite_id)

        self.sdk._request.assert_called_once_with("GET", f"/me/invites/{invite_id}")

    def test_accept_invite(self):
        invite_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"

        self.sdk.accept_invite(invite_id)

        self.sdk._request.assert_called_once_with(
            "POST", f"/me/invites/{invite_id}/accept"
        )

    ###################################################
    # Account API key
    ###################################################

    def test_iter_api_keys(self):
        try:
            next(self.sdk.iter_api_keys())
        except StopIteration:
            pass

        self.sdk._request.assert_called_once_with("GET", "/me/apikeys")

    def test_create_api_key(self):
        name = "MyKey"

        self.sdk.create_api_key(name)

        self.sdk._request.assert_called_once_with(
            "POST", "/me/apikeys", body={"name": name}
        )

    def test_delete_api_key(self):
        api_key = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"

        self.sdk.delete_api_key(api_key)

        self.sdk._request.assert_called_once_with("DELETE", f"/me/apikeys/{api_key}")

    ###################################################
    # Organization
    ###################################################

    def test_iter_organizations(self):
        try:
            next(self.sdk.iter_organizations())
        except StopIteration:
            pass

        self.sdk._request.assert_called_once_with("GET", "/organizations")

    def test_get_organization(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"

        self.sdk.get_organization(organization_id)

        self.sdk._request.assert_called_once_with(
            "GET", f"/organizations/{organization_id}"
        )

    def test_delete_organization(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"

        self.sdk.delete_organization(organization_id)

        self.sdk._request.assert_called_once_with(
            "DELETE", f"/organizations/{organization_id}"
        )

    def test_update_organization(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        name = "Tabajara"
        picture = "https://pic-store.com/pic1.png"
        email = "ceo@tabajara.com.br"

        self.sdk.update_organization(organization_id, name, picture, email)

        self.sdk._request.assert_called_once_with(
            "PUT",
            f"/organizations/{organization_id}",
            body={"name": name, "picture": picture, "email": email},
        )

    def test_create_organization(self):
        name = "Tabajara"

        self.sdk.create_organization(name)

        self.sdk._request.assert_called_once_with(
            "POST", f"/organizations", body={"name": name}
        )

    ###################################################
    # Organization Member
    ###################################################

    def test_iter_organization_members(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"

        try:
            next(self.sdk.iter_organization_members(organization_id))
        except StopIteration:
            pass

        self.sdk._request.assert_called_once_with(
            "GET", f"/organizations/{organization_id}/members"
        )

    def test_get_organization_members(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        member_id = "e22f4225-43e9-4922-b6b8-8b0620bdb110"

        self.sdk.get_organization_member(organization_id, member_id)

        self.sdk._request.assert_called_once_with(
            "GET", f"/organizations/{organization_id}/members/{member_id}"
        )

    def test_update_organization_members(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        member_id = "e22f4225-43e9-4922-b6b8-8b0620bdb110"
        role = [zanshinsdk.Roles.ADMIN]

        self.sdk.update_organization_member(organization_id, member_id, role)

        self.sdk._request.assert_called_once_with(
            "PUT",
            f"/organizations/{organization_id}/members/{member_id}",
            body={"roles": role},
        )

    def test_delete_organization_members(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        member_id = "e22f4225-43e9-4922-b6b8-8b0620bdb110"

        self.sdk.delete_organization_member(organization_id, member_id)

        self.sdk._request.assert_called_once_with(
            "DELETE", f"/organizations/{organization_id}/members/{member_id}"
        )

    def test_reset_organization_member_mfa(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        member_id = "e22f4225-43e9-4922-b6b8-8b0620bdb110"

        self.sdk.reset_organization_member_mfa(organization_id, member_id)

        self.sdk._request.assert_called_once_with(
            "POST", f"/organizations/{organization_id}/members/{member_id}/mfa/reset"
        )

    def test_reset_delete_organization_password(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        member_id = "e22f4225-43e9-4922-b6b8-8b0620bdb110"

        self.sdk.reset_delete_organization_password(organization_id, member_id)

        self.sdk._request.assert_called_once_with(
            "POST",
            f"/organizations/{organization_id}/members/{member_id}/password/reset",
        )

    ###################################################
    # Organization Member Invite
    ###################################################

    def test_iter_organization_members_invites(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"

        try:
            next(self.sdk.iter_organization_members_invites(organization_id))
        except StopIteration:
            pass

        self.sdk._request.assert_called_once_with(
            "GET", f"/organizations/{organization_id}/invites"
        )

    def test_create_organization_members_invite(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        email = "juca@example.com"
        role = [zanshinsdk.Roles.ADMIN]

        self.sdk.create_organization_members_invite(organization_id, email, role)

        self.sdk._request.assert_called_once_with(
            "POST",
            f"/organizations/{organization_id}/invites",
            body={"email": email, "roles": role},
        )

    def test_get_organization_member_invite(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        email = "juca@example.com"

        self.sdk.get_organization_member_invite(organization_id, email)

        self.sdk._request.assert_called_once_with(
            "GET", f"/organizations/{organization_id}/invites/{email}"
        )

    def test_delete_organization_member_invite(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        email = "juca@example.com"

        self.sdk.delete_organization_member_invite(organization_id, email)

        self.sdk._request.assert_called_once_with(
            "DELETE", f"/organizations/{organization_id}/invites/{email}"
        )

    def test_resend_organization_member_invite(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        email = "juca@example.com"

        self.sdk.resend_organization_member_invite(organization_id, email)

        self.sdk._request.assert_called_once_with(
            "POST", f"/organizations/{organization_id}/invites/{email}/resend"
        )

    ###################################################
    # Organization Follower
    ###################################################

    def test_iter_organization_followers(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"

        try:
            next(self.sdk.iter_organization_followers(organization_id))
        except StopIteration:
            pass

        self.sdk._request.assert_called_once_with(
            "GET", f"/organizations/{organization_id}/followers"
        )

    def test_stop_organization_follower(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        follower_id = "e22f4225-43e9-4922-b6b8-8b0620bdb110"

        self.sdk.stop_organization_follower(organization_id, follower_id)

        self.sdk._request.assert_called_once_with(
            "DELETE", f"/organizations/{organization_id}/followers/{follower_id}"
        )

    ###################################################
    # Organization Follower Request
    ###################################################

    def test_iter_organization_follower_requests(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        try:
            next(self.sdk.iter_organization_follower_requests(organization_id))
        except StopIteration:
            pass

        self.sdk._request.assert_called_once_with(
            "GET", f"/organizations/{organization_id}/followers/requests"
        )

    def test_create_organization_follower_request(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        token = "e22f4225-43e9-4922-b6b8-8b0620bdb110"

        self.sdk.create_organization_follower_request(organization_id, token)

        self.sdk._request.assert_called_once_with(
            "POST",
            f"/organizations/{organization_id}/followers/requests",
            body={"token": token},
        )

    def test_get_organization_follower_request(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        follower_id = "e22f4225-43e9-4922-b6b8-8b0620bdb110"

        self.sdk.get_organization_follower_request(organization_id, follower_id)

        self.sdk._request.assert_called_once_with(
            "GET", f"/organizations/{organization_id}/followers/requests/{follower_id}"
        )

    def test_delete_organization_follower_request(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        follower_id = "e22f4225-43e9-4922-b6b8-8b0620bdb110"

        self.sdk.delete_organization_follower_request(organization_id, follower_id)

        self.sdk._request.assert_called_once_with(
            "DELETE",
            f"/organizations/{organization_id}/followers/requests/{follower_id}",
        )

    ###################################################
    # Organization Following
    ###################################################

    def test_iter_organization_following(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"

        try:
            next(self.sdk.iter_organization_following(organization_id))
        except StopIteration:
            pass

        self.sdk._request.assert_called_once_with(
            "GET", f"/organizations/{organization_id}/following"
        )

    def test_stop_organization_following(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        following_id = "e22f4225-43e9-4922-b6b8-8b0620bdb110"

        self.sdk.stop_organization_following(organization_id, following_id)

        self.sdk._request.assert_called_once_with(
            "DELETE", f"/organizations/{organization_id}/following/{following_id}"
        )

    ###################################################
    # Organization Following Request
    ###################################################

    def test_iter_organization_following_requests(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"

        try:
            next(self.sdk.iter_organization_following_requests(organization_id))
        except StopIteration:
            pass

        self.sdk._request.assert_called_once_with(
            "GET", f"/organizations/{organization_id}/following/requests"
        )

    def test_get_organization_following_request(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        following_id = "e22f4225-43e9-4922-b6b8-8b0620bdb110"

        self.sdk.get_organization_following_request(organization_id, following_id)

        self.sdk._request.assert_called_once_with(
            "GET", f"/organizations/{organization_id}/following/requests/{following_id}"
        )

    def test_accept_organization_following_request(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        following_id = "e22f4225-43e9-4922-b6b8-8b0620bdb110"

        self.sdk.accept_organization_following_request(organization_id, following_id)

        self.sdk._request.assert_called_once_with(
            "POST",
            f"/organizations/{organization_id}/following/requests/{following_id}/accept",
        )

    def test_decline_organization_following_request(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        following_id = "e22f4225-43e9-4922-b6b8-8b0620bdb110"

        self.sdk.decline_organization_following_request(organization_id, following_id)

        self.sdk._request.assert_called_once_with(
            "POST",
            f"/organizations/{organization_id}/following/requests/{following_id}/decline",
        )

    ###################################################
    # Organization Scan Target
    ###################################################

    def test_iter_organization_scan_targets(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"

        try:
            next(self.sdk.iter_organization_scan_targets(organization_id))
        except StopIteration:
            pass

        self.sdk._request.assert_called_once_with(
            "GET", f"/organizations/{organization_id}/scantargets"
        )

    def test_create_organization_scan_target_AWS(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        kind = zanshinsdk.ScanTargetKind.AWS
        name = "ScanTargetTest"
        credential = zanshinsdk.ScanTargetAWS("123456")
        schedule = zanshinsdk.DAILY

        self.sdk.create_organization_scan_target(
            organization_id, kind, name, credential, schedule
        )

        self.sdk._request.assert_called_once_with(
            "POST",
            f"/organizations/{organization_id}/scantargets",
            body={
                "name": name,
                "kind": kind,
                "credential": credential,
                "schedule": {"frequency": "1d", "timeOfDay": "NIGHT"},
            },
        )

    def test_create_organization_scan_target_AZURE(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        kind = zanshinsdk.ScanTargetKind.AZURE
        name = "ScanTargetTest"
        credential = zanshinsdk.ScanTargetAZURE(
            "1234567890", "0123456789", "2345678901", "SECRET"
        )
        schedule = zanshinsdk.DAILY

        self.sdk.create_organization_scan_target(
            organization_id, kind, name, credential, schedule
        )

        self.sdk._request.assert_called_once_with(
            "POST",
            f"/organizations/{organization_id}/scantargets",
            body={
                "name": name,
                "kind": kind,
                "credential": credential,
                "schedule": {"frequency": "1d", "timeOfDay": "NIGHT"},
            },
        )

    def test_create_organization_scan_target_GCP(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        kind = zanshinsdk.ScanTargetKind.GCP
        name = "ScanTargetTest"
        credential = zanshinsdk.ScanTargetGCP("123456")
        schedule = zanshinsdk.DAILY

        self.sdk.create_organization_scan_target(
            organization_id, kind, name, credential, schedule
        )

        self.sdk._request.assert_called_once_with(
            "POST",
            f"/organizations/{organization_id}/scantargets",
            body={
                "name": name,
                "kind": kind,
                "credential": credential,
                "schedule": {"frequency": "1d", "timeOfDay": "NIGHT"},
            },
        )

    def test_create_organization_scan_target_HUAWEI(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        kind = zanshinsdk.ScanTargetKind.HUAWEI
        name = "ScanTargetTest"
        credential = zanshinsdk.ScanTargetHUAWEI("123456")
        schedule = zanshinsdk.DAILY

        self.sdk.create_organization_scan_target(
            organization_id, kind, name, credential, schedule
        )

        self.sdk._request.assert_called_once_with(
            "POST",
            f"/organizations/{organization_id}/scantargets",
            body={
                "name": name,
                "kind": kind,
                "credential": credential,
                "schedule": {"frequency": "1d", "timeOfDay": "NIGHT"},
            },
        )

    def test_create_organization_scan_target_DOMAIN(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        kind = zanshinsdk.ScanTargetKind.DOMAIN
        name = "ScanTargetTest"
        credential = zanshinsdk.ScanTargetDOMAIN("domain.com")
        schedule = zanshinsdk.DAILY

        self.sdk.create_organization_scan_target(
            organization_id, kind, name, credential, schedule
        )

        self.sdk._request.assert_called_once_with(
            "POST",
            f"/organizations/{organization_id}/scantargets",
            body={
                "name": name,
                "kind": kind,
                "credential": credential,
                "schedule": {"frequency": "1d", "timeOfDay": "NIGHT"},
            },
        )

    def test_get_organization_scan_target(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        scan_target_id = "e22f4225-43e9-4922-b6b8-8b0620bdb110"

        self.sdk.get_organization_scan_target(organization_id, scan_target_id)

        self.sdk._request.assert_called_once_with(
            "GET", f"/organizations/{organization_id}/scantargets/{scan_target_id}"
        )

    def test_update_organization_scan_target(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        scan_target_id = "e22f4225-43e9-4922-b6b8-8b0620bdb110"
        name = "ScanTargetTest"
        schedule = zanshinsdk.DAILY

        self.sdk.update_organization_scan_target(
            organization_id, scan_target_id, name, schedule
        )

        self.sdk._request.assert_called_once_with(
            "PUT",
            f"/organizations/{organization_id}/scantargets/{scan_target_id}",
            body={
                "name": name,
                "schedule": {"frequency": "1d", "timeOfDay": "NIGHT"},
            },
        )

    def test_delete_organization_scan_target(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        scan_target_id = "e22f4225-43e9-4922-b6b8-8b0620bdb110"

        self.sdk.delete_organization_scan_target(organization_id, scan_target_id)

        self.sdk._request.assert_called_once_with(
            "DELETE", f"/organizations/{organization_id}/scantargets/{scan_target_id}"
        )

    def test_start_organization_scan_target_scan(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        scan_target_id = "e22f4225-43e9-4922-b6b8-8b0620bdb110"

        self.sdk.start_organization_scan_target_scan(
            organization_id, scan_target_id, True
        )

        self.sdk._request.assert_called_once_with(
            "POST",
            f"/organizations/{organization_id}/scantargets/{scan_target_id}/scan",
            params={"force": "true"},
        )

    def test_stop_organization_scan_target_scan(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        scan_target_id = "e22f4225-43e9-4922-b6b8-8b0620bdb110"

        self.sdk.stop_organization_scan_target_scan(organization_id, scan_target_id)

        self.sdk._request.assert_called_once_with(
            "POST",
            f"/organizations/{organization_id}/scantargets/{scan_target_id}/stop",
        )

    def test_check_organization_scan_target(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        scan_target_id = "e22f4225-43e9-4922-b6b8-8b0620bdb110"

        self.sdk.check_organization_scan_target(organization_id, scan_target_id)

        self.sdk._request.assert_called_once_with(
            "POST",
            f"/organizations/{organization_id}/scantargets/{scan_target_id}/check",
        )

    def test_get_scan_target_group_oauth_link_should_call_apiß(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        scan_target_group_id = "e22f4225-43e9-4922-b6b8-8b0620bdb110"

        self.sdk.get_scan_target_group_oauth_link(organization_id, scan_target_group_id)

        self.sdk._request.assert_called_once_with(
            "GET",
            f"/oauth/link?"
            f"organizationId={organization_id}"
            f"&scanTargetGroupId={scan_target_group_id}",
        )

    def test_get_scan_target_oauth_link_should_call_api_with_scan_target_group_id(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        scan_target_id = "e22f4225-43e9-4922-b6b8-8b0620bdb110"

        self.sdk.get_scan_target_oauth_link(organization_id, scan_target_id)

        self.sdk._request.assert_called_once_with(
            "GET",
            f"/oauth/link?"
            f"organizationId={organization_id}"
            f"&scanTargetId={scan_target_id}",
        )

    def test_get_gworkspace_oauth_link(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        scan_target_id = "e22f4225-43e9-4922-b6b8-8b0620bdb110"
        self.sdk.get_gworkspace_oauth_link(organization_id, scan_target_id)

        self.sdk._request.assert_called_once_with(
            "GET",
            f"/gworkspace/oauth/link?scanTargetId={scan_target_id}"
            f"&organizationId={organization_id}",
        )

    ###################################################
    # Organization Scan Target Scan
    ###################################################
    def test_iter_organization_scan_target_scans_request(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        scan_target_id = "e22f4225-43e9-4922-b6b8-8b0620bdb110"

        try:
            next(
                self.sdk.iter_organization_scan_target_scans(
                    organization_id, scan_target_id
                )
            )
        except StopIteration:
            pass

        self.sdk._request.assert_called_once_with(
            "GET",
            f"/organizations/{organization_id}/scantargets/{scan_target_id}/scans",
        )

    @patch("zanshinsdk.client.isfile")
    @patch("zanshinsdk.Client._request")
    def test_iter_organization_scan_target_scans_response(self, request, mock_is_file):
        organization_id = "f59fd172-d968-4e94-9cc7-bc1ed33155f1"
        scan_target_id = "0c89dc67-eeec-4004-8ca4-98669047417a"
        scan_data = {
            "summary": {
                "infos": {
                    "NEW": {"HIGH": 0, "INFO": 0, "MEDIUM": 0, "LOW": 0, "CRITICAL": 0},
                    "COLLECTED": 6726,
                    "REOPEN": {
                        "HIGH": 0,
                        "INFO": 0,
                        "MEDIUM": 0,
                        "LOW": 0,
                        "CRITICAL": 0,
                    },
                    "CLOSED": {
                        "HIGH": 0,
                        "INFO": 0,
                        "MEDIUM": 0,
                        "LOW": 0,
                        "CRITICAL": 0,
                    },
                    "UNKNOWN": 485,
                    "FAIL": 642,
                    "OPEN": {
                        "HIGH": 0,
                        "MEDIUM": 0,
                        "INFO": 0,
                        "LOW": 0,
                        "CRITICAL": 0,
                    },
                },
                "states": {"CLOSED": 442, "OPEN": 638, "RISK_ACCEPTED": 4},
                "severities": {
                    "HIGH": 55,
                    "INFO": 49,
                    "MEDIUM": 283,
                    "LOW": 232,
                    "CRITICAL": 23,
                },
            },
            "updatedAt": "2022-07-10T00:10:24.593646",
            "status": "DONE",
            "createdAt": "2022-07-10T00:04:08.076Z",
            "scanTargetId": scan_target_id,
            "slot": "2022-07-10T00:04:07.953Z",
            "organizationId": organization_id,
        }

        mock_is_file.return_value = True
        
        request.return_value = Mock(
            status_code=200, json=lambda: {"data": [scan_data]}
        )
        client = zanshinsdk.Client(
            profile=False,
            api_key="api_key",
            api_url="https://api.test",
            user_agent="test_agent"
        )
        client._client.request = request

        iter = client.iter_organization_scan_target_scans(
            organization_id, scan_target_id
        )

        self.assertDictEqual(iter.__next__(), scan_data)
        self.assertRaises(StopIteration, iter.__next__)

    def test_get_organization_scan_target_scan(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        scan_target_id = "e22f4225-43e9-4922-b6b8-8b0620bdb110"
        scan_id = "e22f4225-43e9-4922-b6b8-8b0620bdb112"

        self.sdk.get_organization_scan_target_scan(
            organization_id, scan_target_id, scan_id
        )

        self.sdk._request.assert_called_once_with(
            "GET",
            f"/organizations/{organization_id}/scantargets/{scan_target_id}/scans/{scan_id}",
        )

    ###################################################
    # Organization Scan Target Groups
    ###################################################

    def test_iter_organization_scan_target_groups(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"

        try:
            next(self.sdk.iter_organization_scan_target_groups(organization_id))
        except StopIteration:
            pass

        self.sdk._request.assert_called_once_with(
            "GET", f"/organizations/{organization_id}/scantargetgroups"
        )

        with self.assertRaises(TypeError):
            next(self.sdk.iter_organization_scan_target_groups(1))
        with self.assertRaises(TypeError):
            next(self.sdk.iter_organization_scan_target_groups(None))
        with self.assertRaises(ValueError):
            next(self.sdk.iter_organization_scan_target_groups(""))
        with self.assertRaises(ValueError):
            next(self.sdk.iter_organization_scan_target_groups("foo"))

    def test_get_organization_scan_target_group(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        scan_target_group_id = "322f4225-43e9-4922-b6b8-8b0620bdb110"

        self.sdk.get_organization_scan_target_group(
            organization_id, scan_target_group_id
        )

        self.sdk._request.assert_called_once_with(
            "GET",
            f"/organizations/{organization_id}/scantargetgroups/{scan_target_group_id}",
        )
        with self.assertRaises(TypeError):
            self.sdk.get_organization_scan_target_group(None, scan_target_group_id)
        with self.assertRaises(TypeError):
            self.sdk.get_organization_scan_target_group(1, scan_target_group_id)
        with self.assertRaises(TypeError):
            self.sdk.get_organization_scan_target_group(organization_id, None)
        with self.assertRaises(TypeError):
            self.sdk.get_organization_scan_target_group(organization_id, 1)
        with self.assertRaises(ValueError):
            self.sdk.get_organization_scan_target_group(organization_id, "")
        with self.assertRaises(ValueError):
            self.sdk.get_organization_scan_target_group(organization_id, "foo")
        with self.assertRaises(ValueError):
            self.sdk.get_organization_scan_target_group("", scan_target_group_id)
        with self.assertRaises(ValueError):
            self.sdk.get_organization_scan_target_group("foo", scan_target_group_id)

    def test_update_scan_target_group(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        scan_target_group_id = "e22f4225-43e9-4922-b6b8-8b0620bdb110"
        name = "ScanTargetGroupTest"

        self.sdk.update_scan_target_group(organization_id, scan_target_group_id, name)

        self.sdk._request.assert_called_once_with(
            "PUT",
            f"/organizations/{organization_id}/scantargetgroups/{scan_target_group_id}",
            body={"name": name},
        )

    def test_create_scan_target_group_should_call_api_with_valid_kind(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        kind = zanshinsdk.ScanTargetKind.BITBUCKET
        name = "ScanTargetTest"

        self.sdk.create_scan_target_group(organization_id, kind, name)

        self.sdk._request.assert_called_once_with(
            "POST",
            f"/organizations/{organization_id}/scantargetgroups",
            body={"name": name, "kind": kind},
        )

    def test_create_scan_target_group_should_throw_exception_with_invalid_kind(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        kind = zanshinsdk.ScanTargetKind.AWS
        name = "ScanTargetTest"

        with self.assertRaises(ValueError):
            self.sdk.create_scan_target_group(organization_id, kind, name)

    def test_iter_scan_target_group_compartments(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        scan_target_group_id = "322f4225-43e9-4922-b6b8-8b0620bdb110"
        try:
            next(
                self.sdk.iter_scan_target_group_compartments(
                    organization_id, scan_target_group_id
                )
            )
        except StopIteration:
            pass
        self.sdk._request.assert_called_once_with(
            "GET",
            f"/organizations/{organization_id}/scantargetgroups/{scan_target_group_id}/targets",
        )
        with self.assertRaises(TypeError):
            next(self.sdk.iter_scan_target_group_compartments(1, scan_target_group_id))
        with self.assertRaises(TypeError):
            next(
                self.sdk.iter_scan_target_group_compartments(None, scan_target_group_id)
            )
        with self.assertRaises(ValueError):
            next(self.sdk.iter_scan_target_group_compartments("", scan_target_group_id))
        with self.assertRaises(ValueError):
            next(
                self.sdk.iter_scan_target_group_compartments(
                    "foo", scan_target_group_id
                )
            )
        with self.assertRaises(TypeError):
            next(self.sdk.iter_scan_target_group_compartments(organization_id, 1))
        with self.assertRaises(TypeError):
            next(self.sdk.iter_scan_target_group_compartments(organization_id, None))
        with self.assertRaises(ValueError):
            next(self.sdk.iter_scan_target_group_compartments(organization_id, ""))
        with self.assertRaises(ValueError):
            next(self.sdk.iter_scan_target_group_compartments(organization_id, "foo"))

    def test_create_scan_target_by_compartments(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        scan_target_group_id = "322f4225-43e9-4922-b6b8-8b0620bdb110"

        ocid = "ocid"
        name = "ScanTargetTest"

        self.sdk.create_scan_target_by_compartments(
            organization_id, scan_target_group_id, name, ocid
        )

        compartments = [{"name": name, "ocid": ocid}]

        body = {"compartments": compartments}

        self.sdk._request.assert_called_once_with(
            "POST",
            f"/organizations/{organization_id}/scantargetgroups/{scan_target_group_id}/targets",
            body=body,
        )

    def test_iter_scan_targets_from_group(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        scan_target_group_id = "322f4225-43e9-4922-b6b8-8b0620bdb110"

        try:
            next(
                self.sdk.iter_scan_targets_from_group(
                    organization_id, scan_target_group_id
                )
            )
        except StopIteration:
            pass

        self.sdk._request.assert_called_once_with(
            "GET",
            f"/organizations/{organization_id}/scantargetgroups/{scan_target_group_id}/scantargets",
        )

        with self.assertRaises(TypeError):
            next(self.sdk.iter_scan_targets_from_group(1, scan_target_group_id))
        with self.assertRaises(TypeError):
            next(self.sdk.iter_scan_targets_from_group(None, scan_target_group_id))
        with self.assertRaises(ValueError):
            next(self.sdk.iter_scan_targets_from_group("", scan_target_group_id))
        with self.assertRaises(ValueError):
            next(self.sdk.iter_scan_targets_from_group("foo", scan_target_group_id))
        with self.assertRaises(TypeError):
            next(self.sdk.iter_scan_targets_from_group(organization_id, 1))
        with self.assertRaises(TypeError):
            next(self.sdk.iter_scan_targets_from_group(organization_id, None))
        with self.assertRaises(ValueError):
            next(self.sdk.iter_scan_targets_from_group(organization_id, ""))
        with self.assertRaises(ValueError):
            next(self.sdk.iter_scan_targets_from_group(organization_id, "foo"))

    def test_delete_organization_scan_target_group(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        scan_target_id_group = "e22f4225-43e9-4922-b6b8-8b0620bdb110"

        self.sdk.delete_organization_scan_target_group(
            organization_id, scan_target_id_group
        )

        self.sdk._request.assert_called_once_with(
            "DELETE",
            f"/organizations/{organization_id}/scantargetgroups/{scan_target_id_group}",
        )
        with self.assertRaises(TypeError):
            self.sdk.delete_organization_scan_target_group(None, scan_target_id_group)
        with self.assertRaises(TypeError):
            self.sdk.delete_organization_scan_target_group(1, scan_target_id_group)
        with self.assertRaises(TypeError):
            self.sdk.delete_organization_scan_target_group(organization_id, None)
        with self.assertRaises(TypeError):
            self.sdk.delete_organization_scan_target_group(organization_id, 1)
        with self.assertRaises(ValueError):
            self.sdk.delete_organization_scan_target_group(organization_id, "")
        with self.assertRaises(ValueError):
            self.sdk.delete_organization_scan_target_group(organization_id, "foo")
        with self.assertRaises(ValueError):
            self.sdk.delete_organization_scan_target_group("", scan_target_id_group)
        with self.assertRaises(ValueError):
            self.sdk.delete_organization_scan_target_group("foo", scan_target_id_group)

    def test_get_scan_target_group_script(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        scan_target_group_id = "322f4225-43e9-4922-b6b8-8b0620bdb110"

        self.sdk.get_scan_target_group_script(organization_id, scan_target_group_id)

        self.sdk._request.assert_called_once_with(
            "GET",
            f"/organizations/{organization_id}/scantargetgroups/{scan_target_group_id}/scripts",
        )
        with self.assertRaises(TypeError):
            self.sdk.get_scan_target_group_script(None, scan_target_group_id)
        with self.assertRaises(TypeError):
            self.sdk.get_scan_target_group_script(1, scan_target_group_id)
        with self.assertRaises(TypeError):
            self.sdk.get_scan_target_group_script(organization_id, None)
        with self.assertRaises(TypeError):
            self.sdk.get_scan_target_group_script(organization_id, 1)
        with self.assertRaises(ValueError):
            self.sdk.get_scan_target_group_script(organization_id, "")
        with self.assertRaises(ValueError):
            self.sdk.get_scan_target_group_script(organization_id, "foo")
        with self.assertRaises(ValueError):
            self.sdk.get_scan_target_group_script("", scan_target_group_id)
        with self.assertRaises(ValueError):
            self.sdk.get_scan_target_group_script("foo", scan_target_group_id)

    def test_insert_scan_target_group_credential(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        scan_target_group_id = "e22f4225-43e9-4922-b6b8-8b0620bdb110"
        credential = zanshinsdk.ScanTargetGroupCredentialListORACLE(
            "us-ashburn-1",
            "ocid1.tenancy.oc1..aaaaaaaa0000000000000000000000000000000000000000000000000000",
            "ocid1.user.oc1..aaaaaaaa0000000000000000000000000000000000000000000000000000",
            "1a:1a:aa:1a:11:11:aa:11:11:11:1a:1a:1a:a:1a:1a",
        )

        self.sdk.insert_scan_target_group_credential(
            organization_id, scan_target_group_id, credential
        )

        self.sdk._request.assert_called_once_with(
            "POST",
            f"/organizations/{organization_id}/scantargetgroups/{scan_target_group_id}",
            body={"credential": credential},
        )
        with self.assertRaises(TypeError):
            self.sdk.insert_scan_target_group_credential(
                None, scan_target_group_id, credential
            )
        with self.assertRaises(TypeError):
            self.sdk.insert_scan_target_group_credential(
                1, scan_target_group_id, credential
            )
        with self.assertRaises(TypeError):
            self.sdk.insert_scan_target_group_credential(
                organization_id, None, credential
            )
        with self.assertRaises(TypeError):
            self.sdk.insert_scan_target_group_credential(organization_id, 1, credential)
        with self.assertRaises(ValueError):
            self.sdk.insert_scan_target_group_credential(
                organization_id, "", credential
            )
        with self.assertRaises(ValueError):
            self.sdk.insert_scan_target_group_credential(
                organization_id, "foo", credential
            )
        with self.assertRaises(ValueError):
            self.sdk.insert_scan_target_group_credential(
                "", scan_target_group_id, credential
            )
        with self.assertRaises(ValueError):
            self.sdk.insert_scan_target_group_credential(
                "foo", scan_target_group_id, credential
            )

    ###################################################
    # Alerts
    ###################################################

    def test_get_alerts_page(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        page = 1
        page_size = 100
        rule = "rule"
        language = zanshinsdk.Languages.EN_US
        # TODO: use valid dates
        created_at_start = "created_at_start"
        created_at_end = "created_at_end"
        updated_at_start = "updated_at_start"
        updated_at_end = "updated_at_end"
        search = "search"
        sort = zanshinsdk.SortOpts.ASC
        order = zanshinsdk.AlertsOrderOpts.SEVERITY

        self.sdk._get_alerts_page(
            organization_id,
            page=page,
            page_size=page_size,
            rule=rule,
            language=language,
            search=search,
            order=order,
            sort=sort,
            created_at_start=created_at_start,
            created_at_end=created_at_end,
            updated_at_start=updated_at_start,
            updated_at_end=updated_at_end,
        )

        self.sdk._request.assert_called_once_with(
            "POST",
            f"/alerts",
            body={
                "organizationId": organization_id,
                "page": page,
                "pageSize": page_size,
                "rule": rule,
                "lang": language,
                "search": search,
                "order": order,
                "sort": sort,
                "createdAtStart": created_at_start,
                "createdAtEnd": created_at_end,
                "updatedAtStart": updated_at_start,
                "updatedAtEnd": updated_at_end,
            },
        )

    def test_get_alerts_page_str_scan_target_ids(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        page = 1
        page_size = 100
        scan_target_ids = "e22f4225-43e9-4922-b6b8-8b0620bdb110"

        self.sdk._get_alerts_page(
            organization_id,
            page=page,
            page_size=page_size,
            scan_target_ids=scan_target_ids,
        )

        self.sdk._request.assert_called_once_with(
            "POST",
            f"/alerts",
            body={
                "organizationId": organization_id,
                "page": page,
                "pageSize": page_size,
                "scanTargetIds": [scan_target_ids],
            },
        )

    def test_get_alerts_page_iterable_scan_target_ids(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        page = 1
        page_size = 100
        scan_target_ids = [
            "e22f4225-43e9-4922-b6b8-8b0620bdb110",
            "e22f4225-43e9-4922-b6b8-8b0620bdb112",
        ]

        self.sdk._get_alerts_page(
            organization_id,
            page=page,
            page_size=page_size,
            scan_target_ids=scan_target_ids,
        )

        self.sdk._request.assert_called_once_with(
            "POST",
            f"/alerts",
            body={
                "organizationId": organization_id,
                "page": page,
                "pageSize": page_size,
                "scanTargetIds": scan_target_ids,
            },
        )

    def test_get_alerts_page_str_states(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        page = 1
        page_size = 100
        states = zanshinsdk.AlertState.OPEN

        self.sdk._get_alerts_page(
            organization_id, page=page, page_size=page_size, states=states
        )

        self.sdk._request.assert_called_once_with(
            "POST",
            f"/alerts",
            body={
                "organizationId": organization_id,
                "page": page,
                "pageSize": page_size,
                "states": [states],
            },
        )

    def test_get_alerts_page_iterable_states(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        page = 1
        page_size = 100
        states = [zanshinsdk.AlertState.OPEN, zanshinsdk.AlertState.CLOSED]

        self.sdk._get_alerts_page(
            organization_id, page=page, page_size=page_size, states=states
        )

        self.sdk._request.assert_called_once_with(
            "POST",
            f"/alerts",
            body={
                "organizationId": organization_id,
                "page": page,
                "pageSize": page_size,
                "states": states,
            },
        )

    def test_get_alerts_page_str_severities(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        page = 1
        page_size = 100
        severities = zanshinsdk.AlertSeverity.CRITICAL

        self.sdk._get_alerts_page(
            organization_id, page=page, page_size=page_size, severities=severities
        )

        self.sdk._request.assert_called_once_with(
            "POST",
            f"/alerts",
            body={
                "organizationId": organization_id,
                "page": page,
                "pageSize": page_size,
                "severities": [severities],
            },
        )

    def test_get_alerts_page_iterable_severities(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        page = 1
        page_size = 100
        severities = [zanshinsdk.AlertSeverity.CRITICAL, zanshinsdk.AlertSeverity.HIGH]

        self.sdk._get_alerts_page(
            organization_id, page=page, page_size=page_size, severities=severities
        )

        self.sdk._request.assert_called_once_with(
            "POST",
            f"/alerts",
            body={
                "organizationId": organization_id,
                "page": page,
                "pageSize": page_size,
                "severities": severities,
            },
        )

    @patch("zanshinsdk.client.Client._get_alerts_page")
    def test_iter_alerts(self, request):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        page = 1
        page_size = 1

        request.return_value = {
            "data": [""],
            "total": 2,
        }

        self.sdk._get_alerts_page = request
        iterator = self.sdk.iter_alerts(organization_id, page_size=page_size)

        next(iterator)
        next(iterator)

        self.sdk._get_alerts_page.assert_has_calls(
            [
                call(
                    organization_id,
                    None,
                    None,
                    None,
                    None,
                    page=page,
                    page_size=page_size,
                    language=None,
                    search=None,
                    order=None,
                    sort=None,
                    created_at_start=None,
                    created_at_end=None,
                    updated_at_start=None,
                    updated_at_end=None,
                ),
                call(
                    organization_id,
                    None,
                    None,
                    None,
                    None,
                    page=page + 1,
                    page_size=page_size,
                    language=None,
                    search=None,
                    order=None,
                    sort=None,
                    created_at_start=None,
                    created_at_end=None,
                    updated_at_start=None,
                    updated_at_end=None,
                ),
            ]
        )

    def test_get_following_alerts_page(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        page = 1
        page_size = 100
        rule = "rule"
        language = zanshinsdk.Languages.EN_US
        created_at_start = "created_at_start"
        created_at_end = "created_at_end"
        updated_at_start = "updated_at_start"
        updated_at_end = "updated_at_end"

        self.sdk._get_following_alerts_page(
            organization_id,
            page=page,
            page_size=page_size,
            rule=rule,
            language=language,
            created_at_start=created_at_start,
            created_at_end=created_at_end,
            updated_at_start=updated_at_start,
            updated_at_end=updated_at_end,
        )

        self.sdk._request.assert_called_once_with(
            "POST",
            f"/alerts/following",
            body={
                "organizationId": organization_id,
                "page": page,
                "pageSize": page_size,
                "rule": rule,
                "lang": language,
                "CreatedAtStart": created_at_start,
                "CreatedAtEnd": created_at_end,
                "UpdatedAtStart": updated_at_start,
                "UpdatedAtEnd": updated_at_end,
            },
        )

    def test_get_following_alerts_page_str_following_ids(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        page = 1
        page_size = 100
        following_ids = "e22f4225-43e9-4922-b6b8-8b0620bdb110"

        self.sdk._get_following_alerts_page(
            organization_id, page=page, page_size=page_size, following_ids=following_ids
        )

        self.sdk._request.assert_called_once_with(
            "POST",
            f"/alerts/following",
            body={
                "organizationId": organization_id,
                "page": page,
                "pageSize": page_size,
                "followingIds": [following_ids],
            },
        )

    def test_get_following_alerts_page_iterable_following_ids(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        page = 1
        page_size = 100
        following_ids = [
            "e22f4225-43e9-4922-b6b8-8b0620bdb110",
            "e22f4225-43e9-4922-b6b8-8b0620bdb112",
        ]

        self.sdk._get_following_alerts_page(
            organization_id, page=page, page_size=page_size, following_ids=following_ids
        )

        self.sdk._request.assert_called_once_with(
            "POST",
            f"/alerts/following",
            body={
                "organizationId": organization_id,
                "page": page,
                "pageSize": page_size,
                "followingIds": following_ids,
            },
        )

    def test_get_following_alerts_page_str_states(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        page = 1
        page_size = 100
        states = zanshinsdk.AlertState.OPEN

        self.sdk._get_following_alerts_page(
            organization_id, page=page, page_size=page_size, states=states
        )

        self.sdk._request.assert_called_once_with(
            "POST",
            f"/alerts/following",
            body={
                "organizationId": organization_id,
                "page": page,
                "pageSize": page_size,
                "states": [states],
            },
        )

    def test_get_following_alerts_page_iterable_states(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        page = 1
        page_size = 100
        states = [zanshinsdk.AlertState.OPEN, zanshinsdk.AlertState.CLOSED]

        self.sdk._get_following_alerts_page(
            organization_id, page=page, page_size=page_size, states=states
        )

        self.sdk._request.assert_called_once_with(
            "POST",
            f"/alerts/following",
            body={
                "organizationId": organization_id,
                "page": page,
                "pageSize": page_size,
                "states": states,
            },
        )

    def test_get_following_alerts_page_str_severities(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        page = 1
        page_size = 100
        severities = zanshinsdk.AlertSeverity.CRITICAL

        self.sdk._get_following_alerts_page(
            organization_id, page=page, page_size=page_size, severities=severities
        )

        self.sdk._request.assert_called_once_with(
            "POST",
            f"/alerts/following",
            body={
                "organizationId": organization_id,
                "page": page,
                "pageSize": page_size,
                "severities": [severities],
            },
        )

    def test_get_following_alerts_page_iterable_severities(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        page = 1
        page_size = 100
        severities = [zanshinsdk.AlertSeverity.CRITICAL, zanshinsdk.AlertSeverity.HIGH]

        self.sdk._get_following_alerts_page(
            organization_id, page=page, page_size=page_size, severities=severities
        )

        self.sdk._request.assert_called_once_with(
            "POST",
            f"/alerts/following",
            body={
                "organizationId": organization_id,
                "page": page,
                "pageSize": page_size,
                "severities": severities,
            },
        )

    @patch("zanshinsdk.client.Client._get_following_alerts_page")
    def test_iter_following_alerts(self, request):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        page = 1
        page_size = 1

        request.return_value = {
            "data": [""],
            "total": 2,
        }

        self.sdk._get_following_alerts_page = request
        iterator = self.sdk.iter_following_alerts(organization_id, page_size=page_size)

        next(iterator)
        next(iterator)

        self.sdk._get_following_alerts_page.assert_has_calls(
            [
                call(
                    organization_id,
                    None,
                    None,
                    None,
                    None,
                    page=page,
                    page_size=page_size,
                    language=None,
                    created_at_start=None,
                    created_at_end=None,
                    updated_at_start=None,
                    updated_at_end=None,
                    search=None,
                    order=None,
                    sort=None,
                ),
                call(
                    organization_id,
                    None,
                    None,
                    None,
                    None,
                    page=page + 1,
                    page_size=page_size,
                    language=None,
                    created_at_start=None,
                    created_at_end=None,
                    updated_at_start=None,
                    updated_at_end=None,
                    search=None,
                    order=None,
                    sort=None,
                ),
            ]
        )

    def test_get_alerts_history_page(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        page_size = 100
        language = zanshinsdk.Languages.EN_US
        cursor = "12345678"

        self.sdk._get_alerts_history_page(
            organization_id, page_size=page_size, language=language, cursor=cursor
        )

        self.sdk._request.assert_called_once_with(
            "POST",
            f"/alerts/history",
            body={
                "organizationId": organization_id,
                "pageSize": page_size,
                "lang": language,
                "cursor": cursor,
            },
        )

    def test_get_alerts_history_page_str_scan_target_ids(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        page_size = 100
        scan_target_ids = "e22f4225-43e9-4922-b6b8-8b0620bdb110"

        self.sdk._get_alerts_history_page(
            organization_id, page_size=page_size, scan_target_ids=scan_target_ids
        )

        self.sdk._request.assert_called_once_with(
            "POST",
            f"/alerts/history",
            body={
                "organizationId": organization_id,
                "pageSize": page_size,
                "scanTargetIds": [scan_target_ids],
            },
        )

    def test_get_alerts_history_page_iterable_scan_target_ids(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        page_size = 100
        scan_target_ids = [
            "e22f4225-43e9-4922-b6b8-8b0620bdb110",
            "e22f4225-43e9-4922-b6b8-8b0620bdb112",
        ]

        self.sdk._get_alerts_history_page(
            organization_id, page_size=page_size, scan_target_ids=scan_target_ids
        )

        self.sdk._request.assert_called_once_with(
            "POST",
            f"/alerts/history",
            body={
                "organizationId": organization_id,
                "pageSize": page_size,
                "scanTargetIds": scan_target_ids,
            },
        )

    @patch("zanshinsdk.client.Client._get_alerts_history_page")
    def test_iter_alerts_history(self, request):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        page_size = 1

        request.return_value = {
            "data": [{"cursor": 1}],
        }

        self.sdk._get_alerts_history_page = request
        iterator = self.sdk.iter_alerts_history(organization_id, page_size=page_size)

        next(iterator)
        next(iterator)

        self.sdk._get_alerts_history_page.assert_has_calls(
            [
                call(
                    organization_id,
                    None,
                    page_size=page_size,
                    language=None,
                    cursor=None,
                ),
                call(
                    organization_id, None, page_size=page_size, language=None, cursor=1
                ),
            ]
        )

    def test_get_alerts_following_history_page(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        page_size = 100
        language = zanshinsdk.Languages.EN_US
        cursor = "12345678"

        self.sdk._get_alerts_following_history_page(
            organization_id, page_size=page_size, language=language, cursor=cursor
        )

        self.sdk._request.assert_called_once_with(
            "POST",
            f"/alerts/history/following",
            body={
                "organizationId": organization_id,
                "pageSize": page_size,
                "lang": language,
                "cursor": cursor,
            },
        )

    def test_get_alerts_following_history_page_str_following_ids(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        page_size = 100
        following_ids = "e22f4225-43e9-4922-b6b8-8b0620bdb110"

        self.sdk._get_alerts_following_history_page(
            organization_id, page_size=page_size, following_ids=following_ids
        )

        self.sdk._request.assert_called_once_with(
            "POST",
            f"/alerts/history/following",
            body={
                "organizationId": organization_id,
                "pageSize": page_size,
                "followingIds": [following_ids],
            },
        )

    def test_get_alerts_following_history_page_iterable_following_ids(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        page_size = 100
        following_ids = [
            "e22f4225-43e9-4922-b6b8-8b0620bdb110",
            "e22f4225-43e9-4922-b6b8-8b0620bdb112",
        ]

        self.sdk._get_alerts_following_history_page(
            organization_id, page_size=page_size, following_ids=following_ids
        )

        self.sdk._request.assert_called_once_with(
            "POST",
            f"/alerts/history/following",
            body={
                "organizationId": organization_id,
                "pageSize": page_size,
                "followingIds": following_ids,
            },
        )

    @patch("zanshinsdk.client.Client._get_alerts_following_history_page")
    def test_iter_alerts_following_history(self, request):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        page_size = 1

        request.return_value = {
            "data": [{"cursor": 1}],
        }

        self.sdk._get_alerts_following_history_page = request
        iterator = self.sdk.iter_alerts_following_history(
            organization_id, page_size=page_size
        )

        next(iterator)
        next(iterator)

        self.sdk._get_alerts_following_history_page.assert_has_calls(
            [
                call(
                    organization_id,
                    None,
                    page_size=page_size,
                    language=None,
                    cursor=None,
                ),
                call(
                    organization_id, None, page_size=page_size, language=None, cursor=1
                ),
            ]
        )

    def test_get_grouped_alerts_page(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        page = 1
        page_size = 100

        self.sdk._get_grouped_alerts_page(
            organization_id, page=page, page_size=page_size
        )

        self.sdk._request.assert_called_once_with(
            "POST",
            f"/alerts/rules",
            body={
                "organizationId": organization_id,
                "page": page,
                "pageSize": page_size,
            },
        )

    def test_get_grouped_alerts_page_str_scan_target_ids(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        page = 1
        page_size = 100
        scan_target_ids = "e22f4225-43e9-4922-b6b8-8b0620bdb110"

        self.sdk._get_grouped_alerts_page(
            organization_id,
            page=page,
            page_size=page_size,
            scan_target_ids=scan_target_ids,
        )

        self.sdk._request.assert_called_once_with(
            "POST",
            f"/alerts/rules",
            body={
                "organizationId": organization_id,
                "page": page,
                "pageSize": page_size,
                "scanTargetIds": [scan_target_ids],
            },
        )

    def test_get_grouped_alerts_page_iterable_scan_target_ids(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        page = 1
        page_size = 100
        scan_target_ids = [
            "e22f4225-43e9-4922-b6b8-8b0620bdb110",
            "e22f4225-43e9-4922-b6b8-8b0620bdb112",
        ]

        self.sdk._get_grouped_alerts_page(
            organization_id,
            page=page,
            page_size=page_size,
            scan_target_ids=scan_target_ids,
        )

        self.sdk._request.assert_called_once_with(
            "POST",
            f"/alerts/rules",
            body={
                "organizationId": organization_id,
                "page": page,
                "pageSize": page_size,
                "scanTargetIds": scan_target_ids,
            },
        )

    def test_get_grouped_alerts_page_str_states(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        page = 1
        page_size = 100
        states = zanshinsdk.AlertState.OPEN

        self.sdk._get_grouped_alerts_page(
            organization_id, page=page, page_size=page_size, states=states
        )

        self.sdk._request.assert_called_once_with(
            "POST",
            f"/alerts/rules",
            body={
                "organizationId": organization_id,
                "page": page,
                "pageSize": page_size,
                "states": [states],
            },
        )

    def test_get_grouped_alerts_page_iterable_states(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        page = 1
        page_size = 100
        states = [zanshinsdk.AlertState.OPEN, zanshinsdk.AlertState.CLOSED]

        self.sdk._get_grouped_alerts_page(
            organization_id, page=page, page_size=page_size, states=states
        )

        self.sdk._request.assert_called_once_with(
            "POST",
            f"/alerts/rules",
            body={
                "organizationId": organization_id,
                "page": page,
                "pageSize": page_size,
                "states": states,
            },
        )

    def test_get_grouped_alerts_page_str_severities(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        page = 1
        page_size = 100
        severities = zanshinsdk.AlertSeverity.CRITICAL

        self.sdk._get_grouped_alerts_page(
            organization_id, page=page, page_size=page_size, severities=severities
        )

        self.sdk._request.assert_called_once_with(
            "POST",
            f"/alerts/rules",
            body={
                "organizationId": organization_id,
                "page": page,
                "pageSize": page_size,
                "severities": [severities],
            },
        )

    def test_get_grouped_alerts_page_iterable_severities(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        page = 1
        page_size = 100
        severities = [zanshinsdk.AlertSeverity.CRITICAL, zanshinsdk.AlertSeverity.HIGH]

        self.sdk._get_grouped_alerts_page(
            organization_id, page=page, page_size=page_size, severities=severities
        )

        self.sdk._request.assert_called_once_with(
            "POST",
            f"/alerts/rules",
            body={
                "organizationId": organization_id,
                "page": page,
                "pageSize": page_size,
                "severities": severities,
            },
        )

    @patch("zanshinsdk.client.Client._get_grouped_alerts_page")
    def test_iter_grouped_alerts(self, request):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        page = 1
        page_size = 1

        request.return_value = {"data": [""], "total": 2}

        self.sdk._get_grouped_alerts_page = request
        iterator = self.sdk.iter_grouped_alerts(organization_id, page_size=page_size)

        next(iterator)
        next(iterator)

        self.sdk._get_grouped_alerts_page.assert_has_calls(
            [
                call(
                    organization_id,
                    None,
                    None,
                    None,
                    page=page,
                    page_size=page_size,
                    language=None,
                    search=None,
                    order=None,
                    sort=None,
                ),
                call(
                    organization_id,
                    None,
                    None,
                    None,
                    page=page + 1,
                    page_size=page_size,
                    language=None,
                    search=None,
                    order=None,
                    sort=None,
                ),
            ]
        )

    def test_get_grouped_following_alerts_page(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        page = 1
        page_size = 100

        self.sdk._get_grouped_following_alerts_page(
            organization_id, page=page, page_size=page_size
        )

        self.sdk._request.assert_called_once_with(
            "POST",
            f"/alerts/rules/following",
            body={
                "organizationId": organization_id,
                "page": page,
                "pageSize": page_size,
            },
        )

    def test_get_grouped_following_alerts_page_str_following_ids(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        page = 1
        page_size = 100
        following_ids = "e22f4225-43e9-4922-b6b8-8b0620bdb110"

        self.sdk._get_grouped_following_alerts_page(
            organization_id, page=page, page_size=page_size, following_ids=following_ids
        )

        self.sdk._request.assert_called_once_with(
            "POST",
            f"/alerts/rules/following",
            body={
                "organizationId": organization_id,
                "page": page,
                "pageSize": page_size,
                "followingIds": [following_ids],
            },
        )

    def test_get_grouped_following_alerts_page_iterable_following_ids(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        page = 1
        page_size = 100
        following_ids = [
            "e22f4225-43e9-4922-b6b8-8b0620bdb110",
            "e22f4225-43e9-4922-b6b8-8b0620bdb112",
        ]

        self.sdk._get_grouped_following_alerts_page(
            organization_id, page=page, page_size=page_size, following_ids=following_ids
        )

        self.sdk._request.assert_called_once_with(
            "POST",
            f"/alerts/rules/following",
            body={
                "organizationId": organization_id,
                "page": page,
                "pageSize": page_size,
                "followingIds": following_ids,
            },
        )

    def test_get_grouped_following_alerts_page_str_states(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        page = 1
        page_size = 100
        states = zanshinsdk.AlertState.OPEN

        self.sdk._get_grouped_following_alerts_page(
            organization_id, page=page, page_size=page_size, states=states
        )

        self.sdk._request.assert_called_once_with(
            "POST",
            f"/alerts/rules/following",
            body={
                "organizationId": organization_id,
                "page": page,
                "pageSize": page_size,
                "states": [states],
            },
        )

    def test_get_grouped_following_alerts_page_iterable_states(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        page = 1
        page_size = 100
        states = [zanshinsdk.AlertState.OPEN, zanshinsdk.AlertState.CLOSED]

        self.sdk._get_grouped_following_alerts_page(
            organization_id, page=page, page_size=page_size, states=states
        )

        self.sdk._request.assert_called_once_with(
            "POST",
            f"/alerts/rules/following",
            body={
                "organizationId": organization_id,
                "page": page,
                "pageSize": page_size,
                "states": states,
            },
        )

    def test_get_grouped_following_alerts_page_str_severities(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        page = 1
        page_size = 100
        severities = zanshinsdk.AlertSeverity.CRITICAL

        self.sdk._get_grouped_following_alerts_page(
            organization_id, page=page, page_size=page_size, severities=severities
        )

        self.sdk._request.assert_called_once_with(
            "POST",
            f"/alerts/rules/following",
            body={
                "organizationId": organization_id,
                "page": page,
                "pageSize": page_size,
                "severities": [severities],
            },
        )

    def test_get_grouped_following_alerts_page_iterable_severities(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        page = 1
        page_size = 100
        severities = [zanshinsdk.AlertSeverity.CRITICAL, zanshinsdk.AlertSeverity.HIGH]

        self.sdk._get_grouped_following_alerts_page(
            organization_id, page=page, page_size=page_size, severities=severities
        )

        self.sdk._request.assert_called_once_with(
            "POST",
            f"/alerts/rules/following",
            body={
                "organizationId": organization_id,
                "page": page,
                "pageSize": page_size,
                "severities": severities,
            },
        )

    @patch("zanshinsdk.client.Client._get_grouped_following_alerts_page")
    def test_iter_grouped_following_alerts(self, request):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        page = 1
        page_size = 1

        request.return_value = {"data": [""], "total": 2}

        self.sdk._get_grouped_following_alerts_page = request
        iterator = self.sdk.iter_grouped_following_alerts(
            organization_id, page_size=page_size
        )

        next(iterator)
        next(iterator)

        self.sdk._get_grouped_following_alerts_page.assert_has_calls(
            [
                call(
                    organization_id,
                    None,
                    None,
                    None,
                    page=page,
                    page_size=page_size,
                    language=None,
                    search=None,
                    order=None,
                    sort=None,
                ),
                call(
                    organization_id,
                    None,
                    None,
                    None,
                    page=page + 1,
                    page_size=page_size,
                    language=None,
                    search=None,
                    order=None,
                    sort=None,
                ),
            ]
        )

    def test_get_alert(self):
        alert_id = "e22f4225-43e9-4922-b6b8-8b0620bdb110"

        self.sdk.get_alert(alert_id)

        self.sdk._request.assert_called_once_with(
            "GET",
            f"/alerts/{alert_id}",
        )

    def test_iter_alert_history(self):
        alert_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"

        try:
            next(self.sdk.iter_alert_history(alert_id))
        except StopIteration:
            pass

        self.sdk._request.assert_called_once_with(
            "GET",
            f"/alerts/{alert_id}/history",
        )

    def test_iter_alert_comments(self):
        alert_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"

        try:
            next(self.sdk.iter_alert_comments(alert_id))
        except StopIteration:
            pass

        self.sdk._request.assert_called_once_with(
            "GET",
            f"/alerts/{alert_id}/comments",
        )

    def test_update_alert(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        alert_id = "e22f4225-43e9-4922-b6b8-8b0620bdb110"
        scan_target_id = "e22f4225-43e9-4922-b6b8-8b0620bdb113"
        state = zanshinsdk.AlertState.OPEN
        labels = ["Test"]
        comment = "Comment test"

        self.sdk.update_alert(
            organization_id, scan_target_id, alert_id, state, labels, comment
        )

        self.sdk._request.assert_called_once_with(
            "PUT",
            f"/organizations/{organization_id}/scantargets/{scan_target_id}/alerts/{alert_id}",
            body={"state": state, "labels": labels, "comment": comment},
        )

    def test_create_alert_comment(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        alert_id = "e22f4225-43e9-4922-b6b8-8b0620bdb110"
        scan_target_id = "e22f4225-43e9-4922-b6b8-8b0620bdb113"
        comment = "Comment test"

        self.sdk.create_alert_comment(
            organization_id, scan_target_id, alert_id, comment
        )

        self.sdk._request.assert_called_once_with(
            "POST",
            f"/organizations/{organization_id}/scantargets/{scan_target_id}/alerts/{alert_id}/comments",
            body={"comment": comment},
        )

    ###################################################
    # Summary
    ###################################################

    def test_get_alert_summaries(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"

        self.sdk.get_alert_summaries(organization_id)

        self.sdk._request.assert_called_once_with(
            "POST", f"/alerts/summaries", body={"organizationId": organization_id}
        )

    def test_get_alert_summaries_str_scan_target_ids(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        scan_target_ids = "e22f4225-43e9-4922-b6b8-8b0620bdb110"

        self.sdk.get_alert_summaries(organization_id, scan_target_ids=scan_target_ids)

        self.sdk._request.assert_called_once_with(
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

        self.sdk.get_alert_summaries(organization_id, scan_target_ids=scan_target_ids)

        self.sdk._request.assert_called_once_with(
            "POST",
            f"/alerts/summaries",
            body={"organizationId": organization_id, "scanTargetIds": scan_target_ids},
        )

    def test_get_following_alert_summaries(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"

        self.sdk.get_following_alert_summaries(organization_id)

        self.sdk._request.assert_called_once_with(
            "POST",
            f"/alerts/summaries/following",
            body={"organizationId": organization_id},
        )

    def test_get_following_alert_summaries_str_following_ids(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        following_ids = "e22f4225-43e9-4922-b6b8-8b0620bdb110"

        self.sdk.get_following_alert_summaries(
            organization_id, following_ids=following_ids
        )

        self.sdk._request.assert_called_once_with(
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

        self.sdk.get_following_alert_summaries(
            organization_id, following_ids=following_ids
        )

        self.sdk._request.assert_called_once_with(
            "POST",
            f"/alerts/summaries/following",
            body={"organizationId": organization_id, "followingIds": following_ids},
        )

    def test_get_scan_summaries(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        days = 7

        self.sdk.get_scan_summaries(organization_id, days=days)

        self.sdk._request.assert_called_once_with(
            "POST",
            f"/alerts/summaries/scans",
            body={"organizationId": organization_id, "daysBefore": days},
        )

    def test_get_scan_summaries_str_scan_target_ids(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        days = 7
        scan_target_ids = "e22f4225-43e9-4922-b6b8-8b0620bdb110"

        self.sdk.get_scan_summaries(
            organization_id, days=days, scan_target_ids=scan_target_ids
        )

        self.sdk._request.assert_called_once_with(
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

        self.sdk.get_scan_summaries(
            organization_id, days=days, scan_target_ids=scan_target_ids
        )

        self.sdk._request.assert_called_once_with(
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

        self.sdk.get_following_scan_summaries(organization_id, days=days)

        self.sdk._request.assert_called_once_with(
            "POST",
            f"/alerts/summaries/scans/following",
            body={"organizationId": organization_id, "daysBefore": days},
        )

    def test_get_following_scan_summaries_str_following_ids(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        days = 7
        following_ids = "e22f4225-43e9-4922-b6b8-8b0620bdb110"

        self.sdk.get_following_scan_summaries(
            organization_id, days=days, following_ids=following_ids
        )

        self.sdk._request.assert_called_once_with(
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

        self.sdk.get_following_scan_summaries(
            organization_id, days=days, following_ids=following_ids
        )

        self.sdk._request.assert_called_once_with(
            "POST",
            f"/alerts/summaries/scans/following",
            body={
                "organizationId": organization_id,
                "daysBefore": days,
                "followingIds": following_ids,
            },
        )

    ###################################################
    # validates
    ###################################################

    def test_validate_int_none(self):
        _int = None
        self.assertIsNone(zanshinsdk.client.validate_int(_int))

    def test_validate_int_none_required(self):
        _int = None
        try:
            zanshinsdk.client.validate_int(_int, required=True)
        except Exception as e:
            self.assertEqual(str(e), f"required integer parameter missing")

    def test_validate_int_not_int(self):
        _int = "NaN"
        try:
            zanshinsdk.client.validate_int(_int)
        except Exception as e:
            self.assertEqual(str(e), f"{repr(_int)} is not an integer")

    def test_validate_int_lower_than(self):
        _int = 9
        _min_value = 10
        try:
            zanshinsdk.client.validate_int(_int, min_value=_min_value)
        except Exception as e:
            self.assertEqual(str(e), f"{_int} shouldn't be lower than {_min_value}")

    def test_validate_int_higher_than(self):
        _int = 11
        _max_value = 10
        try:
            zanshinsdk.client.validate_int(_int, max_value=_max_value)
        except Exception as e:
            self.assertEqual(str(e), f"{_int} shouldn't be higher than {_max_value}")

    def test_validate_class(self):
        _invalid_class = "invalid"
        try:
            zanshinsdk.client.validate_class(_invalid_class, UUID)
        except Exception as e:
            self.assertEqual(
                str(e), f"{repr(_invalid_class)} is not an instance of {UUID.__name__}"
            )

    def test_validate_uuid(self):
        _uuid = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        _response = zanshinsdk.validate_uuid(UUID(_uuid))
        self.assertEqual(_uuid, _response)

    def test_validate_uuid_invalid(self):
        _uuid = "invalid_uuid"
        try:
            zanshinsdk.validate_uuid(_uuid)
        except Exception as e:
            self.assertEqual(str(e), f"{repr(_uuid)} is not a valid UUID")

    def test_validate_uuid_input(self):
        with self.assertRaises(TypeError):
            zanshinsdk.validate_uuid(1)
        with self.assertRaises(TypeError):
            zanshinsdk.validate_uuid(None)
        with self.assertRaises(ValueError):
            zanshinsdk.validate_uuid("foo")
        with self.assertRaises(ValueError):
            zanshinsdk.validate_uuid("")

    def test_onboard_scan_target_unsupported_scan_target_kind(self):
        """
        Call onboard_scan_target with an scan target different than AWS. Currently we support only AWS for
        onboard via SDK.

        :param region: str
        :param organization_id: str
        :param kind: ScanTargetKind.AZURE
        :param credential: ScanTargetAZURE
        :param boto3_profile: str
        :param schedule: obj

        :raises: Exception Onboard does\'t support given environment yet


        >>> self.sdk.onboard_scan_target(
                region, organization_id, kind, name, credential, None, boto3_profile, schedule)
        raises:
        >>> Onboard doesn't support AZURE environment yet
        """
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        kind = zanshinsdk.ScanTargetKind.AZURE
        name = "OnboardTesting-it"
        credential = zanshinsdk.ScanTargetAZURE("4321", "1234", "1234", "s3cr3t")
        schedule = zanshinsdk.DAILY
        region = "us-east-1"
        boto3_profile = "foo"

        try:
            self.sdk.onboard_scan_target(
                region,
                organization_id,
                kind,
                name,
                credential,
                None,
                boto3_profile,
                schedule,
            )
        except Exception as e:
            self.assertEqual(str(e), "Onboard doesn't support AZURE environment yet")

    @unittest.skipIf("HAVE_BOTO3", "requires not have boto3")
    def test_onboard_scan_target_aws_missing_boto3(self):
        """
        Call onboard_scan_target without boto3 installed.
        Skip this test unless boto3 is installed in environment.

        :param region: str
        :param organization_id: str
        :param kind: ScanTargetKind.AZURE
        :param credential: ScanTargetAZURE
        :param boto3_profile: str
        :param schedule: obj

        :raises: boto3 not present. boto3 is required to perform AWS onboard.


        >>> self.sdk.onboard_scan_target(
                region, organization_id, kind, name, credential, None, boto3_profile, schedule)
        raises:
        >>> boto3 not present. boto3 is required to perform AWS onboard.
        """
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        kind = zanshinsdk.ScanTargetKind.AWS
        name = "OnboardTesting-it"
        credential = zanshinsdk.ScanTargetAWS("4321")
        schedule = zanshinsdk.DAILY
        region = "us-east-1"
        boto3_profile = "foo"

        try:
            self.sdk.onboard_scan_target(
                region,
                organization_id,
                kind,
                name,
                credential,
                None,
                boto3_profile,
                schedule,
            )
        except Exception as e:
            self.assertEqual(
                str(e), "boto3 not present. boto3 is required to perform AWS onboard."
            )

    @unittest.skipUnless("HAVE_BOTO3", "requires boto3")
    def test_onboard_scan_target_aws_invalid_credentials_boto3_profile(self):
        """
        Call onboard_scan_target passing a non-existing boto3_profile.
        Skip this test unless boto3 is installed in environment.

        :param region: str
        :param organization_id: str
        :param kind: ScanTargetKind.AZURE
        :param credential: ScanTargetAZURE
        :param boto3_profile: str
        :param schedule: obj

        :raises: The config profile (non_default) could not be found


        >>> self.sdk.onboard_scan_target(
                region, organization_id, kind, name, credential, None, boto3_profile, schedule)
        raises:
        >>> The config profile (non_default) could not be found
        """
        self.mock_aws_credentials()
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        kind = zanshinsdk.ScanTargetKind.AWS
        name = "OnboardTesting-it"
        credential = zanshinsdk.ScanTargetAWS("4321")
        schedule = zanshinsdk.DAILY
        region = "us-east-1"
        boto3_profile = "non_default"

        try:
            self.sdk.onboard_scan_target(
                region=region,
                organization_id=organization_id,
                kind=kind,
                name=name,
                credential=credential,
                boto3_profile=boto3_profile,
                schedule=schedule,
            )
        except Exception as e:
            self.assertEqual(
                str(e), "The config profile (non_default) could not be found"
            )

    @unittest.skipUnless("HAVE_BOTO3", "requires boto3")
    def test_onboard_scan_target_aws_invalid_credentials_boto3_session(self):
        """
        Call onboard_scan_target passing an invalid boto3_session.
        Skip this test unless boto3 is installed in environment.

        :param region: str
        :param organization_id: str
        :param kind: ScanTargetKind.AZURE
        :param credential: ScanTargetAZURE
        :param boto3_profile: str
        :param schedule: obj

        :raises: boto3 session is invalid. Working boto3 session is required.


        >>> self.sdk.onboard_scan_target(
                region, organization_id, kind, name, credential, None, boto3_profile, schedule)
        raises:
        >>> boto3 session is invalid. Working boto3 session is required.
        """
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        kind = zanshinsdk.ScanTargetKind.AWS
        name = "OnboardTesting-it"
        credential = zanshinsdk.ScanTargetAWS("4321")
        region = "us-east-1"

        import boto3

        try:
            boto3_session = boto3.Session(
                aws_access_key_id="EXAMPLE_NON_EXISTING_KEY",
                aws_secret_access_key="&x@mP|e$3cReT",
                aws_session_token="session_token",
            )
            self.sdk.onboard_scan_target(
                region=region,
                organization_id=organization_id,
                kind=kind,
                name=name,
                credential=credential,
                boto3_session=boto3_session,
            )
        except Exception as e:
            self.assertEqual(
                str(e), "boto3 session is invalid. Working boto3 session is required."
            )
