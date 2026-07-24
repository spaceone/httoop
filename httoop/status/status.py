"""
HTTP status codes.

.. seealso:: :rfc:`2616#section-6.2`
.. seealso:: :rfc:`2616#section-10`
"""
# ruff: file-ignore[PLR2004]

from __future__ import annotations

import re
from typing import Any

from httoop.exceptions import InvalidLine
from httoop.meta import Semantic
from httoop.util import _, integer


STATUSES = {}


class Status(Semantic):  # noqa: PLW1641
    """
    A HTTP Status.

    :rfc:`2616#section-6.2`
    """

    # __slots__ = ('__code', '__reason')  # conflicts with StatusException

    @property
    def informational(self) -> bool:
        return 99 < self.__code < 200

    @property
    def successful(self) -> bool:
        return 199 < self.__code < 300

    @property
    def redirection(self) -> bool:
        return 299 < self.__code < 400

    @property
    def client_error(self) -> bool:
        return 399 < self.__code < 500

    @property
    def server_error(self) -> bool:
        return 499 < self.__code < 600

    # aliases
    @property
    def status(self) -> int:
        return self.__code

    @property
    def reason_phrase(self) -> str:
        return self.__reason

    @property
    def code(self):
        return self.__code

    @code.setter
    def code(self, code) -> None:
        self.set((code, self.__reason))

    @property
    def reason(self):
        return self.__reason

    @reason.setter
    def reason(self, reason) -> None:
        self.set((self.__code, reason))

    description = ''

    STATUS_RE = re.compile(rb'^([1-5]\d{2})(?:\s+([\s\w]*))\Z')

    def __init__(self, code: int | None = None, reason: bytes | None = None) -> None:
        """
        :param code: the HTTP Statuscode
        :type code: int

        :param reason: the HTTP Reason-Phrase
        :type reason: str
        """
        self.__code = 0
        self.__reason = ''
        reason = reason or ''
        reason = reason or reason or REASONS.get(code, ('', ''))[0]
        if code is not None:
            self.set((code, reason))

    def __init_subclass__(cls, code=None, **kwargs):
        super().__init_subclass__(**kwargs)
        if code is None:
            return

        if not (100 <= code <= 599):
            raise RuntimeError('HTTP status code must be between 100 and 599', code, cls)

        if code < 200:
            expected = 'InformationalStatus'
        elif code < 300:
            expected = 'SuccessStatus'
        elif code < 400:
            expected = 'RedirectStatus'
        elif code < 500:
            expected = 'ClientErrorStatus'
        else:
            expected = 'ServerErrorStatus'

        if not any(base.__name__ == expected for base in cls.__mro__):
            raise RuntimeError(f'{cls.__name__} must inherit from {expected}')

        cls.code = code
        reason, description = REASONS.get(code, ('', ''))
        if cls.reason is Status.reason:
            cls.reason = reason
        if not cls.description:
            cls.description = description
        STATUSES[code] = cls

    def parse(self, status: bytes) -> None:
        """
        Parse a Statuscode and Reason-Phrase.

        :param status: the code and reason
        :type  status: bytes
        """
        match = self.STATUS_RE.match(status)
        if match is None:
            raise InvalidLine(_('Invalid status %r'), status.decode('ISO8859-1'))

        self.set((integer(match.group(1)), match.group(2).decode('ascii')))

    def compose(self) -> bytes:
        return b'%d %s' % (self.__code, self.__reason.encode('ascii'))

    def __str__(self) -> str:
        return self.compose().decode('ascii')

    def __int__(self) -> int:
        """Returns this status as number."""
        return self.__code

    def __eq__(self, other: object) -> bool:
        """Compares a status with another :class:`Status` or :class:`int`."""
        if isinstance(other, int):
            return self.__code == other
        if isinstance(other, Status):
            return self.__code == other.code
        return super().__eq__(other)

    def __lt__(self, other: int | Status) -> bool:
        return self.__code < other

    def __gt__(self, other: int | Status) -> bool:
        return self.__code > other

    def set(self, status: Any) -> None:
        """
        Sets reason and status.

        :param status:
        A HTTP Status, e.g.: 200, (200, 'OK'), '200 OK'
        :type  status:
        int or tuple or bytes or Status
        """
        if isinstance(status, int):
            self.__code, self.__reason = status, REASONS.get(status, ('', ''))[0]
        elif isinstance(status, tuple):
            code, reason = status
            if isinstance(reason, bytes):
                reason = reason.decode('ascii')
            self.__code, self.__reason = integer(code), reason
        elif isinstance(status, (bytes, str)):
            code, reason = status.split(None, 1)
            if isinstance(reason, bytes):
                reason = reason.decode('ascii')
            self.__code, self.__reason = integer(code), reason
        elif isinstance(status, Status):
            self.__code, self.__reason = status.code, status.reason
        else:
            raise TypeError('invalid status')
        if not (99 < self.__code < 600):
            raise TypeError('invalid status')

    def __repr__(self) -> str:
        return '<HTTP Status (code=%d, reason=%r)>' % (self.__code, self.__reason)


