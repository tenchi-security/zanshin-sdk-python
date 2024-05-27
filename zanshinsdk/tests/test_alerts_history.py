import unittest
from unittest.mock import mock_open, patch

from zanshinsdk.alerts_history import FilePersistentAlertsIterator
from zanshinsdk.client import Client


class TestAlertsHistoryIterator(unittest.TestCase):
    ###################################################
    # __init__
    ###################################################

    @patch("zanshinsdk.Client._request")
    def setUp(self, request):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        scan_target_ids = []
        cursor = "8b0620bdb1e3"
        client = Client(profile="", api_key="api_key")

        self.file_persistent = FilePersistentAlertsIterator(
            filename="test_zanshin",
            client=client,
            organization_id=organization_id,
            scan_target_ids=scan_target_ids,
            cursor=cursor,
        )
        self.file_persistent.client._request = request

    ###################################################
    # _save
    ###################################################

    @patch("__main__.__builtins__.open", new_callable=mock_open)
    def test_save(self, mock_file):
        self.file_persistent._save()
        mock_file.assert_called_with("test_zanshin", "w")

    ###################################################
    # _load
    ###################################################

    @patch("zanshinsdk.alerts_history.isfile")
    def test_load(self, mock_is_file):
        mock_is_file.return_value = True

        data = (
            '{"organization_id":"822f4225-43e9-4922-b6b8-8b0620bdb1e3", "scan_target_ids": "", "cursor": '
            '"8b0620bdb1e3"}'
        )

        with patch(
            "__main__.__builtins__.open", mock_open(read_data=data)
        ) as mock_file:
            self.file_persistent._load()

        mock_file.assert_called_with("test_zanshin", "r")

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
            f"/alerts/history",
            body={"organizationId": organization_id, "pageSize": 100, "cursor": cursor},
        )
