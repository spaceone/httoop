from httoop.status.types import StatusException


class InformationalStatus(StatusException):
    """
    INFORMATIONAL = 1xx
    Mostly used for negotiation with the HTTP Server.
    """


class CONTINUE(InformationalStatus, code=100):
    """
    This is, beside 417, the code for a LBYL (Look before you leap) request.
    It indicates that the request is OK and the client should resent its request.

    .. seealso:: :rfc:`2616#section-10.1`
    """

    body = None


class SWITCHING_PROTOCOLS(InformationalStatus, code=101):
    """
    If the client wants to use another protocol (in the Upgrade-header)
    this is the response that the TCP server now speaks another protocol.
    """

    body = None


class PROCESSING(InformationalStatus, code=102):
    """Processing."""
