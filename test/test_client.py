import unittest
from unittest.mock import mock_open, patch
from uuid import UUID

from httpx import Request, Response

import zanshinsdk
from src.bin import client
from src.bin.client import (
    CONFIG_FILE,
    Client,
    Roles,
    ScanTargetSchedule,
    isfile,
    validate_class,
    validate_int,
    validate_uuid,
)


class TestClient(unittest.TestCase):
    ###################################################
    # setUp
    ###################################################

    @patch("isfile")
    @patch("Client._request")
    def setUp(self, request, mock_is_file):
        mock_is_file.return_value = True
        _data = "[default]\napi_key=api_key"

        with patch("__main__.__builtins__.open", mock_open(read_data=_data)):
            self.sdk = Client()
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

    @patch("isfile")
    def test_init_empty_profile(self, mock_is_file):
        mock_is_file.return_value = True
        _data = "[default]\napi_key=api_key"

        try:
            with patch("__main__.__builtins__.open", mock_open(read_data=_data)):
                Client(profile="")
        except Exception as e:
            self.assertIn("profile  not found", str(e))

    @patch("isfile")
    def test_init_wrong_profile(self, mock_is_file):
        mock_is_file.return_value = True
        _profile = "XYZ"
        _data = "[default]\napi_key=api_key"

        try:
            with patch("__main__.__builtins__.open", mock_open(read_data=_data)):
                Client(profile=_profile)
        except Exception as e:
            self.assertEqual(
                str(e),
                f"profile {_profile} not found in {CONFIG_FILE}",
            )

    @patch("isfile")
    def test_init_api_url(self, mock_is_file):
        mock_is_file.return_value = True
        _api_url = "https://api.test"
        _data = "[default]\napi_key=api_key"

        with patch("__main__.__builtins__.open", mock_open(read_data=_data)):
            client = Client(api_url=_api_url)

        self.assertEqual(client._api_url, _api_url)

    @patch("isfile")
    def test_init_invalid_api_url(self, mock_is_file):
        mock_is_file.return_value = True
        _api_url = "invalid://api.test"
        _data = "[default]\napi_key=api_key"

        try:
            with patch("__main__.__builtins__.open", mock_open(read_data=_data)):
                Client(api_url=_api_url)
        except Exception as e:
            self.assertEqual(str(e), f"Invalid API URL: {_api_url}")

    @patch("isfile")
    def test_init_api_url_from_config(self, mock_is_file):
        mock_is_file.return_value = True
        _api_url = "https://api.test"
        _data = f"[default]\napi_key=api_key\napi_url={_api_url}"

        with patch("__main__.__builtins__.open", mock_open(read_data=_data)):
            client = Client()

        self.assertEqual(client._api_url, _api_url)

    @patch("isfile")
    def test_init_proxy_url(self, mock_is_file):
        mock_is_file.return_value = True
        _proxy_url = "https://proxy.test"
        _data = "[default]\napi_key=api_key"

        with patch("__main__.__builtins__.open", mock_open(read_data=_data)):
            client = Client(proxy_url=_proxy_url)

        self.assertEqual(client._proxy_url, _proxy_url)

    @patch("isfile")
    def test_init_invalid_proxy_url(self, mock_is_file):
        mock_is_file.return_value = True
        _proxy_url = "invalid://proxy.api.test"
        _data = "[default]\napi_key=api_key"

        try:
            with patch("__main__.__builtins__.open", mock_open(read_data=_data)):
                Client(proxy_url=_proxy_url)
        except Exception as e:
            self.assertEqual(str(e), f"Invalid proxy URL: {_proxy_url}")

    @patch("isfile")
    def test_init_proxy_url_from_config(self, mock_is_file):
        mock_is_file.return_value = True
        _proxy_url = "https://proxy.test"
        _data = f"[default]\napi_key=api_key\nproxy_url={_proxy_url}"

        with patch("__main__.__builtins__.open", mock_open(read_data=_data)):
            client = Client()

        self.assertEqual(client._proxy_url, _proxy_url)

    @patch("isfile")
    def test_init_user_agent(self, mock_is_file):
        mock_is_file.return_value = True
        _user_agent = "test_agent"
        _data = "[default]\napi_key=api_key"

        with patch("__main__.__builtins__.open", mock_open(read_data=_data)):
            client = Client(user_agent=_user_agent)

        self.assertEqual(
            client._user_agent,
            f"{_user_agent} (Zanshin Python SDK v{zanshinsdk.version.__version__})",
        )

    @patch("isfile")
    def test_init_user_agent_from_config(self, mock_is_file):
        mock_is_file.return_value = True
        _user_agent = "test_agent"
        _data = f"[default]\napi_key=api_key\nuser_agent={_user_agent}"

        with patch("__main__.__builtins__.open", mock_open(read_data=_data)):
            client = Client()

        self.assertEqual(
            client._user_agent,
            f"{_user_agent} (Zanshin Python SDK v{zanshinsdk.version.__version__})",
        )

    ###################################################
    # _update_client except
    ###################################################

    @patch("isfile")
    def test_update_client_except(self, mock_is_file):
        mock_is_file.return_value = True
        _data = "[default]\napi_key=api_key"

        with patch("__main__.__builtins__.open", mock_open(read_data=_data)):
            client = Client()

        client._client = None
        client._update_client()

        self.assertIsNotNone(client._client)

    ###################################################
    # Properties
    ###################################################

    @patch("isfile")
    def test_get_api_url(self, mock_is_file):
        mock_is_file.return_value = True
        _api_url = "https://api.test"
        _data = "[default]\napi_key=api_key"

        with patch("__main__.__builtins__.open", mock_open(read_data=_data)):
            client = Client(api_url=_api_url)

        self.assertEqual(client.api_url, _api_url)

    @patch("isfile")
    def test_set_api_url(self, mock_is_file):
        mock_is_file.return_value = True
        _api_url = "https://api.test"
        _new_api_url = "https://new.api.test"
        _data = "[default]\napi_key=api_key"

        with patch("__main__.__builtins__.open", mock_open(read_data=_data)):
            client = Client(api_url=_api_url)

        client.api_url = _new_api_url

        self.assertEqual(client.api_url, _new_api_url)

    @patch("isfile")
    def test_set_invalid_api_url(self, mock_is_file):
        mock_is_file.return_value = True
        _api_url = "https://api.test"
        _new_api_url = "invalid://new.api.test"
        _data = "[default]\napi_key=api_key"

        try:
            with patch("__main__.__builtins__.open", mock_open(read_data=_data)):
                client = Client(api_url=_api_url)

            client.api_url = _new_api_url
        except Exception as e:
            self.assertEqual(str(e), f"Invalid API URL: {_new_api_url}")

    @patch("isfile")
    def test_set_none_api_url(self, mock_is_file):
        mock_is_file.return_value = True
        _api_key = "https://api.test"
        _data = "[default]\napi_key=api_key"

        try:
            with patch("__main__.__builtins__.open", mock_open(read_data=_data)):
                client = Client(api_url=_api_key)

            client.api_url = None
        except Exception as e:
            self.assertEqual(str(e), f"API URL cannot be null")

    @patch("isfile")
    def test_get_api_key(self, mock_is_file):
        mock_is_file.return_value = True
        _api_key = "api_key"
        _data = "[default]\napi_key=api_key"

        with patch("__main__.__builtins__.open", mock_open(read_data=_data)):
            client = Client(api_key=_api_key)

        self.assertEqual(client.api_key, _api_key)

    @patch("isfile")
    def test_set_api_key(self, mock_is_file):
        mock_is_file.return_value = True
        _api_key = "api_key"
        _new_api_key = "new_api_key"
        _data = "[default]\napi_key=api_key"

        with patch("__main__.__builtins__.open", mock_open(read_data=_data)):
            client = Client(api_key=_api_key)

        client.api_key = _new_api_key

        self.assertEqual(client.api_key, _new_api_key)

    @patch("isfile")
    def test_get_proxy_url(self, mock_is_file):
        mock_is_file.return_value = True
        _proxy_url = "https://proxy.test"
        _data = "[default]\napi_key=api_key"

        with patch("__main__.__builtins__.open", mock_open(read_data=_data)):
            client = Client(proxy_url=_proxy_url)

        self.assertEqual(client.proxy_url, _proxy_url)

    @patch("isfile")
    def test_set_proxy_url(self, mock_is_file):
        mock_is_file.return_value = True
        _proxy_url = "https://proxy.test"
        _new_proxy_url = "https://new.proxy.test"
        _data = "[default]\napi_key=api_key"

        with patch("__main__.__builtins__.open", mock_open(read_data=_data)):
            client = Client(proxy_url=_proxy_url)

        client.proxy_url = _new_proxy_url

        self.assertEqual(client.proxy_url, _new_proxy_url)

    @patch("isfile")
    def test_set_invalid_proxy_url(self, mock_is_file):
        mock_is_file.return_value = True
        _proxy_url = "https://proxy.test"
        _new_proxy_url = "invalid://new.proxy.test"
        _data = "[default]\napi_key=api_key"

        try:
            with patch("__main__.__builtins__.open", mock_open(read_data=_data)):
                client = Client(proxy_url=_proxy_url)

            client.proxy_url = _new_proxy_url
        except Exception as e:
            self.assertEqual(str(e), f"Invalid proxy URL: {_new_proxy_url}")

    @patch("isfile")
    def test_set_equal_proxy_url(self, mock_is_file):
        mock_is_file.return_value = True
        _proxy_url = "https://proxy.test"
        _data = "[default]\napi_key=api_key"

        with patch("__main__.__builtins__.open", mock_open(read_data=_data)):
            client = Client(proxy_url=_proxy_url)

        client.proxy_url = _proxy_url

        self.assertEqual(client.proxy_url, _proxy_url)

    @patch("isfile")
    def test_set_none_proxy_url(self, mock_is_file):
        mock_is_file.return_value = True
        _proxy_url = "https://proxy.test"
        _data = "[default]\napi_key=api_key"

        with patch("__main__.__builtins__.open", mock_open(read_data=_data)):
            client = Client(proxy_url=_proxy_url)

        client.proxy_url = None

        self.assertIsNone(client.proxy_url)

    @patch("isfile")
    def test_get_user_agent(self, mock_is_file):
        mock_is_file.return_value = True
        _user_agent = "test_agent"
        _data = "[default]\napi_key=api_key"

        with patch("__main__.__builtins__.open", mock_open(read_data=_data)):
            client = Client(user_agent=_user_agent)

        self.assertEqual(
            client.user_agent,
            f"{_user_agent} (Zanshin Python SDK v{zanshinsdk.version.__version__})",
        )

    @patch("isfile")
    def test_set_user_agent(self, mock_is_file):
        mock_is_file.return_value = True
        _user_agent = "test_agent"
        _new_user_agent = "new_test_agent"
        _data = "[default]\napi_key=api_key"

        with patch("__main__.__builtins__.open", mock_open(read_data=_data)):
            client = Client(user_agent=_user_agent)

        client.user_agent = _new_user_agent

        self.assertEqual(
            client.user_agent,
            f"{_new_user_agent} (Zanshin Python SDK v{zanshinsdk.version.__version__})",
        )

    @patch("isfile")
    def test_get_sanitized_proxy_url_none(self, mock_is_file):
        mock_is_file.return_value = True
        _data = "[default]\napi_key=api_key"

        with patch("__main__.__builtins__.open", mock_open(read_data=_data)):
            client = Client()

        self.assertIsNone(client._get_sanitized_proxy_url())

    @patch("isfile")
    def test_get_sanitized_proxy_url(self, mock_is_file):
        mock_is_file.return_value = True
        _proxy_url = "https://username:password@proxy.test:8000"
        _data = "[default]\napi_key=api_key"

        with patch("__main__.__builtins__.open", mock_open(read_data=_data)):
            client = Client(proxy_url=_proxy_url)

        self.assertIsNotNone(client._get_sanitized_proxy_url())

    ###################################################
    # Request
    ###################################################

    @patch("isfile")
    @patch("client.httpx.Client.request")
    def test_request(self, request, mock_is_file):
        mock_is_file.return_value = True
        _api_url = "https://api.test"
        _data = "[default]\napi_key=api_key"

        with patch("__main__.__builtins__.open", mock_open(read_data=_data)):
            client = Client(api_url=_api_url)

        req = Request(method="GET", url=f"{_api_url}/path", content="{}")
        value = Response(request=req, status_code=200)
        request.return_value = value
        client._client.request = request
        client._request("GET", "/path")

        client._client.request.assert_called_once_with(
            method="GET", url=f"{_api_url}/path", params=None, json=None
        )

    @patch("isfile")
    @patch("client.httpx.Client.request")
    def test_request_without_content(self, request, mock_is_file):
        mock_is_file.return_value = True
        _api_url = "https://api.test"
        _data = "[default]\napi_key=api_key"

        with patch("__main__.__builtins__.open", mock_open(read_data=_data)):
            client = Client(api_url=_api_url)

        req = Request(method="GET", url=f"{_api_url}/path")
        value = Response(request=req, status_code=200)
        request.return_value = value
        client._client.request = request
        client._request("GET", "/path")

        client._client.request.assert_called_once_with(
            method="GET", url=f"{_api_url}/path", params=None, json=None
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
        role = [Roles.ADMIN]

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
        self.assertIsNone(validate_int(_int))

    def test_validate_int_none_required(self):
        _int = None
        try:
            validate_int(_int, required=True)
        except Exception as e:
            self.assertEqual(str(e), f"required integer parameter missing")

    def test_validate_int_not_int(self):
        _int = "NaN"
        try:
            validate_int(_int)
        except Exception as e:
            self.assertEqual(str(e), f"{repr(_int)} is not an integer")

    def test_validate_int_lower_than(self):
        _int = 9
        _min_value = 10
        try:
            validate_int(_int, min_value=_min_value)
        except Exception as e:
            self.assertEqual(str(e), f"{_int} shouldn't be lower than {_min_value}")

    def test_validate_int_higher_than(self):
        _int = 11
        _max_value = 10
        try:
            validate_int(_int, max_value=_max_value)
        except Exception as e:
            self.assertEqual(str(e), f"{_int} shouldn't be higher than {_max_value}")

    def test_validate_class(self):
        _invalid_class = "invalid"
        try:
            validate_class(_invalid_class, UUID)
        except Exception as e:
            self.assertEqual(
                str(e), f"{repr(_invalid_class)} is not an instance of {UUID.__name__}"
            )

    def test_validate_uuid(self):
        _uuid = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        _response = validate_uuid(UUID(_uuid))
        self.assertEqual(_uuid, _response)

    def test_validate_uuid_invalid(self):
        _uuid = "invalid_uuid"
        try:
            validate_uuid(_uuid)
        except Exception as e:
            self.assertEqual(str(e), f"{repr(_uuid)} is not a valid UUID")

    def test_validate_uuid_input(self):
        with self.assertRaises(TypeError):
            validate_uuid(1)
        with self.assertRaises(TypeError):
            validate_uuid(None)
        with self.assertRaises(ValueError):
            validate_uuid("foo")
        with self.assertRaises(ValueError):
            validate_uuid("")


class TestScanTargetSchedule(unittest.TestCase):
    def test_from_value(self):
        """
        Tests the initialization of a new scan target schedule instance using the new enum class, its string equivalent
        and the old cron-style strings.
        """
        for k, v in ScanTargetSchedule.__members__.items():
            self.assertEqual(ScanTargetSchedule.from_value(v.value), v)
            self.assertEqual(ScanTargetSchedule.from_value(v), v)

        self.assertEqual(
            ScanTargetSchedule.from_value("0 * * * *"),
            ScanTargetSchedule.ONE_HOUR,
        )
        self.assertEqual(
            ScanTargetSchedule.from_value("0 */6 * * *"),
            ScanTargetSchedule.SIX_HOURS,
        )
        self.assertEqual(
            ScanTargetSchedule.from_value("0 */12 * * *"),
            ScanTargetSchedule.TWELVE_HOURS,
        )
        self.assertEqual(
            ScanTargetSchedule.from_value("0 0 * * *"),
            ScanTargetSchedule.TWENTY_FOUR_HOURS,
        )
        self.assertEqual(
            ScanTargetSchedule.from_value("0 0 * * 0"),
            ScanTargetSchedule.SEVEN_DAYS,
        )

        self.assertRaises(TypeError, ScanTargetSchedule.from_value, 1)
        self.assertRaises(TypeError, ScanTargetSchedule.from_value, 1.0)
        self.assertRaises(ValueError, ScanTargetSchedule.from_value, "foo")
        self.assertRaises(ValueError, ScanTargetSchedule.from_value, "0 */8 * * *")
