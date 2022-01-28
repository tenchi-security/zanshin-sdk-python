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


class PersistenceFollowingEntry(object):
    """Class that encapsulates the minimal persistence information needed to continuously process
    only new alerts from a given organization."""

    def __init__(self, organization_id, following_ids=None, cursor=None):

        if following_ids is None:
            following_ids = []
        if not validate_uuid(organization_id):
            raise ValueError('invalid organization ID')
        self._organization_id = organization_id

        if following_ids:
            for following_id in following_ids:
                if not validate_uuid(following_id):
                    raise ValueError('invalid Following ID')
        self._following_ids = following_ids

        self._cursor = cursor

    @property
    def organization_id(self):
        """A string in UUID format containing the ID's of the organization."""
        return self._organization_id

    @property
    def following_ids(self):
        """A string in UUID format containing the ID's of the Scan Target or Following."""
        return self._following_ids

    @property
    def cursor(self):
        """A string representing the most recent alerts that has already been processed."""
        return self._cursor

    @cursor.setter
    def cursor(self, value):
        self._cursor = value

    def __str__(self):
        return "%s(organization_id=%s, following_ids=%s, cursor=%s)" \
               % (self.__class__.__name__, self.organization_id, self.following_ids, self.cursor)


class AbstractPersistentFollowingAlertsIterator(Iterator):
    """Abstract class that encapsulates the logic of walking through an organization's alerts in
    increasing batch date order and persisting state the prevents an alert from being seen multiple
    times across executions."""

    __metaclass__ = ABCMeta

    def __init__(self, client, organization_id, following_ids=None, cursor=None):
        """Initializes a persistent alert iterator
        :param client: an instance of zanshinsdk.Client
        :param organization_id: a string containing an organization ID in UUID format
        :param following_ids:
        :param cursor:
        """

        if following_ids is None:
            following_ids = []
        if not isinstance(client, Client):
            raise ValueError('invalid client')
        self._client = client

        if not validate_uuid(organization_id):
            raise ValueError('invalid organization ID')
        self._organization_id = organization_id

        if following_ids:
            for following_ids in following_ids:
                if not validate_uuid(following_ids):
                    raise ValueError('invalid Scan Target IDs')
        self._following_ids = following_ids

        self._cursor = cursor

        self._persistence_following_entry = None
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
    def following_ids(self):
        """A string in UUID format containing the ID's of the Scan Target."""
        return self._following_ids

    @property
    def cursor(self):
        """A string in UUID format containing the ID's of the Scan Target or Following."""
        return self._cursor

    @property
    def persistence_following_entry(self):
        if not self._persistence_following_entry:
            self._persistence_following_entry = self._load()

            if self._persistence_following_entry is None:
                self._persistence_following_entry = PersistenceFollowingEntry(self.organization_id, self.following_ids,
                                                                              self.cursor)
            else:
                if not isinstance(self._persistence_following_entry, PersistenceFollowingEntry):
                    raise ValueError('load method should return a PersistenceEntry instance')
                if not str(self._persistence_following_entry.organization_id) == str(self.organization_id):
                    raise ValueError(
                        'PersistenceEntry instance does not match organization ID: ' + self.organization_id)
                if tuple(self._persistence_following_entry.following_ids) != self.following_ids:
                    raise ValueError(
                        'PersistenceEntry instance does not match Scan Target IDs: ' + self.following_ids)
        return self._persistence_following_entry

    @persistence_following_entry.setter
    def persistence_following_entry(self, value):
        self._persistence_following_entry = value

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
            self.persistence_following_entry.cursor = alert['cursor']
            return alert
        else:
            raise StopIteration

    def _load_alerts(self):
        # if we already have cached alerts, do nothing
        if self._alerts:
            return

        alerts_generator = self.client.iter_alerts_following_history(
            organization_id=self.persistence_following_entry.organization_id,
            following_ids=self.persistence_following_entry.following_ids,
            cursor=self.persistence_following_entry.cursor
        )

        for alert in alerts_generator:
            self._alerts.append(alert)

        # if alert cache is not empty, we are finished for now
        if self._alerts:
            return

    def save(self):
        self._save()

    def load(self):
        self.persistence_following_entry = None
        self._alerts = []

    def __str__(self):
        return "%s(organization_id=%s, following_ids=%s, cursor=%s, persistence_entry=%s) " \
               % (self.__class__.__name__, self.organization_id, self.following_ids, self.cursor,
                  self.persistence_following_entry)


class FilePersistentFollowingAlertsIterator(AbstractPersistentFollowingAlertsIterator):
    def __init__(self, filename, *args, **kwargs):
        super(FilePersistentFollowingAlertsIterator, self).__init__(*args, **kwargs)
        self._filename = filename

    @property
    def filename(self):
        return self._filename

    def _load(self):
        if isfile(self.filename):
            with open(self.filename, 'r') as f:
                pe = json.load(f)
                if 'cursor' in pe:
                    return PersistenceFollowingEntry(pe['organization_id'], pe['following_ids'].split(), pe['cursor'])
        else:
            return None

    def _save(self):
        with open(self.filename, 'w') as f:
            pe = {
                'organization_id': str(self.persistence_following_entry.organization_id),
                'following_ids': ','.join(self.persistence_following_entry.following_ids),
                'cursor': str(self.persistence_following_entry.cursor)
            }
            json.dump(pe, f)

    def __str__(self):
        return super(FilePersistentFollowingAlertsIterator, self).__str__()[:-1] + ", filename=%s)" \
               % self.filename
