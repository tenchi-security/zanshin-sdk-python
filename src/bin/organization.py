from typing import Dict, Iterator, Optional, Union
from uuid import UUID

from client import Client, validate_uuid

###################################################
# Organization
###################################################


def iter_organizations() -> Iterator[Dict]:
    """
    Iterates over organizations of current logged user.
    <https://api.zanshin.tenchisecurity.com/#operation/getOrganizations>
    :return: an iterator over the organizations objects
    """
    yield from Client._request("GET", "/organizations").json()


def get_organization(organization_id: Union[UUID, str]) -> Dict:
    """
    Gets an organization given its ID.
    <https://api.zanshin.tenchisecurity.com/#operation/getOrganizationById>
    :param organization_id: the ID of the organization
    :return: a dict representing the organization detail
    """
    return Client._request(
        "GET", f"/organizations/{validate_uuid(organization_id)}"
    ).json()


def delete_organization(organization_id: Union[UUID, str]) -> bool:
    """
    Deletes an organization given its ID.
    <https://api.zanshin.tenchisecurity.com/#operation/getOrganizationById>
    :param organization_id: the ID of the organization
    :return: a boolean if success
    """
    return Client._request(
        "DELETE", f"/organizations/{validate_uuid(organization_id)}"
    ).json()


def update_organization(
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
    return Client._request(
        "PUT", f"/organizations/{validate_uuid(organization_id)}", body=body
    ).json()


def create_organization(name: str) -> Dict:
    """
    Create organization.
    <https://api.zanshin.tenchisecurity.com/#operation/createOrganization>
    :param name: the Name of the organization
    :return: a dict representing the organization
    """
    body = {"name": name}
    return Client._request("POST", f"/organizations", body=body).json()
