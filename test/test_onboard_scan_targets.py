import os
import unittest
from pathlib import Path
from unittest.mock import Mock, mock_open, patch

import boto3
from moto import mock_cloudformation, mock_s3, mock_sts

from src.bin.client import Client, ScanTargetAWS, ScanTargetAZURE, ScanTargetKind
from src.bin.onboard_scan_targets import onboard_scan_target

###################################################
# __mock_aws_credentials__
###################################################


def mock_aws_credentials(self):
    """Mocked AWS Credentials for moto."""
    moto_credentials_file_path = (
        Path(__file__).parent.absolute() / "dummy_aws_credentials"
    )
    os.environ["AWS_SHARED_CREDENTIALS_FILE"] = str(moto_credentials_file_path)


###################################################
# Onboard Scan Targets
###################################################


class OnboardScanTargetsTest(unittest.TestCase):
    def test_onboard_scan_target_unsupported_scan_target_kind(self):
        """
        Call onboard_scan_target with an scan target different than AWS. Currently we support only AWS for
        onboard via SDK.

        :param region: str
        :param organization_id: str
        :param kind: ScanTargetKind.AZURE
        :param credential: ScanTargetAZURE
        :param boto3_profile: str
        :param schedule: str

        :raises: Exception Onboard does\'t support given environment yet


        >>> self.sdk.onboard_scan_target(
                region, organization_id, kind, name, credential, None, boto3_profile, schedule)
        raises:
        >>> Onboard doesn't support AZURE environment yet
        """
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        kind = ScanTargetKind.AZURE
        name = "OnboardTesting-it"
        credential = ScanTargetAZURE("4321", "1234", "1234", "s3cr3t")
        schedule = "0 0 * * *"
        region = "us-east-1"
        boto3_profile = "foo"

        try:
            onboard_scan_target(
                region,
                organization_id,
                kind,
                name,
                credential,
                None,
                boto3_profile,
                schedule,
            )
        except Exception as e:
            self.assertEqual(str(e), "Onboard doesn't support AZURE environment yet")

    @unittest.skipIf("HAVE_BOTO3", "requires not have boto3")
    def test_onboard_scan_target_aws_missing_boto3(self):
        """
        Call onboard_scan_target without boto3 installed.
        Skip this test unless boto3 is installed in environment.

        :param region: str
        :param organization_id: str
        :param kind: ScanTargetKind.AZURE
        :param credential: ScanTargetAZURE
        :param boto3_profile: str
        :param schedule: str

        :raises: boto3 not present. boto3 is required to perform AWS onboard.


        >>> self.sdk.onboard_scan_target(
                region, organization_id, kind, name, credential, None, boto3_profile, schedule)
        raises:
        >>> boto3 not present. boto3 is required to perform AWS onboard.
        """
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        kind = ScanTargetKind.AWS
        name = "OnboardTesting-it"
        credential = ScanTargetAWS("4321")
        schedule = "0 0 * * *"
        region = "us-east-1"
        boto3_profile = "foo"

        try:
            onboard_scan_target(
                region,
                organization_id,
                kind,
                name,
                credential,
                None,
                boto3_profile,
                schedule,
            )
        except Exception as e:
            self.assertEqual(
                str(e), "boto3 not present. boto3 is required to perform AWS onboard."
            )

    @unittest.skipUnless("HAVE_BOTO3", "requires boto3")
    def test_onboard_scan_target_aws_invalid_credentials_boto3_profile(self):
        """
        Call onboard_scan_target passing a non-existing boto3_profile.
        Skip this test unless boto3 is installed in environment.

        :param region: str
        :param organization_id: str
        :param kind: ScanTargetKind.AZURE
        :param credential: ScanTargetAZURE
        :param boto3_profile: str
        :param schedule: str

        :raises: The config profile (non_default) could not be found


        >>> self.sdk.onboard_scan_target(
                region, organization_id, kind, name, credential, None, boto3_profile, schedule)
        raises:
        >>> The config profile (non_default) could not be found
        """
        mock_aws_credentials()
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        kind = ScanTargetKind.AWS
        name = "OnboardTesting-it"
        credential = ScanTargetAWS("4321")
        schedule = "0 0 * * *"
        region = "us-east-1"
        boto3_profile = "non_default"

        try:
            onboard_scan_target(
                region=region,
                organization_id=organization_id,
                kind=kind,
                name=name,
                credential=credential,
                boto3_profile=boto3_profile,
                schedule=schedule,
            )
        except Exception as e:
            self.assertEqual(
                str(e), "The config profile (non_default) could not be found"
            )

    @unittest.skipUnless("HAVE_BOTO3", "requires boto3")
    def test_onboard_scan_target_aws_invalid_credentials_boto3_session(self):
        """
        Call onboard_scan_target passing an invalid boto3_session.
        Skip this test unless boto3 is installed in environment.

        :param region: str
        :param organization_id: str
        :param kind: ScanTargetKind.AZURE
        :param credential: ScanTargetAZURE
        :param boto3_profile: str
        :param schedule: str

        :raises: boto3 session is invalid. Working boto3 session is required.


        >>> self.sdk.onboard_scan_target(
                region, organization_id, kind, name, credential, None, boto3_profile, schedule)
        raises:
        >>> boto3 session is invalid. Working boto3 session is required.
        """
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        kind = ScanTargetKind.AWS
        name = "OnboardTesting-it"
        credential = ScanTargetAWS("4321")
        region = "us-east-1"

        try:
            boto3_session = boto3.Session(
                aws_access_key_id="EXAMPLE_NON_EXISTING_KEY",
                aws_secret_access_key="&x@mP|e$3cReT",
                aws_session_token="session_token",
            )
            onboard_scan_target(
                region=region,
                organization_id=organization_id,
                kind=kind,
                name=name,
                credential=credential,
                boto3_session=boto3_session,
            )
        except Exception as e:
            self.assertEqual(
                str(e), "boto3 session is invalid. Working boto3 session is required."
            )

    @unittest.skipUnless("HAVE_BOTO3", "requires boto3")
    @patch("zanshinsdk.client.isfile")
    @patch("zanshinsdk.Client._request")
    @mock_sts
    @mock_cloudformation
    @mock_s3
    def test_onboard_scan_target_aws_boto3_profile(self, request, mock_is_file):
        """
        Call onboard_scan_target with valid boto3_profile.
        Skip this test unless boto3 is installed in environment.
        Mock the creation of a new Scan Target, and behavior of AWS Services STS, CloudFormation and S3.

        :param region: str
        :param organization_id: str
        :param kind: ScanTargetKind.AZURE
        :param credential: ScanTargetAZURE
        :param boto3_profile: str
        :param schedule: str

        Asserts:
        * New Scan Target was created, with given parameters.
        * Scan was Started for this new Scan Target.
        * CloudFormation with Zanshin Role was deployed sucessfully.

        >>> new_scan_target = self.sdk.onboard_scan_target(
                region, organization_id, kind, name, credential, None, boto3_profile, schedule)
        """
        import json

        # Setup test data
        aws_account_id = "123456789012"
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        created_scan_target_id = "14f79567-6b68-4e3a-b2f2-4f1383546251"
        kind = ScanTargetKind.AWS
        name = "OnboardTesting-it"
        credential = ScanTargetAWS(aws_account_id)
        schedule = "24h"
        region = "us-east-1"
        boto3_profile = "foo"

        # Mock AWS Credentials for Boto3
        mock_aws_credentials()

        # Mock request to create new Scan Target
        mock_is_file.return_value = True
        _data = "[default]\napi_key=api_key"

        with patch("__main__.__builtins__.open", mock_open(read_data=_data)):
            request.return_value = Mock(
                status_code=200, json=lambda: {"id": created_scan_target_id}
            )
            client = Client()
            client._client.request = request

        # Create Mocked S3 tenchi-assets bucket
        with open(
            "zanshinsdk/dummy_cloudformation_zanshin_service_role_template.json", "r"
        ) as dummy_template_file:
            DUMMY_TEMPLATE = json.load(dummy_template_file)
            s3 = boto3.client("s3", region_name="us-east-2")
            s3.create_bucket(
                Bucket="tenchi-assets",
                CreateBucketConfiguration={"LocationConstraint": "us-east-2"},
            )
            s3.put_object(
                Bucket="tenchi-assets",
                Key="zanshin-service-role.template",
                Body=json.dumps(DUMMY_TEMPLATE),
            )

        # Call method onboard_scan_target with boto3_profile
        new_scan_target = client.onboard_scan_target(
            region,
            organization_id,
            kind,
            name,
            credential,
            None,
            boto3_profile,
            schedule,
        )

        # Assert that Scan Target was created
        self.assertEqual(created_scan_target_id, new_scan_target["id"])

        # Assert that Scan Target was called with correct parameters
        client._client.request.assert_any_call(
            "POST",
            f"/organizations/{organization_id}/scantargets",
            body={
                "name": name,
                "kind": kind,
                "schedule": schedule,
                "credential": {"account": aws_account_id},
            },
        )
        # Assert that we checked Scan Target to start scan
        client._client.request.assert_any_call(
            "POST",
            f"/organizations/{organization_id}/scantargets/{created_scan_target_id}/check",
        )

        # Assert CloudFormation Stack was created successfully
        zanshin_cloudformation_stack_name = "tenchi-zanshin-service-role"
        cloudformation = boto3.client("cloudformation", region_name="us-east-1")
        zanshin_stack = cloudformation.describe_stacks(
            StackName=zanshin_cloudformation_stack_name
        )["Stacks"][0]
        self.assertEqual("CREATE_COMPLETE", zanshin_stack["StackStatus"])
        self.assertEqual(zanshin_cloudformation_stack_name, zanshin_stack["StackName"])

        # Clean Up CloudFormation
        cf_stacks = cloudformation.describe_stacks(
            StackName=zanshin_cloudformation_stack_name
        )
        for cf_stack in cf_stacks["Stacks"]:
            cloudformation.delete_stack(StackName=cf_stack["StackName"])

    @unittest.skipUnless("HAVE_BOTO3", "requires boto3")
    @patch("zanshinsdk.client.isfile")
    @patch("zanshinsdk.Client._request")
    @mock_sts
    @mock_cloudformation
    @mock_s3
    def test_onboard_scan_target_aws_boto3_session(self, request, mock_is_file):
        """
        Call onboard_scan_target with valid boto3_session.
        Skip this test unless boto3 is installed in environment.
        Mock the creation of a new Scan Target, and behavior of AWS Services STS, CloudFormation and S3.

        :param region: str
        :param organization_id: str
        :param kind: ScanTargetKind.AZURE
        :param credential: ScanTargetAZURE
        :param boto3_profile: str
        :param schedule: str

        Asserts:
        * New Scan Target was created, with given parameters.
        * Scan was Started for this new Scan Target.
        * CloudFormation with Zanshin Role was deployed sucessfully.

        >>> new_scan_target = self.sdk.onboard_scan_target(
                region, organization_id, kind, name, credential, None, boto3_profile, schedule)
        """
        import json

        # Setup test data
        aws_account_id = "123456789012"
        organization_id = "822f4225-43e9-4922-b6b8-8b0620bdb1e3"
        created_scan_target_id = "14f79567-6b68-4e3a-b2f2-4f1383546251"
        kind = ScanTargetKind.AWS
        name = "OnboardTesting-it"
        credential = ScanTargetAWS(aws_account_id)
        schedule = "24h"
        region = "us-east-1"

        boto3_session = boto3.Session(
            aws_access_key_id="EXAMPLE_NON_EXISTING_KEY",
            aws_secret_access_key="&x@mP|e$3cReT",
            aws_session_token="session_token",
        )

        # Mock request to create new Scan Target
        mock_is_file.return_value = True
        _data = "[default]\napi_key=api_key"

        with patch("__main__.__builtins__.open", mock_open(read_data=_data)):
            request.return_value = Mock(
                status_code=200, json=lambda: {"id": created_scan_target_id}
            )
            client = Client()
            client._client.request = request

        # Create Mocked S3 tenchi-assets bucket
        with open(
            "zanshinsdk/dummy_cloudformation_zanshin_service_role_template.json", "r"
        ) as dummy_template_file:
            DUMMY_TEMPLATE = json.load(dummy_template_file)
            s3 = boto3.client("s3", region_name="us-east-2")
            s3.create_bucket(
                Bucket="tenchi-assets",
                CreateBucketConfiguration={"LocationConstraint": "us-east-2"},
            )
            s3.put_object(
                Bucket="tenchi-assets",
                Key="zanshin-service-role.template",
                Body=json.dumps(DUMMY_TEMPLATE),
            )

        # Call method onboard_scan_target with boto3_session instead of boto3_profile
        new_scan_target = client.onboard_scan_target(
            region,
            organization_id,
            kind,
            name,
            credential,
            boto3_session,
            None,
            schedule,
        )

        # Assert that Scan Target was created
        self.assertEqual(created_scan_target_id, new_scan_target["id"])

        # Assert that Scan Target was called with correct parameters
        client._client.request.assert_any_call(
            "POST",
            f"/organizations/{organization_id}/scantargets",
            body={
                "name": name,
                "kind": kind,
                "schedule": schedule,
                "credential": {"account": aws_account_id},
            },
        )
        # Assert that we checked Scan Target to start scan
        client._client.request.assert_any_call(
            "POST",
            f"/organizations/{organization_id}/scantargets/{created_scan_target_id}/check",
        )

        # Assert CloudFormation Stack was created successfully
        zanshin_cloudformation_stack_name = "tenchi-zanshin-service-role"
        cloudformation = boto3.client("cloudformation", region_name="us-east-1")
        zanshin_stack = cloudformation.describe_stacks(
            StackName=zanshin_cloudformation_stack_name
        )["Stacks"][0]
        self.assertEqual("CREATE_COMPLETE", zanshin_stack["StackStatus"])
        self.assertEqual(zanshin_cloudformation_stack_name, zanshin_stack["StackName"])

        # Clean Up CloudFormation
        cf_stacks = cloudformation.describe_stacks(
            StackName=zanshin_cloudformation_stack_name
        )
        for cf_stack in cf_stacks["Stacks"]:
            cloudformation.delete_stack(StackName=cf_stack["StackName"])
