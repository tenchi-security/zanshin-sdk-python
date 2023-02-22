import unittest
from unittest.mock import Mock, mock_open, patch

from src.bin.client import Client
from src.bin.scan_target_scan import (
    get_organization_scan_target_scan,
    iter_organization_scan_target_scans,
)

###################################################
# Organization Scan Target Scan
###################################################


class ScanTargetScanTest(unittest.TestCase):
    def test_iter_organization_scan_target_scans_request(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        scan_target_id = "e22f4225-43e9-4922-b6b8-8b0620bdb110"

        try:
            next(iter_organization_scan_target_scans(organization_id, scan_target_id))
        except StopIteration:
            pass

        Client._request.assert_called_once_with(
            "GET",
            f"/organizations/{organization_id}/scantargets/{scan_target_id}/scans",
        )

    @patch("zanshinsdk.client.isfile")
    @patch("zanshinsdk.Client._request")
    def test_iter_organization_scan_target_scans_response(self, request, mock_is_file):
        organization_id = "f59fd172-d968-4e94-9cc7-bc1ed33155f1"
        scan_target_id = "0c89dc67-eeec-4004-8ca4-98669047417a"
        scan_data = {
            "summary": {
                "infos": {
                    "NEW": {"HIGH": 0, "INFO": 0, "MEDIUM": 0, "LOW": 0, "CRITICAL": 0},
                    "COLLECTED": 6726,
                    "REOPEN": {
                        "HIGH": 0,
                        "INFO": 0,
                        "MEDIUM": 0,
                        "LOW": 0,
                        "CRITICAL": 0,
                    },
                    "CLOSED": {
                        "HIGH": 0,
                        "INFO": 0,
                        "MEDIUM": 0,
                        "LOW": 0,
                        "CRITICAL": 0,
                    },
                    "UNKNOWN": 485,
                    "FAIL": 642,
                    "OPEN": {
                        "HIGH": 0,
                        "MEDIUM": 0,
                        "INFO": 0,
                        "LOW": 0,
                        "CRITICAL": 0,
                    },
                },
                "states": {"CLOSED": 442, "OPEN": 638, "RISK_ACCEPTED": 4},
                "severities": {
                    "HIGH": 55,
                    "INFO": 49,
                    "MEDIUM": 283,
                    "LOW": 232,
                    "CRITICAL": 23,
                },
            },
            "updatedAt": "2022-07-10T00:10:24.593646",
            "status": "DONE",
            "createdAt": "2022-07-10T00:04:08.076Z",
            "scanTargetId": scan_target_id,
            "slot": "2022-07-10T00:04:07.953Z",
            "organizationId": organization_id,
        }

        mock_is_file.return_value = True
        with patch(
            "__main__.__builtins__.open",
            mock_open(read_data="[default]\napi_key=api_key"),
        ):
            request.return_value = Mock(
                status_code=200, json=lambda: {"data": [scan_data]}
            )
            client = Client()
            client._client.request = request

            iter = client.iter_organization_scan_target_scans(
                organization_id, scan_target_id
            )

        self.assertDictEqual(iter.__next__(), scan_data)
        self.assertRaises(StopIteration, iter.__next__)

    def test_get_organization_scan_target_scan(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        scan_target_id = "e22f4225-43e9-4922-b6b8-8b0620bdb110"
        scan_id = "e22f4225-43e9-4922-b6b8-8b0620bdb112"

        get_organization_scan_target_scan(organization_id, scan_target_id, scan_id)

        Client._request.assert_called_once_with(
            "GET",
            f"/organizations/{organization_id}/scantargets/{scan_target_id}/scans/{scan_id}",
        )
