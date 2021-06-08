import logging
import os
from configparser import RawConfigParser
from typing import Dict
from urllib.parse import urlparse

from requests import request, Response

from zanshinsdk import __version__ as sdk_version

# Default values used for the configuration
_CONFIG_FILE = os.path.join(os.path.expanduser('~/.tenchi'), "config")


class Connection:
    def __init__(self, profile: str = 'default', api_key: str = None, api_url: str = None, user_agent=None,
                 proxy_url: str = None):
        """
        Initialize a new connection to the Zanshin API.
        :param profile: which configuration file section to use for settings, or None to ignore configuration file
        :param api_key: optional override of the API key to use
        :param api_url: optional override of the base URL of the Zanshin API to use
        :param user_agent: optional override of the user agent to use in requests performed
        :param proxy_url: optional URL indicating which proxy server to use, or None for direct connections to the API
        """
        self._logger = logging.getLogger('zanshinsdk')

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
            self.api_key: str = api_key
        elif parser and parser.get(profile, 'api_key', fallback=None):
            self.api_key: str = parser.get(profile, 'api_key')
        else:
            raise ValueError('no API key found')
        self._auth_header = f'Bearer {self.api_key}'

        # set API URL
        if api_url:
            self.api_url: str = api_url
        elif parser and parser.get(profile, 'api_url', fallback=None):
            self.api_url: str = parser.get(profile, 'api_url')
        else:
            self.api_url: str = 'https://api.zanshin.tenchisecurity.com'
        api_url = urlparse(self.api_url)
        if not api_url.scheme or api_url.scheme not in ('http', 'https') or not api_url.hostname:
            raise ValueError(f'Invalid API URL: {self.api_url}')

        # set proxy URL
        if proxy_url:
            self._proxy_url: str = proxy_url
        elif parser and parser.get(profile, 'proxy_url', fallback=None):
            self._proxy_url: str = parser.get(profile, 'proxy_url')
        else:
            self._proxy_url = None

        # set requests proxy object
        if self._proxy_url:
            proxy_url = urlparse(self._proxy_url)
            if not proxy_url.scheme or proxy_url.scheme not in ('http', 'https') or not proxy_url.hostname or (
                    proxy_url.password and not proxy_url.username):
                raise ValueError(f'Invalid proxy URL: {self._proxy_url}')
            self._proxy = {api_url.scheme: self._proxy_url}
        else:
            self._proxy = None

        # set user-agent
        if user_agent:
            self.user_agent: str = user_agent
        elif parser and parser.get(profile, 'user_agent', fallback=None):
            self.user_agent: str = parser.get(profile, 'user_agent')
        else:
            self.user_agent: str = f'Zanshin Python SDK v{sdk_version}'

    def _get_sanitized_proxy_url(self) -> str:
        """
        Returns a sanitized proxy URL that doesn't expose a password, if one is present.
        :return:
        """
        if self._proxy_url:
            url = urlparse(self._proxy_url)
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

    def __repr__(self):
        return f'Connection(api_url="{self.api_url}", api_key="{self.api_key[0:6] + "***"}", user_agent="{self.user_agent}, proxy_url={self._get_sanitized_proxy_url()}")'
