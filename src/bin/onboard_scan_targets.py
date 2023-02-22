import sys
import time
from importlib.util import find_spec, module_from_spec
from typing import Dict, Union
from uuid import UUID

import scan_target

from src.bin.client import (
    Client,
    ScanTargetAWS,
    ScanTargetAZURE,
    ScanTargetDOMAIN,
    ScanTargetGCP,
    ScanTargetHUAWEI,
    ScanTargetKind,
    ScanTargetSchedule,
    validate_class,
)

###################################################
# Onboard Scan Targets
###################################################


def onboard_scan_target(
    region: str,
    organization_id: Union[UUID, str],
    kind: Union[ScanTargetKind, str],
    name: str,
    credential: Union[
        ScanTargetAWS,
        ScanTargetAZURE,
        ScanTargetGCP,
        ScanTargetHUAWEI,
        ScanTargetDOMAIN,
    ],
    boto3_session: any = None,
    boto3_profile: str = "default",
    schedule: Union[str, ScanTargetSchedule] = ScanTargetSchedule.TWENTY_FOUR_HOURS,
) -> Dict:
    """
    Currently supports only AWS Scan Targets.
    For AWS Scan Target:
    If boto3 is installed, creates a Scan Target for the given organization and perform the onboard.
    :param region: the AWS Region to deploy the CloudFormation Template of Zanshin Service Role.
    :param organization_id: the ID of the organization to have the new Scan Target.
    :param kind: the Kind of scan target (AWS, GCP, AZURE, DOMAIN)
    :param name: the name of the new scan target.
    :param credential: credentials to access the cloud account to be scanned:
        * For AWS scan targets, provide the account ID in the *account* field.
        * For Azure scan targets, provide *applicationId*, *subscriptionId*, *directoryId* and *secret* fields.
        * For GCP scan targets, provide a *projectId* field.
        * For DOMAIN scan targets, provide a URL in the *domain* field.

    :param schedule: schedule in string or enum format.
    :param boto3_profile: boto3 profile name used for CloudFormation Deployment. If none, uses \"default\" profile.
    :param boto3_session: boto3 session used for CloudFormation Deployment. If informed, will ignore boto3_profile.
    :return: JSON object containing newly created scan target .
    """

    if isinstance(kind, str):
        kind = ScanTargetKind(kind.strip().upper())
    else:
        validate_class(kind, ScanTargetKind)
    _check_scantarget_is_aws(kind)

    boto3 = _check_boto3_installation()
    if not boto3_session:
        boto3_session = _get_session_from_boto3_profile(
            boto3_profile=boto3_profile, boto3=boto3
        )

    _check_aws_credentials_are_valid(boto3_session=boto3_session)

    if len(name) < 3:
        name = f"{name}_{credential['account']}"

    new_scan_target = scan_target.create_organization_scan_target(
        organization_id, kind, name, credential, schedule
    )
    new_scan_target_id = new_scan_target["id"]

    zanshin_stack_name = "tenchi-zanshin-service-role"
    try:
        cloudformation_client = _deploy_cloudformation_zanshin_service_role(
            boto3_session, region, new_scan_target_id, zanshin_stack_name
        )
        retries = 0
        max_retry = 10
        wait_between_retries = 10
        zanshin_stack = _get_cloudformation_stack_status(
            zanshin_stack_name, cloudformation_client
        )

        while zanshin_stack["StackStatus"] != "CREATE_COMPLETE":
            if not retries:
                Client._logger.debug(
                    f"Failed to confirm CloudFormation Stack {zanshin_stack_name} completion. Retrying."
                )
            if retries >= max_retry:
                raise RuntimeError("CloudFormation Stack wasn't deployed")
            time.sleep(wait_between_retries)
            Client._logger.debug(
                f"Checking CloudFormation Stack {zanshin_stack_name}..."
            )
            retries += 1
            zanshin_stack = _get_cloudformation_stack_status(
                zanshin_stack_name, cloudformation_client
            )

    except Exception as error:
        print("err", error)
        raise ValueError(
            f"Failed to confirm CloudFormation Stack {zanshin_stack_name} completion."
        )

    scan_target.check_organization_scan_target(
        organization_id=organization_id, scan_target_id=new_scan_target_id
    )
    scan_target.start_organization_scan_target_scan(
        organization_id=organization_id,
        scan_target_id=new_scan_target_id,
        force=True,
    )
    return scan_target.get_organization_scan_target(
        organization_id=organization_id, scan_target_id=new_scan_target_id
    )


def _deploy_cloudformation_zanshin_service_role(
    boto3_session: object,
    region: str,
    new_scan_target_id: str,
    zanshin_stack_name: str,
):
    """
    Instantiate boto3 client for CloudFormation, and create the Stack containing Zanshin Service Role.
    :return: boto3 cloudformation client.
    """
    try:
        cloudformation_client = boto3_session.client(
            "cloudformation", region_name=region
        )
        cloudformation_client.create_stack(
            StackName=zanshin_stack_name,
            TemplateURL="https://s3.amazonaws.com/tenchi-assets/zanshin-service-role.template",
            Parameters=[
                {"ParameterKey": "ExternalId", "ParameterValue": new_scan_target_id}
            ],
            Capabilities=["CAPABILITY_IAM", "CAPABILITY_NAMED_IAM"],
        )

        return cloudformation_client
    except Exception as e:
        Client._logger.error(
            "Unable to deploy CloudFormation zanshin-tenchi-service-role. The onboard won't succeed."
        )
        raise e


def _get_cloudformation_stack_status(zanshin_stack_name, cloudformation_client):
    """
    Fetch CloudFormation Stack details. Assumes that there's only one Stack with given name.
    :return: cloudformation stack.
    """
    zanshin_stack = cloudformation_client.describe_stacks(StackName=zanshin_stack_name)[
        "Stacks"
    ][0]
    return zanshin_stack


def _get_session_from_boto3_profile(self, boto3_profile, boto3):
    """
    Return boto3_session from boto3_profile informed
    :return: boto3_session.
    """
    return boto3.Session(profile_name=boto3_profile)


def _check_aws_credentials_are_valid(self, boto3_session):
    """
    Check if boto3 informed credentials are valid performing aws sts get-caller-identity. In case of
    problem, raises ValueError.
    """
    try:
        sts = boto3_session.client("sts")
        sts.get_caller_identity()
    except Exception as e:
        self._logger.exception("boto3 session is invalid")
        raise ValueError("boto3 session is invalid. Working boto3 session is required.")


def _check_scantarget_is_aws(self, kind):
    """
    Check if informed Scan Target is of AWS Kind. If not, raises NotImplementedError.
    """
    if kind != ScanTargetKind.AWS:
        raise NotImplementedError(
            f"Onboard doesn't support {kind.value} environment yet"
        )


def _check_boto3_installation(self):
    """
    Check if boto3 is installed in the current environment. If not, raises ImportError.
    :return: boto3 module if present.
    """
    package_name = "boto3"
    spec = find_spec(package_name)
    if spec is None:
        raise ImportError(
            f"{package_name} not present. {package_name} is required to perform AWS onboard."
        )

    module = module_from_spec(spec)
    sys.modules[package_name] = module
    spec.loader.exec_module(module)
    return module
