__version__ = "0.4.0"

# set up package logger
import logging
logging.getLogger(__name__).addHandler(logging.NullHandler())

# import Connection class into namespace, but handle failure during setup if
# dependencies are not present yet
try:
    from zanshinsdk.client import Client, AlertState, AlertSeverity, ScanTargetKind
except ImportError:
    pass
