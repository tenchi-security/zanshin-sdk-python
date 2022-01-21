# -*- coding: utf-8 -*-
"""
This module allows persistent iteration of alerts. Some use cases include opening tickets based
on new alerts, or even automating responses for some high-confidence alerts.
"""
import json
from abc import ABCMeta, abstractmethod
from collections import Iterable, Iterator
from os.path import isfile

class PersistenceEntry(object):
    """Class that encapsulates the minimal persistence information needed to continuously process
    only new alerts from a given organization."""

    @property
    def organization_id(self):
        """A string in UUID format containing the ID's of the organization."""
        return self._organization_id

    @property
    def filter_ids(self):
        """A string in UUID format containing the ID's of the Scan Target or Following."""
        return self._filter_ids

    @property
    def latest_api_cursor(self):
        """A string representing the most recent alerts that has already been processed."""
        return self._latest_api_cursor

    def __init__(self, organization_id, filter_ids=None, latest_api_cursor=None):
        if not is_valid_uuid(organization_id):
            raise ValueError('invalid organization ID')
        self._organization_id = organization_id

        if filter_ids:
            for filter_id in filter_ids:
              if not is_valid_uuid(filter_id):
                  raise ValueError('invalid Scan Target/Following ID')
        self._filter_ids = filter_ids

        self._latest_api_cursor = latest_api_cursor

    def __str__(self):
        return "%s(organization_id=%s, filter_ids=%s, latest_api_cursor=%s)" \
               % (self.__class__.__name__, self.organization_id, self.filter_ids, self.latest_api_cursor)

class AbstractPersistentAlertIterator(Iterator):
    """Abstract class that encapsulates the logic of walking through an organization's alerts in
    increasing batch date order and persisting state the prevents an alert from being seen multiple
    times across executions."""

    __metaclass__ = ABCMeta

    def __init__(self, organization_id, filter_ids=None):
        """Initializes a persistent alert iterator.
        :param organization_id: a string containing an organization ID in UUID format
        """

        if not is_valid_uuid(organization_id):
            raise ValueError('invalid organization ID')
        self._organization_id = organization_id

        if filter_ids:
            for filter_id in filter_ids:
              if not is_valid_uuid(filter_id):
                  raise ValueError('invalid Scan Target/Following ID')
        self._filter_ids = filter_ids

    @property
    def organization_id(self):
        """A string in UUID format containing the ID's of the organization."""
        return self._organization_id

    @property
    def filter_ids(self):
        """A string in UUID format containing the ID's of the Scan Target or Following."""
        return self._filter_ids

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

    def load(self):
        self._load()

    def save(self):
        self._save()

class FilePersistentAlertIterator(AbstractPersistentAlertIterator):
    def __init__(self, filename, *args, **kwargs):
        self._filename = filename
        super(FilePersistentAlertIterator, self).__init__(*args, **kwargs)

    @property
    def filename(self):
        return self._filename

    def _load(self):
        if isfile(self._filename):
            with open(self._filename, 'r') as f:
                pe = json.load(f)
                if 'latest_api_cursor' in pe:
                    return PersistenceEntry(pe['organization_id'], pe['filter_ids'], pe['latest_api_cursor'])
        else:
            return None

    def _save(self):
        pe = {
            'organization_id': str(self.persistence_entry.organization_id),
            'filter_ids': str(self.persistence_entry.filter_ids),
            'latest_api_cursor': self.persistence_entry.latest_api_cursor
        }
        with open(self._filename, 'w') as f:
            json.dump(pe, f)

    def __str__(self):
        return super(FilePersistentAlertIterator, self).__str__()[:-1] + ", filename=%s)" \
                                                                         % self._filename