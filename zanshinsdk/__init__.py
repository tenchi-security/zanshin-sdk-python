__version__ = "1.2.0"

# set up package logger
import logging
logging.getLogger(__name__).addHandler(logging.NullHandler())

# import Connection class into namespace, but handle failure during setup if
# dependencies are not present yet
try:
    from zanshinsdk.client import Client, AlertState, AlertSeverity, ScanTargetKind, validate_uuid
    from zanshinsdk.iterator import AbstractPersistentAlertsIterator, PersistenceEntry
    from zanshinsdk.alerts_history import FilePersistentAlertsIterator
    from zanshinsdk.following_alerts_history import FilePersistentFollowingAlertsIterator
except ImportError:
    pass
