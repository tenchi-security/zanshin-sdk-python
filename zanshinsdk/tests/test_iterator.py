import unittest
from typing import Dict, Iterator

from zanshinsdk.client import Client
from zanshinsdk.iterator import AbstractPersistentAlertsIterator, PersistenceEntry


class TestPersistentAlertsIterator(AbstractPersistentAlertsIterator):
    def __init__(self, test_persistence_entry, test_alerts, *args, **kwargs):
        super(TestPersistentAlertsIterator, self).__init__(*args, **kwargs)
        self._test_persistence_entry = test_persistence_entry
        self._test_alerts = test_alerts

    def _load_alerts(self) -> Iterator[Dict]:
        return self._test_alerts

    def _load(self):
        return self._test_persistence_entry

    def _save(self):
        return "_save"


class TestIterator(unittest.TestCase):
    ###################################################
    # __init__
    ###################################################

    def test_init_invalid_organization_id(self):
        organization_id = "invalid_UUID"

        try:
            PersistenceEntry(organization_id)
        except Exception as e:
            self.assertEqual(str(e), "invalid organization ID")

    def test_init_valid_organization_id(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"

        persistence_entry = PersistenceEntry(organization_id)

        self.assertEqual(organization_id, persistence_entry.organization_id)

    def test_init_invalid_filter_id(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        filter_id = ["invalid_UUID"]

        try:
            PersistenceEntry(organization_id, filter_id)
        except Exception as e:
            self.assertEqual(str(e), "invalid filter ID")

    def test_init_valid_filter_id(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        filter_id = ["822f4225-43e9-4922-b6b8-8b0620bdb1e3"]

        persistence_entry = PersistenceEntry(organization_id, filter_id)

        self.assertEqual(filter_id, persistence_entry.filter_ids)

    ###################################################
    # cursor
    ###################################################

    def test_cursor(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        cursor = "8b0620bdb1e3"

        persistence_entry = PersistenceEntry(organization_id)
        persistence_entry.cursor = cursor

        self.assertEqual(cursor, persistence_entry.cursor)

    ###################################################
    # AbstractPersistentAlertsIterator
    ###################################################

    def test_abstract_persistent_alerts_iterator_invalid_client_instance(self):
        field_name = "field_name"
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"

        client = ""

        try:
            TestPersistentAlertsIterator(
                None, None, field_name, client, organization_id
            )
        except Exception as e:
            self.assertEqual(str(e), "invalid client")

    def test_abstract_persistent_alerts_iterator_invalid_organization_id(self):
        field_name = "field_name"
        organization_id = "invalid_UUID"

        client = Client(api_key="api_key")

        try:
            TestPersistentAlertsIterator(
                None, None, field_name, client, organization_id
            )
        except Exception as e:
            self.assertEqual(str(e), "invalid organization ID")

    def test_abstract_persistent_alerts_iterator_invalid_filter_id(self):
        field_name = "field_name"
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        filter_id = ["invalid_UUID"]

        client = Client(api_key="api_key")

        try:
            TestPersistentAlertsIterator(
                None, None, field_name, client, organization_id, filter_id
            )
        except Exception as e:
            self.assertEqual(str(e), f"invalid {field_name} ID")

    def test_abstract_persistent_alerts_iterator_get_client(self):
        field_name = "field_name"
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"

        client = Client(api_key="api_key")

        test_persistent_alerts_iterator = TestPersistentAlertsIterator(
            None, None, field_name, client, organization_id
        )

        self.assertEqual(client, test_persistent_alerts_iterator.client)

    def test_abstract_persistent_alerts_iterator_get_save(self):
        field_name = "field_name"
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"

        client = Client(api_key="api_key")

        test_persistent_alerts_iterator = TestPersistentAlertsIterator(
            None, None, field_name, client, organization_id
        )

        self.assertEqual("_save", test_persistent_alerts_iterator._save())

    def test_abstract_persistent_alerts_iterator_get_load_persistence_entry(self):
        field_name = "field_name"
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"

        client = Client(api_key="api_key")

        persistence_entry = PersistenceEntry(organization_id)
        test_persistent_alerts_iterator = TestPersistentAlertsIterator(
            persistence_entry, None, field_name, client, organization_id
        )

        self.assertEqual(
            persistence_entry.organization_id,
            test_persistent_alerts_iterator._load().organization_id,
        )

    def test_abstract_persistent_alerts_iterator_get_load_persistence_entry_none(self):
        field_name = "field_name"
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"

        client = Client(api_key="api_key")

        test_persistent_alerts_iterator = TestPersistentAlertsIterator(
            None, None, field_name, client, organization_id
        )

        self.assertEqual(
            organization_id,
            test_persistent_alerts_iterator.persistence_entry.organization_id,
        )

    def test_abstract_persistent_alerts_iterator_get_load_persistence_entry_invalid_instance(
        self,
    ):
        field_name = "field_name"
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"

        client = Client(api_key="api_key")

        test_persistent_alerts_iterator = TestPersistentAlertsIterator(
            "invalid_persistence_entry", None, field_name, client, organization_id
        )

        try:
            test_persistent_alerts_iterator.persistence_entry()
        except Exception as e:
            self.assertEqual(
                str(e), "load method should return a PersistenceEntry instance"
            )

    def test_abstract_persistent_alerts_iterator_get_load_persistence_entry_instance_org_id_not_match(
        self,
    ):
        field_name = "field_name"
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        organization_id_wrong = "822f4225-43e9-4922-b6b8-8b0620bdb1e0"

        client = Client(api_key="api_key")

        persistence_entry = PersistenceEntry(organization_id_wrong)
        test_persistent_alerts_iterator = TestPersistentAlertsIterator(
            persistence_entry, None, field_name, client, organization_id
        )

        try:
            test_persistent_alerts_iterator.persistence_entry()
        except Exception as e:
            self.assertEqual(
                str(e),
                f"PersistenceEntry instance does not match organization ID: {organization_id}",
            )

    def test_abstract_persistent_alerts_iterator_get_load_persistence_entry_instance_filter_ids_not_match(
        self,
    ):
        field_name = "field_name"
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        filter_id = ["822f4225-43e9-4922-b6b8-8b0620bdb1e3"]
        filter_id_wrong = ["822f4225-43e9-4922-b6b8-8b0620bdb1e0"]

        client = Client(api_key="api_key")

        persistence_entry = PersistenceEntry(organization_id, filter_id_wrong)
        test_persistent_alerts_iterator = TestPersistentAlertsIterator(
            persistence_entry, None, field_name, client, organization_id, filter_id
        )

        try:
            test_persistent_alerts_iterator.persistence_entry()
        except Exception as e:
            self.assertEqual(
                str(e),
                f"PersistenceEntry instance does not match {field_name} IDs: "
                + ",".join([str(filter_id) for filter_id in filter_id]),
            )

    def test_abstract_persistent_alerts_iterator_next(self):
        field_name = "field_name"
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        alerts = iter([{"cursor": "abc"}])
        client = Client(api_key="api_key")

        test_persistent_alerts_iterator = TestPersistentAlertsIterator(
            None, alerts, field_name, client, organization_id
        )

        alert = test_persistent_alerts_iterator.__next__()

        self.assertEqual(
            alert["cursor"], test_persistent_alerts_iterator.persistence_entry.cursor
        )

    def test_abstract_persistent_alerts_iterator_next_stop_iteration(self):
        field_name = "field_name"
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"

        client = Client(api_key="api_key")

        test_persistent_alerts_iterator = TestPersistentAlertsIterator(
            None, None, field_name, client, organization_id
        )

        try:
            test_persistent_alerts_iterator.__next__()
        except Exception as e:
            self.assertIsInstance(e, StopIteration)

    def test_abstract_persistent_alerts_iterator_save_load(self):
        field_name = "field_name"
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"

        client = Client(api_key="api_key")

        persistence_entry = PersistenceEntry(organization_id)
        test_persistent_alerts_iterator = TestPersistentAlertsIterator(
            persistence_entry, None, field_name, client, organization_id
        )

        test_persistent_alerts_iterator.save()
        test_persistent_alerts_iterator.load()

        self.assertIsNone(test_persistent_alerts_iterator._persistence_entry)
