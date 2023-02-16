import unittest

from account import get_me
from client import Client

###################################################
# Account
###################################################


class TestAccount(unittest.TestCase):
    def test_get_me(self):
        get_me()

        Client._request.assert_called_once_with("GET", "/me")
