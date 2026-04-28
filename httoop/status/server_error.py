from __future__ import annotations

from httoop.status.types import StatusException


class ServerErrorStatus(StatusException):
    """
    SERVER_ERRORS = 5xx
    Indicates that something gone wrong on the server side.
    The server can send the Retry-After header if
    it knows that the problem is temporary.
    """

    def to_dict(self) -> dict[str, str | int]:
        dct = super().to_dict()
        dct.update({'traceback': self.traceback or ''})
        return dct


class INTERNAL_SERVER_ERROR(ServerErrorStatus, code=500):
    """
    The generic status code.
    Mostly used when an exception in the request handler occurs.
    """

    cacheable = True


class NOT_IMPLEMENTED(ServerErrorStatus, code=501):
    """
    The client tried to use a HTTP feature which the server does not support.
    Used if the server does not know the request method.
    """


class BAD_GATEWAY(ServerErrorStatus, code=502):
    """Problem with the proxy server."""

    cacheable = True


class SERVICE_UNAVAILABLE(ServerErrorStatus, code=503):
    """
    There is currently a problem with the server.
    Probably too many requests at once.
    """

    cacheable = True


class GATEWAY_TIMEOUT(ServerErrorStatus, code=504):
    """The proxy could not connect to the upstream server."""

    cacheable = True


class HTTP_VERSION_NOT_SUPPORTED(ServerErrorStatus, code=505):
    """
    The clients http version is not supported.
    This should not happen since HTTP 1.1 is backward compatible.
    The entity-body should contain a list of supported protocols.
    """


class VARIANT_ALSO_NEGOTIATES(ServerErrorStatus, code=506):
    """Variant also negotiates."""


class INSUFFICIENT_STORAGE(ServerErrorStatus, code=507):
    """Insufficient storage."""


class LOOP_DETECTED(ServerErrorStatus, code=508):
    """Loop detected."""


class BANDWIDTH_LIMIT_EXCEEDET(ServerErrorStatus, code=509):
    """Bandwith limit exceedet."""


# class NOT_EXTENDED(ServerErrorStatus, code=510):


class NETWORK_AUTHENTICATION_REQUIRED(ServerErrorStatus, code=511):
    """Network authentication required."""


# class NETWORK_READ_TIMEOUT_ERROR(ServerErrorStatus, code=598):

# class NETWORK_CONNECT_TIMEOUT_ERROR(ServerErrorStatus, code=599):