REASONS = {
    # code: (reason, description)
    100: ('Continue', 'Request received, please continue'),
    101: ('Switching Protocols', 'Switching to new protocol; obey Upgrade header'),
    200: ('OK', 'Request fulfilled, document follows'),
    201: ('Created', 'Document created, URL follows'),
    202: ('Accepted', 'Request accepted, processing continues off-line'),
    203: ('Non-Authoritative Information', 'Request fulfilled from cache'),
    204: ('No Content', 'Request fulfilled, nothing follows'),
    205: ('Reset Content', 'Clear input form for further input.'),
    206: ('Partial Content', 'Partial content follows.'),
    300: ('Multiple Choices', 'Object has several resources -- see URI list'),
    301: ('Moved Permanently', 'Object moved permanently -- see URI list'),
    302: ('Found', 'Object moved temporarily -- see URI list'),
    303: ('See Other', 'Object moved -- see Method and URL list'),
    304: ('Not Modified', 'Document has not changed since given time'),
    305: ('Use Proxy', 'You must use proxy specified in Location to access this resource.'),
    307: ('Temporary Redirect', 'Object moved temporarily -- see URI list'),
    400: ('Bad Request', 'Bad request syntax or unsupported method'),
    401: ('Unauthorized', 'No permission -- see authorization schemes'),
    402: ('Payment Required', 'No payment -- see charging schemes'),
    403: ('Forbidden', 'Request forbidden -- authorization will not help'),
    404: ('Not Found', 'Nothing matches the given URI'),
    405: ('Method Not Allowed', 'Specified method is invalid for this resource.'),
    406: ('Not Acceptable', 'URI not available in preferred format.'),
    407: ('Proxy Authentication Required', 'You must authenticate with this proxy before proceeding.'),
    408: ('Request Timeout', 'Request timed out; try again later.'),
    409: ('Conflict', 'Request conflict.'),
    410: ('Gone', 'URI no longer exists and has been permanently removed.'),
    411: ('Length Required', 'Client must specify Content-Length.'),
    412: ('Precondition Failed', 'Precondition in headers is false.'),
    413: ('Payload Too Large', 'Payload is too large.'),
    414: ('URI Too Long', 'URI is too long.'),
    415: ('Unsupported Media Type', 'Entity body in unsupported format.'),
    416: ('Requested Range Not Satisfiable', 'Cannot satisfy request range.'),
    417: ('Expectation Failed', 'Expect condition could not be satisfied.'),
    500: ('Internal Server Error', 'The server encountered an unexpected condition which prevented it from fulfilling the request.'),
    501: ('Not Implemented', 'Server does not support this operation'),
    502: ('Bad Gateway', 'Invalid responses from another server/proxy.'),
    503: ('Service Unavailable', 'The server is currently unable to handle the request due to a temporary overloading or maintenance of the server.'),
    504: ('Gateway Timeout', 'The gateway server did not receive a timely response'),
    505: ('HTTP Version Not Supported', 'Cannot fulfill request.'),
}
