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

    def test_iter_organizations(self):
        try:
            next(self.cli.iter_organizations())
        except StopIteration:
            pass

        self.cli._request.assert_called_once_with('GET', '/organizations')


    def test_get_organization(self):
        self.cli.get_organization('b72f4225-43e9-4922-b6b7-8b0620bdb1ca')

        self.cli._request.assert_called_once_with('GET', '/organizations/b72f4225-43e9-4922-b6b7-8b0620bdb1ca')


    def test_update_organization(self):
        self.cli.update_organization(
            'c72f4225-43e1-4922-b6b7-8b0620bdb1c3',
            name='Tabajara', picture='http://pic-store.com/pic1.png', email='ceo@tabajara.com.br')

        self.cli._request.assert_called_once_with(
            'PUT',
            '/organizations/c72f4225-43e1-4922-b6b7-8b0620bdb1c3',
            body={'name': 'Tabajara', 'email': 'ceo@tabajara.com.br', 'picture': 'http://pic-store.com/pic1.png'})

    ###################################################
    # Organization Member
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

    ###################################################
    # Organization Member Invite
    ###################################################

    def test_iter_organization_members_invites(self):
        try:
            next(self.cli.iter_organization_members_invites('c92f4225-43e9-4922-b6b7-8b0620bdb1d3'))
        except:
            StopIteration

        self.cli._request.assert_called_once_with('GET', '/organizations/c92f4225-43e9-4922-b6b7-8b0620bdb1d3/invites')

    def test_create_organization_members_invite(self):
        self.cli.create_organization_members_invite(
            'c92f4225-43e9-4922-b6b7-8b0620bdb1d3', 'johndoe@example.com', ['ADMIN'])

        self.cli._request.assert_called_once_with(
            'POST',
            '/organizations/c92f4225-43e9-4922-b6b7-8b0620bdb1d3/invites',
            body={ 'email': 'johndoe@example.com', 'roles': ['ADMIN']})

    def test_get_organization_member_invite(self):
        self.cli.get_organization_member_invite('d12f4225-43e9-4922-b6b8-8b0620bdb1f5', 'joe@example.com')

        self.cli._request.assert_called_once_with(
            'GET', '/organizations/d12f4225-43e9-4922-b6b8-8b0620bdb1f5/invites/joe@example.com')

    def test_delete_organization_member_invite(self):
        self.cli.delete_organization_member_invite('e22f4225-43e9-4922-b6b8-8b0620bdb110', 'john@example.com')

        self.cli._request.assert_called_once_with(
            'DELETE', '/organizations/e22f4225-43e9-4922-b6b8-8b0620bdb110/invites/john@example.com')

    def test_resend_organization_member_invite(self):
        self.cli.resend_organization_member_invite('822f4225-43e9-4922-b6b8-8b0620bdb1e3', 'juca@example.com')

        self.cli._request.assert_called_once_with(
            'POST', '/organizations/822f4225-43e9-4922-b6b8-8b0620bdb1e3/invites/juca@example.com/resend')
