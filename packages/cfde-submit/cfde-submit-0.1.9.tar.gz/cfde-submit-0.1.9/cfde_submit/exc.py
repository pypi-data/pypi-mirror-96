"""
CFDE Submit Exceptions. The client should only throw these when something goes wrong,
everything else is a bug.

Catch all top level exceptions under CfdeClientException.
"""


class CfdeClientException(Exception):
    """Base Exception for client"""
    pass


class ValidationException(CfdeClientException):
    """Something didn't validate"""
    pass


class InvalidInput(CfdeClientException):
    """A dataset given to the client was not valid"""


class RemoteConfigException(CfdeClientException):
    """There was a problem with the catalog"""
    pass


class PermissionDenied(CfdeClientException):
    """The user needs to be added to a Globus Group"""
    pass


class NotLoggedIn(CfdeClientException):
    """User is not logged in"""
    pass


class OutdatedVersion(CfdeClientException):
    """The current version of cfde-submit is out of date"""
    pass


class SubmissionsUnavailable(CfdeClientException):
    pass
