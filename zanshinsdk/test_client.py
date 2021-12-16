from unittest.mock import patch

import unittest
import zanshinsdk

class TestClient(unittest.TestCase):
    @patch("zanshinsdk.Client._request")
    def setUp(self, request):
        self.cli = zanshinsdk.Client(profile=None, api_key="abc")
        self.cli._request = request

    ###################################################
    # Account
    ###################################################

    def test_get_me(self):
        self.cli.get_me()

        self.cli._request.assert_called_once_with('GET', '/me')

    ###################################################
    # Account Invites
    ###################################################

    def test_iter_invites(self):
        try:
            next(self.cli.iter_invites())
        except StopIteration:
            pass

        self.cli._request.assert_called_once_with('GET', '/me/invites')

    def test_get_invite(self):
        self.cli.get_invite("a72f4225-43e9-4922-b6b7-8b0620bdb1c0")

        self.cli._request.assert_called_once_with('GET', '/me/invites/a72f4225-43e9-4922-b6b7-8b0620bdb1c0')

    def test_accept_invite(self):
        self.cli.accept_invite("a72f4225-43e9-4922-b6b7-8b0620bdb1c0")

        self.cli._request.assert_called_once_with('POST', '/me/invites/a72f4225-43e9-4922-b6b7-8b0620bdb1c0/accept')

    ###################################################
    # Account API key
    ###################################################

    def test_iter_api_keys(self):
        try:
            next(self.cli.iter_api_keys())
        except StopIteration:
            pass

        self.cli._request.assert_called_once_with('GET', '/me/apikeys')

    def test_create_api_key(self):
        self.cli.create_api_key("my key")

        self.cli._request.assert_called_once_with('POST', '/me/apikeys', body={"name": "my key"})

    def test_delete_api_key(self):
        self.cli.delete_api_key("a72f4225-43e9-4922-b6b7-8b0620bdb1c0")

        self.cli._request.assert_called_once_with('DELETE', '/me/apikeys/a72f4225-43e9-4922-b6b7-8b0620bdb1c0')

    ###################################################
    # Organization
    ###################################################

    def test_iter_organization_members(self):
        try:
            next(self.cli.iter_organization_members("a72f4225-43e9-4922-b6b7-8b0620bdb1c0"))
        except StopIteration:
            pass

        self.cli._request.assert_called_once_with('GET', '/organizations/a72f4225-43e9-4922-b6b7-8b0620bdb1c0/members')

    def test_get_organization_members(self):
        self.cli.get_organization_member('a72f4225-43e9-4922-b6b7-8b0620bdb1c0', 'b72f4225-43e1-1922-b6b7-8b0620bdb1d1')

        self.cli._request.assert_called_once_with('GET', '/organizations/a72f4225-43e9-4922-b6b7-8b0620bdb1c0/members/b72f4225-43e1-1922-b6b7-8b0620bdb1d1')

    def test_update_organization_members(self):
        #TODO(edpin): figure out why importing Roles is not working.
        self.cli.update_organization_member(
            'a72f4225-43e9-4922-b6b7-8b0620bdb1c0',
            'b72f4225-43e1-1922-b6b7-8b0620bdb1d1',
            ['ADMIN'])

        self.cli._request.assert_called_once_with(
            'PUT',
            '/organizations/a72f4225-43e9-4922-b6b7-8b0620bdb1c0/members/b72f4225-43e1-1922-b6b7-8b0620bdb1d1',
            body = {"roles": ['ADMIN']})

    def test_delete_organization_members(self):
        self.cli.delete_organization_member(
            'a72f4225-43e9-4922-b6b7-8b0620bdb1c0',
            'b72f4225-43e1-1922-b6b7-8b0620bdb1d1')

        self.cli._request.assert_called_once_with(
            'DELETE',
            '/organizations/a72f4225-43e9-4922-b6b7-8b0620bdb1c0/members/b72f4225-43e1-1922-b6b7-8b0620bdb1d1')
