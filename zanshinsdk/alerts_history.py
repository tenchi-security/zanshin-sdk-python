# -*- coding: utf-8 -*-
"""
This module allows persistent iteration of alerts. Some use cases include opening tickets based
on new alerts, or even automating responses for some high-confidence alerts.
"""
import json
from abc import ABCMeta, abstractmethod
from collections import Iterator
from os.path import isfile
from zanshinsdk import Client, validate_uuid


class PersistenceEntry(object):
    """Class that encapsulates the minimal persistence information needed to continuously process
    only new alerts from a given organization."""

    def __init__(self, organization_id, scan_target_ids=None, cursor=None):

        if scan_target_ids is None:
            scan_target_ids = []
        if not validate_uuid(organization_id):
            raise ValueError('invalid organization ID')
        self._organization_id = organization_id

        if scan_target_ids:
            for scan_target_id in scan_target_ids:
                if not validate_uuid(scan_target_id):
                    raise ValueError('invalid Scan Target ID')
        self._scan_target_ids = scan_target_ids

        self._cursor = cursor

    @property
    def organization_id(self):
        """A string in UUID format containing the ID's of the organization."""
        return self._organization_id

    @property
    def scan_target_ids(self):
        """A string in UUID format containing the ID's of the Scan Target or Following."""
        return self._scan_target_ids

    @property
    def cursor(self):
        """A string representing the most recent alerts that has already been processed."""
        return self._cursor

    @cursor.setter
    def cursor(self, value):
        self._cursor = value

    def __str__(self):
        return "%s(organization_id=%s, scan_target_ids=%s, cursor=%s)" \
               % (self.__class__.__name__, self.organization_id, self.scan_target_ids, self.cursor)


class AbstractPersistentAlertsIterator(Iterator):
    """Abstract class that encapsulates the logic of walking through an organization's alerts in
    increasing batch date order and persisting state the prevents an alert from being seen multiple
    times across executions."""

    __metaclass__ = ABCMeta

    def __init__(self, client, organization_id, scan_target_ids=None, cursor=None):
        """Initializes a persistent alert iterator
        :param client: an instance of zanshinsdk.Client
        :param organization_id: a string containing an organization ID in UUID format
        :param scan_target_ids:
        :param cursor:
        """

        if scan_target_ids is None:
            scan_target_ids = []
        if not isinstance(client, Client):
            raise ValueError('invalid client')
        self._client = client

        if not validate_uuid(organization_id):
            raise ValueError('invalid organization ID')
        self._organization_id = organization_id

        if scan_target_ids:
            for scan_target_ids in scan_target_ids:
                if not validate_uuid(scan_target_ids):
                    raise ValueError('invalid Scan Target IDs')
        self._scan_target_ids = scan_target_ids

        self._cursor = cursor

        self._persistence_entry = None
        self._alerts = []

    @property
    def client(self):
        """Zanshin SDK client."""
        return self._client

    @property
    def organization_id(self):
        """A string in UUID format containing the ID's of the organization."""
        return self._organization_id

    @property
    def scan_target_ids(self):
        """A string in UUID format containing the ID's of the Scan Target."""
        return self._scan_target_ids

    @property
    def cursor(self):
        """A string in UUID format containing the ID's of the Scan Target or Following."""
        return self._cursor

    @property
    def persistence_entry(self):
        if not self._persistence_entry:
            self._persistence_entry = self._load()

            if self._persistence_entry is None:
                self._persistence_entry = PersistenceEntry(self.organization_id, self.scan_target_ids, self.cursor)
            else:
                if not isinstance(self._persistence_entry, PersistenceEntry):
                    raise ValueError('load method should return a PersistenceEntry instance')
                if not str(self._persistence_entry.organization_id) == str(self.organization_id):
                    raise ValueError(
                        'PersistenceEntry instance does not match organization ID: ' + self.organization_id)
                if tuple(self._persistence_entry.scan_target_ids) != self.scan_target_ids:
                    raise ValueError(
                        'PersistenceEntry instance does not match Scan Target IDs: ' + self.scan_target_ids)
        return self._persistence_entry

    @abstractmethod
    def _load(self):
        """Abstract method that loads a given organization's persistence data. Implementations
        should return a PersistenceEntry instance or None."""
        pass

    @abstractmethod
    def _save(self):
        """Abstract method that saves a given organization's persistence data."""
        pass

    def __iter__(self):
        return self

    def __next__(self):
        if not self._alerts:
            self._load_alerts()

        if self._alerts:
            alert = self._alerts.pop(0)
            self._persistence_entry.cursor = alert['cursor']
            self.save()
            return alert
        else:
            raise StopIteration

    def _load_alerts(self):
        # if we already have cached alerts, do nothing
        if self._alerts:
            return

        alerts_generator = self.client.iter_alerts_history(
            organization_id=self.persistence_entry.organization_id,
            scan_target_ids=self.persistence_entry.scan_target_ids,
            cursor=self.persistence_entry.cursor
        )

        for alert in alerts_generator:
            self._alerts.append(alert)

        # if alert cache is not empty, we are finished for now
        if self._alerts:
            return

    def save(self):
        self._save()

    def load(self):
        self._persistence_entry = None
        self._alerts = []

    def __str__(self):
        return "%s(organization_id=%s, scan_target_ids=%s, cursor=%s, persistence_entry=%s) " \
               % (self.__class__.__name__, self.organization_id, self.scan_target_ids, self.cursor,
                  self.persistence_entry)


class FilePersistentAlertsIterator(AbstractPersistentAlertsIterator):
    def __init__(self, filename, *args, **kwargs):
        super(FilePersistentAlertsIterator, self).__init__(*args, **kwargs)
        self._filename = filename

    @property
    def filename(self):
        return self._filename

    def _load(self):
        if isfile(self.filename):
            with open(self.filename, 'r') as f:
                pe = json.load(f)
                if 'cursor' in pe:
                    return PersistenceEntry(pe['organization_id'], pe['scan_target_ids'].split(), pe['cursor'])
        else:
            return None

    def _save(self):
        with open(self.filename, 'w') as f:
            pe = {
                'organization_id': str(self.persistence_entry.organization_id),
                'scan_target_ids': ','.join(self.persistence_entry.scan_target_ids),
                'cursor': str(self.persistence_entry.cursor)
            }
            json.dump(pe, f)

    def __str__(self):
        return super(FilePersistentAlertsIterator, self).__str__()[:-1] + ", filename=%s)" \
               % self._filename
