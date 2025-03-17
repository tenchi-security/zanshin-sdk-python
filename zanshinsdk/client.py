from __future__ import annotations

import json
import logging
import sys
import time
from configparser import RawConfigParser
from importlib.util import find_spec, module_from_spec
from math import ceil
from os import environ
from os.path import isfile
from pathlib import Path
from typing import Dict, Iterable, Iterator, Optional, Union
from urllib.parse import urlparse
from uuid import UUID

import httpx
from pydantic import BaseModel, Field

from zanshinsdk.common.enums import (
    AlertSeverity,
    AlertsOrderOpts,
    AlertState,
    Day,
    Frequency,
    GroupedAlertOrderOpts,
    Languages,
    OAuthTargetKind,
    Roles,
    ScanTargetGroupKind,
    ScanTargetKind,
    SortOpts,
    TimeOfDay,
)
from zanshinsdk.common.targets import (
    ScanTargetAWS,
    ScanTargetAZURE,
    ScanTargetBITBUCKET,
    ScanTargetDOMAIN,
    ScanTargetGCP,
    ScanTargetGITHUB,
    ScanTargetGITLAB,
    ScanTargetGroupCredentialListORACLE,
    ScanTargetGWORKSPACE,
    ScanTargetHUAWEI,
    ScanTargetJIRA,
    ScanTargetMS365,
    ScanTargetORACLE,
    ScanTargetSALESFORCE,
    ScanTargetSLACK,
    ScanTargetZENDESK,
)
from zanshinsdk.common.validators import (
    validate_base_alert_filter,
    validate_class,
    validate_date,
    validate_int,
    validate_uuid,
)
from zanshinsdk.version import __version__ as sdk_version

CONFIG_DIR = Path.home() / ".tenchi"
CONFIG_FILE = CONFIG_DIR / "config"


class ScanTargetSchedule(BaseModel):
    frequency: Frequency
    time_of_day: Optional[TimeOfDay] = Field(TimeOfDay.NIGHT, alias="timeOfDay")
    day: Optional[Day] = Day.SUNDAY

    def value(self):
        if self.frequency in (Frequency.SIX_HOURS, Frequency.TWELVE_HOURS):
            return {"frequency": self.frequency.value}
        if self.frequency == Frequency.WEEKLY:
            return {
                "frequency": self.frequency.value,
                "timeOfDay": self.time_of_day.value,
                "day": self.day.value,
            }
        return {
            "frequency": self.frequency.value,
            "timeOfDay": self.time_of_day.value,
        }

    def json(self):
        return json.dumps(self.value())


DAILY = ScanTargetSchedule(frequency=Frequency.DAILY, time_of_day=TimeOfDay.NIGHT)
WEEKLY = ScanTargetSchedule(
    frequency=Frequency.WEEKLY, time_of_day=TimeOfDay.NIGHT, day=Day.SUNDAY
)


