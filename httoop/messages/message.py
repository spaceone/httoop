"""
HTTP request and response messages.

.. seealso:: :rfc:`2616#section-4`
"""

import httoop.header.headers
from httoop.header import Headers
from httoop.messages.body import Body
from httoop.messages.protocol import Protocol
from httoop.meta import Semantic


__all__ = ('Message',)


class Message(Semantic):
    """
    A HTTP message.

    .. seealso:: :rfc:`2616#section-4`
    """

    __slots__ = ('__body', '__headers', '__protocol')

    @property
    def protocol(self):
        return self.__protocol

    @protocol.setter
    def protocol(self, protocol) -> None:
        self.__protocol.set(protocol)

    @property
    def headers(self):
        return self.__headers

    @headers.setter
    def headers(self, headers) -> None:
        self.__headers.set(headers)

    @property
    def body(self):
        return self.__body

    @body.setter
    def body(self, body) -> None:
        self.__body.set(body)

    @property
    def trailer(self) -> httoop.header.headers.Headers:
        return Headers((key, self.headers[key]) for key in self.headers.values('Trailer') if key in self.headers)

    # @trailer.setter
    # def trailer(self, trailer):
    #     self.headers.pop('Trailer', None)
    #     if trailer:
    #         trailer = Headers(trailer)
    #         for key in trailer:
    #             self.headers.append('Trailer', key)
    #         self.headers.elements('Trailer')  # sanitize
    #         self.headers.merge(trailer)

    def __init__(self, protocol: None = None, headers: None = None, body: None = None) -> None:
        """
        Initiates a new Message to hold information about the message.

        :param protocol: the requested protocol
        :type  protocol: str|tuple

        :param headers: the request headers
        :type  headers: dict or :class:`Headers`

        :param body: the request body
        :type  body: any
        """
        self.__protocol = Protocol(protocol or (1, 1))
        self.__headers = Headers(headers or {})
        self.__body = Body(body or b'')

    def parse(self, protocol: bytes) -> None:
        """
        Parses the HTTP protocol version.

        :param protocol: the protocol version string
        :type  protocol: bytes
        """
        self.protocol.parse(protocol)

    def __repr__(self) -> str:
        return f'<HTTP Message(protocol={self.protocol})>'
