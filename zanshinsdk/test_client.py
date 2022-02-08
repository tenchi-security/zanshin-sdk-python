from unittest.mock import patch

import unittest
import zanshinsdk


class TestClient(unittest.TestCase):
    ###################################################
    # setUp
    ###################################################

    @patch("zanshinsdk.Client._request")
    def setUp(self, request):
        self.sdk = zanshinsdk.Client(api_key="api_key")
        self.sdk._request = request

    ###################################################
    # __init__
    ###################################################

    def test_init_empty_profile(self):
        try:
            zanshinsdk.Client(profile="")
        except Exception as e:
            self.assertEqual(str(e), "no API key found")

    def test_init_wrong_profile(self):
        profile = "XYZ"
        try:
            zanshinsdk.Client(profile=profile)
        except Exception as e:
            self.assertEqual(str(e), f"profile {profile} not found in {zanshinsdk.client.CONFIG_FILE}")

    def test_init_api_url(self):
        _api_url = "https://api.test"

        client = zanshinsdk.Client(api_url=_api_url)

        self.assertEqual(client._api_url, _api_url)

    def test_init_invalid_api_url(self):
        _api_url = "invalid://new.api.test"

        try:
            zanshinsdk.Client(api_url=_api_url)
        except Exception as e:
            self.assertEqual(str(e), f"Invalid API URL: {_api_url}")

    def test_init_proxy_url(self):
        _proxy_url = "https://proxy.test"

        client = zanshinsdk.Client(proxy_url=_proxy_url)

        self.assertEqual(client._proxy_url, _proxy_url)

    def test_init_invalid_proxy_url(self):
        _proxy_url = "invalid://proxy.api.test"

        try:
            zanshinsdk.Client(proxy_url=_proxy_url)
        except Exception as e:
            self.assertEqual(str(e), f"Invalid proxy URL: {_proxy_url}")

    def test_init_user_agent(self):
        _user_agent = "test_agent"

        client = zanshinsdk.Client(user_agent=_user_agent)

        self.assertEqual(client._user_agent, _user_agent)

    ###################################################
    # _update_client except
    ###################################################

    def test_update_client_except(self):
        client = zanshinsdk.Client()
        client._client = None
        client._update_client()
        self.assertIsNotNone(client._client)

    ###################################################
    # Properties
    ###################################################

    def test_get_api_url(self):
        _api_url = "https://api.test"

        client = zanshinsdk.Client(api_url=_api_url)

        self.assertEqual(client.api_url, _api_url)

    def test_set_api_url(self):
        _api_url = "https://api.test"
        _new_api_url = "https://new.api.test"

        client = zanshinsdk.Client(api_url=_api_url)
        client.api_url = _new_api_url

        self.assertEqual(client.api_url, _new_api_url)

    def test_set_invalid_api_url(self):
        _api_url = "https://api.test"
        _new_api_url = "invalid://new.api.test"

        try:
            client = zanshinsdk.Client(api_url=_api_url)
            client.api_url = _new_api_url
        except Exception as e:
            self.assertEqual(str(e), f"Invalid API URL: {_new_api_url}")

    def test_set_none_api_url(self):
        _api_key = "https://api.test"

        try:
            client = zanshinsdk.Client(api_url=_api_key)
            client.api_url = None
        except Exception as e:
            self.assertEqual(str(e), f"API URL cannot be null")

    def test_get_api_key(self):
        _api_key = "api_key"

        client = zanshinsdk.Client(api_key=_api_key)

        self.assertEqual(client.api_key, _api_key)

    def test_set_api_key(self):
        _api_key = "api_key"
        _new_api_key = "new_api_key"

        client = zanshinsdk.Client(api_key=_api_key)
        client.api_key = _new_api_key

        self.assertEqual(client.api_key, _new_api_key)

    def test_get_proxy_url(self):
        _proxy_url = "https://proxy.test"

        client = zanshinsdk.Client(proxy_url=_proxy_url)

        self.assertEqual(client.proxy_url, _proxy_url)

    def test_set_proxy_url(self):
        _proxy_url = "https://proxy.test"
        _new_proxy_url = "https://new.proxy.test"

        client = zanshinsdk.Client(proxy_url=_proxy_url)
        client.proxy_url = _new_proxy_url

        self.assertEqual(client.proxy_url, _new_proxy_url)

    def test_set_invalid_proxy_url(self):
        _proxy_url = "https://proxy.test"
        _new_proxy_url = "invalid://new.proxy.test"

        try:
            client = zanshinsdk.Client(proxy_url=_proxy_url)
            client.proxy_url = _new_proxy_url
        except Exception as e:
            self.assertEqual(str(e), f"Invalid proxy URL: {_new_proxy_url}")

    def test_set_equal_proxy_url(self):
        _proxy_url = "https://proxy.test"

        client = zanshinsdk.Client(proxy_url=_proxy_url)
        client.proxy_url = _proxy_url

        self.assertEqual(client.proxy_url, _proxy_url)

    def test_set_none_proxy_url(self):
        _proxy_url = "https://proxy.test"

        client = zanshinsdk.Client(proxy_url=_proxy_url)
        client.proxy_url = None

        self.assertIsNone(client.proxy_url)

    def test_get_user_agent(self):
        _user_agent = "test_agent"

        client = zanshinsdk.Client(user_agent=_user_agent)

        self.assertEqual(client.user_agent, _user_agent)

    def test_set_user_agent(self):
        _user_agent = "test_agent"
        _new_user_agent = "new_test_agent"

        client = zanshinsdk.Client(user_agent=_user_agent)
        client.user_agent = _new_user_agent

        self.assertEqual(client.user_agent, _new_user_agent)

    ###################################################
    # Account
    ###################################################

    def test_get_me(self):
        self.sdk.get_me()

        self.sdk._request.assert_called_once_with(
            "GET", "/me"
        )

    ###################################################
    # Account Invites
    ###################################################

    def test_iter_invites(self):
        try:
            next(self.sdk.iter_invites())
        except StopIteration:
            pass

        self.sdk._request.assert_called_once_with(
            "GET", "/me/invites"
        )

    def test_get_invite(self):
        invite_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"

        self.sdk.get_invite(invite_id)

        self.sdk._request.assert_called_once_with(
            "GET", f"/me/invites/{invite_id}"
        )

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

        self.sdk._request.assert_called_once_with(
            "GET", "/me/apikeys"
        )

    def test_create_api_key(self):
        name = "MyKey"

        self.sdk.create_api_key(name)

        self.sdk._request.assert_called_once_with(
            "POST", "/me/apikeys",
            body={"name": name}
        )

    def test_delete_api_key(self):
        api_key = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"

        self.sdk.delete_api_key(api_key)

        self.sdk._request.assert_called_once_with(
            "DELETE", f"/me/apikeys/{api_key}"
        )

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

    def test_update_organization(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        name = "Tabajara"
        picture = "https://pic-store.com/pic1.png"
        email = "ceo@tabajara.com.br"

        self.sdk.update_organization(organization_id, name, picture, email)

        self.sdk._request.assert_called_once_with(
            "PUT", f"/organizations/{organization_id}",
            body={"name": name, "picture": picture, "email": email}
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
        role = [zanshinsdk.client.Roles.ADMIN]

        self.sdk.update_organization_member(organization_id, member_id, role)

        self.sdk._request.assert_called_once_with(
            "PUT", f"/organizations/{organization_id}/members/{member_id}",
            body={"roles": role}
        )

    def test_delete_organization_members(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        member_id = "e22f4225-43e9-4922-b6b8-8b0620bdb110"

        self.sdk.delete_organization_member(organization_id, member_id)

        self.sdk._request.assert_called_once_with(
            "DELETE", f"/organizations/{organization_id}/members/{member_id}"
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
        role = [zanshinsdk.client.Roles.ADMIN]

        self.sdk.create_organization_members_invite(organization_id, email, role)

        self.sdk._request.assert_called_once_with(
            "POST", f"/organizations/{organization_id}/invites",
            body={"email": email, "roles": role}
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
            "POST", f"/organizations/{organization_id}/followers/requests",
            body={"token": token}
        )

    def test_get_organization_follower_request(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        follower_id = "e22f4225-43e9-4922-b6b8-8b0620bdb110"

        self.sdk.get_organization_follower_request(organization_id, follower_id)

        self.sdk._request.assert_called_once_with(
            "GET", f"/organizations/{organization_id}/followers/requests/{follower_id}")

    def test_delete_organization_follower_request(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        follower_id = "e22f4225-43e9-4922-b6b8-8b0620bdb110"

        self.sdk.delete_organization_follower_request(organization_id, follower_id)

        self.sdk._request.assert_called_once_with(
            "DELETE", f"/organizations/{organization_id}/followers/requests/{follower_id}"
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
            "POST", f"/organizations/{organization_id}/following/requests/{following_id}/accept"
        )

    def test_decline_organization_following_request(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        following_id = "e22f4225-43e9-4922-b6b8-8b0620bdb110"

        self.sdk.decline_organization_following_request(organization_id, following_id)

        self.sdk._request.assert_called_once_with(
            "POST", f"/organizations/{organization_id}/following/requests/{following_id}/decline"
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
        kind = zanshinsdk.client.ScanTargetKind.AWS
        name = "ScanTargetTest"
        credential = {
            "account": "123456"
        }
        schedule = "0 0 * * *"

        self.sdk.create_organization_scan_target(organization_id, kind, name, credential, schedule)

        self.sdk._request.assert_called_once_with(
            "POST", f"/organizations/{organization_id}/scantargets",
            body={"name": name, "kind": kind, "credential": credential, "schedule": schedule}
        )

    def test_create_organization_scan_target_AZURE(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        kind = zanshinsdk.client.ScanTargetKind.AZURE
        name = "ScanTargetTest"
        credential = {
            "applicationId": "1234567890",
            "directoryId": "0123456789",
            "subscriptionId": "2345678901",
            "secret": "SECRET"
        }
        schedule = "0 0 * * *"

        self.sdk.create_organization_scan_target(organization_id, kind, name, credential, schedule)

        self.sdk._request.assert_called_once_with(
            "POST", f"/organizations/{organization_id}/scantargets",
            body={"name": name, "kind": kind, "credential": credential, "schedule": schedule}
        )

    def test_create_organization_scan_target_GCP(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        kind = zanshinsdk.client.ScanTargetKind.GCP
        name = "ScanTargetTest"
        credential = {
            "projectId": "123456"
        }
        schedule = "0 0 * * *"

        self.sdk.create_organization_scan_target(organization_id, kind, name, credential, schedule)

        self.sdk._request.assert_called_once_with(
            "POST", f"/organizations/{organization_id}/scantargets",
            body={"name": name, "kind": kind, "credential": credential, "schedule": schedule}
        )

    def test_create_organization_scan_target_HUAWEI(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        kind = zanshinsdk.client.ScanTargetKind.HUAWEI
        name = "ScanTargetTest"
        credential = {
            "accountId": "123456"
        }
        schedule = "0 0 * * *"

        self.sdk.create_organization_scan_target(organization_id, kind, name, credential, schedule)

        self.sdk._request.assert_called_once_with(
            "POST", f"/organizations/{organization_id}/scantargets",
            body={"name": name, "kind": kind, "credential": credential, "schedule": schedule}
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
        schedule = "0 0 * * *"

        self.sdk.update_organization_scan_target(organization_id, scan_target_id, name, schedule)

        self.sdk._request.assert_called_once_with(
            "PUT", f"/organizations/{organization_id}/scantargets/{scan_target_id}",
            body={"name": name, "schedule": schedule}
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

        self.sdk.start_organization_scan_target_scan(organization_id, scan_target_id)

        self.sdk._request.assert_called_once_with(
            "POST", f"/organizations/{organization_id}/scantargets/{scan_target_id}/scan"
        )

    def test_stop_organization_scan_target_scan(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        scan_target_id = "e22f4225-43e9-4922-b6b8-8b0620bdb110"

        self.sdk.stop_organization_scan_target_scan(organization_id, scan_target_id)

        self.sdk._request.assert_called_once_with(
            "POST", f"/organizations/{organization_id}/scantargets/{scan_target_id}/stop"
        )

    def test_check_organization_scan_target(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        scan_target_id = "e22f4225-43e9-4922-b6b8-8b0620bdb110"

        self.sdk.check_organization_scan_target(organization_id, scan_target_id)

        self.sdk._request.assert_called_once_with(
            "POST", f"/organizations/{organization_id}/scantargets/{scan_target_id}/check"
        )

    ###################################################
    # Organization Scan Target Scan
    ###################################################

    def test_iter_organization_scan_target_scans(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        scan_target_id = "e22f4225-43e9-4922-b6b8-8b0620bdb110"

        try:
            next(self.sdk.iter_organization_scan_target_scans(organization_id, scan_target_id))
        except StopIteration:
            pass

        self.sdk._request.assert_called_once_with(
            "GET", f"/organizations/{organization_id}/scantargets/{scan_target_id}/scans"
        )

    def test_get_organization_scan_target_scan(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        scan_target_id = "e22f4225-43e9-4922-b6b8-8b0620bdb110"
        scan_id = "e22f4225-43e9-4922-b6b8-8b0620bdb112"

        self.sdk.get_organization_scan_target_scan(organization_id, scan_target_id, scan_id)

        self.sdk._request.assert_called_once_with(
            "GET", f"/organizations/{organization_id}/scantargets/{scan_target_id}/scans/{scan_id}"
        )

    ###################################################
    # Alerts
    ###################################################

    def test_get_alerts_page(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        page = 1
        page_size = 100

        self.sdk._get_alerts_page(organization_id, page=page, page_size=page_size)

        self.sdk._request.assert_called_once_with(
            "POST", f"/alerts",
            body={"organizationId": organization_id, "page": page, "pageSize": page_size}
        )

    def test_iter_alerts(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        page = 1
        page_size = 100

        try:
            next(self.sdk.iter_alerts(organization_id, page_size=page_size))
        except StopIteration:
            pass

        self.sdk._request.assert_called_once_with(
            "POST", f"/alerts",
            body={"organizationId": organization_id, "page": page, "pageSize": page_size}
        )

    def test_get_following_alerts_page(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        page = 1
        page_size = 100

        self.sdk._get_following_alerts_page(organization_id, page=page, page_size=page_size)

        self.sdk._request.assert_called_once_with(
            "POST", f"/alerts/following",
            body={"organizationId": organization_id, "page": page, "pageSize": page_size}
        )

    def test_iter_following_alerts(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        page = 1
        page_size = 100

        try:
            next(self.sdk.iter_following_alerts(organization_id, page_size=page_size))
        except StopIteration:
            pass

        self.sdk._request.assert_called_with(
            "POST", f"/alerts/following",
            body={"organizationId": organization_id, "page": page, "pageSize": page_size}
        )

    def test_get_alerts_history_page(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        page_size = 100

        self.sdk._get_alerts_history_page(organization_id, page_size=page_size)

        self.sdk._request.assert_called_once_with(
            "POST", f"/alerts/history",
            body={"organizationId": organization_id, "pageSize": page_size}
        )

    def test_iter_alerts_history(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        page_size = 100

        try:
            next(self.sdk.iter_alerts_history(organization_id, page_size=page_size))
        except StopIteration:
            pass

        self.sdk._request.assert_called_once_with(
            "POST", f"/alerts/history",
            body={"organizationId": organization_id, "pageSize": page_size}
        )

    def test_get_alerts_following_history_page(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        page_size = 100

        self.sdk._get_alerts_following_history_page(organization_id, page_size=page_size)

        self.sdk._request.assert_called_once_with(
            "POST", f"/alerts/history/following",
            body={"organizationId": organization_id, "pageSize": page_size}
        )

    def test_iter_alerts_following_history(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        page_size = 100

        try:
            next(self.sdk.iter_alerts_following_history(organization_id, page_size=page_size))
        except StopIteration:
            pass

        self.sdk._request.assert_called_once_with(
            "POST", f"/alerts/history/following",
            body={"organizationId": organization_id, "pageSize": page_size}
        )

    def test_get_grouped_alerts_page(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        page = 1
        page_size = 100

        self.sdk._get_grouped_alerts_page(organization_id, page=page, page_size=page_size)

        self.sdk._request.assert_called_once_with(
            "POST", f"/alerts/rules",
            body={"organizationId": organization_id, "page": page, "pageSize": page_size}
        )

    def test_iter_grouped_alerts(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        page = 1
        page_size = 100

        try:
            next(self.sdk.iter_grouped_alerts(organization_id, page_size=page_size))
        except StopIteration:
            pass

        self.sdk._request.assert_called_once_with(
            "POST", f"/alerts/rules",
            body={"organizationId": organization_id, "page": page, "pageSize": page_size}
        )

    def test_get_grouped_following_alerts_page(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        page = 1
        page_size = 100

        self.sdk._get_grouped_following_alerts_page(organization_id, page=page, page_size=page_size)

        self.sdk._request.assert_called_once_with(
            "POST", f"/alerts/rules/following",
            body={"organizationId": organization_id, "page": page, "pageSize": page_size}
        )

    def test_iter_grouped_following_alerts(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        page = 1
        page_size = 100

        try:
            next(self.sdk.iter_grouped_following_alerts(organization_id, page_size=page_size))
        except StopIteration:
            pass

        self.sdk._request.assert_called_with(
            "POST", f"/alerts/rules/following",
            body={"organizationId": organization_id, "page": page, "pageSize": page_size}
        )

    def test_get_alert(self):
        alert_id = "e22f4225-43e9-4922-b6b8-8b0620bdb110"

        self.sdk.get_alert(alert_id)

        self.sdk._request.assert_called_once_with(
            "GET", f"/alerts/{alert_id}",
        )

    def test_iter_alert_history(self):
        alert_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"

        try:
            next(self.sdk.iter_alert_history(alert_id))
        except StopIteration:
            pass

        self.sdk._request.assert_called_once_with(
            "GET", f"/alerts/{alert_id}/history",
        )

    def test_iter_alert_comments(self):
        alert_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"

        try:
            next(self.sdk.iter_alert_comments(alert_id))
        except StopIteration:
            pass

        self.sdk._request.assert_called_once_with(
            "GET", f"/alerts/{alert_id}/comments",
        )

    def test_update_alert(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        alert_id = "e22f4225-43e9-4922-b6b8-8b0620bdb110"
        scan_target_id = "e22f4225-43e9-4922-b6b8-8b0620bdb113"
        state = zanshinsdk.client.AlertState.OPEN
        labels = ["Test"]
        comment = "Comment test"

        self.sdk.update_alert(organization_id, scan_target_id, alert_id, state, labels, comment)

        self.sdk._request.assert_called_once_with(
            "PUT", f"/organizations/{organization_id}/scantargets/{scan_target_id}/alerts/{alert_id}",
            body={"state": state, "labels": labels, "comment": comment}
        )

    def test_create_alert_comment(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        alert_id = "e22f4225-43e9-4922-b6b8-8b0620bdb110"
        scan_target_id = "e22f4225-43e9-4922-b6b8-8b0620bdb113"
        comment = "Comment test"

        self.sdk.create_alert_comment(organization_id, scan_target_id, alert_id, comment)

        self.sdk._request.assert_called_once_with(
            "POST", f"/organizations/{organization_id}/scantargets/{scan_target_id}/alerts/{alert_id}/comments",
            body={"comment": comment}
        )

    ###################################################
    # Summary
    ###################################################

    def test_get_alert_summaries(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"

        self.sdk.get_alert_summaries(organization_id)

        self.sdk._request.assert_called_once_with(
            "POST", f"/alerts/summaries",
            body={"organizationId": organization_id}
        )

    def test_get_following_alert_summaries(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"

        self.sdk.get_following_alert_summaries(organization_id)

        self.sdk._request.assert_called_once_with(
            "POST", f"/alerts/summaries/following",
            body={"organizationId": organization_id}
        )

    def test_get_scan_summaries(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        days = 7

        self.sdk.get_scan_summaries(organization_id, days=days)

        self.sdk._request.assert_called_once_with(
            "POST", f"/alerts/summaries/scans",
            body={"organizationId": organization_id, "daysBefore": days}
        )

    def test_get_following_scan_summaries(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        days = 7

        self.sdk.get_following_scan_summaries(organization_id, days=days)

        self.sdk._request.assert_called_once_with(
            "POST", f"/alerts/summaries/scans/following",
            body={"organizationId": organization_id, "daysBefore": days}
        )