class Client:
    def __init__(
        self,
        profile: str = "default",
        api_key: Optional[str] = None,
        api_url: Optional[str] = None,
        user_agent: Optional[str] = None,
        proxy_url: Optional[str] = None,
        verify: httpx._types.VerifyTypes = True,
    ):
        """
        Initialize a new connection to the Zanshin API
        :param profile: which configuration file section to use for settings, or None to ignore configuration file
        :param api_key: optional override of the API key to use
        :param api_url: optional override of the base URL of the Zanshin API to use
        :param user_agent: optional addition of the user agent to use in requests performed
        :param proxy_url: optional URL indicating which proxy server to use, or None for direct connections to the API
        :verify: optional parameter to control how SSL connections are verified as per the parameter of the same name in the constructor of :httpx:Client
        """
        self._client = None
        self._logger: logging.Logger = logging.getLogger("zanshinsdk")

        (
            api_key,
            api_url,
            user_agent,
            proxy_url,
        ) = self._get_config_from_env_if_not_exists(
            api_key=api_key, api_url=api_url, user_agent=user_agent, proxy_url=proxy_url
        )

        # read configuration file if no env variable is set
        if (
            profile
            and isfile(CONFIG_FILE)
            or all(value is None for value in [api_key, api_url, user_agent])
        ):
            parser = RawConfigParser()
            parser.read(str(CONFIG_FILE))
            if not parser.has_section(profile):
                raise ValueError(f"profile {profile} not found in {CONFIG_FILE}")
        else:
            parser = None

        # set API key
        if api_key:
            self._api_key = api_key
        elif parser and parser.get(profile, "api_key", fallback=None):
            self._api_key = parser.get(profile, "api_key")
        else:
            raise ValueError("no API key found")

        # set API URL
        if api_url:
            self._api_url = api_url
        elif parser and parser.get(profile, "api_url", fallback=None):
            self._api_url = parser.get(profile, "api_url")
        else:
            self._api_url = "https://api.zanshin.tenchisecurity.com"

        if self._api_url:
            parsed = urlparse(self._api_url)
            if (
                not parsed.scheme
                or parsed.scheme not in ("http", "https")
                or not parsed.hostname
                or parsed.password
                or parsed.username
                or (parsed.port and (parsed.port <= 0 or parsed.port > 65535))
            ):
                raise ValueError(f"Invalid API URL: {self._api_url}")

        # set proxy URL
        if proxy_url:
            self._proxy_url = proxy_url
        elif parser and parser.get(profile, "proxy_url", fallback=None):
            self._proxy_url = parser.get(profile, "proxy_url")
        else:
            self._proxy_url = None

        if self._proxy_url:
            parsed = urlparse(self._proxy_url)
            if (
                parsed.scheme not in ("http", "https")
                or not parsed.hostname
                or (parsed.password and not parsed.username)
                or (parsed.port and (parsed.port <= 0 or parsed.port > 65535))
            ):
                raise ValueError(f"Invalid proxy URL: {self._proxy_url}")

        # set user-agent
        if user_agent:
            self._user_agent = f"{user_agent} (Zanshin Python SDK v{sdk_version})"
        elif parser and parser.get(profile, "user_agent", fallback=None):
            self._user_agent = f"{parser.get(profile, 'user_agent')} (Zanshin Python SDK v{sdk_version})"
        else:
            self._user_agent = f"Zanshin Python SDK v{sdk_version}"

        # set verify
        self._verify = verify

        self._update_client()

    def _get_config_from_env_if_not_exists(
        self, api_key: str, api_url: str, user_agent: str, proxy_url: str
    ):
        """
        If api_key, api_url_, proxy_url, or user_agent are not set, try to get them from Environment Variables
        If any configuration value is set, ignore the Environment Variables
        """
        env_zanshin_api_key = (
            environ["ZANSHIN_API_KEY"] if "ZANSHIN_API_KEY" in environ else None
        )
        env_zanshin_api_url = (
            environ["ZANSHIN_API_URL"] if "ZANSHIN_API_URL" in environ else None
        )
        env_zanshin_user_agent = (
            environ["ZANSHIN_USER_AGENT"] if "ZANSHIN_USER_AGENT" in environ else None
        )
        if "HTTPS_PROXY" in environ:
            env_proxy_url = environ["HTTPS_PROXY"]
        elif "HTTP_PROXY" in environ:
            env_proxy_url = environ["HTTP_PROXY"]
        else:
            env_proxy_url = None

        if not api_key and env_zanshin_api_key:
            api_key = env_zanshin_api_key
        if not api_url and env_zanshin_api_url:
            api_url = env_zanshin_api_url
        if not user_agent and env_zanshin_user_agent:
            user_agent = env_zanshin_user_agent
        if not proxy_url and env_proxy_url:
            proxy_url = env_proxy_url
        return api_key, api_url, user_agent, proxy_url

    def _update_client(self):
        """
        Internal method to create a new pre-configured httpx Client instance when one of the relevant settings
        is changed (API key, proxy URL or user-agent).
        """
        try:
            if self._client:
                self._client.close()
        except AttributeError:
            pass
        finally:
            self._client = httpx.Client(
                proxy=self._proxy_url,
                timeout=60,
                verify=self._verify,
                headers={
                    "Authorization": f"Bearer {self._api_key}",
                    "Accept-Encoding": "gzip, deflate",
                    "User-Agent": self.user_agent,
                    "Accept": "application/json",
                },
            )

    @property
    def api_url(self) -> str:
        return self._api_url

    @api_url.setter
    def api_url(self, new_api_url: str) -> None:
        if new_api_url is None:
            raise ValueError("API URL cannot be null")

        parsed = urlparse(new_api_url)
        if (
            not parsed.scheme
            or parsed.scheme not in ("http", "https")
            or not parsed.hostname
            or parsed.password
            or parsed.username
            or (parsed.port and (parsed.port <= 0 or parsed.port > 65535))
        ):
            raise ValueError(f"Invalid API URL: {new_api_url}")
        self._api_url: str = new_api_url.rstrip("/")

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
        if new_proxy_url is None:
            self._proxy_url = None
        elif new_proxy_url != self._proxy_url:
            parsed = urlparse(new_proxy_url)
            if (
                parsed.scheme not in ("http", "https")
                or not parsed.hostname
                or (parsed.password and not parsed.username)
                or (parsed.port and (parsed.port <= 0 or parsed.port > 65535))
            ):
                raise ValueError(f"Invalid proxy URL: {new_proxy_url}")
            self._proxy_url = new_proxy_url
        self._update_client()

    @property
    def user_agent(self) -> str:
        return self._user_agent

    @user_agent.setter
    def user_agent(self, new_user_agent: str) -> None:
        self._user_agent = f"{new_user_agent} (Zanshin Python SDK v{sdk_version})"
        self._update_client()

    def _get_sanitized_proxy_url(self) -> Optional[str]:
        """
        Returns a sanitized proxy URL that doesn't expose a password, if one is present.
        :return:
        """
        if self.proxy_url:
            url = urlparse(self.proxy_url)
            proxy_url = f"{url.scheme}://"
            if url.username:
                proxy_url += url.username
                if url.password:
                    proxy_url += ":***"
                proxy_url += "@"
            proxy_url += url.hostname
            if url.port:
                proxy_url += f":{url.port}"
            return proxy_url
        else:
            return None

    def _request(
        self, method: str, path: str, params=None, body=None
    ) -> httpx.Response:
        """
        Internal method to simplify calling requests
        :param method: HTTP method to pass along to httpx.Client.request
        :param path: API path to access
        :param params: parameters to pass along to httpx.Client.request
        :param body: request body to pass along to httpx.Client.request
        :return: the requests.Response object returned by httpx.Client.request
        """

        self._logger.debug("Requesting body=%s", body)
        response = self._client.request(
            method=method, url=self.api_url + path, params=params, json=body
        )
        if response.request.content:
            self._logger.debug(
                "%s %s (%d bytes in request body) status code %d",
                response.request.method,
                response.request.url,
                len(response.request.content),
                response.status_code,
            )
        else:
            self._logger.debug(
                "%s %s status code %d",
                response.request.method,
                response.request.url,
                response.status_code,
            )
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
        Gets a specific invitation details, it only works if the invitation was made for the current logged user.
        <https://api.zanshin.tenchisecurity.com/#operation/getInviteById>
        :param invite_id: the ID of the invite
        :return: a dict representing the user invite
        """
        return self._request("GET", f"/me/invites/{validate_uuid(invite_id)}").json()

    def accept_invite(self, invite_id: Union[UUID, str]) -> Dict:
        """
        Accepts an invitation with the informed ID, it only works if the user accepting the invitation is the user that
        received the invitation.
        <https://api.zanshin.tenchisecurity.com/#operation/acceptInviteById>
        :param invite_id: the ID of the invite
        :return: a dict representing the organization of this invite
        """
        return self._request(
            "POST", f"/me/invites/{validate_uuid(invite_id)}/accept"
        ).json()

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
        Creates a new API key for the current logged user, API Keys can be used to interact with the zanshin api
        directly on behalf of that user.
        <https://api.zanshin.tenchisecurity.com/#operation/createApiKeys>
        :param name: the Name of your new API key
        :return: a dict representing the user api key
        """
        body = {"name": name}
        return self._request("POST", "/me/apikeys", body=body).json()

    def delete_api_key(self, api_key_id: Union[UUID, str]) -> bool:
        """
        Deletes a given API key by its id, it will only work if the informed ID belongs to the current logged user.
        <https://api.zanshin.tenchisecurity.com/#operation/deleteApiKey>
        :param api_key_id: the ID of the API key
        :return: a boolean if success
        """
        return self._request(
            "DELETE", f"/me/apikeys/{validate_uuid(api_key_id)}"
        ).json()

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
        return self._request(
            "GET", f"/organizations/{validate_uuid(organization_id)}"
        ).json()

    def delete_organization(self, organization_id: Union[UUID, str]) -> bool:
        """
        Deletes an organization given its ID.
        <https://api.zanshin.tenchisecurity.com/#operation/getOrganizationById>
        :param organization_id: the ID of the organization
        :return: a boolean if success
        """
        return self._request(
            "DELETE", f"/organizations/{validate_uuid(organization_id)}"
        ).json()

    def update_organization(
        self,
        organization_id: Union[UUID, str],
        name: Optional[str],
        picture: Optional[str],
        email: Optional[str],
    ) -> Dict:
        """
        Update organization given its ID.
        <https://api.zanshin.tenchisecurity.com/#operation/editOrganizationById>
        :param organization_id: the ID of the organization
        :param name: the Name of the organization
        :param picture: the picture URL of the organization, accepted formats: jpg, jpeg, png, svg
        :param email: the e-mail contact of the organization
        :return: a dict representing the organization object
        """
        body = {"name": name, "picture": picture, "email": email}
        return self._request(
            "PUT", f"/organizations/{validate_uuid(organization_id)}", body=body
        ).json()

    def create_organization(self, name: str) -> Dict:
        """
        Create organization.
        <https://api.zanshin.tenchisecurity.com/#operation/createOrganization>
        :param name: the Name of the organization
        :return: a dict representing the organization
        """
        body = {"name": name}
        return self._request("POST", f"/organizations", body=body).json()

    ###################################################
    # Organization Member
    ###################################################

    def iter_organization_members(
        self, organization_id: Union[UUID, str]
    ) -> Iterator[Dict]:
        """
        Iterates over the users which are members of an organization.
        <https://api.zanshin.tenchisecurity.com/#operation/getOrganizationMembers>
        :param organization_id: the ID of the organization
        :return: an iterator over the organization members objects
        """
        yield from self._request(
            "GET", f"/organizations/{validate_uuid(organization_id)}/members"
        ).json()

    def get_organization_member(
        self, organization_id: Union[UUID, str], member_id: Union[UUID, str]
    ) -> Dict:
        """
        Get details on a user's organization membership.
        <https://api.zanshin.tenchisecurity.com/#operation/getOrganizationMembers>
        :param organization_id: the ID of the organization
        :param member_id: the ID of the member
        :return: a dict representing the organization member
        """
        return self._request(
            "GET",
            f"/organizations/{validate_uuid(organization_id)}/members/"
            f"{validate_uuid(member_id)}",
        ).json()

    def update_organization_member(
        self,
        organization_id: Union[UUID, str],
        member_id: Union[UUID, str],
        roles: Optional[Iterable[Roles]],
    ) -> Dict:
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
        return self._request(
            "PUT",
            f"/organizations/{validate_uuid(organization_id)}/members/{validate_uuid(member_id)}",
            body=body,
        ).json()

    def delete_organization_member(
        self, organization_id: Union[UUID, str], member_id: Union[UUID, str]
    ) -> bool:
        """
        Delete organization member.
        <https://api.zanshin.tenchisecurity.com/#operation/removeOrganizationMemberById>
        :param organization_id: the ID of the organization
        :param member_id: the ID of the member
        :return: a boolean if success
        """
        return self._request(
            "DELETE",
            f"/organizations/{validate_uuid(organization_id)}/members/"
            f"{validate_uuid(member_id)}",
        ).json()

    def reset_organization_member_mfa(
        self, organization_id: Union[UUID, str], member_id: Union[UUID, str]
    ) -> bool:
        """
        Reset organization member MFA.
        <https://api.zanshin.tenchisecurity.com/#operation/resetOrganizationMemberMfaById>
        :param organization_id: the ID of the organization
        :param member_id: the ID of the member
        :return: a boolean if success
        """
        return self._request(
            "POST",
            f"/organizations/{validate_uuid(organization_id)}/members/"
            f"{validate_uuid(member_id)}/mfa/reset",
        ).json()

    def reset_delete_organization_password(
        self, organization_id: Union[UUID, str], member_id: Union[UUID, str]
    ) -> bool:
        """
        Reset organization member Password.
        <https://api.zanshin.tenchisecurity.com/#operation/resetOrganizationMemberPasswordById>
        :param organization_id: the ID of the organization
        :param member_id: the ID of the member
        :return: a boolean if success
        """
        return self._request(
            "POST",
            f"/organizations/{validate_uuid(organization_id)}/members/"
            f"{validate_uuid(member_id)}/password/reset",
        ).json()

    ###################################################
    # Organization Member Invite
    ###################################################

    def iter_organization_members_invites(
        self, organization_id: Union[UUID, str]
    ) -> Iterator[Dict]:
        """
        Iterates over the members invites of an organization.
        <https://api.zanshin.tenchisecurity.com/#operation/getOrgamizationInvites>
        :param organization_id: the ID of the organization
        :return: an iterator over the organization members invites objects
        """
        yield from self._request(
            "GET", f"/organizations/{validate_uuid(organization_id)}/invites"
        ).json()

    def create_organization_members_invite(
        self,
        organization_id: Union[UUID, str],
        email: str,
        roles: Optional[Iterable[Roles]],
    ) -> Iterator[Dict]:
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
        return self._request(
            "POST",
            f"/organizations/{validate_uuid(organization_id)}/invites",
            body=body,
        ).json()

    def get_organization_member_invite(
        self, organization_id: Union[UUID, str], email: str
    ) -> Iterator[Dict]:
        """
        Get organization member invite.
        <https://api.zanshin.tenchisecurity.com/#operation/getOrganizationInviteByEmail>
        :param organization_id: the ID of the organization
        :param email: the e-mail of the invited member
        :return: a dict representing the organization member invite
        """
        return self._request(
            "GET", f"/organizations/{validate_uuid(organization_id)}/invites/{email}"
        ).json()

    def delete_organization_member_invite(
        self, organization_id: Union[UUID, str], email: str
    ) -> bool:
        """
        Delete organization member invite.
        <https://api.zanshin.tenchisecurity.com/#operation/deleteOrganizationInviteByEmail>
        :param organization_id: the ID of the organization
        :param email: the e-mail of the invited member
        :return: a boolean if success
        """
        return self._request(
            "DELETE", f"/organizations/{validate_uuid(organization_id)}/invites/{email}"
        ).json()

    def resend_organization_member_invite(
        self, organization_id: Union[UUID, str], email: str
    ) -> Dict:
        """
        Resend organization member invitation.
        <https://api.zanshin.tenchisecurity.com/#operation/resendOrganizationInviteByEmail>
        :param organization_id: the ID of the organization
        :param email: the e-mail of the invited member
        :return: a boolean if success
        """
        return self._request(
            "POST",
            f"/organizations/{validate_uuid(organization_id)}/invites/{email}/resend",
        ).json()

    ###################################################
    # Organization Follower
    ###################################################

    def iter_organization_followers(
        self, organization_id: Union[UUID, str]
    ) -> Iterator[Dict]:
        """
        Iterates over the followers of an organization.
        <https://api.zanshin.tenchisecurity.com/#operation/getOrganizationFollowers>
        :param organization_id: the ID of the organization
        :return: an iterator over the organization followers objects
        """
        yield from self._request(
            "GET", f"/organizations/{validate_uuid(organization_id)}/followers"
        ).json()

    def stop_organization_follower(
        self, organization_id: Union[UUID, str], follower_id: Union[UUID, str]
    ) -> bool:
        """
        Stops one organization follower of another.
        <https://api.zanshin.tenchisecurity.com/#operation/removeOrganizationFollower>
        :param organization_id: the ID of the organization
        :param follower_id: the ID of the follower
        :return: a boolean if success
        """
        return self._request(
            "DELETE",
            f"/organizations/{validate_uuid(organization_id)}/followers/"
            f"{validate_uuid(follower_id)}",
        ).json()

    ###################################################
    # Organization Follower Request
    ###################################################

    def iter_organization_follower_requests(
        self, organization_id: Union[UUID, str]
    ) -> Iterator[Dict]:
        """
        Iterates over the follower requests of an organization.
        <https://api.zanshin.tenchisecurity.com/#operation/getOrganizationFollowRequests>
        :param organization_id: the ID of the organization
        :return: an iterator over the organization follower requests objects
        """
        yield from self._request(
            "GET", f"/organizations/{validate_uuid(organization_id)}/followers/requests"
        ).json()

    def create_organization_follower_request(
        self, organization_id: Union[UUID, str], token: Union[UUID, str]
    ) -> Dict:
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
        return self._request(
            "POST",
            f"/organizations/{validate_uuid(organization_id)}/followers/requests",
            body=body,
        ).json()

    def get_organization_follower_request(
        self, organization_id: Union[UUID, str], token: Union[UUID, str]
    ) -> Dict:
        """
        Get organization follower request.
        <https://api.zanshin.tenchisecurity.com/#operation/getOrganizationFollowRequestsByToken>
        :param organization_id: the ID of the organization
        :param token: the token of the follower request
        :return: a dict representing the organization follower
        """
        return self._request(
            "GET",
            f"/organizations/{validate_uuid(organization_id)}/followers/requests/"
            f"{validate_uuid(token)}",
        ).json()

    def delete_organization_follower_request(
        self, organization_id: Union[UUID, str], follower_id: Union[UUID, str]
    ) -> bool:
        """
        Delete organization follower request.
        <https://api.zanshin.tenchisecurity.com/#operation/deleteOrganizationFollowRequestsbyToken>
        :param organization_id: the ID of the organization
        :param follower_id: the ID of the follower
        :return: a boolean if success
        """
        return self._request(
            "DELETE",
            f"/organizations/{validate_uuid(organization_id)}/followers/requests/"
            f"{validate_uuid(follower_id)}",
        ).json()

    ###################################################
    # Organization Following
    ###################################################

    def iter_organization_following(
        self, organization_id: Union[UUID, str]
    ) -> Iterator[Dict]:
        """
        Iterates over the following of an organization.
        <https://api.zanshin.tenchisecurity.com/#operation/getOrganizationFollowing>
        :param organization_id: the ID of the organization whose followed organizations we should list
        :return: an iterator over the JSON decoded followed organizations
        """
        yield from self._request(
            "GET", f"/organizations/{validate_uuid(organization_id)}/following"
        ).json()

    def stop_organization_following(
        self, organization_id: Union[UUID, str], following_id: Union[UUID, str]
    ) -> bool:
        """
        Stops one organization following of another.
        <https://api.zanshin.tenchisecurity.com/#operation/removeOrganizationFollowingById>
        :param organization_id: the follower organization ID
        :param following_id:  the followed organization ID
        :return: a boolean indicating whether the operation was successful
        """
        return self._request(
            "DELETE",
            f"/organizations/{validate_uuid(organization_id)}/following/"
            f"{validate_uuid(following_id)}",
        ).json()

    ###################################################
    # Organization Following Request
    ###################################################

    def iter_organization_following_requests(
        self, organization_id: Union[UUID, str]
    ) -> Iterator[Dict]:
        """
        Returns all requests received by an organization to follow another.
        <https://api.zanshin.tenchisecurity.com/#operation/getOrganizationFollowingRequests>
        :param organization_id: the ID of the organization that was invited to follow another
        :return: an iterator over the JSON decoded following requests
        """
        yield from self._request(
            "GET", f"/organizations/{validate_uuid(organization_id)}/following/requests"
        ).json()

    def get_organization_following_request(
        self, organization_id: Union[UUID, str], following_id: Union[UUID, str]
    ) -> Dict:
        """
        Returns a request received by an organization to follow another.
        <https://api.zanshin.tenchisecurity.com/#operation/getOrganizationFollowingRequestByToken>
        :param organization_id: the ID of the organization
        :param following_id: the ID of the following
        :return: a dict representing the following request
        """
        return self._request(
            "GET",
            f"/organizations/{validate_uuid(organization_id)}/following/requests/"
            f"{validate_uuid(following_id)}",
        ).json()

    def accept_organization_following_request(
        self, organization_id: Union[UUID, str], following_id: Union[UUID, str]
    ) -> Dict:
        """
        Accepts a request to follow another organization.
        <https://api.zanshin.tenchisecurity.com/#operation/acceptOrganizationFollowingRequestByToken>
        :param organization_id: the ID of the organization who was invited to follow another
        :param following_id: the ID of the organization who is going to be followed
        :return: a decoded JSON object describing the newly established following relationship
        """
        return self._request(
            "POST",
            f"/organizations/{validate_uuid(organization_id)}/following/requests/"
            f"{validate_uuid(following_id)}/accept",
        ).json()

    def decline_organization_following_request(
        self, organization_id: Union[UUID, str], following_id: Union[UUID, str]
    ) -> Dict:
        """
        Declines a request to follow another organization.
        <https://api.zanshin.tenchisecurity.com/#operation/declineOrganizationFollowingRequestByToken>
        :param organization_id: the ID of the organization who was invited to follow another
        :param following_id: the ID of the organization who was going to be followed
        :return: a decoded JSON object describing the newly established following relationship
        """
        return self._request(
            "POST",
            f"/organizations/{validate_uuid(organization_id)}/following/requests/"
            f"{validate_uuid(following_id)}/decline",
        ).json()

    ###################################################
    # Organization Scan Target
    ###################################################

    def iter_organization_scan_targets(
        self, organization_id: Union[UUID, str]
    ) -> Iterator[Dict]:
        """
        Iterates over the scan targets of an organization.
        <https://api.zanshin.tenchisecurity.com/#operation/getOrganizationScanTargets>
        :param organization_id: the ID of the organization
        : return: an iterator over the scan target objects
        """
        yield from self._request(
            "GET", f"/organizations/{validate_uuid(organization_id)}/scantargets"
        ).json()

    def create_organization_scan_target(
        self,
        organization_id: Union[UUID, str],
        kind: ScanTargetKind,
        name: str,
        credential: Union[
            ScanTargetAWS,
            ScanTargetAZURE,
            ScanTargetGCP,
            ScanTargetHUAWEI,
            ScanTargetDOMAIN,
            ScanTargetORACLE,
            ScanTargetZENDESK,
            ScanTargetGWORKSPACE,
            ScanTargetSLACK,
            ScanTargetBITBUCKET,
            ScanTargetJIRA,
            ScanTargetGITLAB,
            ScanTargetSALESFORCE,
            ScanTargetMS365,
        ],
        schedule: ScanTargetSchedule = DAILY,
    ) -> Dict:
        """
        Create a new scan target in organization.
        <https://api.zanshin.tenchisecurity.com/#operation/createOrganizationScanTargets>
        :param organization_id: the ID of the organization
        :param kind: the Kind of scan target (AWS, GCP, AZURE)
        :param name: the name of the scan target
        :param credential: credentials to access the cloud account to be scanned:
            * For AWS scan targets, provide the account ID in the *account* field
            * For Azure scan targets, provide *applicationId*, *subscriptionId*, *directoryId* and *secret* fields.
            * For GCP scan targets, provide a *projectId* field
            * For DOMAIN scan targets, provide a URL in the *domain* field
            * For ZENDESK scan target, provide *instance_url* field
            * For Jira scan target, provide *jira_url* field
            * For MS365 scan target, provide *tenant_id*, *application_id*, *secret* fields
            * For GITHUB scan target, provide *installation_id*, *organizationName* fields
            * For GWORKSPACE, SLACK, BITBUCKET, GITLAB, SALESFORCE no one credential are needed
        :param schedule: schedule as a string or enum version of the scan frequency
        :return: a dict representing the newly created scan target
        """
        validate_class(kind, ScanTargetKind)
        validate_class(name, str)

        validator_credential_map = {
            ScanTargetKind.AWS: ScanTargetAWS,
            ScanTargetKind.AZURE: ScanTargetAZURE,
            ScanTargetKind.GCP: ScanTargetGCP,
            ScanTargetKind.HUAWEI: ScanTargetHUAWEI,
            ScanTargetKind.DOMAIN: ScanTargetDOMAIN,
            ScanTargetKind.ORACLE: ScanTargetORACLE,
            ScanTargetKind.ZENDESK: ScanTargetZENDESK,
            ScanTargetKind.GWORKSPACE: ScanTargetGWORKSPACE,
            ScanTargetKind.SLACK: ScanTargetSLACK,
            ScanTargetKind.BITBUCKET: ScanTargetBITBUCKET,
            ScanTargetKind.JIRA: ScanTargetJIRA,
            ScanTargetKind.GITLAB: ScanTargetGITLAB,
            ScanTargetKind.SALESFORCE: ScanTargetSALESFORCE,
            ScanTargetKind.MS365: ScanTargetMS365,
            ScanTargetKind.GITHUB: ScanTargetGITHUB,
        }

        if not validator_credential_map.get(kind):
            raise ValueError(f"Invalid kind: {kind}")

        validate_class(credential, validator_credential_map.get(kind))

        body = {
            "name": name,
            "kind": kind,
            "credential": credential,
            "schedule": schedule.value(),
        }

        return self._request(
            "POST",
            f"/organizations/{validate_uuid(organization_id)}/scantargets",
            body=body,
        ).json()

    def get_organization_scan_target(
        self, organization_id: Union[UUID, str], scan_target_id: Union[UUID, str]
    ) -> Dict:
        """
        Get scan target of organization.
        <https://api.zanshin.tenchisecurity.com/#operation/getOrganizationScanTargetById>
        :param scan_target_id:
        :param organization_id: the ID of the organization
        :return: a dict representing the scan target
        """
        return self._request(
            "GET",
            f"/organizations/{validate_uuid(organization_id)}/scantargets/"
            f"{validate_uuid(scan_target_id)}",
        ).json()

    def update_organization_scan_target(
        self,
        organization_id: Union[UUID, str],
        scan_target_id: Union[UUID, str],
        name: str,
        schedule: ScanTargetSchedule = DAILY,
    ) -> Dict:
        """
        Update scan target of organization.
        <https://api.zanshin.tenchisecurity.com/#operation/editOrganizationScanTargetById>
        :param schedule:
        :param scan_target_id:
        :param name:
        :param organization_id: the ID of the organization
        :return: a dict representing the organization follower
        """

        body = {
            "name": name,
            "schedule": schedule.value(),
        }

        return self._request(
            "PUT",
            f"/organizations/{validate_uuid(organization_id)}/scantargets/"
            f"{validate_uuid(scan_target_id)}",
            body=body,
        ).json()

    def delete_organization_scan_target(
        self, organization_id: Union[UUID, str], scan_target_id: Union[UUID, str]
    ) -> bool:
        """
        Delete scan target of organization.
        <https://api.zanshin.tenchisecurity.com/#operation/deleteOrganizationScanTargetById>
        :param organization_id: the ID of the organization
        :param scan_target_id:
        :return: a boolean if success
        """
        return self._request(
            "DELETE",
            f"/organizations/{validate_uuid(organization_id)}/scantargets/"
            f"{validate_uuid(scan_target_id)}",
        ).json()

    def start_organization_scan_target_scan(
        self,
        organization_id: Union[UUID, str],
        scan_target_id: Union[UUID, str],
        force: Optional[bool],
    ) -> bool:
        """
        Starts a scan on the specified scan target.
        <https://api.zanshin.tenchisecurity.com/#operation/scanOrganizationScanTarget>
        :param organization_id: the ID of organization the scan target belongs to
        :param scan_target_id: the ID of the scan target
        :param force: whether to force a scan that is in state NEW or INVALID_CREDENTIAL
        :return: a boolean if success
        """

        params = {
            "force": "true" if force else "false"  # Http params are always strings
        }
        return self._request(
            "POST",
            f"/organizations/{validate_uuid(organization_id)}/scantargets/"
            f"{validate_uuid(scan_target_id)}/scan",
            params=params,
        ).json()

    def stop_organization_scan_target_scan(
        self, organization_id: Union[UUID, str], scan_target_id: Union[UUID, str]
    ) -> bool:
        """
        Stop a scan on the specific scan target
        :param organization_id: the ID of organization the scan target belongs to
        :param scan_target_id: the ID of the scan target
        :return: a boolean if success
        """
        return self._request(
            "POST",
            f"/organizations/{validate_uuid(organization_id)}/scantargets/"
            f"{validate_uuid(scan_target_id)}/stop",
        ).json()

    def check_organization_scan_target(
        self, organization_id: Union[UUID, str], scan_target_id: Union[UUID, str]
    ) -> Dict:
        """
        Check scan target.
        <https://api.zanshin.tenchisecurity.com/#operation/checkOrganizationScanTarget>
        :param organization_id: the ID of organization the scan target belongs to
        :param scan_target_id: the ID of the scan target
        :return: a dict representing the scan target
        """
        return self._request(
            "POST",
            f"/organizations/{validate_uuid(organization_id)}/scantargets/"
            f"{validate_uuid(scan_target_id)}/check",
        ).json()

    ###################################################
    # Scan Target OAuth
    ###################################################

    def get_scan_target_oauth_link(
        self,
        organization_id: Union[UUID, str],
        scan_target_id: Union[UUID, str],
    ) -> Dict:
        """
        Retrieve a link to authorize zanshin to read info from their target.

        Mandatory for scan targets of kind:
            * ZENDESK
            * GWORKSPACE
            * SLACK
            * BITBUCKET
            * JIRA
            * GITLAB
            * SALESFORCE
        :return: a dict with the link
        """
        path = (
            f"/oauth/link"
            f"?organizationId={validate_uuid(organization_id)}"
            f"&scanTargetId={validate_uuid(scan_target_id)}"
        )

        return self._request("GET", path).json()

    def get_scan_target_group_oauth_link(
        self,
        organization_id: Union[UUID, str],
        scan_target_group_id: Union[UUID, str],
    ):
        """
        Retrieve a link to authorize zanshin to read info from their target group.

        Mandatory for scan target groups of kind:
            * BITBUCKET
            * GITLAB
        :return: a dict with the link
        """
        path = (
            f"/oauth/link"
            f"?organizationId={validate_uuid(organization_id)}"
            f"&scanTargetGroupId={validate_uuid(scan_target_group_id)}"
        )

        return self._request("GET", path).json()

    def get_gworkspace_oauth_link(
        self, organization_id: Union[UUID, str], scan_target_id: Union[UUID, str]
    ) -> Dict:
        """
        Retrieve a link to allow the user to authorize zanshin to read info from their gworkspace environment.
        <https://api.zanshin.tenchisecurity.com/#operation/getGworkspaceOauthLink>
        :return: a dict with the link
        """
        return self._request(
            "GET",
            f"/gworkspace/oauth/link?scanTargetId={validate_uuid(scan_target_id)}"
            f"&organizationId={validate_uuid(organization_id)}",
        ).json()

    ###################################################
    # Organization Scan Target Scan
    ###################################################

    def iter_organization_scan_target_scans(
        self, organization_id: Union[UUID, str], scan_target_id: Union[UUID, str]
    ) -> Iterator[Dict]:
        """
        Iterates over the scan of a scan target.
        <https://api.zanshin.tenchisecurity.com/#operation/getOrganizationScanTargetScans>
        :param organization_id: the ID of the organization
        :param scan_target_id: the ID of the scan target
        :return: an iterator over the JSON decoded scans
        """
        yield from self._request(
            "GET",
            f"/organizations/{validate_uuid(organization_id)}/scantargets/"
            f"{validate_uuid(scan_target_id)}/scans",
        ).json().get("data", [])

    def get_organization_scan_target_scan(
        self,
        organization_id: Union[UUID, str],
        scan_target_id: Union[UUID, str],
        scan_id: Union[UUID, str],
    ) -> Dict:
        """
        Get scan of scan target.
        <https://api.zanshin.tenchisecurity.com/#operation/getOrganizationScanTargetScanSlot>
        :param organization_id: the ID of the organization
        :param scan_target_id: the ID of the scan target
        :param scan_id: the ID of the scan
        :return: a dict representing the scan
        """
        return self._request(
            "GET",
            f"/organizations/{validate_uuid(organization_id)}/scantargets/"
            f"{validate_uuid(scan_target_id)}/scans/{scan_id}",
        ).json()

    ###################################################
    # Organization Scan Target Groups
    ###################################################

    def iter_organization_scan_target_groups(
        self, organization_id: Union[UUID, str]
    ) -> Iterator[Dict]:
        """
        Iterates over the scan targets groups.
        <https://api.zanshin.tenchisecurity.com/#operation/getOrganizationScanTargetGroups>
        :param organization_id: the ID of the organization
        : return: an iterator over the scan target groups
        """
        yield from self._request(
            "GET", f"/organizations/{validate_uuid(organization_id)}/scantargetgroups"
        ).json()

    def get_organization_scan_target_group(
        self, organization_id: Union[UUID, str], scan_target_group_id: Union[UUID, str]
    ) -> Dict:
        """
        Get scan target group of organization.
        <https://api.zanshin.tenchisecurity.com/#operation/getOrganizationScanTargetGroupById>
        :param scan_target_group_id:
        :param organization_id: the ID of the organization
        :return: a dict representing the scan target group
        """
        return self._request(
            "GET",
            f"/organizations/{validate_uuid(organization_id)}/scantargetgroups/"
            f"{validate_uuid(scan_target_group_id)}",
        ).json()

    def create_scan_target_group(
        self, organization_id: Union[UUID, str], kind: ScanTargetKind, name: str
    ) -> Dict:
        """
        Create a new scan target group.
        <https://api.zanshin.tenchisecurity.com/#operation/createOrganizationScanTargetGroup>
        :param organization_id: the ID of the organization
        :param kind: The type of cloud of this scan target group
        :param name: the name of the scan target group
        :return: a dict representing the newly created scan target group
        """
        validate_class(kind, ScanTargetKind)
        validate_class(name, str)
        group_kinds = [member.value for member in ScanTargetGroupKind]

        if kind not in group_kinds:
            raise ValueError(
                f"{repr(kind.value)} is not accepted. '{group_kinds}' is expected"
            )

        body = {
            "name": name,
            "kind": kind,
        }

        return self._request(
            "POST",
            f"/organizations/{validate_uuid(organization_id)}/scantargetgroups",
            body=body,
        ).json()

    def update_scan_target_group(
        self,
        organization_id: Union[UUID, str],
        scan_target_group_id: Union[UUID, str],
        name: str,
    ) -> Dict:
        """
        Update scan target group.
        <https://api.zanshin.tenchisecurity.com/#operation/UpdateOrganizationScanTargetGroup>
        :param scan_target_group_id: the ID of the scan target group
        :param name: The scan target group assigned name
        :param organization_id: the ID of the organization
        :return: a dict representing the scan target group
        """

        body = {"name": name}

        return self._request(
            "PUT",
            f"/organizations/{validate_uuid(organization_id)}/scantargetgroups/"
            f"{validate_uuid(scan_target_group_id)}",
            body=body,
        ).json()

    def iter_scan_target_group_compartments(
        self, organization_id: Union[UUID, str], scan_target_group_id: Union[UUID, str]
    ) -> Iterator[Dict]:
        """
        Iterates over the compartments of a scan target group.
        <https://api.zanshin.tenchisecurity.com/#operation/getOrganizationComapartmentsFromScanTargetGroup>
        :param organization_id: the ID of the organization
        :param scan_target_group_id: the ID of the scan target group
        :return: an iterator over the compartments of a scan target group
        """
        yield from self._request(
            "GET",
            f"/organizations/{validate_uuid(organization_id)}/scantargetgroups/"
            f"{validate_uuid(scan_target_group_id)}/targets",
        ).json()

    def get_scan_target_group_script(
        self, organization_id: Union[UUID, str], scan_target_group_id: Union[UUID, str]
    ) -> Dict:
        """
        Get the terraform download URL of the scan target group.
        <https://api.zanshin.tenchisecurity.com/#operation/getOrganizationScanTargetGroupScrip>
        :param organization_id: the ID of the organization
        :param scan_target_group_id: the ID of the scan target group
        :return: Scan target group terraform URL
        """
        return self._request(
            "GET",
            f"/organizations/{validate_uuid(organization_id)}/scantargetgroups/"
            f"{validate_uuid(scan_target_group_id)}/scripts",
        ).json()

    def iter_scan_targets_from_group(
        self, organization_id: Union[UUID, str], scan_target_group_id: Union[UUID, str]
    ) -> Iterator[Dict]:
        """
        Iterates over the scan targets of a group.
        <https://api.zanshin.tenchisecurity.com/#operation/getOrganizationScanTargetFromScanTargetGroup>
        :param organization_id: the ID of the organization
        :param scan_target_group_id: the ID of the scan target group
        :return: an iterator over scan targets of a group
        """
        yield from self._request(
            "GET",
            f"/organizations/{validate_uuid(organization_id)}/scantargetgroups/"
            f"{validate_uuid(scan_target_group_id)}/scantargets",
        ).json()

    def delete_organization_scan_target_group(
        self, organization_id: Union[UUID, str], scan_target_group_id: Union[UUID, str]
    ) -> bool:
        """
        Delete scan target group of organization.
        <https://api.zanshin.tenchisecurity.com/#operation/deleteOrganizationScanTargetGroupById>
        :param organization_id: the ID of the organization
        :param scan_target_group_id:
        :return: a boolean if success
        """
        return self._request(
            "DELETE",
            f"/organizations/{validate_uuid(organization_id)}/scantargetgroups/"
            f"{validate_uuid(scan_target_group_id)}",
        ).json()

    def insert_scan_target_group_credential(
        self,
        organization_id: Union[UUID, str],
        scan_target_group_id: Union[UUID, str],
        credential: ScanTargetGroupCredentialListORACLE,
    ) -> Dict:
        """
        Insert an already created scan target group.
        <https://api.zanshin.tenchisecurity.com/#operation/UpdateOrganizationScanTargetGroupCredential>
        :param organization_id: the ID of the organization
        :param scan_target_group_id: the ID of the scan target group
        :param credential: scan target group credential oracle
        :return: a dict representing scan target group
        """

        validate_class(credential, ScanTargetGroupCredentialListORACLE)

        body = {
            "credential": credential,
        }
        return self._request(
            "POST",
            f"/organizations/{validate_uuid(organization_id)}/scantargetgroups/"
            f"{validate_uuid(scan_target_group_id)}",
            body=body,
        ).json()

    def create_scan_target_by_compartments(
        self,
        organization_id: Union[UUID, str],
        scan_target_group_id: Union[UUID, str],
        name: str,
        ocid: str,
    ) -> Dict:
        """
        Create Scan Targets from previous listed compartments inside the scan target group.
        <https://api.zanshin.tenchisecurity.com/#operation/createOrganizationScanTargetByCompartments>
        :param organization_id: the ID of the organization
        :param scan_target_group_id: the ID of the scan target group
        :param ocid: Oracle Compartment Id
        :param name: the name of the scan target group
        :return: a dict representing the scan target
        """
        validate_class(ocid, str)
        validate_class(name, str)

        compartments = [{"name": name, "ocid": ocid}]

        body = {"compartments": compartments}
        return self._request(
            "POST",
            f"/organizations/{validate_uuid(organization_id)}/scantargetgroups/"
            f"{validate_uuid(scan_target_group_id)}/targets",
            body=body,
        ).json()

    ###################################################
    # Alerts
    ###################################################

    def _get_alerts_page(
        self,
        organization_id: Union[UUID, str],
        scan_target_ids: Optional[Iterable[Union[UUID, str]]] = None,
        scan_target_tags: Optional[Iterable[str]] = None,
        include_empty_scan_target_tags: Optional[bool] = None,
        rules: Optional[Iterable[str]] = None,
        states: Optional[Iterable[AlertState]] = None,
        severities: Optional[Iterable[AlertSeverity]] = None,
        lang: Optional[Languages] = None,
        opened_at_start: Optional[str] = None,
        opened_at_end: Optional[str] = None,
        resolved_at_start: Optional[str] = None,
        resolved_at_end: Optional[str] = None,
        created_at_start: Optional[str] = None,
        created_at_end: Optional[str] = None,
        updated_at_start: Optional[str] = None,
        updated_at_end: Optional[str] = None,
        search: Optional[str] = None,
        cursor: Optional[str] = None,
        order: Optional[AlertsOrderOpts] = None,
        sort: Optional[SortOpts] = None,
    ) -> Dict:
        """
        Internal method to retrieve a single page of alerts from an organization
        :param organization_id: the ID of the organization
        :param scan_target_ids: optional list of scan target IDs to list alerts from, defaults to all
        :param scan_target_tags: optional list of scan target tags to list alerts from
        :param include_empty_scan_target_tags: optional boolean to include scan targets without tags
        :param rules: list of rules to filter alerts, not passing the field will fetch all
        :param states: optional list of states to filter returned alerts, defaults to all
        :param severities: optional list of severities to filter returned alerts, defaults to all
        :param lang: language the rule will be returned. Ignored when historical is enabled
        :param opened_at_start: Search alerts by opened date - greater or equals than
        :param opened_at_end: Search alerts by opened date - less or equals than
        :param resolved_at_start: Search alerts by resolved date - greater or equals than
        :param resolved_at_end: Search alerts by resolved date - less or equals than
        :param created_at_start: Search alerts by creation date - greater or equals than
        :param created_at_end: Search alerts by creation date - less or equals than
        :param updated_at_start: Search alerts by update date - greater or equals than
        :param updated_at_end: Search alerts by update date - less or equals than
        :param cursor: Cursor of the last alert consumed, when this value is passed, subsequent alert histories will be returned.
        :param order: Sort order to use (ascending or descending)
        :param sort: Which field to sort on
        :return: a JSON decoded alerts
        :return:
        """
        body = {}
        params = {}
        if cursor:
            validate_class(cursor, str)
            params["cursor"] = cursor
        if order:
            validate_class(order, AlertsOrderOpts)
            body["order"] = order.value
        if search:
            validate_class(search, str)
            body["search"] = search
        if sort:
            validate_class(sort, SortOpts)
            body["sort"] = sort.value
        if scan_target_ids:
            if isinstance(scan_target_ids, str):
                scan_target_ids = [scan_target_ids]
            validate_class(scan_target_ids, Iterable)
            body["scanTargetIds"] = [validate_uuid(x) for x in scan_target_ids]
        if scan_target_tags:
            if isinstance(scan_target_tags, str):
                scan_target_tags = [scan_target_tags]
            validate_class(scan_target_tags, Iterable)
            body["scanTargetTags"] = [validate_uuid(x) for x in scan_target_tags]
        if include_empty_scan_target_tags is not None:
            validate_class(include_empty_scan_target_tags, bool)
            body["includeEmptyScanTargetTags"] = include_empty_scan_target_tags
        if rules:
            body["rules"] = [validate_class(rule, str) for rule in rules]
        if states:
            if isinstance(states, str) or isinstance(states, AlertState):
                states = [states]
            validate_class(states, Iterable)
            body["states"] = [
                validate_class(state, AlertState).value for state in states
            ]
        if severities:
            if isinstance(severities, str):
                severities = [severities]
            validate_class(severities, Iterable)
            body["severities"] = [
                validate_class(severity, AlertSeverity).value for severity in severities
            ]
        if lang:
            validate_class(lang, Languages)
            body["lang"] = lang.value
        if opened_at_start:
            body["openedAtStart"] = validate_date(opened_at_start).isoformat()
        if opened_at_end:
            body["openedAtEnd"] = validate_date(opened_at_end).isoformat()
        if resolved_at_start:
            body["resolvedAtStart"] = validate_date(resolved_at_start).isoformat()
        if resolved_at_end:
            body["resolvedAtEnd"] = validate_date(resolved_at_end).isoformat()
        if created_at_start:
            body["createdAtStart"] = validate_date(created_at_start).isoformat()
        if created_at_end:
            body["createdAtEnd"] = validate_date(created_at_end).isoformat()
        if updated_at_start:
            body["updatedAtStart"] = validate_date(updated_at_start).isoformat()
        if updated_at_end:
            body["updatedAtEnd"] = validate_date(updated_at_end).isoformat()
        return self._request(
            "POST",
            f"/organizations/{validate_uuid(organization_id)}/alerts",
            body=body,
            params=params,
        ).json()

    def iter_alerts(
        self,
        organization_id: Union[UUID, str],
        scan_target_ids: Optional[Iterable[Union[UUID, str]]] = None,
        scan_target_tags: Optional[Iterable[str]] = None,
        include_empty_scan_target_tags: Optional[bool] = None,
        rules: Optional[Iterable[str]] = None,
        states: Optional[Iterable[AlertState]] = None,
        severities: Optional[Iterable[AlertSeverity]] = None,
        lang: Optional[Languages] = None,
        opened_at_start: Optional[str] = None,
        opened_at_end: Optional[str] = None,
        resolved_at_start: Optional[str] = None,
        resolved_at_end: Optional[str] = None,
        created_at_start: Optional[str] = None,
        created_at_end: Optional[str] = None,
        updated_at_start: Optional[str] = None,
        updated_at_end: Optional[str] = None,
        search: Optional[str] = None,
        cursor: Optional[str] = None,
        order: Optional[AlertsOrderOpts] = None,
        sort: Optional[SortOpts] = None,
    ) -> Iterator[Dict]:
        """
        Iterates over the alerts of an organization by loading them, transparently paginating on the API
        :param organization_id: the ID of the organization
        :param scan_target_ids: optional list of scan target IDs to list alerts from, defaults to all
        :param scan_target_tags: optional list of scan target tags to list alerts from
        :param include_empty_scan_target_tags: optional boolean to include scan targets without tags
        :param rules: list of rules to filter alerts, not passing the field will fetch all
        :param states: optional list of states to filter returned alerts, defaults to all
        :param severities: optional list of severities to filter returned alerts, defaults to all
        :param lang: language the rule will be returned. Ignored when historical is enabled
        :param opened_at_start: Search alerts by opened date - greater or equals than
        :param opened_at_end: Search alerts by opened date - less or equals than
        :param resolved_at_start: Search alerts by resolved date - greater or equals than
        :param resolved_at_end: Search alerts by resolved date - less or equals than
        :param created_at_start: Search alerts by creation date - greater or equals than
        :param created_at_end: Search alerts by creation date - less or equals than
        :param updated_at_start: Search alerts by update date - greater or equals than
        :param updated_at_end: Search alerts by update date - less or equals than
        :param cursor: Cursor of the last alert consumed, when this value is passed, subsequent alert histories will be returned.
        :param order: Sort order to use (ascending or descending)
        :param sort: Which field to sort on
        :return: an iterator over the JSON decoded alerts
        """
        page = self._get_alerts_page(
            organization_id,
            scan_target_ids,
            scan_target_tags=scan_target_tags,
            include_empty_scan_target_tags=include_empty_scan_target_tags,
            cursor=cursor,
            order=order,
            rules=rules,
            states=states,
            severities=severities,
            lang=lang,
            opened_at_start=opened_at_start,
            opened_at_end=opened_at_end,
            resolved_at_start=resolved_at_start,
            resolved_at_end=resolved_at_end,
            created_at_start=created_at_start,
            created_at_end=created_at_end,
            updated_at_start=updated_at_start,
            updated_at_end=updated_at_end,
            search=search,
            sort=sort,
        )
        yield from page.get("data", [])
        while page.get("cursor"):
            page = self._get_alerts_page(
                organization_id,
                scan_target_ids,
                scan_target_tags=scan_target_tags,
                include_empty_scan_target_tags=include_empty_scan_target_tags,
                cursor=page.get("cursor"),
                order=order,
                rules=rules,
                states=states,
                severities=severities,
                lang=lang,
                opened_at_start=opened_at_start,
                opened_at_end=opened_at_end,
                resolved_at_start=resolved_at_start,
                resolved_at_end=resolved_at_end,
                created_at_start=created_at_start,
                created_at_end=created_at_end,
                updated_at_start=updated_at_start,
                updated_at_end=updated_at_end,
                search=search,
                sort=sort,
            )
            yield from page.get("data", [])

    def _get_following_alerts_page(
        self,
        organization_id: Union[UUID, str],
        following_ids: Optional[Iterable[Union[UUID, str]]] = None,
        following_tags: Optional[Iterable[str]] = None,
        include_empty_following_tags: Optional[bool] = None,
        rules: Optional[Iterable[str]] = None,
        states: Optional[Iterable[AlertState]] = None,
        severities: Optional[Iterable[AlertSeverity]] = None,
        lang: Optional[Languages] = None,
        opened_at_start: Optional[str] = None,
        opened_at_end: Optional[str] = None,
        resolved_at_start: Optional[str] = None,
        resolved_at_end: Optional[str] = None,
        created_at_start: Optional[str] = None,
        created_at_end: Optional[str] = None,
        updated_at_start: Optional[str] = None,
        updated_at_end: Optional[str] = None,
        search: Optional[str] = None,
        cursor: Optional[str] = None,
        order: Optional[AlertsOrderOpts] = None,
        sort: Optional[SortOpts] = None,
    ) -> Dict:
        """
        Internal method to retrieve a single page of alerts from organizations being followed
        :param organization_id: the ID of the organization
        :param following_ids: optional list of scan target IDs to list alerts from, defaults to all
        :param following_tags: optional boolean to include followings without tags
        :param include_empty_following_tags: optional boolean to include followings without tags
        :param rules: list of rules to filter alerts, not passing the field will fetch all
        :param states: optional list of states to filter returned alerts, defaults to all
        :param severities: optional list of severities to filter returned alerts, defaults to all
        :param lang: language the rule will be returned. Ignored when historical is enabled
        :param opened_at_start: Search alerts by opened date - greater or equals than
        :param opened_at_end: Search alerts by opened date - less or equals than
        :param resolved_at_start: Search alerts by resolved date - greater or equals than
        :param resolved_at_end: Search alerts by resolved date - less or equals than
        :param created_at_start: Search alerts by creation date - greater or equals than
        :param created_at_end: Search alerts by creation date - less or equals than
        :param updated_at_start: Search alerts by update date - greater or equals than
        :param updated_at_end: Search alerts by update date - less or equals than
        :param cursor: Cursor of the last alert consumed, when this value is passed, subsequent alert histories will be returned.
        :param order: Sort order to use based on alert order opts
        :param sort: Which field to sort on
        :return: a JSON decoded following alerts
        """
        body = {}
        params = {}
        if cursor:
            validate_class(cursor, str)
            params["cursor"] = cursor
        if order:
            validate_class(order, AlertsOrderOpts)
            body["order"] = order.value
        if search:
            validate_class(search, str)
            body["search"] = search
        if sort:
            validate_class(sort, SortOpts)
            body["sort"] = sort.value
        if following_ids:
            if isinstance(following_ids, str):
                following_ids = [following_ids]
            validate_class(following_ids, Iterable)
            body["followingIds"] = [validate_uuid(x) for x in following_ids]
        if following_tags:
            if isinstance(following_tags, str):
                following_tags = [following_tags]
            validate_class(following_tags, Iterable)
            body["followingTags"] = [validate_uuid(x) for x in following_tags]
        if include_empty_following_tags is not None:
            validate_class(include_empty_following_tags, bool)
            body["includeEmptyFollowingTags"] = include_empty_following_tags
        if rules:
            body["rules"] = [validate_class(rule, str) for rule in rules]
        if states:
            if isinstance(states, str) or isinstance(states, AlertState):
                states = [states]
            validate_class(states, Iterable)
            body["states"] = [
                validate_class(state, AlertState).value for state in states
            ]
        if severities:
            if isinstance(severities, str):
                severities = [severities]
            validate_class(severities, Iterable)
            body["severities"] = [
                validate_class(severity, AlertSeverity).value for severity in severities
            ]
        if lang:
            validate_class(lang, Languages)
            body["lang"] = lang.value
        if opened_at_start:
            body["openedAtStart"] = validate_date(opened_at_start).isoformat()
        if opened_at_end:
            body["openedAtEnd"] = validate_date(opened_at_end).isoformat()
        if resolved_at_start:
            body["resolvedAtStart"] = validate_date(resolved_at_start).isoformat()
        if resolved_at_end:
            body["resolvedAtEnd"] = validate_date(resolved_at_end).isoformat()
        if created_at_start:
            body["createdAtStart"] = validate_date(created_at_start).isoformat()
        if created_at_end:
            body["createdAtEnd"] = validate_date(created_at_end).isoformat()
        if updated_at_start:
            body["updatedAtStart"] = validate_date(updated_at_start).isoformat()
        if updated_at_end:
            body["updatedAtEnd"] = validate_date(updated_at_end).isoformat()
        return self._request(
            "POST",
            f"/organizations/{validate_uuid(organization_id)}/followings/alerts",
            body=body,
            params=params,
        ).json()

    def iter_following_alerts(
        self,
        organization_id: Union[UUID, str],
        following_ids: Optional[Iterable[Union[UUID, str]]] = None,
        following_tags: Optional[Iterable[str]] = None,
        include_empty_following_tags: Optional[bool] = None,
        rules: Optional[Iterable[str]] = None,
        states: Optional[Iterable[AlertState]] = None,
        severities: Optional[Iterable[AlertSeverity]] = None,
        lang: Optional[Languages] = None,
        opened_at_start: Optional[str] = None,
        opened_at_end: Optional[str] = None,
        resolved_at_start: Optional[str] = None,
        resolved_at_end: Optional[str] = None,
        created_at_start: Optional[str] = None,
        created_at_end: Optional[str] = None,
        updated_at_start: Optional[str] = None,
        updated_at_end: Optional[str] = None,
        search: Optional[str] = None,
        cursor: Optional[str] = None,
        order: Optional[AlertsOrderOpts] = None,
        sort: Optional[SortOpts] = None,
    ) -> Iterator[Dict]:
        """
        Iterates over the following alerts from organizations being followed by transparently paginating on the API.
        :param organization_id: the ID of the organization
        :param following_ids: optional list of scan target IDs to list alerts from, defaults to all
        :param following_tags: optional boolean to include followings without tags
        :param include_empty_following_tags: optional boolean to include followings without tags
        :param rules: list of rules to filter alerts, not passing the field will fetch all
        :param states: optional list of states to filter returned alerts, defaults to all
        :param severities: optional list of severities to filter returned alerts, defaults to all
        :param lang: language the rule will be returned. Ignored when historical is enabled
        :param opened_at_start: Search alerts by opened date - greater or equals than
        :param opened_at_end: Search alerts by opened date - less or equals than
        :param resolved_at_start: Search alerts by resolved date - greater or equals than
        :param resolved_at_end: Search alerts by resolved date - less or equals than
        :param created_at_start: Search alerts by creation date - greater or equals than
        :param created_at_end: Search alerts by creation date - less or equals than
        :param updated_at_start: Search alerts by update date - greater or equals than
        :param updated_at_end: Search alerts by update date - less or equals than
        :param cursor: Cursor of the last alert consumed, when this value is passed, subsequent alert histories will be returned.
        :param order: Sort order to use based od alert order opts
        :param sort: Which field to sort on
        :return: an iterator over the JSON decoded alerts
        """
        page = self._get_following_alerts_page(
            organization_id,
            following_ids,
            following_tags=following_tags,
            include_empty_following_tags=include_empty_following_tags,
            cursor=cursor,
            order=order,
            rules=rules,
            states=states,
            severities=severities,
            lang=lang,
            opened_at_start=opened_at_start,
            opened_at_end=opened_at_end,
            resolved_at_start=resolved_at_start,
            resolved_at_end=resolved_at_end,
            created_at_start=created_at_start,
            created_at_end=created_at_end,
            updated_at_start=updated_at_start,
            updated_at_end=updated_at_end,
            search=search,
            sort=sort,
        )
        yield from page.get("data", [])
        while page.get("cursor"):
            page = self._get_following_alerts_page(
                organization_id,
                following_ids,
                following_tags=following_tags,
                include_empty_following_tags=include_empty_following_tags,
                cursor=page.get("cursor"),
                order=order,
                rules=rules,
                states=states,
                severities=severities,
                lang=lang,
                opened_at_start=opened_at_start,
                opened_at_end=opened_at_end,
                resolved_at_start=resolved_at_start,
                resolved_at_end=resolved_at_end,
                created_at_start=created_at_start,
                created_at_end=created_at_end,
                updated_at_start=updated_at_start,
                updated_at_end=updated_at_end,
                search=search,
                sort=sort,
            )
            yield from page.get("data", [])

    def _get_alerts_history_page(
        self,
        organization_id: Union[UUID, str],
        scan_target_ids: Optional[Iterable[Union[UUID, str]]] = None,
        page_size: int = 100,
        language: Optional[Iterable[Languages]] = None,
        cursor: Optional[str] = None,
    ) -> Dict:
        """
        Internal method to retrieve a single page of alerts history from an organization
        :param organization_id: the ID of the organization
        :param scan_target_ids: optional list of scan target IDs to list alerts from, defaults to all
        :param page_size: page size of alerts
        :param language: language the rule will be returned
        :param cursor: Alert Cursor of the last alert consumed, when this value is passed, subsequent alert histories
               will be returned.
        :return: an iterator over the JSON decoded alerts
        :return:
        """
        validate_int(page_size, min_value=1, required=True)
        body = {"organizationId": validate_uuid(organization_id), "pageSize": page_size}

        if scan_target_ids:
            if isinstance(scan_target_ids, str):
                scan_target_ids = [scan_target_ids]
            validate_class(scan_target_ids, Iterable)
            body["scanTargetIds"] = [validate_uuid(x) for x in scan_target_ids]
        if language:
            validate_class(language, Languages)
            body["lang"] = language.value
        if cursor:
            body["cursor"] = cursor

        return self._request("POST", "/alerts/history", body=body).json()

    def iter_alerts_history(
        self,
        organization_id: Union[UUID, str],
        scan_target_ids: Optional[Iterable[Union[UUID, str]]] = None,
        page_size: int = 100,
        language: Optional[Languages] = None,
        cursor: Optional[str] = None,
    ) -> Iterator[Dict]:
        """
        Iterates over the alert's history of an organization by loading them, transparently paginating on the API.
        <https://api.zanshin.tenchisecurity.com/#operation/listAllAlertsHistory>
        :param organization_id: the ID of the organization
        :param scan_target_ids: optional list of scan target IDs to list alerts from, defaults to all
        :param page_size: the number of alerts to load from the API at a time
        :param language: language the rule will be returned.
        :param cursor: Alert Cursor of the last alert consumed, when this value is passed, subsequent alert histories
               will be returned.
        :return: an iterator over the JSON decoded alerts
        """

        page = self._get_alerts_history_page(
            organization_id,
            scan_target_ids,
            page_size=page_size,
            language=language,
            cursor=cursor,
        )
        data = page.get("data", [])
        yield from data

        while len(data) > 0:
            cursor = data[len(data) - 1]["cursor"]
            page = self._get_alerts_history_page(
                organization_id,
                scan_target_ids,
                page_size=page_size,
                language=language,
                cursor=cursor,
            )
            data = page.get("data", [])
            yield from data

    def _get_alerts_following_history_page(
        self,
        organization_id: Union[UUID, str],
        following_ids: Optional[Iterable[Union[UUID, str]]] = None,
        page_size: int = 100,
        language: Optional[Languages] = None,
        cursor: Optional[str] = None,
    ) -> Dict:
        """
        Internal method to retrieve a single page of alerts history from an organization
        :param organization_id: the ID of the organization
        :param following_ids: optional list of IDs of organizations you are following to list alerts from, defaults to
               all
        :param page_size: page size of alerts
        :param language: language the rule will be returned
        :param cursor: Alert Cursor of the last alert consumed, when this value is passed, subsequent alert histories
               will be returned.
        :return: an iterator over the JSON decoded alerts
        :return:
        """
        validate_int(page_size, min_value=1, required=True)
        body = {"organizationId": validate_uuid(organization_id), "pageSize": page_size}

        if following_ids:
            if isinstance(following_ids, str):
                following_ids = [following_ids]
            validate_class(following_ids, Iterable)
            body["followingIds"] = [validate_uuid(x) for x in following_ids]
        if language:
            validate_class(language, Languages)
            body["lang"] = language.value
        if cursor:
            body["cursor"] = cursor

        return self._request("POST", "/alerts/history/following", body=body).json()

    def iter_alerts_following_history(
        self,
        organization_id: Union[UUID, str],
        following_ids: Optional[Iterable[Union[UUID, str]]] = None,
        page_size: int = 100,
        language: Optional[Languages] = None,
        cursor: Optional[str] = None,
    ) -> Iterator[Dict]:
        """
        Iterates over the alert's history of an organization by loading them, transparently paginating on the API
        <https://api.zanshin.tenchisecurity.com/#operation/listAllAlertsHistoryFollowing>
        :param organization_id: the ID of the organization
        :param following_ids: optional list of IDs of organizations you are following to list alerts from, defaults to
               all
        :param page_size: the number of alerts to load from the API at a time
        :param language: language the rule will be returned. Ignored when historical is enabled
        :param cursor: Alert Cursor of the last alert consumed, when this value is passed, subsequent alert histories
               will be returned
        :return: an iterator over the JSON decoded alerts
        """
        page = self._get_alerts_following_history_page(
            organization_id,
            following_ids,
            page_size=page_size,
            language=language,
            cursor=cursor,
        )
        data = page.get("data", [])
        yield from data

        while len(data) > 0:
            cursor = data[len(data) - 1]["cursor"]
            page = self._get_alerts_following_history_page(
                organization_id,
                following_ids,
                page_size=page_size,
                language=language,
                cursor=cursor,
            )
            data = page.get("data", [])
            yield from data

    def _get_grouped_alerts_page(
        self,
        organization_id: Union[UUID, str],
        scan_target_ids: Optional[Iterable[Union[UUID, str]]] = None,
        scan_tagert_tags: Optional[Iterable[str]] = None,
        include_empty_scan_target_tags: Optional[bool] = None,
        rules: Optional[Iterable[str]] = None,
        states: Optional[Iterable[AlertState]] = None,
        severities: Optional[Iterable[AlertSeverity]] = None,
        lang: Optional[Languages] = None,
        opened_at_start: Optional[str] = None,
        opened_at_end: Optional[str] = None,
        resolved_at_start: Optional[str] = None,
        resolved_at_end: Optional[str] = None,
        created_at_start: Optional[str] = None,
        created_at_end: Optional[str] = None,
        updated_at_start: Optional[str] = None,
        updated_at_end: Optional[str] = None,
        search: Optional[str] = None,
        cursor: Optional[str] = None,
        page_size: Optional[int] = 100,
        order: Optional[GroupedAlertOrderOpts] = None,
        sort: Optional[SortOpts] = None,
    ) -> Dict:
        """
        Internal method to retrieve a single page of alerts from an organization
        :param organization_id: the ID of the organization
        :param scan_target_ids: optional list of scan target IDs to list alerts from, defaults to all
        :param states: optional list of states to filter returned alerts, defaults to all
        :param severities: optional list of severities to filter returned alerts, defaults to all
        :param page: page number, starting from 1
        :param page_size: page size of alerts
        :param language: language to use for the returned rules
        :param search: Search string to find in alerts
        :param order: Sort order to use (ascending or descending)
        :param sort: Which field to sort on

        :return:
        """
        body = validate_base_alert_filter(
            body={},
            rules=rules,
            states=states,
            severities=severities,
            search=search,
            lang=lang,
            opened_at_start=opened_at_start,
            opened_at_end=opened_at_end,
            resolved_at_start=resolved_at_start,
            resolved_at_end=resolved_at_end,
            created_at_start=created_at_start,
            created_at_end=created_at_end,
            updated_at_start=updated_at_start,
            updated_at_end=updated_at_end,
            sort=sort,
        )
        params = {}
        if page_size:
            validate_int(page_size, min_value=1, required=True)
            params["pageSize"] = page_size
        if order:
            validate_class(order, GroupedAlertOrderOpts)
            body["order"] = order.value
        if cursor:
            validate_class(cursor, str)
            params["cursor"] = cursor
        if scan_target_ids:
            if isinstance(scan_target_ids, str):
                scan_target_ids = [scan_target_ids]
            validate_class(scan_target_ids, Iterable)
            body["scanTargetIds"] = [validate_uuid(x) for x in scan_target_ids]
        if scan_tagert_tags:
            if isinstance(scan_tagert_tags, str):
                scan_tagert_tags = [scan_tagert_tags]
            validate_class(scan_tagert_tags, Iterable)
            body["scanTargetTags"] = [validate_uuid(x) for x in scan_tagert_tags]
        if include_empty_scan_target_tags is not None:
            validate_class(include_empty_scan_target_tags, bool)
            body["includeEmptyScanTargetTags"] = include_empty_scan_target_tags
        return self._request(
            "POST",
            f"/organizations/{validate_uuid(organization_id)}/alerts/rules",
            body=body,
            params=params,
        ).json()

    def iter_grouped_alerts(
        self,
        organization_id: Union[UUID, str],
        scan_target_ids: Optional[Iterable[Union[UUID, str]]] = None,
        scan_tagert_tags: Optional[Iterable[str]] = None,
        include_empty_scan_target_tags: Optional[bool] = None,
        rules: Optional[Iterable[str]] = None,
        states: Optional[Iterable[AlertState]] = None,
        severities: Optional[Iterable[AlertSeverity]] = None,
        lang: Optional[Languages] = None,
        opened_at_start: Optional[str] = None,
        opened_at_end: Optional[str] = None,
        resolved_at_start: Optional[str] = None,
        resolved_at_end: Optional[str] = None,
        created_at_start: Optional[str] = None,
        created_at_end: Optional[str] = None,
        updated_at_start: Optional[str] = None,
        updated_at_end: Optional[str] = None,
        search: Optional[str] = None,
        cursor: Optional[str] = None,
        page_size: Optional[int] = 100,
        order: Optional[GroupedAlertOrderOpts] = None,
        sort: Optional[SortOpts] = None,
    ) -> Iterator[Dict]:
        """
        Iterates over the grouped alerts of an organization by loading them, transparently paginating on the API.
        <https://api.zanshin.tenchisecurity.com/#operation/listAllAlertRules>
        :param organization_id: the ID of the organization
        :param scan_target_ids: optional list of scan target IDs to list alerts from, defaults to all
        :param scan_target_tags: optional list of scan target tags to list alerts from
        :param include_empty_scan_target_tags: optional boolean to include scan targets without tags
        :param rules: list of rules to filter alerts, not passing the field will fetch all
        :param states: optional list of states to filter returned alerts, defaults to all
        :param severities: optional list of severities to filter returned alerts, defaults to all
        :param lang: language the rule will be returned. Ignored when historical is enabled
        :param opened_at_start: Search alerts by opened date - greater or equals than
        :param opened_at_end: Search alerts by opened date - less or equals than
        :param resolved_at_start: Search alerts by resolved date - greater or equals than
        :param resolved_at_end: Search alerts by resolved date - less or equals than
        :param created_at_start: Search alerts by creation date - greater or equals than
        :param created_at_end: Search alerts by creation date - less or equals than
        :param updated_at_start: Search alerts by update date - greater or equals than
        :param updated_at_end: Search alerts by update date - less or equals than
        :param cursor: Cursor of the last alert consumed, when this value is passed, subsequent alert histories will be returned.
        :param order: Sort order to use (ascending or descending)
        :param sort: Which field to sort on
        :return: an iterator over the JSON decoded alerts
        """
        page = self._get_grouped_alerts_page(
            organization_id,
            scan_target_ids=scan_target_ids,
            scan_tagert_tags=scan_tagert_tags,
            include_empty_scan_target_tags=include_empty_scan_target_tags,
            cursor=cursor,
            page_size=page_size,
            order=order,
            rules=rules,
            states=states,
            severities=severities,
            lang=lang,
            opened_at_start=opened_at_start,
            opened_at_end=opened_at_end,
            resolved_at_start=resolved_at_start,
            resolved_at_end=resolved_at_end,
            created_at_start=created_at_start,
            created_at_end=created_at_end,
            updated_at_start=updated_at_start,
            updated_at_end=updated_at_end,
            search=search,
            sort=sort,
        )
        yield from page.get("data", [])
        while page.get("cursor"):
            page = self._get_grouped_alerts_page(
                organization_id,
                scan_target_ids,
                scan_tagert_tags=scan_tagert_tags,
                include_empty_scan_target_tags=include_empty_scan_target_tags,
                cursor=page.get("cursor"),
                page_size=page_size,
                order=order,
                rules=rules,
                states=states,
                severities=severities,
                lang=lang,
                opened_at_start=opened_at_start,
                opened_at_end=opened_at_end,
                resolved_at_start=resolved_at_start,
                resolved_at_end=resolved_at_end,
                created_at_start=created_at_start,
                created_at_end=created_at_end,
                updated_at_start=updated_at_start,
                updated_at_end=updated_at_end,
                search=search,
                sort=sort,
            )
            yield from page.get("data", [])

    def _get_grouped_following_alerts_page(
        self,
        organization_id: Union[UUID, str],
        following_ids: Optional[Iterable[Union[UUID, str]]] = None,
        following_tags: Optional[Iterable[str]] = None,
        include_empty_following_tags: Optional[bool] = None,
        rules: Optional[Iterable[str]] = None,
        states: Optional[Iterable[AlertState]] = None,
        severities: Optional[Iterable[AlertSeverity]] = None,
        lang: Optional[Languages] = None,
        opened_at_start: Optional[str] = None,
        opened_at_end: Optional[str] = None,
        resolved_at_start: Optional[str] = None,
        resolved_at_end: Optional[str] = None,
        created_at_start: Optional[str] = None,
        created_at_end: Optional[str] = None,
        updated_at_start: Optional[str] = None,
        updated_at_end: Optional[str] = None,
        search: Optional[str] = None,
        cursor: Optional[str] = None,
        page_size: Optional[int] = 100,
        order: Optional[GroupedAlertOrderOpts] = None,
        sort: Optional[SortOpts] = None,
    ) -> Dict:
        """
        Internal method to retrieve a single page of alerts from organizations being followed
        :param organization_id: the ID of the organization
        :param following_ids: optional list of scan target IDs to list alerts from, defaults to all
        :param following_tags: optional boolean to include followings without tags
        :param include_empty_following_tags: optional boolean to include followings without tags
        :param rules: list of rules to filter alerts, not passing the field will fetch all
        :param states: optional list of states to filter returned alerts, defaults to all
        :param severities: optional list of severities to filter returned alerts, defaults to all
        :param lang: language the rule will be returned. Ignored when historical is enabled
        :param opened_at_start: Search alerts by opened date - greater or equals than
        :param opened_at_end: Search alerts by opened date - less or equals than
        :param resolved_at_start: Search alerts by resolved date - greater or equals than
        :param resolved_at_end: Search alerts by resolved date - less or equals than
        :param created_at_start: Search alerts by creation date - greater or equals than
        :param created_at_end: Search alerts by creation date - less or equals than
        :param updated_at_start: Search alerts by update date - greater or equals than
        :param updated_at_end: Search alerts by update date - less or equals than
        :param cursor: Cursor of the last alert consumed, when this value is passed, subsequent alert histories will be returned.
        :param order: Sort order to use (ascending or descending)
        :param cursor: Cursor of the last alert consumed, when this value is passed, subsequent alert histories will be returned.
        :param sort: Which field to sort on
        :return: the decoded JSON response from the API
        """
        body = validate_base_alert_filter(
            body={},
            rules=rules,
            states=states,
            severities=severities,
            search=search,
            lang=lang,
            opened_at_start=opened_at_start,
            opened_at_end=opened_at_end,
            resolved_at_start=resolved_at_start,
            resolved_at_end=resolved_at_end,
            created_at_start=created_at_start,
            created_at_end=created_at_end,
            updated_at_start=updated_at_start,
            updated_at_end=updated_at_end,
            sort=sort,
        )
        params = {
            "pageSize": page_size,
        }
        if order:
            validate_class(order, GroupedAlertOrderOpts)
            body["order"] = order.value
        if cursor:
            validate_class(cursor, str)
            params["cursor"] = cursor
        if following_ids:
            if isinstance(following_ids, str):
                following_ids = [following_ids]
            validate_class(following_ids, Iterable)
            body["followingIds"] = [validate_uuid(x) for x in following_ids]
        if following_tags:
            if isinstance(following_tags, str):
                following_tags = [following_tags]
            validate_class(following_tags, Iterable)
            body["followingTags"] = [validate_uuid(x) for x in following_tags]
        if include_empty_following_tags is not None:
            validate_class(include_empty_following_tags, bool)
            body["includeEmptyFollowingTags"] = include_empty_following_tags
        return self._request(
            "POST",
            f"/organizations/{validate_uuid(organization_id)}/followings/alerts/rules",
            body=body,
            params=params,
        ).json()

    def iter_grouped_following_alerts(
        self,
        organization_id: Union[UUID, str],
        following_ids: Optional[Iterable[Union[UUID, str]]] = None,
        following_tags: Optional[Iterable[str]] = None,
        include_empty_following_tags: Optional[bool] = None,
        rules: Optional[Iterable[str]] = None,
        states: Optional[Iterable[AlertState]] = None,
        severities: Optional[Iterable[AlertSeverity]] = None,
        lang: Optional[Languages] = None,
        opened_at_start: Optional[str] = None,
        opened_at_end: Optional[str] = None,
        resolved_at_start: Optional[str] = None,
        resolved_at_end: Optional[str] = None,
        created_at_start: Optional[str] = None,
        created_at_end: Optional[str] = None,
        updated_at_start: Optional[str] = None,
        updated_at_end: Optional[str] = None,
        search: Optional[str] = None,
        cursor: Optional[str] = None,
        page_size: Optional[int] = 100,
        order: Optional[GroupedAlertOrderOpts] = None,
        sort: Optional[SortOpts] = None,
    ) -> Iterator[Dict]:
        """
        Iterates over the grouped following alerts from organizations being followed by transparently paginating on the API.
        :param organization_id: the ID of the organization
        :param following_ids: optional list of scan target IDs to list alerts from, defaults to all
        :param following_tags: optional boolean to include followings without tags
        :param include_empty_following_tags: optional boolean to include followings without tags
        :param rules: list of rules to filter alerts, not passing the field will fetch all
        :param states: optional list of states to filter returned alerts, defaults to all
        :param severities: optional list of severities to filter returned alerts, defaults to all
        :param lang: language the rule will be returned. Ignored when historical is enabled
        :param opened_at_start: Search alerts by opened date - greater or equals than
        :param opened_at_end: Search alerts by opened date - less or equals than
        :param resolved_at_start: Search alerts by resolved date - greater or equals than
        :param resolved_at_end: Search alerts by resolved date - less or equals than
        :param created_at_start: Search alerts by creation date - greater or equals than
        :param created_at_end: Search alerts by creation date - less or equals than
        :param updated_at_start: Search alerts by update date - greater or equals than
        :param updated_at_end: Search alerts by update date - less or equals than
        :param cursor: Cursor of the last alert consumed, when this value is passed, subsequent alert histories will be returned.
        :param order: Sort order to use (ascending or descending)
        :param cursor: Cursor of the last alert consumed, when this value is passed, subsequent alert histories will be returned.
        :param sort: Which field to sort on
        """

        page = self._get_grouped_following_alerts_page(
            organization_id,
            following_ids,
            following_tags=following_tags,
            include_empty_following_tags=include_empty_following_tags,
            cursor=cursor,
            page_size=page_size,
            order=order,
            rules=rules,
            states=states,
            severities=severities,
            lang=lang,
            opened_at_start=opened_at_start,
            opened_at_end=opened_at_end,
            resolved_at_start=resolved_at_start,
            resolved_at_end=resolved_at_end,
            created_at_start=created_at_start,
            created_at_end=created_at_end,
            updated_at_start=updated_at_start,
            updated_at_end=updated_at_end,
            search=search,
            sort=sort,
        )
        yield from page.get("data", [])
        while page.get("cursor"):
            page = self._get_grouped_following_alerts_page(
                organization_id,
                following_ids,
                following_tags=following_tags,
                include_empty_following_tags=include_empty_following_tags,
                cursor=page.get("cursor"),
                page_size=page_size,
                order=order,
                rules=rules,
                states=states,
                severities=severities,
                lang=lang,
                opened_at_start=opened_at_start,
                opened_at_end=opened_at_end,
                resolved_at_start=resolved_at_start,
                resolved_at_end=resolved_at_end,
                created_at_start=created_at_start,
                created_at_end=created_at_end,
                updated_at_start=updated_at_start,
                updated_at_end=updated_at_end,
                search=search,
                sort=sort,
            )
            yield from page.get("data", [])

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
        yield from self._request(
            "GET", f"/alerts/{validate_uuid(alert_id)}/history"
        ).json()

    def _get_alert_comment_page(
        self,
        alert_id: Union[UUID, str],
        page: Optional[int] = 1,
        page_size: Optional[int] = 100,
    ) -> Dict:
        validate_int(page, min_value=1, required=True)
        validate_int(page_size, min_value=1, required=True)
        params = {"page": page, "pageSize": page_size}
        return self._request(
            "GET", f"/alerts/{validate_uuid(alert_id)}/comments", params=params
        ).json()

    def iter_alert_comments(
        self,
        alert_id: Union[UUID, str],
        page_size: Optional[int] = 100,
    ) -> Iterator[Dict]:
        """
        Iterates over the comment of an alert.
        <https://api.zanshin.tenchisecurity.com/#operation/listAllAlertComments>
        :param alert_id: the ID of the alert
        :return:
        """
        page = self._get_alert_comment_page(
            alert_id=alert_id, page_size=page_size, page=1
        )
        yield from page.get("data", [])
        for page_number in range(
            2, int(ceil(page.get("total", 0) / float(page_size))) + 1
        ):
            page = self._get_alert_comment_page(
                alert_id=alert_id,
                page_size=page_size,
                page=page_number,
            )
            yield from page.get("data", [])

    def update_alert(
        self,
        organization_id: Union[UUID, str],
        scan_target_id: Union[UUID, str],
        alert_id: Union[UUID, str],
        state: Optional[AlertState],
        labels: Optional[Iterable[str]],
        comment: Optional[str],
    ) -> Dict:
        """
        Update alert.
        <https://api.zanshin.tenchisecurity.com/#operation/editOrganizationScanTargetAlertById>
        :param comment:
        :param labels:
        :param state:
        :param scan_target_id:
        :param organization_id:
        :param alert_id: the ID of the alert
        :return: the decoded JSON object returned by the API
        """

        body = dict()
        if state:
            body["state"] = state

        if labels:
            body["labels"] = labels

        if comment:
            body["comment"] = comment

        return self._request(
            "PUT",
            f"/organizations/{validate_uuid(organization_id)}/scantargets/"
            f"{validate_uuid(scan_target_id)}/alerts/{validate_uuid(alert_id)}",
            body=body,
        ).json()

    def batch_update_alerts_state(
        self,
        organization_id: Union[UUID, str],
        state: AlertState,
        dry_run: bool,
        comment: str,
        scan_target_ids: Optional[Iterable[Union[UUID, str]]] = None,
        alert_ids: Optional[Iterable[str]] = None,
        states: Optional[Iterable[AlertState]] = None,
        rules: Optional[Iterable[str]] = None,
        severities: Optional[Iterable[str]] = None,
        include_empty_scan_target_tags: Optional[bool] = None,
    ) -> bool:
        body = {
            "state": validate_class(state, AlertState).value,
            "comment": validate_class(comment, str),
            "condition": {
                "dryRun": validate_class(dry_run, bool),
                "scanTargetIds": (
                    [
                        validate_uuid(scan_target_id)
                        for scan_target_id in scan_target_ids
                    ]
                    if scan_target_ids
                    else None
                ),
                "states": (
                    [validate_class(state, AlertState).value for state in states]
                    if states
                    else None
                ),
                "severities": (
                    [validate_class(severity, AlertSeverity) for severity in severities]
                    if severities
                    else None
                ),
                "selection": {
                    "rules": (
                        [validate_class(rule, str) for rule in rules] if rules else None
                    ),
                    "alertIds": (
                        [validate_uuid(alert_id) for alert_id in alert_ids]
                        if alert_ids
                        else None
                    ),
                },
                "includeEmptyScanTargetTags": (
                    validate_class(include_empty_scan_target_tags, bool)
                    if include_empty_scan_target_tags
                    else None
                ),
            },
        }
        return self._request(
            "PUT",
            f"/organizations/{validate_uuid(organization_id)}/alerts/status/batch",
            body=body,
        )

    def create_alert_comment(
        self,
        organization_id: Union[UUID, str],
        scan_target_id: Union[UUID, str],
        alert_id: Union[UUID, str],
        comment: str,
    ) -> Iterator[Dict]:
        """
        Iterates over the comment of an alert.
        <https://api.zanshin.tenchisecurity.com/#operation/listAllAlertComments>
        :param comment:
        :param organization_id: the ID of the organization
        :param scan_target_id: the ID of the scan target
        :param alert_id: the ID of the alert
        :return:
        """

        body = {"comment": comment}

        return self._request(
            "POST",
            f"/organizations/{validate_uuid(organization_id)}/scantargets/"
            f"{validate_uuid(scan_target_id)}/alerts/{validate_uuid(alert_id)}/comments",
            body=body,
        ).json()

    ###################################################
    # Summary
    ###################################################

    def get_following_scan_summaries(
        self,
        organization_id: Union[UUID, str],
        following_ids: Optional[Iterable[Union[UUID, str]]] = None,
        days: Optional[int] = 7,
    ) -> Dict:
        """
        Gets a summary of the current state of alerts for followed organizations.
        <https://api.zanshin.tenchisecurity.com/#operation/scanSummaryFollowing>
        :param organization_id:
        :param following_ids: list of IDs of organizations being followed to summarize alerts from
        :param days: number of days to go back in time in historical search
        :return: JSON object containing the scan summaries
        """

        body = {
            "organizationId": validate_uuid(organization_id),
            "daysBefore": validate_int(days, min_value=1),
        }

        if following_ids:
            if isinstance(following_ids, str):
                following_ids = [following_ids]
            validate_class(following_ids, Iterable)
            body["followingIds"] = [validate_uuid(x) for x in following_ids]

        return self._request(
            "POST", "/alerts/summaries/scans/following", body=body
        ).json()

    def get_scan_targets_following_summary(
        self,
        organization_id: Union[UUID, str],
        following_ids: Optional[Iterable[Union[UUID, str]]] = None,
        following_tags: Optional[Iterable[str]] = None,
        scan_target_kinds: Optional[Iterable[Union[ScanTargetKind, str]]] = None,
        alert_severities: Optional[Iterable[Union[AlertSeverity, str]]] = None,
        include_empty_following_tags: Optional[bool] = None,
    ) -> Dict:
        """
        Get scan target following summary.
        <https://api.zanshin.tenchisecurity.com/#tag/Summaries/operation/summaries_getScanTargetFollowingSummaryHandler>
        :param organization_id: the ID of the organization
        :param following_ids: optional list of IDs of organizations being followed
        :param following_tags: optional list of tags of followed scan targets
        :param scan_target_kinds: optional list of scan targets kinds (AWS, GCP, AZURE)
        :param alert_severities: optional list of severities
        :return: JSON object containing the following summaries
        """
        body = {}

        if following_ids:
            validate_class(following_ids, Iterable)
            body["followingIds"] = [
                validate_uuid(following_id) for following_id in following_ids
            ]

        if following_tags:
            validate_class(following_tags, Iterable)
            body["followingTags"] = [
                validate_class(following_tag, str) for following_tag in following_tags
            ]

        if scan_target_kinds:
            validate_class(scan_target_kinds, Iterable)
            body["scanTargetKinds"] = [
                validate_class(scan_target_kind, ScanTargetKind)
                for scan_target_kind in scan_target_kinds
            ]

        if alert_severities:
            validate_class(alert_severities, Iterable)
            body["alertSeverities"] = [
                validate_class(alert_severity, AlertSeverity)
                for alert_severity in alert_severities
            ]

        if include_empty_following_tags is not None:
            validate_class(include_empty_following_tags, bool)
            body["includeEmptyFollowingTags"] = include_empty_following_tags

        return self._request(
            "POST",
            f"/organizations/{validate_uuid(organization_id)}"
            "/followings/summaries/scantargets/details",
            body=body,
        ).json()

    def get_scan_target_detail_summary(
        self,
        organization_id: Union[UUID, str],
        scan_target_ids: Optional[Iterable[Union[UUID, str]]] = None,
        scan_target_tags: Optional[Iterable[str]] = None,
        scan_target_kinds: Optional[Iterable[Union[ScanTargetKind, str]]] = None,
        alert_severities: Optional[Iterable[Union[AlertSeverity, str]]] = None,
    ) -> Dict:
        """
        Get scan target following summary.
        <https://api.zanshin.tenchisecurity.com/#tag/Summaries/operation/summaries_getScanTargetDetailSummaryHandler>
        :param organization_id: the ID of the organization
        :param scan_target_ids: optional list of scan target IDs
        :param scan_target_tags: optional list of tags of organization scan targets
        :param scan_target_kinds: optional list of scan targets kinds (AWS, GCP, AZURE)
        :param alert_severities: optional list of severities
        :return: JSON object containing the following summaries
        """
        body = {}

        if scan_target_ids:
            validate_class(scan_target_ids, Iterable)
            body["scanTargetIds"] = [
                validate_uuid(scan_target_id) for scan_target_id in scan_target_ids
            ]

        if scan_target_tags:
            validate_class(scan_target_tags, Iterable)
            body["scanTargetTags"] = [
                validate_class(scan_target_tag, str)
                for scan_target_tag in scan_target_tags
            ]

        if scan_target_kinds:
            validate_class(scan_target_kinds, Iterable)
            body["scanTargetKinds"] = [
                validate_class(scan_target_kind, ScanTargetKind)
                for scan_target_kind in scan_target_kinds
            ]

        if alert_severities:
            validate_class(alert_severities, Iterable)
            body["alertSeverities"] = [
                validate_class(alert_severity, AlertSeverity)
                for alert_severity in alert_severities
            ]

        return self._request(
            "POST",
            f"/organizations/{validate_uuid(organization_id)}/summaries"
            "/scantargets/details",
            body=body,
        ).json()

    ###################################################
    # Onboard Scan Targets
    ###################################################

    def onboard_scan_target(
        self,
        region: str,
        organization_id: Union[UUID, str],
        kind: Union[ScanTargetKind, str],
        name: str,
        credential: Union[
            ScanTargetAWS,
            ScanTargetAZURE,
            ScanTargetGCP,
            ScanTargetHUAWEI,
            ScanTargetDOMAIN,
        ],
        boto3_session: any = None,
        boto3_profile: str = "default",
        schedule: ScanTargetSchedule = DAILY,
    ) -> Dict:
        """
        Currently supports only AWS Scan Targets.
        For AWS Scan Target:
        If boto3 is installed, creates a Scan Target for the given organization and perform the onboard.
        :param region: the AWS Region to deploy the CloudFormation Template of Zanshin Service Role.
        :param organization_id: the ID of the organization to have the new Scan Target.
        :param kind: the Kind of scan target (AWS, GCP, AZURE, DOMAIN)
        :param name: the name of the new scan target.
        :param credential: credentials to access the cloud account to be scanned:
            * For AWS scan targets, provide the account ID in the *account* field.
            * For Azure scan targets, provide *applicationId*, *subscriptionId*, *directoryId* and *secret* fields.
            * For GCP scan targets, provide a *projectId* field.
            * For DOMAIN scan targets, provide a URL in the *domain* field.

        :param schedule: schedule in string or enum format.
        :param boto3_profile: boto3 profile name used for CloudFormation Deployment. If none, uses \"default\" profile.
        :param boto3_session: boto3 session used for CloudFormation Deployment. If informed, will ignore boto3_profile.
        :return: JSON object containing newly created scan target .
        """

        if isinstance(kind, str):
            kind = ScanTargetKind(kind.strip().upper())
        else:
            validate_class(kind, ScanTargetKind)
        self._check_scantarget_is_aws(kind)

        boto3 = self._check_boto3_installation()
        if not boto3_session:
            boto3_session = self._get_session_from_boto3_profile(
                boto3_profile=boto3_profile, boto3=boto3
            )

        self._check_aws_credentials_are_valid(boto3_session=boto3_session)

        if len(name) < 3:
            name = f"{name}_{credential['account']}"

        new_scan_target = self.create_organization_scan_target(
            organization_id, kind, name, credential, schedule
        )
        new_scan_target_id = new_scan_target["id"]

        zanshin_stack_name = "tenchi-zanshin-service-role"
        try:
            cloudformation_client = self._deploy_cloudformation_zanshin_service_role(
                boto3_session, region, new_scan_target_id, zanshin_stack_name
            )
            retries = 0
            max_retry = 10
            wait_between_retries = 10
            zanshin_stack = self._get_cloudformation_stack_status(
                zanshin_stack_name, cloudformation_client
            )

            while zanshin_stack["StackStatus"] != "CREATE_COMPLETE":
                if not retries:
                    self._logger.debug(
                        f"Failed to confirm CloudFormation Stack {zanshin_stack_name} completion. Retrying."
                    )
                if retries >= max_retry:
                    raise RuntimeError("CloudFormation Stack wasn't deployed")
                time.sleep(wait_between_retries)
                self._logger.debug(
                    f"Checking CloudFormation Stack {zanshin_stack_name}..."
                )
                retries += 1
                zanshin_stack = self._get_cloudformation_stack_status(
                    zanshin_stack_name, cloudformation_client
                )

        except Exception as error:
            print("err", error)
            raise ValueError(
                f"Failed to confirm CloudFormation Stack {zanshin_stack_name} completion."
            )

        self.check_organization_scan_target(
            organization_id=organization_id, scan_target_id=new_scan_target_id
        )
        self.start_organization_scan_target_scan(
            organization_id=organization_id,
            scan_target_id=new_scan_target_id,
            force=True,
        )
        return self.get_organization_scan_target(
            organization_id=organization_id, scan_target_id=new_scan_target_id
        )

    def _deploy_cloudformation_zanshin_service_role(
        self,
        boto3_session: object,
        region: str,
        new_scan_target_id: str,
        zanshin_stack_name: str,
    ):
        """
        Instantiate boto3 client for CloudFormation, and create the Stack containing Zanshin Service Role.
        :return: boto3 cloudformation client.
        """
        try:
            cloudformation_client = boto3_session.client(
                "cloudformation", region_name=region
            )
            cloudformation_client.create_stack(
                StackName=zanshin_stack_name,
                TemplateURL="https://s3.amazonaws.com/tenchi-assets/zanshin-service-role.template",
                Parameters=[
                    {"ParameterKey": "ExternalId", "ParameterValue": new_scan_target_id}
                ],
                Capabilities=["CAPABILITY_IAM", "CAPABILITY_NAMED_IAM"],
            )

            return cloudformation_client
        except Exception as e:
            self._logger.error(
                "Unable to deploy CloudFormation zanshin-tenchi-service-role. The onboard won't succeed."
            )
            raise e

    def _get_cloudformation_stack_status(
        self, zanshin_stack_name, cloudformation_client
    ):
        """
        Fetch CloudFormation Stack details. Assumes that there's only one Stack with given name.
        :return: cloudformation stack.
        """
        zanshin_stack = cloudformation_client.describe_stacks(
            StackName=zanshin_stack_name
        )["Stacks"][0]

        return zanshin_stack

    def _get_session_from_boto3_profile(self, boto3_profile, boto3):
        """
        Return boto3_session from boto3_profile informed
        :return: boto3_session.
        """
        return boto3.Session(profile_name=boto3_profile)

    def _check_aws_credentials_are_valid(self, boto3_session):
        """
        Check if boto3 informed credentials are valid performing aws sts get-caller-identity. In case of
        problem, raises ValueError.

        """
        try:
            sts = boto3_session.client("sts")
            sts.get_caller_identity()
        except Exception as e:
            self._logger.exception("boto3 session is invalid")
            raise ValueError(
                "boto3 session is invalid. Working boto3 session is required."
            )

    def _check_scantarget_is_aws(self, kind):
        """
        Check if informed Scan Target is of AWS Kind. If not, raises NotImplementedError.
        """
        if kind != ScanTargetKind.AWS:
            raise NotImplementedError(
                f"Onboard doesn't support {kind.value} environment yet"
            )

    def _check_boto3_installation(self):
        """
        Check if boto3 is installed in the current environment. If not, raises ImportError.
        :return: boto3 module if present.
        """
        package_name = "boto3"
        spec = find_spec(package_name)
        if spec is None:
            raise ImportError(
                f"{package_name} not present. {package_name} is required to perform AWS onboard."
            )

        module = module_from_spec(spec)
        sys.modules[package_name] = module
        spec.loader.exec_module(module)
        return module

    def __repr__(self):
        return (
            f"Connection(api_url='{self.api_url}', api_key='***{self._api_key[-6:]}', "
            f"user_agent='{self.user_agent}', proxy_url='{self._get_sanitized_proxy_url()}')"
        )
