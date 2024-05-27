import unittest
from unittest.mock import mock_open, patch

from zanshinsdk.client import Client
from zanshinsdk.following_alerts_history import FilePersistentFollowingAlertsIterator


class TestAlertsHistoryIterator(unittest.TestCase):
    ###################################################
    # __init__
    ###################################################

    @patch("zanshinsdk.Client._request")
    def setUp(self, request):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        following_ids = []
        cursor = "8b0620bdb1e3"
        client = Client(profile="", api_key="api_key")

        self.file_persistent = FilePersistentFollowingAlertsIterator(
            filename="test_zanshin_following",
            client=client,
            organization_id=organization_id,
            following_ids=following_ids,
            cursor=cursor,
        )
        self.file_persistent.client._request = request

    ###################################################
    # _save
    ###################################################

    @patch("__main__.__builtins__.open", new_callable=mock_open)
    def test_save(self, mock_file):
        self.file_persistent._save()
        mock_file.assert_called_with("test_zanshin_following", "w")

    ###################################################
    # _load
    ###################################################

    @patch("zanshinsdk.following_alerts_history.isfile")
    def test_load(self, mock_is_file):
        mock_is_file.return_value = True

        data = (
            '{"organization_id":"822f4225-43e9-4922-b6b8-8b0620bdb1e3", "following_ids": "", "cursor": '
            '"8b0620bdb1e3"} '
        )

        with patch(
            "__main__.__builtins__.open", mock_open(read_data=data)
        ) as mock_file:
            self.file_persistent._load()

        mock_file.assert_called_with("test_zanshin_following", "r")

    ###################################################
    # _load_alerts
    ###################################################

    def test_get_organization_members(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        cursor = "8b0620bdb1e3"

        try:
            next(self.file_persistent._load_alerts())
        except StopIteration:
            pass

        self.file_persistent.client._request.assert_called_once_with(
            "POST",
            f"/alerts/history/following",
            body={"organizationId": organization_id, "pageSize": 100, "cursor": cursor},
        )
