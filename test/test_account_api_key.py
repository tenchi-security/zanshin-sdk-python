import unittest

from src.bin.account_api_key import create_api_key, delete_api_key, iter_api_keys
from src.bin.client import Client

###################################################
# Account API key
###################################################


class AccountApiKeyTest(unittest.TestCase):
    def test_iter_api_keys(self):
        try:
            next(iter_api_keys())
        except StopIteration:
            pass

        Client._request.assert_called_once_with("GET", "/me/apikeys")

    def test_create_api_key(self):
        name = "MyKey"

        create_api_key(name)

        Client._request.assert_called_once_with(
            "POST", "/me/apikeys", body={"name": name}
        )

    def test_delete_api_key(self):
        api_key = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"

        delete_api_key(api_key)

        Client._request.assert_called_once_with("DELETE", f"/me/apikeys/{api_key}")
