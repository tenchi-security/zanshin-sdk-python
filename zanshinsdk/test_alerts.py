import unittest
from unittest.mock import call, patch

from alerts import (
    _get_alerts_following_history_page,
    _get_alerts_history_page,
    _get_alerts_page,
    _get_following_alerts_page,
    _get_grouped_alerts_page,
    _get_grouped_following_alerts_page,
    create_alert_comment,
    get_alert,
    iter_alert_comments,
    iter_alert_history,
    iter_alerts,
    iter_alerts_following_history,
    iter_alerts_history,
    iter_following_alerts,
    iter_grouped_alerts,
    iter_grouped_following_alerts,
    update_alert,
)
from client import (
    AlertSeverity,
    AlertsOrderOpts,
    AlertState,
    Client,
    Languages,
    SortOpts,
)

###################################################
# Alerts
###################################################


class AlertsTest(unittest.TestCase):
    def test_get_alerts_page(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        page = 1
        page_size = 100
        rule = "rule"
        language = Languages.EN_US
        # TODO: use valid dates
        created_at_start = "created_at_start"
        created_at_end = "created_at_end"
        updated_at_start = "updated_at_start"
        updated_at_end = "updated_at_end"
        search = "search"
        sort = SortOpts.ASC
        order = AlertsOrderOpts.SEVERITY

        _get_alerts_page(
            organization_id,
            page=page,
            page_size=page_size,
            rule=rule,
            language=language,
            search=search,
            order=order,
            sort=sort,
            created_at_start=created_at_start,
            created_at_end=created_at_end,
            updated_at_start=updated_at_start,
            updated_at_end=updated_at_end,
        )

        Client._request.assert_called_once_with(
            "POST",
            f"/alerts",
            body={
                "organizationId": organization_id,
                "page": page,
                "pageSize": page_size,
                "rule": rule,
                "lang": language,
                "search": search,
                "order": order,
                "sort": sort,
                "createdAtStart": created_at_start,
                "createdAtEnd": created_at_end,
                "updatedAtStart": updated_at_start,
                "updatedAtEnd": updated_at_end,
            },
        )

    def test_get_alerts_page_str_scan_target_ids(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        page = 1
        page_size = 100
        scan_target_ids = "e22f4225-43e9-4922-b6b8-8b0620bdb110"

        _get_alerts_page(
            organization_id,
            page=page,
            page_size=page_size,
            scan_target_ids=scan_target_ids,
        )

        Client._request.assert_called_once_with(
            "POST",
            f"/alerts",
            body={
                "organizationId": organization_id,
                "page": page,
                "pageSize": page_size,
                "scanTargetIds": [scan_target_ids],
            },
        )

    def test_get_alerts_page_iterable_scan_target_ids(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        page = 1
        page_size = 100
        scan_target_ids = [
            "e22f4225-43e9-4922-b6b8-8b0620bdb110",
            "e22f4225-43e9-4922-b6b8-8b0620bdb112",
        ]

        _get_alerts_page(
            organization_id,
            page=page,
            page_size=page_size,
            scan_target_ids=scan_target_ids,
        )

        Client._request.assert_called_once_with(
            "POST",
            f"/alerts",
            body={
                "organizationId": organization_id,
                "page": page,
                "pageSize": page_size,
                "scanTargetIds": scan_target_ids,
            },
        )

    def test_get_alerts_page_str_states(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        page = 1
        page_size = 100
        states = AlertState.OPEN

        _get_alerts_page(organization_id, page=page, page_size=page_size, states=states)

        Client._request.assert_called_once_with(
            "POST",
            f"/alerts",
            body={
                "organizationId": organization_id,
                "page": page,
                "pageSize": page_size,
                "states": [states],
            },
        )

    def test_get_alerts_page_iterable_states(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        page = 1
        page_size = 100
        states = [AlertState.OPEN, AlertState.CLOSED]

        _get_alerts_page(organization_id, page=page, page_size=page_size, states=states)

        Client._request.assert_called_once_with(
            "POST",
            f"/alerts",
            body={
                "organizationId": organization_id,
                "page": page,
                "pageSize": page_size,
                "states": states,
            },
        )

    def test_get_alerts_page_str_severities(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        page = 1
        page_size = 100
        severities = AlertSeverity.CRITICAL

        _get_alerts_page(
            organization_id, page=page, page_size=page_size, severities=severities
        )

        Client._request.assert_called_once_with(
            "POST",
            f"/alerts",
            body={
                "organizationId": organization_id,
                "page": page,
                "pageSize": page_size,
                "severities": [severities],
            },
        )

    def test_get_alerts_page_iterable_severities(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        page = 1
        page_size = 100
        severities = [AlertSeverity.CRITICAL, AlertSeverity.HIGH]

        _get_alerts_page(
            organization_id, page=page, page_size=page_size, severities=severities
        )

        Client._request.assert_called_once_with(
            "POST",
            f"/alerts",
            body={
                "organizationId": organization_id,
                "page": page,
                "pageSize": page_size,
                "severities": severities,
            },
        )

    @patch("client.Client._get_alerts_page")
    def test_iter_alerts(self, request):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        page = 1
        page_size = 1

        request.return_value = {
            "data": [""],
            "total": 2,
        }

        _get_alerts_page = request
        iterator = iter_alerts(organization_id, page_size=page_size)

        next(iterator)
        next(iterator)

        _get_alerts_page.assert_has_calls(
            [
                call(
                    organization_id,
                    None,
                    None,
                    None,
                    None,
                    page=page,
                    page_size=page_size,
                    language=None,
                    search=None,
                    order=None,
                    sort=None,
                    created_at_start=None,
                    created_at_end=None,
                    updated_at_start=None,
                    updated_at_end=None,
                ),
                call(
                    organization_id,
                    None,
                    None,
                    None,
                    None,
                    page=page + 1,
                    page_size=page_size,
                    language=None,
                    search=None,
                    order=None,
                    sort=None,
                    created_at_start=None,
                    created_at_end=None,
                    updated_at_start=None,
                    updated_at_end=None,
                ),
            ]
        )

    def test_get_following_alerts_page(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        page = 1
        page_size = 100
        rule = "rule"
        language = Languages.EN_US
        created_at_start = "created_at_start"
        created_at_end = "created_at_end"
        updated_at_start = "updated_at_start"
        updated_at_end = "updated_at_end"

        _get_following_alerts_page(
            organization_id,
            page=page,
            page_size=page_size,
            rule=rule,
            language=language,
            created_at_start=created_at_start,
            created_at_end=created_at_end,
            updated_at_start=updated_at_start,
            updated_at_end=updated_at_end,
        )

        Client._request.assert_called_once_with(
            "POST",
            f"/alerts/following",
            body={
                "organizationId": organization_id,
                "page": page,
                "pageSize": page_size,
                "rule": rule,
                "lang": language,
                "CreatedAtStart": created_at_start,
                "CreatedAtEnd": created_at_end,
                "UpdatedAtStart": updated_at_start,
                "UpdatedAtEnd": updated_at_end,
            },
        )

    def test_get_following_alerts_page_str_following_ids(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        page = 1
        page_size = 100
        following_ids = "e22f4225-43e9-4922-b6b8-8b0620bdb110"

        _get_following_alerts_page(
            organization_id, page=page, page_size=page_size, following_ids=following_ids
        )

        Client._request.assert_called_once_with(
            "POST",
            f"/alerts/following",
            body={
                "organizationId": organization_id,
                "page": page,
                "pageSize": page_size,
                "followingIds": [following_ids],
            },
        )

    def test_get_following_alerts_page_iterable_following_ids(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        page = 1
        page_size = 100
        following_ids = [
            "e22f4225-43e9-4922-b6b8-8b0620bdb110",
            "e22f4225-43e9-4922-b6b8-8b0620bdb112",
        ]

        _get_following_alerts_page(
            organization_id, page=page, page_size=page_size, following_ids=following_ids
        )

        Client._request.assert_called_once_with(
            "POST",
            f"/alerts/following",
            body={
                "organizationId": organization_id,
                "page": page,
                "pageSize": page_size,
                "followingIds": following_ids,
            },
        )

    def test_get_following_alerts_page_str_states(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        page = 1
        page_size = 100
        states = AlertState.OPEN

        _get_following_alerts_page(
            organization_id, page=page, page_size=page_size, states=states
        )

        Client._request.assert_called_once_with(
            "POST",
            f"/alerts/following",
            body={
                "organizationId": organization_id,
                "page": page,
                "pageSize": page_size,
                "states": [states],
            },
        )

    def test_get_following_alerts_page_iterable_states(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        page = 1
        page_size = 100
        states = [AlertState.OPEN, AlertState.CLOSED]

        _get_following_alerts_page(
            organization_id, page=page, page_size=page_size, states=states
        )

        Client._request.assert_called_once_with(
            "POST",
            f"/alerts/following",
            body={
                "organizationId": organization_id,
                "page": page,
                "pageSize": page_size,
                "states": states,
            },
        )

    def test_get_following_alerts_page_str_severities(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        page = 1
        page_size = 100
        severities = AlertSeverity.CRITICAL

        _get_following_alerts_page(
            organization_id, page=page, page_size=page_size, severities=severities
        )

        Client._request.assert_called_once_with(
            "POST",
            f"/alerts/following",
            body={
                "organizationId": organization_id,
                "page": page,
                "pageSize": page_size,
                "severities": [severities],
            },
        )

    def test_get_following_alerts_page_iterable_severities(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        page = 1
        page_size = 100
        severities = [AlertSeverity.CRITICAL, AlertSeverity.HIGH]

        _get_following_alerts_page(
            organization_id, page=page, page_size=page_size, severities=severities
        )

        Client._request.assert_called_once_with(
            "POST",
            f"/alerts/following",
            body={
                "organizationId": organization_id,
                "page": page,
                "pageSize": page_size,
                "severities": severities,
            },
        )

    @patch("client.Client._get_following_alerts_page")
    def test_iter_following_alerts(self, request):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        page = 1
        page_size = 1

        request.return_value = {
            "data": [""],
            "total": 2,
        }

        _get_following_alerts_page = request
        iterator = iter_following_alerts(organization_id, page_size=page_size)

        next(iterator)
        next(iterator)

        _get_following_alerts_page.assert_has_calls(
            [
                call(
                    organization_id,
                    None,
                    None,
                    None,
                    None,
                    page=page,
                    page_size=page_size,
                    language=None,
                    created_at_start=None,
                    created_at_end=None,
                    updated_at_start=None,
                    updated_at_end=None,
                    search=None,
                    order=None,
                    sort=None,
                ),
                call(
                    organization_id,
                    None,
                    None,
                    None,
                    None,
                    page=page + 1,
                    page_size=page_size,
                    language=None,
                    created_at_start=None,
                    created_at_end=None,
                    updated_at_start=None,
                    updated_at_end=None,
                    search=None,
                    order=None,
                    sort=None,
                ),
            ]
        )

    def test_get_alerts_history_page(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        page_size = 100
        language = Languages.EN_US
        cursor = "12345678"

        _get_alerts_history_page(
            organization_id, page_size=page_size, language=language, cursor=cursor
        )

        Client._request.assert_called_once_with(
            "POST",
            f"/alerts/history",
            body={
                "organizationId": organization_id,
                "pageSize": page_size,
                "lang": language,
                "cursor": cursor,
            },
        )

    def test_get_alerts_history_page_str_scan_target_ids(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        page_size = 100
        scan_target_ids = "e22f4225-43e9-4922-b6b8-8b0620bdb110"

        _get_alerts_history_page(
            organization_id, page_size=page_size, scan_target_ids=scan_target_ids
        )

        Client._request.assert_called_once_with(
            "POST",
            f"/alerts/history",
            body={
                "organizationId": organization_id,
                "pageSize": page_size,
                "scanTargetIds": [scan_target_ids],
            },
        )

    def test_get_alerts_history_page_iterable_scan_target_ids(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        page_size = 100
        scan_target_ids = [
            "e22f4225-43e9-4922-b6b8-8b0620bdb110",
            "e22f4225-43e9-4922-b6b8-8b0620bdb112",
        ]

        _get_alerts_history_page(
            organization_id, page_size=page_size, scan_target_ids=scan_target_ids
        )

        Client._request.assert_called_once_with(
            "POST",
            f"/alerts/history",
            body={
                "organizationId": organization_id,
                "pageSize": page_size,
                "scanTargetIds": scan_target_ids,
            },
        )

    @patch("client.Client._get_alerts_history_page")
    def test_iter_alerts_history(self, request):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        page_size = 1

        request.return_value = {
            "data": [{"cursor": 1}],
        }

        _get_alerts_history_page = request
        iterator = iter_alerts_history(organization_id, page_size=page_size)

        next(iterator)
        next(iterator)

        _get_alerts_history_page.assert_has_calls(
            [
                call(
                    organization_id,
                    None,
                    page_size=page_size,
                    language=None,
                    cursor=None,
                ),
                call(
                    organization_id, None, page_size=page_size, language=None, cursor=1
                ),
            ]
        )

    def test_get_alerts_following_history_page(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        page_size = 100
        language = Languages.EN_US
        cursor = "12345678"

        _get_alerts_following_history_page(
            organization_id, page_size=page_size, language=language, cursor=cursor
        )

        Client._request.assert_called_once_with(
            "POST",
            f"/alerts/history/following",
            body={
                "organizationId": organization_id,
                "pageSize": page_size,
                "lang": language,
                "cursor": cursor,
            },
        )

    def test_get_alerts_following_history_page_str_following_ids(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        page_size = 100
        following_ids = "e22f4225-43e9-4922-b6b8-8b0620bdb110"

        _get_alerts_following_history_page(
            organization_id, page_size=page_size, following_ids=following_ids
        )

        Client._request.assert_called_once_with(
            "POST",
            f"/alerts/history/following",
            body={
                "organizationId": organization_id,
                "pageSize": page_size,
                "followingIds": [following_ids],
            },
        )

    def test_get_alerts_following_history_page_iterable_following_ids(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        page_size = 100
        following_ids = [
            "e22f4225-43e9-4922-b6b8-8b0620bdb110",
            "e22f4225-43e9-4922-b6b8-8b0620bdb112",
        ]

        _get_alerts_following_history_page(
            organization_id, page_size=page_size, following_ids=following_ids
        )

        Client._request.assert_called_once_with(
            "POST",
            f"/alerts/history/following",
            body={
                "organizationId": organization_id,
                "pageSize": page_size,
                "followingIds": following_ids,
            },
        )

    @patch("client.Client._get_alerts_following_history_page")
    def test_iter_alerts_following_history(self, request):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        page_size = 1

        request.return_value = {
            "data": [{"cursor": 1}],
        }

        _get_alerts_following_history_page = request
        iterator = iter_alerts_following_history(organization_id, page_size=page_size)

        next(iterator)
        next(iterator)

        _get_alerts_following_history_page.assert_has_calls(
            [
                call(
                    organization_id,
                    None,
                    page_size=page_size,
                    language=None,
                    cursor=None,
                ),
                call(
                    organization_id, None, page_size=page_size, language=None, cursor=1
                ),
            ]
        )

    def test_get_grouped_alerts_page(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        page = 1
        page_size = 100

        _get_grouped_alerts_page(organization_id, page=page, page_size=page_size)

        Client._request.assert_called_once_with(
            "POST",
            f"/alerts/rules",
            body={
                "organizationId": organization_id,
                "page": page,
                "pageSize": page_size,
            },
        )

    def test_get_grouped_alerts_page_str_scan_target_ids(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        page = 1
        page_size = 100
        scan_target_ids = "e22f4225-43e9-4922-b6b8-8b0620bdb110"

        _get_grouped_alerts_page(
            organization_id,
            page=page,
            page_size=page_size,
            scan_target_ids=scan_target_ids,
        )

        Client._request.assert_called_once_with(
            "POST",
            f"/alerts/rules",
            body={
                "organizationId": organization_id,
                "page": page,
                "pageSize": page_size,
                "scanTargetIds": [scan_target_ids],
            },
        )

    def test_get_grouped_alerts_page_iterable_scan_target_ids(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        page = 1
        page_size = 100
        scan_target_ids = [
            "e22f4225-43e9-4922-b6b8-8b0620bdb110",
            "e22f4225-43e9-4922-b6b8-8b0620bdb112",
        ]

        _get_grouped_alerts_page(
            organization_id,
            page=page,
            page_size=page_size,
            scan_target_ids=scan_target_ids,
        )

        Client._request.assert_called_once_with(
            "POST",
            f"/alerts/rules",
            body={
                "organizationId": organization_id,
                "page": page,
                "pageSize": page_size,
                "scanTargetIds": scan_target_ids,
            },
        )

    def test_get_grouped_alerts_page_str_states(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        page = 1
        page_size = 100
        states = AlertState.OPEN

        _get_grouped_alerts_page(
            organization_id, page=page, page_size=page_size, states=states
        )

        Client._request.assert_called_once_with(
            "POST",
            f"/alerts/rules",
            body={
                "organizationId": organization_id,
                "page": page,
                "pageSize": page_size,
                "states": [states],
            },
        )

    def test_get_grouped_alerts_page_iterable_states(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        page = 1
        page_size = 100
        states = [AlertState.OPEN, AlertState.CLOSED]

        _get_grouped_alerts_page(
            organization_id, page=page, page_size=page_size, states=states
        )

        Client._request.assert_called_once_with(
            "POST",
            f"/alerts/rules",
            body={
                "organizationId": organization_id,
                "page": page,
                "pageSize": page_size,
                "states": states,
            },
        )

    def test_get_grouped_alerts_page_str_severities(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        page = 1
        page_size = 100
        severities = AlertSeverity.CRITICAL

        _get_grouped_alerts_page(
            organization_id, page=page, page_size=page_size, severities=severities
        )

        Client._request.assert_called_once_with(
            "POST",
            f"/alerts/rules",
            body={
                "organizationId": organization_id,
                "page": page,
                "pageSize": page_size,
                "severities": [severities],
            },
        )

    def test_get_grouped_alerts_page_iterable_severities(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        page = 1
        page_size = 100
        severities = [AlertSeverity.CRITICAL, AlertSeverity.HIGH]

        _get_grouped_alerts_page(
            organization_id, page=page, page_size=page_size, severities=severities
        )

        Client._request.assert_called_once_with(
            "POST",
            f"/alerts/rules",
            body={
                "organizationId": organization_id,
                "page": page,
                "pageSize": page_size,
                "severities": severities,
            },
        )

    @patch("client.Client._get_grouped_alerts_page")
    def test_iter_grouped_alerts(self, request):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        page = 1
        page_size = 1

        request.return_value = {"data": [""], "total": 2}

        _get_grouped_alerts_page = request
        iterator = iter_grouped_alerts(organization_id, page_size=page_size)

        next(iterator)
        next(iterator)

        _get_grouped_alerts_page.assert_has_calls(
            [
                call(
                    organization_id,
                    None,
                    None,
                    None,
                    page=page,
                    page_size=page_size,
                    language=None,
                    search=None,
                    order=None,
                    sort=None,
                ),
                call(
                    organization_id,
                    None,
                    None,
                    None,
                    page=page + 1,
                    page_size=page_size,
                    language=None,
                    search=None,
                    order=None,
                    sort=None,
                ),
            ]
        )

    def test_get_grouped_following_alerts_page(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        page = 1
        page_size = 100

        _get_grouped_following_alerts_page(
            organization_id, page=page, page_size=page_size
        )

        Client._request.assert_called_once_with(
            "POST",
            f"/alerts/rules/following",
            body={
                "organizationId": organization_id,
                "page": page,
                "pageSize": page_size,
            },
        )

    def test_get_grouped_following_alerts_page_str_following_ids(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        page = 1
        page_size = 100
        following_ids = "e22f4225-43e9-4922-b6b8-8b0620bdb110"

        _get_grouped_following_alerts_page(
            organization_id, page=page, page_size=page_size, following_ids=following_ids
        )

        Client._request.assert_called_once_with(
            "POST",
            f"/alerts/rules/following",
            body={
                "organizationId": organization_id,
                "page": page,
                "pageSize": page_size,
                "followingIds": [following_ids],
            },
        )

    def test_get_grouped_following_alerts_page_iterable_following_ids(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        page = 1
        page_size = 100
        following_ids = [
            "e22f4225-43e9-4922-b6b8-8b0620bdb110",
            "e22f4225-43e9-4922-b6b8-8b0620bdb112",
        ]

        _get_grouped_following_alerts_page(
            organization_id, page=page, page_size=page_size, following_ids=following_ids
        )

        Client._request.assert_called_once_with(
            "POST",
            f"/alerts/rules/following",
            body={
                "organizationId": organization_id,
                "page": page,
                "pageSize": page_size,
                "followingIds": following_ids,
            },
        )

    def test_get_grouped_following_alerts_page_str_states(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        page = 1
        page_size = 100
        states = AlertState.OPEN

        _get_grouped_following_alerts_page(
            organization_id, page=page, page_size=page_size, states=states
        )

        Client._request.assert_called_once_with(
            "POST",
            f"/alerts/rules/following",
            body={
                "organizationId": organization_id,
                "page": page,
                "pageSize": page_size,
                "states": [states],
            },
        )

    def test_get_grouped_following_alerts_page_iterable_states(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        page = 1
        page_size = 100
        states = [AlertState.OPEN, AlertState.CLOSED]

        _get_grouped_following_alerts_page(
            organization_id, page=page, page_size=page_size, states=states
        )

        Client._request.assert_called_once_with(
            "POST",
            f"/alerts/rules/following",
            body={
                "organizationId": organization_id,
                "page": page,
                "pageSize": page_size,
                "states": states,
            },
        )

    def test_get_grouped_following_alerts_page_str_severities(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        page = 1
        page_size = 100
        severities = AlertSeverity.CRITICAL

        _get_grouped_following_alerts_page(
            organization_id, page=page, page_size=page_size, severities=severities
        )

        Client._request.assert_called_once_with(
            "POST",
            f"/alerts/rules/following",
            body={
                "organizationId": organization_id,
                "page": page,
                "pageSize": page_size,
                "severities": [severities],
            },
        )

    def test_get_grouped_following_alerts_page_iterable_severities(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        page = 1
        page_size = 100
        severities = [AlertSeverity.CRITICAL, AlertSeverity.HIGH]

        _get_grouped_following_alerts_page(
            organization_id, page=page, page_size=page_size, severities=severities
        )

        Client._request.assert_called_once_with(
            "POST",
            f"/alerts/rules/following",
            body={
                "organizationId": organization_id,
                "page": page,
                "pageSize": page_size,
                "severities": severities,
            },
        )

    @patch("client.Client._get_grouped_following_alerts_page")
    def test_iter_grouped_following_alerts(self, request):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        page = 1
        page_size = 1

        request.return_value = {"data": [""], "total": 2}

        _get_grouped_following_alerts_page = request
        iterator = iter_grouped_following_alerts(organization_id, page_size=page_size)

        next(iterator)
        next(iterator)

        _get_grouped_following_alerts_page.assert_has_calls(
            [
                call(
                    organization_id,
                    None,
                    None,
                    None,
                    page=page,
                    page_size=page_size,
                    language=None,
                    search=None,
                    order=None,
                    sort=None,
                ),
                call(
                    organization_id,
                    None,
                    None,
                    None,
                    page=page + 1,
                    page_size=page_size,
                    language=None,
                    search=None,
                    order=None,
                    sort=None,
                ),
            ]
        )

    def test_get_alert(self):
        alert_id = "e22f4225-43e9-4922-b6b8-8b0620bdb110"

        get_alert(alert_id)

        Client._request.assert_called_once_with(
            "GET",
            f"/alerts/{alert_id}",
        )

    def test_iter_alert_history(self):
        alert_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"

        try:
            next(iter_alert_history(alert_id))
        except StopIteration:
            pass

        Client._request.assert_called_once_with(
            "GET",
            f"/alerts/{alert_id}/history",
        )

    def test_iter_alert_comments(self):
        alert_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"

        try:
            next(iter_alert_comments(alert_id))
        except StopIteration:
            pass

        Client._request.assert_called_once_with(
            "GET",
            f"/alerts/{alert_id}/comments",
        )

    def test_update_alert(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        alert_id = "e22f4225-43e9-4922-b6b8-8b0620bdb110"
        scan_target_id = "e22f4225-43e9-4922-b6b8-8b0620bdb113"
        state = AlertState.OPEN
        labels = ["Test"]
        comment = "Comment test"

        update_alert(organization_id, scan_target_id, alert_id, state, labels, comment)

        Client._request.assert_called_once_with(
            "PUT",
            f"/organizations/{organization_id}/scantargets/{scan_target_id}/alerts/{alert_id}",
            body={"state": state, "labels": labels, "comment": comment},
        )

    def test_create_alert_comment(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        alert_id = "e22f4225-43e9-4922-b6b8-8b0620bdb110"
        scan_target_id = "e22f4225-43e9-4922-b6b8-8b0620bdb113"
        comment = "Comment test"

        create_alert_comment(organization_id, scan_target_id, alert_id, comment)

        Client._request.assert_called_once_with(
            "POST",
            f"/organizations/{organization_id}/scantargets/{scan_target_id}/alerts/{alert_id}/comments",
            body={"comment": comment},
        )
