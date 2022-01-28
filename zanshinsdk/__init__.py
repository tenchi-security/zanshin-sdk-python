__version__ = "1.2.0"

# set up package logger
import logging
logging.getLogger(__name__).addHandler(logging.NullHandler())

# import Connection class into namespace, but handle failure during setup if
# dependencies are not present yet
try:
    from zanshinsdk.client import Client, AlertState, AlertSeverity, ScanTargetKind, validate_uuid
except ImportError:
    pass
