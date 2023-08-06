"""Botocore with support for AWS SSO exceptions."""
# Copyright 2012-2014 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You
# may not use this file except in compliance with the License. A copy of
# the License is located at
#
# http://aws.amazon.com/apache2.0/
#
# or in the "license" file accompanying this file. This file is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF
# ANY KIND, either express or implied. See the License for the specific
# language governing permissions and limitations under the License.
from botocore.exceptions import BotoCoreError


class SSOError(BotoCoreError):
    """Base class for AWS SSO authentication errors."""

    fmt = "An unspecified error happened when resolving SSO credentials"


class PendingAuthorizationExpiredError(SSOError):
    """Pending AWS SSO authorization expired."""

    fmt = (
        "The pending authorization to retrieve an SSO token has expired. The "
        "device authorization flow to retrieve an SSO token must be restarted."
    )


class SSOTokenLoadError(SSOError):
    """AWS SSO token load error."""

    fmt = "Error loading SSO Token: {error_msg}"


class UnauthorizedSSOTokenError(SSOError):
    """Unauthorized AWS SSO token."""

    fmt = (
        "The SSO session associated with this profile has expired or is "
        "otherwise invalid. To refresh this SSO session run aws sso login "
        "with the corresponding profile."
    )
