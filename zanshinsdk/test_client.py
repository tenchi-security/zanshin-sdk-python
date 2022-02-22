from unittest.mock import patch, mock_open
from uuid import UUID

import unittest
import zanshinsdk


class TestClient(unittest.TestCase):
    ###################################################
    # setUp
    ###################################################

    @patch("zanshinsdk.Client._request")
    def setUp(self, request):
        _data = f"[default]\napi_key=api_key"

        with patch("__main__.__builtins__.open", mock_open(read_data=_data)):
            self.sdk = zanshinsdk.Client()
            self.sdk._request = request

    ###################################################
    # __init__
    ###################################################

    def test_init_empty_profile(self):
        _data = f"[default]\napi_key=api_key"

        try:
            with patch("__main__.__builtins__.open", mock_open(read_data=_data)):
                zanshinsdk.Client(profile="")
        except Exception as e:
            self.assertEqual(str(e), "no API key found")

    def test_init_wrong_profile(self):
        _profile = "XYZ"
        _data = "[default]\napi_key=api_key"

        try:
            with patch("__main__.__builtins__.open", mock_open(read_data=_data)):
                zanshinsdk.Client(profile=_profile)
        except Exception as e:
            self.assertEqual(str(e), f"profile {_profile} not found in {zanshinsdk.client.CONFIG_FILE}")

    def test_init_api_url(self):
        _api_url = "https://api.test"
        _data = f"[default]\napi_key=api_key"

        with patch("__main__.__builtins__.open", mock_open(read_data=_data)):
            client = zanshinsdk.Client(api_url=_api_url)

        self.assertEqual(client._api_url, _api_url)

    def test_init_invalid_api_url(self):
        _api_url = "invalid://api.test"
        _data = f"[default]\napi_key=api_key"

        try:
            with patch("__main__.__builtins__.open", mock_open(read_data=_data)):
                zanshinsdk.Client(api_url=_api_url)
        except Exception as e:
            self.assertEqual(str(e), f"Invalid API URL: {_api_url}")

    def test_init_api_url_from_config(self):
        _api_url = "https://api.test"
        _data = f"[default]\napi_key=api_key\napi_url={_api_url}"

        with patch("__main__.__builtins__.open", mock_open(read_data=_data)):
            client = zanshinsdk.Client()

        self.assertEqual(client._api_url, _api_url)

    def test_init_proxy_url(self):
        _proxy_url = "https://proxy.test"
        _data = f"[default]\napi_key=api_key"

        with patch("__main__.__builtins__.open", mock_open(read_data=_data)):
            client = zanshinsdk.Client(proxy_url=_proxy_url)

        self.assertEqual(client._proxy_url, _proxy_url)

    def test_init_invalid_proxy_url(self):
        _proxy_url = "invalid://proxy.api.test"
        _data = f"[default]\napi_key=api_key"

        try:
            with patch("__main__.__builtins__.open", mock_open(read_data=_data)):
                zanshinsdk.Client(proxy_url=_proxy_url)
        except Exception as e:
            self.assertEqual(str(e), f"Invalid proxy URL: {_proxy_url}")

    def test_init_proxy_url_from_config(self):
        _proxy_url = "https://proxy.test"
        _data = f"[default]\napi_key=api_key\nproxy_url={_proxy_url}"

        with patch("__main__.__builtins__.open", mock_open(read_data=_data)):
            client = zanshinsdk.Client()

        self.assertEqual(client._proxy_url, _proxy_url)

    def test_init_user_agent(self):
        _user_agent = "test_agent"
        _data = f"[default]\napi_key=api_key"

        with patch("__main__.__builtins__.open", mock_open(read_data=_data)):
            client = zanshinsdk.Client(user_agent=_user_agent)

        self.assertEqual(client._user_agent, f"{_user_agent} (Zanshin Python SDK v{zanshinsdk.__version__})")

    def test_init_user_agent_from_config(self):
        _user_agent = "test_agent"
        _data = f"[default]\napi_key=api_key\nuser_agent={_user_agent}"

        with patch("__main__.__builtins__.open", mock_open(read_data=_data)):
            client = zanshinsdk.Client()

        self.assertEqual(client._user_agent, f"{_user_agent} (Zanshin Python SDK v{zanshinsdk.__version__})")

    ###################################################
    # _update_client except
    ###################################################

    def test_update_client_except(self):
        _data = f"[default]\napi_key=api_key"

        with patch("__main__.__builtins__.open", mock_open(read_data=_data)):
            client = zanshinsdk.Client()

        client._client = None
        client._update_client()

        self.assertIsNotNone(client._client)

    ###################################################
    # Properties
    ###################################################

    def test_get_api_url(self):
        _api_url = "https://api.test"
        _data = f"[default]\napi_key=api_key"

        with patch("__main__.__builtins__.open", mock_open(read_data=_data)):
            client = zanshinsdk.Client(api_url=_api_url)

        self.assertEqual(client.api_url, _api_url)

    def test_set_api_url(self):
        _api_url = "https://api.test"
        _new_api_url = "https://new.api.test"
        _data = f"[default]\napi_key=api_key"

        with patch("__main__.__builtins__.open", mock_open(read_data=_data)):
            client = zanshinsdk.Client(api_url=_api_url)

        client.api_url = _new_api_url

        self.assertEqual(client.api_url, _new_api_url)

    def test_set_invalid_api_url(self):
        _api_url = "https://api.test"
        _new_api_url = "invalid://new.api.test"
        _data = f"[default]\napi_key=api_key"

        try:
            with patch("__main__.__builtins__.open", mock_open(read_data=_data)):
                client = zanshinsdk.Client(api_url=_api_url)

            client.api_url = _new_api_url
        except Exception as e:
            self.assertEqual(str(e), f"Invalid API URL: {_new_api_url}")

    def test_set_none_api_url(self):
        _api_key = "https://api.test"
        _data = f"[default]\napi_key=api_key"

        try:
            with patch("__main__.__builtins__.open", mock_open(read_data=_data)):
                client = zanshinsdk.Client(api_url=_api_key)

            client.api_url = None
        except Exception as e:
            self.assertEqual(str(e), f"API URL cannot be null")

    def test_get_api_key(self):
        _api_key = "api_key"
        _data = f"[default]\napi_key=api_key"

        with patch("__main__.__builtins__.open", mock_open(read_data=_data)):
            client = zanshinsdk.Client(api_key=_api_key)

        self.assertEqual(client.api_key, _api_key)

    def test_set_api_key(self):
        _api_key = "api_key"
        _new_api_key = "new_api_key"
        _data = f"[default]\napi_key=api_key"

        with patch("__main__.__builtins__.open", mock_open(read_data=_data)):
            client = zanshinsdk.Client(api_key=_api_key)

        client.api_key = _new_api_key

        self.assertEqual(client.api_key, _new_api_key)

    def test_get_proxy_url(self):
        _proxy_url = "https://proxy.test"
        _data = f"[default]\napi_key=api_key"

        with patch("__main__.__builtins__.open", mock_open(read_data=_data)):
            client = zanshinsdk.Client(proxy_url=_proxy_url)

        self.assertEqual(client.proxy_url, _proxy_url)

    def test_set_proxy_url(self):
        _proxy_url = "https://proxy.test"
        _new_proxy_url = "https://new.proxy.test"
        _data = f"[default]\napi_key=api_key"

        with patch("__main__.__builtins__.open", mock_open(read_data=_data)):
            client = zanshinsdk.Client(proxy_url=_proxy_url)

        client.proxy_url = _new_proxy_url

        self.assertEqual(client.proxy_url, _new_proxy_url)

    def test_set_invalid_proxy_url(self):
        _proxy_url = "https://proxy.test"
        _new_proxy_url = "invalid://new.proxy.test"
        _data = f"[default]\napi_key=api_key"

        try:
            with patch("__main__.__builtins__.open", mock_open(read_data=_data)):
                client = zanshinsdk.Client(proxy_url=_proxy_url)

            client.proxy_url = _new_proxy_url
        except Exception as e:
            self.assertEqual(str(e), f"Invalid proxy URL: {_new_proxy_url}")

    def test_set_equal_proxy_url(self):
        _proxy_url = "https://proxy.test"
        _data = f"[default]\napi_key=api_key"

        with patch("__main__.__builtins__.open", mock_open(read_data=_data)):
            client = zanshinsdk.Client(proxy_url=_proxy_url)

        client.proxy_url = _proxy_url

        self.assertEqual(client.proxy_url, _proxy_url)

    def test_set_none_proxy_url(self):
        _proxy_url = "https://proxy.test"
        _data = f"[default]\napi_key=api_key"

        with patch("__main__.__builtins__.open", mock_open(read_data=_data)):
            client = zanshinsdk.Client(proxy_url=_proxy_url)

        client.proxy_url = None

        self.assertIsNone(client.proxy_url)

    def test_get_user_agent(self):
        _user_agent = "test_agent"
        _data = f"[default]\napi_key=api_key"

        with patch("__main__.__builtins__.open", mock_open(read_data=_data)):
            client = zanshinsdk.Client(user_agent=_user_agent)

        self.assertEqual(client.user_agent, f"{_user_agent} (Zanshin Python SDK v{zanshinsdk.__version__})")

    def test_set_user_agent(self):
        _user_agent = "test_agent"
        _new_user_agent = "new_test_agent"
        _data = f"[default]\napi_key=api_key"

        with patch("__main__.__builtins__.open", mock_open(read_data=_data)):
            client = zanshinsdk.Client(user_agent=_user_agent)

        client.user_agent = _new_user_agent

        self.assertEqual(client.user_agent, f"{_new_user_agent} (Zanshin Python SDK v{zanshinsdk.__version__})")

    def test_get_sanitized_proxy_url_none(self):
        _data = f"[default]\napi_key=api_key"

        with patch("__main__.__builtins__.open", mock_open(read_data=_data)):
            client = zanshinsdk.Client()

        self.assertIsNone(client._get_sanitized_proxy_url())

    def test_get_sanitized_proxy_url(self):
        _proxy_url = "https://username:password@proxy.test:8000"
        _data = f"[default]\napi_key=api_key"

        with patch("__main__.__builtins__.open", mock_open(read_data=_data)):
            client = zanshinsdk.Client(proxy_url=_proxy_url)

        self.assertIsNotNone(client._get_sanitized_proxy_url())

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
        role = [zanshinsdk.Roles.ADMIN]

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
        role = [zanshinsdk.Roles.ADMIN]

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
        kind = zanshinsdk.ScanTargetKind.AWS
        name = "ScanTargetTest"
        credential = zanshinsdk.ScanTargetAWS()
        credential.account = "123456"
        schedule = "0 0 * * *"

        self.sdk.create_organization_scan_target(organization_id, kind, name, credential, schedule)

        self.sdk._request.assert_called_once_with(
            "POST", f"/organizations/{organization_id}/scantargets",
            body={"name": name, "kind": kind, "credential": credential, "schedule": schedule}
        )

    def test_create_organization_scan_target_AZURE(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        kind = zanshinsdk.ScanTargetKind.AZURE
        name = "ScanTargetTest"
        credential = zanshinsdk.ScanTargetAZURE()
        credential.applicationId = "1234567890",
        credential.directoryId = "0123456789",
        credential.subscriptionId = "2345678901",
        credential.secret = "SECRET"
        schedule = "0 0 * * *"

        self.sdk.create_organization_scan_target(organization_id, kind, name, credential, schedule)

        self.sdk._request.assert_called_once_with(
            "POST", f"/organizations/{organization_id}/scantargets",
            body={"name": name, "kind": kind, "credential": credential, "schedule": schedule}
        )

    def test_create_organization_scan_target_GCP(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        kind = zanshinsdk.ScanTargetKind.GCP
        name = "ScanTargetTest"
        credential = zanshinsdk.ScanTargetGCP()
        credential.projectId = "123456"
        schedule = "0 0 * * *"

        self.sdk.create_organization_scan_target(organization_id, kind, name, credential, schedule)

        self.sdk._request.assert_called_once_with(
            "POST", f"/organizations/{organization_id}/scantargets",
            body={"name": name, "kind": kind, "credential": credential, "schedule": schedule}
        )

    def test_create_organization_scan_target_HUAWEI(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        kind = zanshinsdk.ScanTargetKind.HUAWEI
        name = "ScanTargetTest"
        credential = zanshinsdk.ScanTargetHUAWEI()
        credential.accountId = "123456"
        schedule = "0 0 * * *"

        self.sdk.create_organization_scan_target(organization_id, kind, name, credential, schedule)

        self.sdk._request.assert_called_once_with(
            "POST", f"/organizations/{organization_id}/scantargets",
            body={"name": name, "kind": kind, "credential": credential, "schedule": schedule}
        )

    def test_create_organization_scan_target_DOMAIN(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        kind = zanshinsdk.ScanTargetKind.DOMAIN
        name = "ScanTargetTest"
        credential = zanshinsdk.ScanTargetDOMAIN()
        credential.domain = "123456"
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
        rule = "rule"
        language = zanshinsdk.Languages.ENUS
        created_at_start = "created_at_start"
        created_at_end = "created_at_end"
        updated_at_start = "updated_at_start"
        updated_at_end = "updated_at_end"

        self.sdk._get_alerts_page(organization_id,
                                  page=page,
                                  page_size=page_size,
                                  rule=rule,
                                  language=language,
                                  created_at_start=created_at_start,
                                  created_at_end=created_at_end,
                                  updated_at_start=updated_at_start,
                                  updated_at_end=updated_at_end)

        self.sdk._request.assert_called_once_with(
            "POST", f"/alerts",
            body={
                "organizationId": organization_id,
                "page": page,
                "pageSize": page_size,
                "rule": rule,
                "lang": language,
                "CreatedAtStart": created_at_start,
                "CreatedAtEnd": created_at_end,
                "UpdatedAtStart": updated_at_start,
                "UpdatedAtEnd": updated_at_end
            }
        )

    def test_get_alerts_page_str_scan_target_ids(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        page = 1
        page_size = 100
        scan_target_ids = "e22f4225-43e9-4922-b6b8-8b0620bdb110"

        self.sdk._get_alerts_page(organization_id, page=page, page_size=page_size, scan_target_ids=scan_target_ids)

        self.sdk._request.assert_called_once_with(
            "POST", f"/alerts",
            body={
                "organizationId": organization_id,
                "page": page,
                "pageSize": page_size,
                "scanTargetIds": [scan_target_ids]
            }
        )

    def test_get_alerts_page_iterable_scan_target_ids(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        page = 1
        page_size = 100
        scan_target_ids = ["e22f4225-43e9-4922-b6b8-8b0620bdb110", "e22f4225-43e9-4922-b6b8-8b0620bdb112"]

        self.sdk._get_alerts_page(organization_id, page=page, page_size=page_size, scan_target_ids=scan_target_ids)

        self.sdk._request.assert_called_once_with(
            "POST", f"/alerts",
            body={
                "organizationId": organization_id,
                "page": page,
                "pageSize": page_size,
                "scanTargetIds": scan_target_ids
            }
        )

    def test_get_alerts_page_str_states(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        page = 1
        page_size = 100
        states = zanshinsdk.AlertState.OPEN

        self.sdk._get_alerts_page(organization_id, page=page, page_size=page_size, states=states)

        self.sdk._request.assert_called_once_with(
            "POST", f"/alerts",
            body={
                "organizationId": organization_id,
                "page": page,
                "pageSize": page_size,
                "states": [states]
            }
        )

    def test_get_alerts_page_iterable_states(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        page = 1
        page_size = 100
        states = [zanshinsdk.AlertState.OPEN, zanshinsdk.AlertState.CLOSED]

        self.sdk._get_alerts_page(organization_id, page=page, page_size=page_size, states=states)

        self.sdk._request.assert_called_once_with(
            "POST", f"/alerts",
            body={
                "organizationId": organization_id,
                "page": page,
                "pageSize": page_size,
                "states": states
            }
        )

    def test_get_alerts_page_str_severities(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        page = 1
        page_size = 100
        severities = zanshinsdk.AlertSeverity.CRITICAL

        self.sdk._get_alerts_page(organization_id, page=page, page_size=page_size, severities=severities)

        self.sdk._request.assert_called_once_with(
            "POST", f"/alerts",
            body={
                "organizationId": organization_id,
                "page": page,
                "pageSize": page_size,
                "severities": [severities]
            }
        )

    def test_get_alerts_page_iterable_severities(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        page = 1
        page_size = 100
        severities = [zanshinsdk.AlertSeverity.CRITICAL, zanshinsdk.AlertSeverity.HIGH]

        self.sdk._get_alerts_page(organization_id, page=page, page_size=page_size, severities=severities)

        self.sdk._request.assert_called_once_with(
            "POST", f"/alerts",
            body={
                "organizationId": organization_id,
                "page": page,
                "pageSize": page_size,
                "severities": severities
            }
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
        rule = "rule"
        language = zanshinsdk.Languages.ENUS
        created_at_start = "created_at_start"
        created_at_end = "created_at_end"
        updated_at_start = "updated_at_start"
        updated_at_end = "updated_at_end"

        self.sdk._get_following_alerts_page(organization_id,
                                            page=page,
                                            page_size=page_size,
                                            rule=rule,
                                            language=language,
                                            created_at_start=created_at_start,
                                            created_at_end=created_at_end,
                                            updated_at_start=updated_at_start,
                                            updated_at_end=updated_at_end)

        self.sdk._request.assert_called_once_with(
            "POST", f"/alerts/following",
            body={
                "organizationId": organization_id,
                "page": page,
                "pageSize": page_size,
                "rule": rule,
                "lang": language,
                "CreatedAtStart": created_at_start,
                "CreatedAtEnd": created_at_end,
                "UpdatedAtStart": updated_at_start,
                "UpdatedAtEnd": updated_at_end
            }
        )

    def test_get_following_alerts_page_str_following_ids(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        page = 1
        page_size = 100
        following_ids = "e22f4225-43e9-4922-b6b8-8b0620bdb110"

        self.sdk._get_following_alerts_page(organization_id,
                                            page=page,
                                            page_size=page_size,
                                            following_ids=following_ids)

        self.sdk._request.assert_called_once_with(
            "POST", f"/alerts/following",
            body={
                "organizationId": organization_id,
                "page": page,
                "pageSize": page_size,
                "followingIds": [following_ids]
            }
        )

    def test_get_following_alerts_page_iterable_following_ids(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        page = 1
        page_size = 100
        following_ids = ["e22f4225-43e9-4922-b6b8-8b0620bdb110", "e22f4225-43e9-4922-b6b8-8b0620bdb112"]

        self.sdk._get_following_alerts_page(organization_id,
                                            page=page,
                                            page_size=page_size,
                                            following_ids=following_ids)

        self.sdk._request.assert_called_once_with(
            "POST", f"/alerts/following",
            body={
                "organizationId": organization_id,
                "page": page,
                "pageSize": page_size,
                "followingIds": following_ids
            }
        )

    def test_get_following_alerts_page_str_states(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        page = 1
        page_size = 100
        states = zanshinsdk.AlertState.OPEN

        self.sdk._get_following_alerts_page(organization_id, page=page, page_size=page_size, states=states)

        self.sdk._request.assert_called_once_with(
            "POST", f"/alerts/following",
            body={
                "organizationId": organization_id,
                "page": page,
                "pageSize": page_size,
                "states": [states]
            }
        )

    def test_get_following_alerts_page_iterable_states(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        page = 1
        page_size = 100
        states = [zanshinsdk.AlertState.OPEN, zanshinsdk.AlertState.CLOSED]

        self.sdk._get_following_alerts_page(organization_id, page=page, page_size=page_size, states=states)

        self.sdk._request.assert_called_once_with(
            "POST", f"/alerts/following",
            body={
                "organizationId": organization_id,
                "page": page,
                "pageSize": page_size,
                "states": states
            }
        )

    def test_get_following_alerts_page_str_severities(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        page = 1
        page_size = 100
        severities = zanshinsdk.AlertSeverity.CRITICAL

        self.sdk._get_following_alerts_page(organization_id, page=page, page_size=page_size, severities=severities)

        self.sdk._request.assert_called_once_with(
            "POST", f"/alerts/following",
            body={
                "organizationId": organization_id,
                "page": page,
                "pageSize": page_size,
                "severities": [severities]
            }
        )

    def test_get_following_alerts_page_iterable_severities(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        page = 1
        page_size = 100
        severities = [zanshinsdk.AlertSeverity.CRITICAL, zanshinsdk.AlertSeverity.HIGH]

        self.sdk._get_following_alerts_page(organization_id, page=page, page_size=page_size, severities=severities)

        self.sdk._request.assert_called_once_with(
            "POST", f"/alerts/following",
            body={
                "organizationId": organization_id,
                "page": page,
                "pageSize": page_size,
                "severities": severities
            }
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
        language = zanshinsdk.Languages.ENUS
        cursor = "12345678"

        self.sdk._get_alerts_history_page(organization_id,
                                          page_size=page_size,
                                          language=language,
                                          cursor=cursor)

        self.sdk._request.assert_called_once_with(
            "POST", f"/alerts/history",
            body={
                "organizationId": organization_id,
                "pageSize": page_size,
                "lang": language,
                "cursor": cursor
            }
        )

    def test_get_alerts_history_page_str_scan_target_ids(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        page_size = 100
        scan_target_ids = "e22f4225-43e9-4922-b6b8-8b0620bdb110"

        self.sdk._get_alerts_history_page(organization_id,
                                          page_size=page_size,
                                          scan_target_ids=scan_target_ids)

        self.sdk._request.assert_called_once_with(
            "POST", f"/alerts/history",
            body={
                "organizationId": organization_id,
                "pageSize": page_size,
                "scanTargetIds": [scan_target_ids]
            }
        )

    def test_get_alerts_history_page_iterable_scan_target_ids(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        page_size = 100
        scan_target_ids = ["e22f4225-43e9-4922-b6b8-8b0620bdb110", "e22f4225-43e9-4922-b6b8-8b0620bdb112"]

        self.sdk._get_alerts_history_page(organization_id,
                                          page_size=page_size,
                                          scan_target_ids=scan_target_ids)

        self.sdk._request.assert_called_once_with(
            "POST", f"/alerts/history",
            body={
                "organizationId": organization_id,
                "pageSize": page_size,
                "scanTargetIds": scan_target_ids
            }
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
        language = zanshinsdk.Languages.ENUS
        cursor = "12345678"

        self.sdk._get_alerts_following_history_page(organization_id,
                                                    page_size=page_size,
                                                    language=language,
                                                    cursor=cursor)

        self.sdk._request.assert_called_once_with(
            "POST", f"/alerts/history/following",
            body={
                "organizationId": organization_id,
                "pageSize": page_size,
                "lang": language,
                "cursor": cursor
            }
        )

    def test_get_alerts_following_history_page_str_following_ids(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        page_size = 100
        following_ids = "e22f4225-43e9-4922-b6b8-8b0620bdb110"

        self.sdk._get_alerts_following_history_page(organization_id,
                                                    page_size=page_size,
                                                    following_ids=following_ids)

        self.sdk._request.assert_called_once_with(
            "POST", f"/alerts/history/following",
            body={
                "organizationId": organization_id,
                "pageSize": page_size,
                "followingIds": [following_ids]
            }
        )

    def test_get_alerts_following_history_page_iterable_following_ids(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        page_size = 100
        following_ids = ["e22f4225-43e9-4922-b6b8-8b0620bdb110", "e22f4225-43e9-4922-b6b8-8b0620bdb112"]

        self.sdk._get_alerts_following_history_page(organization_id,
                                                    page_size=page_size,
                                                    following_ids=following_ids)

        self.sdk._request.assert_called_once_with(
            "POST", f"/alerts/history/following",
            body={
                "organizationId": organization_id,
                "pageSize": page_size,
                "followingIds": following_ids
            }
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

        self.sdk._get_grouped_alerts_page(organization_id,
                                          page=page,
                                          page_size=page_size)

        self.sdk._request.assert_called_once_with(
            "POST", f"/alerts/rules",
            body={
                "organizationId": organization_id,
                "page": page,
                "pageSize": page_size
            }
        )

    def test_get_grouped_alerts_page_str_scan_target_ids(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        page = 1
        page_size = 100
        scan_target_ids = "e22f4225-43e9-4922-b6b8-8b0620bdb110"

        self.sdk._get_grouped_alerts_page(organization_id,
                                          page=page,
                                          page_size=page_size,
                                          scan_target_ids=scan_target_ids)

        self.sdk._request.assert_called_once_with(
            "POST", f"/alerts/rules",
            body={
                "organizationId": organization_id,
                "page": page,
                "pageSize": page_size,
                "scanTargetIds": [scan_target_ids]
            }
        )

    def test_get_grouped_alerts_page_iterable_scan_target_ids(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        page = 1
        page_size = 100
        scan_target_ids = ["e22f4225-43e9-4922-b6b8-8b0620bdb110", "e22f4225-43e9-4922-b6b8-8b0620bdb112"]

        self.sdk._get_grouped_alerts_page(organization_id,
                                          page=page,
                                          page_size=page_size,
                                          scan_target_ids=scan_target_ids)

        self.sdk._request.assert_called_once_with(
            "POST", f"/alerts/rules",
            body={
                "organizationId": organization_id,
                "page": page,
                "pageSize": page_size,
                "scanTargetIds": scan_target_ids
            }
        )

    def test_get_grouped_alerts_page_str_states(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        page = 1
        page_size = 100
        states = zanshinsdk.AlertState.OPEN

        self.sdk._get_grouped_alerts_page(organization_id, page=page, page_size=page_size, states=states)

        self.sdk._request.assert_called_once_with(
            "POST", f"/alerts/rules",
            body={
                "organizationId": organization_id,
                "page": page,
                "pageSize": page_size,
                "states": [states]
            }
        )

    def test_get_grouped_alerts_page_iterable_states(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        page = 1
        page_size = 100
        states = [zanshinsdk.AlertState.OPEN, zanshinsdk.AlertState.CLOSED]

        self.sdk._get_grouped_alerts_page(organization_id, page=page, page_size=page_size, states=states)

        self.sdk._request.assert_called_once_with(
            "POST", f"/alerts/rules",
            body={
                "organizationId": organization_id,
                "page": page,
                "pageSize": page_size,
                "states": states
            }
        )

    def test_get_grouped_alerts_page_str_severities(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        page = 1
        page_size = 100
        severities = zanshinsdk.AlertSeverity.CRITICAL

        self.sdk._get_grouped_alerts_page(organization_id, page=page, page_size=page_size, severities=severities)

        self.sdk._request.assert_called_once_with(
            "POST", f"/alerts/rules",
            body={
                "organizationId": organization_id,
                "page": page,
                "pageSize": page_size,
                "severities": [severities]
            }
        )

    def test_get_grouped_alerts_page_iterable_severities(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        page = 1
        page_size = 100
        severities = [zanshinsdk.AlertSeverity.CRITICAL, zanshinsdk.AlertSeverity.HIGH]

        self.sdk._get_grouped_alerts_page(organization_id, page=page, page_size=page_size, severities=severities)

        self.sdk._request.assert_called_once_with(
            "POST", f"/alerts/rules",
            body={
                "organizationId": organization_id,
                "page": page,
                "pageSize": page_size,
                "severities": severities
            }
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

    def test_get_grouped_following_alerts_page_str_following_ids(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        page = 1
        page_size = 100
        following_ids = "e22f4225-43e9-4922-b6b8-8b0620bdb110"

        self.sdk._get_grouped_following_alerts_page(organization_id,
                                                    page=page,
                                                    page_size=page_size,
                                                    following_ids=following_ids)

        self.sdk._request.assert_called_once_with(
            "POST", f"/alerts/rules/following",
            body={
                "organizationId": organization_id,
                "page": page,
                "pageSize": page_size,
                "followingIds": [following_ids]
            }
        )

    def test_get_grouped_following_alerts_page_iterable_following_ids(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        page = 1
        page_size = 100
        following_ids = ["e22f4225-43e9-4922-b6b8-8b0620bdb110", "e22f4225-43e9-4922-b6b8-8b0620bdb112"]

        self.sdk._get_grouped_following_alerts_page(organization_id,
                                                    page=page,
                                                    page_size=page_size,
                                                    following_ids=following_ids)

        self.sdk._request.assert_called_once_with(
            "POST", f"/alerts/rules/following",
            body={
                "organizationId": organization_id,
                "page": page,
                "pageSize": page_size,
                "followingIds": following_ids
            }
        )

    def test_get_grouped_following_alerts_page_str_states(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        page = 1
        page_size = 100
        states = zanshinsdk.AlertState.OPEN

        self.sdk._get_grouped_following_alerts_page(organization_id,
                                                    page=page,
                                                    page_size=page_size,
                                                    states=states)

        self.sdk._request.assert_called_once_with(
            "POST", f"/alerts/rules/following",
            body={
                "organizationId": organization_id,
                "page": page,
                "pageSize": page_size,
                "states": [states]
            }
        )

    def test_get_grouped_following_alerts_page_iterable_states(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        page = 1
        page_size = 100
        states = [zanshinsdk.AlertState.OPEN, zanshinsdk.AlertState.CLOSED]

        self.sdk._get_grouped_following_alerts_page(organization_id,
                                                    page=page,
                                                    page_size=page_size,
                                                    states=states)

        self.sdk._request.assert_called_once_with(
            "POST", f"/alerts/rules/following",
            body={
                "organizationId": organization_id,
                "page": page,
                "pageSize": page_size,
                "states": states
            }
        )

    def test_get_grouped_following_alerts_page_str_severities(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        page = 1
        page_size = 100
        severities = zanshinsdk.AlertSeverity.CRITICAL

        self.sdk._get_grouped_following_alerts_page(organization_id,
                                                    page=page,
                                                    page_size=page_size,
                                                    severities=severities)

        self.sdk._request.assert_called_once_with(
            "POST", f"/alerts/rules/following",
            body={
                "organizationId": organization_id,
                "page": page,
                "pageSize": page_size,
                "severities": [severities]
            }
        )

    def test_get_grouped_following_alerts_page_iterable_severities(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        page = 1
        page_size = 100
        severities = [zanshinsdk.AlertSeverity.CRITICAL, zanshinsdk.AlertSeverity.HIGH]

        self.sdk._get_grouped_following_alerts_page(organization_id,
                                                    page=page,
                                                    page_size=page_size,
                                                    severities=severities)

        self.sdk._request.assert_called_once_with(
            "POST", f"/alerts/rules/following",
            body={
                "organizationId": organization_id,
                "page": page,
                "pageSize": page_size,
                "severities": severities
            }
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
        state = zanshinsdk.AlertState.OPEN
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

    def test_get_alert_summaries_str_scan_target_ids(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        scan_target_ids = "e22f4225-43e9-4922-b6b8-8b0620bdb110"

        self.sdk.get_alert_summaries(organization_id,
                                     scan_target_ids=scan_target_ids)

        self.sdk._request.assert_called_once_with(
            "POST", f"/alerts/summaries",
            body={
                "organizationId": organization_id,
                "scanTargetIds": [scan_target_ids]
            }
        )

    def test_get_alert_summaries_iterable_scan_target_ids(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        scan_target_ids = ["e22f4225-43e9-4922-b6b8-8b0620bdb110", "e22f4225-43e9-4922-b6b8-8b0620bdb112"]

        self.sdk.get_alert_summaries(organization_id,
                                     scan_target_ids=scan_target_ids)

        self.sdk._request.assert_called_once_with(
            "POST", f"/alerts/summaries",
            body={
                "organizationId": organization_id,
                "scanTargetIds": scan_target_ids
            }
        )

    def test_get_following_alert_summaries(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"

        self.sdk.get_following_alert_summaries(organization_id)

        self.sdk._request.assert_called_once_with(
            "POST", f"/alerts/summaries/following",
            body={"organizationId": organization_id}
        )

    def test_get_following_alert_summaries_str_following_ids(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        following_ids = "e22f4225-43e9-4922-b6b8-8b0620bdb110"

        self.sdk.get_following_alert_summaries(organization_id,
                                               following_ids=following_ids)

        self.sdk._request.assert_called_once_with(
            "POST", f"/alerts/summaries/following",
            body={
                "organizationId": organization_id,
                "followingIds": [following_ids]
            }
        )

    def test_get_following_alert_summaries_iterable_following_ids(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        following_ids = ["e22f4225-43e9-4922-b6b8-8b0620bdb110", "e22f4225-43e9-4922-b6b8-8b0620bdb112"]

        self.sdk.get_following_alert_summaries(organization_id,
                                               following_ids=following_ids)

        self.sdk._request.assert_called_once_with(
            "POST", f"/alerts/summaries/following",
            body={
                "organizationId": organization_id,
                "followingIds": following_ids
            }
        )

    def test_get_scan_summaries(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        days = 7

        self.sdk.get_scan_summaries(organization_id, days=days)

        self.sdk._request.assert_called_once_with(
            "POST", f"/alerts/summaries/scans",
            body={
                "organizationId": organization_id,
                "daysBefore": days
            }
        )

    def test_get_scan_summaries_str_scan_target_ids(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        days = 7
        scan_target_ids = "e22f4225-43e9-4922-b6b8-8b0620bdb110"

        self.sdk.get_scan_summaries(organization_id,
                                    days=days,
                                    scan_target_ids=scan_target_ids)

        self.sdk._request.assert_called_once_with(
            "POST", f"/alerts/summaries/scans",
            body={
                "organizationId": organization_id,
                "daysBefore": days,
                "scanTargetIds": [scan_target_ids]
            }
        )

    def test_get_scan_summaries_iterable_scan_target_ids(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        days = 7
        scan_target_ids = ["e22f4225-43e9-4922-b6b8-8b0620bdb110", "e22f4225-43e9-4922-b6b8-8b0620bdb112"]

        self.sdk.get_scan_summaries(organization_id,
                                    days=days,
                                    scan_target_ids=scan_target_ids)

        self.sdk._request.assert_called_once_with(
            "POST", f"/alerts/summaries/scans",
            body={
                "organizationId": organization_id,
                "daysBefore": days,
                "scanTargetIds": scan_target_ids
            }
        )

    def test_get_following_scan_summaries(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        days = 7

        self.sdk.get_following_scan_summaries(organization_id, days=days)

        self.sdk._request.assert_called_once_with(
            "POST", f"/alerts/summaries/scans/following",
            body={
                "organizationId": organization_id,
                "daysBefore": days
            }
        )

    def test_get_following_scan_summaries_str_following_ids(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        days = 7
        following_ids = "e22f4225-43e9-4922-b6b8-8b0620bdb110"

        self.sdk.get_following_scan_summaries(organization_id,
                                              days=days,
                                              following_ids=following_ids)

        self.sdk._request.assert_called_once_with(
            "POST", f"/alerts/summaries/scans/following",
            body={
                "organizationId": organization_id,
                "daysBefore": days,
                "followingIds": [following_ids]
            }
        )

    def test_get_following_scan_summaries_iterable_following_ids(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        days = 7
        following_ids = ["e22f4225-43e9-4922-b6b8-8b0620bdb110", "e22f4225-43e9-4922-b6b8-8b0620bdb112"]

        self.sdk.get_following_scan_summaries(organization_id,
                                              days=days,
                                              following_ids=following_ids)

        self.sdk._request.assert_called_once_with(
            "POST", f"/alerts/summaries/scans/following",
            body={
                "organizationId": organization_id,
                "daysBefore": days,
                "followingIds": following_ids
            }
        )

    ###################################################
    # validates
    ###################################################

    def test__repr__(self):
        _response = f"Connection(api_url='https://api.zanshin.tenchisecurity.com', api_key='***pi_key', " \
                    f"user_agent='Zanshin Python SDK v{zanshinsdk.__version__}', proxy_url='None')"
        self.assertEqual(self.sdk.__repr__(), _response)

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
            self.assertEqual(str(e), f"{_int} shouldn\'t be lower than {_min_value}")

    def test_validate_int_higher_than(self):
        _int = 11
        _max_value = 10
        try:
            zanshinsdk.client.validate_int(_int, max_value=_max_value)
        except Exception as e:
            self.assertEqual(str(e), f"{_int} shouldn\'t be higher than {_max_value}")

    def test_validate_class(self):
        _invalid_class = "invalid"
        try:
            zanshinsdk.client.validate_class(_invalid_class, UUID)
        except Exception as e:
            self.assertEqual(str(e), f"{repr(_invalid_class)} is not an instance of {UUID.__name__}")

    def test_validate_uuid(self):
        _uuid = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        _response = zanshinsdk.client.validate_uuid(UUID(_uuid))
        self.assertEqual(_uuid, _response)

    def test_validate_uuid_invalid(self):
        _uuid = "invalid_uuid"
        try:
            zanshinsdk.client.validate_uuid(_uuid)
        except Exception as e:
            self.assertEqual(str(e), f"{repr(_uuid)} is not a valid UUID")
