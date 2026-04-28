"""
HTTP status codes.

.. seealso:: :rfc:`2616#section-10`
"""

from __future__ import annotations

from httoop.status.status import Status


class StatusException(Status, Exception):
    """
    This class represents a small HTTP Response message
    for error handling purposes
    .
    """

    @property
    def headers(self) -> dict[str, str]:
        return self._headers

    @property
    def body(self):
        if not hasattr(self, '_body'):
            from httoop.messages.body import Body

            self._body = Body(mimetype='application/json')
            self._body.data = self.to_dict()
        return self._body

    @body.setter
    def body(self, value) -> None:
        self.body.set(value)

    header_to_remove = ()
    """a tuple of header field names which should be
        removed when responding with this error"""

    description = ''

    cacheable = False

    @property
    def traceback(self):
        return self._traceback

    @traceback.setter
    def traceback(self, tb) -> None:
        if self.server_error:
            self._traceback = tb

    code = None

    def __init__(self, description: str | None = None, reason: None = None, headers: dict[str, str] | None = None, traceback: str | None = None) -> None:
        """
        :param description:
        a description of the error which happened
        :type description: str

        :param reason:
        a additional reason phrase
        :type reason: str

        :param headers:
        :type headers: dict

        :param traceback:
        A Traceback for the error
        :type traceback: str
        """
        Status.__init__(self, self.__class__.code, reason=reason)  # pylint: disable=W0233

        self._headers = {}
        self._traceback = None

        if isinstance(headers, dict):
            self._headers.update(headers)

        if description is not None:
            self.description = description
        else:
            self.description = type(self).description

        if traceback:
            self.traceback = traceback

    def __repr__(self) -> str:
        description = ''
        if self.description:
            description = f'({self.description})'
        return '<HTTP Status %d %r %s>' % (int(self), self.reason, description)

    __str__ = __repr__

    def to_dict(self) -> dict[str, int | str | dict[str, str]]:
        """The default body arguments."""
        return {
            'status': self.status,
            'reason': self.reason,
            'description': self.description,
            'headers': self.headers,
        }
