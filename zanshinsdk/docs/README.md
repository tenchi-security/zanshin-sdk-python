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


Parameters:
- boto3_profile: the profile name that boto3 will use.
- organization_id: the ID of the organization to have the new Scan Target.
- kind: the Kind of scan target (AWS, GCP, AZURE, DOMAIN).
- name: the name of the new scan target.
- credential: credentials to access the cloud account to be scanned:
    * For AWS scan targets, provide the account ID in the *account* field
    * For Azure scan targets, provide *applicationId*, *subscriptionId*, *directoryId* and *secret* fields.
    * For GCP scan targets, provide a *projectId* field
    * For DOMAIN scan targets, provide a URL in the *domain* field
- schedule: schedule in cron format for when the scan will happen.

Returns
- JSON object containing newly created scan target.

**Example**

```python
from zanshinsdk import Client, ScanTargetKind, ScanTargetAWS

client = Client()

organization_id = "bd0e..." # Zanshin Organization ID to include the Scan Target to.
kind = ScanTargetKind.AWS
name = "AWS Account included via SDK"
credential = ScanTargetAWS("123456789012") # ID of AWS Account to onboard.
schedule = "0 0 * * *" # When the scan will happen.
region = "us-east-1" # Region to run the CloudFormation Stack responsible for onboarding.

boto3_profile = 'aws_profile'

my_new_scan_target = client.onboard_scan_target(boto3_profile, region, organization_id, kind, name, credential, schedule)

```
---
#### Minimum required AWS IAM Privileges
The minimum required privileges that you need in your boto3 profile to deploy sucessfully the CloudFormation for Zanshin Tenchi Service Role are below:
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Action": [
                "cloudformation:CreateStack",
                "cloudformation:DescribeStacks",
                "iam:GetRole",
                "iam:CreateRole",
                "iam:CreatePolicy",
                "iam:CreatePolicyVersion",
                "iam:PutRolePolicy",
                "iam:AttachRolePolicy"
            ],
            "Effect": "Allow",
            "Resource": "*"
        }
    ]
}
```

