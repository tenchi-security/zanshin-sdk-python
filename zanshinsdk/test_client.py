from unittest.mock import patch

import unittest
import zanshinsdk

class TestClient(unittest.TestCase):
    @patch("zanshinsdk.Client._request")
    def test_get_me(self, _):
        cli = zanshinsdk.Client()
        cli.get_me()

        cli._request.assert_called_once_with('GET', '/me')

    @patch("zanshinsdk.Client._request")
    def test_iter_invites(self, _):
        cli = zanshinsdk.Client()

        try:
            next(cli.iter_invites())
        except StopIteration:
            pass

        cli._request.assert_called_once_with('GET', '/me/invites')

    @patch("zanshinsdk.Client._request")
    def test_get_invite(self, _):
        cli = zanshinsdk.Client()
        cli.get_invite("a72f4225-43e9-4922-b6b7-8b0620bdb1c0")

        cli._request.assert_called_once_with('GET', '/me/invites/a72f4225-43e9-4922-b6b7-8b0620bdb1c0')

    @patch("zanshinsdk.Client._request")
    def test_accept_invite(self, _):
        cli = zanshinsdk.Client()
        cli.accept_invite("a72f4225-43e9-4922-b6b7-8b0620bdb1c0")

        cli._request.assert_called_once_with('POST', '/me/invites/a72f4225-43e9-4922-b6b7-8b0620bdb1c0/accept')


    @patch("zanshinsdk.Client._request")
    def test_iter_api_keys(self, _):
        cli = zanshinsdk.Client()

        try:
            next(cli.iter_api_keys())
        except StopIteration:
            pass

        cli._request.assert_called_once_with('GET', '/me/apikeys')

    @patch("zanshinsdk.Client._request")
    def test_create_api_key(self, _):
        cli = zanshinsdk.Client()
        cli.create_api_key("my key")

        cli._request.assert_called_once_with('POST', '/me/apikeys', body={"name": "my key"})


    @patch("zanshinsdk.Client._request")
    def test_delete_api_key(self, _):
        cli = zanshinsdk.Client()
        cli.delete_api_key("a72f4225-43e9-4922-b6b7-8b0620bdb1c0")

        cli._request.assert_called_once_with('DELETE', '/me/apikeys/a72f4225-43e9-4922-b6b7-8b0620bdb1c0')

    @patch("zanshinsdk.Client._request")
    def test_iter_organization_members(self, _):
        cli = zanshinsdk.Client()

        try:
            next(cli.iter_organization_members("a72f4225-43e9-4922-b6b7-8b0620bdb1c0"))
        except StopIteration:
            pass

        cli._request.assert_called_once_with('GET', '/organizations/a72f4225-43e9-4922-b6b7-8b0620bdb1c0/members')

    @patch("zanshinsdk.Client._request")
    def test_get_organization_members(self, _):
        cli = zanshinsdk.Client()
        cli.get_organization_member('a72f4225-43e9-4922-b6b7-8b0620bdb1c0', 'b72f4225-43e1-1922-b6b7-8b0620bdb1d1')

        cli._request.assert_called_once_with('GET', '/organizations/a72f4225-43e9-4922-b6b7-8b0620bdb1c0/members/b72f4225-43e1-1922-b6b7-8b0620bdb1d1')

    @patch("zanshinsdk.Client._request")
    def test_update_organization_members(self, _):
        cli = zanshinsdk.Client()

        #TODO(edpin): figure out why importing Roles is not working.
        cli.update_organization_member(
            'a72f4225-43e9-4922-b6b7-8b0620bdb1c0',
            'b72f4225-43e1-1922-b6b7-8b0620bdb1d1',
            ['ADMIN'])

        cli._request.assert_called_once_with(
            'PUT',
            '/organizations/a72f4225-43e9-4922-b6b7-8b0620bdb1c0/members/b72f4225-43e1-1922-b6b7-8b0620bdb1d1',
            body = {"roles": ['ADMIN']})

    @patch("zanshinsdk.Client._request")
    def test_delete_organization_members(self, _):
        cli = zanshinsdk.Client()
        cli.delete_organization_member(
            'a72f4225-43e9-4922-b6b7-8b0620bdb1c0',
            'b72f4225-43e1-1922-b6b7-8b0620bdb1d1')

        cli._request.assert_called_once_with(
            'DELETE',
            '/organizations/a72f4225-43e9-4922-b6b7-8b0620bdb1c0/members/b72f4225-43e1-1922-b6b7-8b0620bdb1d1')
