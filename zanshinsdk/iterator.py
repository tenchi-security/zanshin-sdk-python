# -*- coding: utf-8 -*-
"""
This module allows persistent iteration of alerts. Some use cases include opening tickets based
on new alerts, or even automating responses for some high-confidence alerts.
"""
from abc import ABCMeta, abstractmethod
from typing import Dict, Iterator
from zanshinsdk import Client, validate_uuid


class PersistenceEntry(object):
    """Class that encapsulates the minimal persistence information needed to continuously process
    only new alerts from a given organization."""

    def __init__(self, organization_id, filter_ids=None, cursor=None):
        """Initializes a persistent alert iterator
        :param organization_id: a string containing an organization ID in UUID format
        :param filter_ids:
        :param cursor:
        """

        try:
            validate_uuid(organization_id)
        except:
            raise ValueError("invalid organization ID")
        self._organization_id = organization_id

        if filter_ids is None:
            filter_ids = []

        if filter_ids:
            for filter_id in filter_ids:
                try:
                    validate_uuid(filter_id)
                except:
                    raise ValueError("invalid filter ID")
        self._filter_ids = filter_ids

        self._cursor = cursor

    @property
    def organization_id(self):
        """A string in UUID format containing the ID's of the organization."""
        return self._organization_id

    @property
    def filter_ids(self):
        """A string in UUID format containing the ID's of the Scan Target or Following."""
        return self._filter_ids

    @property
    def cursor(self):
        """A string representing the most recent alerts that has already been processed."""
        return self._cursor

    @cursor.setter
    def cursor(self, value):
        self._cursor = value


class AbstractPersistentAlertsIterator(Iterator):
    """Abstract class that encapsulates the logic of walking through an organization's alerts in
    increasing batch date order and persisting state the prevents an alert from being seen multiple
    times across executions."""

    __metaclass__ = ABCMeta

    def __init__(self, field_name, client, organization_id, filter_ids=None, cursor=None):
        """Initializes a persistent alert iterator
        :param field_name:
        :param client: an instance of zanshinsdk.Client
        :param organization_id: a string containing an organization ID in UUID format
        :param filter_ids:
        :param cursor:
        """

        self._field_name = field_name

        if filter_ids is None:
            filter_ids = []

        if not isinstance(client, Client):
            raise ValueError("invalid client")
        self._client = client

        try:
            validate_uuid(organization_id)
        except:
            raise ValueError("invalid organization ID")
        self._organization_id = organization_id

        if filter_ids:
            for filter_id in filter_ids:
                try:
                    validate_uuid(filter_id)
                except:
                    raise ValueError(f"invalid {field_name} ID")
        self._filter_ids = filter_ids

        self._cursor = cursor

        self._persistence_entry = None
        self._alerts = []

    @property
    def client(self):
        """Zanshin SDK client."""
        return self._client

    @property
    def persistence_entry(self):
        if not self._persistence_entry:
            self._persistence_entry = self._load()

            if self._persistence_entry is None:
                self._persistence_entry = PersistenceEntry(self._organization_id, self._filter_ids, self._cursor)
            else:
                if not isinstance(self._persistence_entry, PersistenceEntry):
                    raise ValueError("load method should return a PersistenceEntry instance")
                if not str(self._persistence_entry.organization_id) == str(self._organization_id):
                    raise ValueError(
                        f"PersistenceEntry instance does not match organization ID: {str(self._organization_id)}")
                if ",".join([str(filter_id) for filter_id in self._persistence_entry.filter_ids]) !=\
                        ",".join([str(filter_id) for filter_id in self._filter_ids]):
                    raise ValueError(
                        f"PersistenceEntry instance does not match {self._field_name} IDs: " +
                        ",".join([str(filter_id) for filter_id in self._filter_ids]))
        return self._persistence_entry

    @abstractmethod
    def _load(self):
        """Abstract method that loads a given organization's persistence data. Implementations
        should return a PersistenceEntry instance or None."""

    @abstractmethod
    def _save(self):
        """Abstract method that saves a given organization's persistence data."""

    @abstractmethod
    def _load_alerts(self) -> Iterator[Dict]:
        """Abstract method that saves a given organization's persistence data."""

    def __next__(self):
        if not self._alerts:
            self._alerts = self.load_alerts()

        if self._alerts:
            alert = next(self._alerts)
            self.persistence_entry.cursor = alert["cursor"]
            return alert
        else:
            raise StopIteration

    def save(self):
        self._save()

    def load(self):
        self._persistence_entry = None
        self._alerts = []

    def load_alerts(self) -> Iterator[Dict]:
        return self._load_alerts()
