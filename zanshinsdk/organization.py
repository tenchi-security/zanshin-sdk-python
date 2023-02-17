from typing import Dict, Iterator, Optional, Union
from uuid import UUID

from client import validate_uuid

###################################################
# Organization
###################################################


def iter_organizations(self) -> Iterator[Dict]:
    """
    Iterates over organizations of current logged user.
    <https://api.zanshin.tenchisecurity.com/#operation/getOrganizations>
    :return: an iterator over the organizations objects
    """
    yield from self._request("GET", "/organizations").json()


def get_organization(self, organization_id: Union[UUID, str]) -> Dict:
    """
    Gets an organization given its ID.
    <https://api.zanshin.tenchisecurity.com/#operation/getOrganizationById>
    :param organization_id: the ID of the organization
    :return: a dict representing the organization detail
    """
    return self._request(
        "GET", f"/organizations/{validate_uuid(organization_id)}"
    ).json()


def delete_organization(self, organization_id: Union[UUID, str]) -> bool:
    """
    Deletes an organization given its ID.
    <https://api.zanshin.tenchisecurity.com/#operation/getOrganizationById>
    :param organization_id: the ID of the organization
    :return: a boolean if success
    """
    return self._request(
        "DELETE", f"/organizations/{validate_uuid(organization_id)}"
    ).json()


def update_organization(
    self,
    organization_id: Union[UUID, str],
    name: Optional[str],
    picture: Optional[str],
    email: Optional[str],
) -> Dict:
    """
    Update organization given its ID.
    <https://api.zanshin.tenchisecurity.com/#operation/editOrganizationById>
    :param organization_id: the ID of the organization
    :param name: the Name of the organization
    :param picture: the picture URL of the organization, accepted formats: jpg, jpeg, png, svg
    :param email: the e-mail contact of the organization
    :return: a dict representing the organization object
    """
    body = {"name": name, "picture": picture, "email": email}
    return self._request(
        "PUT", f"/organizations/{validate_uuid(organization_id)}", body=body
    ).json()


def create_organization(self, name: str) -> Dict:
    """
    Create organization.
    <https://api.zanshin.tenchisecurity.com/#operation/createOrganization>
    :param name: the Name of the organization
    :return: a dict representing the organization
    """
    body = {"name": name}
    return self._request("POST", f"/organizations", body=body).json()
