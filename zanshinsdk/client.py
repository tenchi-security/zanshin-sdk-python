import logging
from configparser import RawConfigParser
from enum import Enum
from math import ceil
from pathlib import Path
from typing import Dict, Optional, Iterator, Iterable, Union
from urllib.parse import urlparse
from uuid import UUID

import httpx

from zanshinsdk import __version__ as sdk_version

# Default values used for the configuration
_CONFIG_DIR = Path.home() / '.tenchi'
_CONFIG_FILE = _CONFIG_DIR / "config"


class AlertState(str, Enum):
    OPEN = 'OPEN'
    ACTIVE = 'ACTIVE'
    IN_PROGRESS = 'IN_PROGRESS'
    RISK_ACCEPTED = 'RISK_ACCEPTED'
    SOLVED = 'SOLVED'
    CLOSED = 'CLOSED'


class AlertSeverity(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"


class ScanTargetKind(str, Enum):
    AWS = "AWS"
    GCP = "GCP"
    AZURE = "AZURE"

class Roles(str, Enum):
    ADMIN = "ADMIN"

class Languages(str, Enum):
    PTBR = "pt-BR"
    ENUS = "en-US"

class Client:
    def __init__(self, profile: str = 'default', api_key: Optional[str] = None, api_url: Optional[str] = None,
                 user_agent: Optional[str] = None, proxy_url: Optional[str] = None):
        """
        Initialize a new connection to the Zanshin API.
        :param profile: which configuration file section to use for settings, or None to ignore configuration file
        :param api_key: optional override of the API key to use
        :param api_url: optional override of the base URL of the Zanshin API to use
        :param user_agent: optional override of the user agent to use in requests performed
        :param proxy_url: optional URL indicating which proxy server to use, or None for direct connections to the API
        """
        self._logger: logging.Logger = logging.getLogger('zanshinsdk')

        # read configuration file
        if profile and _CONFIG_FILE.is_file():
            parser = RawConfigParser()
            parser.read(str(_CONFIG_FILE))
            if not parser.has_section(profile):
                raise ValueError(
                    f'profile {profile} not found in {_CONFIG_FILE}')
        else:
            parser = None

        # set API key
        if api_key:
            self._api_key = api_key
        elif parser and parser.get(profile, 'api_key', fallback=None):
            self._api_key = parser.get(profile, 'api_key')
        else:
            raise ValueError('no API key found')

        # set API URL
        if api_url:
            self._api_url = api_url
        elif parser and parser.get(profile, 'api_url', fallback=None):
            self._api_url = parser.get(profile, 'api_url')
        else:
            self._api_url = 'https://api.zanshin.tenchisecurity.com'

        # set proxy URL
        if proxy_url:
            self._proxy_url = proxy_url
        elif parser and parser.get(profile, 'proxy_url', fallback=None):
            self._proxy_url = parser.get(profile, 'proxy_url')
        else:
            self._proxy_url = None

        # set user-agent
        if user_agent:
            self._user_agent = user_agent
        elif parser and parser.get(profile, 'user_agent', fallback=None):
            self._user_agent = parser.get(profile, 'user_agent')
        else:
            self._user_agent = f'Zanshin Python SDK v{sdk_version}'

        self._update_client()

    def _update_client(self):
        """
        Internal method to create a new pre-configured httpx Client instance when one of the relevant settings
        is changed (API key, proxy URL or user-agent).
        """
        try:
            self._client.close()
        except AttributeError:
            pass
        finally:
            self._client = httpx.Client(proxies=self._proxy_url, timeout=60,
                                        headers={"Authorization": f'Bearer {self._api_key}',
                                                 "Accept-Encoding": "gzip, deflate",
                                                 "User-Agent": self.user_agent,
                                                 "Accept": "application/json"})

    @property
    def api_url(self) -> str:
        return self._api_url

    @api_url.setter
    def api_url(self, new_api_url: str) -> None:
        parsed = urlparse(new_api_url)
        if not parsed.scheme or parsed.scheme not in (
                'http', 'https') or not parsed.hostname or parsed.password or parsed.username or (
                parsed.port and (parsed.port <= 0 or parsed.port > 65535)):
            raise ValueError(f'Invalid API URL: {self.api_url}')
        self._api_url: str = new_api_url.rstrip('/')

    @property
    def api_key(self) -> str:
        return self._api_key

    @api_key.setter
    def api_key(self, new_api_key: str) -> None:
        self._api_key = new_api_key
        self._update_client()

    @property
    def proxy_url(self) -> str:
        return self._proxy_url

    @proxy_url.setter
    def proxy_url(self, new_proxy_url: Optional[str]) -> None:
        if new_proxy_url and new_proxy_url != self._proxy_url:
            self._proxy_url: Optional[str] = new_proxy_url
            parsed = urlparse(self._proxy_url)
            if parsed.scheme not in ('http', 'https') or not parsed.hostname or (
                    parsed.password and not parsed.username) or (
                    parsed.port and (parsed.port <= 0 or parsed.port > 65535)):
                raise ValueError(f'Invalid proxy URL: {self._proxy_url}')
        else:
            self._proxy_url: Optional[str] = None
        self._update_client()

    @property
    def user_agent(self) -> str:
        return self._user_agent

    @user_agent.setter
    def user_agent(self, new_user_agent: str) -> None:
        self._user_agent = new_user_agent
        self._update_client()

    def _get_sanitized_proxy_url(self) -> Optional[str]:
        """
        Returns a sanitized proxy URL that doesn't expose a password, if one is present.
        :return:
        """
        if self.proxy_url:
            url = urlparse(self.proxy_url)
            proxy_url = f'{url.scheme}://'
            if url.username:
                proxy_url += url.username
                if url.password:
                    proxy_url += ':***'
                proxy_url += '@'
            proxy_url += url.hostname
            if url.port:
                proxy_url += f':{url.port}'
            return proxy_url
        else:
            return None

    def _request(self, method: str, path: str, params=None, body=None) -> httpx.Response:
        """
        Internal method to simplify calling requests.
        :param method: HTTP method to pass along to httpx.Client.request
        :param path: API path to access
        :param params: parameters to pass along to httpx.Client.request
        :param body: request body to pass along to httpx.Client.request
        :return: the requests.Response object returned by httpx.Client.request
        """
        response = self._client.request(
            method=method, url=self.api_url + path, params=params, json=body)
        if response.request.content:
            self._logger.debug('%s %s (%d bytes in request body) status code %d', response.request.method,
                               response.request.url,
                               len(response.request.content), response.status_code)
        else:
            self._logger.debug('%s %s status code %d', response.request.method, response.request.url,
                               response.status_code)
        response.raise_for_status()
        return response

    ###################################################
    # Account
    ###################################################

    def get_me(self) -> Dict:
        """
        Returns the details of the user account that owns the API key used by this Connection instance as per.
        <https://api.zanshin.tenchisecurity.com/#operation/getMe>
        :return: a dict representing the user
        """
        return self._request("GET", "/me").json()
    
    ###################################################
    # Account Invites
    ###################################################

    def iter_invites(self) -> Iterator[Dict]:
        """
        Iterates over the invites of current logged user.
        <https://api.zanshin.tenchisecurity.com/#operation/getInvites>
        :return: an iterator over the invites objects
        """
        yield from self._request("GET", "/me/invites").json()

    def get_invite(self, invite_id: Union[UUID, str]) -> Dict:
        """
        Gets an specific invitation details, it only works if the invitation was made for the current logged user.
        <https://api.zanshin.tenchisecurity.com/#operation/getInviteById>
        :param invite_id: the ID of the invite
        :return: a dict representing the user invite
        """
        return self._request("GET", f"/me/invites/{validate_uuid(invite_id)}").json()

    def accept_invite(self, invite_id: Union[UUID, str]) -> Dict:
        """
        Accepts an inivitation with the informed ID, it only works if the user accepting the invitation is the user that received the invitation.
        <https://api.zanshin.tenchisecurity.com/#operation/acceptInviteById>
        :param invite_id: the ID of the invite
        :return: a dict representing the organization of this invite
        """
        return self._request("POST", f"/me/invites/{validate_uuid(invite_id)}/accept").json()

    ###################################################
    # Account API key
    ###################################################

    def iter_api_keys(self) -> Iterator[Dict]:
        """
        Iterates over the API keys of current logged user.
        <https://api.zanshin.tenchisecurity.com/#operation/getMyApiKeys>
        :return: an iterator over the api keys objects
        """
        yield from self._request("GET", "/me/apikeys").json()

    def create_api_key(self, name: Optional[str]) -> Dict:
        """
        Creates a new API key for the current logged user, API Keys can be used to interact with the zanshin api directly on behalf of that user.
        <https://api.zanshin.tenchisecurity.com/#operation/createApiKeys>
        :param name: the Name of your new API key
        :return: a dict representing the user api key
        """
        body = {
            "name": name
        }
        return self._request("POST", "/me/apikeys", body=body).json()

    def delete_api_key(self, api_key_id: Union[UUID, str]) -> bool:
        """
        Deletes a given API key by its id, it will only work if the informed ID belongs to the current logged user.
        <https://api.zanshin.tenchisecurity.com/#operation/deleteApiKey>
        :param api_key_id: the ID of the API key
        :return: a boolean if success
        """
        return self._request("DELETE", f"/me/apikeys/{validate_uuid(api_key_id)}").json()

    ###################################################
    # Organization
    ###################################################

    def iter_organizations(self) -> Iterator[Dict]:
        """
        Iterates over organizations of current logged user.
        <https://api.zanshin.tenchisecurity.com/#operation/getOrganizations>
        :return: an iterator over the organizations objects
        """
        yield from self._request("GET", "/organizations").json()

    def get_organization(self, organization_id: Union[UUID, str]) -> Dict:
        """
        Gets an organization given its ID.
        <https://api.zanshin.tenchisecurity.com/#operation/getOrganizationById>
        :param organization_id: the ID of the organization
        :return: a dict representing the organization detail
        """
        return self._request("GET", f"/organizations/{validate_uuid(organization_id)}").json()

    def update_organization(self, organization_id: Union[UUID, str], name: Optional[str], picture: Optional[str], email: Optional[str]) -> Dict:
        """
        Update organization given its ID.
        <https://api.zanshin.tenchisecurity.com/#operation/editOrganizationById>
        :param organization_id: the ID of the organization
        :param name: the Name of the oranization
        :param picture: the picture URL of the organization, accepted formats: jpg, jpeg, png, svg
        :param email: the e-mail contact of the organization
        :return: a dict representing the organization object
        """
        body = {
            "name": name,
            "picture": picture,
            "email": email
        }
        return self._request("PUT", f"/organizations/{validate_uuid(organization_id)}", body=body).json()

    ###################################################
    # Organization Member
    ###################################################

    def iter_organization_members(self, organization_id: Union[UUID, str]) -> Iterator[Dict]:
        """
        Iterates over the users which are members of an organization.
        <https://api.zanshin.tenchisecurity.com/#operation/getOrganizationMembers>
        :param organization_id: the ID of the organization
        :return: an iterator over the organization members objects
        """
        yield from self._request("GET", f"/organizations/{validate_uuid(organization_id)}/members").json()

    def get_organization_member(self, organization_id: Union[UUID, str], member_id: Union[UUID, str]) -> Dict:
        """
        Get details on a user's organization membership.
        <https://api.zanshin.tenchisecurity.com/#operation/getOrganizationMembers>
        :param organization_id: the ID of the organization
        :param member_id: the ID of the member
        :return: a dict representing the organization member
        """
        return self._request("GET", f"/organizations/{validate_uuid(organization_id)}/members/{validate_uuid(member_id)}").json()

    def update_organization_member(self, organization_id: Union[UUID, str], member_id: Union[UUID, str], roles: Optional[Iterable[Roles]]) -> Dict:
        """
        Update organization member.
        <https://api.zanshin.tenchisecurity.com/#operation/editOrganizationMembersById>
        :param organization_id: the ID of the organization
        :param member_id: the ID of the member
        :param roles: the Role of the member (ADMIN, None)
        :return: a dict representing the organization member
        """
        body = {
            "roles": roles,
        }
        return self._request("PUT", f"/organizations/{validate_uuid(organization_id)}/{validate_uuid(member_id)}", body=body).json()

    def delete_organization_member(self, organization_id: Union[UUID, str], member_id: Union[UUID, str]) -> bool:
        """
        Delete organization member.
        <https://api.zanshin.tenchisecurity.com/#operation/removeOrganizationMemberById>
        :param organization_id: the ID of the organization
        :param member_id: the ID of the member
        :return: a boolean if success
        """
        return self._request("DELETE", f"/organizations/{validate_uuid(organization_id)}/{validate_uuid(member_id)}").json()

    ###################################################
    # Organization Member Invite
    ###################################################

    def iter_organization_members_invites(self, organization_id: Union[UUID, str]) -> Iterator[Dict]:
        """
        Iterates over the members invites of an organization.
        <https://api.zanshin.tenchisecurity.com/#operation/getOrgamizationInvites>
        :param organization_id: the ID of the organization
        :return: an iterator over the organization members invites objects
        """
        yield from self._request("GET", f"/organizations/{validate_uuid(organization_id)}/invites").json()

    def create_organization_members_invite(self, organization_id: Union[UUID, str], email: str, roles: Optional[Iterable[Roles]]) -> Iterator[Dict]:
        """
        Create organization member invite.
        <https://api.zanshin.tenchisecurity.com/#operation/createOrgamizationInvite>
        :param organization_id: the ID of the organization
        :param email: the e-mail of the new member
        :param roles: the Role of the member (ADMIN, None)
        :return: a dict representing the organization member invite
        """
        body = {
            "email": email,
            "roles": roles,
        }
        return self._request("POST", f"/organizations/{validate_uuid(organization_id)}/invites", body=body).json()

    def get_organization_member_invite(self, organization_id: Union[UUID, str], email: str) -> Iterator[Dict]:
        """
        Get organization member invite.
        <https://api.zanshin.tenchisecurity.com/#operation/getOrganizationInviteByEmail>
        :param organization_id: the ID of the organization
        :param email: the e-mail of the invited member
        :return: a dict representing the organization member invite
        """
        return self._request("GET", f"/organizations/{validate_uuid(organization_id)}/invites/{email}").json()

    def delete_organization_member_invite(self, organization_id: Union[UUID, str], email: str) -> bool:
        """
        Delete organization member invite.
        <https://api.zanshin.tenchisecurity.com/#operation/deleteOrganizationInviteByEmail>
        :param organization_id: the ID of the organization
        :param email: the e-mail of the invited member
        :return: a boolean if success
        """
        return self._request("PUT", f"/organizations/{validate_uuid(organization_id)}/invites/{email}").json()

    def resend_organization_member_invite(self, organization_id: Union[UUID, str], email: str) -> Dict:
        """
        Resend organization member invitation.
        <https://api.zanshin.tenchisecurity.com/#operation/resendOrganizationInviteByEmail>
        :param organization_id: the ID of the organization
        :param email: the e-mail of the invited member
        :return: a boolean if success
        """
        return self._request("POST", f"/organizations/{validate_uuid(organization_id)}/invites/{email}/resend").json()

    ###################################################
    # Organization Follower
    ###################################################

    def iter_organization_followers(self, organization_id: Union[UUID, str]) -> Iterator[Dict]:
        """
        Iterates over the followers of an organization.
        <https://api.zanshin.tenchisecurity.com/#operation/getOrganizationFollowers>
        :param organization_id: the ID of the organization
        :return: an iterator over the organization followers objects
        """
        yield from self._request("GET", f"/organizations/{validate_uuid(organization_id)}/followers").json()

    def stop_organization_follower(self, organization_id: Union[UUID, str], follower_id: Union[UUID, str]) -> bool:
        """
        Stops one organization follower of another.
        <https://api.zanshin.tenchisecurity.com/#operation/removeOrganizationFollower>
        :param organization_id: the ID of the organization
        :param follower_id: the ID of the follower
        :return: a boolean if success
        """
        return self._request("DELETE", f"/organizations/{validate_uuid(organization_id)}/followers/{validate_uuid(follower_id)}").json()

    ###################################################
    # Organization Follower Request
    ###################################################

    def iter_organization_follower_requests(self, organization_id: Union[UUID, str]) -> Iterator[Dict]:
        """
        Iterates over the follower requests of an organization.
        <https://api.zanshin.tenchisecurity.com/#operation/getOrganizationFollowRequests>
        :param organization_id: the ID of the organization
        :return: an iterator over the organization follower requests objects
        """
        yield from self._request("GET", f"/organizations/{validate_uuid(organization_id)}/followers/requests").json()

    def create_organization_follower_request(self, organization_id: Union[UUID, str], token: Union[UUID, str]) -> Dict:
        """
        Create organization follower request.
        <https://api.zanshin.tenchisecurity.com/#operation/createOrganizationFollowRequests>
        :param organization_id: the ID of the organization
        :param token: the token of the follower request
        :return: a dict representing the organization follower
        """
        body = {
            "token": validate_uuid(token),
        }
        return self._request("POST", f"/organizations/{validate_uuid(organization_id)}/followers/requests", body=body).json()

    def get_organization_follower_request(self, organization_id: Union[UUID, str], token: Union[UUID, str]) -> Dict:
        """
        Get organization follower request.
        <https://api.zanshin.tenchisecurity.com/#operation/getOrganizationFollowRequestsByToken>
        :param organization_id: the ID of the organization
        :param token: the token of the follower request
        :return: a dict representing the organization follower
        """
        return self._request("GET", f"/organizations/{validate_uuid(organization_id)}/followers/requests/{validate_uuid(token)}").json()

    def delete_organization_follower_request(self, organization_id: Union[UUID, str], follower_id: Union[UUID, str]) -> bool:
        """
        Delete organization follower request.
        <https://api.zanshin.tenchisecurity.com/#operation/deleteOrganizationFollowRequestsbyToken>
        :param organization_id: the ID of the organization
        :param follower_id: the ID of the follower
        :return: a boolean if success
        """
        return self._request("DELETE", f"/organizations/{validate_uuid(organization_id)}/followers/requests/{validate_uuid(follower_id)}").json()

    ###################################################
    # Organization Following
    ###################################################

    def iter_organization_following(self, organization_id: Union[UUID, str]) -> Iterator[Dict]:
        """
        Iterates over the following of an organization.
        <https://api.zanshin.tenchisecurity.com/#operation/getOrganizationFollowing>
        :param organization_id: the ID of the organization whose followed organizations we should list
        :return: an iterator over the JSON decoded followed organizations
        """
        yield from self._request("GET", f"/organizations/{validate_uuid(organization_id)}/following").json()

    def stop_organization_following(self, organization_id: Union[UUID, str], following_id: Union[UUID, str]) -> bool:
        """
        Stops one organization following of another.
        <https://api.zanshin.tenchisecurity.com/#operation/removeOrganizationFollowingById>
        :param organization_id: the follower organization ID
        :param following_id:  the followed organization ID
        :return: a boolean indicating whether the operation was successful
        """
        return self._request("DELETE",
                             f"/organizations/{validate_uuid(organization_id)}/following/{validate_uuid(following_id)}").json()

    ###################################################
    # Organization Following Request
    ###################################################

    def iter_organization_following_requests(self, organization_id: Union[UUID, str]) -> Iterator[Dict]:
        """
        Returns all requests received by an organization to follow another.
        <https://api.zanshin.tenchisecurity.com/#operation/getOrganizationFollowingRequests>
        :param organization_id: the ID of the organization that was invited to follow another
        :return: an iterator over the JSON decoded following requests
        """
        yield from self._request("GET", f"/organizations/{validate_uuid(organization_id)}/following/requests").json()

    def get_organization_following_request(self, organization_id: Union[UUID, str], following_id: Union[UUID, str]) -> Dict:
        """
        Returns a request received by an organization to follow another.
        <https://api.zanshin.tenchisecurity.com/#operation/getOrganizationFollowingRequestByToken>
        :param organization_id: the ID of the organization
        :param following_id: the ID of the following
        :return: a dict representing the following request
        """
        return self._request("GET", f"/organizations/{validate_uuid(organization_id)}/followers/requests/{validate_uuid(following_id)}").json()

    def accept_organization_following_request(self, organization_id: Union[UUID, str], following_id: Union[UUID, str]) -> Dict:
        """
        Accepts a request to follow another organization.
        <https://api.zanshin.tenchisecurity.com/#operation/acceptOrganizationFollowingRequestByToken>
        :param organization_id: the ID of the organization who was invited to follow another
        :param following_id: thet ID of the organization who is going to be followed
        :return: a decoded JSON object describing the newly established following relationship
        """
        return self._request("POST",
                             f"/organizations/{validate_uuid(organization_id)}/following/requests/{validate_uuid(following_id)}/accept").json()

    def decline_organization_following_request(self, organization_id: Union[UUID, str], following_id: Union[UUID, str]) -> Dict:
        """
        Declines a request to follow another organization.
        <https://api.zanshin.tenchisecurity.com/#operation/declineOrganizationFollowingRequestByToken>
        :param organization_id: the ID of the organization who was invited to follow another
        :param following_id: thet ID of the organization who was going to be followed
        :return: a decoded JSON object describing the newly established following relationship
        """
        return self._request("POST",
                             f"/organizations/{validate_uuid(organization_id)}/following/requests/{validate_uuid(following_id)}/accept").json()

    ###################################################
    # Organization Scan Target
    ###################################################

    def iter_organization_scan_targets(self, organization_id: Union[UUID, str]) -> Iterator[Dict]:
        """
        Iterates over the scan targets of an organization.
        <https://api.zanshin.tenchisecurity.com/#operation/getOrganizationScanTargets>
        :param organization_id: the ID of the organization
        : return: an iterator over the scan target objects
        """
        yield from self._request("GET", f"/organizations/{validate_uuid(organization_id)}/scantargets").json()

    def create_organization_scan_target(self, organization_id: Union[UUID, str], kind: ScanTargetKind, name: str,
                           credential: Dict[str, any], schedule: str = "0 0 * * *") -> Dict:
        """
        Create a new scan target in organization.
        <https://api.zanshin.tenchisecurity.com/#operation/createOrganizationScanTargets>
        :param organization_id: the ID of the organization
        :param kind: the Kind of scan target (AWS, GCP, AZURE)
        :param name: the name of the scan target
        :param credential: credentials to access the cloud account to be scanned:
            * For AWS scan targets, provide the account ID in the *account* field
            * For Azure scan targets, provide *applicationId*, *subscriptionId*, *directoryId* and *secret* fields.
            * For GCP scan targets, provide a *projectId* field.
        :param schedule: schedule in cron format
        """
        validate_class(kind, ScanTargetKind)
        validate_class(name, str)
        validate_class(schedule, str)

        validate_class(credential, dict)
        if kind == ScanTargetKind.AWS:
            credential_keys = {'account'}
        elif kind == ScanTargetKind.AZURE:
            credential_keys = {'applicationId',
                               'subscriptionId', 'directoryId', 'secret'}
        elif kind == ScanTargetKind.GCP:
            credential_keys = {'projectId'}
        if set(credential.keys()) != credential_keys:
            raise ValueError(
                f'credential should contain the following field(s): {", ".join(credential_keys)}')
        for k in credential_keys:
            validate_class(credential[k], str)

        body = {
            'name': name,
            'kind': kind,
            'credential': credential
        }
        return self._request('POST', f'/organizations/{validate_uuid(organization_id)}/scantargets',
                             body=body).json()

    def get_organization_scan_target(self, organization_id: Union[UUID, str], scan_target_id: Union[UUID, str]) -> Dict:
        """
        Get scan target of organization.
        <https://api.zanshin.tenchisecurity.com/#operation/getOrganizationScanTargetById>
        :param organization_id: the ID of the organization
        :param token: the token of the follower request
        :return: a dict representing the scan target
        """
        return self._request("GET", f"/organizations/{validate_uuid(organization_id)}/scantargets/{validate_uuid(scan_target_id)}").json()

    def update_organization_scan_target(self, organization_id: Union[UUID, str], scan_target_id: Union[UUID, str], name: str, schedule: str) -> Dict:
        """
        Update scan target of organization.
        <https://api.zanshin.tenchisecurity.com/#operation/editOrganizationScanTargetById>
        :param organization_id: the ID of the organization
        :param token: the token of the follower request
        :return: a dict representing the organization follower
        """

        body = {
            "name": name,
            "schedule": schedule,
        }

        return self._request("PUT", f"/organizations/{validate_uuid(organization_id)}/scantargets/{validate_uuid(scan_target_id)}", body=body).json()

    def delete_organization_scan_target(self, organization_id: Union[UUID, str], scan_target_id: Union[UUID, str]) -> bool:
        """
        Delete scan target of organization.
        <https://api.zanshin.tenchisecurity.com/#operation/deleteOrganizationScanTargetById>
        :param organization_id: the ID of the organization
        :param token: the token of the follower request
        :return: a boolean if success
        """
        return self._request("DELETE", f"/organizations/{validate_uuid(organization_id)}/scantargets/{validate_uuid(scan_target_id)}").json()

    def start_organization_scan_target_scan(self, organization_id: Union[UUID, str], scan_target_id: Union[UUID, str]) -> bool:
        """
        Starts a scan on the specified scan target.
        <https://api.zanshin.tenchisecurity.com/#operation/scanOrganizationScanTarget>
        :param organization_id: the ID of organization the scan target belongs to
        :param scan_target_id: the ID of the scan target
        :return: a boolean if success
        """
        return self._request("POST",
                             f"/organizations/{validate_uuid(organization_id)}/scantargets/{validate_uuid(scan_target_id)}/scan").json()

    def check_organization_scan_target(self, organization_id: Union[UUID, str], scan_target_id: Union[UUID, str]) -> Dict:
        """
        Check scan target.
        <https://api.zanshin.tenchisecurity.com/#operation/checkOrganizationScanTarget>
        :param organization_id: the ID of organization the scan target belongs to
        :param scan_target_id: the ID of the scan target
        :return: a dict representing the scan target
        """
        return self._request("POST",
                             f"/organizations/{validate_uuid(organization_id)}/scantargets/{validate_uuid(scan_target_id)}/check").json()

    ###################################################
    # Organization Scan Target Scan
    ###################################################

    def iter_organization_scan_target_scans(self, organization_id: Union[UUID, str], scan_target_id: Union[UUID, str]) -> Iterator[Dict]:
        """
        Iterates over the scan of an scan target.
        <https://api.zanshin.tenchisecurity.com/#operation/getOrganizationScanTargetScans>
        :param organization_id: the ID of the organization
        :param scan_target_id: the ID of the scan target
        :return: an iterator over the JSON decoded scans
        """
        yield from self._request("GET", f"/organizations/{validate_uuid(organization_id)}/scantargets/{validate_uuid(scan_target_id)}/scans").json()

    def get_organization_scan_target_scan(self, organization_id: Union[UUID, str], scan_target_id: Union[UUID, str], scan_id: Union[UUID, str]) -> Dict:
        """
        Get scan of scan target.
        <https://api.zanshin.tenchisecurity.com/#operation/getOrganizationScanTargetScanSlot>
        :param organization_id: the ID of the organization
        :param scan_target_id: the ID of the scan target
        :param scan_id: the ID of the scan
        :return: a dict representing the scan
        """
        return self._request("GET", f"/organizations/{validate_uuid(organization_id)}/scantargets/{validate_uuid(scan_target_id)}/scans/{scan_id}").json()

    ###################################################
    # Alerts
    ###################################################

    def _get_alerts_page(self, organization_id: Union[UUID, str],
                        scan_target_ids: Optional[Iterable[Union[UUID, str]]] = None,
                        states: Optional[Iterable[AlertState]] = None,
                        severities: Optional[Iterable[AlertSeverity]] = None,
                        page: int = 1,
                        page_size: int = 100,
                        language: Optional[Iterable[Languages]] = None,
                        start_date: Optional[str] = None,
                        historical: Optional[bool] = None) -> Dict:
        """
        Internal method to retrieve a single page of alerts from an organization.
        :param organization_id: the ID of the organization
        :param scan_target_ids: optional list of scan target IDs to list alerts from, defaults to all
        :param states: optional list of states to filter returned alerts, defaults to all. Ignored when historical is enabled
        :param severities: optional list of severities to filter returned alerts, defaults to all. Ignored when historical is enabled
        :param page: page number, starting from 1
        :param page_size: page size in number of alerts
        :param language: language the rule will be returned. Ignored when historical is enabled
        :param start_date: search alerts from that date. Only works when historical is enabled
        >param historical: return complete history of alerts
        :return: an iterator over the JSON decoded alerts
        :return:
        """
        validate_int(page, min_value=1, required=True)
        validate_int(page_size, min_value=1, required=True)
        body = {
            "page": page,
            "pageSize": page_size
        }
        if organization_id:
            body['organizationId'] = validate_uuid(organization_id)
        if scan_target_ids:
            if isinstance(scan_target_ids, str):
                scan_target_ids = [scan_target_ids]
            else:
                validate_class(scan_target_ids, Iterable)
            body['scanTargetIds'] = [validate_uuid(x) for x in scan_target_ids]
        if states:
            validate_class(states, Iterable)
            body['states'] = [validate_class(
                x, AlertState).value for x in states]
        if severities:
            validate_class(severities, Iterable)
            body['severities'] = [validate_class(
                x, AlertSeverity).value for x in severities]
        if language:
            body['lang'] = language
        if start_date:
            body['startDate'] = start_date
        if historical:
            body['historical'] = historical
        return self._request("POST", "/alerts", body=body).json()

    def iter_alerts(self, organization_id: Union[UUID, str],
                    scan_target_ids: Optional[Iterable[Union[UUID, str]]] = None,
                    states: Optional[Iterable[AlertState]] = None,
                    severities: Optional[Iterable[AlertSeverity]] = None,
                    page_size: int = 100,
                    language: Optional[Languages] = None,
                    start_date: Optional[str] = None,
                    historical: Optional[bool] = None) -> Iterator[Dict]:
        """
        Iterates over the alerts of an organization by loading them, transparently paginating on the API.
        <https://api.zanshin.tenchisecurity.com/#operation/listAllAlert>
        :param organization_id: the ID of the organization
        :param scan_target_ids: optional list of scan target IDs to list alerts from, defaults to all
        :param states: optional list of states to filter returned alerts, defaults to all. Ignored when historical is enabled
        :param severities: optional list of severities to filter returned alerts, defaults to all. Ignored when historical is enabled
        :param page_size: the number of alerts to load from the API at a time
        :param language: language the rule will be returned. Ignored when historical is enabled
        :param start_date: search alerts from that date. Only works when historical is enabled
        >param historical: return complete history of alerts
        :return: an iterator over the JSON decoded alerts
        """
        page = self._get_alerts_page(organization_id, scan_target_ids, states, severities, page=1,
                                    page_size=page_size, language=language, start_date=start_date, historical=historical)
        yield from page.get('data', [])
        for page_number in range(2, int(ceil(page.get('total', 0) / float(page_size))) + 1):
            page = self._get_alerts_page(organization_id, scan_target_ids, states, severities,
                                        page=page_number, page_size=page_size, language=language, start_date=start_date, historical=historical)
            yield from page.get('data', [])

    def _get_following_alerts_page(self, following_ids: Optional[Iterable[Union[UUID, str]]] = None,
                                   states: Optional[Iterable[AlertState]] = None,
                                   severities: Optional[Iterable[AlertSeverity]] = None, page: int = 1,
                                   page_size: int = 100) -> Dict:
        """
        Internal method to retrieve a single page of alerts from organizations being followed.
        :param following_ids: optional list of scan target IDs to list alerts from, defaults to all
        :param states: optional list of states to filter returned alerts, defaults to all
        :param severities: optional list of severities to filter returned alerts, defaults to all
        :param page: page number, starting from 1
        :param page_size: page size in number of alerts
        :return: the decoded JSON response from the API
        """
        validate_int(page, min_value=1, required=True)
        validate_int(page_size, min_value=1, required=True)
        body = {
            "page": page,
            "pageSize": page_size
        }
        if following_ids:
            if isinstance(following_ids, str):
                following_ids = [following_ids]
            else:
                validate_class(following_ids, Iterable)
            body['followingIds'] = [validate_uuid(x) for x in following_ids]
        if states:
            validate_class(states, Iterable)
            body['states'] = [validate_class(
                x, AlertState).value for x in states]
        if severities:
            validate_class(severities, Iterable)
            body['severities'] = [validate_class(
                x, AlertSeverity).value for x in severities]

        return self._request("POST", "/alerts/following", body=body).json()

    def iter_following_alerts(self, following_ids: Optional[Iterable[Union[UUID, str]]] = None,
                              states: Optional[Iterable[AlertState]] = None,
                              severities: Optional[Iterable[AlertSeverity]] = None, page_size: int = 100) -> Iterator[Dict]:
        """
        Iterates over the following alerts froms organizations being followed by transparently paginating on the API.
        <https://api.zanshin.tenchisecurity.com/#operation/listFollowingAlerts>
        :param following_ids: optional list of IDs of organizations you are following to list alerts from, defaults to all
        :param states: optional list of states to filter returned alerts, defaults to all
        :param severities: optional list of severities to filter returned alerts, defaults to all
        :param page_size: the number of alerts to load from the API at a time
        :return: an iterator over the JSON decoded alerts
        """

        if following_ids:
            if isinstance(following_ids, str):
                following_ids = [following_ids]
            else:
                validate_class(following_ids, Iterable)
        else:
            # workaround for API limitation
            following_ids = set()
            for org in self.iter_organizations():
                following_ids |= {x['id']
                                  for x in self.iter_following(org['id'])}
            following_ids = list(following_ids)

        page = self._get_following_alerts_page(
            following_ids, states, severities, page=1, page_size=page_size)
        yield from page.get('data', [])

        for page_number in range(2, int(ceil(page.get('total', 0) / float(page_size))) + 1):
            page = self._get_following_alerts_page(following_ids, states, severities, page=page_number,
                                                   page_size=page_size)
            yield from page.get('data', [])

    def _get_grouped_alerts_page(self, organization_id: Union[UUID, str],
                                scan_target_ids: Optional[Iterable[Union[UUID, str]]] = None,
                                states: Optional[Iterable[AlertState]] = None,
                                severities: Optional[Iterable[AlertSeverity]] = None, page: int = 1,
                                page_size: int = 100) -> Dict:
        """
        Internal method to retrieve a single page of alerts from an organization.
        :param organization_id: the ID of the organization
        :param scan_target_ids: optional list of scan target IDs to list alerts from, defaults to all
        :param states: optional list of states to filter returned alerts, defaults to all
        :param severities: optional list of severities to filter returned alerts, defaults to all
        :param page: page number, starting from 1
        :param page_size: page size in number of alerts
        :return:
        """
        validate_int(page, min_value=1, required=True)
        validate_int(page_size, min_value=1, required=True)
        body = {
            "page": page,
            "pageSize": page_size
        }
        if organization_id:
            body['organizationId'] = validate_uuid(organization_id)
        if scan_target_ids:
            if isinstance(scan_target_ids, str):
                scan_target_ids = [scan_target_ids]
            else:
                validate_class(scan_target_ids, Iterable)
            body['scanTargetIds'] = [validate_uuid(x) for x in scan_target_ids]
        if states:
            validate_class(states, Iterable)
            body['states'] = [validate_class(
                x, AlertState).value for x in states]
        if severities:
            validate_class(severities, Iterable)
            body['severities'] = [validate_class(
                x, AlertSeverity).value for x in severities]
        return self._request("POST", "/alerts/rules", body=body).json()

    def iter_grouped_alerts(self, organization_id: Union[UUID, str],
                            scan_target_ids: Optional[Iterable[Union[UUID, str]]] = None,
                            states: Optional[Iterable[AlertState]] = None,
                            severities: Optional[Iterable[AlertSeverity]] = None, page_size: int = 100) -> Iterator[Dict]:
        """
        Iterates over the grouped alerts of an organization by loading them, transparently paginating on the API.
        <https://api.zanshin.tenchisecurity.com/#operation/listAllAlertRules>
        :param organization_id: the ID of the organization
        :param scan_target_ids: optional list of scan target IDs to list alerts from, defaults to all
        :param states: optional list of states to filter returned alerts, defaults to all
        :param severities: optional list of severities to filter returned alerts, defaults to all
        :param page_size: the number of alerts to load from the API at a time
        :return: an iterator over the JSON decoded alerts
        """
        page = self._get_grouped_alerts_page(organization_id, scan_target_ids, states, severities, page=1,
                                            page_size=page_size)
        yield from page.get('data', [])
        for page_number in range(2, int(ceil(page.get('total', 0) / float(page_size))) + 1):
            page = self._get_grouped_alerts_page(organization_id, scan_target_ids, states, severities,
                                                page=page_number, page_size=page_size)
            yield from page.get('data', [])

    def _get_grouped_following_alerts_page(self, following_ids: Optional[Iterable[Union[UUID, str]]] = None,
                                            states: Optional[Iterable[AlertState]] = None,
                                            severities: Optional[Iterable[AlertSeverity]] = None, page: int = 1,
                                            page_size: int = 100) -> Dict:
        """
        Internal method to retrieve a single page of alerts from organizations being followed.
        :param following_ids: optional list of scan target IDs to list alerts from, defaults to all
        :param states: optional list of states to filter returned alerts, defaults to all
        :param severities: optional list of severities to filter returned alerts, defaults to all
        :param page: page number, starting from 1
        :param page_size: page size in number of alerts
        :return: the decoded JSON response from the API
        """
        validate_int(page, min_value=1, required=True)
        validate_int(page_size, min_value=1, required=True)
        body = {
            "page": page,
            "pageSize": page_size
        }
        if following_ids:
            if isinstance(following_ids, str):
                following_ids = [following_ids]
            else:
                validate_class(following_ids, Iterable)
            body['followingIds'] = [validate_uuid(x) for x in following_ids]
        if states:
            validate_class(states, Iterable)
            body['states'] = [validate_class(
                x, AlertState).value for x in states]
        if severities:
            validate_class(severities, Iterable)
            body['severities'] = [validate_class(
                x, AlertSeverity).value for x in severities]

        return self._request("POST", "/alerts/rules/following", body=body).json()

    def iter_grouped_following_alerts(self, following_ids: Optional[Iterable[Union[UUID, str]]] = None,
                                    states: Optional[Iterable[AlertState]] = None,
                                    severities: Optional[Iterable[AlertSeverity]] = None, page_size: int = 100) -> Iterator[Dict]:
        """
        Iterates over the grouped following alerts froms organizations being followed by transparently paginating on the API.
        <https://api.zanshin.tenchisecurity.com/#operation/listAllAlertRulesFollowing>
        :param following_ids: optional list of IDs of organizations you are following to list alerts from, defaults to all
        :param states: optional list of states to filter returned alerts, defaults to all
        :param severities: optional list of severities to filter returned alerts, defaults to all
        :param page_size: the number of alerts to load from the API at a time
        :return: an iterator over the JSON decoded alerts
        """

        if following_ids:
            if isinstance(following_ids, str):
                following_ids = [following_ids]
            else:
                validate_class(following_ids, Iterable)
        else:
            # workaround for API limitation
            following_ids = set()
            for org in self.iter_organizations():
                following_ids |= {x['id']
                                  for x in self.iter_following(org['id'])}
            following_ids = list(following_ids)

        page = self._get_following_alerts_page(
            following_ids, states, severities, page=1, page_size=page_size)
        yield from page.get('data', [])

        for page_number in range(2, int(ceil(page.get('total', 0) / float(page_size))) + 1):
            page = self._get_following_alerts_page(following_ids, states, severities, page=page_number,
                                                   page_size=page_size)
            yield from page.get('data', [])

    def get_alert(self, alert_id: Union[UUID, str]) -> Dict:
        """
        Returns the detailed object that describes an alert.
        <https://api.zanshin.tenchisecurity.com/#operation/getAlertById>
        :param alert_id: the ID of the alert
        :return: the decoded JSON object returned by the API
        """
        return self._request("GET", f"/alerts/{validate_uuid(alert_id)}").json()

    def iter_alert_history(self, alert_id: Union[UUID, str]) -> Iterator[Dict]:
        """
        Iterates over the history of an alert.
        <https://api.zanshin.tenchisecurity.com/#operation/listAllAlertHistory>
        :param alert_id: the ID of the alert
        :return: 
        """
        yield from self._request("GET", f"/alerts/{validate_uuid(alert_id)}/history").json()

    def iter_alert_comments(self, alert_id: Union[UUID, str]) -> Iterator[Dict]:
        """
        Iterates over the comment of an alert.
        <https://api.zanshin.tenchisecurity.com/#operation/listAllAlertComments>
        :param alert_id: the ID of the alert
        :return: 
        """
        yield from self._request("GET", f"/alerts/{validate_uuid(alert_id)}/comments").json()

    def update_alert(self, organization_id: Union[UUID, str], scan_target_id: Union[UUID, str], alert_id: Union[UUID, str],
                    state: Optional[AlertState], labels: Optional[Iterable[str]], comment: Optional[str]) -> Dict:
        """
        Update alert.
        <https://api.zanshin.tenchisecurity.com/#operation/editOrganizationScanTargetAlertById>
        :param alert_id: the ID of the alert
        :return: the decoded JSON object returned by the API
        """

        body = {
            "state": state,
            "labels": labels,
            "comment": comment,
        }

        return self._request("PUT", f"/organizations/{validate_uuid(organization_id)}/scantargets/{validate_uuid(scan_target_id)}/alerts/{validate_uuid(alert_id)}", body=body).json()

    def create_alert_comment(self, organization_id: Union[UUID, str], scan_target_id: Union[UUID, str], alert_id: Union[UUID, str], comment: str) -> Iterator[Dict]:
        """
        Iterates over the comment of an alert.
        <https://api.zanshin.tenchisecurity.com/#operation/listAllAlertComments>
        :param organization_id: the ID of the organization
        :param scan_target_id: the ID of the scan target
        :param alert_id: the ID of the alert
        :return: 
        """

        body = {
            "comment": comment
        }

        yield from self._request("POST", f"/organizations/{validate_uuid(organization_id)}/scantargets/{validate_uuid(scan_target_id)}/alerts/{validate_uuid(alert_id)}/comments", body=body).json()

    ###################################################
    # Summary
    ###################################################

    def get_alert_summaries(self, organization_id: Union[UUID, str],
                            scan_target_ids: Optional[Iterable[Union[UUID, str]]] = None) -> Dict:
        """
        Gets a summary of the current state of alerts for an organization, both in total and broken down by scan
        target.
        <https://api.zanshin.tenchisecurity.com/#operation/alertSummary>
        :param organization_id: the ID of the organization whose alert summaries are desired
        :param scan_target_ids: optional list of scan target IDs to summarize alerts from, defaults to all
        :return: JSON object containing the alert summaries
        """

        body = {"organizationId": validate_uuid(organization_id)}

        if scan_target_ids:
            if isinstance(scan_target_ids, str):
                scan_target_ids = [scan_target_ids]
            else:
                validate_class(scan_target_ids, Iterable)
            body['scanTargetIds'] = list(
                {validate_uuid(x) for x in scan_target_ids})

        return self._request("POST", "/alerts/summaries", body=body).json()
    
    def get_following_alert_summaries(self, organization_id: Union[UUID, str], following_ids: Iterable[Union[UUID, str]]) -> Dict:
        """
        Gets a summary of the current state of alerts for followed organizations.
        <https://api.zanshin.tenchisecurity.com/#operation/alertFollowingSummary>
        :param following_ids: list of IDs of organizations being followed to summarize alerts from
        :return: JSON object containing the alert summaries
        """

        if isinstance(following_ids, str):
            following_ids = [following_ids]
        else:
            validate_class(following_ids, Iterable)

        body = {
            "organizationId": validate_uuid(organization_id),
            "followingIds": list({validate_uuid(x)
                                  for x in following_ids})}

        return self._request("POST", "/alerts/summaries/following", body=body).json()

    def get_scan_summaries(self, organization_id: Union[UUID, str],
                            scan_target_ids: Optional[Iterable[Union[UUID, str]]] = None,
                            days: Optional[int] = 7) -> Dict:
        """
        Returns summaries of scan results over a period of time, summarizing number of alerts that changed states.
        <https://api.zanshin.tenchisecurity.com/#operation/scanSummary>
        :param organization_id: the ID of the organization whose scan summaries are desired
        :param scan_target_ids: optional list of scan target IDs to summarize scans from, defaults to all
        :param days: number of days to go back in time in historical search
        :return: JSON object containing the scan summaries
        """

        body = {
            "organizationId": validate_uuid(organization_id),
            "daysBefore": validate_int(days, min_value=1)
        }

        if scan_target_ids:
            if isinstance(scan_target_ids, str):
                scan_target_ids = [scan_target_ids]
            else:
                validate_class(scan_target_ids, Iterable)
            body['scanTargetIds'] = list(
                {validate_uuid(x) for x in scan_target_ids})

        return self._request("POST", "/alerts/summaries/scans", body=body).json()

    def get_following_scan_summaries(self, organization_id: Union[UUID, str], following_ids: Iterable[Union[UUID, str]], days: Optional[int] = 7) -> Dict:
        """
        Gets a summary of the current state of alerts for followed organizations.
        <https://api.zanshin.tenchisecurity.com/#operation/scanSummaryFollowing>
        :param following_ids: list of IDs of organizations being followed to summarize alerts from
        :param days: number of days to go back in time in historical search
        :return: JSON object containing the scan summaries
        """

        if isinstance(following_ids, str):
            following_ids = [following_ids]
        else:
            validate_class(following_ids, Iterable)

        body = {
            "organizationId": validate_uuid(organization_id),
            "followingIds": list({validate_uuid(x) for x in following_ids}),
            "daysBefore": validate_int(days, min_value=1)
        }

        return self._request("POST", "/alerts/summaries/scans/following", body=body).json()

    def __repr__(self):
        return f'Connection(api_url="{self.api_url}", api_key="***{self._api_key[-6:]}", user_agent="{self.user_agent}, proxy_url={self._get_sanitized_proxy_url()}")'

def validate_int(value, min_value=None, max_value=None, required=False) -> Optional[int]:
    if value is None:
        if required:
            raise ValueError('required integer parameter missing')
        else:
            return value
    if not isinstance(value, int):
        raise TypeError(f'{repr(value)} is not an integer')
    if min_value and value < min_value:
        raise ValueError(f'{repr(value)} shouldn\'t be lower than {min_value}')
    if max_value and value > max_value:
        raise ValueError(
            f'{repr(value)} shouldn\'t be higher than {max_value}')
    return value


def validate_class(value, class_type):
    if not isinstance(value, class_type):
        raise TypeError(
            f'{repr(value)} is not an instance of {class_type.__name__}')
    return value


def validate_uuid(uuid: Union[UUID, str]) -> str:
    if isinstance(uuid, str):
        return str(UUID(uuid))
    elif isinstance(uuid, UUID):
        return str(uuid)
    else:
        raise TypeError(f'{repr(uuid)} is not a valid UUID')
