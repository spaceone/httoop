from __future__ import annotations

from httoop.status.types import StatusException


class SuccessStatus(StatusException):
    """
    SUCCESS = 2xx
    indicates that an operation was successful.
    """


class OK(SuccessStatus, code=200):
    """
    The request was successful.
    On GET requests the entity body will be a
    representation of the requested resource.
    For other methods the entity body contains a representation of
    the current state of the resource or a description of the performed action.
    """

    cacheable = True


class CREATED(SuccessStatus, code=201):
    """
    A new resource was created.
    This should only be send on POST and PUT requests.
    The Location-Header should contain the URI to the created resource.
    The entity-body should describe and link to the created resource.
    """

    def __init__(self, location: str, *args, **kwargs) -> None:
        kwargs.setdefault('headers', {})['Location'] = location
        super().__init__(*args, **kwargs)

    def to_dict(self) -> dict[str, int | str | dict[str, str]]:
        dct = super().to_dict()
        dct.update({'Location': self.headers['Location']})
        return dct


class ACCEPTED(SuccessStatus, code=202):
    """
    The request looks valid but will be procecced later.
    It is an asynchronous action.
    The Location-Header should contain a URI where
    the status of processing can be found.
    If this is not possible it should give an estimate
    time when the request will be processed.
    """


class NON_AUTHORITATIVE_INFORMATION(SuccessStatus, code=203):
    """
    Everything is OK but the response headers
    may be altered by a third party.
    """

    cacheable = True


class NO_CONTENT(SuccessStatus, code=204):
    """
    GET: The representation of the resource is empty.
    other request methods: the status message or representation is not needed.
    This is useful for ajax requests.
    It is also useful for making series of edits
    to a single record (a HTML POST form).
    """

    body = None
    cacheable = True


class RESET_CONTENT(SuccessStatus, code=205):
    """
    The same as 204 but this indicated that the client should
    reset the view of its data structure.
    This is useful for entering a series of records
    in succession (a HTML POST form).
    """

    body = None


class PARTIAL_CONTENT(SuccessStatus, code=206):
    """
    Partial GET:
    The response does not contain the full representation of a resource
    but only the bytes requested in the Content-Range-header.
    It is often use to resume an interrupted download.
    The Date-header is required, the ETag-header
    and Content-Location-header are useful.
    """


class MULTI_STATUS(SuccessStatus, code=207):
    """
    This status code indicated that the entity-body contains information
    about the states of the batch request.
    It is not an official HTTP-Status-Code: WebDAV
    The entity-body is descripted in RFC 2518.
    """


class ALREADY_REPORTED(SuccessStatus, code=208):
    """Already reported."""


class IM_USED(SuccessStatus, code=226):
    """I'm used."""

    reason = 'foo'
