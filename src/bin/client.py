from __future__ import annotations

import logging
from configparser import RawConfigParser
from enum import Enum
from os import environ
from os.path import isfile
from pathlib import Path
from typing import Optional, Union
from urllib.parse import urlparse
from uuid import UUID

import httpx

from zanshinsdk.version import __version__ as sdk_version

CONFIG_DIR = Path.home() / ".tenchi"
CONFIG_FILE = CONFIG_DIR / "config"


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
                proxies=self._proxy_url,
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


def validate_int(
    value, min_value=None, max_value=None, required=False
) -> Optional[int]:
    if value is None:
        if required:
            raise ValueError("required integer parameter missing")
        else:
            return value
    if not isinstance(value, int):
        raise TypeError(f"{repr(value)} is not an integer")
    if min_value and value < min_value:
        raise ValueError(f"{value} shouldn't be lower than {min_value}")
    if max_value and value > max_value:
        raise ValueError(f"{value} shouldn't be higher than {max_value}")
    return value


def validate_class(value, class_type):
    if not isinstance(value, class_type):
        raise TypeError(f"{repr(value)} is not an instance of {class_type.__name__}")
    return value


def validate_uuid(uuid: Union[UUID, str]) -> str:
    try:
        if isinstance(uuid, str):
            return str(UUID(uuid))

        if isinstance(uuid, UUID):
            return str(uuid)

        raise TypeError
    except (ValueError, TypeError) as ex:
        ex.args = (f"{repr(uuid)} is not a valid UUID",)
        raise ex
