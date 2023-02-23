import unittest

from src.bin.client import Client
from src.bin.scan_target_groups import (
    create_scan_target_by_compartments,
    create_scan_target_group,
    delete_organization_scan_target_group,
    get_organization_scan_target_group,
    get_scan_target_group_script,
    insert_scan_target_group_credential,
    iter_organization_scan_target_groups,
    iter_scan_target_group_compartments,
    iter_scan_targets_from_group,
    update_scan_target_group,
)
from src.lib.models import ScanTargetGroupCredentialListORACLE, ScanTargetKind


###################################################
# Organization Scan Target Groups
###################################################
class ScanTargetGroupsTest(unittest.TestCase):
    def test_iter_organization_scan_target_groups(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"

        try:
            next(iter_organization_scan_target_groups(organization_id))
        except StopIteration:
            pass

        Client._request.assert_called_once_with(
            "GET", f"/organizations/{organization_id}/scantargetgroups"
        )

        with self.assertRaises(TypeError):
            next(iter_organization_scan_target_groups(1))
        with self.assertRaises(TypeError):
            next(iter_organization_scan_target_groups(None))
        with self.assertRaises(ValueError):
            next(iter_organization_scan_target_groups(""))
        with self.assertRaises(ValueError):
            next(iter_organization_scan_target_groups("foo"))

    def test_get_organization_scan_target_group(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        scan_target_group_id = "322f4225-43e9-4922-b6b8-8b0620bdb110"

        get_organization_scan_target_group(organization_id, scan_target_group_id)

        Client._request.assert_called_once_with(
            "GET",
            f"/organizations/{organization_id}/scantargetgroups/{scan_target_group_id}",
        )
        with self.assertRaises(TypeError):
            get_organization_scan_target_group(None, scan_target_group_id)
        with self.assertRaises(TypeError):
            get_organization_scan_target_group(1, scan_target_group_id)
        with self.assertRaises(TypeError):
            get_organization_scan_target_group(organization_id, None)
        with self.assertRaises(TypeError):
            get_organization_scan_target_group(organization_id, 1)
        with self.assertRaises(ValueError):
            get_organization_scan_target_group(organization_id, "")
        with self.assertRaises(ValueError):
            get_organization_scan_target_group(organization_id, "foo")
        with self.assertRaises(ValueError):
            get_organization_scan_target_group("", scan_target_group_id)
        with self.assertRaises(ValueError):
            get_organization_scan_target_group("foo", scan_target_group_id)

    def test_update_scan_target_group(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        scan_target_group_id = "e22f4225-43e9-4922-b6b8-8b0620bdb110"
        name = "ScanTargetGroupTest"

        update_scan_target_group(organization_id, scan_target_group_id, name)

        Client._request.assert_called_once_with(
            "PUT",
            f"/organizations/{organization_id}/scantargetgroups/{scan_target_group_id}",
            body={"name": name},
        )

    def test_create_scan_target_group(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        kind = ScanTargetKind.ORACLE
        name = "ScanTargetTest"

        create_scan_target_group(organization_id, kind, name)

        with self.assertRaises(ValueError):
            create_scan_target_group(organization_id, ScanTargetKind.AWS, name)

        Client._request.assert_called_once_with(
            "POST",
            f"/organizations/{organization_id}/scantargetgroups",
            body={"name": name, "kind": kind},
        )

    def test_iter_scan_target_group_compartments(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        scan_target_group_id = "322f4225-43e9-4922-b6b8-8b0620bdb110"
        try:
            next(
                iter_scan_target_group_compartments(
                    organization_id, scan_target_group_id
                )
            )
        except StopIteration:
            pass
        Client._request.assert_called_once_with(
            "GET",
            f"/organizations/{organization_id}/scantargetgroups/{scan_target_group_id}/targets",
        )
        with self.assertRaises(TypeError):
            next(iter_scan_target_group_compartments(1, scan_target_group_id))
        with self.assertRaises(TypeError):
            next(iter_scan_target_group_compartments(None, scan_target_group_id))
        with self.assertRaises(ValueError):
            next(iter_scan_target_group_compartments("", scan_target_group_id))
        with self.assertRaises(ValueError):
            next(iter_scan_target_group_compartments("foo", scan_target_group_id))
        with self.assertRaises(TypeError):
            next(iter_scan_target_group_compartments(organization_id, 1))
        with self.assertRaises(TypeError):
            next(iter_scan_target_group_compartments(organization_id, None))
        with self.assertRaises(ValueError):
            next(iter_scan_target_group_compartments(organization_id, ""))
        with self.assertRaises(ValueError):
            next(iter_scan_target_group_compartments(organization_id, "foo"))

    def test_create_scan_target_by_compartments(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        scan_target_group_id = "322f4225-43e9-4922-b6b8-8b0620bdb110"

        ocid = "ocid"
        name = "ScanTargetTest"

        create_scan_target_by_compartments(
            organization_id, scan_target_group_id, name, ocid
        )

        compartments = [{"name": name, "ocid": ocid}]

        body = {"compartments": compartments}

        Client._request.assert_called_once_with(
            "POST",
            f"/organizations/{organization_id}/scantargetgroups/{scan_target_group_id}/targets",
            body=body,
        )

    def test_iter_scan_targets_from_group(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        scan_target_group_id = "322f4225-43e9-4922-b6b8-8b0620bdb110"

        try:
            next(iter_scan_targets_from_group(organization_id, scan_target_group_id))
        except StopIteration:
            pass

        Client._request.assert_called_once_with(
            "GET",
            f"/organizations/{organization_id}/scantargetgroups/{scan_target_group_id}/scantargets",
        )

        with self.assertRaises(TypeError):
            next(iter_scan_targets_from_group(1, scan_target_group_id))
        with self.assertRaises(TypeError):
            next(iter_scan_targets_from_group(None, scan_target_group_id))
        with self.assertRaises(ValueError):
            next(iter_scan_targets_from_group("", scan_target_group_id))
        with self.assertRaises(ValueError):
            next(iter_scan_targets_from_group("foo", scan_target_group_id))
        with self.assertRaises(TypeError):
            next(iter_scan_targets_from_group(organization_id, 1))
        with self.assertRaises(TypeError):
            next(iter_scan_targets_from_group(organization_id, None))
        with self.assertRaises(ValueError):
            next(iter_scan_targets_from_group(organization_id, ""))
        with self.assertRaises(ValueError):
            next(iter_scan_targets_from_group(organization_id, "foo"))

    def test_delete_organization_scan_target_group(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        scan_target_id_group = "e22f4225-43e9-4922-b6b8-8b0620bdb110"

        delete_organization_scan_target_group(organization_id, scan_target_id_group)

        Client._request.assert_called_once_with(
            "DELETE",
            f"/organizations/{organization_id}/scantargetgroups/{scan_target_id_group}",
        )
        with self.assertRaises(TypeError):
            delete_organization_scan_target_group(None, scan_target_id_group)
        with self.assertRaises(TypeError):
            delete_organization_scan_target_group(1, scan_target_id_group)
        with self.assertRaises(TypeError):
            delete_organization_scan_target_group(organization_id, None)
        with self.assertRaises(TypeError):
            delete_organization_scan_target_group(organization_id, 1)
        with self.assertRaises(ValueError):
            delete_organization_scan_target_group(organization_id, "")
        with self.assertRaises(ValueError):
            delete_organization_scan_target_group(organization_id, "foo")
        with self.assertRaises(ValueError):
            delete_organization_scan_target_group("", scan_target_id_group)
        with self.assertRaises(ValueError):
            delete_organization_scan_target_group("foo", scan_target_id_group)

    def test_get_scan_target_group_script(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        scan_target_group_id = "322f4225-43e9-4922-b6b8-8b0620bdb110"

        get_scan_target_group_script(organization_id, scan_target_group_id)

        Client._request.assert_called_once_with(
            "GET",
            f"/organizations/{organization_id}/scantargetgroups/{scan_target_group_id}/scripts",
        )
        with self.assertRaises(TypeError):
            get_scan_target_group_script(None, scan_target_group_id)
        with self.assertRaises(TypeError):
            get_scan_target_group_script(1, scan_target_group_id)
        with self.assertRaises(TypeError):
            get_scan_target_group_script(organization_id, None)
        with self.assertRaises(TypeError):
            get_scan_target_group_script(organization_id, 1)
        with self.assertRaises(ValueError):
            get_scan_target_group_script(organization_id, "")
        with self.assertRaises(ValueError):
            get_scan_target_group_script(organization_id, "foo")
        with self.assertRaises(ValueError):
            get_scan_target_group_script("", scan_target_group_id)
        with self.assertRaises(ValueError):
            get_scan_target_group_script("foo", scan_target_group_id)

    def test_insert_scan_target_group_credential(self):
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        scan_target_group_id = "e22f4225-43e9-4922-b6b8-8b0620bdb110"
        credential = ScanTargetGroupCredentialListORACLE(
            "us-ashburn-1",
            "ocid1.tenancy.oc1..aaaaaaaa0000000000000000000000000000000000000000000000000000",
            "ocid1.user.oc1..aaaaaaaa0000000000000000000000000000000000000000000000000000",
            "1a:1a:aa:1a:11:11:aa:11:11:11:1a:1a:1a:a:1a:1a",
        )

        insert_scan_target_group_credential(
            organization_id, scan_target_group_id, credential
        )

        Client._request.assert_called_once_with(
            "POST",
            f"/organizations/{organization_id}/scantargetgroups/{scan_target_group_id}",
            body={"credential": credential},
        )
        with self.assertRaises(TypeError):
            insert_scan_target_group_credential(None, scan_target_group_id, credential)
        with self.assertRaises(TypeError):
            insert_scan_target_group_credential(1, scan_target_group_id, credential)
        with self.assertRaises(TypeError):
            insert_scan_target_group_credential(organization_id, None, credential)
        with self.assertRaises(TypeError):
            insert_scan_target_group_credential(organization_id, 1, credential)
        with self.assertRaises(ValueError):
            insert_scan_target_group_credential(organization_id, "", credential)
        with self.assertRaises(ValueError):
            insert_scan_target_group_credential(organization_id, "foo", credential)
        with self.assertRaises(ValueError):
            insert_scan_target_group_credential("", scan_target_group_id, credential)
        with self.assertRaises(ValueError):
            insert_scan_target_group_credential("foo", scan_target_group_id, credential)
