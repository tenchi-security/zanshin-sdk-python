# -*- coding: utf-8 -*-
"""
This module allows persistent iteration of alerts. Some use cases include opening tickets based
on new alerts, or even automating responses for some high-confidence alerts.
"""
import json

from os.path import isfile
from zanshinsdk.iterator import AbstractPersistentAlertsIterator, PersistenceEntry


class FilePersistentFollowingAlertsIterator(AbstractPersistentAlertsIterator):
    def __init__(self, filename, following_ids, *args, **kwargs):
        super(FilePersistentFollowingAlertsIterator, self).__init__(field_name='following_ids',
                                                                    filter_ids=following_ids, *args, **kwargs)
        self._filename = filename

    @property
    def filename(self):
        return self._filename

    def _load_alerts(self):
        # if we already have cached alerts, do nothing
        if self._alerts:
            return

        alerts_generator = self.client.iter_alerts_following_history(
            organization_id=self.persistence_entry.organization_id,
            following_ids=self.persistence_entry.filter_ids,
            cursor=self.persistence_entry.cursor
        )

        for alert in alerts_generator:
            self._alerts.append(alert)

        # if alert cache is not empty, we are finished for now
        if self._alerts:
            return

    def _load(self):
        if isfile(self.filename):
            with open(self.filename, 'r') as f:
                pe = json.load(f)
                if 'cursor' in pe:
                    return PersistenceEntry(pe['organization_id'], pe['following_ids'].split(), pe['cursor'])
        else:
            return None

    def _save(self):
        with open(self.filename, 'w') as f:
            pe = {
                'organization_id': str(self.persistence_entry.organization_id),
                'following_ids': ','.join(self.persistence_entry.filter_ids),
                'cursor': str(self.persistence_entry.cursor)
            }
            json.dump(pe, f)
