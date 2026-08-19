from __future__ import annotations

from httoop.status.types import StatusException


class ClientErrorStatus(StatusException):
    """
    CLIENT_ERRORS = 4xx
    Something is wrong with the client: e.g. authentication,
    format of wanted representation, or error in the clients http library.
    """


class BAD_REQUEST(ClientErrorStatus, code=400):
    """
    The generic response code for client side errors.
    The response entity-body should contain information
    about what is wrong with the request.
    """

    cacheable = True


class UNAUTHORIZED(ClientErrorStatus, code=401):
    """
    The requested resource is protected and no or wrong
    authentication credentials were given.
    The WWW-Authenticate-header contains information about
    the accepted authentication method.
    The entity-body should contain information about what was wrong with
    the given credentials and where to register a new account.
    """

    def __init__(self, authenticate: str, *args, **kwargs) -> None:
        kwargs.setdefault('headers', {})['WWW-Authenticate'] = authenticate
        super().__init__(*args, **kwargs)

    def to_dict(self) -> dict[str, int | str | dict[str, str]]:
        dct = super().to_dict()
        dct.update({'WWW-Authenticate': self.headers['WWW-Authenticate']})
        return dct


class PAYMENT_REQUIRED(ClientErrorStatus, code=402):
    """Payment required."""


class FORBIDDEN(ClientErrorStatus, code=403):
    """
    The resource can only be served for specific users, at a specific time
    or from a certain IP address, etc.
    """


class NOT_FOUND(ClientErrorStatus, code=404):
    """No resource could be found at the given URI."""

    cacheable = True

    def __init__(self, path: str, **kwargs) -> None:
        self.path = path
        kwargs.update({'description': f'The requested resource "{path}" was not found on this server.'})
        super().__init__(**kwargs)


class METHOD_NOT_ALLOWED(ClientErrorStatus, code=405):
    """
    The client tried to use a HTTP Method which is not allowed.
    The Allow-header has to contain the allowed methods for this resource.
    """

    def __init__(self, allow: str, *args, **kwargs) -> None:
        kwargs.setdefault('headers', {})['Allow'] = allow
        super().__init__(*args, **kwargs)

    def to_dict(self) -> dict[str, int | str | dict[str, str]]:
        dct = super().to_dict()
        dct.update({'Allow': self.headers['Allow']})
        return dct


class NOT_ACCEPTABLE(ClientErrorStatus, code=406):
    r"""
    The clients Accept-\*-header wants a representation of
    the resource which the server can not deliver.
    The entity body should contain a list of links with
    acceptable representations (similar to 300).
    """


class PROXY_AUTHENTICATION_REQUIRED(ClientErrorStatus, code=407):
    """Proxy authenticate required."""


class REQUEST_TIMEOUT(ClientErrorStatus, code=408):
    """
    The client opens a connection to a server without sending a
    request after a specific amount of time.
    """

    def __init__(self, *args, **kwargs) -> None:
        kwargs.setdefault('headers', {})['Connection'] = 'close'
        super().__init__(*args, **kwargs)


class CONFLICT(ClientErrorStatus, code=409):
    """
    If the request would cause to leave the resource in an inconsequent
    state this status is send.
    Examples: DELETE of a non empty bucket, changing a username to
    a already taken username.
    The location header can point to the conflicting resource.
    The entity body should contain a description of the conflict.
    """


class GONE(ClientErrorStatus, code=410):
    """The resource exists but is not anymore available (propably DELETEd)."""

    cacheable = True


class LENGTH_REQUIRED(ClientErrorStatus, code=411):
    """
    If a request representation is given but no Content-Length-header
    the HTTP server can decide to respond with this status code.
    """


class PRECONDITION_FAILED(ClientErrorStatus, code=412):
    r"""
    If a condition from any of the If-\*-headers except for conditional
    GET fails this status code is the respond.
    """


class CONTENT_TOO_LARGE(ClientErrorStatus, code=413):
    """
    The HTTP server can deny too large representations.
    A LBYL request can be useful.
    If the server can only not handle the request e.g. because of
    full disk space it can send the Retry-After-header.
    """


class URI_TOO_LONG(ClientErrorStatus, code=414):
    """Raised if the given URI is too long for the server."""


class UNSUPPORTED_MEDIA_TYPE(ClientErrorStatus, code=415):
    """
    This status code is sent when the server does not know
    the representation media type given in Content-Type-header.
    If the representation is just broken use 400 or 422.
    """


class RANGE_NOT_SATISFIABLE(ClientErrorStatus, code=416):
    """Range not satisfiable."""


class EXPECTATION_FAILED(ClientErrorStatus, code=417):
    """
    This is the response code if a LBYL request (Expect-header) fails.
    It is the flip side of 100 Continue.
    """


class I_AM_A_TEAPOT(ClientErrorStatus, code=418):
    """I am a teapot."""


# class ENHANCE_YOUR_CALM(ClientErrorStatus, code=420):
#     """Enhance our calm."""


class MISDIRECTED_REQUEST(ClientErrorStatus, code=421):
    """Misredirected request."""


class UNPROCESSABLE_ENTITY(ClientErrorStatus, code=422):
    """Unprocessable entity."""


class LOCKED(ClientErrorStatus, code=423):
    """Locked."""


class FAILED_DEPENDENCY(ClientErrorStatus, code=424):
    """Failed dependency."""


class UPGRADE_REQUIRED(ClientErrorStatus, code=426):
    def __init__(self, upgrade: str, *args, **kwargs) -> None:
        kwargs.setdefault('headers', {})['Upgrade'] = upgrade
        kwargs['headers']['Connection'] = 'Upgrade'
        super().__init__(*args, **kwargs)


class PRECONDITION_REQUIRED(ClientErrorStatus, code=428):
    """Precondition required."""


class TOO_MANY_REQUESTS(ClientErrorStatus, code=429):
    """Too many requests."""


class REQUEST_HEADER_FIELDS_TOO_LARGE(ClientErrorStatus, code=431):
    """Request header fields too large."""


# class NO_RESPONSE(ClientErrorStatus, code=444):
#
# class UNAVAILABLE_FOR_LEGAL_REASONS(ClientErrorStatus, code=451):
#
# class CLIENT_CLOSED_REQUEST(ClientErrorStatus, code=499):
