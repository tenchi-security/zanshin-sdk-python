class ScanTargetAWS(dict):
    def __init__(self, account):
        dict.__init__(self, account=account)


class ScanTargetAZURE(dict):
    def __init__(self, application_id, subscription_id, directory_id, secret):
        dict.__init__(
            self,
            applicationId=application_id,
            subscriptionId=subscription_id,
            directoryId=directory_id,
            secret=secret,
        )


class ScanTargetGCP(dict):
    def __init__(self, project_id):
        dict.__init__(self, projectId=project_id)


class ScanTargetHUAWEI(dict):
    def __init__(self, account_id):
        dict.__init__(self, accountId=account_id)


class ScanTargetDOMAIN(dict):
    def __init__(self, domain):
        dict.__init__(self, domain=domain)


class ScanTargetORACLE(dict):
    def __init__(self, compartment_id, region, tenancy_id, user_id, key_fingerprint):
        dict.__init__(
            self,
            compartment_id=compartment_id,
            region=region,
            tenancy_id=tenancy_id,
            user_id=user_id,
            key_fingerprint=key_fingerprint,
        )


class ScanTargetGroupCredentialListORACLE(dict):
    def __init__(self, region, tenancy_id, user_id, key_fingerprint):
        dict.__init__(
            self,
            region=region,
            tenancy_id=tenancy_id,
            user_id=user_id,
            key_fingerprint=key_fingerprint,
        )


class ScanTargetZENDESK(dict):
    def __init__(self, instance_url):
        dict.__init__(self, instanceUrl=instance_url)


class ScanTargetGWORKSPACE(dict):
    def __init__(self):
        dict.__init__(self)


class ScanTargetSLACK(dict):
    def __init__(self):
        dict.__init__(self)


class ScanTargetBITBUCKET(dict):
    def __init__(self):
        dict.__init__(self)


class ScanTargetJIRA(dict):
    def __init__(self, jira_url):
        dict.__init__(self, jiraUrl=jira_url)


class ScanTargetGITLAB(dict):
    def __init__(self):
        dict.__init__(self)


class ScanTargetSALESFORCE(dict):
    def __init__(self):
        dict.__init__(self)


class ScanTargetMS365(dict):
    def __init__(self, application_id, tenant_id, secret):
        dict.__init__(
            self,
            applicationId=application_id,
            tenantId=tenant_id,
            secret=secret,
        )


class ScanTargetGITHUB(dict):
    def __init__(self, organization_name, installation_id):
        dict.__init__(
            self, organizationName=organization_name, installationId=installation_id
        )
