# -*- coding: utf-8 -*-
"""
This module allows persistent iteration of alerts. Some use cases include opening tickets based
on new alerts, or even automating responses for some high-confidence alerts.
"""
import json

from os.path import isfile
from typing import Dict, Iterator
from zanshinsdk.iterator import AbstractPersistentAlertsIterator, PersistenceEntry


class FilePersistentAlertsIterator(AbstractPersistentAlertsIterator):
    def __init__(self, filename, scan_target_ids, *args, **kwargs):
        super(FilePersistentAlertsIterator, self).__init__(field_name='scan_target_ids', filter_ids=scan_target_ids,
                                                           *args, **kwargs)
        self._filename = filename

    @property
    def filename(self):
        return self._filename

    def _load_alerts(self) -> Iterator[Dict]:
        return self.client.iter_alerts_history(
            organization_id=self.persistence_entry.organization_id,
            scan_target_ids=self.persistence_entry.filter_ids,
            cursor=self.persistence_entry.cursor
        )

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
                'scan_target_ids': ','.join([str(filter_id) for filter_id in self.persistence_entry.filter_ids]),
                'cursor': str(self.persistence_entry.cursor)
            }
            json.dump(pe, f)
