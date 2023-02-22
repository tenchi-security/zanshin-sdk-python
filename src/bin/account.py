from typing import Dict

from src.bin.client import Client

###################################################
# Account
###################################################


def get_me() -> Dict:
    """
    Returns the details of the user account that owns the API key used by this Connection instance as per.
    <https://api.zanshin.tenchisecurity.com/#operation/getMe>
    :return: a dict representing the user
    """
    return Client._request("GET", "/me").json()
