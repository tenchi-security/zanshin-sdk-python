import logging
import os
from configparser import RawConfigParser
from enum import Enum
from math import ceil
from typing import Dict, Optional, Iterator, Iterable, Union
from urllib.parse import urlparse
from uuid import UUID

from requests import request, Response

from zanshinsdk import __version__ as sdk_version

# Default values used for the configuration
_CONFIG_FILE = os.path.join(os.path.expanduser('~/.tenchi'), "config")


class AlertState(str, Enum):
    OPEN = 'OPEN'
    ACTIVE = 'ACTIVE'
    IN_PROGRESS = 'IN_PROGRESS'
    RISK_ACCEPTED = 'RISK_ACCEPTED'
    RESOLVED = 'RESOLVED'
    CLOSED = 'CLOSED'


class AlertSeverity(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"


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
        self._proxy: Optional[Dict[str, str]] = None

        # read configuration file
        if profile and os.path.isfile(_CONFIG_FILE):
            parser = RawConfigParser()
            parser.read(_CONFIG_FILE)
            if not parser.has_section(profile):
                raise ValueError(f'profile {profile} not found in {_CONFIG_FILE}')
        else:
            parser = None

        # set API key
        if api_key:
            self.api_key = api_key
        elif parser and parser.get(profile, 'api_key', fallback=None):
            self.api_key = parser.get(profile, 'api_key')
        else:
            raise ValueError('no API key found')

        # set API URL
        if api_url:
            self.api_url = api_url
        elif parser and parser.get(profile, 'api_url', fallback=None):
            self.api_url = parser.get(profile, 'api_url')
        else:
            self.api_url = 'https://api.zanshin.tenchisecurity.com'

        # set proxy URL
        if proxy_url:
            self.proxy_url = proxy_url
        elif parser and parser.get(profile, 'proxy_url', fallback=None):
            self.proxy_url = parser.get(profile, 'proxy_url')
        else:
            self.proxy_url = None

        # set user-agent
        if user_agent:
            self.user_agent: str = user_agent
        elif parser and parser.get(profile, 'user_agent', fallback=None):
            self.user_agent: str = parser.get(profile, 'user_agent')
        else:
            self.user_agent: str = f'Zanshin Python SDK v{sdk_version}'

    @property
    def api_url(self) -> str:
        return self._api_url

    @api_url.setter
    def api_url(self, new_api_url: str) -> str:
        parsed = urlparse(new_api_url)
        if not parsed.scheme or parsed.scheme not in (
                'http', 'https') or not parsed.hostname or parsed.password or parsed.username or (
                parsed.port and (parsed.port <= 0 or parsed.port > 65535)):
            raise ValueError(f'Invalid API URL: {self.api_url}')
        self._api_url: str = new_api_url
        if self._proxy and parsed.scheme not in self._proxy:
            # if protocol changed, the requests proxies dict needs to be updated
            self._proxy: Optional[Dict[str, str]] = {parsed.scheme: self.proxy_url}

    @property
    def api_key(self) -> str:
        return self._api_key

    @api_key.setter
    def api_key(self, new_api_key: str) -> str:
        self._api_key = new_api_key
        self._auth_header: str = f'Bearer {self._api_key}'

    @property
    def proxy_url(self) -> str:
        return self._proxy_url

    @proxy_url.setter
    def proxy_url(self, new_proxy_url: Optional[str]) -> Optional[str]:
        if new_proxy_url:
            self._proxy_url: Optional[str] = new_proxy_url
            parsed = urlparse(self._proxy_url)
            if parsed.scheme not in ('http', 'https') or not parsed.hostname or (
                    parsed.password and not parsed.username) or (
                    parsed.port and (parsed.port <= 0 or parsed.port > 65535)):
                raise ValueError(f'Invalid proxy URL: {self._proxy_url}')
            self._proxy: Optional[Dict[str, str]] = {urlparse(self.api_url).scheme: self.proxy_url}
        else:
            self._proxy_url: Optional[str] = None
            self._proxy: Optional[Dict[str, str]] = None

    def _get_sanitized_proxy_url(self) -> str:
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

    def _request(self, method: str, path: str, params=None, body=None) -> Response:
        """
        Internal method to simplify calling requests.
        :param method: HTTP method to pass along to requests.request
        :param path: API path to access
        :param params: parameters to pass along to requests.request
        :param body: request body to pass along to requests.request
        :return: the requests.Response object returned by requests.request
        """
        response = request(method=method, url=self.api_url + path, params=params, json=body, proxies=self._proxy,
                           timeout=(5, 60),
                           headers={"Authorization": self._auth_header,
                                    "Accept-Encoding": "gzip, deflate",
                                    "User-Agent": self.user_agent,
                                    "Accept": "application/json"})
        if response.request.body:
            self._logger.debug('%s %s (%d bytes in body) status code %d', response.request.method, response.request.url,
                               len(response.request.body), response.status_code)
        else:
            self._logger.debug('%s %s status code %d', response.request.method, response.request.url,
                               response.status_code)
        return response

    def me(self) -> Dict:
        """
        Returns the details of the user account that owns the API key used by this Connection instance as per
        <https://api.zanshin.tenchisecurity.com/#tag/Account>
        :return: a dict representing the user
        """
        return self._request("GET", "/me").json()

    def iter_organizations(self) -> Iterator[Dict]:
        """
        Iterates over the organizations the API key owner has access to.
        :return: an iterator over the organization objects
        """
        yield from self._request("GET", "/organizations").json()

    def iter_scan_targets(self, organization_id: Union[UUID, str]) -> Iterator[Dict]:
        """
        Iterates over the scan targets of an organization.
        :param organization_id: the ID of the organization
        : return: an iterator over the scan target objects
        """
        yield from self._request("GET", f"/organizations/{_stringify_UUID(organization_id)}/scantargets").json()

    def _get_organization_alerts_page(self, organization_id: Union[UUID, str],
                                      scan_target_ids: Optional[Iterable[Union[UUID, str]]] = None,
                                      states: Optional[Iterable[AlertState]] = None,
                                      severities: Optional[Iterable[AlertSeverity]] = None, page: int = 1,
                                      page_size: int = 100) -> Dict:
        """
        Internal method to retrieve a single page of alerts from an organization.
        :param organization_id: the ID of the organization
        :param scan_target_ids: optional list of scan target IDs to list alerts from, defaults to all
        :param states: optional list of states to filter returned alerts
        :param severities: optional list of severities to filter returned alerts
        :param page: page number, starting from 1
        :param page_size: page size in number of alerts
        :return:
        """
        body = {
            "page": page,
            "pageSize": page_size
        }
        if organization_id:
            body['organizationId'] = _stringify_UUID(organization_id)
        if scan_target_ids:
            body['scanTargetIds'] = [_stringify_UUID(x) for x in scan_target_ids]
        if states:
            body['states'] = [x.value for x in states]
        if severities:
            body['severities'] = [x.value for x in severities]
        return self._request("POST", "/alerts", body=body).json()

    def iter_organization_alerts(self, organization_id: Union[UUID, str],
                                 scan_target_ids: Optional[Iterable[Union[UUID, str]]] = None,
                                 states: Optional[Iterable[AlertState]] = None,
                                 severities: Optional[Iterable[AlertSeverity]] = None, page_size: int = 100):
        page = self._get_organization_alerts_page(organization_id, scan_target_ids, states, severities, page=1,
                                                  page_size=page_size)
        yield from page.get('data', [])
        for page_number in range(2, int(ceil(page.get('total', 0) / float(page_size))) + 1):
            page = self._get_organization_alerts_page(organization_id, scan_target_ids, states, severities,
                                                      page=page_number,
                                                      page_size=page_size)
            yield from page.get('data', [])

    def start_scan_target(self, organization_id: Union[UUID, str], scan_target_id: Union[UUID, str]) -> Dict:
        return self._request("POST", f"/organizations/{_stringify_UUID(organization_id)}/scantargets/{_stringify_UUID(scan_target_id)}/scan").json()

    def check_scan_target(self, organization_id: Union[UUID, str], scan_target_id: Union[UUID, str]) -> Dict:
        return self._request("POST", f"/organizations/{_stringify_UUID(organization_id)}/scantargets/{_stringify_UUID(scan_target_id)}/check").json()

    def __repr__(self):
        return f'Connection(api_url="{self.api_url}", api_key="{self._api_key[0:6] + "***"}", user_agent="{self.user_agent}, proxy_url={self._get_sanitized_proxy_url()}")'


def _stringify_UUID(uuid: Union[UUID, str]):
    if isinstance(uuid, str):
        return str(UUID(uuid))
    else:
        return str(uuid)
