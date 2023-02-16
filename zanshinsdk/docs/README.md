# Zanshin Python SDK Documentation

This section contains information about how to use methods available in the Zanshin Python SDK, along with some concepts.

## Onboarding

Onboarding is the process of adding new AWS Account (Scan Targets) to your Organization in Zanshin.
Scan Targets can be of four kinds
- AWS Accounts
- Azure Subscriptions
- Google Cloud Projects
- Domains

### onboard_scan_target

This method automatically creates a new Scan Targets to the Zanshin Organization informed in parameters and performs the onbard creating the roles required in your AWS Account.

Currently using the Zanshin SDK you're only able to onboard **AWS Scan Targets**.

> :warning: This method will deploy a CloudFormation stack in your AWS account. So it's required that you have `boto3` installed in your system, as well as privileges to create CloudFormation stacks and create IAM roles in the given AWS Account.
> You must set up a [boto3 profile](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/configuration.html#using-a-configuration-file).


**Currently supports only AWS Scan Targets.**

_For AWS Scan Target:_

If boto3 is installed, creates a Scan Target for the given organization and perform the onboard.

Parameters:

- :param region: the AWS Region to deploy the CloudFormation Template of Zanshin Service Role.
- :param organization_id: the ID of the organization to have the new Scan Target.
- :param kind: the Kind of scan target (AWS, GCP, AZURE, DOMAIN)
- :param name: the name of the new scan target.
- :param credential: credentials to access the cloud account to be scanned:
	* For AWS scan targets, provide the account ID in the *account* field.
	* For Azure scan targets, provide *applicationId*, *subscriptionId*, *directoryId* and *secret* fields.
	* For GCP scan targets, provide a *projectId* field.
	* For DOMAIN scan targets, provide a URL in the *domain* field.

- :param schedule: schedule in cron format.
- :param boto3_profile: boto3 profile name used for CloudFormation Deployment. If none, uses \"default\" profile.
- :param boto3_session: boto3 session used for CloudFormation Deployment. If informed, will ignore boto3_profile.

Return:

- :return: JSON object containing newly created scan target .


**Usage**

```python
from zanshinsdk import Client, ScanTargetKind, ScanTargetAWS
import boto3

client = Client()

# Zanshin Organization ID to include the Scan Target to.
organization_id = "bd0..."
kind = ScanTargetKind.AWS
name = "AWS Account included via SDK"
credential = ScanTargetAWS("418069676198")  # ID of AWS Account to onboard.
schedule = "0 0 * * *"  # Schedule time that the scan will happen.
region = "us-east-1" # Region to run the CloudFormation Stack responsible for onboarding.
boto3_session = boto3.Session( # Boto3 session with adequate privileges
    aws_access_key_id="ASIAEXAMPLEKEY",
    aws_secret_access_key="eJs3cret",
    aws_session_token="IQSessionToken",
)

my_new_scan_target = client.onboard_scan_target(region=region, organization_id=organization_id, kind=kind,
                                                name=name, credential=credential, boto3_session=boto3_session,
                                                schedule=schedule)


```
---

#### Minimum required AWS IAM Privileges

The minimum required privileges that you need in your boto3 profile to deploy sucessfully the CloudFormation for Zanshin Tenchi Service Role are below:
```json
{
	"Version": "2012-10-17",
	"Statement": [{
			"Sid": "PrivCloudFormation",
			"Action": [
				"cloudformation:CreateStack",
				"cloudformation:DescribeStacks"
			],
			"Effect": "Allow",
			"Resource": "*"

		},
		{
			"Sid": "IAMRole",
			"Action": [
				"iam:GetRole",
				"iam:CreateRole",
				"iam:PutRolePolicy",
				"iam:AttachRolePolicy"
			],
			"Effect": "Allow",
			"Resource": "arn:aws:iam::<your AWS account ID|*>:role/Tenchi-Zanshin-Service-Role",
			"Condition": {
				"ForAnyValue:StringEquals": {
					"aws:CalledVia": "cloudformation.amazonaws.com"
				}
			}
		},
		{
			"Sid": "IAMPolicy",
			"Action": [
				"iam:CreatePolicy",
				"iam:CreatePolicyVersion"
			],
			"Effect": "Allow",
			"Resource": "*",
			"Condition": {
				"ForAnyValue:StringEquals": {
					"aws:CalledVia": "cloudformation.amazonaws.com"
				}
			}
		}
	]
}
```

> **Attention**
> :warning: Make sure to substitute the `your AWS account ID` to the correct value.
