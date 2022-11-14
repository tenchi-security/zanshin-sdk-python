from __future__ import annotations

from .client import Client, ScanTargetKind, ScanTargetSchedule
from .protect_attributes import protect_attributes

from dataclasses import dataclass, field
import datetime
from typing import Optional, Set, Union, Iterator
from uuid import UUID
from enum import Enum
from types import MethodType

from dateutil.parser import parse


class OOClient(object):
    """
    Main object-oriented class used to access the Zanshin API. Wraps around <zanshinsdk.client.Client> and provides
    a more pythonic and object-oriented way to interact with the API.
    """

    def __init__(self, *args, **kwargs):
        """
        Initialize a new connection to the Zanshin API, passing along all parameters to <zanshinsdk.client.Client.__init__>.
        """
        self._client = Client(*args, **kwargs)

    @property
    def client(self) -> Client:
        """

        Returns: the underlying <zanshinsdk.client.Client> instance used by this object.

        """
        return self._client

    def organization(self, id: Union[UUID, str]) -> Organization:
        """
        Gets an organization based on its identifier.
        Args:
            id: a valid organization ID (string or UUID)

        Returns: an instance of <zanshinsdk.ooclient.Organization>

        """
        return Organization.from_dict(self, self.client.get_organization(id))

    def iter_organizations(self) -> Iterator[Organization]:
        """
        Iterates over the organizations the credentials used to authenticate to the API have access to.
        Returns: the <zanshinsdk.ooclient.Organization> instances

        """
        for org in self.client.iter_organizations():
            yield Organization.from_dict(self, org)


class OrganizationStatus(str, Enum):
    """
    List of states an organization can be in.
    """
    ACTIVE = "ACTIVE"           """Organization is healthy."""
    SUSPENDED = "SUSPENDED"     """Organization is suspended, meaning no new scans are performed."""


@dataclass(eq=False, order=False)
@protect_attributes
class Organization(object):
    ooclient: OOClient = field(metadata={'nodel': True})
    id: UUID = field(metadata={'readonly': True})
    name: str = field(metadata={'nodel': True})
    status: OrganizationStatus = field(metadata={'readonly': True})
    updatedAt: datetime = field(metadata={'readonly': True})
    email: Optional[str] = field(default=None, metadata={'nodel': True})
    picture: Optional[str] = field(default=None, metadata={'nodel': True})
    features: Set[str] = field(default_factory=set, metadata={'nodel': True})

    @classmethod
    def from_dict(cls, ooclient: OOClient, data: dict):
        return Organization(
            ooclient=ooclient,
            id=UUID(data['id']),
            name=data['name'],
            status=OrganizationStatus[data['status']],
            updatedAt=parse(data['updatedAt']),
            email=data.get('email', None) or None,
            picture=data.get('picture', None) or None,
            features=set(data.get('features', []))
        )


class ScanTargetStatus(enum):
    NEW = "NEW"
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"
    ERROR = "ERROR"
    RUNNING = "RUNNING"
    INVALID_CREDENTIAL = "INVALID_CREDENTIAL"


@dataclass(eq=False, order=False)
@protect_attributes
class ScanTarget(object):
    ooclient: OOClient = field(repr=False, hash=False, compare=False, metadata={'nodel': True})
    id: UUID = field(metadata={'readonly': True})
    organization: Organization = field(metadata={'readonly': True})
    name: str = field(metadata={'nodel': True})
    kind: ScanTargetKind = field(metadata={'readonly': True})
    status: ScanTargetStatus = field(metadata={'readonly': True})
    updatedAt: datetime = field(metadata={'readonly': True})
    lastScan: datetime = field(metadata={'readonly': True})
    account: str = field(metadata={'nodel': True})
    schedule: ScanTargetSchedule = field(metadata={'nodel': True})

    def from_dict(cls, ooclient: OOClient, data: dict):
        return Organization(
            ooclient=ooclient,
            id=UUID(data['id']),
            name=data['name'],
            status=OrganizationStatus[data['status']],
            updatedAt=parse(data['updatedAt']),
            email=data.get('email', None) or None,
            picture=data.get('picture', None) or None,
            features=set(data.get('features', []))
        )
