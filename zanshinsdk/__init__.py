from zanshinsdk.client import Client, AlertState, AlertSeverity, ScanTargetKind, ScanTargetSchedule, Languages, \
    AlertsOrderOpts, SortOpts, ScanTargetAWS, ScanTargetAZURE, ScanTargetGCP, ScanTargetHUAWEI, ScanTargetDOMAIN, Roles, validate_uuid
from zanshinsdk.iterator import AbstractPersistentAlertsIterator, PersistenceEntry
from zanshinsdk.alerts_history import FilePersistentAlertsIterator
from zanshinsdk.following_alerts_history import FilePersistentFollowingAlertsIterator
from zanshinsdk.version import __version__

import logging

logging.getLogger(__name__).addHandler(logging.NullHandler())
