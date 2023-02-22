from typing import Dict, Iterator, Optional, Union
from uuid import UUID

from client import Client, validate_uuid

###################################################
# Account API key
###################################################


def iter_api_keys() -> Iterator[Dict]:
    """
    Iterates over the API keys of current logged user.
    <https://api.zanshin.tenchisecurity.com/#operation/getMyApiKeys>
    :return: an iterator over the api keys objects
    """
    yield from Client._request("GET", "/me/apikeys").json()


def create_api_key(name: Optional[str]) -> Dict:
    """
    Creates a new API key for the current logged user, API Keys can be used to interact with the zanshin api
    directly on behalf of that user.
    <https://api.zanshin.tenchisecurity.com/#operation/createApiKeys>
    :param name: the Name of your new API key
    :return: a dict representing the user api key
    """
    body = {"name": name}
    return Client._request("POST", "/me/apikeys", body=body).json()


def delete_api_key(api_key_id: Union[UUID, str]) -> bool:
    """
    Deletes a given API key by its id, it will only work if the informed ID belongs to the current logged user.
    <https://api.zanshin.tenchisecurity.com/#operation/deleteApiKey>
    :param api_key_id: the ID of the API key
    :return: a boolean if success
    """
    return Client._request("DELETE", f"/me/apikeys/{validate_uuid(api_key_id)}").json()
