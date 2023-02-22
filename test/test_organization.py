import unittest

from src.bin.client import Client
from src.bin.organization import (
    create_organization,
    delete_organization,
    get_organization,
    iter_organizations,
    update_organization,
)

###################################################
# Organization
###################################################


class OrganizationsTest(unittest.TestCase):
    def test_iter_organizations(self):
        try:
            next(iter_organizations())
        except StopIteration:
            pass

        Client._request.assert_called_once_with("GET", "/organizations")

    def test_get_organization(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"

        get_organization(organization_id)

        Client._request.assert_called_once_with(
            "GET", f"/organizations/{organization_id}"
        )

    def test_delete_organization(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"

        delete_organization(organization_id)

        Client._request.assert_called_once_with(
            "DELETE", f"/organizations/{organization_id}"
        )

    def test_update_organization(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        name = "Tabajara"
        picture = "https://pic-store.com/pic1.png"
        email = "ceo@tabajara.com.br"

        update_organization(organization_id, name, picture, email)

        Client._request.assert_called_once_with(
            "PUT",
            f"/organizations/{organization_id}",
            body={"name": name, "picture": picture, "email": email},
        )

    def test_create_organization(self):
        name = "Tabajara"

        create_organization(name)

        Client._request.assert_called_once_with(
            "POST", f"/organizations", body={"name": name}
        )
