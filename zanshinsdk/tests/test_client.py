import os
import unittest
from pathlib import Path
from unittest.mock import Mock, call, mock_open, patch
from uuid import UUID

from httpx import Request, Response
from moto import mock_cloudformation, mock_s3, mock_sts

import zanshinsdk


class TestClient(unittest.TestCase):
    ###################################################
    # setUp
    ###################################################

    @patch("zanshinsdk.client.isfile")
    @patch("zanshinsdk.Client._request")
    def setUp(self, request, mock_is_file):
        mock_is_file.return_value = True
        _data = "[default]\napi_key=api_key"

        with patch("__main__.__builtins__.open", mock_open(read_data=_data)):
            self.sdk = zanshinsdk.Client()
            self.sdk._request = request

        self.HAVE_BOTO3 = False
        try:
            import boto3

            self.HAVE_BOTO3 = True
        except ModuleNotFoundError:
            pass
            self.HAVE_BOTO3 = False

    ###################################################
    # __init__
    ###################################################

    @patch("zanshinsdk.client.isfile")
    def test_init_empty_profile(self, mock_is_file):
        mock_is_file.return_value = True
        _data = "[default]\napi_key=api_key"

        try:
            with patch("__main__.__builtins__.open", mock_open(read_data=_data)):
                zanshinsdk.Client(profile="")
        except Exception as e:
            self.assertIn("profile  not found", str(e))

    @patch("zanshinsdk.client.isfile")
    def test_init_wrong_profile(self, mock_is_file):
        mock_is_file.return_value = True
        _profile = "XYZ"
        _data = "[default]\napi_key=api_key"

        try:
            with patch("__main__.__builtins__.open", mock_open(read_data=_data)):
                zanshinsdk.Client(profile=_profile)
        except Exception as e:
            self.assertEqual(
                str(e),
                f"profile {_profile} not found in {zanshinsdk.client.CONFIG_FILE}",
            )

    @patch("zanshinsdk.client.isfile")
    def test_init_api_url(self, mock_is_file):
        mock_is_file.return_value = True
        _api_url = "https://api.test"
        _data = "[default]\napi_key=api_key"

        with patch("__main__.__builtins__.open", mock_open(read_data=_data)):
            client = zanshinsdk.Client(api_url=_api_url)

        self.assertEqual(client._api_url, _api_url)

    @patch("zanshinsdk.client.isfile")
    def test_init_invalid_api_url(self, mock_is_file):
        mock_is_file.return_value = True
        _api_url = "invalid://api.test"
        _data = "[default]\napi_key=api_key"

        try:
            with patch("__main__.__builtins__.open", mock_open(read_data=_data)):
                zanshinsdk.Client(api_url=_api_url)
        except Exception as e:
            self.assertEqual(str(e), f"Invalid API URL: {_api_url}")

    @patch("zanshinsdk.client.isfile")
    def test_init_api_url_from_config(self, mock_is_file):
        mock_is_file.return_value = True
        _api_url = "https://api.test"
        _data = f"[default]\napi_key=api_key\napi_url={_api_url}"

        with patch("__main__.__builtins__.open", mock_open(read_data=_data)):
            client = zanshinsdk.Client()

        self.assertEqual(client._api_url, _api_url)

    @patch("zanshinsdk.client.isfile")
    def test_init_proxy_url(self, mock_is_file):
        mock_is_file.return_value = True
        _proxy_url = "https://proxy.test"
        _data = "[default]\napi_key=api_key"

        with patch("__main__.__builtins__.open", mock_open(read_data=_data)):
            client = zanshinsdk.Client(proxy_url=_proxy_url)

        self.assertEqual(client._proxy_url, _proxy_url)

    @patch("zanshinsdk.client.isfile")
    def test_init_invalid_proxy_url(self, mock_is_file):
        mock_is_file.return_value = True
        _proxy_url = "invalid://proxy.api.test"
        _data = "[default]\napi_key=api_key"

        try:
            with patch("__main__.__builtins__.open", mock_open(read_data=_data)):
                zanshinsdk.Client(proxy_url=_proxy_url)
        except Exception as e:
            self.assertEqual(str(e), f"Invalid proxy URL: {_proxy_url}")

    @patch("zanshinsdk.client.isfile")
    def test_init_proxy_url_from_config(self, mock_is_file):
        mock_is_file.return_value = True
        _proxy_url = "https://proxy.test"
        _data = f"[default]\napi_key=api_key\nproxy_url={_proxy_url}"

        with patch("__main__.__builtins__.open", mock_open(read_data=_data)):
            client = zanshinsdk.Client()

        self.assertEqual(client._proxy_url, _proxy_url)

    @patch("zanshinsdk.client.isfile")
    def test_init_user_agent(self, mock_is_file):
        mock_is_file.return_value = True
        _user_agent = "test_agent"
        _data = "[default]\napi_key=api_key"

        with patch("__main__.__builtins__.open", mock_open(read_data=_data)):
            client = zanshinsdk.Client(user_agent=_user_agent)

        self.assertEqual(
            client._user_agent,
            f"{_user_agent} (Zanshin Python SDK v{zanshinsdk.version.__version__})",
        )

    @patch("zanshinsdk.client.isfile")
    def test_init_user_agent_from_config(self, mock_is_file):
        mock_is_file.return_value = True
        _user_agent = "test_agent"
        _data = f"[default]\napi_key=api_key\nuser_agent={_user_agent}"

        with patch("__main__.__builtins__.open", mock_open(read_data=_data)):
            client = zanshinsdk.Client()

        self.assertEqual(
            client._user_agent,
            f"{_user_agent} (Zanshin Python SDK v{zanshinsdk.version.__version__})",
        )

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
    # _update_client except
    ###################################################

    @patch("zanshinsdk.client.isfile")
    def test_update_client_except(self, mock_is_file):
        mock_is_file.return_value = True
        _data = "[default]\napi_key=api_key"

        with patch("__main__.__builtins__.open", mock_open(read_data=_data)):
            client = zanshinsdk.Client()

        client._client = None
        client._update_client()

        self.assertIsNotNone(client._client)

    ###################################################
    # Properties
    ###################################################

    @patch("zanshinsdk.client.isfile")
    def test_get_api_url(self, mock_is_file):
        mock_is_file.return_value = True
        _api_url = "https://api.test"
        _data = "[default]\napi_key=api_key"

        with patch("__main__.__builtins__.open", mock_open(read_data=_data)):
            client = zanshinsdk.Client(api_url=_api_url)

        self.assertEqual(client.api_url, _api_url)

    @patch("zanshinsdk.client.isfile")
    def test_set_api_url(self, mock_is_file):
        mock_is_file.return_value = True
        _api_url = "https://api.test"
        _new_api_url = "https://new.api.test"
        _data = "[default]\napi_key=api_key"

        with patch("__main__.__builtins__.open", mock_open(read_data=_data)):
            client = zanshinsdk.Client(api_url=_api_url)

        client.api_url = _new_api_url

        self.assertEqual(client.api_url, _new_api_url)

    @patch("zanshinsdk.client.isfile")
    def test_set_invalid_api_url(self, mock_is_file):
        mock_is_file.return_value = True
        _api_url = "https://api.test"
        _new_api_url = "invalid://new.api.test"
        _data = "[default]\napi_key=api_key"

        try:
            with patch("__main__.__builtins__.open", mock_open(read_data=_data)):
                client = zanshinsdk.Client(api_url=_api_url)

            client.api_url = _new_api_url
        except Exception as e:
            self.assertEqual(str(e), f"Invalid API URL: {_new_api_url}")

    @patch("zanshinsdk.client.isfile")
    def test_set_none_api_url(self, mock_is_file):
        mock_is_file.return_value = True
        _api_key = "https://api.test"
        _data = "[default]\napi_key=api_key"

        try:
            with patch("__main__.__builtins__.open", mock_open(read_data=_data)):
                client = zanshinsdk.Client(api_url=_api_key)

            client.api_url = None
        except Exception as e:
            self.assertEqual(str(e), f"API URL cannot be null")

    @patch("zanshinsdk.client.isfile")
    def test_get_api_key(self, mock_is_file):
        mock_is_file.return_value = True
        _api_key = "api_key"
        _data = "[default]\napi_key=api_key"

        with patch("__main__.__builtins__.open", mock_open(read_data=_data)):
            client = zanshinsdk.Client(api_key=_api_key)

        self.assertEqual(client.api_key, _api_key)

    @patch("zanshinsdk.client.isfile")
    def test_set_api_key(self, mock_is_file):
        mock_is_file.return_value = True
        _api_key = "api_key"
        _new_api_key = "new_api_key"
        _data = "[default]\napi_key=api_key"

        with patch("__main__.__builtins__.open", mock_open(read_data=_data)):
            client = zanshinsdk.Client(api_key=_api_key)

        client.api_key = _new_api_key

        self.assertEqual(client.api_key, _new_api_key)

    @patch("zanshinsdk.client.isfile")
    def test_get_proxy_url(self, mock_is_file):
        mock_is_file.return_value = True
        _proxy_url = "https://proxy.test"
        _data = "[default]\napi_key=api_key"

        with patch("__main__.__builtins__.open", mock_open(read_data=_data)):
            client = zanshinsdk.Client(proxy_url=_proxy_url)

        self.assertEqual(client.proxy_url, _proxy_url)

    @patch("zanshinsdk.client.isfile")
    def test_set_proxy_url(self, mock_is_file):
        mock_is_file.return_value = True
        _proxy_url = "https://proxy.test"
        _new_proxy_url = "https://new.proxy.test"
        _data = "[default]\napi_key=api_key"

        with patch("__main__.__builtins__.open", mock_open(read_data=_data)):
            client = zanshinsdk.Client(proxy_url=_proxy_url)

        client.proxy_url = _new_proxy_url

        self.assertEqual(client.proxy_url, _new_proxy_url)

    @patch("zanshinsdk.client.isfile")
    def test_set_invalid_proxy_url(self, mock_is_file):
        mock_is_file.return_value = True
        _proxy_url = "https://proxy.test"
        _new_proxy_url = "invalid://new.proxy.test"
        _data = "[default]\napi_key=api_key"

        try:
            with patch("__main__.__builtins__.open", mock_open(read_data=_data)):
                client = zanshinsdk.Client(proxy_url=_proxy_url)

            client.proxy_url = _new_proxy_url
        except Exception as e:
            self.assertEqual(str(e), f"Invalid proxy URL: {_new_proxy_url}")

    @patch("zanshinsdk.client.isfile")
    def test_set_equal_proxy_url(self, mock_is_file):
        mock_is_file.return_value = True
        _proxy_url = "https://proxy.test"
        _data = "[default]\napi_key=api_key"

        with patch("__main__.__builtins__.open", mock_open(read_data=_data)):
            client = zanshinsdk.Client(proxy_url=_proxy_url)

        client.proxy_url = _proxy_url

        self.assertEqual(client.proxy_url, _proxy_url)

    @patch("zanshinsdk.client.isfile")
    def test_set_none_proxy_url(self, mock_is_file):
        mock_is_file.return_value = True
        _proxy_url = "https://proxy.test"
        _data = "[default]\napi_key=api_key"

        with patch("__main__.__builtins__.open", mock_open(read_data=_data)):
            client = zanshinsdk.Client(proxy_url=_proxy_url)

        client.proxy_url = None

        self.assertIsNone(client.proxy_url)

    @patch("zanshinsdk.client.isfile")
    def test_get_user_agent(self, mock_is_file):
        mock_is_file.return_value = True
        _user_agent = "test_agent"
        _data = "[default]\napi_key=api_key"

        with patch("__main__.__builtins__.open", mock_open(read_data=_data)):
            client = zanshinsdk.Client(user_agent=_user_agent)

        self.assertEqual(
            client.user_agent,
            f"{_user_agent} (Zanshin Python SDK v{zanshinsdk.version.__version__})",
        )

    @patch("zanshinsdk.client.isfile")
    def test_set_user_agent(self, mock_is_file):
        mock_is_file.return_value = True
        _user_agent = "test_agent"
        _new_user_agent = "new_test_agent"
        _data = "[default]\napi_key=api_key"

        with patch("__main__.__builtins__.open", mock_open(read_data=_data)):
            client = zanshinsdk.Client(user_agent=_user_agent)

        client.user_agent = _new_user_agent

        self.assertEqual(
            client.user_agent,
            f"{_new_user_agent} (Zanshin Python SDK v{zanshinsdk.version.__version__})",
        )

    @patch("zanshinsdk.client.isfile")
    def test_get_sanitized_proxy_url_none(self, mock_is_file):
        mock_is_file.return_value = True
        _data = "[default]\napi_key=api_key"

        with patch("__main__.__builtins__.open", mock_open(read_data=_data)):
            client = zanshinsdk.Client()

        self.assertIsNone(client._get_sanitized_proxy_url())

    @patch("zanshinsdk.client.isfile")
    def test_get_sanitized_proxy_url(self, mock_is_file):
        mock_is_file.return_value = True
        _proxy_url = "https://username:password@proxy.test:8000"
        _data = "[default]\napi_key=api_key"

        with patch("__main__.__builtins__.open", mock_open(read_data=_data)):
            client = zanshinsdk.Client(proxy_url=_proxy_url)

        self.assertIsNotNone(client._get_sanitized_proxy_url())

    ###################################################
    # Request
    ###################################################

    @patch("zanshinsdk.client.isfile")
    @patch("zanshinsdk.client.httpx.Client.request")
    def test_request(self, request, mock_is_file):
        mock_is_file.return_value = True
        _api_url = "https://api.test"
        _data = "[default]\napi_key=api_key"

        with patch("__main__.__builtins__.open", mock_open(read_data=_data)):
            client = zanshinsdk.Client(api_url=_api_url)

        req = Request(method="GET", url=f"{_api_url}/path", content="{}")
        value = Response(request=req, status_code=200)
        request.return_value = value
        client._client.request = request
        client._request("GET", "/path")

        client._client.request.assert_called_once_with(
            method="GET", url=f"{_api_url}/path", params=None, json=None
        )

    @patch("zanshinsdk.client.isfile")
    @patch("zanshinsdk.client.httpx.Client.request")
    def test_request_without_content(self, request, mock_is_file):
        mock_is_file.return_value = True
        _api_url = "https://api.test"
        _data = "[default]\napi_key=api_key"

        with patch("__main__.__builtins__.open", mock_open(read_data=_data)):
            client = zanshinsdk.Client(api_url=_api_url)

        req = Request(method="GET", url=f"{_api_url}/path")
        value = Response(request=req, status_code=200)
        request.return_value = value
        client._client.request = request
        client._request("GET", "/path")

        client._client.request.assert_called_once_with(
            method="GET", url=f"{_api_url}/path", params=None, json=None
        )

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
        with patch(
            "__main__.__builtins__.open",
            mock_open(read_data="[default]\napi_key=api_key"),
        ):
            request.return_value = Mock(
                status_code=200, json=lambda: {"data": [scan_data]}
            )
            client = zanshinsdk.Client()
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
        scan_target_ids = ["421cfe8a-1777-4000-a000-f836dfdfcfb8"]
        order = zanshinsdk.AlertsOrderOpts.SEVERITY
        scan_target_tags = None
        include_empty_scan_target_tags = None
        cursor = "eyJpZCI6IjAyYWQxOGU3LTY1ODUtNDAwMC1hMDAwLWY2YTQzMTFlYzI4NyJ9"
        resolved_at_start = "2025-02-10"
        resolved_at_end = "2025-02-12T20:22:54.440101Z"
        severities = zanshinsdk.AlertSeverity.CRITICAL

        self.sdk._get_alerts_page(
            organization_id=organization_id,
            scan_target_ids=scan_target_ids,
            scan_target_tags=scan_target_tags,
            include_empty_scan_target_tags=include_empty_scan_target_tags,
            cursor=cursor,
            order=order,
            severities=severities,
            resolved_at_start=resolved_at_start,
            resolved_at_end=resolved_at_end,
        )

        self.sdk._request.assert_called_once_with(
            "POST",
            f"/organizations/{organization_id}/alerts",
            body={
                "order": order.value,
                "scanTargetIds": scan_target_ids,
                "severities": ["CRITICAL"],
                "resolvedAtStart": "2025-02-10T00:00:00",
                "resolvedAtEnd": "2025-02-12T20:22:54.440101",
            },
            params={
                "cursor": "eyJpZCI6IjAyYWQxOGU3LTY1ODUtNDAwMC1hMDAwLWY2YTQzMTFlYzI4NyJ9"
            },
        )

    @patch("zanshinsdk.client.Client._get_alerts_page")
    def test_iter_alerts(self, request):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        scan_target_ids = ["421cfe8a-1777-4000-a000-f836dfdfcfb8"]
        request.return_value = {
            "data": [""],
            "cursor": None,
        }
        self.sdk._get_alerts_page = request
        iterator = self.sdk.iter_alerts(
            organization_id, scan_target_ids=scan_target_ids
        )
        next(iterator)

        self.sdk._get_alerts_page.assert_called_once_with(
            organization_id,
            scan_target_ids,
            scan_target_tags=None,
            include_empty_scan_target_tags=None,
            cursor=None,
            order=None,
            rules=None,
            states=None,
            severities=None,
            lang=None,
            opened_at_start=None,
            opened_at_end=None,
            resolved_at_start=None,
            resolved_at_end=None,
            created_at_start=None,
            created_at_end=None,
            updated_at_start=None,
            updated_at_end=None,
            search=None,
            sort=None,
        )

    def test_get_following_alerts_page(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        following_ids = ["421cfe8a-1777-4000-a000-f836dfdfcfb8"]
        order = zanshinsdk.AlertsOrderOpts.SEVERITY
        following_tags = None
        include_empty_following_tags = None
        cursor = "eyJpZCI6IjAyYWQxOGU3LTY1ODUtNDAwMC1hMDAwLWY2YTQzMTFlYzI4NyJ9"
        opened_at_start = "2025-01-10"
        severities = [zanshinsdk.AlertSeverity.CRITICAL, zanshinsdk.AlertSeverity.HIGH]

        self.sdk._get_following_alerts_page(
            organization_id=organization_id,
            following_ids=following_ids,
            following_tags=following_tags,
            include_empty_following_tags=include_empty_following_tags,
            opened_at_start=opened_at_start,
            severities=severities,
            cursor=cursor,
            order=order,
        )
        self.sdk._request.assert_called_once_with(
            "POST",
            f"/organizations/{organization_id}/followings/alerts",
            body={
                "order": zanshinsdk.AlertsOrderOpts.SEVERITY.value,
                "followingIds": following_ids,
                "severities": ["CRITICAL", "HIGH"],
                "openedAtStart": "2025-01-10T00:00:00",
            },
            params={
                "cursor": "eyJpZCI6IjAyYWQxOGU3LTY1ODUtNDAwMC1hMDAwLWY2YTQzMTFlYzI4NyJ9"
            },
        )

    @patch("zanshinsdk.client.Client._get_following_alerts_page")
    def test_iter_following_alerts(self, request):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        following_ids = ["421cfe8a-1777-4000-a000-f836dfdfcfb8"]
        request.return_value = {
            "data": [""],
            "cursor": None,
        }
        self.sdk._get_following_alerts_page = request
        iterator = self.sdk.iter_following_alerts(
            organization_id, following_ids=following_ids
        )
        next(iterator)
        self.sdk._get_following_alerts_page.assert_called_once_with(
            organization_id,
            following_ids,
            following_tags=None,
            include_empty_following_tags=None,
            cursor=None,
            order=None,
            rules=None,
            states=None,
            severities=None,
            lang=None,
            opened_at_start=None,
            opened_at_end=None,
            resolved_at_start=None,
            resolved_at_end=None,
            created_at_start=None,
            created_at_end=None,
            updated_at_start=None,
            updated_at_end=None,
            search=None,
            sort=None,
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
        order = zanshinsdk.GroupedAlertOrderOpts.SEVERITY
        page_size = 50

        self.sdk._get_grouped_alerts_page(
            organization_id, page_size=page_size, order=order
        )

        self.sdk._request.assert_called_once_with(
            "POST",
            f"/organizations/{organization_id}/alerts/rules",
            body={"order": order},
            params={"pageSize": page_size},
        )

    @patch("zanshinsdk.client.Client._get_grouped_alerts_page")
    def test_iter_grouped_alerts(self, request):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        request.return_value = {"data": [""], "cursor": None}
        self.sdk._get_grouped_alerts_page = request
        iterator = self.sdk.iter_grouped_alerts(organization_id)
        next(iterator)
        self.sdk._get_grouped_alerts_page.assert_called_once_with(
            organization_id,
            scan_target_ids=None,
            scan_tagert_tags=None,
            include_empty_scan_target_tags=None,
            cursor=None,
            page_size=100,
            order=None,
            rules=None,
            states=None,
            severities=None,
            lang=None,
            opened_at_start=None,
            opened_at_end=None,
            resolved_at_start=None,
            resolved_at_end=None,
            created_at_start=None,
            created_at_end=None,
            updated_at_start=None,
            updated_at_end=None,
            search=None,
            sort=None,
        )

    def test_get_grouped_following_alerts_page(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        following_ids = ["421cfe8a-1777-4000-a000-f836dfdfcfb8"]
        order = zanshinsdk.GroupedAlertOrderOpts.SEVERITY
        following_tags = None
        include_empty_following_tags = None
        cursor = "eyJpZCI6IjAyYWQxOGU3LTY1ODUtNDAwMC1hMDAwLWY2YTQzMTFlYzI4NyJ9"

        self.sdk._get_grouped_following_alerts_page(
            organization_id=organization_id,
            following_ids=following_ids,
            following_tags=following_tags,
            include_empty_following_tags=include_empty_following_tags,
            cursor=cursor,
            order=order,
        )
        self.sdk._request.assert_called_once_with(
            "POST",
            f"/organizations/{organization_id}/followings/alerts/rules",
            body={
                "order": order,
                "followingIds": following_ids,
            },
            params={
                "cursor": "eyJpZCI6IjAyYWQxOGU3LTY1ODUtNDAwMC1hMDAwLWY2YTQzMTFlYzI4NyJ9",
                "pageSize": 100,
            },
        )

    @patch("zanshinsdk.client.Client._get_grouped_following_alerts_page")
    def test_iter_grouped_following_alerts(self, request):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        following_ids = ["421cfe8a-1777-4000-a000-f836dfdfcfb8"]
        request.return_value = {
            "data": [""],
            "cursor": None,
        }
        self.sdk._get_grouped_following_alerts_page = request
        iterator = self.sdk.iter_grouped_following_alerts(
            organization_id, following_ids=following_ids
        )
        next(iterator)
        self.sdk._get_grouped_following_alerts_page.assert_called_once_with(
            organization_id,
            following_ids,
            following_tags=None,
            include_empty_following_tags=None,
            cursor=None,
            page_size=100,
            order=None,
            rules=None,
            states=None,
            severities=None,
            lang=None,
            opened_at_start=None,
            opened_at_end=None,
            resolved_at_start=None,
            resolved_at_end=None,
            created_at_start=None,
            created_at_end=None,
            updated_at_start=None,
            updated_at_end=None,
            search=None,
            sort=None,
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
            "/alerts/summaries/scans/following",
            body={
                "organizationId": organization_id,
                "daysBefore": days,
                "followingIds": following_ids,
            },
        )

    def test_get_scan_targets_following_summary(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        scan_target_kinds = [zanshinsdk.ScanTargetKind.DOMAIN]
        alert_severities = [zanshinsdk.AlertSeverity.HIGH]

        self.sdk.get_scan_targets_following_summary(
            organization_id=organization_id,
            scan_target_kinds=scan_target_kinds,
            alert_severities=alert_severities,
        )

        self.sdk._request.assert_called_once_with(
            "POST",
            f"/organizations/{organization_id}/followings/summaries/scantargets/details",
            body={
                "scanTargetKinds": scan_target_kinds,
                "alertSeverities": alert_severities,
            },
        )

    def test_get_scan_target_detail_summary(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        scan_target_kinds = [zanshinsdk.ScanTargetKind.SLACK]
        alert_severities = [zanshinsdk.AlertSeverity.MEDIUM]

        self.sdk.get_scan_target_detail_summary(
            organization_id=organization_id,
            scan_target_kinds=scan_target_kinds,
            alert_severities=alert_severities,
        )

        self.sdk._request.assert_called_once_with(
            "POST",
            f"/organizations/{organization_id}/summaries/scantargets/details",
            body={
                "scanTargetKinds": scan_target_kinds,
                "alertSeverities": alert_severities,
            },
        )

    ###################################################
    # validates
    ###################################################

    def test__repr__(self):
        _response = (
            f"Connection(api_url='https://api.zanshin.tenchisecurity.com', api_key='***pi_key', "
            f"user_agent='Zanshin Python SDK v{zanshinsdk.version.__version__}', proxy_url='None')"
        )
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
        _response = zanshinsdk.client.validate_uuid(UUID(_uuid))
        self.assertEqual(_uuid, _response)

    def test_validate_uuid_invalid(self):
        _uuid = "invalid_uuid"
        try:
            zanshinsdk.client.validate_uuid(_uuid)
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

    @unittest.skipUnless("HAVE_BOTO3", "requires boto3")
    @patch("zanshinsdk.client.isfile")
    @patch("zanshinsdk.Client._request")
    @mock_sts
    @mock_cloudformation
    @mock_s3
    def test_onboard_scan_target_aws_boto3_profile(self, request, mock_is_file):
        """
        Call onboard_scan_target with valid boto3_profile.
        Skip this test unless boto3 is installed in environment.
        Mock the creation of a new Scan Target, and behavior of AWS Services STS, CloudFormation and S3.

        :param region: str
        :param organization_id: str
        :param kind: ScanTargetKind.AZURE
        :param credential: ScanTargetAZURE
        :param boto3_profile: str
        :param schedule: obj

        Asserts:
        * New Scan Target was created, with given parameters.
        * Scan was Started for this new Scan Target.
        * CloudFormation with Zanshin Role was deployed sucessfully.

        >>> new_scan_target = self.sdk.onboard_scan_target(
                region, organization_id, kind, name, credential, None, boto3_profile, schedule)
        """
        import json

        import boto3

        # Setup test data
        aws_account_id = "123456789012"
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        created_scan_target_id = "14f79567-6b68-4e3a-b2f2-4f1383546251"
        kind = zanshinsdk.ScanTargetKind.AWS
        name = "OnboardTesting-it"
        credential = zanshinsdk.ScanTargetAWS(aws_account_id)
        schedule = zanshinsdk.DAILY
        region = "us-east-1"
        boto3_profile = "foo"

        # Mock AWS Credentials for Boto3
        self.mock_aws_credentials()

        # Mock request to create new Scan Target
        mock_is_file.return_value = True
        _data = "[default]\napi_key=api_key"

        with patch("__main__.__builtins__.open", mock_open(read_data=_data)):
            request.return_value = Mock(
                status_code=200, json=lambda: {"id": created_scan_target_id}
            )
            client = zanshinsdk.Client()
            client._client.request = request

        # Create Mocked S3 tenchi-assets bucket
        with open(
            "zanshinsdk/tests/data/dummy_cloudformation_zanshin_service_role_template.json",
            "r",
        ) as dummy_template_file:
            DUMMY_TEMPLATE = json.load(dummy_template_file)
            s3 = boto3.client("s3", region_name="us-east-2")
            s3.create_bucket(
                Bucket="tenchi-assets",
                CreateBucketConfiguration={"LocationConstraint": "us-east-2"},
            )
            s3.put_object(
                Bucket="tenchi-assets",
                Key="zanshin-service-role.template",
                Body=json.dumps(DUMMY_TEMPLATE),
            )

        # Call method onboard_scan_target with boto3_profile
        new_scan_target = client.onboard_scan_target(
            region,
            organization_id,
            kind,
            name,
            credential,
            None,
            boto3_profile,
            schedule,
        )

        # Assert that Scan Target was created
        self.assertEqual(created_scan_target_id, new_scan_target["id"])

        # Assert that Scan Target was called with correct parameters
        client._client.request.assert_any_call(
            "POST",
            f"/organizations/{organization_id}/scantargets",
            body={
                "name": name,
                "kind": kind,
                "schedule": {"frequency": "1d", "timeOfDay": "NIGHT"},
                "credential": {"account": aws_account_id},
            },
        )
        # Assert that we checked Scan Target to start scan
        client._client.request.assert_any_call(
            "POST",
            f"/organizations/{organization_id}/scantargets/{created_scan_target_id}/check",
        )

        # Assert CloudFormation Stack was created successfully
        zanshin_cloudformation_stack_name = "tenchi-zanshin-service-role"
        cloudformation = boto3.client("cloudformation", region_name="us-east-1")
        zanshin_stack = cloudformation.describe_stacks(
            StackName=zanshin_cloudformation_stack_name
        )["Stacks"][0]
        self.assertEqual("CREATE_COMPLETE", zanshin_stack["StackStatus"])
        self.assertEqual(zanshin_cloudformation_stack_name, zanshin_stack["StackName"])

        # Clean Up CloudFormation
        cf_stacks = cloudformation.describe_stacks(
            StackName=zanshin_cloudformation_stack_name
        )
        for cf_stack in cf_stacks["Stacks"]:
            cloudformation.delete_stack(StackName=cf_stack["StackName"])

    @unittest.skipUnless("HAVE_BOTO3", "requires boto3")
    @patch("zanshinsdk.client.isfile")
    @patch("zanshinsdk.Client._request")
    @mock_sts
    @mock_cloudformation
    @mock_s3
    def test_onboard_scan_target_aws_boto3_session(self, request, mock_is_file):
        """
        Call onboard_scan_target with valid boto3_session.
        Skip this test unless boto3 is installed in environment.
        Mock the creation of a new Scan Target, and behavior of AWS Services STS, CloudFormation and S3.

        :param region: str
        :param organization_id: str
        :param kind: ScanTargetKind.AZURE
        :param credential: ScanTargetAZURE
        :param boto3_profile: str
        :param schedule: obj

        Asserts:
        * New Scan Target was created, with given parameters.
        * Scan was Started for this new Scan Target.
        * CloudFormation with Zanshin Role was deployed sucessfully.

        >>> new_scan_target = self.sdk.onboard_scan_target(
                region, organization_id, kind, name, credential, None, boto3_profile, schedule)
        """
        import json

        import boto3

        # Setup test data
        aws_account_id = "123456789012"
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        created_scan_target_id = "14f79567-6b68-4e3a-b2f2-4f1383546251"
        kind = zanshinsdk.ScanTargetKind.AWS
        name = "OnboardTesting-it"
        credential = zanshinsdk.ScanTargetAWS(aws_account_id)
        schedule = zanshinsdk.DAILY
        region = "us-east-1"

        boto3_session = boto3.Session(
            aws_access_key_id="EXAMPLE_NON_EXISTING_KEY",
            aws_secret_access_key="&x@mP|e$3cReT",
            aws_session_token="session_token",
        )

        # Mock request to create new Scan Target
        mock_is_file.return_value = True
        _data = "[default]\napi_key=api_key"

        with patch("__main__.__builtins__.open", mock_open(read_data=_data)):
            request.return_value = Mock(
                status_code=200, json=lambda: {"id": created_scan_target_id}
            )
            client = zanshinsdk.Client()
            client._client.request = request

        # Create Mocked S3 tenchi-assets bucket
        with open(
            "zanshinsdk/tests/data/dummy_cloudformation_zanshin_service_role_template.json",
            "r",
        ) as dummy_template_file:
            DUMMY_TEMPLATE = json.load(dummy_template_file)
            s3 = boto3.client("s3", region_name="us-east-2")
            s3.create_bucket(
                Bucket="tenchi-assets",
                CreateBucketConfiguration={"LocationConstraint": "us-east-2"},
            )
            s3.put_object(
                Bucket="tenchi-assets",
                Key="zanshin-service-role.template",
                Body=json.dumps(DUMMY_TEMPLATE),
            )

        # Call method onboard_scan_target with boto3_session instead of boto3_profile
        new_scan_target = client.onboard_scan_target(
            region,
            organization_id,
            kind,
            name,
            credential,
            boto3_session,
            None,
            schedule,
        )

        # Assert that Scan Target was created
        self.assertEqual(created_scan_target_id, new_scan_target["id"])

        # Assert that Scan Target was called with correct parameters
        client._client.request.assert_any_call(
            "POST",
            f"/organizations/{organization_id}/scantargets",
            body={
                "name": name,
                "kind": kind,
                "schedule": {"frequency": "1d", "timeOfDay": "NIGHT"},
                "credential": {"account": aws_account_id},
            },
        )
        # Assert that we checked Scan Target to start scan
        client._client.request.assert_any_call(
            "POST",
            f"/organizations/{organization_id}/scantargets/{created_scan_target_id}/check",
        )

        # Assert CloudFormation Stack was created successfully
        zanshin_cloudformation_stack_name = "tenchi-zanshin-service-role"
        cloudformation = boto3.client("cloudformation", region_name="us-east-1")
        zanshin_stack = cloudformation.describe_stacks(
            StackName=zanshin_cloudformation_stack_name
        )["Stacks"][0]
        self.assertEqual("CREATE_COMPLETE", zanshin_stack["StackStatus"])
        self.assertEqual(zanshin_cloudformation_stack_name, zanshin_stack["StackName"])

        # Clean Up CloudFormation
        cf_stacks = cloudformation.describe_stacks(
            StackName=zanshin_cloudformation_stack_name
        )
        for cf_stack in cf_stacks["Stacks"]:
            cloudformation.delete_stack(StackName=cf_stack["StackName"])

    def test_get_alert_comment_page(self):
        alert_id = "e22f4225-43e9-4922-b6b8-8b0620bdb110"
        page = 1
        page_size = 100

        self.sdk._get_alert_comment_page(alert_id, page=page, page_size=page_size)

        self.sdk._request.assert_called_once_with(
            "GET",
            f"/alerts/{alert_id}/comments",
            params={
                "page": page,
                "pageSize": page_size,
            },
        )

    @patch("zanshinsdk.client.Client._get_alert_comment_page")
    def test_iter_alert_comments(self, request):
        alert_id = "e22f4225-43e9-4922-b6b8-8b0620bdb110"
        page_size = 2
        total_comments = 5

        request.side_effect = [
            {"data": ["comment1", "comment2"], "total": total_comments},
            {"data": ["comment3", "comment4"]},
            {"data": ["comment5"]},
        ]

        self.sdk._get_alert_comment_page = request
        iterator = self.sdk.iter_alert_comments(alert_id, page_size=page_size)
        comments = list(iterator)

        self.assertEqual(
            comments, ["comment1", "comment2", "comment3", "comment4", "comment5"]
        )

        expected_calls = [
            call(alert_id=alert_id, page_size=page_size, page=1),
            call(alert_id=alert_id, page_size=page_size, page=2),
            call(alert_id=alert_id, page_size=page_size, page=3),
        ]
        self.sdk._get_alert_comment_page.assert_has_calls(expected_calls)
